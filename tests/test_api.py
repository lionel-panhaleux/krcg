# import pytest
# import requests

# from krcg import flask


# @pytest.fixture
# def client():
#     app = flask.create_app(test=True)
#     app.config["TESTING"] = True
#     with app.test_client() as client:
#         yield client


# def test_complete(client):
#     response = client.get("/complete")
#     assert response.status_code == 404
#     response = client.get("/complete/NotACard")
#     assert response.status_code == 200
#     assert response.json == []
#     # must match every word, if one word matches nothing, no match
#     response = client.get("/complete/NotACard%20Pentex")
#     assert response.status_code == 200
#     assert response.json == []
#     # same match level, order alphabetically
#     response = client.get("/complete/unn")
#     assert response.status_code == 200
#     assert response.json == ["The unnamed", "Unnatural Disaster"]
#     # first word is a better match
#     response = client.get("/complete/pentex")
#     assert response.status_code == 200
#     assert response.json == [
#         "Pentex™ Loves You!",  # Pentex is first word
#         "Pentex™ Subversion",
#         "Enzo Giovanni, Pentex Board of Directors",  # then alphabetically
#         "Enzo Giovanni, Pentex Board of Directors (ADV)",
#         "Harold Zettler, Pentex Director",
#     ]
#     # for multiple words, all must match
#     response = client.get("/complete/the%20ru")
#     assert response.status_code == 200
#     assert response.json == [
#         "The Rumor Mill, Tabloid Newspaper",
#         "Darvag, The Butcher of Rus",
#     ]
#     # match names with special chars
#     response = client.get("/complete/rot")
#     assert response.status_code == 200
#     assert response.json == ["Rötschreck", "Ulrike Rothbart"]
#     # do not complete translations without accept-language header
#     response = client.get("/complete/Aide%20des")
#     assert response.status_code == 200
#     assert response.json == []


# def test_complete_i18n(client):
#     response = client.get("/complete/Aide%20des", headers=[("accept-language", "fr")])
#     assert response.status_code == 200
#     assert response.json == ["Aide des chauves-souris"]
#     response = client.get("/complete/Ankara", headers=[("accept-language", "fr")])
#     assert response.status_code == 200
#     assert response.json == ["La citadelle d'Ankara, Turquie"]
#     response = client.get("/complete/Ankara", headers=[("accept-language", "es")])
#     assert response.status_code == 200
#     assert response.json == ["La Ciudadela de Ankara, Turquía"]


