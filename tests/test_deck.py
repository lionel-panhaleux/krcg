import os

from krcg import deck
from krcg import twda


def test_cards():
    d = deck.Deck()
    d.update({"Fame": 3})
    assert list(d.cards()) == [("Fame", 3)]


def test_cards_count():
    d = deck.Deck()
    d.update({"Fame": 3, "Bum's Rush": 10, "Crusher": 4})
    assert d.cards_count() == 17


def test_deck_display():
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2010tcdbng.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert (
        TWDA["2010tcdbng"].to_txt(format="twd")
        == """Trading Card Day
Bad Naumheim, Germany
May 8th 2010
2R+F
10 players
Rudolf Scholz

-- 4vp in the final

Deck Name: The Storage Procurers

Description: Allies with Flash Grenades to keep troubles at bay.
Storage Annex for card efficiency and a structured hand. Weenies and
Midcaps with Obfuscate and/or Dominate to oust via Conditionings and
Deflections.

Crypt (12 cards, min=7, max=24, avg=3.75)
-----------------------------------------
1x Gilbert Duane          7 AUS DOM OBF      prince  Malkavian:1
1x Mariel, Lady Thunder   7 DOM OBF aus tha          Malkavian:1
1x Badr al-Budur          5 OBF cel dom qui          Banu Haqim:2
1x Count Ormonde          5 OBF dom pre ser          Ministry:2
1x Didi Meyers            5 DOM aus cel obf          Malkavian:1
1x Zebulon                5 OBF aus dom pro          Malkavian:1
1x Dimple                 2 obf                      Nosferatu:1
1x Mustafa Rahman         2 dom                      Tremere:2
1x Normal                 2 obf                      Malkavian:1
1x Ohanna                 2 dom                      Malkavian:2
1x Samson                 2 dom                      Ventrue antitribu:2
1x Basil                  1 obf                      Pander:2

Library (87 cards)
Master (19; 3 trifle)
1x Channel 10
2x Charisma
1x Creepshow Casino
1x KRCG News Radio
2x Perfectionist
6x Storage Annex           -- great card! usually underestimated
3x Sudden Reversal
3x Vessel

Ally (12)
1x Carlton Van Wyk
1x Gregory Winter
1x Impundulu
1x Muddled Vampire Hunter
1x Ossian
6x Procurer
1x Young Bloods

Equipment (9)
1x Deer Rifle
8x Flash Grenade           -- brings fear to the methuselahs rather than to minions

Action Modifier (19)
6x Cloak the Gathering
7x Conditioning            -- should be more!
2x Lost in Crowds
4x Veil the Legions

Reaction (16)
7x Deflection
2x Delaying Tactics
7x On the Qui Vive

Combat (8)
8x Concealed Weapon

Event (4)
1x FBI Special Affairs Division
1x Hunger Moon
1x Restricted Vitae
1x Unmasking, The"""
    )
    assert (
        TWDA["2010tcdbng"].to_txt(format="jol")
        == """1x Gilbert Duane
1x Mariel, Lady Thunder
1x Badr al-Budur
1x Count Ormonde
1x Didi Meyers
1x Zebulon
1x Dimple
1x Mustafa Rahman
1x Normal
1x Ohanna
1x Samson
1x Basil

1x Channel 10
2x Charisma
1x Creepshow Casino
1x KRCG News Radio
2x Perfectionist
6x Storage Annex
3x Sudden Reversal
3x Vessel
1x Carlton Van Wyk
1x Gregory Winter
1x Impundulu
1x Muddled Vampire Hunter
1x Ossian
6x Procurer
1x Young Bloods
1x Deer Rifle
8x Flash Grenade
6x Cloak the Gathering
7x Conditioning
2x Lost in Crowds
4x Veil the Legions
7x Deflection
2x Delaying Tactics
7x On the Qui Vive
8x Concealed Weapon
1x FBI Special Affairs Division
1x Hunger Moon
1x Restricted Vitae
1x Unmasking, The"""
    )
    assert (
        TWDA["2010tcdbng"].to_txt(format="lackey")
        == """1	Channel 10
2	Charisma
1	Creepshow Casino
1	KRCG News Radio
2	Perfectionist
6	Storage Annex
3	Sudden Reversal
3	Vessel
1	Carlton Van Wyk
1	Gregory Winter
1	Impundulu
1	Muddled Vampire Hunter
1	Ossian
6	Procurer
1	Young Bloods
1	Deer Rifle
8	Flash Grenade
6	Cloak the Gathering
7	Conditioning
2	Lost in Crowds
4	Veil the Legions
7	Deflection
2	Delaying Tactics
7	On the Qui Vive
8	Concealed Weapon
1	FBI Special Affairs Division
1	Hunger Moon
1	Restricted Vitae
1	Unmasking, The
Crypt:
1	Gilbert Duane
1	Mariel, Lady Thunder
1	Badr al-Budur
1	Count Ormonde
1	Didi Meyers
1	Zebulon
1	Dimple
1	Mustafa Rahman
1	Normal
1	Ohanna
1	Samson
1	Basil"""
    )


