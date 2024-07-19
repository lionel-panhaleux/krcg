"""Test the parsing of hand-picked examples from the TWDA.
"""

import logging
import os.path
import textwrap

import json

from krcg import twda


def test_load_and_dump():
    test_twda = twda._TWDA()
    test_twda.load()
    assert len(test_twda) >= 3125
    # test dump
    json.dumps(test_twda.to_json())


def test_ampersand(TWDA):
    assert TWDA["2020afb"].name == "Robbing & Rapeing"


def test_2019grdojf(caplog):
    """Recent classic layout, we must get everything seamlessly"""
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2019grdojf.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["2019grdojf"].to_json() == {
        "id": "2019grdojf",
        "date": "2019-06-29",
        "event": "Garou Rim: Dawn Operation",
        "event_link": "http://www.vekn.net/event-calendar/event/9292",
        "place": "Joensuu, Finland",
        "players_count": 10,
        "player": "Esa-Matti Smolander",
        "tournament_format": "3R+F",
        "score": "1GW3.5+4",
        "name": "Parliament of Shadows precon with no changes.",
        "crypt": {
            "cards": [
                {"count": 2, "id": 200867, "name": "Luca Italicus"},
                {"count": 2, "id": 200114, "name": "Antón de Concepción"},
                {"count": 2, "id": 200249, "name": "Carolina Vález"},
                {"count": 2, "id": 201513, "name": "Charles Delmare"},
                {"count": 2, "id": 201517, "name": "Lord Leopold Valdemar"},
                {"count": 2, "id": 201518, "name": "Percival"},
            ],
            "count": 12,
        },
        "library": {
            "cards": [
                {
                    "cards": [
                        {"count": 1, "id": 100984, "name": "Information Highway"},
                        {"count": 1, "id": 101019, "name": "Jake Washington"},
                        {"count": 1, "id": 101238, "name": "Monastery of Shadows"},
                        {"count": 1, "id": 101350, "name": "Papillon"},
                        {"count": 1, "id": 101415, "name": "Political Hunting Ground"},
                        {"count": 1, "id": 101430, "name": "Power Structure"},
                        {"count": 1, "id": 101437, "name": "Powerbase: Madrid"},
                        {"count": 4, "id": 102121, "name": "Villein"},
                        {"count": 2, "id": 102207, "name": "Zillah's Valley"},
                    ],
                    "count": 13,
                    "type": "Master",
                },
                {
                    "cards": [
                        {"count": 6, "id": 100845, "name": "Govern the Unaligned"},
                        {"count": 2, "id": 102063, "name": "Under Siege"},
                    ],
                    "count": 8,
                    "type": "Action",
                },
                {
                    "cards": [{"count": 1, "id": 101261, "name": "Mylan Horseed"}],
                    "count": 1,
                    "type": "Ally",
                },
                {
                    "cards": [
                        {"count": 1, "id": 100059, "name": "Anarchist Uprising"},
                        {"count": 1, "id": 100064, "name": "Ancient Influence"},
                        {"count": 2, "id": 100131, "name": "Banishment"},
                        {"count": 8, "id": 101056, "name": "Kine Resources Contested"},
                        {"count": 1, "id": 101271, "name": "Neonate Breach"},
                        {"count": 1, "id": 101417, "name": "Political Stranglehold"},
                        {"count": 1, "id": 101591, "name": "Reins of Power"},
                    ],
                    "count": 15,
                    "type": "Political Action",
                },
                {
                    "cards": [
                        {"count": 2, "id": 100177, "name": "Blanket of Night"},
                        {"count": 4, "id": 100401, "name": "Conditioning"},
                        {"count": 4, "id": 101712, "name": "Seduction"},
                        {"count": 4, "id": 101743, "name": "Shadow Play"},
                        {"count": 4, "id": 101774, "name": "Shroud of Absence"},
                        {"count": 4, "id": 101775, "name": "Shroud of Night"},
                        {"count": 2, "id": 101957, "name": "Tenebrous Form"},
                    ],
                    "count": 24,
                    "type": "Action Modifier",
                },
                {
                    "cards": [
                        {"count": 4, "id": 100518, "name": "Deflection"},
                        {"count": 2, "id": 101309, "name": "Obedience"},
                        {"count": 2, "id": 101321, "name": "On the Qui Vive"},
                        {
                            "count": 2,
                            "id": 102137,
                            "name": "Wake with Evening's Freshness",
                        },
                    ],
                    "count": 10,
                    "type": "Reaction",
                },
                {
                    "cards": [
                        {"count": 3, "id": 101334, "name": "Oubliette"},
                        {"count": 3, "id": 101735, "name": "Shadow Body"},
                    ],
                    "count": 6,
                    "type": "Combat",
                },
            ],
            "count": 77,
        },
        "comments": (
            "Finals Seating\n\n"
            "Esa-Matti Smolander (Lasombra Starter) --> Petrus Makkonen (Epikasta TGB) "
            "--> Simo Tiippana (Lydia + Al-Muntathir Trujah Toolbox) --> Aapo Järvelin "
            "(Theo + Beast anarch Rush) --> Petro Hirvonen (Hektor Toolbox)\n"
        ),
    }
    assert caplog.record_tuples == []


def test_2016ggs(caplog):
    """Pretty straightforward, we must get everything seamlessly"""
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2016ggs.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["2016ggs"].to_json() == {
        "id": "2016ggs",
        "event": "Gothcon",
        "place": "Goteborg, Sweden",
        "date": "2016-03-26",
        "players_count": 16,
        "player": "Hugh Angseesing",
        "tournament_format": "3R+F",
        "score": "2GW9",
        "name": "DoC Swedish Sirens",
        "crypt": {
            "cards": [
                {"count": 2, "id": 200727, "name": "Jost Werner"},
                {"count": 2, "id": 201280, "name": "Sheila Mezarin"},
                {"count": 2, "id": 200091, "name": "Angela Preston"},
                {"count": 1, "id": 200491, "name": "Gaël Pilet"},
                {"count": 1, "id": 201492, "name": "Yseult"},
                {"count": 1, "id": 200331, "name": "Delilah Monroe"},
                {"count": 1, "id": 200903, "name": "Maldavis"},
                {"count": 1, "id": 201178, "name": "Remilliard, Devout Crusader"},
                {"count": 1, "id": 200258, "name": "Céleste, The Voice of a Secret"},
            ],
            "count": 12,
        },
        "library": {
            "cards": [
                {
                    "cards": [
                        {"count": 3, "id": 100058, "name": "Anarch Troublemaker"},
                        {"count": 1, "id": 100085, "name": "Archon Investigation"},
                        {"count": 2, "id": 100199, "name": "Blood Doll"},
                        {"count": 1, "id": 100435, "name": "The Coven"},
                        {"count": 1, "id": 100545, "name": "Direct Intervention"},
                        {"count": 1, "id": 100588, "name": "Dreams of the Sphinx"},
                        {
                            "count": 1,
                            "id": 100724,
                            "name": "Fetish Club Hunting Ground",
                        },
                        {"count": 1, "id": 100824, "name": "Giant's Blood"},
                        {"count": 1, "id": 101346, "name": "Palla Grande"},
                        {"count": 1, "id": 101352, "name": "Paris Opera House"},
                        {"count": 1, "id": 101384, "name": "Pentex™ Subversion"},
                        {"count": 2, "id": 101480, "name": "Presence"},
                        {"count": 3, "id": 102113, "name": "Vessel"},
                    ],
                    "count": 19,
                    "type": "Master",
                },
                {
                    "cards": [
                        {"count": 4, "id": 100652, "name": "Entrancement"},
                        {"count": 4, "id": 101089, "name": "Legal Manipulations"},
                        {"count": 2, "id": 101211, "name": "Mind Numb"},
                        {"count": 3, "id": 101819, "name": "Social Charm"},
                    ],
                    "count": 13,
                    "type": "Action",
                },
                {
                    "cards": [
                        {"count": 6, "id": 100031, "name": "Aire of Elation"},
                        {"count": 2, "id": 100492, "name": "Daring the Dawn"},
                        {"count": 4, "id": 101226, "name": "The Missing Voice"},
                        {"count": 2, "id": 101397, "name": "Phantom Speaker"},
                        {"count": 7, "id": 101786, "name": "Siren's Lure"},
                    ],
                    "count": 21,
                    "type": "Action Modifier",
                },
                {
                    "cards": [
                        {"count": 3, "id": 100519, "name": "Delaying Tactics"},
                        {"count": 2, "id": 101259, "name": "My Enemy's Enemy"},
                        {"count": 2, "id": 101321, "name": "On the Qui Vive"},
                        {"count": 8, "id": 101949, "name": "Telepathic Misdirection"},
                        {
                            "count": 5,
                            "id": 102137,
                            "name": "Wake with Evening's Freshness",
                        },
                    ],
                    "count": 20,
                    "type": "Reaction",
                },
                {
                    "cards": [
                        {"count": 8, "id": 101144, "name": "Majesty"},
                        {"count": 6, "id": 101817, "name": "Soak"},
                    ],
                    "count": 14,
                    "type": "Combat",
                },
                {
                    "cards": [{"count": 1, "id": 102057, "name": "The Uncoiling"}],
                    "count": 1,
                    "type": "Event",
                },
            ],
            "count": 88,
        },
    }
    assert caplog.record_tuples == []