# def test_card(client):
#     response = client.get("/card/NotACard")
#     assert response.status_code == 404
#     response = client.get("/card/Alastor")
#     assert response.status_code == 200
#     assert response.json == {
#         "Id": "100038",
#         "Name": "Alastor",
#         "Image": "https://images.krcg.org/alastor.jpg",
#         "Type": ["Political Action"],
#         "Burn Option": False,
#         "Card Text": (
#             "Requires a justicar or Inner Circle member.\n"
#             "Choose a ready Camarilla vampire. If this referendum is successful, "
#             "search your library for an equipment card and place this card "
#             "and the equipment on the chosen vampire. "
#             "Pay half the cost (round down) of the equipment. "
#             "This vampire may enter combat with any vampire "
#             "controlled by another Methuselah as a +1 stealth Ⓓ  action. "
#             "This vampire cannot commit diablerie. A vampire may have only one Alastor."
#         ),
#         "Set": {
#             "Gehenna": [{"Rarity": "Rare", "Release Date": "2004-05-17"}],
#             "Keepers of Tradition": [{"Rarity": "Rare", "Release Date": "2008-11-19"}],
#             "Kindred Most Wanted": [
#                 {"Copies": 1, "Precon": "Alastors", "Release Date": "2005-02-21"}
#             ],
#         },
#         "Requirement": ["justicar", "inner circle"],
#         "Artist": "Monte Moore",
#         "Rulings": [
#             "If the given weapon costs blood, "
#             "the target Alastor pays the cost. [LSJ 20040518]",
#             "Requirements do not apply. [ANK 20200901]",
#         ],
#         "Rulings Links": [
#             {
#                 "Reference": "LSJ 20040518",
#                 "URL": "https://groups.google.com/d/msg/rec.games.trading-cards.jyhad/"
#                 "4emymfUPwAM/B2SCC7L6kuMJ",
#             },
#             {
#                 "Reference": "ANK 20200901",
#                 "URL": "http://www.vekn.net/forum/rules-questions/"
#                 "78830-alastor-and-ankara-citadel#100653",
#             },
#         ],
#     }
#     id_response = client.get("/card/100038")
#     assert id_response.status_code == 200
#     assert id_response.json == response.json
#     # slash in names cannot be used
#     response = client.get("/card/Kpist%20m45")
#     assert response.status_code == 200
#     # translated card
#     response = client.get("/card/Aid%20from%20Bats")
#     assert response.status_code == 200
#     assert response.json == {  # noqa: E501
#         "Artist": "Melissa Benson; Eric Lofgren",
#         "Burn Option": False,
#         "Card Text": (
#             "[ani] Strike: 1R damage, with 1 optional maneuver.\n"
#             "[ANI] As above, with 1 optional press."
#         ),
#         "Discipline": ["Animalism"],
#         "Flavor Text": (
#             "Hanging upside down like rows of disgusting old rags\n"
#             "And grinning in their sleep. Bats!\n"
#             'D.H. Lawrence, "Bat"'
#         ),
#         "Id": "100029",
#         "Image": "https://images.krcg.org/aidfrombats.jpg",
#         "Name": "Aid from Bats",
#         "Rulings": [
#             "[ANI] The press can only be used during the current round. [TOM "
#             "19960521]"
#         ],
#         "Rulings Links": [
#             {
#                 "Reference": "TOM 19960521",
#                 "URL": (
#                     "https://groups.google.com/d/msg/rec.games.trading-cards.jyhad/"
#                     "poYD3n0TKGo/xvU5HW7lBxMJ"
#                 ),
#             }
#         ],
#         "Set": {
#             "Anarchs": [
#                 {"Copies": 2, "Precon": "Gangrel", "Release Date": "2003-05-19"}
#             ],
#             "Camarilla Edition": [
#                 {"Rarity": "Common", "Release Date": "2002-08-19"},
#                 {"Copies": 3, "Precon": "Nosferatu", "Release Date": "2002-08-19"},
#             ],
#             "First Blood": [
#                 {"Copies": 6, "Precon": "Nosferatu", "Release Date": "2019-10-01"}
#             ],
#             "Jyhad": [{"Rarity": "Common", "Release Date": "1994-08-16"}],
#             "Keepers of Tradition": [
#                 {"Rarity": "Common", "Release Date": "2008-11-19"}
#             ],
#             "Third Edition": [{"Rarity": "Common", "Release Date": "2006-09-04"}],
#             "Vampire: The Eternal Struggle": [
#                 {"Rarity": "Common", "Release Date": "1995-09-15"}
#             ],
#         },
#         "Translations": {
#             "es": {
#                 "Card Text": (
#                     "[ani] Ataque: 1 de daño a distancia, con 1 maniobra opcional.\n"
#                     "[ANI] Como antes, con 1 acoso opcional."
#                 ),
#                 "Flavor Text": (
#                     "Colgando boca abajo como hileras de trapos viejos y repugnantes\n"
#                     "Y sonriendo mientras duermen. ¡Murciélagos!\n"
#                     'D.H. Lawrence, "Murciélago"'
#                 ),
#                 "Name": "Ayuda de murciélagos",
#                 "Set": {"First Blood": "Primera Sangre"},
#             },
#             "fr": {
#                 "Card Text": (
#                     "[ani] Frapper à toute portée : 1 point de dégâts, "
#                     "avec 1 manœuvre optionnelle.\n"
#                     "[ANI] Comme ci-dessus, avec 1 poursuite optionnelle."
#                 ),
#                 "Flavor Text": (
#                     "Pendues tête en bas comme des rangées de guenilles repoussantes\n"
#                     "Et souriant de toutes leurs dents dans leur sommeil. "
#                     "Des chauves-souris !\n"
#                     'D.H. Lawrence, "La Chauve-souris"'
#                 ),
#                 "Name": "Aide des chauves-souris",
#                 "Set": {"First Blood": "Premier Sang"},
#             },
#         },
#         "Type": ["Combat"],
#     }
#     # fetching by translated name works
#     response = client.get("/card/Aide%20des%20chauves-souris")
#     assert response.status_code == 200
#     # sets serialization (prom, POD, PDF sets, ...)
#     response = client.get("/card/The%20Line")
#     assert response.status_code == 200
#     assert response.json == {  # noqa: E501
#         "Artist": "Carmen Cornet",
#         "Burn Option": False,
#         "Card Text": (
#             "Unique location.\n"
#             "Lock to reduce the cost of an action card played by a vampire "
#             "you control by 1 blood (this location is not locked if that "
#             "card is canceled as it is played). Any vampire can steal this "
#             "location as a Ⓓ  action."
#         ),
#         "Id": "101110",
#         "Image": "https://images.krcg.org/linethe.jpg",
#         "Name": "The Line",
#         "Rulings": [
#             "Can be locked when the action is announced or when the cost is "
#             "paid. [ANK 20170605]",
#             "Can be used to reduce the cost in blood of a recruit ally (eg. "
#             "{Shambling Hordes}) or employ retainer action. [ANK 20181007]",
#             'Cannot be used by an ally acting "as a vampire". [ANK 20200605]',
#         ],
#         "Rulings Links": [
#             {
#                 "Reference": "ANK 20170605",
#                 "URL": (
#                     "http://www.vekn.net/forum/rules-questions/"
#                     "75862-timing-of-the-line#82113"
#                 ),
#             },
#             {
#                 "Reference": "ANK 20181007",
#                 "URL": (
#                     "http://www.vekn.net/forum/rules-questions/"
#                     "77057-quick-question-on-the-line#91020"
#                 ),
#             },
#             {
#                 "Reference": "ANK 20200605",
#                 "URL": (
#                     "http://www.vekn.net/forum/rules-questions/"
#                     "78671-can-an-ally-with-play-as-a-vampire-"
#                     "use-the-line-to-reduce-action-costs#100015"
#                 ),
#             },
#         ],
#         "Set": {
#             "Anthology": [
#                 {
#                     "Copies": 1,
#                     "Precon": "EC Berlin Edition",
#                     "Release Date": "2017-05-11",
#                 }
#             ]
#         },
#         "Type": ["Master"],
#     }
#     # sets serialization (promo, POD, PDF sets, ...)
#     response = client.get("/card/The%20Dracon")
#     assert response.status_code == 200
#     assert response.json == {  # noqa: E501
#         "Adv": False,
#         "Artist": "Ginés Quiñonero",
#         "Capacity": "11",
#         "Card Text": "Independent: Cards requiring Vicissitude [vic] cost The Dracon "
#         "1 fewer blood. He inflicts +1 damage or steals 1 additional "
#         "blood or life with ranged strikes (even at close range). Flight "
#         "[FLIGHT]. +1 bleed. +2 strength.",
#         "Clan": ["Tzimisce"],
#         "Disciplines": ["ANI", "AUS", "POT", "THA", "VIC"],
#         "Group": "5",
#         "Id": "200385",
#         "Image": "https://images.krcg.org/draconthe.jpg",
#         "Name": "The Dracon",
#         "Set": {
#             "2015 Storyline Rewards": [{"Copies": 1, "Release Date": "2015-02-16"}],
#             "2018 Humble Bundle": [
#                 {"Copies": 2, "Precon": "Humble Bundle", "Release Date": "2018-10-04"}
#             ],
#             "2019 Promo Pack 1": [{"Copies": 1, "Release Date": "2019-04-08"}],
#         },
#         "Type": ["Vampire"],
#     }
#     response = client.get("/card/Ophidian%20Gaze")
#     assert response.status_code == 200
#     assert response.json == {  # noqa: E501
#         "Artist": "Ginés Quiñonero",
#         "Burn Option": False,
#         "Card Text": (
#             "[pre][ser] Reduce a bleed against you by 2.\n"
#             "[PRE][SER] Only usable during a political action, after blocks are "
#             "declined. Cancel an action modifier as it is played, and its cost is not "
#             "paid."
#         ),
#         "Discipline": ["Presence", "Serpentis"],
#         "Id": "101325",
#         "Image": "https://images.krcg.org/ophidiangaze.jpg",
#         "Name": "Ophidian Gaze",
#         "Rulings": [
#             "[SER][PRE] Can be used to cancel an action modifier player "
#             '"after the action/referendum is successful" (eg. {Voter '
#             "Captivatoin} or {Freak Drive}). [ANK 20180909]"
#         ],
#         "Rulings Links": [
#             {
#                 "Reference": "ANK 20180909",
#                 "URL": (
#                     "http://www.vekn.net/forum/rules-questions/"
#                     "76987-ophidian-gaze-and-post-referendum-action-modifiers#90501"
#                 ),
#             }
#         ],
#         "Set": {"The Unaligned": [{"Rarity": "Common", "Release Date": "2014-10-04"}]},
#         "Type": ["Reaction"],
#     }
#     response = client.get("/card/Tyler")
#     assert response.status_code == 200
#     assert response.json == {  # noqa: E501
#         "Adv": False,
#         "Artist": "Lawrence Snelly",
#         "Capacity": "9",
#         "Card Text": (
#             "Camarilla primogen: When Tyler diablerizes a vampire, she "
#             "unlocks and gains a blood from the blood bank. Once per turn, "
#             "she may burn a blood to get +1 bleed or an additional vote."
#         ),
#         "Clan": ["Brujah"],
#         "Disciplines": ["dom", "for", "obt", "CEL", "POT", "PRE"],
#         "Group": "3",
#         "Id": "201397",
#         "Image": "https://images.krcg.org/tyler.jpg",
#         "Name": "Tyler",
#         "Set": {
#             "Blood Shadowed Court": [{"Release Date": "2008-04-14"}],
#             "Camarilla Edition": [{"Rarity": "Vampire", "Release Date": "2002-08-19"}],
#         },
#         "Title": "primogen",
#         "Type": ["Vampire"],
#     }
#     response = client.get("/card/Ashur%20Tablets")
#     assert response.status_code == 200
#     assert response.json == {  # noqa: E501
#         "Artist": "Sandra Chang-Adair; Ginés Quiñonero; Sandra Chang-Adair",
#         "Burn Option": False,
#         "Card Text": (
#             "Put this card in play. If you control three copies, remove all "
#             "copies in play (even controlled by other Methuselahs) from the "
#             "game to gain 3 pool and choose up to thirteen library cards "
#             "from your ash heap; move one of the chosen cards to your hand "
#             "and shuffle the others in your library."
#         ),
#         "Id": "100106",
#         "Image": "https://images.krcg.org/ashurtablets.jpg",
#         "Name": "Ashur Tablets",
#         "Rulings": [
#             "Can be played with no card in the ash heap. [PIB 20130119]",
#             "Is played without announcing targets: they are only chosen once "
#             "the third copy get into play. [LSJ 20091030]",
#         ],
#         "Rulings Links": [
#             {
#                 "Reference": "PIB 20130119",
#                 "URL": (
#                     "http://www.vekn.net/forum/rules-questions/"
#                     "44197-ashur-tablets-for-zero#44229"
#                 ),
#             },
#             {
#                 "Reference": "LSJ 20091030",
#                 "URL": (
#                     "https://groups.google.com/g/rec.games.trading-cards.jyhad"
#                     "/c/ZKuCyTayYbc/m/5nMjLpX4DuMJ"
#                 ),
#             },
#         ],
#         "Set": {
#             "Anthology": [{"Copies": 3, "Release Date": "2017-05-11"}],
#             "Keepers of Tradition": [
#                 {"Rarity": "Common", "Release Date": "2008-11-19"}
#             ],
#         },
#         "Type": ["Master"],
#     }


