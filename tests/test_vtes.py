from src import vtes


def test_init():
    vtes.VTES.load_from_vekn()
    vtes.VTES.configure()
    assert sorted(vtes.VTES.trait_choices("Discipline")) == [
        "Abombwe",
        "Animalism",
        "Auspex",
        "Celerity",
        "Chimerstry",
        "Combo",
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

    def sorted_variant(card):
        return sorted(n.lower() for n in vtes.VTES.get_name_variants(card))

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