def test_2k5alboraya(caplog):
    """Card name abbreviation (fetish club) with tailing point."""
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k5alboraya.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["2k5alboraya"].to_json() == {
        "id": "2k5alboraya",
        "event": "Spanish NCQ",
        "place": "Alboraya (Valencia), Spain",
        "date": "2005-02-12",
        "players_count": 34,
        "player": "Jose Vicente Coll",
        "tournament_format": "3R+F",
        "crypt": {
            "cards": [
                {"count": 3, "id": 200727, "name": "Jost Werner"},
                {"count": 2, "id": 200824, "name": "Le Dinh Tho"},
                {"count": 1, "id": 200540, "name": "Greta Kircher"},
                {"count": 1, "id": 200617, "name": "Ian Wallingford"},
                {"count": 1, "id": 201280, "name": "Sheila Mezarin"},
                {"count": 1, "id": 200299, "name": "Creamy Jade"},
                {"count": 1, "id": 200978, "name": "Mercy, Knight Inquisitor"},
                {"count": 1, "id": 201178, "name": "Remilliard, Devout Crusader"},
                {"count": 1, "id": 200849, "name": "Lolita"},
                {"count": 1, "id": 201055, "name": "Nicholas Chang"},
            ],
            "count": 13,
        },
        "library": {
            "cards": [
                {
                    "cards": [
                        {"count": 2, "id": 100058, "name": "Anarch Troublemaker"},
                        {"count": 3, "id": 100199, "name": "Blood Doll"},
                        {"count": 1, "id": 100435, "name": "The Coven"},
                        {"count": 1, "id": 100444, "name": "Creepshow Casino"},
                        {"count": 3, "id": 100545, "name": "Direct Intervention"},
                        {
                            "count": 1,
                            "id": 100724,
                            "name": "Fetish Club Hunting Ground",
                        },
                        {"count": 1, "id": 100945, "name": "The Hungry Coyote"},
                        {"count": 4, "id": 101346, "name": "Palla Grande"},
                        {"count": 2, "id": 101384, "name": "Pentex™ Subversion"},
                        {"count": 1, "id": 101896, "name": "Sudden Reversal"},
                    ],
                    "count": 19,
                    "type": "Master",
                },
                {
                    "cards": [
                        {"count": 8, "id": 100099, "name": "Art Scam"},
                        {"count": 8, "id": 100633, "name": "The Embrace"},
                        {"count": 4, "id": 100640, "name": "Enchant Kindred"},
                        {"count": 2, "id": 100652, "name": "Entrancement"},
                        {"count": 4, "id": 101211, "name": "Mind Numb"},
                        {"count": 2, "id": 101627, "name": "Revelations"},
                    ],
                    "count": 28,
                    "type": "Action",
                },
                {
                    "cards": [
                        {"count": 2, "id": 101164, "name": "Marijava Ghoul"},
                        {"count": 1, "id": 101340, "name": "Owl Companion"},
                    ],
                    "count": 3,
                    "type": "Retainer",
                },
                {
                    "cards": [{"count": 8, "id": 100323, "name": "Change of Target"}],
                    "count": 8,
                    "type": "Action Modifier",
                },
                {
                    "cards": [
                        {"count": 1, "id": 100519, "name": "Delaying Tactics"},
                        {"count": 2, "id": 100598, "name": "Eagle's Sight"},
                        {"count": 2, "id": 100644, "name": "Enhanced Senses"},
                        {"count": 3, "id": 101259, "name": "My Enemy's Enemy"},
                        {"count": 2, "id": 101948, "name": "Telepathic Counter"},
                        {"count": 7, "id": 101949, "name": "Telepathic Misdirection"},
                        {
                            "count": 5,
                            "id": 102137,
                            "name": "Wake with Evening's Freshness",
                        },
                    ],
                    "count": 22,
                    "type": "Reaction",
                },
                {
                    "cards": [
                        {"count": 7, "id": 101144, "name": "Majesty"},
                        {"count": 3, "id": 101859, "name": "Staredown"},
                    ],
                    "count": 10,
                    "type": "Combat",
                },
            ],
            "count": 90,
        },
    }
    assert caplog.record_tuples == []


def test_2k4dcqualifier(caplog):
    """A lot of comments (description, end) plus inline C-style card comment"""
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k4dcqualifier.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["2k4dcqualifier"].to_json() == {
        "id": "2k4dcqualifier",
        "event": "Atlantic Regional Qualifier",
        "place": "Washington, D.C.",
        "date": "2004-06-12",
        "players_count": 33,
        "player": "Matt Morgan",
        "name": "Call me Julio",
        "comments": textwrap.dedent(
            """
    Description: POT/DOM is always good.  Let's add permanent rush, +strength,
    Nosferatu Kingdom and a bad attitude!

    You can see from the crypt that an important part of playing this deck
    is being incredibly lucky.  I drew Beast in three out of four games and
    I drew Julio in every one.  How'd I get so lucky?  Dunno, I got a horrible
    crypt draw in a casual game on Friday.

    I've discussed some of the combat above and in other threads.
    In many ways, it's your basic Potence package.  The key is the guys with
    +strength.  The first time they beat someone down, they'll need a few
    cards (or a lot of cards) to do so.  After that, a Grapple might not
    even be necessary.  Pure goodness.

    An earlier version of the deck used Guardian Angels to avoid agg pokes
    and similar, but I took them out of the final version reasoning that most
    of the combat I see in tournaments is potence combat or guns and also that
    considering the expense of my minions, my masters should gain me pool, not
    cost pool.  I also had some Gang Tactics in an earlier version just because
    I think the art on them is hysterical and they're kind of useful.
    They were ultimately dropped for maneuvers because it seems more useful to
    me to be able to hold the maneuvers and play them in combat as needed than
    it is to assume I'll want close range on a certain action.  Now that I've
    won a tournament with this deck, I might put them back in just for fun.
    """
        )[1:],
        "crypt": {
            "cards": [
                {"count": 3, "id": 200736, "name": "Julio Martinez"},
                {"count": 2, "id": 201343, "name": "Tarbaby Jack"},
                {"count": 1, "id": 200232, "name": "Cailean"},
                {"count": 1, "id": 200958, "name": "Mateusz Gryzbowsky"},
                {"count": 1, "id": 200179, "name": "Beast, The Leatherface of Detroit"},
                {"count": 1, "id": 201088, "name": "Ox, Viceroy of the Hollows"},
                {"count": 1, "id": 201058, "name": "Nigel the Shunned"},
                {"count": 1, "id": 201077, "name": "Olivia"},
                {"count": 1, "id": 200020, "name": "Agatha"},
            ],
            "count": 12,
        },
        "library": {
            "cards": [
                {
                    "cards": [
                        {
                            "comments": (
                                "Not enough unless you're lucky (like I was)."
                            ),
                            "count": 4,
                            "id": 100199,
                            "name": "Blood Doll",
                        },
                        {
                            "comments": (
                                "Didn't really use them, but they were supposed to "
                                "justify the crypt\n"
                                "spread.  If there's no Julio, a Tarbaby or Cailean "
                                "and a Dominate master\n"
                                "is nearly as good, right?"
                            ),
                            "count": 2,
                            "id": 100572,
                            "name": "Dominate",
                        },
                        {"count": 1, "id": 100588, "name": "Dreams of the Sphinx"},
                        {"count": 2, "id": 100698, "name": "Fame"},
                        {
                            "comments": "Played it, but never tapped it.",
                            "count": 1,
                            "id": 100985,
                            "name": "Information Network",
                        },
                        {
                            "comments": (
                                "Absolutely essential.  Always got one after the "
                                "other, though."
                            ),
                            "count": 2,
                            "id": 101300,
                            "name": "Nosferatu Kingdom",
                        },
                        {
                            "count": 1,
                            "id": 101753,
                            "name": "Shanty Town Hunting Ground",
                        },
                    ],
                    "count": 13,
                    "type": "Master",
                },
                {
                    "cards": [
                        {"count": 6, "id": 100266, "name": "Bum's Rush"},
                        {
                            "comments": "Almost always played superior.",
                            "count": 6,
                            "id": 100845,
                            "name": "Govern the Unaligned",
                        },
                    ],
                    "count": 12,
                    "type": "Action",
                },
                {
                    "cards": [
                        {
                            "comments": (
                                "Because Colin said it was a good idea (he's right)."
                            ),
                            "count": 4,
                            "id": 100401,
                            "name": "Conditioning",
                        }
                    ],
                    "count": 4,
                    "type": "Action Modifier",
                },
                {
                    "cards": [
                        {"count": 4, "id": 101913, "name": "Swallowed by the Night"}
                    ],
                    "count": 4,
                    "type": "Action Modifier/Combat",
                },
                {
                    "cards": [
                        {"count": 8, "id": 100518, "name": "Deflection"},
                        {
                            "comments": (
                                "Replace one with Mylan Horseed as soon as Gehenna is "
                                "legal."
                            ),
                            "count": 7,
                            "id": 102137,
                            "name": "Wake with Evening's Freshness",
                        },
                    ],
                    "count": 15,
                    "type": "Reaction",
                },
                {
                    "cards": [
                        {"count": 3, "id": 100149, "name": "Behind You!"},
                        {"count": 4, "id": 100301, "name": "Carrion Crows"},
                        {"count": 10, "id": 100959, "name": "Immortal Grapple"},
                        {"count": 6, "id": 101945, "name": "Taste of Vitae"},
                        {"count": 10, "id": 101993, "name": "Torn Signpost"},
                        {"count": 9, "id": 102061, "name": "Undead Strength"},
                    ],
                    "count": 42,
                    "type": "Combat",
                },
            ],
            "count": 90,
        },
    }
    assert caplog.record_tuples == []


def test_2010tcdbng(caplog):
    """Card-level parenthesised commends (common)"""
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2010tcdbng.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["2010tcdbng"].to_json() == {
        "id": "2010tcdbng",
        "event": "Trading Card Day",
        "place": "Bad Naumheim, Germany",
        "date": "2010-05-08",
        "players_count": 10,
        "player": "Rudolf Scholz",
        "tournament_format": "2R+F",
        "score": "+4",
        "name": "The Storage Procurers",
        "crypt": {
            "cards": [
                {"count": 1, "id": 200517, "name": "Gilbert Duane"},
                {"count": 1, "id": 200929, "name": "Mariel, Lady Thunder"},
                {"count": 1, "id": 200161, "name": "Badr al-Budur"},
                {"count": 1, "id": 200295, "name": "Count Ormonde"},
                {"count": 1, "id": 200343, "name": "Didi Meyers"},
                {"count": 1, "id": 201503, "name": "Zebulon"},
                {"count": 1, "id": 200346, "name": "Dimple"},
                {"count": 1, "id": 201027, "name": "Mustafa Rahman"},
                {"count": 1, "id": 201065, "name": "Normal"},
                {"count": 1, "id": 201073, "name": "Ohanna"},
                {"count": 1, "id": 201231, "name": "Samson"},
                {"count": 1, "id": 200173, "name": "Basil"},
            ],
            "count": 12,
        },
        "library": {
            "cards": [
                {
                    "cards": [
                        {"count": 1, "id": 100327, "name": "Channel 10"},
                        {"count": 2, "id": 100332, "name": "Charisma"},
                        {"count": 1, "id": 100444, "name": "Creepshow Casino"},
                        {"count": 1, "id": 101067, "name": "KRCG News Radio"},
                        {"count": 2, "id": 101388, "name": "Perfectionist"},
                        {
                            "comments": "great card! usually " "underestimated",
                            "count": 6,
                            "id": 101877,
                            "name": "Storage Annex",
                        },
                        {"count": 3, "id": 101896, "name": "Sudden Reversal"},
                        {"count": 3, "id": 102113, "name": "Vessel"},
                    ],
                    "count": 19,
                    "type": "Master",
                },
                {
                    "cards": [
                        {"count": 1, "id": 100298, "name": "Carlton Van Wyk"},
                        {"count": 1, "id": 100855, "name": "Gregory Winter"},
                        {"count": 1, "id": 100966, "name": "Impundulu"},
                        {"count": 1, "id": 101250, "name": "Muddled Vampire Hunter"},
                        {"count": 1, "id": 101333, "name": "Ossian"},
                        {"count": 6, "id": 101491, "name": "Procurer"},
                        {"count": 1, "id": 102202, "name": "Young Bloods"},
                    ],
                    "count": 12,
                    "type": "Ally",
                },
                {
                    "cards": [
                        {"count": 1, "id": 100516, "name": "Deer Rifle"},
                        {
                            "comments": (
                                "brings fear to the methuselahs rather than to minions"
                            ),
                            "count": 8,
                            "id": 100745,
                            "name": "Flash Grenade",
                        },
                    ],
                    "count": 9,
                    "type": "Equipment",
                },
                {
                    "cards": [
                        {"count": 6, "id": 100362, "name": "Cloak the Gathering"},
                        {
                            "comments": "should be more!",
                            "count": 7,
                            "id": 100401,
                            "name": "Conditioning",
                        },
                        {"count": 2, "id": 101125, "name": "Lost in Crowds"},
                        {"count": 4, "id": 102097, "name": "Veil the Legions"},
                    ],
                    "count": 19,
                    "type": "Action Modifier",
                },
                {
                    "cards": [
                        {"count": 7, "id": 100518, "name": "Deflection"},
                        {"count": 2, "id": 100519, "name": "Delaying Tactics"},
                        {"count": 7, "id": 101321, "name": "On the Qui Vive"},
                    ],
                    "count": 16,
                    "type": "Reaction",
                },
                {
                    "cards": [{"count": 8, "id": 100392, "name": "Concealed Weapon"}],
                    "count": 8,
                    "type": "Combat",
                },
                {
                    "cards": [
                        {
                            "count": 1,
                            "id": 100709,
                            "name": "FBI Special Affairs Division",
                        },
                        {"count": 1, "id": 100944, "name": "Hunger Moon"},
                        {"count": 1, "id": 101614, "name": "Restricted Vitae"},
                        {"count": 1, "id": 102079, "name": "The Unmasking"},
                    ],
                    "count": 4,
                    "type": "Event",
                },
            ],
            "count": 87,
        },
        "comments": textwrap.dedent(
            """
    Description: Allies with Flash Grenades to keep troubles at bay.
    Storage Annex for card efficiency and a structured hand. Weenies and
    Midcaps with Obfuscate and/or Dominate to oust via Conditionings and
    Deflections.
    """
        )[1:],
    }
    assert caplog.record_tuples == []


