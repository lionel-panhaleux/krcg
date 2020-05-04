import os.path

from src import twda
from src import vtes


def test_init():
    assert sorted(vtes.VTES.trait_choices("Discipline")) == [
        "Abombwe",
        "Animalism",
        "Auspex",
        "Celerity",
        "Chimerstry",
        "Daimoinon",
        "Defense",
        "Dementation",
        "Dominate",
        "Flight",
        "Fortitude",
        "Innocence",
        "Judgment",
        "Maleficia",
        "Martyrdom",
        "Melpominee",
        "Mytherceria",
        "Necromancy",
        "Obeah",
        "Obfuscate",
        "Obtenebration",
        "Potence",
        "Presence",
        "Protean",
        "Quietus",
        "Redemption",
        "Sanguinus",
        "Serpentis",
        "Spiritus",
        "Striga",
        "Temporis",
        "Thanatosis",
        "Thaumaturgy",
        "Valeren",
        "Vengeance",
        "Vicissitude",
        "Visceratika",
        "Vision",
    ]


def test_card_variants():
    sacha_vykos = {"Name": "Sascha Vykos, The Angel of Caine"}
    sacha_vykos_adv = {"Name": "Sascha Vykos, The Angel of Caine", "Adv": "Advanced"}
    praxis_athens = {"Name": "Praxis Seizure: Athens"}
    the_unnamed = {"Name": "unnamed, The"}
    the_line = {"Name": "Line, The"}
    sebastien_goulet = {
        "Name": "Sébastien Goulet",
        "Aka": "Sébastian Goulet",
        "Adv": "",
    }
    sebastien_goulet_adv = {
        "Name": "Sébastien Goulet",
        "Aka": "Sébastian Goulet",
        "Adv": "Advanced",
    }
    rumor_mill = {"Name": "Rumor Mill, Tabloid Newspaper, The"}
    sacre_coeur = {
        "Name": "Sacré-Cœur Cathedral, France",
        "Aka": "Sacre-Cour Cathedral, France",
    }

    fourth_tradition = {
        "Name": "Fourth Tradition: The Accounting",
        "Aka": "Fourth Tradition: The Accounting, The",
    }
    louvre = {"Name": "Louvre, Paris, The"}

    def sorted_variant(card, safe=True):
        return sorted(n.lower() for n in vtes.VTES.get_name_variants(card, safe))

    # "," suffixes in vampire names are common, and often omitted in deck lists
    assert sorted_variant(sacha_vykos) == [
        "sascha vykos",
        "sascha vykos, the angel of caine",
    ]
    # the (adv) suffix should always be present, even when suffix is removed
    assert sorted_variant(sacha_vykos_adv) == [
        "sascha vykos (adv)",
        "sascha vykos, the angel of caine (adv)",
    ]
    # ":" suffixes should not be removed because of this
    assert sorted_variant(praxis_athens) == ["praxis seizure: athens"]
    # ", The" suffix produces two variants : "The " prefix and omission.
    assert sorted_variant(the_unnamed) == ["the unnamed", "unnamed", "unnamed, the"]
    # Do not omit the "The" particle on too short a name
    assert sorted_variant(the_line) == ["line, the", "the line"]
    # Unless safe is False
    assert sorted_variant(the_line, safe=False) == ["line", "line, the", "the line"]
    # Produce ascii variants of "Aka" variant ("sEbastiAn")
    assert sorted_variant(sebastien_goulet) == [
        "sebastian goulet",
        "sebastien goulet",
        "sébastian goulet",
        "sébastien goulet",
    ]
    # the (adv) suffix should be present in all variants, for the advanced form
    assert sorted_variant(sebastien_goulet_adv) == [
        "sebastian goulet (adv)",
        "sebastien goulet (adv)",
        "sébastian goulet (adv)",
        "sébastien goulet (adv)",
    ]
    # multiple commas produce a lot of variants
    assert sorted_variant(rumor_mill) == [
        "rumor mill",
        "rumor mill, tabloid newspaper",
        "rumor mill, tabloid newspaper, the",
        "the rumor mill",
        "the rumor mill, tabloid newspaper",
    ]
    # The "The" omission variant is not included if the base name is too short,
    # even in multiple commas cases.
    assert sorted_variant(louvre) == [
        "louvre, paris",
        "louvre, paris, the",
        "the louvre",
        "the louvre, paris",
    ]
    assert sorted_variant(louvre, safe=False) == [
        "louvre",
        "louvre, paris",
        "louvre, paris, the",
        "the louvre",
        "the louvre, paris",
    ]
    # mixing commas, non-ASCII and "Aka" produces a lot of variants, too.
    # Note we do not produce "partial" unidecoded variants, like for example
    # "sacré-coeur" (keep the accent, asciify "œ").
    # This will fuzzy match "sacre-coeur" though, so this is good enough.
    assert sorted_variant(sacre_coeur) == [
        "sacre-coeur cathedral",
        "sacre-coeur cathedral, france",
        "sacre-cour cathedral",
        "sacre-cour cathedral, france",
        "sacré-cœur cathedral",
        "sacré-cœur cathedral, france",
    ]
    # ", The" suffix in "Aka" produces a variant with "The " prefix.
    # Note the base name is yielded twice because "Aka" adds a ", The" suffix,
    # which me produce a variant for, without the suffix.
    # Duplicates are not an issue, since we work with dicts.
    # We do not get the simple "fourth tradition" variant, see below.
    assert sorted_variant(fourth_tradition) == [
        "fourth tradition: the accounting",
        "fourth tradition: the accounting",
        "fourth tradition: the accounting, the",
        "the fourth tradition: the accounting",
    ]


