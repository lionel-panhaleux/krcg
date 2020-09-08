import pytest
import requests

from src import flask  # noqa: E402


@pytest.fixture
def client():
    app = flask.create_app(test=True)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_complete(client):
    response = client.get("/complete")
    assert response.status_code == 404
    response = client.get("/complete/NotACard")
    assert response.status_code == 200
    assert response.json == []
    # same match level, order alphabetically
    response = client.get("/complete/unn")
    assert response.status_code == 200
    assert response.json == ["The unnamed", "Unnatural Disaster"]
    # first word is a better match
    response = client.get("/complete/pentex")
    assert response.status_code == 200
    assert response.json == [
        "Pentex™ Loves You!",
        "Pentex™ Subversion",
        "Enzo Giovanni, Pentex Board of Directors",
        "Enzo Giovanni, Pentex Board of Directors (ADV)",
        "Harold Zettler, Pentex Director",
    ]
    # for multiple words, all must match
    response = client.get("/complete/the%20ru")
    assert response.status_code == 200
    assert response.json == [
        "The Rumor Mill, Tabloid Newspaper",
        "Darvag, The Butcher of Rus",
    ]
    # match names with special chars
    response = client.get("/complete/rot")
    assert response.status_code == 200
    assert response.json == ["Rötschreck", "Ulrike Rothbart"]


def test_card(client):
    response = client.get("/card/NotACard")
    assert response.status_code == 404
    response = client.get("/card/Alastor")
    assert response.status_code == 200
    assert response.json == {
        "Id": "100038",
        "Name": "Alastor",
        "Image": "https://images.krcg.org/alastor.jpg",
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
            "the target Alastor pays the cost. [LSJ 20040518]",
            "Requirements do not apply. [ANK 20200901]",
        ],
        "Rulings Links": [
            {
                "Reference": "LSJ 20040518",
                "URL": "https://groups.google.com/d/msg/rec.games.trading-cards.jyhad/"
                "4emymfUPwAM/B2SCC7L6kuMJ",
            },
            {
                "Reference": "ANK 20200901",
                "URL": "http://www.vekn.net/forum/rules-questions/"
                "78830-alastor-and-ankara-citadel#100653",
            },
        ],
    }
    id_response = client.get("/card/100038")
    assert id_response.status_code == 200
    assert id_response.json == response.json
    # slash in names cannot be used
    response = client.get("/card/Kpist%20m45")
    assert response.status_code == 200


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
        "score": "0gw2 + 4vp in the final",
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
                            "name": "Pentex™ Subversion",
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