def test_2012pslp(caplog):
    """Discipline included after card names (common)"""
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2012pslp.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["2012pslp"].to_json() == {
        "id": "2012pslp",
        "event": "Praxis Seizure: Leiria",
        "place": "Leiria, Portugal",
        "date": "2012-10-13",
        "players_count": 12,
        "player": "Patrick Gordo",
        "tournament_format": "2R+F",
        "name": "Shadowfang",
        "crypt": {
            "cards": [
                {"count": 3, "id": 201010, "name": "Morel"},
                {"count": 2, "id": 200498, "name": "Gem Ghastly"},
                {"count": 2, "id": 200560, "name": "Hagar Stone"},
                {"count": 2, "id": 200144, "name": "Arthur Denholm"},
                {"count": 1, "id": 200390, "name": "Drusilla Euphemia"},
                {"count": 1, "id": 200122, "name": "Apache Jones"},
                {"count": 1, "id": 200186, "name": "Bela"},
            ],
            "count": 12,
        },
        "library": {
            "cards": [
                {
                    "cards": [
                        {"count": 1, "id": 100135, "name": "The Barrens"},
                        {"count": 1, "id": 100199, "name": "Blood Doll"},
                        {"count": 2, "id": 100588, "name": "Dreams of the Sphinx"},
                        {"count": 1, "id": 100824, "name": "Giant's Blood"},
                        {"count": 1, "id": 101384, "name": "Pentex™ Subversion"},
                        {"count": 3, "id": 101896, "name": "Sudden Reversal"},
                        {"count": 2, "id": 102113, "name": "Vessel"},
                    ],
                    "count": 11,
                    "type": "Master",
                },
                {
                    "cards": [
                        {"count": 16, "id": 101055, "name": "Kindred Spirits"},
                        {"count": 1, "id": 101615, "name": "Restructure"},
                    ],
                    "count": 17,
                    "type": "Action",
                },
                {
                    "cards": [
                        {"count": 3, "id": 100362, "name": "Cloak the Gathering"},
                        {"count": 8, "id": 100405, "name": "Confusion"},
                        {"count": 3, "id": 100617, "name": "Elder Impersonation"},
                        {"count": 7, "id": 100682, "name": "Eyes of Chaos"},
                        {"count": 2, "id": 100687, "name": "Faceless Night"},
                        {"count": 3, "id": 101125, "name": "Lost in Crowds"},
                        {"count": 5, "id": 101857, "name": "Spying Mission"},
                    ],
                    "count": 31,
                    "type": "Action Modifier",
                },
                {
                    "cards": [
                        {"count": 3, "id": 100524, "name": "Deny"},
                        {"count": 4, "id": 101913, "name": "Swallowed by the Night"},
                    ],
                    "count": 7,
                    "type": "Action Modifier/Combat",
                },
                {
                    "cards": [
                        {"count": 2, "id": 100519, "name": "Delaying Tactics"},
                        {"count": 3, "id": 101259, "name": "My Enemy's Enemy"},
                        {"count": 3, "id": 101321, "name": "On the Qui Vive"},
                        {"count": 5, "id": 101949, "name": "Telepathic Misdirection"},
                        {
                            "count": 2,
                            "id": 102137,
                            "name": "Wake with Evening's Freshness",
                        },
                    ],
                    "count": 15,
                    "type": "Reaction",
                },
            ],
            "count": 81,
        },
    }
    assert caplog.record_tuples == []


def test_2k5sharednun(caplog):
    """Discipline name as header must not be mistaken for the Master card
    Note "2 Animalism" was changed to "Animalism x2" in decklist
    This serves as a test for post-name counts decklists like 2k9linkopingmay
    """
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k5sharednun.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["2k5sharednun"].to_json() == {
        "id": "2k5sharednun",
        "event": "Shared Nightmare",
        "place": "Utrecht, Netherlands",
        "date": "2005-07-02",
        "players_count": 16,
        "player": "Jeroen van Oort",
        "tournament_format": "3R+F",
        "name": "Deeper Underground",
        "comments": "\"Look in the sky, it's a raven. No, it's a bat.\n"
        "No, it's a crow, No it's a swarm of them all!!!\"\n",
        "crypt": {
            "cards": [
                {
                    "count": 1,
                    "id": 200272,
                    "name": "Christanius Lionel, The Mad Chronicler",
                },
                {"count": 1, "id": 200235, "name": "Calebros, The Martyr"},
                {"count": 1, "id": 200499, "name": "Gemini"},
                {"count": 1, "id": 201058, "name": "Nigel the Shunned"},
                {"count": 1, "id": 200211, "name": "Bobby Lemon"},
                {"count": 1, "id": 201198, "name": "Roger Farnsworth"},
                {"count": 1, "id": 200276, "name": "Clarissa Steinburgen"},
                {"count": 1, "id": 201090, "name": "Panagos Levidis"},
                {"count": 1, "id": 201276, "name": "Shannon Price, the Whisperer"},
                {"count": 1, "id": 201464, "name": "Watenda"},
                {"count": 1, "id": 201014, "name": "Mouse"},
                {"count": 1, "id": 201507, "name": "Zip"},
            ],
            "count": 12,
        },
        "library": {
            "cards": [
                {
                    "cards": [
                        {"count": 2, "id": 100070, "name": "Animalism"},
                        {"count": 6, "id": 100199, "name": "Blood Doll"},
                        {"count": 2, "id": 100545, "name": "Direct Intervention"},
                        {"count": 1, "id": 100588, "name": "Dreams of the Sphinx"},
                        {
                            "count": 2,
                            "id": 100908,
                            "name": "Heidelberg Castle, Germany",
                        },
                        {"count": 1, "id": 101808, "name": "Slum Hunting Ground"},
                    ],
                    "count": 14,
                    "type": "Master",
                },
                {
                    "cards": [
                        {"count": 1, "id": 100093, "name": "Army of Rats"},
                        {"count": 2, "id": 100365, "name": "Clotho's Gift"},
                        {"count": 5, "id": 100390, "name": "Computer Hacking"},
                    ],
                    "count": 8,
                    "type": "Action",
                },
                {
                    "cards": [{"count": 3, "id": 101073, "name": "Laptop Computer"}],
                    "count": 3,
                    "type": "Equipment",
                },
                {
                    "cards": [
                        {"count": 1, "id": 101015, "name": "J. S. Simmons, Esq."},
                        {"count": 7, "id": 101550, "name": "Raven Spy"},
                        {"count": 1, "id": 101943, "name": "Tasha Morgan"},
                    ],
                    "count": 9,
                    "type": "Retainer",
                },
                {
                    "cards": [
                        {"count": 6, "id": 100362, "name": "Cloak the Gathering"},
                        {"count": 3, "id": 100687, "name": "Faceless Night"},
                        {"count": 2, "id": 101125, "name": "Lost in Crowds"},
                    ],
                    "count": 11,
                    "type": "Action Modifier",
                },
                {
                    "cards": [
                        {"count": 5, "id": 100308, "name": "Cats' Guidance"},
                        {"count": 2, "id": 100519, "name": "Delaying Tactics"},
                        {"count": 7, "id": 100760, "name": "Forced Awakening"},
                        {"count": 3, "id": 100863, "name": "Guard Dogs"},
                    ],
                    "count": 17,
                    "type": "Reaction",
                },
                {
                    "cards": [
                        {"count": 7, "id": 100029, "name": "Aid from Bats"},
                        {"count": 4, "id": 100149, "name": "Behind You!"},
                        {"count": 3, "id": 100290, "name": "Canine Horde"},
                        {"count": 8, "id": 100301, "name": "Carrion Crows"},
                        {"count": 3, "id": 100567, "name": "Dodge"},
                        {"count": 3, "id": 101342, "name": "Pack Alpha"},
                    ],
                    "count": 28,
                    "type": "Combat",
                },
            ],
            "count": 90,
        },
    }
    assert caplog.record_tuples == [
        (
            "krcg",
            logging.WARNING,
            '[    40][2k5sharednun] improper discipline "Obfuscate 17"',
        ),
        (
            "krcg",
            logging.WARNING,
            '[    47][2k5sharednun] improper discipline "Animalism: 37"',
        ),
    ]


