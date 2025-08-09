import pytest
import warnings
from krcg import cards


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_card_variants():
    sacha_vykos = {
        "Id": "201244",
        "Name": "Sascha Vykos, The Angel of Caine",
        "Group": "2",
        "Set": "Jyhad",
    }
    sacha_vykos_adv = {
        "Id": "201245",
        "Name": "Sascha Vykos, The Angel of Caine",
        "Group": "2",
        "Adv": "Advanced",
        "Set": "Jyhad",
    }
    praxis_athens = {"Id": "101448", "Name": "Praxis Seizure: Athens", "Set": "Jyhad"}
    the_unnamed = {"Id": "201411", "Name": "unnamed, The", "Group": "6", "Set": "Jyhad"}
    anarch_convert = {
        "Id": "200076",
        "Name": "Anarch Convert",
        "Group": "ANY",
        "Set": "Jyhad",
    }
    the_line = {"Id": "101110", "Name": "Line, The", "Set": "Jyhad"}
    sebastien_goulet = {
        "Id": "201257",
        "Name": "Sébastien Goulet",
        "Aka": "Sébastian Goulet",
        "Group": "3",
        "Adv": "",
        "Set": "Jyhad",
    }
    sebastien_goulet_adv = {
        "Id": "201258",
        "Name": "Sébastien Goulet",
        "Aka": "Sébastian Goulet",
        "Group": "3",
        "Adv": "Advanced",
        "Set": "Jyhad",
    }
    theo_bell = {
        "Id": "201362",
        "Name": "Theo Bell",
        "Group": "2",
        "Set": "Jyhad",
    }
    theo_bell_adv = {
        "Id": "201363",
        "Name": "Theo Bell",
        "Group": "2",
        "Adv": "Advanced",
        "Set": "Jyhad",
    }
    theo_bell_g6 = {
        "Id": "201613",
        "Name": "Theo Bell",
        "Group": "6",
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
    card_map = cards.CardMap()

    def add_card(card_map, data):
        data.setdefault("Aka", "")
        data.setdefault("Clan", "")
        data.setdefault("Type", "")
        data.setdefault("Disciplines", "")
        data.setdefault("Card Text", "")
        data.setdefault("Banned", "")
        data.setdefault("Artist", "")
        card = cards.Card()
        card.from_vekn(data)
        card_map[card.id] = card

    add_card(card_map, sacha_vykos)
    add_card(card_map, sacha_vykos_adv)
    add_card(card_map, praxis_athens)
    add_card(card_map, the_unnamed)
    add_card(card_map, anarch_convert)
    add_card(card_map, the_line)
    add_card(card_map, sebastien_goulet)
    add_card(card_map, sebastien_goulet_adv)
    add_card(card_map, theo_bell)
    add_card(card_map, theo_bell_adv)
    add_card(card_map, theo_bell_g6)
    add_card(card_map, rumor_mill)
    add_card(card_map, sacre_coeur)
    add_card(card_map, fourth_tradition)
    add_card(card_map, louvre)
    add_card(card_map, ankara_citadel)

    card_map._set_enriched_properties()
    card_map._map_names()

    def sorted_variant(data):
        return sorted(
            k
            for k, v in card_map._dict.items()
            if isinstance(k, str) and v.id == int(data["Id"])
        )

    # "," suffixes in vampire names are common, and often omitted in deck lists
    assert sorted_variant(sacha_vykos) == [
        "sascha vykos",
        "sascha vykos (g2)",
        "sascha vykos, the angel of caine",
        "sascha vykos, the angel of caine (g2)",
    ]
    # the (adv) suffix should always be present, even when suffix is removed
    assert sorted_variant(sacha_vykos_adv) == [
        "sascha vykos (adv)",
        "sascha vykos (g2 adv)",
        "sascha vykos, the angel of caine (adv)",
        "sascha vykos, the angel of caine (g2 adv)",
    ]
    # ":" suffixes should not be removed because of this
    assert sorted_variant(praxis_athens) == ["praxis seizure: athens"]
    # ", The" suffix produces two variants : "The " prefix and omission.
    assert sorted_variant(the_unnamed) == [
        "the unnamed",
        "the unnamed (g6)",
        "unnamed",
        "unnamed (g6)",
        "unnamed, the",
        "unnamed, the (g6)",
    ]
    assert sorted_variant(anarch_convert) == [
        "anarch convert",
        "anarch convert (any)",
    ]
    # Do not omit the "The" particle on too short a name
    assert sorted_variant(the_line) == ["line, the", "the line"]
    # Produce ascii variants of "Aka" variant ("sEbastiAn")
    assert sorted_variant(sebastien_goulet) == [
        "sebastian goulet",
        "sebastian goulet (g3)",
        "sebastien goulet",
        "sebastien goulet (g3)",
    ]
    # the (adv) suffix should be present in all variants, for the advanced form
    assert sorted_variant(sebastien_goulet_adv) == [
        "sebastian goulet (adv)",
        "sebastian goulet (g3 adv)",
        "sebastien goulet (adv)",
        "sebastien goulet (g3 adv)",
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
    ]
    # ", The" suffix in "Aka" produces a variant with "The " prefix.
    # Note the base name is yielded twice because "Aka" adds a ", The" suffix,
    # which me produce a variant for, without the suffix.
    # Duplicates are not an issue, since we work with dicts.
    # We do not get the simple "fourth tradition" variant, ":" suffix cannot be removed
    # because it is the meaningful part in of crusade/praxis/powerbase cards
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


def test_load_from_static_server():
    with warnings.catch_warnings(record=True) as wrec:
        warnings.simplefilter("always")
        cm = cards.CardMap()
        cm.load()
    assert not wrec
    # Ensure we have at least one well-known card present
    assert 200076 in cm  # Anarch Convert
    assert cm[200076].name.lower().startswith("anarch convert")


def test_load_from_vekn_github_default(monkeypatch):
    # Default path should use GitHub when neither LOCAL_CARDS nor VEKN_NET_CSV is set
    monkeypatch.delenv("LOCAL_CARDS", raising=False)
    monkeypatch.delenv("VEKN_NET_CSV", raising=False)
    with warnings.catch_warnings(record=True) as wrec:
        warnings.simplefilter("always")
        cm = cards.CardMap()
        cm.load_from_vekn()
    assert not wrec
    assert 200076 in cm  # Anarch Convert


def test_load_from_vekn_vekn_net(monkeypatch):
    # Force using official VEKN.net zip
    monkeypatch.delenv("LOCAL_CARDS", raising=False)
    monkeypatch.setenv("VEKN_NET_CSV", "1")
    with warnings.catch_warnings(record=True) as wrec:
        warnings.simplefilter("always")
        cm = cards.CardMap()
        cm.load_from_vekn()
    assert not wrec
    assert 200076 in cm  # Anarch Convert


def test_load_from_vekn_local(monkeypatch):
    # Use local packaged CSVs under the `cards` package
    monkeypatch.setenv("LOCAL_CARDS", "1")
    monkeypatch.delenv("VEKN_NET_CSV", raising=False)
    with warnings.catch_warnings(record=True) as wrec:
        warnings.simplefilter("always")
        cm = cards.CardMap()
        cm.load_from_vekn()
    assert not wrec
    assert 200076 in cm  # Anarch Convert
