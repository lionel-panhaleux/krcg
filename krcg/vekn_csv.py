"""VEKN CSV parser."""

from collections.abc import Generator
import csv
import enum
import datetime
import importlib.resources
import itertools
import logging
import re
import urllib.parse
import warnings

from . import models
from . import utils

logger = logging.getLogger("krcg")


BASE_SETS = "vtessets.csv"
BASE_BUNDLES = "vtesbundles.csv"
BASE_CRYPT = "vtescrypt.csv"
BASE_LIB = "vteslib.csv"
KRCG_STATIC_SERVER = "https://static.krcg.org"
TRANSLATIONS = [
    (models.Lang.ES, "vtescsv-es/vtescrypt.es-ES.csv"),
    (models.Lang.ES, "vtescsv-es/vteslib.es-ES.csv"),
    (models.Lang.FR, "vtescsv-fr/vtescrypt.fr-FR.csv"),
    (models.Lang.FR, "vtescsv-fr/vteslib.fr-FR.csv"),
]

ALIASES = {
    # traditions
    100737: [
        "The First Tradition",
        "First Tradition",
        "1st Tradition",
    ],
    101706: [
        "The Second Tradition",
        "Second Tradition",
        "2nd Tradition",
    ],
    101973: [
        "The Third Tradition",
        "Third Tradition",
        "3rd Tradition",
    ],
    100782: [
        "The Fourth Tradition",
        "Fourth Tradition",
        "4th Tradition",
    ],
    100727: [
        "The Fifth Tradition",
        "Fifth Tradition",
        "5th Tradition",
    ],
    101788: [
        "The Sixth Tradition",
        "Sixth Tradition",
        "6th Tradition",
    ],
    # known abbreviations
    100130: ["Bang Nakh"],
    100298: ["Carlton"],
    100303: ["Carver's Meat Packing"],
    100519: ["Delaying"],
    100588: ["Dreams"],
    100632: ["Elysium: Versailles"],
    100719: ["Felix Fix"],
    100765: ["Foreshadowing"],
    100842: ["Golconda"],
    100845: ["Govern"],
    100908: ["Heidelberg"],
    100984: ["Info Highway"],
    101067: ["KRCG"],
    101073: ["Laptop"],
    101249: ["Mister Winthrop"],
    101357: ["Patagia: Flaps", "Patagia"],
    101896: ["Sudden"],
    102131: ["Voter Cap"],
    102137: ["WwEF"],
    102189: ["WMRH"],
    # 🥚
    100645: ["Enkil Cock"],
    101353: ["Parity Shit"],
    100903: ["Heart of Cheating"],
}

DictOfCards = dict[int, models.Card]
DictofSets = dict[int | str, models.Set]


def from_files() -> tuple[DictOfCards, DictofSets]:
    """Load cards from local CSV files."""
    cards = DictOfCards()
    sets = dict[int | str, models.Set]()
    sets["Promo"] = models.Set(
        code="Promo",
        name="Promo",
    )
    sets["POD"] = models.Set(
        code="POD",
        name="Print on Demand",
    )
    local_dir = importlib.resources.files("krcg.cards")
    with local_dir.joinpath(BASE_SETS).open(encoding="utf-8-sig") as f:
        for line in csv.DictReader(f):
            set_ = set_from_vekn(line)
            sets[set_.id] = set_
            sets[set_.code] = set_
            sets[set_.name] = set_
    with local_dir.joinpath(BASE_BUNDLES).open(encoding="utf-8-sig") as f:
        for line in csv.DictReader(f):
            add_bundle(sets, line)
    with local_dir.joinpath(BASE_CRYPT).open(encoding="utf-8-sig") as f:
        for line in csv.DictReader(f):
            crypt = crypt_card_from_vekn(sets, line)
            cards[crypt.id] = crypt
    with local_dir.joinpath(BASE_LIB).open(encoding="utf-8-sig") as f:
        for line in csv.DictReader(f):
            lib = lib_card_from_vekn(sets, line)
            cards[lib.id] = lib
    for lang, path in TRANSLATIONS:
        with local_dir.joinpath(path).open(encoding="utf-8-sig") as f:
            for line in csv.DictReader(f):
                add_translation(cards, line, lang)
    compute_variants(cards)
    compute_urls(cards, sets)
    return cards, sets