def test_2020pihc(caplog):
    """Discipline name as header must not be mistaken for the Master card
    Long preface with formatted comment (keep spaces and carriage returns)
    Using long vampire name with comma and (ADV)
    """
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2020pihc.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["2020pihc"].to_json() == {
        "id": "2020pihc",
        "event": "Personal Involvement",
        "event_link": "http://www.vekn.net/event-calendar/event/9566",
        "place": "Hamilton, Canada",
        "date": "2020-02-22",
        "player": "Jay Kristoff",
        "players_count": 10,
        "tournament_format": "2R+F",
        "score": "0GW2.5+1.5",
        "name": "Sauce or GTFO",
        "crypt": {
            "cards": [
                {"count": 6, "id": 200956, "name": "Matasuntha"},
                {"count": 1, "id": 200238, "name": "Calvin Cleaver"},
                {"count": 1, "id": 200463, "name": "Fergus Alexander"},
                {"count": 1, "id": 200836, "name": "Lillian"},
                {"count": 1, "id": 201334, "name": "T.J."},
                {"count": 1, "id": 200902, "name": "Malcolm"},
                {"count": 1, "id": 201192, "name": "Robert Price"},
            ],
            "count": 12,
        },
        "library": {
            "cards": [
                {
                    "cards": [
                        {"count": 1, "id": 100009, "name": "Abombwe"},
                        {"count": 1, "id": 100609, "name": "Ecoterrorists"},
                        {"count": 1, "id": 100698, "name": "Fame"},
                        {"count": 1, "id": 100824, "name": "Giant's Blood"},
                        {"count": 1, "id": 101388, "name": "Perfectionist"},
                        {"count": 1, "id": 102121, "name": "Villein"},
                        {"count": 1, "id": 102180, "name": "Wider View"},
                    ],
                    "count": 7,
                    "type": "Master",
                },
                {
                    "cards": [
                        {"count": 2, "id": 100266, "name": "Bum's Rush"},
                        {"count": 2, "id": 100515, "name": "Deep Song"},
                        {"count": 1, "id": 100840, "name": "Go Anarch"},
                        {"count": 2, "id": 100886, "name": "Harass"},
                        {"count": 2, "id": 101296, "name": "Nose of the Hound"},
                        {"count": 1, "id": 101632, "name": "Rewilding"},
                        {"count": 1, "id": 101740, "name": "Shadow of the Beast"},
                        {"count": 2, "id": 101972, "name": "Thing"},
                    ],
                    "count": 13,
                    "type": "Action",
                },
                {
                    "cards": [{"count": 1, "id": 101261, "name": "Mylan Horseed"}],
                    "count": 1,
                    "type": "Ally",
                },
                {
                    "cards": [
                        {"count": 1, "id": 100243, "name": "Bowl of Convergence"},
                        {"count": 1, "id": 100678, "name": "Eye of Hazimel"},
                        {"count": 1, "id": 100847, "name": "Gran Madre di Dio, Italy"},
                        {"count": 1, "id": 101007, "name": "IR Goggles"},
                        {"count": 1, "id": 101040, "name": "Kevlar Vest"},
                    ],
                    "count": 5,
                    "type": "Equipment",
                },
                {
                    "cards": [{"count": 1, "id": 100064, "name": "Ancient Influence"}],
                    "count": 1,
                    "type": "Political Action",
                },
                {
                    "cards": [
                        {"count": 2, "id": 100568, "name": "Dog Pack"},
                        {"count": 1, "id": 100932, "name": "Homunculus"},
                    ],
                    "count": 3,
                    "type": "Retainer",
                },
                {
                    "cards": [
                        {"count": 1, "id": 100645, "name": "Enkil Cog"},
                        {"count": 3, "id": 100761, "name": "Forced March"},
                        {"count": 5, "id": 100788, "name": "Freak Drive"},
                        {
                            "count": 3,
                            "id": 100994,
                            "name": "Instantaneous Transformation",
                        },
                    ],
                    "count": 12,
                    "type": "Action Modifier",
                },
                {
                    "cards": [
                        {"count": 2, "id": 100680, "name": "Eyes of Argus"},
                        {"count": 1, "id": 101949, "name": "Telepathic Misdirection"},
                    ],
                    "count": 3,
                    "type": "Reaction",
                },
                {
                    "cards": [
                        {"count": 4, "id": 100227, "name": "Blur"},
                        {"count": 2, "id": 100749, "name": "Flesh of Marble"},
                        {"count": 1, "id": 100771, "name": "Form of Mist"},
                        {"count": 2, "id": 101523, "name": "Pursuit"},
                        {"count": 1, "id": 101790, "name": "Skin of Night"},
                        {"count": 3, "id": 101945, "name": "Taste of Vitae"},
                    ],
                    "count": 13,
                    "type": "Combat",
                },
                {
                    "cards": [{"count": 1, "id": 100581, "name": "Dragonbound"}],
                    "count": 1,
                    "type": "Event",
                },
            ],
            "count": 59,
        },
        "comments": """Final round recap written by Darby Keeney:

Jay (3rd seed, Matasuntha multiaction) --> Karl (2nd seed, Palla Grande Undue Influence)
  --> Marshall (5th seed, Valkyrie bleed)
  --> Darby (1st seed, Blood Deprivation/Tempt)
  --> Tim (4th seed, Prince politics with Rabbat kicker).

The mind games start even before the first transfer. Jay's 3rd seed placement
was conventional, but Karl wants nothing to do with Temptation. That part of
his plan works, Darby won't sit near Jay and instead plans to exploit the
Valkyrie's almost-slave status.

The early game proceeds as expected with Karl dropping a couple of early bleed
bombs. Subsequent rushes from Matasuntha and a Valkyrie pretty much doom him.

The key interactions defining the game's development:
  - Tim passes Jay's Ancient Influence, netting Jay 3 more beads than anyone
    else and giving him a large safety margin.
  - Matasuntha's early 1-pt bleed gets bounced with My Enemy's Enemy but Tim
    throws it back at Karl, requiring a second MEE. The pool loss is
    insignificant, but using the 2nd bounce gets Matasuntha an Enkil Cog one
    turn earlier.

On the other side of the table, Darby sprinkles Disease counters and
Temptations liberally. Marshall starts to bleed with the Valks, facing bleed
reduction and S:CE lockdown. With three players now leaning left, Jay simply
moves faster at a minion-less Karl and gets the first oust.

Things tilt in the 4-player as Jay makes it clear that Marshall will face no
predation, immediately Rewilding Darby's Heidleburg Castle. The action is
blocked but the shape of the endgame is clearly defined. Darby isn't happy
about having a pair of predators, especially since Mataunta has both the Eye of
Hazimel and Enkil Cog.

Marshall shows down for a turn and Matasuntha gets flat-out burned with Society
of Leopold. Jay has tons of pool and the Ecoterrorists, so Matasuntha V2 gets
beads as Marshall and Darby do bleedy things, leading to Tim getting ousted.

Marshall correctly Rewilds the Heidleburg (instead of Jay's Ecoterrorists) and
Darby loses an Impundulu with 4 life in a Trapped combat. Neither is completely
happy with that outcome, but Darby's resources are getting thin. Despite a
hectic last turn, Darby can't quite defend his sole pool counter, but Marshall
taps out getting it.

Matasunta immediately rushes Brunhilde and some chump eats her, setting
Marshall on Jay's earlier path of "it's time for V2." He has planned ahead and
only loses one turn - but that's enough to cause the game to time out.

Jay mentions that Marshall wins the game with 5 more minutes since Matasuntha
V1 lost some important tools. Without that time available, Jay gleefully
accepts the dubious honor of winning a tournament with exactly zero games wins
for the day.
""",
    }
    assert caplog.record_tuples == [
        (
            "krcg",
            logging.WARNING,
            "deck 2020pihc has too few cards (59) [Sauce or GTFO]",
        ),
    ]


def test_2011ptwolss(caplog):
    """Card cited in the preface can lead to parsing errors."""
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2011ptwolss.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["2011ptwolss"].to_json() == {
        "id": "2011ptwolss",
        "date": "2011-10-29",
        "event": "Poison the Well of Life",
        "name": "Yet another Imbued deck winning a tournament",
        "place": "Stockholm, Sweden",
        "player": "Marcus Berg",
        "players_count": 19,
        "tournament_format": "2R+F",
        "comments": (
            "Description: Too many cards, should be slimmed about 15 cards.\n"
            "All Enchant Kindred should be Entrancement. One or both Kiss of\n"
            "Ra should be Mind Numb. Villein and Lilith's Blessing should be\n"
            "2 Blood Doll and 2 Vessel. Should maybe add 2-4 Majesty. Crypt\n"
            "should be 4 Mary Anne Blaire, 2 Lodin and the rest singles.\n"
        ),
        "crypt": {
            "cards": [
                {"count": 2, "id": 200946, "name": "Mary Anne Blaire"},
                {"count": 2, "id": 200427, "name": "Epikasta Rigatos"},
                {"count": 2, "id": 200848, "name": "Lodin (Olaf Holte)"},
                {"count": 2, "id": 201438, "name": "Victor Donaldson"},
                {"count": 2, "id": 200421, "name": "Emily Carson"},
                {"count": 1, "id": 200907, "name": "Maman Boumba"},
                {"count": 1, "id": 200767, "name": "Keith Moody"},
            ],
            "count": 12,
        },
        "library": {
            "cards": [
                {
                    "cards": [
                        {"count": 1, "id": 100058, "name": "Anarch Troublemaker"},
                        {"count": 4, "id": 100588, "name": "Dreams of the Sphinx"},
                        {"count": 1, "id": 100824, "name": "Giant's Blood"},
                        {"count": 1, "id": 100984, "name": "Information Highway"},
                        {"count": 1, "id": 101108, "name": "Lilith's Blessing"},
                        {"count": 1, "id": 101225, "name": "Misdirection"},
                        {"count": 2, "id": 101384, "name": "Pentex™ Subversion"},
                        {"count": 6, "id": 102121, "name": "Villein"},
                        {"count": 2, "id": 102180, "name": "Wider View"},
                    ],
                    "count": 19,
                    "type": "Master",
                },
                {
                    "cards": [
                        {"count": 1, "id": 101557, "name": "React with Conviction"}
                    ],
                    "count": 1,
                    "type": "Conviction",
                },
                {
                    "cards": [
                        {"count": 4, "id": 100640, "name": "Enchant Kindred"},
                        {"count": 15, "id": 100845, "name": "Govern the Unaligned"},
                        {"count": 2, "id": 101211, "name": "Mind Numb"},
                    ],
                    "count": 21,
                    "type": "Action",
                },
                {
                    "cards": [{"count": 1, "id": 100298, "name": "Carlton Van Wyk"}],
                    "count": 1,
                    "type": "Ally",
                },
                {
                    "cards": [{"count": 1, "id": 100903, "name": "Heart of Nizchetus"}],
                    "count": 1,
                    "type": "Equipment",
                },
                {
                    "cards": [
                        {"count": 1, "id": 100131, "name": "Banishment"},
                        {"count": 1, "id": 101353, "name": "Parity Shift"},
                    ],
                    "count": 2,
                    "type": "Political Action",
                },
                {
                    "cards": [
                        {"count": 3, "id": 100401, "name": "Conditioning"},
                        {"count": 1, "id": 100492, "name": "Daring the Dawn"},
                        {"count": 7, "id": 100788, "name": "Freak Drive"},
                        {"count": 2, "id": 101062, "name": "The Kiss of Ra"},
                    ],
                    "count": 13,
                    "type": "Action Modifier",
                },
                {
                    "cards": [
                        {"count": 6, "id": 101256, "name": "Murmur of the False Will"}
                    ],
                    "count": 6,
                    "type": "Action Modifier/Reaction",
                },
                {
                    "cards": [
                        {"count": 7, "id": 100518, "name": "Deflection"},
                        {"count": 3, "id": 100680, "name": "Eyes of Argus"},
                        {"count": 8, "id": 101309, "name": "Obedience"},
                        {"count": 8, "id": 101706, "name": "Second Tradition: Domain"},
                    ],
                    "count": 26,
                    "type": "Reaction",
                },
            ],
            "count": 90,
        },
    }
    assert caplog.record_tuples == []


