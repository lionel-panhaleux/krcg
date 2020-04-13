import pytest

from src import twda
from src import vtes

# speed up the tests: parse the first 100 decks only to avoid useless 25 seconds.
# need to load before import flask.py to avoid launching the initialization thread.
vtes.VTES.load_from_vekn(save=False)
twda.TWDA.load_from_vekn(limit=100, save=False)

from src import flask  # noqa: E402


@pytest.fixture
def client():
    flask.app.config["TESTING"] = True
    with flask.app.test_client() as client:
        yield client


def test_complete(client):
    response = client.get("/complete")
    assert response.status_code == 404
    response = client.get("/complete/NotACard")
    assert response.status_code == 200
    assert response.json == []
    response = client.get("/complete/unn")
    assert response.status_code == 200
    assert response.json == ["The unnamed", "Unnatural Disaster"]


def test_card(client):
    response = client.get("/card/NotACard")
    assert response.status_code == 404
    response = client.get("/card/Alastor")
    assert response.status_code == 200
    assert response.json == {
        "Id": "100038",
        "Name": "Alastor",
        "Aka": "",
        "Type": ["Political Action"],
        "Clan": [],
        "Discipline": [],
        "Pool Cost": "",
        "Blood Cost": "",
        "Conviction Cost": "",
        "Burn Option": False,
        "Card Text": (
            "Requires a justicar or Inner Circle member.\n"
            "Choose a ready Camarilla vampire. If this referendum is successful, "
            "search your library for an equipment card and place this card "
            "and the equipment on the chosen vampire. "
            "Pay half the cost (round down) of the equipment. "
            "This vampire may enter combat with any vampire "
            "controlled by another Methuselah as a +1 stealth Ⓓ  action. "
            "This vampire cannot commit diablerie. A vampire may have only one Alastor."
        ),
        "Flavor Text": "",
        "Set": ["Gehenna:R", "KMW:PAl", "KoT:R"],
        "Requirement": ["justicar", "inner circle"],
        "Banned": "",
        "Artist": "Monte Moore",
        "Capacity": "",
        "Draft": "",
        "Rulings": [
            "If the given weapon costs blood, "
            "the target Alastor pays the cost. [LSJ 20040518]"
        ],
        "Rulings Links": [
            {
                "Reference": "LSJ 20040518",
                "URL": "https://groups.google.com/d/msg/rec.games.trading-cards.jyhad/"
                "4emymfUPwAM/B2SCC7L6kuMJ",
            }
        ],
    }