def test_search(client):
    response = client.post("/card")
    assert response.status_code == 200
    assert len(response.json) == 3738
    # non-existing filters have no impact
    response = client.post("/card", json={"foo": ["bar"]})
    assert response.status_code == 200
    assert len(response.json) == 3738
    # non-existing values do not crash
    response = client.post("/card", json={"bonus": ["foo"]})
    assert response.status_code == 200
    assert len(response.json) == 0
    response = client.post("/card", json={"trait": ["foo"]})
    assert response.status_code == 200
    assert len(response.json) == 0
    # discipline, title
    response = client.post(
        "/card", json={"trait": ["primogen"], "discipline": ["serpentis"]}
    )
    assert response.json == ["Amenophobis"]
    # city title
    response = client.post("/card", json={"trait": ["chicago"]})
    assert response.json == [
        "Antón de Concepción",
        "Crusade: Chicago",
        "Lachlan, Noddist",
        "Lodin (Olaf Holte)",
        "Maldavis (ADV)",
        "Praxis Seizure: Chicago",
        "Sir Walter Nash",
    ]
    # stealth, votes
    response = client.post("/card", json={"bonus": ["stealth", "votes"]})
    assert response.json == [
        "Antonio Veradas",
        "Bulscu (ADV)",
        "Dark Selina",
        "Jessica (ADV)",
        "Joseph Cambridge",
        "Karen Suadela",
        "Loki's Gift",
        "Maxwell",
        "Natasha Volfchek",
        "Perfect Paragon",
        "Sela (ADV)",
        "Suhailah",
        "Zayyat, The Sandstorm",
    ]

    # votes provided by master cards
    response = client.post(
        "/card",
        json={"bonus": ["votes"], "clan": ["Assamite"], "type": ["Master"]},
    )
    assert response.json == ["Alamut", "The Black Throne"]
    # votes provided by titles
    response = client.post(
        "/card",
        json={"bonus": ["votes"], "clan": ["Assamite"], "group": ["3"]},
    )
    assert response.json == ["Enam", "Rebekah"]
    # title when MERGED
    response = client.post("/card", json={"clan": ["Assamite"], "trait": ["justicar"]})
    assert response.json == ["Tegyrius, Vizier (ADV)"]
    # traits: black hand, red list ...
    response = client.post(
        "/card",
        json={"clan": ["Nagaraja"], "trait": ["black hand"]},
    )
    assert response.json == ["Sennadurek"]
    response = client.post("/card", json={"clan": ["Assamite"], "trait": ["red list"]})
    assert response.json == ["Jamal", "Tariq, The Silent (ADV)"]
    # sect
    response = client.post(
        "/card",
        json={"clan": ["assamite"], "trait": ["camarilla"], "group": ["2"]},
    )
    assert response.json == [
        "Al-Ashrad, Amr of Alamut (ADV)",
        "Tegyrius, Vizier",
        "Tegyrius, Vizier (ADV)",
    ]
    # traits on library cards
    response = client.post(
        "/card",
        json={"type": ["action modifier"], "trait": ["black hand"]},
    )
    assert response.json == [
        "Circumspect Revelation",
        "Seraph's Second",
        "The Art of Memory",
    ]
    # required title
    response = client.post("/card", json={"type": ["reaction"], "trait": ["justicar"]})
    assert response.json == ["Legacy of Power", "Second Tradition: Domain"]
    # "Requires titled Sabbat/Camarilla" maps to all possible titles
    response = client.post(
        "/card",
        json={"bonus": ["intercept"], "trait": ["archbishop"]},
    )
    assert response.json == [
        "Matteus, Flesh Sculptor",
        "National Guard Support",
        "Persona Non Grata",
        "Under Siege",
    ]
    # Reducing intercept is stealth
    response = client.post(
        "/card",
        json={"bonus": ["stealth"], "discipline": ["chimerstry"], "type": ["library"]},
    )
    assert response.json == [
        "Fata Morgana",
        "Mirror's Visage",
        "Smoke and Mirrors",
        "Will-o'-the-Wisp",
    ]
    # Reducing stealth is intercept
    response = client.post(
        "/card",
        json={
            "bonus": ["intercept"],
            "discipline": ["chimerstry"],
            "type": ["library"],
        },
    )
    assert response.json == [
        "Draba",
        "Ignis Fatuus",
        # multi-disc are tricky: it has chi, it has intercept.
        # chi doesn't provide intercept, but it matches - fair enough
        "Netwar",
        "Veiled Sight",
    ]
    # no discipline (crypt)
    response = client.post("/card", json={"discipline": ["none"], "type": ["crypt"]})
    assert response.json == ["Anarch Convert", "Sandra White", "Smudge the Ignored"]
    response = client.post(
        "/card",
        json={"discipline": ["none"], "bonus": ["intercept"], "trait": ["sabbat"]},
    )
    # no discipline, sect (or independent) required
    assert response.json == ["Abbot", "Harzomatuili", "Under Siege"]
    response = client.post(
        "/card",
        json={"type": ["political action"], "trait": ["independent"]},
    )
    assert response.json == ["Free States Rant", "Reckless Agitation"]
    response = client.post(
        "/card",
        json={"type": ["political action"], "trait": ["anarch"]},
    )
    assert response.json == [
        "Anarch Salon",
        "Eat the Rich",
        "Exclusion Principle",
        "Firebrand",
        "Free States Rant",
        "Patsy",
        "Persona Non Grata",
        "Reckless Agitation",
        "Revolutionary Council",
        "Sweeper",
    ]
    # multi-disciplines
    response = client.post(
        "/card",
        json={"discipline": ["*", "animalism"], "bonus": ["intercept"]},
    )
    assert response.json == [
        "Detect Authority",
        "Falcon's Eye",
        "Read the Winds",
        "Speak with Spirits",
        "The Mole",
    ]
    # superior disciplines (vampires only)
    response = client.post("/card", json={"discipline": ["OBEAH"], "group": ["2"]})
    assert response.json == ["Blanche Hill", "Matthias"]
    # clans abbreviations
    response = client.post("/card", json={"clan": ["trujah"], "group": ["2"]})
    assert response.json == ["Krassimir", "Nu, The Pillar", "Synesios"]
    # Gwen Brand special case, disciplines abbreviations
    response = client.post(
        "/card",
        json={
            "clan": ["ravnos"],
            "group": ["5"],
            "discipline": ["AUS", "CHI", "FOR", "ANI"],
        },
    )
    assert response.json == ["Gwen Brand"]


def test_submit_ruling(client, monkeypatch):
    class SessionMock:
        called = False

        @classmethod
        def post(cls, *args, **kwargs):
            cls.called = True
            cls.args = args
            cls.kwargs = kwargs
            cls.ok = True
            cls.status_code = 201
            return cls

        @classmethod
        def json(cls):
            return {"response": "ok"}

    monkeypatch.setattr(requests, "session", lambda: SessionMock)
    response = client.post(
        "/submit-ruling/Arson", json={"text": "foo", "link": "http://example.com"}
    )
    assert response.status_code == 400
    response = client.post(
        "/submit-ruling/Arson", json={"text": "foo", "link": "http://www.vekn.net"}
    )
    assert response.status_code == 201
    assert response.json == {"response": "ok"}
    assert SessionMock.called
    assert SessionMock.auth == (None, None)
    assert SessionMock.args == (
        "https://api.github.com/repos/lionel-panhaleux/krcg/issues",
        '{"title": "Arson", "body": "- **text:** foo\\n- **link:** '
        'http://www.vekn.net"}',
    )
    assert SessionMock.kwargs == {}
    assert SessionMock.ok