def test_deck_display():
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2010tcdbng.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert (
        vtes.VTES.deck_to_txt(TWDA["2010tcdbng"])
        == """Trading Card Day
Bad Naumheim, Germany
May 8th 2010
2R+F
10 players
Rudolf Scholz

-- 4VP in final

Deck Name: The Storage Procurers
Allies with Flash Grenades to keep troubles at bay.
Storage Annex for card efficiency and a structured hand. Weenies and
Midcaps with Obfuscate and/or Dominate to oust via Conditionings and
Deflections.


-- Crypt: (12 cards)
---------------------------------------
1  Gilbert Duane                       7  AUS DOM OBF               Malkavian:1
1  Mariel, Lady Thunder                7  aus tha DOM OBF           Malkavian:1
1  Badr al-Budur                       5  cel dom qui OBF           Assamite:2
1  Count Ormonde                       5  dom pre ser OBF           Follower of Set:2
1  Didi Meyers                         5  aus cel obf DOM           Malkavian:1
1  Zebulon                             5  aus dom pro OBF           Malkavian:1
1  Dimple                              2  obf                       Nosferatu:1
1  Mustafa Rahman                      2  dom                       Tremere:2
1  Normal                              2  obf                       Malkavian:1
1  Ohanna                              2  dom                       Malkavian:2
1  Samson                              2  dom                       Ventrue antitribu:2
1  Basil                               1  obf                       Pander:2
-- Library (87)
-- Master (19)
6  Storage Annex           -- great card! usually underestimated
3  Sudden Reversal
3  Vessel
2  Charisma
2  Perfectionist
1  Channel 10
1  Creepshow Casino
1  KRCG News Radio
-- Action Modifier (19)
7  Conditioning            -- should be more!
6  Cloak the Gathering
4  Veil the Legions
2  Lost in Crowds
-- Combat (8)
8  Concealed Weapon
-- Reaction (16)
7  Deflection
7  On the Qui Vive
2  Delaying Tactics
-- Equipment (9)
8  Flash Grenade           -- brings fear to the methuselahs rather than to minions
1  Deer Rifle
-- Ally (12)
6  Procurer
1  Carlton Van Wyk
1  Gregory Winter
1  Impundulu
1  Muddled Vampire Hunter
1  Ossian
1  Young Bloods
-- Event (4)
1  FBI Special Affairs Division
1  Hunger Moon
1  Restricted Vitae
1  The Unmasking"""
    )