def test_2k8tfnwesterville(caplog):
    """A dubious "Reactions" header that has once been wrongly parsed as a card."""
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k8tfnwesterville.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["2k8tfnwesterville"].to_json() == {
        "id": "2k8tfnwesterville",
        "date": "2008-01-27",
        "event": "The Final Nights",
        "name": "Tembo!!",
        "place": "Westerville, Ohio",
        "player": "Matt Piatek",
        "players_count": 16,
        "tournament_format": "2R+F",
        "comments": (
            "Description: Demdemeh makes a herd of elephant allies with 2 hand\n"
            "damage and one bleed. Babalawo Alafin combines with Maabara to allow\n"
            "you to craft the hand you need.\n\n"
            "It didn't work the way it was intended to in the finals. In retrospect\n"
            "I should have brought out Demdemeh instead of Wamukota as my second\n"
            "vampire, but I thought his ability would be important for my retain\n"
            "actions(it was never used). I never could get enough pool to bring\n"
            "out Demdemeh afterwards. A herd of elephants would have greatly\n"
            "increased my ousting ability.\n\n"
            'It is nice to know that the deck can survive without all of the "A"\n'
            "team in play.\n"
        ),
        "crypt": {
            "cards": [
                {"count": 3, "id": 200333, "name": "Demdemeh"},
                {"count": 3, "id": 200957, "name": "Matata"},
                {"count": 3, "id": 200158, "name": "Babalawo Alafin"},
                {"count": 2, "id": 201463, "name": "Wamukota"},
                {"count": 2, "id": 201305, "name": "Solomon Batanea"},
            ],
            "count": 13,
        },
        "library": {
            "cards": [
                {
                    "cards": [
                        {"count": 1, "id": 100070, "name": "Animalism"},
                        {"count": 2, "id": 100199, "name": "Blood Doll"},
                        {"count": 1, "id": 100445, "name": "Crematorium"},
                        {
                            "count": 1,
                            "id": 100908,
                            "name": "Heidelberg Castle, Germany",
                        },
                        {"count": 1, "id": 101076, "name": "Lazarene Inquisitor"},
                        {"count": 2, "id": 101136, "name": "Maabara"},
                        {"count": 1, "id": 101189, "name": "Mbare Market, Harare"},
                        {"count": 3, "id": 101217, "name": "Minion Tap"},
                        {"count": 2, "id": 101355, "name": "The Parthenon"},
                    ],
                    "count": 14,
                    "type": "Master",
                },
                {
                    "cards": [
                        {"count": 1, "id": 100759, "name": "Force of Will"},
                        {"count": 2, "id": 101543, "name": "Rapid Healing"},
                        {"count": 2, "id": 101613, "name": "Restoration"},
                        {"count": 1, "id": 101984, "name": "Tier of Souls"},
                    ],
                    "count": 6,
                    "type": "Action",
                },
                {
                    "cards": [
                        {"count": 1, "id": 100657, "name": "Erebus Mask"},
                        {"count": 1, "id": 101039, "name": "Kerrie"},
                        {"count": 1, "id": 102078, "name": "Unlicensed Taxicab"},
                    ],
                    "count": 3,
                    "type": "Equipment",
                },
                {
                    "cards": [
                        {"count": 7, "id": 100626, "name": "Elephant Guardian"},
                        {"count": 1, "id": 101015, "name": "J. S. Simmons, Esq."},
                        {"count": 3, "id": 101550, "name": "Raven Spy"},
                        {"count": 2, "id": 101914, "name": "Swarm"},
                        {"count": 1, "id": 101943, "name": "Tasha Morgan"},
                    ],
                    "count": 14,
                    "type": "Retainer",
                },
                {
                    "cards": [
                        {"count": 2, "id": 100502, "name": "Day Operation"},
                        {"count": 5, "id": 100788, "name": "Freak Drive"},
                    ],
                    "count": 7,
                    "type": "Action Modifier",
                },
                {
                    "cards": [
                        {"count": 1, "id": 100308, "name": "Cats' Guidance"},
                        {"count": 1, "id": 100598, "name": "Eagle's Sight"},
                        {"count": 1, "id": 100644, "name": "Enhanced Senses"},
                        {"count": 1, "id": 100863, "name": "Guard Dogs"},
                        {"count": 1, "id": 101259, "name": "My Enemy's Enemy"},
                        {"count": 1, "id": 101475, "name": "Precognition"},
                        {"count": 2, "id": 101547, "name": "Rat's Warning"},
                        {"count": 1, "id": 101559, "name": "Read the Winds"},
                        {"count": 2, "id": 101850, "name": "Spirit's Touch"},
                        {"count": 2, "id": 101949, "name": "Telepathic Misdirection"},
                        {
                            "count": 4,
                            "id": 102137,
                            "name": "Wake with Evening's Freshness",
                        },
                    ],
                    "count": 17,
                    "type": "Reaction",
                },
                {
                    "cards": [
                        {"count": 1, "id": 100290, "name": "Canine Horde"},
                        {"count": 2, "id": 100585, "name": "Drawing Out the Beast"},
                        {"count": 2, "id": 100918, "name": "Hidden Strength"},
                        {"count": 4, "id": 100973, "name": "Indomitability"},
                        {"count": 1, "id": 101342, "name": "Pack Alpha"},
                        {"count": 3, "id": 101608, "name": "Resilience"},
                        {"count": 4, "id": 101649, "name": "Rolling with the Punches"},
                        {"count": 2, "id": 101791, "name": "Skin of Rock"},
                        {"count": 6, "id": 101945, "name": "Taste of Vitae"},
                        {"count": 2, "id": 102071, "name": "Unflinching Persistence"},
                    ],
                    "count": 27,
                    "type": "Combat",
                },
                {
                    "cards": [
                        {"count": 2, "id": 100074, "name": "Anthelios, The Red Star"}
                    ],
                    "count": 2,
                    "type": "Event",
                },
            ],
            "count": 90,
        },
    }
    assert caplog.record_tuples == [
        (
            "krcg",
            logging.WARNING,
            "[    85][2k8tfnwesterville] failed to parse \"Matt's comments "
            'on the final:"',
        )
    ]


def test_2k7fsmc(caplog):
    """Cards listed in the preface is a common thing in the TWDA."""
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k7fsmc.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["2k7fsmc"].to_json() == {
        "id": "2k7fsmc",
        "date": "2007-12-08",
        "event": "Fee Stake: Mexico City",
        "name": "Nephandi",
        "place": "Mexico City, Mexico",
        "player": "Omael Rangel",
        "players_count": 10,
        "tournament_format": "2R+F",
        "comments": (
            "4 memories of mortality -- when they are gone i should add a fort. "
            "library, a pentex subversion and maybe anarchist troublemaker\n"
            "6 computer hacking -- maybe add 1 more\n"
            "3 glancing blows -- I'll remove this and add more concealed and molotovs\n"
            "1 .44 magnum -- this should be another grenade but i only had 7 at the "
            "time\n"
        ),
        "crypt": {
            "cards": [
                {"count": 4, "id": 200116, "name": "Antonio d'Erlette"},
                {"count": 4, "id": 201393, "name": "Tupdog"},
                {"count": 2, "id": 200767, "name": "Keith Moody"},
                {"count": 1, "id": 200418, "name": "Ember Wright"},
                {"count": 1, "id": 201222, "name": "Saiz"},
            ],
            "count": 12,
        },
        "library": {
            "cards": [
                {
                    "cards": [
                        {"count": 1, "id": 100085, "name": "Archon Investigation"},
                        {"count": 4, "id": 100199, "name": "Blood Doll"},
                        {"count": 3, "id": 100545, "name": "Direct Intervention"},
                        {"count": 2, "id": 100897, "name": "Haven Uncovered"},
                        {"count": 1, "id": 100984, "name": "Information Highway"},
                        {"count": 6, "id": 101104, "name": "Life in the City"},
                        {"count": 4, "id": 101198, "name": "Memories of Mortality"},
                        {"count": 1, "id": 101229, "name": "Mob Connections"},
                    ],
                    "count": 22,
                    "type": "Master",
                },
                {
                    "cards": [{"count": 6, "id": 100390, "name": "Computer Hacking"}],
                    "count": 6,
                    "type": "Action",
                },
                {
                    "cards": [
                        {"count": 8, "id": 101272, "name": "Nephandus"},
                        {"count": 1, "id": 101333, "name": "Ossian"},
                        {"count": 1, "id": 102087, "name": "Vagabond Mystic"},
                    ],
                    "count": 10,
                    "type": "Ally",
                },
                {
                    "cards": [
                        {"count": 1, "id": 100001, "name": ".44 Magnum"},
                        {"count": 7, "id": 100745, "name": "Flash Grenade"},
                    ],
                    "count": 8,
                    "type": "Equipment",
                },
                {
                    "cards": [
                        {"count": 8, "id": 100639, "name": "Empowering the Puppet King"}
                    ],
                    "count": 8,
                    "type": "Action Modifier",
                },
                {
                    "cards": [
                        {"count": 8, "id": 100518, "name": "Deflection"},
                        {"count": 5, "id": 101321, "name": "On the Qui Vive"},
                        {
                            "count": 3,
                            "id": 102137,
                            "name": "Wake with Evening's Freshness",
                        },
                    ],
                    "count": 16,
                    "type": "Reaction",
                },
                {
                    "cards": [
                        {"count": 8, "id": 100392, "name": "Concealed Weapon"},
                        {"count": 3, "id": 100834, "name": "Glancing Blow"},
                        {"count": 3, "id": 101235, "name": "Molotov Cocktail"},
                    ],
                    "count": 14,
                    "type": "Combat",
                },
                {
                    "cards": [{"count": 2, "id": 102079, "name": "The Unmasking"}],
                    "count": 2,
                    "type": "Event",
                },
            ],
            "count": 86,
        },
    }
    assert caplog.record_tuples == []