# def test_deck(client, twda):
#     # the test example TWDA contains only 20 decks
#     response = client.post("/deck")
#     assert response.status_code == 200
#     assert len(response.json) == 20
#     # the test TWDA has a single deck with Lodin
#     response = client.post("/deck", json={"cards": ["Lodin (Olaf Holte)"]})
#     assert response.status_code == 200
#     assert len(response.json) == 1
#     response = client.post("/deck", json={"cards": ["Not a Card"]})
#     assert response.status_code == 400
#     response = client.post("/deck", json={"cards": ["Antithesis"]})
#     assert response.status_code == 404
#     response = client.post("/deck", json={"cards": [""]})
#     # test deck parsing and serialization - it has both general and cards comments
#     response = client.get("/deck/2020bf3hf")
#     assert response.json == {
#         "twda_id": "2020bf3hf",
#         "event": "Black Forest Base 3",
#         "place": "Hyvinkää, Finland",
#         "date": "2020-09-05",
#         "name": "My stick is better than bacon",
#         "tournament_format": "2R+F",
#         "players_count": 14,
#         "player": "Niko Vanhatalo",
#         "score": "1gw5 + 3vp in the final",
#         "comments": """Here is a quick report by the Winner of the event Niko Vanhatalo.

# Just your average Ventrue grinder/stickmen with my own personal preferences

