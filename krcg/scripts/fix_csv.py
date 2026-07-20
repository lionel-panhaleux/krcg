#!/usr/bin/env python3
"""Fix VEKN csvs."""

import csv
import collections
import datetime
import os
import re
import warnings

#: Filing articles, longest-first so 'An' is matched before 'A' and 'The' before
#: nothing. Names are stored as printed (article prefixed); filing/sort order is
#: a separate concern (see models.filing_name). Mirrors models.FILING_PREFIXES.
PREFIX_ARTICLES = ["Une", "Una", "Les", "The", "An", "El", "La", "Le", "Un", "A"]

#: Upstream delimits a referenced card name with slashes ("cards named /Choir/").
#: The delimiters are whitespace-bounded, which is what separates them from the
#: slash of "and/or" and "that/those" — those sit between word characters. The
#: span itself may not start or end on whitespace, or two unrelated slashes on one
#: line would pair up ("1 blood / pool, or burn 1 blood / pool").
RE_CARD_REFERENCE = re.compile(r"(?<!\S)/(\S|\S[^/\n]*?\S)/(?![^\s,.;:)])")


def fix_sets_csv(path: str | os.PathLike[str]) -> None:
    """Fix the sets csv file."""
    result: list[dict[str, str]] = []
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        for row in reader:
            fixed = fix_set_row(row)
            if fixed:
                result.append(fixed)
    result.extend(MISSING_SETS)
    with open(path, "w", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in result:
            writer.writerow(row)


def fix_library_csv(path: str | os.PathLike[str], lang: str | None = None) -> None:
    """Fix the library csv file."""
    result: list[dict[str, str]] = []
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        if "Format" not in fieldnames:
            fieldnames.append("Format")
        for row in reader:
            fixed = fix_card_text(row, name_2=f"Name {lang}" if lang else None)
            if not lang:
                fixed = fix_lib_row(fixed)
                fixed = fix_card_row(fixed)
            if fixed:
                result.append(fixed)
    with open(path, "w", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in result:
            writer.writerow(row)


def fix_crypt_csv(path: str | os.PathLike[str], lang: str | None = None) -> None:
    """Fix the crypt csv file."""
    result: list[dict[str, str]] = []
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        if "Format" not in fieldnames:
            fieldnames.append("Format")
        for row in reader:
            fixed = fix_card_text(row, name_2=f"Name {lang}" if lang else None)
            if not lang:
                fixed = fix_crypt_row(fixed)
                fixed = fix_card_row(fixed)
            if fixed:
                result.append(fixed)
    with open(path, "w", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in result:
            writer.writerow(row)


def fix_set_row(row: dict[str, str]) -> dict[str, str] | None:
    """Fix a set row."""
    if row["Abbrev"].startswith("Promo"):
        return None
    if row["Abbrev"] in MISSING_SETS_ABBREVS:
        return None
    row["Company"] = row["Company"].strip()
    return row


def re_split(pattern: str, s: str) -> list[str]:
    """Split a string by a pattern and filter out empty strings."""
    ret = [a.strip() for a in re.split(pattern, s)]
    return list(filter(bool, ret))


def fix_name_articles(name: str) -> str:
    """Store names as printed: move a trailing filing article back to a prefix.

    'Ankou, The' -> 'The Ankou', 'Manifesto, An' -> 'An Manifesto'. Filing/sort
    order (which ignores the article) is handled separately by models.filing_name.
    """
    for article in PREFIX_ARTICLES:
        if name.endswith(f", {article}"):
            return f"{article} {name[: -len(article) - 2]}"
    return name


def fix_card_text(row: dict[str, str], name_2: str | None = None) -> dict[str, str]:
    """Fix card name."""
    row["Name"] = fix_name_articles(row["Name"].replace("(TM)", "™").strip())
    if name_2:
        if not row[name_2]:
            row[name_2] = row["Name"]
        row[name_2] = fix_name_articles(row[name_2].replace("(TM)", "™").strip())

    text = row["Card Text"]
    text = text.replace("(D)", "Ⓓ")
    text = text.replace("{", "")
    text = text.replace("}", "")
    text = text.replace("@", "")
    # before marking: a rename inside a marker would leave a name that resolves to
    # nothing ("<Thaumaturgy>" -> "<Blood Sorcery>", both real but different cards)
    for old, new in CLAN_RENAMES.items():
        text = text.replace(old, new)
    for old, new in DISC_RENAMES.items():
        text = text.replace(old, new)
    text = RE_CARD_REFERENCE.sub(r"<\1>", text)
    if not name_2:
        # longest first: marking "Frenzy" before "Terror Frenzy" would split the latter
        for literal in sorted(
            CARD_REFERENCES.get(int(row["Id"]), []), key=len, reverse=True
        ):
            text = re.sub(
                rf"<[^<>]*>|(?<![\w']){re.escape(literal)}(?![\w])",
                lambda m: m.group(0) if m.group(0)[0] == "<" else f"<{m.group(0)}>",
                text,
            )
    row["Card Text"] = text.strip()
    return row


def fix_card_row(row: dict[str, str]) -> dict[str, str]:
    """Fix a card row."""
    card_id = int(row["Id"])
    if card_id in POD_TAG_ADDITIONS and "POD" not in {
        tag.split(":", 1)[0] for tag in row["Set"].split(", ")
    }:
        row["Set"] += ", POD:DTC"
    row["Set"] = fix_set_field(row)
    artists = re_split(r"[;,&]+(?!\sJr\.)", row["Artist"])
    artists = [ARTISTS_FIXES.get(artist, artist) for artist in artists]
    row["Artist"] = ";".join(collections.Counter(artists).keys())  # preserve order
    if row["Banned"]:
        row["Banned"] = BAN_MAP.get(row["Banned"], row["Banned"])
    aka = re_split(";", row["Aka"]) + AKA.get(card_id, [])
    # store akas as printed too, unless that only re-articles the canonical name
    # (a bare prefix<->suffix of Name is redundant: indexing emits both forms)
    aka = [
        a if fix_name_articles(a) == row["Name"] else fix_name_articles(a) for a in aka
    ]
    row["Aka"] = ";".join(collections.Counter(aka).keys())  # preserve order
    sets = set(a[0] for r in row["Set"].split(", ") for a in r.split(":", 1))
    if V5_SETS & sets:
        row["Format"] = "V5"
    elif card_id in V5_CARDS:
        row["Format"] = "V5"
    else:
        row["Format"] = ""
    return row


def fix_set_field(row: dict[str, str]) -> str:
    """Fix a set."""
    card_id = int(row["Id"])
    field = row["Set"].replace("Promo-20181004:HB2", "Promo-20181004")
    field = field.replace("Promo-20230531:Chapters", "Promo-20230531")
    sets = re_split(", ", field)
    ret = []
    SKIP_ADDITIONS = {v[0] for v in SET_ADDITIONS.values()}
    for tag in sets:
        if tag.startswith("Promo-"):
            tag = tag.replace("Promo-", "Promo:")
        try:
            set_mark = re_split(r":", tag)
            if len(set_mark) > 1:
                if len(set_mark) > 2:
                    warnings.warn(f"failed to parse set ({card_id}): {tag}")
                    exit(1)
                set_, rarities = set_mark
            else:
                set_, rarities = set_mark[0], ""
        except ValueError:
            warnings.warn(f"failed to parse set ({card_id}): {tag}")
            exit(1)
        rarity_list = re_split(r"/", rarities)
        if not rarity_list:
            if set_ == "POD":
                bundle = get_pod_release_date(row)
                ret.append(f"{set_}:{bundle}")
            else:
                ret.append(set_)
            continue
        for rarity in rarity_list:
            match = re.match(r"^([a-zA-Z]*)([\d½]*)$", rarity)
            if not match:
                warnings.warn(f"failed to parse rarity ({card_id}): {rarity}")
                exit(1)
            # cur is a per-rarity copy: a replacement/addition must not leak the
            # set code onto the following rarities of the same slash-joined tag
            cur, (bundle, count) = set_, match.groups()
            # skip our own additions
            if bundle in SKIP_ADDITIONS:
                continue
            if cur == "Promo" or cur == "POD":
                bundle, count = count[:8], ""
            # addition keys on the pre-replacement code: the Anthology:LARP →
            # Anthology: rewrite must not then trigger the Anthology: → Ant1:
            # alias (only the originally empty-coded cards are reprinted in Ant1)
            addition_key = (cur, bundle)
            if (cur, bundle) in SET_REPLACEMENTS:
                cur, bundle = SET_REPLACEMENTS[(cur, bundle)]
            if (cur, bundle) in SET_REMOVALS:
                continue
            if cur == "POD" and not bundle:
                bundle = get_pod_release_date(row)
            if cur != "Promo" and cur != "POD" and not count:
                count = 1
            ret.append(f"{cur}{':' if bundle or count else ''}" + f"{bundle}{count}")
            if addition_key in SET_ADDITIONS:
                cur, bundle = SET_ADDITIONS[addition_key]
                if (cur, bundle) in ADDITION_CARD_COUNTS:
                    try:
                        count = ADDITION_CARD_COUNTS[(cur, bundle)][card_id]
                    except KeyError:
                        warnings.warn(f"missing {card_id} in {cur}:{bundle}")
                        exit(1)
                ret.append(
                    f"{cur}{':' if bundle or count else ''}" + f"{bundle}{count}"
                )
    return ", ".join(ret)


def get_pod_release_date(row: dict[str, str]) -> str:
    """Get the release date for a POD card."""
    card_id = int(row["Id"])
    if card_id in POD_RELEASES_CARDS:
        return POD_RELEASES_CARDS[card_id]
    match = RE_POD_WORD.search(row["Clan"]) or RE_POD_WORD.search(row["Card Text"])
    if match:
        clan = match.group(0)
        return POD_RELEASES_WORDS[clan]
    match = RE_POD_DISC.search(row.get("Disciplines", row.get("Discipline")) or "")
    if match:
        discipline = match.group(0)
        return POD_RELEASES_DISC[discipline]
    warnings.warn(f"failed to find release date for {card_id}")
    return ""


def fix_crypt_row(row: dict[str, str]) -> dict[str, str]:
    """Fix a card row."""
    row["Clan"] = CLAN_RENAMES.get(row["Clan"], row["Clan"])
    if row["Disciplines"] != "-none-":
        for trigram in row["Disciplines"].split():
            if trigram.lower() not in KNOWN_DISCIPLINES:
                warnings.warn(f"unknown crypt discipline ({row['Id']}): {trigram}")
    return row


def fix_lib_row(row: dict[str, str]) -> dict[str, str]:
    """Fix a card row."""
    disciplines = re_split(r"/|\s*&\s*", row["Discipline"])
    disciplines = [DISCIPLINE_MAP.get(d, d) for d in disciplines]
    for trigram in disciplines:
        if trigram not in KNOWN_DISCIPLINES:
            warnings.warn(f"unknown library discipline ({row['Id']}): {trigram}")
    if "&" in row["Discipline"]:
        sep = "&"
    else:
        sep = "/"
    row["Discipline"] = sep.join(disciplines)
    clans = re_split("/", row["Clan"])
    clans = [CLAN_RENAMES.get(clan, clan) for clan in clans]
    row["Clan"] = "/".join(clans)
    return row


#: Card names the upstream CSV names in prose but leaves unmarked, tagged here so
#: the parser sees every reference. A name is only listed when it means that card:
#: on Sire's Index Finger the enumerated "Frenzy" is the card, while elsewhere
#: "Frenzy cards" is the family and is left alone. A card naming itself is not a
#: reference. Entries become redundant as upstream marks them, and the marking is
#: idempotent, so a stale entry is harmless.
CARD_REFERENCES = {
    100050: ["Ivory Bow"],  # Anachronism
    100148: ["Earth Meld"],  # Becoming of Ennoia
    100161: ["Kerrie"],  # Bind the Night-Walker
    100452: ["Lucita"],  # Crusade: Aragon
    100554: ["Immortal Grapple", "Mighty Grapple"],  # Disengage
    100919: ["Illuminate"],  # Hide
    100953: ["The Unmasking"],  # Illuminate
    100960: ["Blood Hunt"],  # Imperator
    101001: ["Lost in Crowds"],  # Into Thin Air
    101115: ["Cleave"],  # Living Wood Staff
    101307: ["Taste of Vitae"],  # The Oath
    101343: ["Elder Intervention"],  # Pack Tactics
    101752: ["Humanitas", "Memories of Mortality"],  # Shame
    101785: [
        "Brujah Frenzy",
        "Drawing Out the Beast",
        "Frenzy",
        "Rötschreck",
        "Terror Frenzy",
    ],  # Sire's Index Finger
    101812: ["IR Goggles", "Laptop Computer", "Phased Motion Detector"],  # Smite
    102186: ["Dodge"],  # Winged Second
    102311: ["Path of Death and the Soul"],  # Burial Site Hunting Ground
    200199: [
        "Arcane Library",
        "Elder Library",
        "Fragment of the Book of Nod",
    ],  # Bindusara, Historian of the Kindred
    200312: ["Giant's Blood"],  # Dan Murdock
    200401: ["Enid Blount"],  # Edith Blount
    200423: ["Edith Blount"],  # Enid Blount
    200493: ["Ubende"],  # Ganhuru
    200613: ["Greensleeves"],  # Humo
    200683: ["Society of Leopold"],  # Jayne Jonestown
    201189: ["Bomb"],  # Rico Loco
    201342: ["Blood Doll", "Minion Tap"],  # Tarautas
    201771: ["Path of Death and the Soul"],  # Sakura, The Merciless
}

CLAN_RENAMES = {
    "Followers of Set": "Ministries",
    "Follower of Set": "Ministry",
    "Assamites": "Banu Haqim",
    "Assamite": "Banu Haqim",
    "Assamita": "Banu Haqim",
}

DISC_RENAMES = {
    "Thaumaturgy": "Blood Sorcery",
}

DISCIPLINE_MAP = {
    "Abombwe": "abo",
    "Animalism": "ani",
    "Auspex": "aus",
    "Blood Sorcery": "tha",  # historical
    "Celerity": "cel",
    "Chimerstry": "chi",
    "Daimoinon": "dai",
    "Dementation": "dem",
    "Dominate": "dom",
    "Flight": "fli",
    "Fortitude": "for",
    "Maleficia": "mal",
    "Melpominee": "mel",
    "Mytherceria": "myt",
    "Necromancy": "nec",
    "Obeah": "obe",
    "Obfuscate": "obf",
    "Oblivion": "obl",
    "Obtenebration": "obt",
    "Potence": "pot",
    "Presence": "pre",
    "Protean": "pro",
    "Quietus": "qui",
    "Sanguinus": "san",
    "Serpentis": "ser",
    "Spiritus": "spi",
    "Striga": "str",
    "Temporis": "tem",
    "Thanatosis": "thn",
    "Thaumaturgy": "tha",
    "Valeren": "val",
    "Vicissitude": "vic",
    "Visceratika": "vis",
    "Vengeance": "ven",
    "Defense": "def",
    "Innocence": "inn",
    "Judgment": "jud",
    "Martyrdom": "mar",
    "Redemption": "red",
    "Vision": "viz",
    "-none-": "",
}

#: Known discipline trigrams, to flag typos in the source CSVs at sync time
KNOWN_DISCIPLINES = {trigram for trigram in DISCIPLINE_MAP.values() if trigram}

# missing from aka field
AKA = {
    101179: ["mask of 1,000 faces"],
}

#: Actual ban dates
BAN_MAP = {
    "1995": "19951101",  # RTR 19951006
    "1997": "19970701",  # RTR 19970701
    "1999": "19990401",  # RTR 19990324
    "2005": "20050101",  # RTR 20041205
    "2008": "20080101",  # RTR 20071204
    "2013": "20130522",  # RTR 20130422
    "2016": "20160216",  # RTR 20160119
    "2020": "20200801",  # RTR 20200705
}

# before that date, cards were legal only 30 days after release
LEGAL_ON_RELEASE = datetime.date(2025, 9, 21)

ARTISTS_FIXES = {
    "Alejandro Collucci": "Alejandro Colucci",
    "Chet Masterz": "Chet Masters",
    "Dimple": 'Nicolas "Dimple" Bigot',
    "EM Gist": "E.M. Gist",
    "G. Goleash": "Grant Goleash",
    "Gabriel de Góes": "Gabriel de Góes Figueiredo",
    "Ginés Quiñonero": "Ginés Quiñonero-Santiago",
    "Glenn Osterberger": "Glen Osterberger",
    "Heather Kreiter": "Heather V. Kreiter",
    'Jeff "el jefe" Holt': "Jeff Holt",
    "L. Snelly": "Lawrence Snelly",
    "Martín de Diego": "Martín de Diego Sábada",
    "Mathias Tapia": "Matias Tapia",
    "Mattias Tapia": "Matias Tapia",
    "Matt Mitchell": "Matthew Mitchell",
    "Mike Gaydos": "Michael Gaydos",
    "Mike Weaver": "Michael Weaver",
    "Nicolas Bigot": 'Nicolas "Dimple" Bigot',
    "Pat McEvoy": "Patrick McEvoy",
    "Randy\xa0Gallegos": "Randy Gallegos",
    "Ron Spenser": "Ron Spencer",
    "Sam Araya": "Samuel Araya",
    "Sandra Chang": "Sandra Chang-Adair",
    "T. Bradstreet": "Tim Bradstreet",
    "Tom Baxa": "Thomas Baxa",
    "zelgaris": 'Tomáš "zelgaris" Zahradníček',
}

MISSING_SETS = [
    {
        "Id": "320001",
        "Abbrev": "HttBR",
        "Full Name": "Heirs to the Blood Reprint",
        "Release Date": "20180714",
        "Company": "Paradox Interactive AB",
    },
    {
        "Id": "320002",
        "Abbrev": "KoTR",
        "Full Name": "Keepers of Tradition Reprint",
        "Release Date": "20180505",
        "Company": "Paradox Interactive AB",
    },
    {
        "Id": "320003",
        "Abbrev": "Ant1",
        "Full Name": "Anthology I",
        "Release Date": "20190216",
        "Company": "Paradox Interactive AB",
    },
    {
        "Id": "320004",
        "Abbrev": "PP1",
        "Full Name": "Promo Pack 1",
        "Release Date": "20200301",
        "Company": "Paradox Interactive AB",
    },
    {
        "Id": "320005",
        "Abbrev": "PP2",
        "Full Name": "Promo Pack 2",
        "Release Date": "20221103",
        "Company": "Paradox Interactive AB",
    },
    {
        "Id": "320006",
        "Abbrev": "PP3",
        "Full Name": "Promo Pack 3 — Icons",
        "Release Date": "20250920",
        "Company": "Paradox Interactive AB",
    },
]

MISSING_SETS_ABBREVS = {set["Abbrev"] for set in MISSING_SETS}

SET_REPLACEMENTS = {
    # drop the LARP code: Anthology is one product. Reprinted cards are told
    # apart only by the Ant1 addition, which keys on the original empty code.
    ("Anthology", "LARP"): ("Anthology", ""),
    ("BSC", "X"): ("BSC", ""),
    ("HttB", "A"): ("HttBR", "A"),
    ("HttB", "B"): ("HttBR", "B"),
    ("KoT", "A"): ("KoTR", "A"),
    ("KoT", "B"): ("KoTR", "B"),
    ("POD", "DTC"): ("POD", ""),
}

SET_ADDITIONS = {
    ("Anthology", ""): ("Ant1", ""),
    ("Promo", "20190408"): ("PP1", ""),
    ("Promo", "20200511"): ("PP2", ""),
    ("Promo", "20211015"): ("PP3", ""),
}

SET_REMOVALS = {
    ("DM", "C"),
    ("TU", "C"),
    ("AU", "C"),
}

ADDITION_CARD_COUNTS = {
    ("PP1", ""): {
        200856: 10,
        201001: 10,
        201006: 10,
        200242: 10,
        200385: 10,
        200587: 1,
        200758: 1,
        200976: 1,
        201048: 1,
        201049: 1,
        201486: 1,
    },
    ("PP2", ""): {
        201524: 10,
        201525: 10,
        201521: 10,
        201523: 10,
        201526: 10,
        201407: 1,
        100071: 1,
        100169: 1,
        101256: 1,
        101353: 1,
        101384: 1,
    },
    ("PP3", ""): {
        201617: 10,
        201618: 10,
        201619: 10,
        201621: 10,
        201616: 10,
        101156: 1,
        101297: 1,
        100018: 1,
        102020: 1,
        101013: 1,
        101028: 1,
    },
}

POD_RELEASES_WORDS = {
    "Baali": "20230306",
    "Banu Haqim": "20191224",
    "Chimerstry": "20210923",
    "Daimoinon": "20230306",
    "Daughter of Cacophony": "20230306",
    "Daughters of Cacophony": "20230306",
    "Dementation": "20260119",
    "Giovanni": "20210307",
    "infernal": "20230306",
    "Lasombra": "20210307",
    "Malkavian antitribu": "20260119",
    "Ministry": "20210307",
    "Ministries": "20210307",
    "Necromancy": "20210307",
    "Obeah": "20220427",
    "Obtenebration": "20210307",
    "Pander": "20220427",
    "Quietus": "20191224",
    "Ravnos": "20210923",
    "Salubri": "20220427",
    "Serpentis": "20210307",
    "Temporis": "20250317",
    "Tremere antitribu": "20230825",
    "True Brujah": "20250317",
    "Tzimisce": "20220427",
    "Vicissitude": "20220427",
}

RE_POD_WORD = re.compile(r"|".join(POD_RELEASES_WORDS.keys()))

POD_RELEASES_DISC = {
    "qui": "20191224",
    "ser": "20210307",
    "nec": "20210307",
    "obt": "20210307",
    "chi": "20210923",
    "obe": "20220427",
    "vic": "20220427",
    "dai": "20230306",
    "tem": "20250317",
    "mel": "20230306",
    "dem": "20260119",
}

RE_POD_DISC = re.compile(r"|".join(POD_RELEASES_DISC.keys()))

POD_RELEASES_CARDS = {
    100545: "20210411",  # Direct Intervention
    100106: "20240101",  # Ashur Tablets
    100634: "20240101",  # Emerald Legionnaire
    100500: "20230825",  # Dauntain Black Magician (Tremere antitribu wave, Malk req)
    201421: "20230825",  # Valerius Maior, Hell's Fool (base clan is Tremere)
}

#: Cards in a Legacy Singles (POD) wave that upstream vtescsv hasn't tagged
#: "POD:DTC" yet — we inject the tag so get_pod_release_date can date them.
#: Drop entries once upstream adds them (the loader skips cards already tagged).
POD_TAG_ADDITIONS = {
    # 2023-08-25 Tremere antitribu wave (57 cards)
    100440,
    100454,
    100500,
    100914,
    100979,
    101272,
    101571,
    101658,
    101849,
    101892,
    102075,
    102102,
    200044,
    200116,
    200146,
    200152,
    200221,
    200225,
    200246,
    200408,
    200418,
    200429,
    200437,
    200438,
    200485,
    200507,
    200528,
    200529,
    200567,
    200583,
    200616,
    200661,
    200674,
    200714,
    200767,
    200782,
    200796,
    200803,
    200827,
    200833,
    200877,
    200905,
    200931,
    201013,
    201056,
    201084,
    201100,
    201182,
    201186,
    201222,
    201261,
    201356,
    201360,
    201418,
    201421,
    201422,
    201483,
    # 2024-01-01 Ashur Tablets, Emerald Legionnaire (already Promo:20240101 upstream)
    100106,
    100634,
}

V5_CARDS = {
    100018,
    201528,
    100408,
    100526,
    201616,
    201527,
    201617,
    101013,
    101019,
    201621,
    201633,
    101156,
    101214,
    101297,
    201618,
    201352,
    101192,
    102020,
    201619,
}

V5_SETS = {
    "V5",
    "V5A",
    "NB",
    "FoL",
    "SoB",
    "NB2",
    "V5C",
    "30th",
    "NB3",
    "SV5",
}

if __name__ == "__main__":
    fix_sets_csv("krcg/cards/vtessets.csv")
    fix_library_csv("krcg/cards/vteslib.csv")
    fix_crypt_csv("krcg/cards/vtescrypt.csv")
    fix_library_csv("krcg/cards/vtescsv-es/vteslib.es-ES.csv", "es-ES")
    fix_crypt_csv("krcg/cards/vtescsv-es/vtescrypt.es-ES.csv", "es-ES")
    fix_library_csv("krcg/cards/vtescsv-fr/vteslib.fr-FR.csv", "fr-FR")
    fix_crypt_csv("krcg/cards/vtescsv-fr/vtescrypt.fr-FR.csv", "fr-FR")