def test_from_amaranth():
    d = deck.Deck.from_amaranth("4d3aa426-70da-44b7-8cb7-92377a1a0dbd")
    assert d.to_json() == {
        "id": "4d3aa426-70da-44b7-8cb7-92377a1a0dbd",
        "date": "2020-12-28",
        "name": "First Blood: Tremere",
        "author": "BCP",
        "comments": (
            "https://blackchantry.com/"
            "How%20to%20play%20the%20First%20Blood%20Tremere%20deck.pdf"
        ),
        "crypt": {
            "count": 12,
            "cards": [
                {"id": 201020, "count": 2, "name": "Muhsin Samir"},
                {"id": 201213, "count": 2, "name": "Rutor"},
                {"id": 201388, "count": 2, "name": "Troius"},
                {"id": 201501, "count": 2, "name": "Zane"},
                {"id": 200025, "count": 2, "name": "Aidan Lyle"},
                {"id": 200280, "count": 2, "name": "Claus Wegener"},
            ],
        },
        "library": {
            "count": 86,
            "cards": [
                {
                    "type": "Master",
                    "count": 9,
                    "cards": [
                        {"id": 100015, "count": 1, "name": "Academic Hunting Ground"},
                        {"id": 100081, "count": 1, "name": "Arcane Library"},
                        {"id": 100199, "count": 4, "name": "Blood Doll"},
                        {"id": 100329, "count": 1, "name": "Chantry"},
                        {"id": 102092, "count": 2, "name": "Vast Wealth"},
                    ],
                },
                {
                    "type": "Action",
                    "count": 12,
                    "cards": [
                        {"id": 100845, "count": 12, "name": "Govern the Unaligned"}
                    ],
                },
                {
                    "type": "Ally",
                    "count": 1,
                    "cards": [{"id": 101963, "count": 1, "name": "Thadius Zho"}],
                },
                {
                    "type": "Equipment",
                    "count": 7,
                    "cards": [
                        {"id": 100001, "count": 4, "name": ".44 Magnum"},
                        {"id": 101014, "count": 1, "name": "Ivory Bow"},
                        {"id": 101856, "count": 2, "name": "Sport Bike"},
                    ],
                },
                {
                    "type": "Retainer",
                    "count": 1,
                    "cards": [{"id": 100335, "count": 1, "name": "Charnas the Imp"}],
                },
                {
                    "type": "Action Modifier",
                    "count": 6,
                    "cards": [{"id": 100236, "count": 6, "name": "Bonding"}],
                },
                {
                    "type": "Reaction",
                    "count": 30,
                    "cards": [
                        {"id": 100644, "count": 4, "name": "Enhanced Senses"},
                        {"id": 100760, "count": 5, "name": "Forced Awakening"},
                        {"id": 101321, "count": 5, "name": "On the Qui Vive"},
                        {"id": 101475, "count": 4, "name": "Precognition"},
                        {"id": 101850, "count": 4, "name": "Spirit's Touch"},
                        {"id": 101949, "count": 8, "name": "Telepathic Misdirection"},
                    ],
                },
                {
                    "type": "Combat",
                    "count": 20,
                    "cards": [
                        {"id": 100077, "count": 8, "name": "Apportation"},
                        {"id": 101966, "count": 10, "name": "Theft of Vitae"},
                        {"id": 102139, "count": 2, "name": "Walk of Flame"},
                    ],
                },
            ],
        },
    }


