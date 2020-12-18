from krcg import cards


def test_card_variants():
    sacha_vykos = {
        "Id": "201244",
        "Name": "Sascha Vykos, The Angel of Caine",
        "Set": "Jyhad",
    }
    sacha_vykos_adv = {
        "Id": "201244",
        "Name": "Sascha Vykos, The Angel of Caine",
        "Adv": "Advanced",
        "Set": "Jyhad",
    }
    praxis_athens = {"Id": "101448", "Name": "Praxis Seizure: Athens", "Set": "Jyhad"}
    the_unnamed = {"Id": "201411", "Name": "unnamed, The", "Set": "Jyhad"}
    the_line = {"Id": "101110", "Name": "Line, The", "Set": "Jyhad"}
    sebastien_goulet = {
        "Id": "201257",
        "Name": "Sébastien Goulet",
        "Aka": "Sébastian Goulet",
        "Adv": "",
        "Set": "Jyhad",
    }
    sebastien_goulet_adv = {
        "Id": "201258",
        "Name": "Sébastien Goulet",
        "Aka": "Sébastian Goulet",
        "Adv": "Advanced",
        "Set": "Jyhad",
    }
    rumor_mill = {
        "Id": "101662",
        "Name": "Rumor Mill, Tabloid Newspaper, The",
        "Set": "Jyhad",
    }
    sacre_coeur = {
        "Id": "101670",
        "Name": "Sacré-Cœur Cathedral, France",
        "Aka": "Sacre-Cour Cathedral, France",
        "Set": "Jyhad",
    }

    fourth_tradition = {
        "Id": "100782",
        "Name": "Fourth Tradition: The Accounting",
        "Aka": "Fourth Tradition: The Accounting, The",
        "Set": "Jyhad",
    }
    louvre = {"Id": "101127", "Name": "Louvre, Paris, The", "Set": "Jyhad"}
    ankara_citadel = {
        "Id": "100071",
        "Name": "Ankara Citadel, Turkey, The",
        "Set": "Jyhad",
    }

    def sorted_variant(card):
        card.setdefault("Aka", "")
        card.setdefault("Clan", "")
        card.setdefault("Type", "")
        card.setdefault("Disciplines", "")
        card.setdefault("Card Text", "")
        card.setdefault("Set", "")
        card.setdefault("Banned", "")
        card.setdefault("Artist", "")
        card = cards.Card._from_vekn({"Jyhad": cards.Set(name="Jyhad")}, card)
        card_map = cards.CardMap()
        card_map.add(card)
        return sorted(k for k in card_map._dict.keys() if isinstance(k, str))

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
    # assert sorted_variant(the_line, safe=False) == ["line", "line, the", "the line"]
    # Produce ascii variants of "Aka" variant ("sEbastiAn")
    assert sorted_variant(sebastien_goulet) == [
        "sebastian goulet",
        "sebastien goulet",
        # "sébastian goulet",
        # "sébastien goulet",
    ]
    # the (adv) suffix should be present in all variants, for the advanced form
    assert sorted_variant(sebastien_goulet_adv) == [
        "sebastian goulet (adv)",
        "sebastien goulet (adv)",
        # "sébastian goulet (adv)",
        # "sébastien goulet (adv)",
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
    # assert sorted_variant(louvre, safe=False) == [
    #     "louvre",
    #     "louvre, paris",
    #     "louvre, paris, the",
    #     "the louvre",
    #     "the louvre, paris",
    # ]
    # mixing commas, non-ASCII and "Aka" produces a lot of variants, too.
    # Note we do not produce "partial" unidecoded variants, like for example
    # "sacré-coeur" (keep the accent, asciify "œ").
    # This will fuzzy match "sacre-coeur" though, so this is good enough.
    assert sorted_variant(sacre_coeur) == [
        "sacre-coeur cathedral",
        "sacre-coeur cathedral, france",
        "sacre-cour cathedral",
        "sacre-cour cathedral, france",
    ]
    # ", The" suffix in "Aka" produces a variant with "The " prefix.
    # Note the base name is yielded twice because "Aka" adds a ", The" suffix,
    # which me produce a variant for, without the suffix.
    # Duplicates are not an issue, since we work with dicts.
    # We do not get the simple "fourth tradition" variant, see below.
    assert sorted_variant(fourth_tradition) == [
        "fourth tradition: the accounting",
        "fourth tradition: the accounting, the",
        "the fourth tradition: the accounting",
    ]
    # translations do not show up on variants
    assert sorted_variant(ankara_citadel) == [
        "ankara citadel",
        "ankara citadel, turkey",
        "ankara citadel, turkey, the",
        "the ankara citadel",
        "the ankara citadel, turkey",
    ]
