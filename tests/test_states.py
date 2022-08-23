import textwrap

from krcg import twda
from krcg import vtes


def test_card():
    assert vtes.VTES["Aid from Bats"].to_json() == {
        "_i18n": {
            "es": {
                "card_text": (
                    "[ani] Ataque: 1 de daño a distancia, con 1 maniobra opcional.\n"
                    "[ANI] Como antes, con 1 acoso opcional."
                ),
                "flavor_text": (
                    "Colgando boca abajo como hileras de trapos viejos y repugnantes\n"
                    "Y sonriendo mientras duermen. ¡Murciélagos!\n"
                    'D.H. Lawrence, "Murciélago"'
                ),
                "name": "Ayuda de murciélagos",
                "sets": {"First Blood": "Primera Sangre"},
                "url": "https://static.krcg.org/card/es/aidfrombats.jpg",
            },
            "fr": {
                "card_text": (
                    "[ani] Frapper à toute portée : 1 point de dégâts, "
                    "avec 1 manœuvre optionnelle.\n"
                    "[ANI] Comme ci-dessus, avec 1 poursuite optionnelle."
                ),
                "flavor_text": (
                    "Pendues tête en bas comme des rangées de guenilles repoussantes\n"
                    "Et souriant de toutes leurs dents dans leur sommeil. "
                    "Des chauves-souris !\n"
                    'D.H. Lawrence, "La Chauve-souris"'
                ),
                "name": "Aide des chauves-souris",
                "sets": {"First Blood": "Premier Sang"},
                "url": "https://static.krcg.org/card/fr/aidfrombats.jpg",
            },
        },
        "_name": "Aid from Bats",
        "artists": ["Eric Lofgren", "Melissa Benson"],
        "card_text": (
            "[ani] Strike: 1R damage, with 1 optional maneuver.\n"
            "[ANI] As above, with 1 optional press."
        ),
        "disciplines": ["ani"],
        "flavor_text": (
            "Hanging upside down like rows of disgusting old rags\n"
            "And grinning in their sleep. Bats!\n"
            'D.H. Lawrence, "Bat"'
        ),
        "id": 100029,
        "name": "Aid from Bats",
        "printed_name": "Aid from Bats",
        "sets": {
            "Anarchs": [
                {"copies": 2, "precon": "Gangrel", "release_date": "2003-05-19"}
            ],
            "Camarilla Edition": [
                {"rarity": "Common", "release_date": "2002-08-19"},
                {"copies": 3, "precon": "Nosferatu", "release_date": "2002-08-19"},
            ],
            "First Blood": [
                {"copies": 6, "precon": "Nosferatu", "release_date": "2019-10-01"}
            ],
            "Jyhad": [{"rarity": "Common", "release_date": "1994-08-16"}],
            "Keepers of Tradition": [
                {"rarity": "Common", "release_date": "2008-11-19"}
            ],
            "Third Edition": [{"rarity": "Common", "release_date": "2006-09-04"}],
            "Vampire: The Eternal Struggle": [
                {"rarity": "Common", "release_date": "1995-09-15"}
            ],
        },
        "scans": {
            "Anarchs": "https://static.krcg.org/card/set/anarchs/aidfrombats.jpg",
            "Camarilla Edition": (
                "https://static.krcg.org/card/set/camarilla-edition/aidfrombats.jpg"
            ),
            "First Blood": (
                "https://static.krcg.org/card/set/first-blood/aidfrombats.jpg"
            ),
            "Jyhad": "https://static.krcg.org/card/set/jyhad/aidfrombats.jpg",
            "Keepers of Tradition": (
                "https://static.krcg.org/card/set/keepers-of-tradition/aidfrombats.jpg"
            ),
            "Third Edition": (
                "https://static.krcg.org/card/set/third-edition/aidfrombats.jpg"
            ),
            "Vampire: The Eternal Struggle": (
                "https://static.krcg.org/card/set/"
                "vampire-the-eternal-struggle/aidfrombats.jpg"
            ),
        },
        "types": ["Combat"],
        "rulings": {
            "links": {
                "[TOM 19960521]": (
                    "https://groups.google.com/d/msg/rec.games.trading-cards.jyhad/"
                    "poYD3n0TKGo/xvU5HW7lBxMJ"
                ),
            },
            "text": [
                "[ANI] The press can only be used during the current round. "
                "[TOM 19960521]"
            ],
        },
        "url": "https://static.krcg.org/card/aidfrombats.jpg",
    }