# Finals were pretty brutal because every deck was a bleeder in some way or the
# other and there was no clear winner even when it was down to 2 players.
# Players from 1 to 5 were Petri with Anarch stealth bleeder, Jyrkkä with
# Lasombra/Kiasyd stealth bleeder, Pauli with Ventrue grinder, me with my own
# Ventrue grinder and Lasse with Legion and Legionnaire bleeder.  My biggest
# concern was my predator who played pretty much the same deck with like 90% of
# the crypt being the same cards, but we were able to avoid unnecesary contesting
# thanks to table talk. He still contested my Lodin later in the game but was
# ousted pretty fast after that before any real damage to me was done.
# """,
#         "crypt": {
#             "cards": [
#                 {"count": 3, "id": "200848", "name": "Lodin (Olaf Holte)"},
#                 {"count": 2, "id": "200533", "name": "Graham Gottesman"},
#                 {"count": 2, "id": "201438", "name": "Victor Donaldson"},
#                 {"count": 1, "id": "201026", "name": "Mustafa, The Heir"},
#                 {"count": 1, "id": "200280", "name": "Claus Wegener"},
#                 {"count": 1, "id": "200421", "name": "Emily Carson"},
#                 {"count": 1, "id": "200691", "name": "Jephta Hester"},
#                 {"count": 1, "id": "201403", "name": "Ulrike Rothbart"},
#             ],
#             "count": 12,
#         },
#         "library": {
#             "cards": [
#                 {
#                     "cards": [
#                         {"count": 1, "id": "100058", "name": "Anarch Troublemaker"},
#                         {"count": 1, "id": "100545", "name": "Direct Intervention"},
#                         {"count": 1, "id": "100588", "name": "Dreams of the Sphinx"},
#                         {"count": 1, "id": "100824", "name": "Giant's Blood"},
#                         {
#                             "comments": "Neat card, but never played. "
#                             "Should propably switch for another Dreams or Wash",
#                             "count": 1,
#                             "id": "100842",
#                             "name": "Golconda: Inner Peace",
#                         },
#                         {"count": 1, "id": "101225", "name": "Misdirection"},
#                         {"count": 1, "id": "101350", "name": "Papillon"},
#                         {"count": 2, "id": "101384", "name": "Pentex™ Subversion"},
#                         {"count": 2, "id": "101388", "name": "Perfectionist"},
#                         {"count": 2, "id": "102113", "name": "Vessel"},
#                         {"count": 2, "id": "102121", "name": "Villein"},
#                         {"count": 1, "id": "102151", "name": "Wash"},
#                     ],
#                     "count": 16,
#                     "type": "Master",
#                 },
#                 {
#                     "cards": [
#                         {"count": 1, "id": "100573", "name": "Dominate Kine"},
#                         {"count": 2, "id": "100652", "name": "Entrancement"},
#                         {"count": 11, "id": "100845", "name": "Govern the Unaligned"},
#                     ],
#                     "count": 14,
#                     "type": "Action",
#                 },
#                 {
#                     "cards": [
#                         {"count": 2, "id": "100903", "name": "Heart of Nizchetus"}
#                     ],
#                     "count": 2,
#                     "type": "Equipment",
#                 },
#                 {
#                     "cards": [{"count": 4, "id": "101353", "name": "Parity Shift"}],
#                     "count": 4,
#                     "type": "Political Action",
#                 },
#                 {
#                     "cards": [
#                         {"count": 2, "id": "100236", "name": "Bonding"},
#                         {"count": 3, "id": "100401", "name": "Conditioning"},
#                         {"count": 3, "id": "100492", "name": "Daring the Dawn"},
#                         {"count": 4, "id": "100788", "name": "Freak Drive"},
#                         {"count": 5, "id": "101712", "name": "Seduction"},
#                         {"count": 2, "id": "101978", "name": "Threats"},
#                     ],
#                     "count": 19,
#                     "type": "Action Modifier",
#                 },
#                 {
#                     "cards": [
#                         {"count": 8, "id": "100518", "name": "Deflection"},
#                         {"count": 3, "id": "101321", "name": "On the Qui Vive"},
#                         {
#                             "count": 4,
#                             "id": "101706",
#                             "name": "Second Tradition: Domain",
#                         },
#                         {
#                             "comments": "This should be another On the Qui Vive "
#                             "but I was too lazy to find 1 from my collection",
#                             "count": 1,
#                             "id": "102137",
#                             "name": "Wake with Evening's Freshness",
#                         },
#                     ],
#                     "count": 16,
#                     "type": "Reaction",
#                 },
#                 {
#                     "cards": [
#                         {"count": 5, "id": "100918", "name": "Hidden Strength"},
#                         {"count": 6, "id": "100973", "name": "Indomitability"},
#                         {
#                             "count": 2,
#                             "id": "101649",
#                             "name": "Rolling with the Punches",
#                         },
#                         {"count": 4, "id": "102169", "name": "Weighted Walking Stick"},
#                     ],
#                     "count": 17,
#                     "type": "Combat",
#                 },
#             ],
#             "count": 88,
#         },
#     }