def test_from_vdb():
    d = deck.Deck.from_vdb("b798e734fff7404085f7b01ad2ccb479")
    assert d.to_json() == {
        "id": "b798e734fff7404085f7b01ad2ccb479",
        "date": "2021-01-11",
        "name": "First Blood Tremere",
        "author": "BCP",
        "comments": (
            "https://blackchantry.com/"
            "How%20to%20play%20the%20First%20Blood%20Tremere%20deck.pdf"
        ),
        "crypt": {
            "count": 12,
            "cards": [
                {"id": 200025, "count": 2, "name": "Aidan Lyle"},
                {"id": 200280, "count": 2, "name": "Claus Wegener"},
                {"id": 201020, "count": 2, "name": "Muhsin Samir"},
                {"id": 201213, "count": 2, "name": "Rutor"},
                {"id": 201388, "count": 2, "name": "Troius"},
                {"id": 201501, "count": 2, "name": "Zane"},
            ],
        },
        "library": {
            "count": 86,
            "cards": [
                {
                    "type": "Master",
                    "count": 9,
                    "cards": [
                        {"id": 100015, "count": 1, "name": "Academic Hunting Ground"},
                        {"id": 100081, "count": 1, "name": "Arcane Library"},
                        {"id": 100199, "count": 4, "name": "Blood Doll"},
                        {"id": 100329, "count": 1, "name": "Chantry"},
                        {"id": 102092, "count": 2, "name": "Vast Wealth"},
                    ],
                },
                {
                    "type": "Action",
                    "count": 12,
                    "cards": [
                        {"id": 100845, "count": 12, "name": "Govern the Unaligned"}
                    ],
                },
                {
                    "type": "Ally",
                    "count": 1,
                    "cards": [{"id": 101963, "count": 1, "name": "Thadius Zho"}],
                },
                {
                    "type": "Equipment",
                    "count": 7,
                    "cards": [
                        {"id": 100001, "count": 4, "name": ".44 Magnum"},
                        {"id": 101014, "count": 1, "name": "Ivory Bow"},
                        {"id": 101856, "count": 2, "name": "Sport Bike"},
                    ],
                },
                {
                    "type": "Retainer",
                    "count": 1,
                    "cards": [{"id": 100335, "count": 1, "name": "Charnas the Imp"}],
                },
                {
                    "type": "Action Modifier",
                    "count": 6,
                    "cards": [{"id": 100236, "count": 6, "name": "Bonding"}],
                },
                {
                    "type": "Reaction",
                    "count": 30,
                    "cards": [
                        {"id": 100644, "count": 4, "name": "Enhanced Senses"},
                        {"id": 100760, "count": 5, "name": "Forced Awakening"},
                        {"id": 101321, "count": 5, "name": "On the Qui Vive"},
                        {"id": 101475, "count": 4, "name": "Precognition"},
                        {"id": 101850, "count": 4, "name": "Spirit's Touch"},
                        {"id": 101949, "count": 8, "name": "Telepathic Misdirection"},
                    ],
                },
                {
                    "type": "Combat",
                    "count": 20,
                    "cards": [
                        {"id": 100077, "count": 8, "name": "Apportation"},
                        {"id": 101966, "count": 10, "name": "Theft of Vitae"},
                        {"id": 102139, "count": 2, "name": "Walk of Flame"},
                    ],
                },
            ],
        },
    }


def test_deck_to_vdb():
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2010tcdbng.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["2010tcdbng"].to_vdb() == (
        "https://vdb.im/decks?name=The+Storage+Procurers&author=Rudolf+Scholz#"
        "200517=1;200929=1;200161=1;200295=1;200343=1;201503=1;200346=1;201027=1;"
        "201065=1;201073=1;201231=1;200173=1;100327=1;100332=2;100444=1;101067=1;"
        "101388=2;101877=6;101896=3;102113=3;100298=1;100855=1;100966=1;101250=1;"
        "101333=1;101491=6;102202=1;100516=1;100745=8;100362=6;100401=7;101125=2;"
        "102097=4;100518=7;100519=2;101321=7;100392=8;100709=1;100944=1;101614=1;"
        "102079=1"
    )


def test_deck_to_minimal_json():
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2010tcdbng.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["2010tcdbng"].to_minimal_json() == {
        "id": "2010tcdbng",
        "name": "The Storage Procurers",
        "cards": {
            "200517": 1,
            "200929": 1,
            "200161": 1,
            "200295": 1,
            "200343": 1,
            "201503": 1,
            "200346": 1,
            "201027": 1,
            "201065": 1,
            "201073": 1,
            "201231": 1,
            "200173": 1,
            "100327": 1,
            "100332": 2,
            "100444": 1,
            "101067": 1,
            "101388": 2,
            "101877": 6,
            "101896": 3,
            "102113": 3,
            "100298": 1,
            "100855": 1,
            "100966": 1,
            "101250": 1,
            "101333": 1,
            "101491": 6,
            "102202": 1,
            "100516": 1,
            "100745": 8,
            "100362": 6,
            "100401": 7,
            "101125": 2,
            "102097": 4,
            "100518": 7,
            "100519": 2,
            "101321": 7,
            "100392": 8,
            "100709": 1,
            "100944": 1,
            "101614": 1,
            "102079": 1,
        },
    }