def test_search():
    # all registered values for reference (must match OpenAPI schema)
    assert sorted(vtes.VTES.search["type"].keys()) == [
        "action",
        "action modifier",
        "ally",
        "combat",
        "conviction",
        "crypt",
        "equipment",
        "event",
        "imbued",
        "library",
        "master",
        "political action",
        "power",
        "reaction",
        "retainer",
        "vampire",
    ]
    assert sorted(vtes.VTES.search["trait"]) == [
        "1 vote",
        "2 votes",
        "amsterdam",
        "anarch",
        "aragon",
        "archbishop",
        "athens",
        "atlanta",
        "barcelona",
        "baron",
        "berlin",
        "bishop",
        "black hand",
        "boston",
        "brussels",
        "budapest",
        "cairo",
        "camarilla",
        "canberra",
        "cardinal",
        "chicago",
        "chicago ",
        "cleveland",
        "columbus",
        "cordoba",
        "corte",
        "dallas",
        "detroit",
        "dublin",
        "fortaleza",
        "frankfurt",
        "geneva",
        "glasgow",
        "guadalajara",
        "guatemala city",
        "houston",
        "imperator",
        "independent",
        "infernal",
        "inner circle",
        "istanbul",
        "justicar",
        "kholo",
        "laibon",
        "liaison",
        "lisbon",
        "london",
        "los angeles",
        "magaji",
        "manila",
        "mexico city",
        "miami",
        "milan",
        "milwaukee",
        "monaco",
        "montreal",
        "new york",
        "paris",
        "perth",
        "philadelphia",
        "pittsburgh",
        "port-au-prince",
        "prague",
        "primogen",
        "prince",
        "priscus",
        "red list",
        "regent",
        "rome",
        "sabbat",
        "san diego",
        "scarce",
        "seattle",
        "seraph",
        "slave",
        "sterile",
        "stockholm",
        "strasbourg",
        "sydney",
        "toronto",
        "venice",
        "versailles",
        "washington, d.c.",
    ]
    assert sorted(vtes.VTES.search["discipline"]) == [
        "*",
        "ANIMALISM",
        "AUSPEX",
        "CELERITY",
        "CHIMERSTRY",
        "DAIMOINON",
        "DEMENTATION",
        "DOMINATE",
        "FORTITUDE",
        "MELPOMINEE",
        "MYTHERCERIA",
        "NECROMANCY",
        "OBEAH",
        "OBFUSCATE",
        "OBTENEBRATION",
        "POTENCE",
        "PRESENCE",
        "PROTEAN",
        "QUIETUS",
        "SANGUINUS",
        "SERPENTIS",
        "SPIRITUS",
        "TEMPORIS",
        "THANATOSIS",
        "THAUMATURGY",
        "VALEREN",
        "VICISSITUDE",
        "VISCERATIKA",
        "abombwe",
        "animalism",
        "auspex",
        "celerity",
        "chimerstry",
        "daimoinon",
        "defense",
        "dementation",
        "dominate",
        "flight",
        "fortitude",
        "innocence",
        "judgment",
        "maleficia",
        "martyrdom",
        "melpominee",
        "mytherceria",
        "necromancy",
        "none",
        "obeah",
        "obfuscate",
        "obtenebration",
        "potence",
        "presence",
        "protean",
        "quietus",
        "redemption",
        "sanguinus",
        "serpentis",
        "spiritus",
        "striga",
        "temporis",
        "thanatosis",
        "thaumaturgy",
        "valeren",
        "vengeance",
        "vicissitude",
        "visceratika",
        "vision",
    ]
    assert sorted(vtes.VTES.search["clan"]) == [
        "abomination",
        "ahrimane",
        "akunanse",
        "assamite",
        "avenger",
        "baali",
        "blood brother",
        "brujah",
        "brujah antitribu",
        "caitiff",
        "daughter of cacophony",
        "defender",
        "follower of set",
        "gangrel",
        "gangrel antitribu",
        "gargoyle",
        "giovanni",
        "guruhi",
        "harbinger of skulls",
        "innocent",
        "ishtarri",
        "judge",
        "kiasyd",
        "lasombra",
        "malkavian",
        "malkavian antitribu",
        "martyr",
        "nagaraja",
        "none",
        "nosferatu",
        "nosferatu antitribu",
        "osebo",
        "pander",
        "ravnos",
        "redeemer",
        "salubri",
        "salubri antitribu",
        "samedi",
        "toreador",
        "toreador antitribu",
        "tremere",
        "tremere antitribu",
        "true brujah",
        "tzimisce",
        "ventrue",
        "ventrue antitribu",
        "visionary",
    ]
    assert sorted(vtes.VTES.search["group"].keys()) == [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "any",
    ]
    assert sorted(vtes.VTES.search["capacity"].keys()) == [
        "+1",
        "-1",
        "-2",
        "0",
        "1",
        "10",
        "11",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
    ]
    # some tricky cards test (add cards for NR tests)
    # providing a stealth action does not register as "stealth" bonus
    assert vtes.VTES["Tracker's Mark"]["Id"] in vtes.VTES.search["intercept"]
    assert vtes.VTES["Tracker's Mark"]["Id"] not in vtes.VTES.search["stealth"]
    assert vtes.VTES["Brain Wash"]["Id"] not in vtes.VTES.search["stealth"]