def set_from_vekn(line: dict[str, str]) -> models.Set:
    """Create a set from a VEKN CSV line."""
    set_ = models.Set(
        id=int(line["Id"]),
        code=line["Abbrev"],
        release_date=datetime.datetime.strptime(line["Release Date"], "%Y%m%d").date(),
        name=line["Full Name"],
        company=line["Company"],
    )
    return set_


def add_bundle(sets: DictofSets, line: dict[str, str]) -> None:
    """Add bundle to sets."""
    bundle = line["Bundle"]
    sets[line["Set"]].bundles[bundle] = models.Bundle(
        code=bundle,
        name=line["Name"],
        size=int(line["Size"]),
    )


GROUP_MAP = {
    "1": models.Group.G1,
    "2": models.Group.G2,
    "3": models.Group.G3,
    "4": models.Group.G4,
    "5": models.Group.G5,
    "6": models.Group.G6,
    "7": models.Group.G7,
    "any": models.Group.Any,
}


# before that date, cards were legal only 30 days after release
LEGAL_ON_RELEASE = datetime.date(2025, 9, 21)


def parse_enum_list[E: enum.Enum](value: str, cls: type[E], sep: str = "/") -> list[E]:
    """Parse a list of enum members from a string."""
    return [cls(v.strip()) for v in value.split(sep) if v.strip()]


def card_from_vekn[T: models.Card](
    sets: dict[int | str, models.Set], line: dict[str, str], cls: type[T]
) -> T:
    """Create a card from a VEKN CSV line."""
    card = cls(
        kind=(
            models.Card.Kind.CRYPT
            if issubclass(cls, models.CryptCard)
            else models.Card.Kind.LIBRARY
        ),
        id=int(line["Id"]),
        printed_name=prefix_name(line["Name"]),
        types=parse_enum_list(line["Type"], models.Card.Type, "/"),
        text=line["Card Text"],
        prints=prints_from_vekn(sets, line["Set"]),
        artists=line.get("Artist", "").split(";"),
        formats=parse_enum_list(line["Format"], models.Format, ";"),
    )
    for aka in [a.strip() for a in line["Aka"].split(";") if a.strip()]:
        aka = prefix_name(aka).strip()
        card.name_variants.append(
            models.NameVariant(type=models.NameVariant.Type.HISTORICAL, name=aka)
        )
    if card.id in ALIASES:
        for alias in ALIASES[card.id]:
            card.name_variants.append(
                models.NameVariant(
                    type=models.NameVariant.Type.VERNACULAR, name=alias.strip()
                )
            )
    if line["Banned"]:
        card.banned = datetime.datetime.strptime(line["Banned"], "%Y%m%d").date()
    if card.prints and len(card.prints) > 1:
        original = sets.get(card.prints[0].set.id)
        if original and original.release_date:
            card.legal = original.release_date
            if card.legal < LEGAL_ON_RELEASE:
                card.legal += datetime.timedelta(days=30)
        # promo only (singles)
        else:
            card.legal = card.prints[0].occurrences[0].date
    return card


def crypt_card_from_vekn(
    sets: dict[int | str, models.Set], line: dict[str, str]
) -> models.CryptCard:
    """Create a crypt card from a VEKN CSV line."""
    card = card_from_vekn(sets, line, models.CryptCard)
    card.clan = line["Clan"]
    card.path = line["Path"]
    card.advanced = bool(line["Adv"])
    card.group = GROUP_MAP[line["Group"].lower()]
    card.capacity = int(line["Capacity"])
    if line["Disciplines"] != "-none-":
        # crypt disciplines encode level by case (lower=inferior, UPPER=superior)
        card.disciplines = line["Disciplines"].split()
    if line["Title"]:
        card.title = models.Title(line["Title"].title())
    match card.group, card.advanced:
        case models.Group.Any, True:
            card.suffix = "ADV"
        case models.Group.Any, False:
            card.suffix = ""
        case _, True:
            card.suffix = f"{card.group.value} ADV"
        case _, False:
            card.suffix = card.group.value
    return card