def test_2k2stranger(caplog):
    """Wrong card, short name and post count: "Jack 5" """
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k2stranger.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["2k2stranger"].to_json() == {
        "id": "2k2stranger",
        "date": "2002-01-05",
        "event": "The Stranger Among Us",
        "place": "Boston, Massachusetts",
        "player": "Kevin Scribner",
        "comments": (
            '"tzimisce - go: counterspell deck"\n\n'
            "special thanks to jay kristoff, for his deck on thelasombra's site,\n"
            "which was the inspiration for this one, and to david d'avila-anderson,\n"
            "for his incredible articles on the subject of intercept-combat decks...\n"
            "-- i've been playing this deck for over a year now, in various forms,\n"
            "but it wasn't until bloodlines and 'read the winds' that i was able to\n"
            "really get it off the ground... the raw power and efficiency of that\n"
            "one card opened up so many card slots, which i was able to dedicate to\n"
            "forward pressure, without compromising my ability to fend off 4-on-1\n"
            "onslaughts turn after turn...\n"
            "-- in light of the lessons i learned at this tournament, i think i'll\n"
            "need to change the 2 anarch revolt to either 2 more smiling jack, or 2\n"
            "war ghoul... the anarch revolts organize the table against me too much,\n"
            "and turn my cross-table buddies into enemies... with smiling jack, they\n"
            "at least think twice before coming at me... removing 2 revolts also\n"
            "allows me to drop 2 of the eagle's sight, so maybe i'd go with 3 smiling\n"
            "jack, 3 war ghoul, and exchange the femur of toomler for one more\n"
            "revenant...\n"
            "-- i'm seriously considering swapping out the duplicate caliban in the\n"
            "crypt for either goratrix, matteus, omaya, or [most likely] jost\n"
            "werner... the duplicate crypt draw doesn't really hurt me much, but\n"
            "having jost's inherent stealth might make a big difference in some\n"
            "games...\n"
        ),
        "crypt": {
            "cards": [
                {"count": 2, "id": 200236, "name": "Caliban"},
                {"count": 1, "id": 200810, "name": "Lambach"},
                {"count": 1, "id": 201319, "name": "Stravinsky"},
                {"count": 1, "id": 200113, "name": "Anton"},
                {"count": 1, "id": 200844, "name": "Little Tailor of Prague"},
                {"count": 1, "id": 200980, "name": "Meshenka"},
                {"count": 1, "id": 201244, "name": "Sascha Vykos, The Angel of Caine"},
                {"count": 1, "id": 200290, "name": "Corine Marcón"},
                {"count": 1, "id": 200339, "name": "Devin Bisley"},
                {"count": 1, "id": 200850, "name": "Lolita Houston"},
                {"count": 1, "id": 201357, "name": "Terrence"},
            ],
            "count": 12,
        },
        "library": {
            "cards": [
                {
                    "cards": [
                        {"count": 2, "id": 100055, "name": "Anarch Revolt"},
                        {"count": 6, "id": 100199, "name": "Blood Doll"},
                        {"count": 1, "id": 101102, "name": "Library Hunting Ground"},
                        {"count": 1, "id": 101439, "name": "Powerbase: Montreal"},
                        {"count": 1, "id": 101536, "name": "The Rack"},
                        {"count": 3, "id": 101654, "name": "Rötschreck"},
                        {"count": 2, "id": 101811, "name": "Smiling Jack, The Anarch"},
                    ],
                    "count": 16,
                    "type": "Master",
                },
                {
                    "cards": [
                        {"count": 3, "id": 101627, "name": "Revelations"},
                        {"count": 3, "id": 101984, "name": "Tier of Souls"},
                    ],
                    "count": 6,
                    "type": "Action",
                },
                {
                    "cards": [
                        {"count": 1, "id": 100720, "name": "Femur of Toomler"},
                        {"count": 1, "id": 101014, "name": "Ivory Bow"},
                    ],
                    "count": 2,
                    "type": "Equipment",
                },
                {
                    "cards": [{"count": 2, "id": 101628, "name": "Revenant"}],
                    "count": 2,
                    "type": "Retainer",
                },
                {
                    "cards": [
                        {"count": 6, "id": 100308, "name": "Cats' Guidance"},
                        {"count": 6, "id": 100598, "name": "Eagle's Sight"},
                        {"count": 4, "id": 100644, "name": "Enhanced Senses"},
                        {"count": 6, "id": 100760, "name": "Forced Awakening"},
                        {"count": 3, "id": 101475, "name": "Precognition"},
                        {"count": 6, "id": 101559, "name": "Read the Winds"},
                        {"count": 3, "id": 101850, "name": "Spirit's Touch"},
                        {"count": 6, "id": 101949, "name": "Telepathic Misdirection"},
                    ],
                    "count": 40,
                    "type": "Reaction",
                },
                {
                    "cards": [
                        {"count": 6, "id": 100250, "name": "Breath of the Dragon"},
                        {"count": 10, "id": 100344, "name": "Chiropteran Marauder"},
                        {"count": 8, "id": 100986, "name": "Inner Essence"},
                    ],
                    "count": 24,
                    "type": "Combat",
                },
            ],
            "count": 90,
        },
    }
    assert caplog.record_tuples == [
        ("krcg", logging.WARNING, '[    55][2k2stranger] failed to parse "notes:"')
    ]


def test_2k2origins1(caplog):
    """Camille Devereux / Raven discirimination

    Before the release of the 10th anniversary edition in 2004,
    Camille Devereux and Raven were two distinct vampires, so they should be kept
    distinct (at least in the txt output) for decklists prior to that.
    """
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k2origins1.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    # for now, Camille / Raven do not show as separated entries in the dict version
    # it would seem a bit old to have two cards with the same ID there
    assert TWDA["2k2origins1"].to_json() == {
        "id": "2k2origins1",
        "date": "2002-07-04",
        "event": "Origins Thursday",
        "place": "Columbus, Ohio",
        "players_count": 25,
        "player": "Jay Kristoff",
        "comments": (
            "I just got home from an amazing first day at Origins. I was able to\n"
            "eak out a tournament victory with my Mirembe Rides Again deck. 25\n"
            "meths played in this event. 4 of the 5 finalists were from Ohio, the\n"
            "other was Halcyan2 who is from somewhere in Illinois.\n"
            "I'm sure details on this and the other events will follow. It's\n"
            "bed time for me, so here is the deck:\n\n"
            "Mirembe Rides Again!\n"
            "by Jay Kristoff - jck@columbus.rr.com\n"
        ),
        "crypt": {
            "count": 12,
            "cards": [
                {"count": 6, "id": 200994, "name": "Mirembe Kabbada"},
                {"count": 4, "id": 200240, "name": "Camille Devereux, The Raven"},
                {"count": 2, "id": 200265, "name": "Chandler Hungerford"},
            ],
        },
        "library": {
            "count": 90,
            "cards": [
                {
                    "type": "Master",
                    "count": 14,
                    "cards": [
                        {"count": 1, "id": 100126, "name": "Backways"},
                        {"count": 1, "id": 100135, "name": "The Barrens"},
                        {"count": 1, "id": 100367, "name": "Club Zombie"},
                        {"count": 1, "id": 100545, "name": "Direct Intervention"},
                        {"count": 2, "id": 100609, "name": "Ecoterrorists"},
                        {"count": 1, "id": 101067, "name": "KRCG News Radio"},
                        {
                            "count": 1,
                            "id": 101120,
                            "name": "London Evening Star, Tabloid " "Newspaper",
                        },
                        {"count": 1, "id": 101439, "name": "Powerbase: Montreal"},
                        {
                            "count": 1,
                            "id": 101662,
                            "name": "The Rumor Mill, Tabloid Newspaper",
                        },
                        {
                            "count": 2,
                            "id": 101811,
                            "name": "Smiling Jack, The Anarch",
                        },
                        {"count": 1, "id": 101896, "name": "Sudden Reversal"},
                        {"count": 1, "id": 102212, "name": "Zoo Hunting Ground"},
                    ],
                },
                {
                    "type": "Action",
                    "count": 14,
                    "cards": [
                        {"count": 2, "id": 100093, "name": "Army of Rats"},
                        {"count": 2, "id": 100094, "name": "Arson"},
                        {"count": 3, "id": 100109, "name": "Atonement"},
                        {"count": 3, "id": 100770, "name": "Form of Corruption"},
                        {"count": 2, "id": 101740, "name": "Shadow of the Beast"},
                        {"count": 2, "id": 101954, "name": "Temptation"},
                    ],
                },
                {
                    "type": "Ally",
                    "count": 2,
                    "cards": [{"count": 2, "id": 101602, "name": "Renegade Garou"}],
                },
                {
                    "type": "Retainer",
                    "count": 7,
                    "cards": [
                        {"count": 1, "id": 101015, "name": "J. S. Simmons, Esq."},
                        {"count": 2, "id": 101249, "name": "Mr. Winthrop"},
                        {"count": 3, "id": 101550, "name": "Raven Spy"},
                        {"count": 1, "id": 101943, "name": "Tasha Morgan"},
                    ],
                },
                {
                    "type": "Action Modifier",
                    "count": 4,
                    "cards": [{"count": 4, "id": 100600, "name": "Earth Control"}],
                },
                {
                    "type": "Reaction",
                    "count": 15,
                    "cards": [
                        {"count": 2, "id": 100610, "name": "Ecstasy"},
                        {"count": 12, "id": 100760, "name": "Forced Awakening"},
                        {"count": 1, "id": 101730, "name": "Set's Call"},
                    ],
                },
                {
                    "type": "Combat",
                    "count": 34,
                    "cards": [
                        {"count": 22, "id": 100601, "name": "Earth Meld"},
                        {"count": 6, "id": 100771, "name": "Form of Mist"},
                        {"count": 6, "id": 101530, "name": "Quick Meld"},
                    ],
                },
            ],
        },
    }
    # the text version is used to generate the normalized twda, it should be there
    assert TWDA["2k2origins1"].to_txt() == (
        """Origins Thursday
Columbus, Ohio
July 4th 2002
25 players
Jay Kristoff

I just got home from an amazing first day at Origins. I was able to
eak out a tournament victory with my Mirembe Rides Again deck. 25
meths played in this event. 4 of the 5 finalists were from Ohio, the
other was Halcyan2 who is from somewhere in Illinois.
I'm sure details on this and the other events will follow. It's
bed time for me, so here is the deck:

Mirembe Rides Again!
by Jay Kristoff - jck@columbus.rr.com

Crypt (12 cards, min=16, max=20, avg=4.67)
------------------------------------------
6x Mirembe Kabbada               5 PRO SER ani    Gangrel:2
2x Camille Devereux              5 FOR PRO ani    Gangrel:1
2x Raven                         5 FOR PRO ani    Gangrel:1
2x Chandler Hungerford           3 PRO            Gangrel:2

Library (90 cards)
Master (14)
1x Backways
1x Barrens, The
1x Club Zombie
1x Direct Intervention
2x Ecoterrorists
1x KRCG News Radio
1x London Evening Star, Tabloid Newspaper
1x Powerbase: Montreal
1x Rumor Mill, Tabloid Newspaper, The
2x Smiling Jack, The Anarch
1x Sudden Reversal
1x Zoo Hunting Ground

Action (14)
2x Army of Rats
2x Arson
3x Atonement
3x Form of Corruption
2x Shadow of the Beast
2x Temptation

Ally (2)
2x Renegade Garou

Retainer (7)
1x J. S. Simmons, Esq.
2x Mr. Winthrop
3x Raven Spy
1x Tasha Morgan

Action Modifier (4)
4x Earth Control

Reaction (15)
2x Ecstasy
12x Forced Awakening
1x Set's Call

Combat (34)
22x Earth Meld
6x Form of Mist
6x Quick Meld"""
    )
    assert caplog.record_tuples == []


