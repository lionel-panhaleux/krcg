"""Test deck."""

import aiohttp

from krcg import providers
from krcg import twda
from krcg import utils
from krcg import vtes

import pytest


def test_deck_display() -> None:
    """Test the deck display."""
    TWDA = twda.TWDA
    assert (
        providers.serialize_txt(TWDA["2010tcdbng"])
        == """Trading Card Day
Bad Nauheim, Germany
May 8th 2010
Standard 2R+F
10 players
Rudolf Scholz

-- +4!

Deck Name: The Storage Procurers

Description: Allies with Flash Grenades to keep troubles at bay.
Storage Annex for card efficiency and a structured hand. Weenies and
Midcaps with Obfuscate and/or Dominate to oust via Conditionings and
Deflections.

Crypt (12 cards)
----------------
1x Badr al-Budur
1x Basil
1x Count Ormonde
1x Didi Meyers
1x Dimple
1x Gilbert Duane (G1)
1x Mariel, Lady Thunder
1x Mustafa Rahman
1x Normal
1x Ohanna
1x Samson
1x Zebulon

Library (87 cards)
------------------

--Master (19)--
1x Channel 10
2x Charisma
1x Creepshow Casino
1x KRCG News Radio
2x Perfectionist
6x Storage Annex -- great card! usually underestimated
3x Sudden Reversal
3x Vessel

--Ally (12)--
1x Carlton Van Wyk
1x Gregory Winter
1x Impundulu
1x Muddled Vampire Hunter
1x Ossian
6x Procurer
1x Young Bloods

--Equipment (9)--
1x Deer Rifle
8x Flash Grenade -- brings fear to the methuselahs rather than to minions

--Action Modifier (19)--
6x Cloak the Gathering
7x Conditioning -- should be more!
2x Lost in Crowds
4x Veil the Legions

--Reaction (16)--
7x Deflection
2x Delaying Tactics
7x On the Qui Vive

--Combat (8)--
8x Concealed Weapon

--Event (4)--
1x FBI Special Affairs Division
1x Hunger Moon
1x Restricted Vitae
1x The Unmasking"""
    )
    assert (
        providers.serialize_twd(TWDA["2010tcdbng"], vtes.VTES.load_local())
        == """Trading Card Day
Bad Nauheim, Germany
May 8th 2010
2R+F
10 players
Rudolf Scholz

-- +4!

Deck Name: The Storage Procurers

Description: Allies with Flash Grenades to keep troubles at bay.
Storage Annex for card efficiency and a structured hand. Weenies and
Midcaps with Obfuscate and/or Dominate to oust via Conditionings and
Deflections.

Crypt (12 cards, min=7, max=24, avg=3.75)
-----------------------------------------
1x Gilbert Duane (G1)     7 AUS DOM OBF      prince  Malkavian:1
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
        providers.serialize_jol(TWDA["2010tcdbng"])
        == """1x Badr al-Budur
1x Basil
1x Count Ormonde
1x Didi Meyers
1x Dimple
1x Gilbert Duane (G1)
1x Mariel, Lady Thunder
1x Mustafa Rahman
1x Normal
1x Ohanna
1x Samson
1x Zebulon

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
        providers.serialize_lackey(TWDA["2010tcdbng"])
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
1	Badr al-Budur
1	Basil
1	Count Ormonde
1	Didi Meyers
1	Dimple
1	Gilbert Duane (G1)
1	Mariel, Lady Thunder
1	Mustafa Rahman
1	Normal
1	Ohanna
1	Samson
1	Zebulon"""
    )


@pytest.mark.asyncio
async def test_from_amaranth() -> None:
    """Test from amaranth.

    Skip the test if offline (cf. conftest).
    """
    VTES = vtes.VTES.load_local()
    async with aiohttp.ClientSession() as session:
        d = await providers.fetch(
            session,
            "https://amaranth.vtes.co.nz/deck/4d3aa426-70da-44b7-8cb7-92377a1a0dbd",
            VTES,
        )

    assert utils.jsonize(d) == {
        "id": "4d3aa426-70da-44b7-8cb7-92377a1a0dbd",
        "name": "First Blood: Tremere",
        "author": "BCP",
        "comment": (
            "https://blackchantry.com/"
            "How%20to%20play%20the%20First%20Blood%20Tremere%20deck.pdf"
        ),
        "cards": [
            {
                "count": 2,
                "id": 200025,
                "kind": "Crypt",
                "printed_name": "Aidan Lyle",
                "suffix": "G5",
                "types": ["Vampire"],
            },
            {
                "count": 2,
                "id": 200280,
                "kind": "Crypt",
                "printed_name": "Claus Wegener",
                "suffix": "G5",
                "types": ["Vampire"],
            },
            {
                "count": 2,
                "id": 201020,
                "kind": "Crypt",
                "printed_name": "Muhsin Samir",
                "suffix": "G4",
                "types": ["Vampire"],
            },
            {
                "count": 2,
                "id": 201213,
                "kind": "Crypt",
                "printed_name": "Rutor",
                "suffix": "G5",
                "types": ["Vampire"],
            },
            {
                "count": 2,
                "id": 201388,
                "kind": "Crypt",
                "printed_name": "Troius",
                "suffix": "G4",
                "types": ["Vampire"],
            },
            {
                "count": 2,
                "id": 201501,
                "kind": "Crypt",
                "printed_name": "Zane",
                "suffix": "G5",
                "types": ["Vampire"],
            },
            {
                "count": 4,
                "id": 100001,
                "kind": "Library",
                "printed_name": ".44 Magnum",
                "types": ["Equipment"],
            },
            {
                "count": 1,
                "id": 100015,
                "kind": "Library",
                "printed_name": "Academic Hunting Ground",
                "types": ["Master"],
            },
            {
                "count": 8,
                "id": 100077,
                "kind": "Library",
                "printed_name": "Apportation",
                "types": ["Combat"],
            },
            {
                "count": 1,
                "id": 100081,
                "kind": "Library",
                "printed_name": "Arcane Library",
                "types": ["Master"],
            },
            {
                "count": 4,
                "id": 100199,
                "kind": "Library",
                "printed_name": "Blood Doll",
                "types": ["Master"],
            },
            {
                "count": 6,
                "id": 100236,
                "kind": "Library",
                "printed_name": "Bonding",
                "types": ["Action Modifier"],
            },
            {
                "count": 1,
                "id": 100329,
                "kind": "Library",
                "printed_name": "Chantry",
                "types": ["Master"],
            },
            {
                "count": 1,
                "id": 100335,
                "kind": "Library",
                "printed_name": "Charnas the Imp",
                "types": ["Retainer"],
            },
            {
                "count": 4,
                "id": 100644,
                "kind": "Library",
                "printed_name": "Enhanced Senses",
                "types": ["Reaction"],
            },
            {
                "count": 5,
                "id": 100760,
                "kind": "Library",
                "printed_name": "Forced Awakening",
                "types": ["Reaction"],
            },
            {
                "count": 12,
                "id": 100845,
                "kind": "Library",
                "printed_name": "Govern the Unaligned",
                "types": ["Action"],
            },
            {
                "count": 1,
                "id": 101014,
                "kind": "Library",
                "printed_name": "Ivory Bow",
                "types": ["Equipment"],
            },
            {
                "count": 5,
                "id": 101321,
                "kind": "Library",
                "printed_name": "On the Qui Vive",
                "types": ["Reaction"],
            },
            {
                "count": 4,
                "id": 101475,
                "kind": "Library",
                "printed_name": "Precognition",
                "types": ["Reaction"],
            },
            {
                "count": 4,
                "id": 101850,
                "kind": "Library",
                "printed_name": "Spirit's Touch",
                "types": ["Reaction"],
            },
            {
                "count": 2,
                "id": 101856,
                "kind": "Library",
                "printed_name": "Sport Bike",
                "types": ["Equipment"],
            },
            {
                "count": 8,
                "id": 101949,
                "kind": "Library",
                "printed_name": "Telepathic Misdirection",
                "types": ["Reaction"],
            },
            {
                "count": 1,
                "id": 101963,
                "kind": "Library",
                "printed_name": "Thadius Zho",
                "types": ["Ally"],
            },
            {
                "count": 10,
                "id": 101966,
                "kind": "Library",
                "printed_name": "Theft of Vitae",
                "types": ["Combat"],
            },
            {
                "count": 2,
                "id": 102092,
                "kind": "Library",
                "printed_name": "Vast Wealth",
                "types": ["Master"],
            },
            {
                "count": 2,
                "id": 102139,
                "kind": "Library",
                "printed_name": "Walk of Flame",
                "types": ["Combat"],
            },
        ],
    }


@pytest.mark.asyncio
async def test_from_vdb() -> None:
    """Test from vdb.

    Skip the test if offline (cf. conftest).
    """
    VTES = vtes.VTES.load_local()
    async with aiohttp.ClientSession() as session:
        d = await providers.fetch(session, "https://vdb.im/decks/5b4312a1f", VTES)

    assert utils.jsonize(d) == {
        "id": "5b4312a1f",
        "author": "BCP",
        "name": "First Blood Tremere",
        "comment": (
            "https://blackchantry.com/"
            "How%20to%20play%20the%20First%20Blood%20Tremere%20deck.pdf"
        ),
        "cards": [
            {
                "count": 2,
                "id": 200025,
                "kind": "Crypt",
                "printed_name": "Aidan Lyle",
                "suffix": "G5",
                "types": ["Vampire"],
            },
            {
                "count": 2,
                "id": 200280,
                "kind": "Crypt",
                "printed_name": "Claus Wegener",
                "suffix": "G5",
                "types": ["Vampire"],
            },
            {
                "count": 2,
                "id": 201020,
                "kind": "Crypt",
                "printed_name": "Muhsin Samir",
                "suffix": "G4",
                "types": ["Vampire"],
            },
            {
                "count": 2,
                "id": 201213,
                "kind": "Crypt",
                "printed_name": "Rutor",
                "suffix": "G5",
                "types": ["Vampire"],
            },
            {
                "count": 2,
                "id": 201388,
                "kind": "Crypt",
                "printed_name": "Troius",
                "suffix": "G4",
                "types": ["Vampire"],
            },
            {
                "count": 2,
                "id": 201501,
                "kind": "Crypt",
                "printed_name": "Zane",
                "suffix": "G5",
                "types": ["Vampire"],
            },
            {
                "count": 4,
                "id": 100001,
                "kind": "Library",
                "printed_name": ".44 Magnum",
                "types": ["Equipment"],
            },
            {
                "count": 1,
                "id": 100015,
                "kind": "Library",
                "printed_name": "Academic Hunting Ground",
                "types": ["Master"],
            },
            {
                "count": 8,
                "id": 100077,
                "kind": "Library",
                "printed_name": "Apportation",
                "types": ["Combat"],
            },
            {
                "count": 1,
                "id": 100081,
                "kind": "Library",
                "printed_name": "Arcane Library",
                "types": ["Master"],
            },
            {
                "count": 4,
                "id": 100199,
                "kind": "Library",
                "printed_name": "Blood Doll",
                "types": ["Master"],
            },
            {
                "count": 6,
                "id": 100236,
                "kind": "Library",
                "printed_name": "Bonding",
                "types": ["Action Modifier"],
            },
            {
                "count": 1,
                "id": 100329,
                "kind": "Library",
                "printed_name": "Chantry",
                "types": ["Master"],
            },
            {
                "count": 1,
                "id": 100335,
                "kind": "Library",
                "printed_name": "Charnas the Imp",
                "types": ["Retainer"],
            },
            {
                "count": 4,
                "id": 100644,
                "kind": "Library",
                "printed_name": "Enhanced Senses",
                "types": ["Reaction"],
            },
            {
                "count": 5,
                "id": 100760,
                "kind": "Library",
                "printed_name": "Forced Awakening",
                "types": ["Reaction"],
            },
            {
                "count": 12,
                "id": 100845,
                "kind": "Library",
                "printed_name": "Govern the Unaligned",
                "types": ["Action"],
            },
            {
                "count": 1,
                "id": 101014,
                "kind": "Library",
                "printed_name": "Ivory Bow",
                "types": ["Equipment"],
            },
            {
                "count": 5,
                "id": 101321,
                "kind": "Library",
                "printed_name": "On the Qui Vive",
                "types": ["Reaction"],
            },
            {
                "count": 4,
                "id": 101475,
                "kind": "Library",
                "printed_name": "Precognition",
                "types": ["Reaction"],
            },
            {
                "count": 4,
                "id": 101850,
                "kind": "Library",
                "printed_name": "Spirit's Touch",
                "types": ["Reaction"],
            },
            {
                "count": 2,
                "id": 101856,
                "kind": "Library",
                "printed_name": "Sport Bike",
                "types": ["Equipment"],
            },
            {
                "count": 8,
                "id": 101949,
                "kind": "Library",
                "printed_name": "Telepathic Misdirection",
                "types": ["Reaction"],
            },
            {
                "count": 1,
                "id": 101963,
                "kind": "Library",
                "printed_name": "Thadius Zho",
                "types": ["Ally"],
            },
            {
                "count": 10,
                "id": 101966,
                "kind": "Library",
                "printed_name": "Theft of Vitae",
                "types": ["Combat"],
            },
            {
                "count": 2,
                "id": 102092,
                "kind": "Library",
                "printed_name": "Vast Wealth",
                "types": ["Master"],
            },
            {
                "count": 2,
                "id": 102139,
                "kind": "Library",
                "printed_name": "Walk of Flame",
                "types": ["Combat"],
            },
        ],
    }


@pytest.mark.asyncio
async def test_from_vtesdecks() -> None:
    """Test from vtesdecks.

    Skip the test if offline (cf. conftest).
    """
    VTES = vtes.VTES.load_local()
    async with aiohttp.ClientSession() as session:
        d = await providers.fetch(
            session,
            "https://vtesdecks.com/deck/user-lionelpx-bf26e06e078348e8b5852d4e86dbdf6c",
            VTES,
        )
    assert utils.jsonize(d) == {
        "id": "user-lionelpx-bf26e06e078348e8b5852d4e86dbdf6c",
        "name": "Test",
        "author": "lionelpx",
        "comment": "Here goes my description!",
        "cards": [
            {
                "count": 7,
                "id": 200001,
                "kind": "Crypt",
                "printed_name": "Aabbt Kindred",
                "suffix": "G2",
                "types": ["Vampire"],
            },
            {
                "count": 6,
                "id": 201520,
                "kind": "Crypt",
                "printed_name": "Nefertiti",
                "suffix": "G2 ADV",
                "types": ["Vampire"],
                "unicity_suffix": "ADV",
            },
            {
                "count": 6,
                "id": 100518,
                "kind": "Library",
                "printed_name": "Deflection",
                "types": ["Reaction"],
            },
            {
                "count": 2,
                "id": 100588,
                "kind": "Library",
                "printed_name": "Dreams of the Sphinx",
                "types": ["Master"],
            },
            {
                "count": 12,
                "id": 100650,
                "kind": "Library",
                "printed_name": "Enticement",
                "types": ["Action"],
            },
            {
                "count": 8,
                "id": 100667,
                "kind": "Library",
                "printed_name": "The Eternals of Sirius",
                "types": ["Master"],
            },
            {
                "count": 6,
                "id": 100769,
                "kind": "Library",
                "printed_name": "Forgotten Labyrinth",
                "types": ["Action Modifier"],
            },
            {
                "count": 12,
                "id": 100973,
                "kind": "Library",
                "printed_name": "Indomitability",
                "types": ["Combat"],
            },
            {
                "count": 6,
                "id": 101001,
                "kind": "Library",
                "printed_name": "Into Thin Air",
                "types": ["Action Modifier"],
            },
            {
                "count": 6,
                "id": 101321,
                "kind": "Library",
                "printed_name": "On the Qui Vive",
                "types": ["Reaction"],
            },
            {
                "count": 6,
                "id": 102121,
                "kind": "Library",
                "printed_name": "Villein",
                "types": ["Master"],
            },
        ],
    }


def test_deck_to_vdb() -> None:
    """Test the deck to vdb."""
    TWDA = twda.TWDA
    result = providers.serialize_vdb(TWDA["2010tcdbng"])
    assert result == (
        "https://vdb.im/decks/deck?name=The+Storage+Procurers#"
        "200517=1;200929=1;200161=1;200295=1;200343=1;201503=1;200346=1;201027=1;"
        "201065=1;201073=1;201231=1;200173=1;100327=1;100332=2;100444=1;101067=1;"
        "101388=2;101877=6;101896=3;102113=3;100298=1;100855=1;100966=1;101250=1;"
        "101333=1;101491=6;102202=1;100516=1;100745=8;100362=6;100401=7;101125=2;"
        "102097=4;100518=7;100519=2;101321=7;100392=8;100709=1;100944=1;101614=1;"
        "102079=1"
    )


def test_deck_to_minimal_json() -> None:
    """Test the deck to minimal json."""
    TWDA = twda.TWDA
    result = providers.serialize_json_minimal(TWDA["2010tcdbng"])
    assert result == {
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