def lib_card_from_vekn(
    sets: dict[int | str, models.Set], line: dict[str, str]
) -> models.LibraryCard:
    """Create a library card from a VEKN CSV line."""
    card = card_from_vekn(sets, line, models.LibraryCard)
    card.burn_option = bool(line["Burn Option"])
    if models.Card.Type.MASTER in card.types and re.search(
        r"(t|T)rifle", card.text.split("\n", 1)[0]
    ):
        card.trifle = True
    if "&" in line["Discipline"]:
        card.discipline_requirement = models.DisciplineRequirement(
            type=models.DisciplineRequirement.Type.COMBO,
            disciplines=[d.strip() for d in line["Discipline"].split("&") if d.strip()],
        )
    else:
        # library requirements are level-agnostic (lowercase trigrams)
        disciplines = [d.strip() for d in line["Discipline"].split("/") if d.strip()]
        card.discipline_requirement = models.DisciplineRequirement(
            type=(
                models.DisciplineRequirement.Type.CHOICE
                if len(disciplines) > 1
                else models.DisciplineRequirement.Type.MONO
            ),
            disciplines=disciplines,
        )
    card.path_requirement = [p.strip() for p in line["Path"].split("/") if p.strip()]
    card.clan_requirement = [c.strip() for c in line["Clan"].split("/") if c.strip()]
    card.flavor = line["Flavor Text"]
    for cost_type, column in (
        (models.Cost.Type.POOL, "Pool Cost"),
        (models.Cost.Type.BLOOD, "Blood Cost"),
        (models.Cost.Type.CONVICTION, "Conviction Cost"),
    ):
        if line[column]:
            value = line[column]
            card.cost = models.Cost(
                type=cost_type, value=int(value) if value.isdigit() else "X"
            )
            break
    return card


def prefix_name(name: str) -> str:
    """Prefix 'The', 'El', 'La' or 'Le' if it's as suffix."""
    for prefix in models.FILING_PREFIXES:
        if name.endswith(f", {prefix}"):
            return prefix + " " + name[: -len(prefix) - 2]
    return name


def prints_from_vekn(
    sets: dict[int | str, models.Set], sets_field: str
) -> list[models.Print]:
    """Create prints from a VEKN CSV line."""
    prints: dict[str, list[models.Occurrence]] = {}
    tags = sets_field.split(", ")
    for tag in tags:
        match = re.match(r"^([a-zA-Z0-9-]+):?([a-zA-Z0-9/½]+)?$", tag)
        if not match:
            warnings.warn(f"failed to parse set: {tag}")
            continue
        expansion, rarity = match.groups()
        if expansion not in sets:
            warnings.warn(f"unknown set: {expansion}")
            continue
        prints.setdefault(expansion, [])
        if rarity:
            match = re.match(r"^([a-zA-Z]*)([\d½]*)$", rarity)
            if not match:
                warnings.warn(f"failed to parse rarity: {tag}")
                continue
            base, count = match.groups()
            if expansion == "Promo" or expansion == "POD":
                base, count = count, ""
            prints.setdefault(expansion, [])
            if base in {"C", "U", "R", "V"}:
                if count == "½":
                    count = 0.5
                prints[expansion].append(
                    models.Occurrence(
                        type=models.Occurrence.Type.RARITY,
                        frequency=models.Occurrence.Frequency(base),
                        multiplier=float(count),
                    )
                )
            elif count:
                prints[expansion].append(
                    models.Occurrence(
                        type=models.Occurrence.Type.PRECON,
                        bundle=base,
                        copies=int(count),
                    )
                )
            elif base:
                try:
                    prints[expansion].append(
                        models.Occurrence(
                            type=models.Occurrence.Type.SINGLE,
                            date=datetime.datetime.strptime(base, "%Y%m%d").date(),
                        )
                    )
                except ValueError:
                    warnings.warn(f"failed to parse date: {base}")
                    raise
    return sorted(
        [
            # url set later by compute_urls
            models.Print(
                set=models.SetMinimal(id=sets[expansion].id, code=expansion),
                occurrences=occurences,
                url="",
            )
            for expansion, occurences in prints.items()
        ],
        key=lambda p: (
            (
                sets[p.set.id].release_date
                if p.set.id and sets[p.set.id].release_date
                else p.occurrences[0].date
            )
            or datetime.date.min
        ),
    )


