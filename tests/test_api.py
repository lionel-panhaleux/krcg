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


def test_card(client):
    response = client.get("/complete")
    assert response.status_code == 404
    response = client.get("/complete/NotACard")
    assert response.status_code == 200
    assert response.json == []
    response = client.get("/complete/unn")
    assert response.status_code == 200
    assert response.json == ["The unnamed", "Unnatural Disaster"]


def test_deck(client):
    response = client.post("/deck")
    assert response.status_code == 200
    assert len(response.json) == 100
    response = client.post("/deck", json={"cards": ["Stavros"]})
    assert response.status_code == 200
    assert len(response.json) == 3
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
                {"comments": None, "count": 5, "name": "Anarch Convert",},
                {"comments": None, "count": 1, "name": "Francesca Giovanni",},
                {"comments": None, "count": 1, "name": "Gloria Giovanni",},
                {"comments": None, "count": 1, "name": "Cristofero Giovanni",},
                {"comments": None, "count": 1, "name": "Lia Milliner"},
                {"comments": None, "count": 1, "name": "Mario Giovanni",},
                {"comments": None, "count": 1, "name": "Rudolfo Giovanni",},
                {
                    "comments": None,
                    "count": 1,
                    "name": "Marciana Giovanni, Investigator",
                },
                {"comments": None, "count": 1, "name": "Paul DiCarlo, The Alpha",},
            ],
            "count": 13,
        },
        "date": "2019-12-15",
        "event": "Rapid Healing",
        "library": {
            "cards": [
                {
                    "cards": [
                        {"comments": None, "count": 5, "name": "Liquidation",},
                        {"comments": None, "count": 3, "name": "Piper"},
                        {"comments": None, "count": 2, "name": "Anarch Railroad",},
                        {"comments": None, "count": 2, "name": "Creepshow Casino",},
                        {"comments": None, "count": 2, "name": "Jake Washington",},
                        {
                            "comments": "this can probably be omitted " "now.\n",
                            "count": 1,
                            "name": "Anarch Troublemaker",
                        },
                        {"comments": None, "count": 1, "name": "Direct Intervention",},
                        {
                            "comments": "unused this tournament\n",
                            "count": 1,
                            "name": "Garibaldi-Meucci Museum",
                        },
                        {
                            "comments": None,
                            "count": 1,
                            "name": "Pentex(TM) Subversion",
                        },
                        {
                            "comments": None,
                            "count": 1,
                            "name": "Powerbase: Cape Verde",
                        },
                        {
                            "comments": None,
                            "count": 1,
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
                            "name": "Khazar's Diary (Endless Night)",
                        },
                        {
                            "comments": "Recursion is dumb, dumb, dumb.\n",
                            "count": 5,
                            "name": "Sudario Refraction",
                        },
                        {"comments": None, "count": 4, "name": "The Embrace",},
                    ],
                    "count": 18,
                    "type": "Action",
                },
                {
                    "cards": [
                        {
                            "comments": None,
                            "count": 3,
                            "name": "Call of the Hungry Dead",
                        }
                    ],
                    "count": 3,
                    "type": "Action Modifier",
                },
                {
                    "cards": [{"comments": None, "count": 5, "name": "Target Vitals",}],
                    "count": 5,
                    "type": "Combat",
                },
                {
                    "cards": [
                        {"comments": None, "count": 5, "name": "On the Qui Vive",},
                        {"comments": None, "count": 4, "name": "Deflection",},
                        {"comments": None, "count": 2, "name": "Delaying Tactics",},
                    ],
                    "count": 11,
                    "type": "Reaction",
                },
                {
                    "cards": [
                        {"comments": None, "count": 1, "name": "Heart of Nizchetus",}
                    ],
                    "count": 1,
                    "type": "Equipment",
                },
                {
                    "cards": [
                        {
                            "comments": "extra entries in the Diary.\n",
                            "count": 8,
                            "name": "Cry Wolf",
                        },
                        {"comments": None, "count": 1, "name": "Carlton Van Wyk",},
                        {
                            "comments": "Burn guns, get an entry in the Diary.\n",
                            "count": 1,
                            "name": "Gianna di Canneto",
                        },
                        {"comments": None, "count": 1, "name": "Ossian",},
                        {
                            "comments": "synergy with Wolves, see also "
                            "dumb, dumb, dumb.\n",
                            "count": 1,
                            "name": "Tye Cooper",
                        },
                        {"comments": None, "count": 1, "name": "Vivienne Géroux",},
                    ],
                    "count": 13,
                    "type": "Ally",
                },
                {
                    "cards": [
                        {"comments": None, "count": 2, "name": "The Unmasking",},
                        {
                            "comments": None,
                            "count": 1,
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
