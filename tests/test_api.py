import pytest
import requests

from krcg import flask


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


def test_deck(client, twda):
    # the test example TWDA contains only 20 decks
    response = client.post("/deck")
    assert response.status_code == 200
    assert len(response.json) == 20
    # the test TWDA has a single deck with Lodin
    response = client.post("/deck", json={"cards": ["Lodin (Olaf Holte)"]})
    assert response.status_code == 200
    assert len(response.json) == 1
    response = client.post("/deck", json={"cards": ["Not a Card"]})
    assert response.status_code == 400
    response = client.post("/deck", json={"cards": ["Antithesis"]})
    assert response.status_code == 404
    response = client.post("/deck", json={"cards": [""]})
    # test deck parsing and serialization - it has both general and cards comments
    response = client.get("/deck/2020bf3hf")
    assert response.json == {
        "twda_id": "2020bf3hf",
        "event": "Black Forest Base 3",
        "place": "Hyvinkää, Finland",
        "date": "2020-09-05",
        "name": "My stick is better than bacon",
        "tournament_format": "2R+F",
        "players_count": 14,
        "player": "Niko Vanhatalo",
        "score": "1gw5 + 3vp in the final",
        "comments": """Here is a quick report by the Winner of the event Niko Vanhatalo.

Just your average Ventrue grinder/stickmen with my own personal preferences

Finals were pretty brutal because every deck was a bleeder in some way or the
other and there was no clear winner even when it was down to 2 players.
Players from 1 to 5 were Petri with Anarch stealth bleeder, Jyrkkä with
Lasombra/Kiasyd stealth bleeder, Pauli with Ventrue grinder, me with my own
Ventrue grinder and Lasse with Legion and Legionnaire bleeder.  My biggest
concern was my predator who played pretty much the same deck with like 90% of
the crypt being the same cards, but we were able to avoid unnecesary contesting
thanks to table talk. He still contested my Lodin later in the game but was
ousted pretty fast after that before any real damage to me was done.
""",
        "crypt": {
            "cards": [
                {"count": 3, "id": "200848", "name": "Lodin (Olaf Holte)"},
                {"count": 2, "id": "200533", "name": "Graham Gottesman"},
                {"count": 2, "id": "201438", "name": "Victor Donaldson"},
                {"count": 1, "id": "201026", "name": "Mustafa, The Heir"},
                {"count": 1, "id": "200280", "name": "Claus Wegener"},
                {"count": 1, "id": "200421", "name": "Emily Carson"},
                {"count": 1, "id": "200691", "name": "Jephta Hester"},
                {"count": 1, "id": "201403", "name": "Ulrike Rothbart"},
            ],
            "count": 12,
        },
        "library": {
            "cards": [
                {
                    "cards": [
                        {"count": 1, "id": "100058", "name": "Anarch Troublemaker"},
                        {"count": 1, "id": "100545", "name": "Direct Intervention"},
                        {"count": 1, "id": "100588", "name": "Dreams of the Sphinx"},
                        {"count": 1, "id": "100824", "name": "Giant's Blood"},
                        {
                            "comments": "Neat card, but never played. "
                            "Should propably switch for another Dreams or Wash",
                            "count": 1,
                            "id": "100842",
                            "name": "Golconda: Inner Peace",
                        },
                        {"count": 1, "id": "101225", "name": "Misdirection"},
                        {"count": 1, "id": "101350", "name": "Papillon"},
                        {"count": 2, "id": "101384", "name": "Pentex™ Subversion"},
                        {"count": 2, "id": "101388", "name": "Perfectionist"},
                        {"count": 2, "id": "102113", "name": "Vessel"},
                        {"count": 2, "id": "102121", "name": "Villein"},
                        {"count": 1, "id": "102151", "name": "Wash"},
                    ],
                    "count": 16,
                    "type": "Master",
                },
                {
                    "cards": [
                        {"count": 1, "id": "100573", "name": "Dominate Kine"},
                        {"count": 2, "id": "100652", "name": "Entrancement"},
                        {"count": 11, "id": "100845", "name": "Govern the Unaligned"},
                    ],
                    "count": 14,
                    "type": "Action",
                },
                {
                    "cards": [
                        {"count": 2, "id": "100903", "name": "Heart of Nizchetus"}
                    ],
                    "count": 2,
                    "type": "Equipment",
                },
                {
                    "cards": [{"count": 4, "id": "101353", "name": "Parity Shift"}],
                    "count": 4,
                    "type": "Political Action",
                },
                {
                    "cards": [
                        {"count": 2, "id": "100236", "name": "Bonding"},
                        {"count": 3, "id": "100401", "name": "Conditioning"},
                        {"count": 3, "id": "100492", "name": "Daring the Dawn"},
                        {"count": 4, "id": "100788", "name": "Freak Drive"},
                        {"count": 5, "id": "101712", "name": "Seduction"},
                        {"count": 2, "id": "101978", "name": "Threats"},
                    ],
                    "count": 19,
                    "type": "Action Modifier",
                },
                {
                    "cards": [
                        {"count": 8, "id": "100518", "name": "Deflection"},
                        {"count": 3, "id": "101321", "name": "On the Qui Vive"},
                        {
                            "count": 4,
                            "id": "101706",
                            "name": "Second Tradition: Domain",
                        },
                        {
                            "comments": "This should be another On the Qui Vive "
                            "but I was too lazy to find 1 from my collection",
                            "count": 1,
                            "id": "102137",
                            "name": "Wake with Evening's Freshness",
                        },
                    ],
                    "count": 16,
                    "type": "Reaction",
                },
                {
                    "cards": [
                        {"count": 5, "id": "100918", "name": "Hidden Strength"},
                        {"count": 6, "id": "100973", "name": "Indomitability"},
                        {
                            "count": 2,
                            "id": "101649",
                            "name": "Rolling with the Punches",
                        },
                        {"count": 4, "id": "102169", "name": "Weighted Walking Stick"},
                    ],
                    "count": 17,
                    "type": "Combat",
                },
            ],
            "count": 88,
        },
    }


def test_search(client):
    response = client.post("/card")
    assert response.status_code == 200
    assert len(response.json) == 3788
    # non-existing filters have no impact
    response = client.post("/card", json={"foo": ["bar"]})
    assert response.status_code == 200
    assert len(response.json) == 3788
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