def test_multiple_rulings():
    assert vtes.VTES["Toreador Grand Ball"].to_json() == {
        "_i18n": {
            "es": {
                "card_text": (
                    "Elige a dos Toreadores preparados que controles, pon esta carta "
                    "en juego, y gira a uno de los dos. El Toreador girado no se "
                    "endereza normalmente. Las acciones que no sean de sangrado del "
                    "otro Toreador no se pueden bloquear. Cualquier siervo puede "
                    "quemar esta carta con una acción Ⓓ; los Nosferatu obtienen -1 "
                    "de sigilo en esa acción."
                ),
                "name": "Gran baile Toreador",
                "sets": {"Fifth Edition": "Quinta Edición"},
                "url": "https://static.krcg.org/card/es/toreadorgrandball.jpg",
            },
            "fr": {
                "card_text": (
                    "Choisissez deux Toréadors disponibles que vous contrôlez, "
                    "mettez cette carte en jeu et inclinez un des deux. Le Toréador "
                    "incliné ne se redresse pas normalement. Les actions qui ne "
                    "sont pas des morsures de l'autre Toréador ne peuvent pas être "
                    "bloquées. N'importe quel serviteur peut brûler cette carte en "
                    "action Ⓓ ; les Nosferatus reçoivent -1 en discrétion durant "
                    "cette action."
                ),
                "name": "Grand bal Toréador",
                "sets": {"Fifth Edition": "Cinquième édition"},
                "url": "https://static.krcg.org/card/fr/toreadorgrandball.jpg",
            },
        },
        "_name": "Toreador Grand Ball",
        "artists": ["Jim Di Bartolo", "Richard Kane Ferguson"],
        "card_text": (
            "Choose two ready Toreador you control, put this card in play, "
            "and lock one of the two. The locked Toreador does not unlock as "
            "normal. The other Toreador's non-bleed actions cannot be "
            "blocked. Minions can burn this card as a Ⓓ action; Nosferatu "
            "get -1 stealth during that action."
        ),
        "clans": ["Toreador"],
        "id": 101989,
        "name": "Toreador Grand Ball",
        "printed_name": "Toreador Grand Ball",
        "pool_cost": "1",
        "rulings": {
            "links": {
                "[LSJ 19970814]": (
                    "https://groups.google.com/d/msg/rec.games.trading-cards.jyhad"
                    "/Xd6HOjnqBpw/_wNl-bMoKiAJ"
                ),
                "[LSJ 20050114]": (
                    "https://groups.google.com/d/msg/rec.games.trading-cards.jyhad"
                    "/JWiZmyC2Y6s/q6JHYrE1zKYJ"
                ),
                "[TOM 19960528]": (
                    "https://groups.google.com/d/msg/rec.games.trading-cards.jyhad"
                    "/SNpATL1McBM/yHonNZINkWUJ"
                ),
            },
            "text": [
                (
                    'The same vampire can serve as the "second Toreador" for '
                    "multiple Toreador Grand Balls. [TOM 19960528]"
                ),
                (
                    "The first Toreador chosen for the Toreador Grand Ball "
                    "is unblockable on all non-bleed actions. This remains "
                    "true even after the vampire attempts a bleed. [LSJ 19970814]"
                ),
                (
                    'The "does not unlock as normal" effect is redundant '
                    "with being infernal. If the minion is infernal, his "
                    "controller can still pay a pool to unlock him. [LSJ 20050114]"
                ),
            ],
        },
        "sets": {
            "Camarilla Edition": [{"rarity": "Uncommon", "release_date": "2002-08-19"}],
            "Dark Sovereigns": [{"rarity": "Uncommon", "release_date": "1995-12-15"}],
            "Fifth Edition": [
                {"copies": 4, "precon": "Toreador", "release_date": "2020-11-30"}
            ],
            "Keepers of Tradition": [
                {"rarity": "Uncommon", "release_date": "2008-11-19"}
            ],
            "New Blood": [
                {"copies": 4, "precon": "Toreador", "release_date": "2022-04-17"}
            ],
        },
        "scans": {
            "Camarilla Edition": (
                "https://static.krcg.org/card/set/"
                "camarilla-edition/toreadorgrandball.jpg"
            ),
            "Dark Sovereigns": (
                "https://static.krcg.org/card/set/dark-sovereigns/toreadorgrandball.jpg"
            ),
            "Fifth Edition": (
                "https://static.krcg.org/card/set/fifth-edition/toreadorgrandball.jpg"
            ),
            "Keepers of Tradition": (
                "https://static.krcg.org/card/set/"
                "keepers-of-tradition/toreadorgrandball.jpg"
            ),
            "New Blood": (
                "https://static.krcg.org/card/set/" "new-blood/toreadorgrandball.jpg"
            ),
        },
        "types": ["Master"],
        "url": "https://static.krcg.org/card/toreadorgrandball.jpg",
    }