# def test_search(client):
#     response = client.post("/card")
#     assert response.status_code == 200
#     assert len(response.json) == 3788
#     # non-existing filters have no impact
#     response = client.post("/card", json={"foo": ["bar"]})
#     assert response.status_code == 200
#     assert len(response.json) == 3788
#     # non-existing values do not crash
#     response = client.post("/card", json={"bonus": ["foo"]})
#     assert response.status_code == 200
#     assert len(response.json) == 0
#     response = client.post("/card", json={"trait": ["foo"]})
#     assert response.status_code == 200
#     assert len(response.json) == 0
#     # card text
#     response = client.post(
#         "/card", json={"text": "this equipment card represents a location"}
#     )
#     assert response.json == [
#         "Catacombs",
#         "Dartmoor, England",
#         "Inveraray, Scotland",
#         "Living Manse",
#         "Local 1111",
#         "Lyndhurst Estate, New York",
#         "Palatial Estate",
#         "Pier 13, Port of Baltimore",
#         "Ruins of Ceoris",
#         "Ruins of Villers Abbey, Belgium",
#         "Sacré-Cœur Cathedral, France",
#         "San Lorenzo de El Escorial, Spain",
#         "San Nicolás de los Servitas",
#         "The Ankara Citadel, Turkey",
#         "Winchester Mansion",
#         "Zaire River Ferry",
#     ]
#     # discipline, title
#     response = client.post(
#         "/card", json={"trait": ["primogen"], "discipline": ["serpentis"]}
#     )
#     assert response.json == ["Amenophobis"]
#     # city title
#     response = client.post("/card", json={"trait": ["chicago"]})
#     assert response.json == [
#         "Antón de Concepción",
#         "Crusade: Chicago",
#         "Lachlan, Noddist",
#         "Lodin (Olaf Holte)",
#         "Maldavis (ADV)",
#         "Praxis Seizure: Chicago",
#         "Sir Walter Nash",
#     ]
#     # stealth, votes
#     response = client.post("/card", json={"bonus": ["stealth", "votes"]})
#     assert response.json == [
#         "Antonio Veradas",
#         "Bulscu (ADV)",
#         "Dark Selina",
#         "Jessica (ADV)",
#         "Joseph Cambridge",
#         "Karen Suadela",
#         "Loki's Gift",
#         "Maxwell",
#         "Natasha Volfchek",
#         "Perfect Paragon",
#         "Sela (ADV)",
#         "Suhailah",
#         "Zayyat, The Sandstorm",
#     ]