def compute_urls(cards: DictOfCards, sets: DictofSets) -> None:
    """Compute the URLs for a card.

    WARNING: compute_variants must be called before this function.
    """
    base_url = urllib.parse.urljoin(KRCG_STATIC_SERVER, "/card/")
    for card in cards.values():
        card_name = re.sub(r"[^\w\d]", "", utils.normalize(card.full_name)) + ".jpg"
        card.url = urllib.parse.urljoin(base_url, card_name)
        for lang, translation in card.i18n.items():
            # url is set dynamically; not a declared Translation field
            translation.url = urllib.parse.urljoin(  # type: ignore[attr-defined]
                base_url, f"{lang.value}/{card_name}"
            )
        for print_ in card.prints:
            set_name = (
                sets[print_.set.code]
                .name.lower()
                .replace(":", "")
                .replace("(", "")
                .replace(")", "")
                .replace(" ", "-")
            )
            print_.url = urllib.parse.urljoin(base_url, f"set/{set_name}/{card_name}")


def add_translation(
    cards: DictOfCards, line: dict[str, str], lang: models.Lang
) -> None:
    """Add a translation to a card."""
    card = cards[int(line["Id"])]
    card.i18n[lang] = models.Translation(
        name=prefix_name(line[f"Name {lang}-{lang.upper()}"]),
        text=line["Card Text"],
        flavor=line["Flavor Text"] if card.kind == models.Card.Kind.LIBRARY else "",
    )