def test_deck(client):
    response = client.post("/deck")
    assert response.status_code == 200
    assert len(response.json) == 100
    response = client.post("/deck", json={"cards": ["Stavros"]})
    assert response.status_code == 200
    assert len(response.json) == 2
    response = client.post("/deck", json={"cards": ["Not a Card"]})
    assert response.status_code == 400
    response = client.post("/deck", json={"cards": ["Antithesis"]})
    assert response.status_code == 404
    response = client.post("/deck", json={"cards": [""]})
    response = client.get("/deck/2019rhho")
    assert response.json == {
        "twda_id": "2019rhho",
        "name": "Farley Mowat V2.01",
        "place": "Heath, Ohio",
        "player": "Darby Keeney",
        "author": None,
        "players_count": 10,
        "score": "0GW2+4",
        "tournament_format": "2R+F",
        "comments": 'Named after the author of the hilarious book "Never Cry Wolf," '
        "this is a\n"
        "twice-modified version of previously winning deck. This iteration seems more\n"
        "stable than previous versions. And I absolutely should have "
        "played this for the\n"
        "previous day's Cup event, when I was 100% certain there would be "
        "at least one\n"
        "Legionnaire deck floating around.\n"
        "\n"
        "The kinda-recent sect inheritance change helps with Cry Wolf and "
        "the Railroad, so Seattle Committee and Twilight Camp could be "
        "removed from the library.\n"
        "\n"
        "This isn't THAT many allies to transform, but there are usually "
        "possibilities from other players' ash heaps before harvesting my "
        "own.\n",
        "crypt": {
            "cards": [
                {
                    "comments": None,
                    "count": 5,
                    "id": "200076",
                    "name": "Anarch Convert",
                },
                {
                    "comments": None,
                    "count": 1,
                    "id": "200474",
                    "name": "Francesca Giovanni",
                },
                {
                    "comments": None,
                    "count": 1,
                    "id": "200525",
                    "name": "Gloria Giovanni",
                },
                {
                    "comments": None,
                    "count": 1,
                    "id": "200301",
                    "name": "Cristofero Giovanni",
                },
                {"comments": None, "count": 1, "id": "200834", "name": "Lia Milliner"},
                {
                    "comments": None,
                    "count": 1,
                    "id": "200932",
                    "name": "Mario Giovanni",
                },
                {
                    "comments": None,
                    "count": 1,
                    "id": "201209",
                    "name": "Rudolfo Giovanni",
                },
                {
                    "comments": None,
                    "count": 1,
                    "id": "200913",
                    "name": "Marciana Giovanni, Investigator",
                },
                {
                    "comments": None,
                    "count": 1,
                    "id": "201101",
                    "name": "Paul DiCarlo, The Alpha",
                },
            ],
            "count": 13,
        },
        "date": "2019-12-15",
        "event": "Rapid Healing",
        "library": {
            "cards": [
                {
                    "cards": [
                        {
                            "comments": None,
                            "count": 5,
                            "id": "101112",
                            "name": "Liquidation",
                        },
                        {"comments": None, "count": 3, "id": "101401", "name": "Piper"},
                        {
                            "comments": None,
                            "count": 2,
                            "id": "100054",
                            "name": "Anarch Railroad",
                        },
                        {
                            "comments": None,
                            "count": 2,
                            "id": "100444",
                            "name": "Creepshow Casino",
                        },
                        {
                            "comments": None,
                            "count": 2,
                            "id": "101019",
                            "name": "Jake Washington",
                        },
                        {
                            "comments": "this can probably be omitted " "now.\n",
                            "count": 1,
                            "id": "100058",
                            "name": "Anarch Troublemaker",
                        },
                        {
                            "comments": None,
                            "count": 1,
                            "id": "100545",
                            "name": "Direct Intervention",
                        },
                        {
                            "comments": "unused this tournament\n",
                            "count": 1,
                            "id": "100809",
                            "name": "Garibaldi-Meucci Museum",
                        },
                        {
                            "comments": None,
                            "count": 1,
                            "id": "101384",
                            "name": "Pentex(TM) Subversion",
                        },
                        {
                            "comments": None,
                            "count": 1,
                            "id": "101433",
                            "name": "Powerbase: Cape Verde",
                        },
                        {
                            "comments": None,
                            "count": 1,
                            "id": "101435",
                            "name": "Powerbase: Los Angeles",
                        },
                    ],
                    "count": 20,
                    "type": "Master",
                },
                {
                    "cards": [
                        {
                            "comments": 'The "Moose Juice" of this deck.\n',
                            "count": 9,
                            "id": "101046",
                            "name": "Khazar's Diary (Endless Night)",
                        },
                        {
                            "comments": "Recursion is dumb, dumb, dumb.\n",
                            "count": 5,
                            "id": "101895",
                            "name": "Sudario Refraction",
                        },
                        {
                            "comments": None,
                            "count": 4,
                            "id": "100633",
                            "name": "The Embrace",
                        },
                    ],
                    "count": 18,
                    "type": "Action",
                },
                {
                    "cards": [
                        {
                            "comments": None,
                            "count": 3,
                            "id": "100279",
                            "name": "Call of the Hungry Dead",
                        }
                    ],
                    "count": 3,
                    "type": "Action Modifier",
                },
                {
                    "cards": [
                        {
                            "comments": None,
                            "count": 5,
                            "id": "101942",
                            "name": "Target Vitals",
                        }
                    ],
                    "count": 5,
                    "type": "Combat",
                },
                {
                    "cards": [
                        {
                            "comments": None,
                            "count": 5,
                            "id": "101321",
                            "name": "On the Qui Vive",
                        },
                        {
                            "comments": None,
                            "count": 4,
                            "id": "100518",
                            "name": "Deflection",
                        },
                        {
                            "comments": None,
                            "count": 2,
                            "id": "100519",
                            "name": "Delaying Tactics",
                        },
                    ],
                    "count": 11,
                    "type": "Reaction",
                },
                {
                    "cards": [
                        {
                            "comments": None,
                            "count": 1,
                            "id": "100903",
                            "name": "Heart of Nizchetus",
                        }
                    ],
                    "count": 1,
                    "type": "Equipment",
                },
                {
                    "cards": [
                        {
                            "comments": "extra entries in the Diary.\n",
                            "count": 8,
                            "id": "100475",
                            "name": "Cry Wolf",
                        },
                        {
                            "comments": None,
                            "count": 1,
                            "id": "100298",
                            "name": "Carlton Van Wyk",
                        },
                        {
                            "comments": "Burn guns, get an entry in the Diary.\n",
                            "count": 1,
                            "id": "100823",
                            "name": "Gianna di Canneto",
                        },
                        {
                            "comments": None,
                            "count": 1,
                            "id": "101333",
                            "name": "Ossian",
                        },
                        {
                            "comments": "synergy with Wolves, see also "
                            "dumb, dumb, dumb.\n",
                            "count": 1,
                            "id": "102053",
                            "name": "Tye Cooper",
                        },
                        {
                            "comments": None,
                            "count": 1,
                            "id": "102128",
                            "name": "Vivienne Géroux",
                        },
                    ],
                    "count": 13,
                    "type": "Ally",
                },
                {
                    "cards": [
                        {
                            "comments": None,
                            "count": 2,
                            "id": "102079",
                            "name": "The Unmasking",
                        },
                        {
                            "comments": None,
                            "count": 1,
                            "id": "100709",
                            "name": "FBI Special Affairs Division",
                        },
                    ],
                    "count": 3,
                    "type": "Event",
                },
            ],
            "count": 74,
        },
    }