#     # votes provided by master cards
#     response = client.post(
#         "/card",
#         json={"bonus": ["votes"], "clan": ["Assamite"], "type": ["Master"]},
#     )
#     assert response.json == ["Alamut", "The Black Throne"]
#     # votes provided by titles
#     response = client.post(
#         "/card",
#         json={"bonus": ["votes"], "clan": ["Assamite"], "group": ["3"]},
#     )
#     assert response.json == ["Enam", "Rebekah"]
#     # title when MERGED
#     response = client.post("/card", json={"clan": ["Assamite"], "trait": ["justicar"]})
#     assert response.json == ["Tegyrius, Vizier (ADV)"]
#     # traits: black hand, red list ...
#     response = client.post(
#         "/card",
#         json={"clan": ["Nagaraja"], "trait": ["black hand"]},
#     )
#     assert response.json == ["Sennadurek"]
#     # return full card info
#     response = client.post(
#         "/card",
#         json={"clan": ["Nagaraja"], "trait": ["black hand"], "mode": "full"},
#     )
#     assert response.json == [
#         {
#             "Adv": False,
#             "Artist": "Andrew Trabbold",
#             "Capacity": "6",
#             "Card Text": (
#                 "Sabbat. Black Hand: Whenever a Methuselah loses the Edge when "
#                 "it is not your turn, Sennadurek unlocks, and you may look at "
#                 "that Methuselah's hand. Scarce."
#             ),
#             "Clan": ["Nagaraja"],
#             "Disciplines": ["dom", "AUS", "NEC"],
#             "Group": "4",
#             "Id": "201263",
#             "Image": "https://images.krcg.org/sennadurek.jpg",
#             "Name": "Sennadurek",
#             "Rulings": [
#                 "Black Hand is not a title, it is a trait unrelated to any sect. "
#                 "The trait is not lost if the vampire changes sect. [LSJ "
#                 "20070322] [ANK 20180807]"
#             ],
#             "Rulings Links": [
#                 {
#                     "Reference": "LSJ 20070322",
#                     "URL": (
#                         "https://groups.google.com/d/msg/rec.games.trading-cards.jyhad/"
#                         "Ww-4rYJxi4w/P3QchWVq2o4J"
#                     ),
#                 },
#                 {
#                     "Reference": "ANK 20180807",
#                     "URL": (
#                         "http://www.vekn.net/forum/rules-questions/"
#                         "76905-going-anarch-as-black-hand#89735"
#                     ),
#                 },
#             ],
#             "Set": {
#                 "Legacies of Blood": [
#                     {"Rarity": "Uncommon", "Release Date": "2005-11-14"}
#                 ]
#             },
#             "Type": ["Vampire"],
#         }
#     ]
#     response = client.post("/card", json={"clan": ["Assamite"], "trait": ["red list"]})
#     assert response.json == ["Jamal", "Tariq, The Silent (ADV)"]
#     # sect
#     response = client.post(
#         "/card",
#         json={"clan": ["assamite"], "trait": ["camarilla"], "group": ["2"]},
#     )
#     assert response.json == [
#         "Al-Ashrad, Amr of Alamut (ADV)",
#         "Tegyrius, Vizier",
#         "Tegyrius, Vizier (ADV)",
#     ]
#     # traits on library cards
#     response = client.post(
#         "/card",
#         json={"type": ["action modifier"], "trait": ["black hand"]},
#     )
#     assert response.json == [
#         "Circumspect Revelation",
#         "Seraph's Second",
#         "The Art of Memory",
#     ]
#     # required title
#     response = client.post("/card", json={"type": ["reaction"], "trait": ["justicar"]})
#     assert response.json == ["Legacy of Power", "Second Tradition: Domain"]
#     # "Requires titled Sabbat/Camarilla" maps to all possible titles
#     response = client.post(
#         "/card",
#         json={"bonus": ["intercept"], "trait": ["archbishop"]},
#     )
#     assert response.json == [
#         "Matteus, Flesh Sculptor",
#         "National Guard Support",
#         "Persona Non Grata",
#         "Under Siege",
#     ]
#     # Reducing intercept is stealth
#     response = client.post(
#         "/card",
#         json={"bonus": ["stealth"], "discipline": ["chimerstry"], "type": ["library"]},
#     )
#     assert response.json == [
#         "Fata Morgana",
#         "Mirror's Visage",
#         "Smoke and Mirrors",
#         "Will-o'-the-Wisp",
#     ]
#     # Reducing stealth is intercept
#     response = client.post(
#         "/card",
#         json={
#             "bonus": ["intercept"],
#             "discipline": ["chimerstry"],
#             "type": ["library"],
#         },
#     )
#     assert response.json == [
#         "Draba",
#         "Ignis Fatuus",
#         # multi-disc are tricky: it has chi, it has intercept.
#         # chi doesn't provide intercept, but it matches - fair enough
#         "Netwar",
#         "Veiled Sight",
#     ]
#     # no discipline (crypt)
#     response = client.post("/card", json={"discipline": ["none"], "type": ["crypt"]})
#     assert response.json == ["Anarch Convert", "Sandra White", "Smudge the Ignored"]
#     response = client.post(
#         "/card",
#         json={"discipline": ["none"], "bonus": ["intercept"], "trait": ["sabbat"]},
#     )
#     # no discipline, sect (or independent) required
#     assert response.json == ["Abbot", "Harzomatuili", "Under Siege"]
#     response = client.post(
#         "/card",
#         json={"type": ["political action"], "trait": ["independent"]},
#     )
#     assert response.json == ["Free States Rant", "Reckless Agitation"]
#     response = client.post(
#         "/card",
#         json={"type": ["political action"], "trait": ["anarch"]},
#     )
#     assert response.json == [
#         "Anarch Salon",
#         "Eat the Rich",
#         "Exclusion Principle",
#         "Firebrand",
#         "Free States Rant",
#         "Patsy",
#         "Persona Non Grata",
#         "Reckless Agitation",
#         "Revolutionary Council",
#         "Sweeper",
#     ]
#     # multi-disciplines
#     response = client.post(
#         "/card",
#         json={"discipline": ["*", "animalism"], "bonus": ["intercept"]},
#     )
#     assert response.json == [
#         "Detect Authority",
#         "Falcon's Eye",
#         "Read the Winds",
#         "Speak with Spirits",
#         "The Mole",
#     ]
#     # superior disciplines (vampires only)
#     response = client.post("/card", json={"discipline": ["OBEAH"], "group": ["2"]})
#     assert response.json == ["Blanche Hill", "Matthias"]
#     # clans abbreviations
#     response = client.post("/card", json={"clan": ["trujah"], "group": ["2"]})
#     assert response.json == ["Krassimir", "Nu, The Pillar", "Synesios"]
#     # Gwen Brand special case, disciplines abbreviations
#     response = client.post(
#         "/card",
#         json={
#             "clan": ["ravnos"],
#             "group": ["5"],
#             "discipline": ["AUS", "CHI", "FOR", "ANI"],
#         },
#     )
#     assert response.json == ["Gwen Brand"]
#     # i18n - still always perform text search in english
#     response = client.post(
#         "/card",
#         json={"text": "this equipment card represents a location", "lang": "fr"},
#     )
#     assert response.json == [
#         "Catacombs",
#         "Dartmoor, England",
#         "Inveraray, Scotland",
#         "Living Manse",
#         "Local 1111",
#         "Lyndhurst Estate, New York",
#         "Palatial Estate",
#         "Pier 13, Port of Baltimore",
#         "Ruins of Ceoris",
#         "Ruins of Villers Abbey, Belgium",
#         "Sacré-Cœur Cathedral, France",
#         "San Lorenzo de El Escorial, Spain",
#         "San Nicolás de los Servitas",
#         "The Ankara Citadel, Turkey",
#         "Winchester Mansion",
#         "Zaire River Ferry",
#     ]
#     # text also matches card name
#     response = client.post(
#         "/card",
#         json={"text": "Ankara"},
#     )
#     assert response.json == ["The Ankara Citadel, Turkey"]
#     # i18n - but match the given language in addition to it
#     response = client.post(
#         "/card",
#         json={"text": "cette carte d'équipement représente un lieu", "lang": "fr"},
#     )
#     assert response.json == ["Living Manse", "The Ankara Citadel, Turkey"]
#     # i18n - should work with regions too, whatever their case
#     response = client.post(
#         "/card",
#         json={"text": "cette carte d'équipement représente un lieu", "lang": "fr-fr"},
#     )
#     assert response.json == ["Living Manse", "The Ankara Citadel, Turkey"]
#     # i18n - should work with regions too, whatever their case
#     response = client.post(
#         "/card",
#         json={"text": "cette carte d'équipement représente un lieu", "lang": "fr_FR"},
#     )
#     assert response.json == ["Living Manse", "The Ankara Citadel, Turkey"]
#     # i18n - do not match unrelated translations
#     response = client.post(
#         "/card", json={"text": "esta carta de equipo representa un lugar", "lang": "fr"}
#     )
#     assert response.json == []
#     response = client.post(
#         "/card", json={"text": "esta carta de equipo representa un lugar", "lang": "es"}
#     )
#     assert response.json == ["Living Manse", "The Ankara Citadel, Turkey"]


# def test_submit_ruling(client, monkeypatch):
#     class SessionMock:
#         called = False

#         @classmethod
#         def post(cls, *args, **kwargs):
#             cls.called = True
#             cls.args = args
#             cls.kwargs = kwargs
#             cls.ok = True
#             cls.status_code = 201
#             return cls

#         @classmethod
#         def json(cls):
#             return {"response": "ok"}

#     monkeypatch.setattr(requests, "session", lambda: SessionMock)
#     response = client.post(
#         "/submit-ruling/Arson", json={"text": "foo", "link": "http://example.com"}
#     )
#     assert response.status_code == 400
#     response = client.post(
#         "/submit-ruling/Arson", json={"text": "foo", "link": "http://www.vekn.net"}
#     )
#     assert response.status_code == 201
#     assert response.json == {"response": "ok"}
#     assert SessionMock.called
#     assert SessionMock.auth == (None, None)
#     assert SessionMock.args == (
#         "https://api.github.com/repos/lionel-panhaleux/krcg/issues",
#         '{"title": "Arson", "body": "- **text:** foo\\n- **link:** '
#         'http://www.vekn.net"}',
#     )
#     assert SessionMock.kwargs == {}
#     assert SessionMock.ok