def compute_variants(cards: DictOfCards) -> None:
    """Compute variants and unicity_suffix for cards."""
    # variants (group/advanced) are a crypt-only concept
    same_name: dict[str, list[models.CryptCard]] = {}
    for card in cards.values():
        if isinstance(card, models.CryptCard):
            same_name.setdefault(card.printed_name, []).append(card)
    same_name = {k: v for k, v in same_name.items() if len(v) > 1}
    for name_group in same_name.values():
        for card, variant in itertools.permutations(name_group, 2):
            assert card.group is not None and variant.group is not None
            if card.group < variant.group:
                type_ = models.Variant.Type.EVOLUTION
            elif card.group > variant.group:
                type_ = models.Variant.Type.PREVIOUS
            else:
                if card.advanced:
                    assert not variant.advanced
                    type_ = models.Variant.Type.BASE
                else:
                    assert variant.advanced
                    type_ = models.Variant.Type.ADVANCED
            card.variants.append(
                models.Variant(
                    type=type_,
                    id=variant.id,
                    suffix=variant.suffix,
                )
            )
    # compute minimum suffix for unicity
    for card in cards.values():
        if isinstance(card, models.CryptCard):
            assert card.group is not None
            has_other_group = any(
                v.type in {models.Variant.Type.PREVIOUS, models.Variant.Type.EVOLUTION}
                for v in card.variants
            )
            match has_other_group, card.advanced:
                case True, True:
                    card.unicity_suffix = f"{card.group.value} ADV"
                case True, False:
                    card.unicity_suffix = card.group.value
                case False, True:
                    card.unicity_suffix = "ADV"
                case False, False:
                    card.unicity_suffix = ""

    # fix suffixes for historical "aka" variants and specific vernaculars
    for card in cards.values():
        previous_variants = card.name_variants
        card.name_variants = []
        for name_variant in previous_variants:
            for name, variant_type in _variants(
                name_variant.name, card, name_variant.type
            ):
                card.name_variants.append(
                    models.NameVariant(
                        name=name,
                        type=variant_type,
                    )
                )
    # the first card with the name is the best guess without suffix
    for card in cards.values():
        if (
            card.variants
            and card.printed_name != card.unique_name
            and all(c.suffix > card.suffix for c in card.variants)
        ):
            card.name_variants.append(
                models.NameVariant(
                    name=card.printed_name,
                    type=models.NameVariant.Type.VERNACULAR,
                )
            )
    # lexicographical and vernacularname variants
    for card in cards.values():
        if (
            isinstance(card, models.CryptCard)
            and card.group == models.Group.Any
            and not card.unicity_suffix
        ):
            for name, variant_type in _word_variants(
                card.printed_name, " (Any)", models.NameVariant.Type.LEXICOGRAPHICAL
            ):
                card.name_variants.append(
                    models.NameVariant(
                        name=name,
                        type=variant_type,
                    )
                )
        for name, variant_type in _variants(
            card.printed_name, card, models.NameVariant.Type.LEXICOGRAPHICAL
        ):
            card.name_variants.append(
                models.NameVariant(
                    name=name,
                    type=variant_type,
                )
            )

        if "™" in card.printed_name:
            for name, variant_type in _variants(
                card.printed_name.replace("™", "(TM)"),
                card,
                models.NameVariant.Type.LEXICOGRAPHICAL,
            ):
                card.name_variants.append(
                    models.NameVariant(
                        name=name,
                        type=variant_type,
                    )
                )
        if card.printed_name.startswith("Powerbase: "):
            for name, variant_type in _variants(
                "PB: " + card.printed_name[11:],
                card,
                models.NameVariant.Type.VERNACULAR,
            ):
                card.name_variants.append(
                    models.NameVariant(
                        name=name,
                        type=variant_type,
                    )
                )
        if card.printed_name.endswith(" Hunting Ground"):
            for name, variant_type in _variants(
                card.printed_name[-15:] + " HG",
                card,
                models.NameVariant.Type.VERNACULAR,
            ):
                card.name_variants.append(
                    models.NameVariant(
                        name=name,
                        type=variant_type,
                    )
                )
        if card.printed_name.endswith("!"):
            for name, variant_type in _variants(
                card.printed_name[-1:], card, models.NameVariant.Type.VERNACULAR
            ):
                card.name_variants.append(
                    models.NameVariant(
                        name=name,
                        type=variant_type,
                    )
                )
        for translation in card.i18n.values():
            if translation.name == card.printed_name:
                continue
            for name, variant_type in _variants(
                translation.name, card, models.NameVariant.Type.VERNACULAR
            ):
                card.name_variants.append(
                    models.NameVariant(name=name, type=variant_type)
                )


def _variants(
    name: str, card: models.CardMinimal, variant_type: models.NameVariant.Type
) -> Generator[tuple[str, models.NameVariant.Type]]:
    if card.unicity_suffix:
        yield from _word_variants(name, f" ({card.unicity_suffix})", variant_type)
    else:
        yield from _word_variants(name, "", variant_type)
    if card.suffix and card.suffix != card.unicity_suffix:
        yield from _word_variants(name, f" ({card.suffix})", variant_type)


def _word_variants(
    name: str, suffix: str, variant_type: models.NameVariant.Type
) -> Generator[tuple[str, models.NameVariant.Type]]:
    yield from _comma_splits(name, suffix, variant_type)
    for prefix in models.FILING_PREFIXES:
        if name.startswith(prefix + " "):
            yield from _comma_splits(
                name[len(prefix) + 1 :] + ", " + prefix, suffix, variant_type
            )


def _comma_splits(
    name: str, suffix: str, variant_type: models.NameVariant.Type
) -> Generator[tuple[str, models.NameVariant.Type]]:
    while True:
        yield name + suffix, variant_type
        name_parts = name.rsplit(",", 1)
        variant_type = models.NameVariant.Type.VERNACULAR
        if len(name_parts) < 2:
            break
        name = name_parts[0]
        if len(name) <= 4:
            break