def test_twda(TWDA):
    deck = TWDA["2020bf3hf"]
    test_twda = twda._TWDA()
    test_twda[deck.id] = deck
    assert test_twda.to_json() == [
        {
            "comments": textwrap.dedent(
                """
Here is a quick report by the Winner of the event Niko Vanhatalo.

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
"""
            )[1:],
            "crypt": {
                "cards": [
                    {"count": 3, "id": 200848, "name": "Lodin (Olaf Holte)"},
                    {"count": 2, "id": 200533, "name": "Graham Gottesman"},
                    {"count": 2, "id": 201438, "name": "Victor Donaldson"},
                    {"count": 1, "id": 201026, "name": "Mustafa, The Heir"},
                    {"count": 1, "id": 200280, "name": "Claus Wegener"},
                    {"count": 1, "id": 200421, "name": "Emily Carson"},
                    {"count": 1, "id": 200691, "name": "Jephta Hester"},
                    {"count": 1, "id": 201403, "name": "Ulrike Rothbart"},
                ],
                "count": 12,
            },
            "date": "2020-09-05",
            "event": "Black Forest Base 3",
            "event_link": "http://www.vekn.net/event-calendar/event/9667",
            "id": "2020bf3hf",
            "library": {
                "cards": [
                    {
                        "cards": [
                            {"count": 1, "id": 100058, "name": "Anarch Troublemaker"},
                            {"count": 1, "id": 100545, "name": "Direct Intervention"},
                            {"count": 1, "id": 100588, "name": "Dreams of the Sphinx"},
                            {"count": 1, "id": 100824, "name": "Giant's Blood"},
                            {
                                "comments": "Neat card, but never played. "
                                "Should propably switch for "
                                "another Dreams or Wash",
                                "count": 1,
                                "id": 100842,
                                "name": "Golconda: Inner Peace",
                            },
                            {"count": 1, "id": 101225, "name": "Misdirection"},
                            {"count": 1, "id": 101350, "name": "Papillon"},
                            {"count": 2, "id": 101384, "name": "Pentex™ Subversion"},
                            {"count": 2, "id": 101388, "name": "Perfectionist"},
                            {"count": 2, "id": 102113, "name": "Vessel"},
                            {"count": 2, "id": 102121, "name": "Villein"},
                            {"count": 1, "id": 102151, "name": "Wash"},
                        ],
                        "count": 16,
                        "type": "Master",
                    },
                    {
                        "cards": [
                            {"count": 1, "id": 100573, "name": "Dominate Kine"},
                            {"count": 2, "id": 100652, "name": "Entrancement"},
                            {"count": 11, "id": 100845, "name": "Govern the Unaligned"},
                        ],
                        "count": 14,
                        "type": "Action",
                    },
                    {
                        "cards": [
                            {"count": 2, "id": 100903, "name": "Heart of Nizchetus"}
                        ],
                        "count": 2,
                        "type": "Equipment",
                    },
                    {
                        "cards": [{"count": 4, "id": 101353, "name": "Parity Shift"}],
                        "count": 4,
                        "type": "Political Action",
                    },
                    {
                        "cards": [
                            {"count": 2, "id": 100236, "name": "Bonding"},
                            {"count": 3, "id": 100401, "name": "Conditioning"},
                            {"count": 3, "id": 100492, "name": "Daring the Dawn"},
                            {"count": 4, "id": 100788, "name": "Freak Drive"},
                            {"count": 5, "id": 101712, "name": "Seduction"},
                            {"count": 2, "id": 101978, "name": "Threats"},
                        ],
                        "count": 19,
                        "type": "Action Modifier",
                    },
                    {
                        "cards": [
                            {"count": 8, "id": 100518, "name": "Deflection"},
                            {"count": 3, "id": 101321, "name": "On the Qui Vive"},
                            {
                                "count": 4,
                                "id": 101706,
                                "name": "Second Tradition: Domain",
                            },
                            {
                                "comments": (
                                    "This should be another On the Qui Vive but I was "
                                    "too lazy to find 1 from my collection"
                                ),
                                "count": 1,
                                "id": 102137,
                                "name": "Wake with Evening's Freshness",
                            },
                        ],
                        "count": 16,
                        "type": "Reaction",
                    },
                    {
                        "cards": [
                            {"count": 5, "id": 100918, "name": "Hidden Strength"},
                            {"count": 6, "id": 100973, "name": "Indomitability"},
                            {
                                "count": 2,
                                "id": 101649,
                                "name": "Rolling with the Punches",
                            },
                            {
                                "count": 4,
                                "id": 102169,
                                "name": "Weighted Walking Stick",
                            },
                        ],
                        "count": 17,
                        "type": "Combat",
                    },
                ],
                "count": 88,
            },
            "name": "My stick is better than bacon",
            "place": "Hyvinkää, Finland",
            "player": "Niko Vanhatalo",
            "players_count": 14,
            "score": "1gw5 + 3vp in the final",
            "tournament_format": "2R+F",
        },
    ]

    read_back = twda._TWDA()
    read_back.from_json(test_twda.to_json())
    assert len(read_back) == 1