def test_2k8TempleConcordance(caplog):
    """Multiline comments with card names inside decklist"""
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(
        os.path.join(os.path.dirname(__file__), "2k8TempleConcordance.html")
    ) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["2k8TempleConcordance"].to_json() == {
        "date": "2008-02-01",
        "event": "TempleConcordance",
        "id": "2k8TempleConcordance",
        "name": "Howling Anarchs",
        "place": "Providence, Rhode Island",
        "player": "Matt Morgan",
        "players_count": 12,
        "tournament_format": "2R+F",
        "crypt": {
            "cards": [
                {"count": 4, "id": 200607, "name": "Howler"},
                {"count": 2, "id": 201285, "name": "The Siamese"},
                {"count": 1, "id": 200306, "name": "Cynthia Ingold"},
                {"count": 1, "id": 201051, "name": "Nettie Hale"},
                {"count": 1, "id": 200211, "name": "Bobby Lemon"},
                {"count": 1, "id": 200730, "name": "Juanita Santiago"},
                {"count": 1, "id": 200315, "name": "Dani"},
                {"count": 1, "id": 200519, "name": "Gillian Krader"},
            ],
            "count": 12,
        },
        "library": {
            "cards": [
                {
                    "cards": [
                        {"count": 1, "id": 100052, "name": "The Anarch Free Press"},
                        {"count": 4, "id": 100055, "name": "Anarch Revolt"},
                        {"count": 1, "id": 100070, "name": "Animalism"},
                        {"count": 2, "id": 100545, "name": "Direct Intervention"},
                        {"count": 1, "id": 100698, "name": "Fame"},
                        {"count": 1, "id": 100824, "name": "Giant's Blood"},
                        {"count": 1, "id": 100866, "name": "Guardian Angel"},
                        {"count": 1, "id": 101536, "name": "The Rack"},
                        {"count": 1, "id": 101704, "name": "Seattle Committee"},
                        {"count": 1, "id": 101811, "name": "Smiling Jack, The Anarch"},
                        {"count": 5, "id": 102113, "name": "Vessel"},
                    ],
                    "count": 19,
                    "type": "Master",
                },
                {
                    "cards": [
                        {"count": 1, "id": 100079, "name": "Aranthebes, The Immortal"},
                        {"count": 6, "id": 100640, "name": "Enchant Kindred"},
                        {"count": 4, "id": 101296, "name": "Nose of the Hound"},
                    ],
                    "count": 11,
                    "type": "Action",
                },
                {
                    "cards": [{"count": 1, "id": 100739, "name": "Flak Jacket"}],
                    "count": 1,
                    "type": "Equipment",
                },
                {
                    "cards": [
                        {"count": 6, "id": 101254, "name": "Murder of Crows"},
                        {"count": 1, "id": 101340, "name": "Owl Companion"},
                        {"count": 4, "id": 101550, "name": "Raven Spy"},
                    ],
                    "count": 11,
                    "type": "Retainer",
                },
                {
                    "cards": [
                        {"count": 5, "id": 101916, "name": "Swiftness of the Stag"}
                    ],
                    "count": 5,
                    "type": "Action Modifier/Combat",
                },
                {
                    "cards": [
                        {"count": 4, "id": 100308, "name": "Cats' Guidance"},
                        {"count": 4, "id": 100694, "name": "Falcon's Eye"},
                        {"count": 3, "id": 101321, "name": "On the Qui Vive"},
                        {"count": 3, "id": 101717, "name": "Sense the Savage Way"},
                        {"count": 8, "id": 101840, "name": "Speak with Spirits"},
                    ],
                    "count": 22,
                    "type": "Reaction",
                },
                {
                    "cards": [
                        {"count": 5, "id": 100029, "name": "Aid from Bats"},
                        {"count": 2, "id": 100290, "name": "Canine Horde"},
                        {"count": 3, "id": 100301, "name": "Carrion Crows"},
                        {"count": 8, "id": 101342, "name": "Pack Alpha"},
                        {"count": 2, "id": 101945, "name": "Taste of Vitae"},
                    ],
                    "count": 20,
                    "type": "Combat",
                },
                {
                    "cards": [{"count": 1, "id": 100581, "name": "Dragonbound"}],
                    "count": 1,
                    "type": "Event",
                },
            ],
            "count": 90,
        },
        "comments": (
            "Description: Continuing in my quest to with a tournament with\n"
            "every clan alphabetically, I had to put together an Ahrimanes\n"
            "deck.  I hadn't ever played them much and generally felt like\n"
            "they were a decent clan, but Howler always goes to torpor, so\n"
            "that's a pretty major liability.  I asked for some advice on\n"
            "the #vtes irc chat and eventually jhattara gave me the idea of\n"
            "playing your traditional blocking felines with some Anarch "
            "Revolts\n"
            "to speed the table up.  Great idea!  Still not having much "
            "experience\n"
            "with Ahrmanes, I basically copied David Quinonero's famous deck\n"
            "and shoehorned some Anarch Revolts.  It turned out pretty well,\n"
            "if a little slow.  I won my first round by the skin of my teeth\n"
            "and had to settle for a 2-2 split in the 2nd as my prey sort of\n"
            "ran away with the table.  The deck was ideal for the more\n"
            "deliberately-played final and I won with 2.5VP.\n\n"
            "I decided to throw a couple small guys in, but in general\n"
            "they weren't super helpful.  The deck is basically Howler\n"
            "with maybe The Siamese or Cynthia filling in if Howler is\n"
            "unwilling or unable to perform her duties.\n\n"
            "Not free and doesn't provide a press.  Can we get some\n"
            "errata?  The one time I tried to play this it was Suddened.\n\n"
            "The Anarch Revolts and Fame were responsible for both my\n"
            "game wins.  I think I nailed a couple Blood Dolls with Vessels,\n"
            "but I mostly included them over Blood Dolls because I was\n"
            "worried about master hand jam.\n\n"
            "Didn't need Aranthebes because of a lack of weenie predators.\n"
            "I mostly played the Enchant Kindreds at inferior, so they might've\n"
            "been better bleed cards (Legal, Social, Entrancement?).  4x Nose\n"
            "of the Hound was pretty nice.\n\n"
            "Okay, so I actually got my firsts ousts in the games I\n"
            "won by bleeding for 2 at 1 stealth, but I like to think the\n"
            "Anarch Revolts and Fame are what got me there.  These were\n"
            "pretty good for keeping things up close and personal with\n"
            "Flash Harrison.\n\n"
            "Never when I needed it.  Sigh.  Same with the Guardian Angel.\n\n"
            "This was mostly only good for backousting Jesse when he\n"
            "wouldn't let Howler out of a Pentex.\n\n"
            "I nearly lost the first game because I just couldn't draw\n"
            "any untap or intercept and my prey was getting away with murder\n"
            "for it.  It's weird because this looks like plenty to me.\n\n"
            "The Murders are pretty good here in that they make up for\n"
            "the fact that the support crew have inferior Animalism (not\n"
            "too scary on its own) and let Howler save on blood by doing\n"
            "a good amount of damage from long range.\n\n"
            "Pretty light combat package, especially since 8 of those\n"
            "cards don't actually do anything to hurt the opponent or\n"
            "protect my minion.  The deck obviously relies heavily on\n"
            "Howler's natural abilities and whatever permanents it can\n"
            "put together.  Some Leapfrog or Majesty or something might've\n"
            "been good, but I didn't feel like there was room for it\n"
            "and it was more important to be able to hurt opposing minions.\n"
        ),
    }
    assert caplog.record_tuples == [
        (
            "krcg",
            logging.WARNING,
            '[    80][2k8TempleConcordance] discarded match "flash harrison." inside '
            'comment "Flash Harrison. */"',
        ),
    ]


def test_10211(caplog):
    """Evolution where group is not indicated in the name (but at end of line)"""
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "10211.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["10211"].to_json() == {
        "date": "2022-06-09",
        "event": "10211Origins - Thursday 2",
        "event_link": "https://www.vekn.net/event-calendar/event/10211",
        "id": "10211",
        "place": "Columbus, Ohio",
        "player": "Darby Keeney",
        "players_count": 21,
        "score": "1GW6+3",
        "tournament_format": "2R+F",
        "comments": "Description: Bruise bleed based around V5 Brujah Barons, New "
        "Carthage and Anarch bleed cards. It carries light multi-action, "
        "a touch of stealth and just enough bounce that it doesn't have "
        "to look left immediately. The titles influence others' political "
        "actions, even if I'm not using them myself.\n"
        "\n"
        "In the final, I roasted my prey's opening (famous) Malgorzata "
        "even though she dropped a Blood of Acid in the first combat.  It "
        "was ENTIRELY worth losing a 3-cap who had already done the "
        "Illegalism/unlock/Manifesto trick.  I ate Mal a turn or two "
        "later, just to be sure she didn't make beads.\n"
        "\n"
        "The original build used more superior Presence minions but no "
        "Theo and some Enchant Kindred. I didn't like the pace at which "
        "it played and adjusted for more immediate offense.  I finally "
        "broke down and added Theo right before Origins - he sheds red "
        "cards and I get a second +1 strength minion.\n"
        "Every one of those revisions made the deck better and this "
        "iteration feels extremely solid.\n"
        "\n"
        "-- I think there might be a 78 card version that's even more "
        "consistent.  And no, you don't need Ashur Tablets.\n",
        "crypt": {
            "cards": [
                {"count": 2, "id": 201613, "name": "Theo Bell (G6)"},
                {"count": 2, "id": 201576, "name": "Aline Gädeke"},
                {"count": 2, "id": 201614, "name": "Valeriya Zinovieva"},
                {"count": 2, "id": 201526, "name": "Leumeah"},
                {"count": 1, "id": 201579, "name": "Atiena"},
                {"count": 1, "id": 201581, "name": "Brandon Grime"},
                {"count": 1, "id": 201585, "name": "Elen Kamjian"},
                {"count": 1, "id": 200132, "name": "Ariane"},
            ],
            "count": 12,
        },
        "library": {
            "cards": [
                {
                    "cards": [
                        {"count": 2, "id": 100199, "name": "Blood Doll"},
                        {"count": 1, "id": 100297, "name": "Carfax Abbey"},
                        {
                            "comments": "dangerous play in today's meta",
                            "count": 1,
                            "id": 100366,
                            "name": "Club Illusion",
                        },
                        {"count": 2, "id": 100588, "name": "Dreams of the Sphinx"},
                        {"count": 1, "id": 100698, "name": "Fame"},
                        {
                            "comments": "this card just keeps getting " "better.",
                            "count": 1,
                            "id": 100809,
                            "name": "Garibaldi-Meucci Museum",
                        },
                        {"count": 1, "id": 100824, "name": "Giant's Blood"},
                        {
                            "comments": "this version could probably " "drop to 1 copy",
                            "count": 2,
                            "id": 101277,
                            "name": "New Carthage",
                        },
                        {
                            "comments": "more unlocked Barons at the "
                            "end of my turn.",
                            "count": 1,
                            "id": 101435,
                            "name": "Powerbase: Los Angeles",
                        },
                        {
                            "comments": "this could be 6 copies and the "
                            "deck wouldn't suffer.",
                            "count": 5,
                            "id": 102121,
                            "name": "Villein",
                        },
                        {"count": 1, "id": 102150, "name": "Warzone Hunting Ground"},
                    ],
                    "count": 18,
                    "type": "Master",
                },
                {
                    "cards": [
                        {
                            "comments": "should probably change to LA "
                            "just for thematic reasons",
                            "count": 1,
                            "id": 100715,
                            "name": "Fee Stake: New York",
                        },
                        {
                            "comments": "combat minions that bleed, "
                            "then unlock and fight are "
                            "pretty good.",
                            "count": 9,
                            "id": 100952,
                            "name": "Illegalism",
                        },
                        {
                            "comments": "see above. The occasional pool "
                            "steal can screw up other "
                            "players' math.",
                            "count": 10,
                            "id": 102229,
                            "name": "Line Brawl",
                        },
                        {
                            "comments": "almost overkill with Theo and " "Line Brawls.",
                            "count": 1,
                            "id": 101324,
                            "name": "Open War",
                        },
                    ],
                    "count": 21,
                    "type": "Action",
                },
                {
                    "cards": [
                        {
                            "comments": "slotted during last revision, "
                            "these things are gold in the "
                            "mid game (get them AFTER you "
                            "unlock from Illegialism, don't "
                            "defer bleed actions to get it)",
                            "count": 2,
                            "id": 100053,
                            "name": "Anarch Manifesto, An",
                        }
                    ],
                    "count": 2,
                    "type": "Equipment",
                },
                {
                    "cards": [
                        {
                            "comments": "I didn't bother with the "
                            "unlimited [pot] line with a "
                            "Monkey Wrench, it's better to "
                            "just have these for stealth on "
                            "bleeds.",
                            "count": 6,
                            "id": 101429,
                            "name": "Power of One",
                        },
                        {
                            "comments": "don't laugh...even at inferior "
                            "it is an unlocked bouncer (or "
                            "a multirushing Theo at "
                            "superior).",
                            "count": 2,
                            "id": 102205,
                            "name": "Zephyr",
                        },
                    ],
                    "count": 8,
                    "type": "Action Modifier",
                },
                {
                    "cards": [
                        {
                            "comments": "this card is shaking up the "
                            "meta around here.",
                            "count": 5,
                            "id": 102218,
                            "name": "Bait and Switch",
                        }
                    ],
                    "count": 5,
                    "type": "Reaction",
                },
                {
                    "cards": [
                        {
                            "comments": "kind of iffy, but I like "
                            "having extra maneuvers and "
                            "presses hanging around.",
                            "count": 2,
                            "id": 100232,
                            "name": "Bollix",
                        },
                        {
                            "comments": "never played on a minion I "
                            "wasn't dunking anyway, this "
                            "might be overkill.",
                            "count": 2,
                            "id": 100549,
                            "name": "Disarm",
                        },
                        {
                            "comments": "only OK in this deck since "
                            "Dust Up often eats the "
                            "additional strike.",
                            "count": 3,
                            "id": 100563,
                            "name": "Diversion",
                        },
                        {
                            "comments": "underrated as a dual use " "combat tool.",
                            "count": 10,
                            "id": 100597,
                            "name": "Dust Up",
                        },
                        {
                            "comments": "because Earth Meld decks need "
                            "to be killed with fire.",
                            "count": 4,
                            "id": 100959,
                            "name": "Immortal Grapple",
                        },
                        {
                            "comments": "sometimes minions just need to " "stay down",
                            "count": 2,
                            "id": 101515,
                            "name": "Pulled Fangs",
                        },
                        {
                            "comments": "slotted in yet another [pot] "
                            "deck....this card is poorly "
                            "designed.",
                            "count": 5,
                            "id": 101942,
                            "name": "Target Vitals",
                        },
                        {"count": 4, "id": 101945, "name": "Taste of Vitae"},
                        {
                            "comments": 'a token nod to "screw your '
                            'Sniper Rifle" with backup '
                            "defensive value",
                            "count": 4,
                            "id": 101982,
                            "name": "Thrown Gate",
                        },
                    ],
                    "count": 36,
                    "type": "Combat",
                },
            ],
            "count": 90,
        },
    }


def test_11435(caplog):
    """New cards issue with Touch of Valeren"""
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "11435.html")) as f:
        TWDA.load_html(f)
    assert len(TWDA) == 1
    assert TWDA["11435"].to_json() == {
        "comments": "A brief explanation about the final, from my point of view.\n"
        "With 1GW4VP I placed second (new salubri powerbleed), so a quite good "
        "position to pick my seat.\n"
        "The other finalists were:\n"
        "Marc Alvarez (1st) Matasuntha rush\n"
        "Albert Dulcet (3rd)  Marie Faucigny with equipments (strange deck)\n"
        "Xavier Macias (4th) Ravnos\n"
        "Germán Sánchez (Gangrel block)\n"
        "When I got the chance to pick my place the order was already:\n"
        "Xavier Macias (Ravnos) -> Albert Dulcet (Marie Faucigny) -> Germán "
        "Sanchez (Gangrel block)\n"
        "I knew I didn't want to prey the gangrels, my thoughts about the Ravnos "
        "were that it was a toolboox with bleed reduction, so ideal choice was "
        "between Ravnos and Marie, but I was sure that Matasuntha would then place "
        "behind me so I risked it and placed myself between Gangrel and the "
        "Ravnos, hoping to get out early and put some pressure on my prey. Marc "
        "placed preying Albert.\n"
        "Pulled out Seraphina and had a GtU and a SM in hand with a freak drive, "
        "so was quite confident to get my second vampire early. Played seduction "
        "on the only Ravnos Xavier had, but unfortunately Kuyén decided to block "
        "me.\n"
        "- I know your deck- Were Germán's words, so I knew he wasn't going to let "
        "me play easily, so decided to bring my second vampire transferring from "
        "my pool.\n"
        "Matasuntha start putting quite some pressure on Marie, but I knew Albert "
        "playstyle, and he is a very resourceful person, and really hard to kill, "
        "so the Gangrels were free to roam, and a couple more joined Kuyén son "
        "enough.\n"
        "A bit later, Xavier discarded a Pentex, so having one in hand I knew "
        "there was my chance, so with a few tricks from the salubris I manage to "
        "give is pool quite a big bite, but not enough to oust him.\n"
        "Germán put some pressure on me, not heavy but steady with 2 or 3 bleeds "
        "per turn, I was lucky to get almost all my deflections, redirections and "
        "TM and that prevent me from dyeing and lowering Xavier's pool a bit. Then "
        "he played a risky move, bringing Club Illusion to the game with some sort "
        "of agreement with my anarch predator, that if he killed me, he would "
        "allow a couple of turns of peace so the Ravnos could recover.\n"
        "Matasuntha's attention suddenly faded from Marie and turned backwards, as "
        "she had 4 vampires with a potential bleed of 9 and Marc's pool was only "
        "at 13, so she multirushed backwards, torporizing 3 vampires. Albert "
        "offered to rescue 1 on order to safe Xavier and keep Matasuntha busy with "
        "him.\n"
        "On his turn, German tried to oust me with his full potential, he had "
        "previously recovered a Monkey Wrench with his Garibaldi, so I was ready "
        "for it and he failed.\n"
        "My second chance was right in front of me, and I wasn't going to waste "
        "it, so I jumped towards Xavier's exposed pool and this time I manage to "
        "successfully oust him, but even before I could savor my victory I felt "
        "Matasuntha's eyes upon me, so with my sweetest salubri voice I offered a "
        "deal, and after a few give and take we manage to get ourselves an "
        "understanding.\n"
        "Marc will not rush me, and I will not bleed him, and the first Monkey "
        "Wrench German played I will directly deflect to Albert, all the other "
        "bleeds I could deflect them to Marc. I knew it wasn't much of a deal, "
        "Albert would get heavy pressure again and the Gangrel will be free to "
        "roam around me, and so he did bringing a 5th vampire to the game, but it "
        "was too late and the finale concluded a few turns after.\n"
        "Special mention to Marie and her crew, who suffered repeatedly "
        "Matasuntha's rushes but manage to come back from torpor more times than "
        "it seems even possible.\n"
        "Hope you all like my chronicle and apologize for my limited English.\n"
        "Miki\n"
        "P.D. Hope I have reported it correctly, if something is missing let me "
        "know.\n",
        "crypt": {
            "cards": [
                {
                    "count": 2,
                    "id": 201663,
                    "name": "Abaddon",
                },
                {
                    "count": 2,
                    "id": 201686,
                    "name": "Seraphina",
                },
                {
                    "count": 2,
                    "id": 201666,
                    "name": "Aniel",
                },
                {
                    "count": 2,
                    "id": 201676,
                    "name": "Malachi",
                },
                {
                    "count": 2,
                    "id": 201680,
                    "name": "Opikun",
                },
                {
                    "count": 1,
                    "id": 201673,
                    "name": "Ilonka",
                },
                {
                    "count": 1,
                    "id": 201691,
                    "name": "Yael",
                },
            ],
            "count": 12,
        },
        "date": "2024-05-04",
        "event": "Powerbase Badalona 2024",
        "event_link": "https://www.vekn.net/event-calendar/event/11435",
        "id": "11435",
        "library": {
            "cards": [
                {
                    "cards": [
                        {
                            "count": 1,
                            "id": 100058,
                            "name": "Anarch Troublemaker",
                        },
                        {
                            "count": 2,
                            "id": 100199,
                            "name": "Blood Doll",
                        },
                        {
                            "count": 1,
                            "id": 100435,
                            "name": "The Coven",
                        },
                        {
                            "count": 1,
                            "id": 100545,
                            "name": "Direct Intervention",
                        },
                        {
                            "count": 1,
                            "id": 100824,
                            "name": "Giant's Blood",
                        },
                        {
                            "count": 1,
                            "id": 102252,
                            "name": "Meditative Grove",
                        },
                        {
                            "count": 2,
                            "id": 101384,
                            "name": "Pentex™ Subversion",
                        },
                        {
                            "count": 4,
                            "id": 101388,
                            "name": "Perfectionist",
                        },
                        {
                            "count": 1,
                            "id": 102259,
                            "name": "Saulot's Healing Touch",
                        },
                    ],
                    "count": 14,
                    "type": "Master",
                },
                {
                    "cards": [
                        {
                            "count": 6,
                            "id": 102248,
                            "name": "Feast of the Soul's Secrets",
                        },
                        {
                            "count": 7,
                            "id": 100845,
                            "name": "Govern the Unaligned",
                        },
                        {
                            "count": 6,
                            "id": 101698,
                            "name": "Scouting Mission",
                        },
                    ],
                    "count": 19,
                    "type": "Action",
                },
                {
                    "cards": [
                        {
                            "count": 6,
                            "id": 102262,
                            "name": "Touch of Valeren",
                        },
                    ],
                    "count": 6,
                    "type": "Action/Combat",
                },
                {
                    "cards": [
                        {
                            "count": 1,
                            "id": 100298,
                            "name": "Carlton Van Wyk",
                        },
                    ],
                    "count": 1,
                    "type": "Ally",
                },
                {
                    "cards": [
                        {
                            "count": 1,
                            "id": 100903,
                            "name": "Heart of Nizchetus",
                        },
                    ],
                    "count": 1,
                    "type": "Equipment",
                },
                {
                    "cards": [
                        {
                            "count": 4,
                            "id": 100236,
                            "name": "Bonding",
                        },
                        {
                            "count": 3,
                            "id": 100492,
                            "name": "Daring the Dawn",
                        },
                        {
                            "count": 6,
                            "id": 102250,
                            "name": "Forced Confessional",
                        },
                        {
                            "count": 8,
                            "id": 100788,
                            "name": "Freak Drive",
                        },
                        {
                            "count": 4,
                            "id": 101712,
                            "name": "Seduction",
                        },
                        {
                            "count": 2,
                            "id": 101978,
                            "name": "Threats",
                        },
                        {
                            "count": 5,
                            "id": 102263,
                            "name": "Unleashing the Bestial Soul",
                        },
                    ],
                    "count": 32,
                    "type": "Action Modifier",
                },
                {
                    "cards": [
                        {
                            "count": 5,
                            "id": 100518,
                            "name": "Deflection",
                        },
                        {
                            "count": 2,
                            "id": 100519,
                            "name": "Delaying Tactics",
                        },
                        {
                            "count": 3,
                            "id": 100680,
                            "name": "Eyes of Argus",
                        },
                        {
                            "count": 3,
                            "id": 101321,
                            "name": "On the Qui Vive",
                        },
                        {
                            "count": 2,
                            "id": 101578,
                            "name": "Redirection",
                        },
                        {
                            "count": 2,
                            "id": 101949,
                            "name": "Telepathic Misdirection",
                        },
                    ],
                    "count": 17,
                    "type": "Reaction",
                },
            ],
            "count": 90,
        },
        "name": "Nuevos Salubri (New Salubri)",
        "place": "Badalona, Spain",
        "player": "Miquel Jorge Tortajada",
        "players_count": 25,
        "tournament_format": "2R+F",
    }
