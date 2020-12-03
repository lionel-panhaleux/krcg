"""Test the parsing of hand-picked examples from the TWDA.
"""
import collections
import logging
import os.path
import textwrap

from krcg import twda


def test_2019grdojf(caplog):
    """Recent classic layout, we must get everything seamlessly"""
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2019grdojf.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2019grdojf"].__getstate__() == {
        "id": "2019grdojf",
        "date": "2019-06-29",
        "event": "Garou Rim: Dawn Operation",
        "event_link": "http://www.vekn.net/event-calendar/event/9292",
        "place": "Joensuu, Finland",
        "players_count": 10,
        "player": "Esa-Matti Smolander",
        "tournament_format": "3R+F",
        "score": "1gw3.5 + 4vp in the final",
        "name": "Parliament of Shadows precon with no changes.",
        "author": None,
        "raven": 0,
        "cards": collections.OrderedDict(
            [
                ("Luca Italicus", 2),
                ("Antón de Concepción", 2),
                ("Carolina Vález", 2),
                ("Charles Delmare", 2),
                ("Lord Leopold Valdemar", 2),
                ("Percival", 2),
                ("Information Highway", 1),
                ("Jake Washington", 1),
                ("Monastery of Shadows", 1),
                ("Papillon", 1),
                ("Political Hunting Ground", 1),
                ("Power Structure", 1),
                ("Powerbase: Madrid", 1),
                ("Villein", 4),
                ("Zillah's Valley", 2),
                ("Govern the Unaligned", 6),
                ("Under Siege", 2),
                ("Mylan Horseed", 1),
                ("Anarchist Uprising", 1),
                ("Ancient Influence", 1),
                ("Banishment", 2),
                ("Kine Resources Contested", 8),
                ("Neonate Breach", 1),
                ("Political Stranglehold", 1),
                ("Reins of Power", 1),
                ("Blanket of Night", 2),
                ("Conditioning", 4),
                ("Seduction", 4),
                ("Shadow Play", 4),
                ("Shroud of Absence", 4),
                ("Shroud of Night", 4),
                ("Tenebrous Form", 2),
                ("Deflection", 4),
                ("Obedience", 2),
                ("On the Qui Vive", 2),
                ("Wake with Evening's Freshness", 2),
                ("Oubliette", 3),
                ("Shadow Body", 3),
            ]
        ),
        "cards_comments": {},
        "comments": "Finals Seating\n\n"
        "Esa-Matti Smolander (Lasombra Starter) --> Petrus Makkonen (Epikasta TGB) "
        "--> Simo Tiippana (Lydia + Al-Muntathir Trujah Toolbox) --> Aapo Järvelin "
        "(Theo + Beast anarch Rush) --> Petro Hirvonen (Hektor Toolbox)\n",
    }
    assert caplog.record_tuples == []


def test_2016ggs(caplog):
    """Pretty straightforward, we must get everything seamlessly"""
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2016ggs.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2016ggs"].__getstate__() == {
        "id": "2016ggs",
        "event": "Gothcon",
        "event_link": None,
        "place": "Goteborg, Sweden",
        "date": "2016-03-26",
        "players_count": 16,
        "player": "Hugh Angseesing",
        "tournament_format": "3R+F",
        "score": None,
        "name": "DoC Swedish Sirens",
        "author": None,
        "raven": 0,
        "cards": collections.OrderedDict(
            [
                ("Jost Werner", 2),
                ("Sheila Mezarin", 2),
                ("Angela Preston", 2),
                ("Gaël Pilet", 1),
                ("Yseult", 1),
                ("Delilah Monroe", 1),
                ("Maldavis", 1),
                ("Remilliard, Devout Crusader", 1),
                ("Céleste, The Voice of a Secret", 1),
                ("Anarch Troublemaker", 3),
                ("Archon Investigation", 1),
                ("Blood Doll", 2),
                ("The Coven", 1),
                ("Direct Intervention", 1),
                ("Dreams of the Sphinx", 1),
                ("Fetish Club Hunting Ground", 1),
                ("Giant's Blood", 1),
                ("Palla Grande", 1),
                ("Paris Opera House", 1),
                ("Pentex™ Subversion", 1),
                ("Presence", 2),
                ("Vessel", 3),
                ("Entrancement", 4),
                ("Legal Manipulations", 4),
                ("Mind Numb", 2),
                ("Social Charm", 3),
                ("Aire of Elation", 6),
                ("Daring the Dawn", 2),
                ("The Missing Voice", 4),
                ("Phantom Speaker", 2),
                ("Siren's Lure", 7),
                ("Delaying Tactics", 3),
                ("My Enemy's Enemy", 2),
                ("On the Qui Vive", 2),
                ("Telepathic Misdirection", 8),
                ("Wake with Evening's Freshness", 5),
                ("Majesty", 8),
                ("Soak", 6),
                ("The Uncoiling", 1),
            ]
        ),
        "cards_comments": {},
        "comments": (
            "Description: 2GW9 and winner in Sweden qualifier 26th March 2016\n"
        ),
    }
    assert caplog.record_tuples == []


def test_2k5alboraya(caplog):
    """Card name abbreviation (fetish club) with tailing point."""
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k5alboraya.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2k5alboraya"].__getstate__() == {
        "id": "2k5alboraya",
        "event": "Spanish NCQ",
        "event_link": None,
        "place": "Alboraya (Valencia), Spain",
        "date": "2005-02-12",
        "players_count": 34,
        "player": "Jose Vicente Coll",
        "tournament_format": "3R+F",
        "score": None,
        "name": None,
        "author": None,
        "raven": 0,
        "cards": collections.OrderedDict(
            [
                ("Jost Werner", 3),
                ("Le Dinh Tho", 2),
                ("Greta Kircher", 1),
                ("Ian Wallingford", 1),
                ("Sheila Mezarin", 1),
                ("Creamy Jade", 1),
                ("Mercy, Knight Inquisitor", 1),
                ("Remilliard, Devout Crusader", 1),
                ("Lolita", 1),
                ("Nicholas Chang", 1),
                ("Palla Grande", 4),
                ("Direct Intervention", 3),
                ("Blood Doll", 3),
                ("Pentex™ Subversion", 2),
                ("Anarch Troublemaker", 2),
                ("The Hungry Coyote", 1),
                ("Fetish Club Hunting Ground", 1),  # should be found
                ("Sudden Reversal", 1),
                ("Creepshow Casino", 1),
                ("The Coven", 1),
                ("Art Scam", 8),
                ("The Embrace", 8),
                ("Mind Numb", 4),
                ("Enchant Kindred", 4),
                ("Entrancement", 2),
                ("Marijava Ghoul", 2),
                ("Revelations", 2),
                ("Owl Companion", 1),
                ("Change of Target", 8),
                ("Wake with Evening's Freshness", 5),
                ("Delaying Tactics", 1),
                ("Telepathic Misdirection", 7),
                ("Telepathic Counter", 2),
                ("My Enemy's Enemy", 3),
                ("Eagle's Sight", 2),
                ("Enhanced Senses", 2),
                ("Majesty", 7),
                ("Staredown", 3),
            ]
        ),
        "cards_comments": {},
        "comments": "",
    }
    assert caplog.record_tuples == []


def test_2k4dcqualifier(caplog):
    """A lot of comments (description, end) plus inline C-style card comment"""
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k4dcqualifier.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2k4dcqualifier"].__getstate__() == {
        "id": "2k4dcqualifier",
        "event": "Atlantic Regional Qualifier",
        "event_link": None,
        "place": "Washington, D.C.",
        "date": "2004-06-12",
        "players_count": 33,
        "player": "Matt Morgan",
        "tournament_format": None,
        "score": None,
        "name": "Call me Julio",
        "author": None,
        "raven": 0,
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
        "cards_comments": {
            "Dominate": textwrap.dedent(
                """
    Didn't really use them, but they were supposed to justify the crypt
    spread.  If there's no Julio, a Tarbaby or Cailean and a Dominate master
    is nearly as good, right?"""
            )[1:],
            "Blood Doll": "Not enough unless you're lucky (like I was).",
            "Govern the Unaligned": "Almost always played superior.",
            "Conditioning": ("Because Colin said it was a good idea (he's right)."),
            "Information Network": "Played it, but never tapped it.",
            "Nosferatu Kingdom": (
                "Absolutely essential.  Always got one after the other, though."
            ),
            "Wake with Evening's Freshness": (
                "Replace one with Mylan Horseed as soon as Gehenna is legal."
            ),
        },
        "cards": collections.OrderedDict(
            [
                ("Julio Martinez", 3),
                ("Tarbaby Jack", 2),
                ("Cailean", 1),
                ("Mateusz Gryzbowsky", 1),
                ("Beast, The Leatherface of Detroit", 1),
                ("Ox, Viceroy of the Hollows", 1),
                ("Nigel the Shunned", 1),
                ("Olivia", 1),
                ("Agatha", 1),
                ("Blood Doll", 4),
                ("Dominate", 2),
                ("Dreams of the Sphinx", 1),
                ("Fame", 2),
                ("Information Network", 1),
                ("Nosferatu Kingdom", 2),
                ("Shanty Town Hunting Ground", 1),
                ("Bum's Rush", 6),
                ("Govern the Unaligned", 6),
                ("Conditioning", 4),
                ("Deflection", 8),
                ("Wake with Evening's Freshness", 7),
                ("Behind You!", 3),
                ("Carrion Crows", 4),
                ("Immortal Grapple", 10),
                ("Taste of Vitae", 6),
                ("Torn Signpost", 10),
                ("Undead Strength", 9),
                ("Swallowed by the Night", 4),
            ]
        ),
    }
    assert caplog.record_tuples == []


def test_2010tcdbng(caplog):
    """Card-level parenthesised commends (common)"""
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2010tcdbng.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2010tcdbng"].__getstate__() == {
        "id": "2010tcdbng",
        "event": "Trading Card Day",
        "event_link": None,
        "place": "Bad Naumheim, Germany",
        "date": "2010-05-08",
        "players_count": 10,
        "player": "Rudolf Scholz",
        "tournament_format": "2R+F",
        "score": "4vp in the final",
        "name": "The Storage Procurers",
        "author": None,
        "raven": 0,
        "cards": collections.OrderedDict(
            [
                ("Gilbert Duane", 1),
                ("Mariel, Lady Thunder", 1),
                ("Badr al-Budur", 1),
                ("Count Ormonde", 1),
                ("Didi Meyers", 1),
                ("Zebulon", 1),
                ("Dimple", 1),
                ("Mustafa Rahman", 1),
                ("Normal", 1),
                ("Ohanna", 1),
                ("Samson", 1),
                ("Basil", 1),
                ("Cloak the Gathering", 6),
                ("Conditioning", 7),
                ("Lost in Crowds", 2),
                ("Veil the Legions", 4),
                ("Carlton Van Wyk", 1),
                ("Gregory Winter", 1),
                ("Impundulu", 1),
                ("Muddled Vampire Hunter", 1),
                ("Ossian", 1),
                ("Procurer", 6),
                ("Young Bloods", 1),
                ("Concealed Weapon", 8),
                ("Deer Rifle", 1),
                ("Flash Grenade", 8),
                ("FBI Special Affairs Division", 1),
                ("Hunger Moon", 1),
                ("Restricted Vitae", 1),
                ("The Unmasking", 1),
                ("Channel 10", 1),
                ("Charisma", 2),
                ("Creepshow Casino", 1),
                ("KRCG News Radio", 1),
                ("Perfectionist", 2),
                ("Storage Annex", 6),
                ("Sudden Reversal", 3),
                ("Vessel", 3),
                ("Deflection", 7),
                ("Delaying Tactics", 2),
                ("On the Qui Vive", 7),
            ]
        ),
        "cards_comments": {
            "Conditioning": "should be more!",
            "Flash Grenade": ("brings fear to the methuselahs rather than to minions"),
            "Storage Annex": "great card! usually underestimated",
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
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2012pslp"].__getstate__() == {
        "id": "2012pslp",
        "event": "Praxis Seizure: Leiria",
        "event_link": None,
        "place": "Leiria, Portugal",
        "date": "2012-10-13",
        "players_count": 12,
        "player": "Patrick Gordo",
        "tournament_format": "2R+F",
        "score": None,
        "name": "Shadowfang",
        "author": None,
        "raven": 0,
        "cards": collections.OrderedDict(
            [
                ("Morel", 3),
                ("Gem Ghastly", 2),
                ("Hagar Stone", 2),
                ("Arthur Denholm", 2),
                ("Drusilla Euphemia", 1),
                ("Apache Jones", 1),
                ("Bela", 1),
                ("The Barrens", 1),
                ("Blood Doll", 1),
                ("Dreams of the Sphinx", 2),
                ("Giant's Blood", 1),
                ("Pentex™ Subversion", 1),
                ("Sudden Reversal", 3),
                ("Vessel", 2),
                ("Kindred Spirits", 16),
                ("Restructure", 1),
                ("Cloak the Gathering", 3),
                ("Confusion", 8),
                ("Elder Impersonation", 3),
                ("Eyes of Chaos", 7),
                ("Faceless Night", 2),
                ("Lost in Crowds", 3),
                ("Spying Mission", 5),
                ("Deny", 3),
                ("Swallowed by the Night", 4),
                ("Delaying Tactics", 2),
                ("My Enemy's Enemy", 3),
                ("On the Qui Vive", 3),
                ("Telepathic Misdirection", 5),
                ("Wake with Evening's Freshness", 2),
            ]
        ),
        "cards_comments": {},
        "comments": "",
    }
    assert caplog.record_tuples == []


def test_2k7campeonatojuizforano(caplog):
    """Very hard to parse comments (line braks, few markers)"""
    TWDA = twda._TWDA()
    with open(
        os.path.join(os.path.dirname(__file__), "2k7campeonatojuizforano.html")
    ) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2k7campeonatojuizforano"].__getstate__() == {
        "id": "2k7campeonatojuizforano",
        "event": "Campeonato Juizforano 2007",
        "event_link": None,
        "place": "Juiz de Fora, Brazil",
        "date": "2007-12-16",
        "players_count": 23,
        "player": "Pedro Paulo de Sousa Mendes",
        "tournament_format": None,
        "score": None,
        "name": "Imbued at Last",
        "author": None,
        "raven": 0,
        "cards": dict(
            [
                ('Travis "Traveler72" Miller', 4),
                ('Jennie "Cassie247" Orne', 3),
                ('Paul "Sixofswords29" Moreton', 2),
                ('François "Warden" Loehr', 2),
                ('Jack "Hannibal137" Harmon', 1),
                ("Aranthebes, The Immortal", 1),
                ("Carlton Van Wyk", 1),
                ("Ossian", 1),
                ("Wendell Delburton", 1),
                ("React with Conviction", 4),
                ("Second Sight", 5),
                ("Strike with Conviction", 5),
                ("The Crusader Sword", 1),
                ("Heart of Nizchetus", 1),
                ("Ivory Bow", 1),
                ("Anthelios, The Red Star", 1),
                ("Edge Explosion", 1),
                ("The Unmasking", 1),
                ("Angel of Berlin", 2),
                ("The Barrens", 1),
                ("The Church of Vindicated Faith", 1),
                ("Direct Intervention", 1),
                ("Fortschritt Library", 1),
                ("Memories of Mortality", 6),
                ("Millicent Smith, Puritan Vampire Hunter", 1),
                ("The Parthenon", 3),
                ("Rötschreck", 1),
                ("The Slaughterhouse", 4),
                ("Smiling Jack, The Anarch", 1),
                ("Tension in the Ranks", 1),
                ("Unity", 1),
                ("Wash", 1),
                ("Champion", 2),
                ("Discern", 2),
                ("Rejuvenate", 1),
                ("Vigilance", 3),
                ("Determine", 3),
            ]
        ),
        "cards_comments": {
            "Direct Intervention": (
                "saved me a lot of times, unfortunately I couldn't pack more than one."
            ),
            "Millicent Smith, Puritan Vampire Hunter": "no comments needed.",
            "The Slaughterhouse": (
                "useful either to speed deck depletion or to trade for something "
                "useful under Anthelios."
            ),
            "Smiling Jack, The Anarch": "crucial contest in the final table.",
            "Vigilance": "I started to win a game when I had those three in play.",
            "Wash": (
                "not as effective as I expected, but also not a hassle because it's "
                "trifle."
            ),
        },
        "comments": textwrap.dedent(
            """
            Description: The deck's goal is to setup as fast as you can by
            depleting your library and to use Unity/Anthelios to cycle back
            whatever master you need the most at the time.

            It was enough. I never needed more than this.

            Heart is no good when it shows up late, but this is a small price
            to pay when compared to how good it is when I draw it early (it was
            decisive in the final table).

            I only packed the extremely necessary events, so I wouldn't draw
            any extra table hate, and was lucky enough to put all 3 in play in
            every game. The decks runs wonderfully with those 3 on the table.
            """
        )[1:],
    }
    assert caplog.record_tuples == [
        # original file errors - the fixed version has none
        # (
        #     "krcg",
        #     logging.WARNING,
        #    "[    58][2k7campeonatojuizforano] failed to parse \"I couldn't pack more "
        #     'than one."',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #     '[    65][2k7campeonatojuizforano] failed to parse "or to trade for '
        #     'something useful under Anthelios."',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #   '[    70][2k7campeonatojuizforano] failed to parse "because it\'s trifle."',
        # ),
    ]


def test_2010pwbla1(caplog):
    """Very hard to parse comments (line braks, few markers)"""
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2010pwbla1.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2010pwbla1"].__getstate__() == {
        "id": "2010pwbla1",
        "event": "Powerbase: Los Angeles Event #1",
        "event_link": None,
        "place": "Strategicon - GAMEX 2010, Los Angeles, California",
        "date": "2010-05-29",
        "players_count": 12,
        "player": "Darby Keeney",
        "tournament_format": "2R+F",
        "score": None,
        "name": "[2010 TW] The World's Biggest Small Multirushers",
        "author": None,
        "raven": 0,
        "cards": dict(
            [
                ("Tupdog", 13),
                ("Esoara", 1),
                ("Janine", 1),
                ("Ember Wright", 1),
                ("Keith Moody", 1),
                ("Saiz", 1),
                ("Dive Bomb", 5),
                ("Goblinism", 1),
                ("Graverobbing", 2),
                ("Raw Recruit", 3),
                ("Thin-Blooded Seer", 2),
                ("As the Crow", 8),
                ("Nephandus", 1),
                ("Brick by Brick", 8),
                ("Immortal Grapple", 8),
                ("Lead Fist", 4),
                ("Raking Talons", 9),
                ("Stonestrength", 10),
                ("Hand of Conrad", 1),
                ("The Sargon Fragment", 1),
                ("Dragonbound", 1),
                ("Ashur Tablets", 5),
                ("Carver's Meat Packing and Storage", 1),
                ("Dreams of the Sphinx", 1),
                ("Fame", 1),
                ("Heidelberg Castle, Germany", 1),
                ("Powerbase: Montreal", 1),
                ("Secure Haven", 1),
                ("Vessel", 2),
                ("Ancient Influence", 1),
                ("Reins of Power", 1),
            ]
        ),
        "cards_comments": {
            "Ancient Influence": (
                'eradicate your prey and call as a "spare" Tupdog action'
            ),
            "As the Crow": "makes my Tuppers freaky.",
            "Ashur Tablets": "tune late-game combat as needed.",
            "Carver's Meat Packing and Storage": "anti-weenie.",
            "Dive Bomb": 'stealth multi-rush as a "spare" Tupdog action',
            "Dreams of the Sphinx": "combat support or free Tupdogs.",
            "Goblinism": 'destroy location as a "spare" Tupdog action.',
            "Hand of Conrad": "recycle Tupdogs, should probably be duplicated.",
            "Lead Fist": 'critical to circumvent "prevent 1" decks',
            "Nephandus": "safe removal of torporized minions.",
            "Powerbase: Montreal": "free Tupdogs",
            "Raking Talons": "probably should be 10.",
            "Raw Recruit": 'additional slaves from a "spare" Tupdog action.',
            "Reins of Power": (
                'eradicate your predator and call as a "spare" Tupdog action'
            ),
            "The Sargon Fragment": "recycle everything else",
            "Secure Haven": "to contest and to save a slave master.",
            "Thin-Blooded Seer": 'Tupdog "spare" actions.',
        },
        "comments": textwrap.dedent(
            """
            Comments:  Many thanks to Fred Scott for lending me 2 Tupdogs for this
            tournament.   Generally, I have found a 2.5:1 Tupdog-to-!Tremere ratio
            to work out pretty well, though a long string of Dogs at the top pf
            one's crypt is frustrating.

            The objective for this deck is to get additional mileage from the
            Tupdogs...decreasing their effective cost from 1 pool per action to
            0.5 pool per action and further leveraging both the rush and the slave
            option (rush first, untap, available for slave clause, take an action
            of the slave clause is not needed).

            The deck is supposed to carry 1 more Ashur Tablet, but I seem to own
            only 5 at this time.  4, 6 or 7 seem like the right numbers to me,
            depending on your risk tolerance and recycling needs.

            Synergies:
            Carver's + Dragonbound and Carver's + Vessel are pretty clear.
            Carver's + Raw Recruit is an indefinate hold on a Recruit target (that
            could not be Graverobbed).  Carver's not affecting Tupdogs is a bonus.

            Heidleburg can save master vampires from dangerous hunting
            requirements, can empty a Tupdog of before it explodes and allows 2
            Hand of Conrad actions per turn.

            a "good" combat ran "set close and agg hands, grapple, prevent and
            untap"
            """
        )[1:],
    }
    # these comments raise errors: they could as weel be cards we fail to parse
    assert caplog.record_tuples == [
        # original file errors - the fixed version has none
        # (
        #     "krcg",
        #     logging.WARNING,
        #     '[    88][2010pwbla1] failed to parse "Tupdog action"',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #     '[    89][2010pwbla1] failed to parse "Tupdog action"',
        # ),
    ]


def test_2k5sharednun(caplog):
    """Discipline name as header must not be mistaken for the Master card
    Note "2 Animalism" was changed to "Animalism x2" in decklist
    This serves as a test for post-name counts decklists like 2k9linkopingmay
    """
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k5sharednun.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2k5sharednun"].__getstate__() == {
        "id": "2k5sharednun",
        "event": "Shared Nightmare",
        "event_link": None,
        "place": "Utrecht, Netherlands",
        "date": "2005-07-02",
        "players_count": 16,
        "player": "Jeroen van Oort",
        "tournament_format": "3R+F",
        "score": None,
        "name": "Deeper Underground",
        "author": None,
        "raven": 0,
        "cards": collections.OrderedDict(
            [
                ("Christanius Lionel, The Mad Chronicler", 1),
                ("Calebros, The Martyr", 1),
                ("Gemini", 1),
                ("Nigel the Shunned", 1),
                ("Bobby Lemon", 1),
                ("Roger Farnsworth", 1),
                ("Clarissa Steinburgen", 1),
                ("Panagos Levidis", 1),
                ("Shannon Price, the Whisperer", 1),
                ("Watenda", 1),
                ("Mouse", 1),
                ("Zip", 1),
                ("Blood Doll", 6),
                ("Direct Intervention", 2),
                ("Heidelberg Castle, Germany", 2),
                ("Animalism", 2),
                ("Slum Hunting Ground", 1),
                ("Dreams of the Sphinx", 1),
                ("Faceless Night", 3),
                ("Cloak the Gathering", 6),
                ("Lost in Crowds", 2),
                ("Clotho's Gift", 2),
                ("Behind You!", 4),
                ("Cats' Guidance", 5),
                ("Guard Dogs", 3),
                ("Raven Spy", 7),
                ("Aid from Bats", 7),
                ("Carrion Crows", 8),
                ("Pack Alpha", 3),
                ("Canine Horde", 3),
                ("Army of Rats", 1),
                ("Forced Awakening", 7),
                ("Computer Hacking", 5),
                ("Delaying Tactics", 2),
                ("J. S. Simmons, Esq.", 1),
                ("Tasha Morgan", 1),
                ("Dodge", 3),
                ("Laptop Computer", 3),
            ]
        ),
        "cards_comments": {},
        "comments": "\"Look in the sky, it's a raven. No, it's a bat.\n"
        "No, it's a crow, No it's a swarm of them all!!!\"\n",
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


def test_2019ecwon1pf(caplog):
    """Discipline name as header must not be mistaken for the Master card
    Using long vampire name with comma and (ADV)
    """
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2019ecwon1pf.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2019ecwon1pf"].__getstate__() == {
        "id": "2019ecwon1pf",
        "event": "EC WoN - Monday",
        "event_link": "http://www.vekn.net/event-calendar/event/9321",
        "place": "Paris, France",
        "date": "2019-08-12",
        "players_count": 25,
        "player": "Randal Rudstam",
        "tournament_format": "2R+F",
        "score": "1gw4.5 + 1.5vp in the final",
        "name": "Sascha Vykos Toolbox",
        "author": None,
        "raven": 0,
        "cards": collections.OrderedDict(
            [
                ("Sascha Vykos, The Angel of Caine (ADV)", 5),
                ("Meshenka", 3),
                ("Lambach", 1),
                ("John Paleologus", 1),
                ("Stravinsky", 1),
                ("Velya, The Flayer", 1),
                ("Ashur Tablets", 6),
                ("Black Forest Base", 1),
                ("Dreams of the Sphinx", 1),
                ("Fear of Mekhet", 1),
                ("Information Highway", 1),
                ("Legendary Vampire", 1),
                ("Library Hunting Ground", 1),
                ("Papillon", 3),
                ("Pentex™ Subversion", 1),
                ("Powerbase: Madrid", 1),
                ("Vessel", 2),
                ("Villein", 5),
                ("Wider View", 1),
                ("Abbot", 1),
                ("Army of Rats", 1),
                ("Deep Song", 1),
                ("Under Siege", 1),
                ("Asanbonsam Ghoul", 2),
                ("Carlton Van Wyk", 1),
                ("Bowl of Convergence", 1),
                ("Anarchist Uprising", 1),
                ("Ancient Influence", 1),
                ("Ancilla Empowerment", 1),
                ("Banishment", 2),
                ("Kine Resources Contested", 2),
                ("Neonate Breach", 1),
                ("Political Stranglehold", 1),
                ("Reins of Power", 1),
                ("Changeling", 2),
                ("Mind of the Wilds", 1),
                ("Private Audience", 1),
                ("Plasmic Form", 1),
                ("Cats' Guidance", 1),
                ("Delaying Tactics", 1),
                ("Eagle's Sight", 1),
                ("Enhanced Senses", 1),
                ("Eyes of Argus", 3),
                ("Guard Dogs", 1),
                ("My Enemy's Enemy", 1),
                ("On the Qui Vive", 2),
                ("Precognition", 1),
                ("Rat's Warning", 1),
                ("Read the Winds", 1),
                ("Sense the Savage Way", 1),
                ("Spirit's Touch", 1),
                ("Telepathic Misdirection", 5),
                ("Aid from Bats", 1),
                ("Breath of the Dragon", 1),
                ("Canine Horde", 1),
                ("Carrion Crows", 2),
                ("Chiropteran Marauder", 3),
                ("Drawing Out the Beast", 1),
                ("Inner Essence", 1),
                ("Meld with the Land", 1),
                ("Starvation of Marena", 1),
            ]
        ),
        "cards_comments": {},
        "comments": "Description: Card selection is strong! Randyman\n",
    }
    assert caplog.record_tuples == []


def test_2020pihc(caplog):
    """Discipline name as header must not be mistaken for the Master card
    Long preface with formatted comment (keep spaces and carriage returns)
    Using long vampire name with comma and (ADV)
    """
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2020pihc.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2020pihc"].__getstate__() == {
        "id": "2020pihc",
        "event": "Personal Involvement",
        "event_link": "http://www.vekn.net/event-calendar/event/9566",
        "place": "Hamilton, Canada",
        "date": "2020-02-22",
        "player": "Jay Kristoff",
        "players_count": 10,
        "tournament_format": "2R+F",
        "score": "0gw2.5 + 1.5vp in the final",
        "author": None,
        "name": "Sauce or GTFO",
        "raven": 0,
        "cards": collections.OrderedDict(
            [
                ("Matasuntha", 6),
                ("Calvin Cleaver", 1),
                ("Fergus Alexander", 1),
                ("Lillian", 1),
                ("T.J.", 1),
                ("Malcolm", 1),
                ("Robert Price", 1),
                ("Abombwe", 1),
                ("Ecoterrorists", 1),
                ("Fame", 1),
                ("Giant's Blood", 1),
                ("Perfectionist", 1),
                ("Villein", 1),
                ("Wider View", 1),
                ("Bum's Rush", 2),
                ("Deep Song", 2),
                ("Go Anarch", 1),
                ("Harass", 2),
                ("Nose of the Hound", 2),
                ("Rewilding", 1),
                ("Shadow of the Beast", 1),
                ("Thing", 2),
                ("Mylan Horseed", 1),
                ("Bowl of Convergence", 1),
                ("Eye of Hazimel", 1),
                ("Gran Madre di Dio, Italy", 1),
                ("IR Goggles", 1),
                ("Kevlar Vest", 1),
                ("Ancient Influence", 1),
                ("Dog Pack", 2),
                ("Homunculus", 1),
                ("Enkil Cog", 1),
                ("Forced March", 3),
                ("Freak Drive", 5),
                ("Instantaneous Transformation", 3),
                ("Eyes of Argus", 2),
                ("Telepathic Misdirection", 1),
                ("Blur", 4),
                ("Flesh of Marble", 2),
                ("Form of Mist", 1),
                ("Pursuit", 2),
                ("Skin of Night", 1),
                ("Taste of Vitae", 3),
                ("Dragonbound", 1),
            ]
        ),
        "cards_comments": {},
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
            "[   134][2020pihc] deck has too few cards (59) [Sauce or GTFO]",
        ),
    ]


def test_2k8sequeenslandcq(caplog):
    """Discipline name as header must not be mistaken for the Master card
    - Using long vampire name with comma and (ADV)
    - Comments on a crypt card

    The unclosed parenthesis on the Elder Impersonation is vicious: this single list
    makes it impossible to considered parenthesised comments as valid multiline,
    since the following Seduction next line shoudl be included
    """
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k8sequeenslandcq.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2k8sequeenslandcq"].__getstate__() == {
        "id": "2k8sequeenslandcq",
        "event": "Gencon SE Queensland CCQ",
        "event_link": None,
        "place": "Gencon Australia, Brisbane, Australia",
        "date": "2008-07-05",
        "player": "Steven McRoy",
        "players_count": 13,
        "tournament_format": None,
        "score": None,
        "author": None,
        "name": "Arika Turbo",
        "raven": 0,
        "cards": dict(
            [
                ("Arika", 15),
                ("Daring the Dawn", 10),
                ("Force of Will", 10),
                ("Soul Gem of Etrius", 7),
                ("Majesty", 3),
                ("Freak Drive", 10),
                ("Conditioning", 10),
                ("Distraction", 10),
                ("Awe", 10),
                ("Forgotten Labyrinth", 5),
                ("Seduction", 2),
                # fix-up
                ("Praxis Seizure: Geneva", 4),
                ("Praxis Seizure: Berlin", 4),
                ("Praxis Seizure: Cairo", 2),
                ("Elder Impersonation", 3),
            ]
        ),
        "cards_comments": {
            "Arika": "could have more, 15 was enough",
            "Elder Impersonation": "would exchange for Faceless Night x4",
            "Forgotten Labyrinth": "would add one more",
            "Seduction": "would delete",
        },
        "comments": """Comments: Well the run is you get Arika out, wait a turn
(hopefully no pentex, smash, or her getting torped), next
you equip her with soul gem, Freak Drive to untap, then
call Praxis S whatever to increase her capacity +1 and to
make her prince of whatever, Awe it so you burn the blood
off Arika down to 2, pass the vote with 22 votes for, now
you are ready to bleed, force of will +2 bleed, daring the
dawn to make it unblockable at inferior, conditioning for
a bleed of 8, taking 3 agg damage burning Arika and a new
ones comes into play. Play Praxis, Awe, Force of Will,
Daring the Dawn, Conditioning bleed of 8, if you get stuck
you can play distraction to not only get rid of the other
soul gems and rubbish from your hand but to get back on
track with the card combo. freak drive to then call PS

repeat until you have wiped everyone out
""",
    }
    assert caplog.record_tuples == [
        # original file errors - the fixed version has none
        # (
        #     "krcg",
        #     logging.WARNING,
        #     '[    24][2k8sequeenslandcq] failed to parse "Praxis Seizure: Geneva x4, '
        #     'Berlin x4, Cairo x2"',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #     '[    26][2k8sequeenslandcq] failed to parse "Elder Impersonation x3 '
        #     '(would exchange for Faceless Night x4"',
        # ),
    ]


def test_2011ptwolss(caplog):
    """Card cited in the preface can lead to parsing errors."""
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2011ptwolss.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2011ptwolss"].__getstate__() == {
        "id": "2011ptwolss",
        "date": "2011-10-29",
        "event": "Poison the Well of Life",
        "event_link": None,
        "name": "Yet another Imbued deck winning a tournament",
        "place": "Stockholm, Sweden",
        "player": "Marcus Berg",
        "players_count": 19,
        "score": None,
        "tournament_format": "2R+F",
        "author": None,
        "raven": 0,
        "cards": collections.OrderedDict(
            [
                ("Mary Anne Blaire", 2),
                ("Epikasta Rigatos", 2),
                ("Lodin (Olaf Holte)", 2),
                ("Victor Donaldson", 2),
                ("Emily Carson", 2),
                ("Maman Boumba", 1),
                ("Keith Moody", 1),
                ("Enchant Kindred", 4),
                ("Govern the Unaligned", 15),
                ("Mind Numb", 2),
                ("Conditioning", 3),
                ("Daring the Dawn", 1),
                ("Freak Drive", 7),
                ("The Kiss of Ra", 2),
                ("Murmur of the False Will", 6),
                ("Carlton Van Wyk", 1),
                ("React with Conviction", 1),
                ("Heart of Nizchetus", 1),
                ("Anarch Troublemaker", 1),
                ("Dreams of the Sphinx", 4),
                ("Giant's Blood", 1),
                ("Information Highway", 1),
                ("Lilith's Blessing", 1),
                ("Misdirection", 1),
                ("Pentex™ Subversion", 2),
                ("Villein", 6),
                ("Wider View", 2),
                ("Banishment", 1),
                ("Parity Shift", 1),
                ("Deflection", 7),
                ("Eyes of Argus", 3),
                ("Obedience", 8),
                ("Second Tradition: Domain", 8),
            ]
        ),
        "cards_comments": {},
        "comments": "Description: Too many cards, should be slimmed about 15 cards.\n"
        "All Enchant Kindred should be Entrancement. One or both Kiss of\n"
        "Ra should be Mind Numb. Villein and Lilith's Blessing should be\n"
        "2 Blood Doll and 2 Vessel. Should maybe add 2-4 Majesty. Crypt\n"
        "should be 4 Mary Anne Blaire, 2 Lodin and the rest singles.\n",
    }
    assert caplog.record_tuples == []


def test_2k8tfnwesterville(caplog):
    """A dubious "Reactions" header that has once been wrongly parsed as a card."""
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k8tfnwesterville.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2k8tfnwesterville"].__getstate__() == {
        "id": "2k8tfnwesterville",
        "date": "2008-01-27",
        "event": "The Final Nights",
        "event_link": None,
        "name": "Tembo!!",
        "place": "Westerville, Ohio",
        "player": "Matt Piatek",
        "players_count": 16,
        "score": None,
        "tournament_format": "2R+F",
        "author": None,
        "raven": 0,
        "cards": collections.OrderedDict(
            [
                ("Demdemeh", 3),
                ("Matata", 3),
                ("Babalawo Alafin", 3),
                ("Wamukota", 2),
                ("Solomon Batanea", 2),
                ("Minion Tap", 3),
                ("Blood Doll", 2),
                ("The Parthenon", 2),
                ("Maabara", 2),
                ("Lazarene Inquisitor", 1),
                ("Mbare Market, Harare", 1),
                ("Heidelberg Castle, Germany", 1),
                ("Crematorium", 1),
                ("Animalism", 1),
                ("Rapid Healing", 2),
                ("Restoration", 2),
                ("Force of Will", 1),
                ("Tier of Souls", 1),
                ("Freak Drive", 5),
                ("Day Operation", 2),
                ("Wake with Evening's Freshness", 4),
                ("Rat's Warning", 2),
                ("Guard Dogs", 1),
                ("Cats' Guidance", 1),
                ("Eagle's Sight", 1),
                ("Spirit's Touch", 2),
                ("Precognition", 1),
                ("Enhanced Senses", 1),
                ("Telepathic Misdirection", 2),
                ("My Enemy's Enemy", 1),
                ("Read the Winds", 1),
                ("Anthelios, The Red Star", 2),
                ("Taste of Vitae", 6),
                ("Indomitability", 4),
                ("Rolling with the Punches", 4),
                ("Resilience", 3),
                ("Skin of Rock", 2),
                ("Unflinching Persistence", 2),
                ("Hidden Strength", 2),
                ("Drawing Out the Beast", 2),
                ("Pack Alpha", 1),
                ("Canine Horde", 1),
                ("Elephant Guardian", 7),
                ("Raven Spy", 3),
                ("Swarm", 2),
                ("J. S. Simmons, Esq.", 1),
                ("Tasha Morgan", 1),
                ("Erebus Mask", 1),
                ("Kerrie", 1),
                ("Unlicensed Taxicab", 1),
            ]
        ),
        "cards_comments": {},
        "comments": "Description: Demdemeh makes a herd of elephant allies with 2 "
        "hand\n"
        "damage and one bleed. Babalawo Alafin combines with Maabara to "
        "allow\n"
        "you to craft the hand you need.\n"
        "\n"
        "It didn't work the way it was intended to in the finals. In "
        "retrospect\n"
        "I should have brought out Demdemeh instead of Wamukota as my "
        "second\n"
        "vampire, but I thought his ability would be important for my "
        "retain\n"
        "actions(it was never used). I never could get enough pool to "
        "bring\n"
        "out Demdemeh afterwards. A herd of elephants would have greatly\n"
        "increased my ousting ability.\n"
        "\n"
        "It is nice to know that the deck can survive without all of the "
        '"A"\n'
        "team in play.\n",
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
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2k7fsmc"].__getstate__() == {
        "id": "2k7fsmc",
        "date": "2007-12-08",
        "event": "Fee Stake: Mexico City",
        "event_link": None,
        "name": "Nephandi",
        "place": "Mexico City, Mexico",
        "player": "Omael Rangel",
        "players_count": 10,
        "score": None,
        "tournament_format": "2R+F",
        "author": None,
        "raven": 0,
        "cards": collections.OrderedDict(
            [
                ("Antonio d'Erlette", 4),
                ("Tupdog", 4),
                ("Keith Moody", 2),
                ("Ember Wright", 1),
                ("Saiz", 1),
                ("Computer Hacking", 6),
                ("Empowering the Puppet King", 8),
                ("Nephandus", 8),
                ("Ossian", 1),
                ("Vagabond Mystic", 1),
                ("Concealed Weapon", 8),
                ("Glancing Blow", 3),
                ("Molotov Cocktail", 3),
                (".44 Magnum", 1),
                ("Flash Grenade", 7),
                ("The Unmasking", 2),
                ("Archon Investigation", 1),
                ("Blood Doll", 4),
                ("Direct Intervention", 3),
                ("Haven Uncovered", 2),
                ("Information Highway", 1),
                ("Life in the City", 6),
                ("Memories of Mortality", 4),
                ("Mob Connections", 1),
                ("Deflection", 8),
                ("On the Qui Vive", 5),
                ("Wake with Evening's Freshness", 3),
            ]
        ),
        "cards_comments": {},
        "comments": (
            "4 memories of mortality -- when they are gone i should add a fort. "
            "library, a pentex subversion and maybe anarchist troublemaker\n"
            "6 computer hacking -- maybe add 1 more\n"
            "3 glancing blows -- I'll remove this and add more concealed and molotovs\n"
            "1 .44 magnum -- this should be another grenade but i only had 7 at the "
            "time\n"
        ),
    }
    assert caplog.record_tuples == []


def test_2k6nerq_templecon(caplog):
    """A vicious example of using disciplines both as headers and master cards."""
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k6nerq-templecon.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2k6nerq-templecon"].__getstate__() == {
        "id": "2k6nerq-templecon",
        "date": "2006-01-28",
        "event": "Saqqaf, Keeper of the Grand TempleCon of Set - Northeast Regional "
        "Qualifier 2006",
        "event_link": None,
        "name": None,
        "place": "Providence, Rhode Island",
        "player": "Jonathan Scherer",
        "players_count": 39,
        "score": None,
        "tournament_format": "3R+F",
        "author": None,
        "raven": 0,
        "cards": dict(
            [
                ("Ingrid Rossler", 3),
                ("Caitlin", 2),
                ("Chandler Hungerford", 2),
                ("Faruq", 1),
                ("Iliana", 1),
                ("Camille Devereux, The Raven", 1),
                ("Ramona", 1),
                ("Ricki Van Demsi", 1),
                ("Earth Control", 5),
                ("Form of Mist", 5),
                ("Earth Meld", 13),
                ("Claws of the Dead", 5),
                ("Restoration", 2),
                ("Day Operation", 1),
                ("Freak Drive", 4),
                ("Govern the Unaligned", 4),
                ("Conditioning", 3),
                ("Foreshadowing Destruction", 1),
                ("Deflection", 4),
                ("Raven Spy", 3),
                ("Cats' Guidance", 5),
                ("Instinctive Reaction", 1),
                ("Computer Hacking", 2),
                ("Aranthebes, The Immortal", 1),
                ("Mr. Winthrop", 1),
                ("Palatial Estate", 1),
                ("Procurer", 1),
                ("Wake with Evening's Freshness", 8),
                ("Second Tradition: Domain", 2),
                ("Renegade Garou", 3),
                ("Club Zombie", 1),
                ("Zoo Hunting Ground", 1),
                ("Ecoterrorists", 2),
                ("KRCG News Radio", 1),
                ("WMRH Talk Radio", 1),
                ("Smiling Jack, The Anarch", 1),
                ("Dreams of the Sphinx", 1),
                ("The Barrens", 1),
                ("Blood Doll", 3),
                # fix-up
                ("Dominate", 3),
            ]
        ),
        "cards_comments": {},
        "comments": "Slippery When Wet\n"
        "\n"
        "This deck is an old friend of mine. It has been\n"
        "heavily modified over the years, with the most recent\n"
        "modification being the addition of dominate to the\n"
        "deck. The Gangrel were the first clan that I really\n"
        "got to work in casual play, many years ago. I tried it\n"
        "a few times in tournaments but it lacked the speed\n"
        "necessary to win a table. After the addition of\n"
        "dominate for some added pressure it has been much more\n"
        "effective, with several strong showings. While a good\n"
        "position and some luck was key in winning the day,\n"
        "this deck showed itself to be a strong competitor.\n",
    }
    assert caplog.record_tuples == [
        # original file errors - the fixed version has none
        # (
        #     "krcg",
        #     logging.WARNING,
        #     '[    24][2k6nerq-templecon] improper discipline "Protean"',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #     '[    30][2k6nerq-templecon] improper discipline "Fortitude"',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #     '[    35][2k6nerq-templecon] improper discipline "Dominate"',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #     '[    41][2k6nerq-templecon] improper discipline "Animalism"',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #     '[    66][2k6nerq-templecon] improper discipline "Dominate\t3"',
        # ),
    ]


def test_2k3italyqualifier(caplog):
    """Multiline cards comments using parentheses."""
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k3italyqualifier.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2k3italyqualifier"].__getstate__() == {
        "id": "2k3italyqualifier",
        "date": "2003-09-27",
        "event": "Italian ECQ",
        "event_link": None,
        "name": "Menú: Paella y Tortilla de Patata (Menu: Paella & Potato",
        "place": "Italy, Modena",
        "player": "Iñaki Puigdollers",
        "players_count": 68,
        "score": None,
        "tournament_format": None,
        "author": None,
        "raven": 0,
        "cards": dict(
            [
                ("Jost Werner", 2),
                ("Creamy Jade", 2),
                ("The Rose", 2),
                ("Sheila Mezarin", 1),
                ("Elizabeth Westcott", 1),
                ("Mercy, Knight Inquisitor", 1),
                ("Remilliard, Devout Crusader", 1),
                ("Lolita", 1),
                ("Carter", 1),
                ("Palla Grande", 4),
                ("The Art of Pain", 1),
                ("Blood Doll", 2),
                ("Direct Intervention", 1),
                ("Vicissitude", 2),
                ("Anarch Troublemaker", 1),
                ("Art Scam", 9),
                ("Enchant Kindred", 9),
                ("Changeling", 6),
                ("Majesty", 7),
                ("War Ghoul", 4),
                ("Tasha Morgan", 1),
                ("J. S. Simmons, Esq.", 1),
                ("Wake with Evening's Freshness", 4),
                ("Forced Awakening", 2),
                ("Telepathic Misdirection", 4),
                ("My Enemy's Enemy", 4),
                ("Plasmic Form", 5),
                # fix-up
                ("Jake Washington", 3),
                ("The Hungry Coyote", 1),
                ("The Embrace", 3),
                ("Entrancement", 3),
                ("The Summoning", 5),
                ("Change of Target", 6),
                ("Marijava Ghoul", 2),
            ]
        ),
        "cards_comments": {
            "Forced Awakening": (
                "helps to dry my vamps before drinking a full Jake for supper"
            ),
            # fix-up
            "Jake Washington": (
                "He is perfect for both the WG and let my midcaps eat if hungry"
            ),
            "The Hungry Coyote": (
                "after the tournament I have decided that the Jakes are enough for "
                "this and that my minions have always better actions to do rather than "
                'hunt. I would change it for a Pentex "anti helena/Lucas halton/..." '
                "Subversion"
            ),
            "The Embrace": (
                "extremely useful for bleed and multiple action as rescuing from "
                "torpor/eating alive/rush walls"
            ),
            "Entrancement": (
                "To defend my omelettes, for bleeding or for an extrarecruitment if "
                "ever able, this card is so great"
            ),
            "The Summoning": (
                "key, essential, If you summon a WG and the action is blocked you "
                "don't lose the Meat machine so you could try it later, and it also "
                "multiplies the number of getting a WG from my library"
            ),
            "Change of Target": (
                "for the embraces aswell and the Ghouls if an evil killer vamps untaps "
                "suddenly while attacking"
            ),
            "Marijava Ghoul": (
                "exceptionals, There are 15 pressence action cards and this makes 'em "
                "more efficient, but he is also meat for the WG god"
            ),
        },
        "comments": "Omelette)\n\n"
        "Description: !toreador module with Tzimisce supportto develope a quiet\n"
        "game while bloating and hitting with the WG. As I have said the deck\n"
        "could be defined as a bloat deck with high bleeding potential while is\n"
        "the time. Defend your ground, generate pool and play as many minions\n"
        "and whever prepared offer Paella for everyone!, The potato omelette\n"
        "will send whoever who tries to interdict to torpor... .\n",
    }
    assert caplog.record_tuples == [
        # original file errors - the fixed version has none
        # (
        #     "krcg",
        #     logging.WARNING,
        #     '[    41][2k3italyqualifier] failed to parse "3 Jake Washington (Hunter) '
        #     '(He is perfect for both the WG and let my midcaps eat..."',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #     '[    52][2k3italyqualifier] failed to parse "3 The Embrace (extremely '
        #     'useful for bleed and multiple action as rescuing from t..."',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #   '[    62][2k3italyqualifier] failed to parse "3 Entrancement (To defend my '
        #     'omelettes, for bleeding or for an extrarecruitment ..."',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #    '[    68][2k3italyqualifier] failed to parse "6 Change of Target (for the '
        #     'embraces aswell and the Ghouls if an evil killer vam..."',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #     '[    75][2k3italyqualifier] failed to parse "2 Marijava Ghoul '
        #     '(exceptionals, There are 15 pressence action cards and this mak..."',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #     '[    89][2k3italyqualifier] failed to parse "Greetings,"',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #    '[    90][2k3italyqualifier] failed to parse "Iñaki, Prince de Barcelona"',
        # ),
    ]


def test_2k8torunminiq(caplog):
    """Multiline cards comments using parentheses."""
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k8torunminiq.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2k8torunminiq"].__getstate__() == {
        "id": "2k8torunminiq",
        "date": "2008-05-31",
        "event": "MQ",
        "event_link": None,
        "name": "Along comes the spider",
        "place": "Torun, Poland",
        "player": "Marcin Szybkowski",
        "players_count": 12,
        "score": None,
        "tournament_format": "3R+F",
        "author": None,
        "raven": 0,
        "cards": dict(
            [
                ("Nkule Galadima", 3),
                ("Uchenna", 3),
                ("Amavi", 2),
                ("Jubal", 1),
                ("Hasani", 1),
                ("Dolie", 1),
                ("Meno Ngari", 1),
                ("Dreams of the Sphinx", 2),
                ("Vessel", 3),
                ("Blood Doll", 2),
                ("Giant's Blood", 1),
                ("Jungle Hunting Ground", 1),
                ("Mbare Market, Harare", 1),
                ("Legendary Vampire", 1),
                ("Ancestor Spirit", 1),
                ("Belonging Grants Protection", 3),
                ("Restoration", 2),
                ("Aranthebes, The Immortal", 1),
                ("Army of Rats", 1),
                ("Freak Drive", 7),
                ("Predator's Mastery", 4),
                ("Akunanse Kholo", 1),
                ("Strange Day", 1),
                ("The Secret Must Be Kept", 2),
                ("Anarchist Uprising", 1),
                ("Sniper Rifle", 2),
                ("Ivory Bow", 1),
                ("Reliquary: Akunanse Remains", 1),
                ("Kduva's Mask", 1),
                ("Raven Spy", 5),
                ("Shaman", 1),
                ("Carrion Crows", 5),
                ("Invoking the Beast", 5),
                ("Taste of Vitae", 4),
                ("Rolling with the Punches", 4),
                ("Skin of Steel", 3),
                ("Canine Horde", 2),
                ("Flesh Bond", 2),
                # fix-up
                ("Direct Intervention", 2),
                ("Powerbase: Tshwane", 1),
                ("WMRH Talk Radio", 1),
                ("No Secrets From the Magaji", 3),
                ("Predator's Transformation", 5),
                ("Ancilla Empowerment", 1),
                ("Superior Mettle", 2),
                ("Predator's Communion", 4),
            ]
        ),
        "cards_comments": {
            "Ancilla Empowerment": "nobody really expects these 2 until its too late",
            "Canine Horde": "crucial in the final",
            "Direct Intervention": (
                "I'm thinking about adding another one, this card is cruicial for any "
                "block denial actions, or things that simply screw your spiders"
            ),
            "Flesh Bond": "butt-saver",
            "No Secrets From the Magaji": (
                "was thinking about 4-5, but 3 is a good number, you draw too much "
                "attention if you put it on too early"
            ),
            "Powerbase: Tshwane": (
                "there was some magic around this card, I got it in every single "
                "game, in the first 10 cards drawn"
            ),
            "Predator's Communion": (
                "very helpful before you get no secrets, easy to drop afterwards"
            ),
            "Predator's Mastery": "lovely thanks to several ally decks playing",
            "Predator's Transformation": (
                "wonderful card, can play it anytime, and the bonus superior effect "
                "did help a lot many times"
            ),
            "Strange Day": "won me the final pretty much",
            "Superior Mettle": (
                "I'd revise the prevent cards anyway, maybe adding some with no cost, "
                "or more of SM. it worked nice in overall though"
            ),
            "The Secret Must Be Kept": "amazing card against any ally deck",
            "WMRH Talk Radio": (
                "didn't use it at all, metagame wasn't stealth heavy though"
            ),
        },
        "comments": (
            "Description: This deck won the mini qualifier in Torun, a local\n"
            "tournament in Warsaw, and managed to get into the final round during\n"
            "the Polish ECQ.  it's a very solid deck against most archetypes, card\n"
            "flow is really impressive, and it does tend to be underestimated (not\n"
            "too often, but it happens).  it's also a very fun deck to play, in the\n"
            "ideal setup you block out your predator while making constant pressure\n"
            "on your prey.\n"
        ),
    }
    # WMRH Talk Radio and Predator's Communion are wrongly parsed but do not show
    # in the log, as they're merged with previous wrongly parsed blocks
    assert caplog.record_tuples == [
        # original file errors - the fixed version has none
        # (
        #     "krcg",
        #     logging.WARNING,
        #     "[    37][2k8torunminiq] failed to parse \"2 Direct Intervention (I'm "
        #     'thinking about adding another one, this card is cruic..."',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #    '[    43][2k8torunminiq] failed to parse "1 Powerbase: Tshwane (there was '
        #     'some magic around this card, I got it in every s..."',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #    '[    50][2k8torunminiq] failed to parse "3 No Secrets of the Magaji (was '
        #     'thinking about 4-5, but 3 is a good number, you ..."',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #     "[    59][2k8torunminiq] failed to parse \"5 Predator's Transformation "
        #     '(wonderful card, can play it anytime, and the bonus ..."',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #     '[    70][2k8torunminiq] failed to parse "1 ancilla empowement (nobody '
        #     'really expects these 2 until its too late)"',
        # ),
        # (
        #     "krcg",
        #     logging.WARNING,
        #     "[    92][2k8torunminiq] failed to parse \"2 Superior Mettle (I'd revise "
        #     'the prevent cards anyway, maybe adding some with n..."',
        # ),
    ]


def test_2k2eclastq(caplog):
    """Wrong card, short name and post count: "Jack 5" """
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k2eclastq.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2k2eclastq"].__getstate__() == {
        "id": "2k2eclastq",
        "date": "2002-11-30",
        "event": "Austrian NC 2002 - Last Chance Qualifier",
        "event_link": None,
        "name": None,
        "place": "Vienna, Austria",
        "player": "Stéphane Lavrut",
        "players_count": 115,
        "score": None,
        "tournament_format": None,
        "author": None,
        "raven": 0,
        "cards": collections.OrderedDict(
            [
                ("Lolita Houston", 3),
                ("Terrence", 2),
                ("Horatio", 2),
                ("Caliban", 1),
                ("Corine Marcón", 1),
                ("Devin Bisley", 1),
                ("The Rose", 1),
                ("Wendy Wade", 1),
                ("Blood Doll", 4),
                ("Direct Intervention", 2),
                ("Jake Washington", 5),
                ("Library Hunting Ground", 2),
                ("Memories of Mortality", 4),
                ("Vagabond Mystic", 2),
                ("War Ghoul", 11),
                ("Ghoul Escort", 5),
                ("Revenant", 4),
                ("Changeling", 6),
                ("Plasmic Form", 5),
                ("Delaying Tactics", 2),
                ("Breath of the Dragon", 2),
                ("Trap", 7),
            ]
        ),
        "cards_comments": {},
        "comments": "Description: Here is THE wargoule deck\n",
    }
    assert caplog.record_tuples == [
        # original file parsing error - the fixed version has no error
        # ("krcg", logging.WARNING, '[    25][2k2eclastq] failed to parse "Jack 5"'),
    ]


def test_2k2stranger(caplog):
    """Wrong card, short name and post count: "Jack 5" """
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k2stranger.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2k2stranger"].__getstate__() == {
        "id": "2k2stranger",
        "date": "2002-01-05",
        "event": "The Stranger Among Us",
        "event_link": None,
        "name": None,
        "place": "Boston, Massachusetts",
        "player": "Kevin Scribner",
        "players_count": 0,
        "score": None,
        "tournament_format": None,
        "author": None,
        "raven": 0,
        "cards": collections.OrderedDict(
            [
                ("Caliban", 2),
                ("Lambach", 1),
                ("Stravinsky", 1),
                ("Anton", 1),
                ("Little Tailor of Prague", 1),
                ("Meshenka", 1),
                ("Sascha Vykos, The Angel of Caine", 1),
                ("Corine Marcón", 1),
                ("Devin Bisley", 1),
                ("Lolita Houston", 1),
                ("Terrence", 1),
                ("Anarch Revolt", 2),
                ("Blood Doll", 6),
                ("Library Hunting Ground", 1),
                ("Powerbase: Montreal", 1),
                ("The Rack", 1),
                ("Rötschreck", 3),
                ("Smiling Jack, The Anarch", 2),
                ("Tier of Souls", 3),
                ("Revelations", 3),
                ("Revenant", 2),
                ("Ivory Bow", 1),
                ("Femur of Toomler", 1),
                ("Cats' Guidance", 6),
                ("Forced Awakening", 6),
                ("Read the Winds", 6),
                ("Eagle's Sight", 6),
                ("Enhanced Senses", 4),
                ("Spirit's Touch", 3),
                ("Precognition", 3),
                ("Telepathic Misdirection", 6),
                ("Inner Essence", 8),
                ("Chiropteran Marauder", 10),
                ("Breath of the Dragon", 6),
            ]
        ),
        "cards_comments": {},
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
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2k2origins1"].__getstate__() == {
        "id": "2k2origins1",
        "date": "2002-07-04",
        "event": "Origins Thursday",
        "event_link": None,
        "name": None,
        "place": "Columbus, Ohio",
        "player": "Jay Kristoff",
        "players_count": 25,
        "score": None,
        "tournament_format": None,
        "author": None,
        "raven": 2,
        "cards": collections.OrderedDict(
            [
                ("Mirembe Kabbada", 6),
                ("Camille Devereux, The Raven", 4),
                ("Chandler Hungerford", 2),
                ("Zoo Hunting Ground", 1),
                ("Ecoterrorists", 2),
                ("Powerbase: Montreal", 1),
                ("Club Zombie", 1),
                ("London Evening Star, Tabloid Newspaper", 1),
                ("KRCG News Radio", 1),
                ("The Rumor Mill, Tabloid Newspaper", 1),
                ("Backways", 1),
                ("Smiling Jack, The Anarch", 2),
                ("The Barrens", 1),
                ("Direct Intervention", 1),
                ("Sudden Reversal", 1),
                ("Earth Meld", 22),
                ("Forced Awakening", 12),
                ("Form of Mist", 6),
                ("Quick Meld", 6),
                ("Earth Control", 4),
                ("Form of Corruption", 3),
                ("Atonement", 3),
                ("Raven Spy", 3),
                ("Mr. Winthrop", 2),
                ("Renegade Garou", 2),
                ("Army of Rats", 2),
                ("Shadow of the Beast", 2),
                ("Temptation", 2),
                ("Arson", 2),
                ("Ecstasy", 2),
                ("Set's Call", 1),
                ("Tasha Morgan", 1),
                ("J. S. Simmons, Esq.", 1),
            ]
        ),
        "cards_comments": {},
        "comments": "I just got home from an amazing first day at Origins. I was able "
        "to\n"
        "eak out a tournament victory with my Mirembe Rides Again deck. "
        "25\n"
        "meths played in this event. 4 of the 5 finalists were from Ohio, "
        "the\n"
        "other was Halcyan2 who is from somewhere in Illinois.\n"
        "I'm sure details on this and the other events will follow. It's\n"
        "bed time for me, so here is the deck:\n"
        "\n"
        "Mirembe Rides Again!\n"
        "by Jay Kristoff - jck@columbus.rr.com\n",
    }
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
    # for now, Camille / Raven do not show as separated entries in the dict version
    # it would seem a bit old to have two cards with the same ID there
    assert TWDA["2k2origins1"].to_dict() == {
        "twda_id": "2k2origins1",
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
                {"count": 6, "id": "200994", "name": "Mirembe Kabbada"},
                {"count": 4, "id": "200240", "name": "Camille Devereux, The Raven"},
                {"count": 2, "id": "200265", "name": "Chandler Hungerford"},
            ],
        },
        "library": {
            "count": 90,
            "cards": [
                {
                    "type": "Master",
                    "count": 14,
                    "cards": [
                        {"count": 1, "id": "100126", "name": "Backways"},
                        {"count": 1, "id": "100135", "name": "The Barrens"},
                        {"count": 1, "id": "100367", "name": "Club Zombie"},
                        {"count": 1, "id": "100545", "name": "Direct Intervention"},
                        {"count": 2, "id": "100609", "name": "Ecoterrorists"},
                        {"count": 1, "id": "101067", "name": "KRCG News Radio"},
                        {
                            "count": 1,
                            "id": "101120",
                            "name": "London Evening Star, Tabloid " "Newspaper",
                        },
                        {"count": 1, "id": "101439", "name": "Powerbase: Montreal"},
                        {
                            "count": 1,
                            "id": "101662",
                            "name": "The Rumor Mill, Tabloid Newspaper",
                        },
                        {
                            "count": 2,
                            "id": "101811",
                            "name": "Smiling Jack, The Anarch",
                        },
                        {"count": 1, "id": "101896", "name": "Sudden Reversal"},
                        {"count": 1, "id": "102212", "name": "Zoo Hunting Ground"},
                    ],
                },
                {
                    "type": "Action",
                    "count": 14,
                    "cards": [
                        {"count": 2, "id": "100093", "name": "Army of Rats"},
                        {"count": 2, "id": "100094", "name": "Arson"},
                        {"count": 3, "id": "100109", "name": "Atonement"},
                        {"count": 3, "id": "100770", "name": "Form of Corruption"},
                        {"count": 2, "id": "101740", "name": "Shadow of the Beast"},
                        {"count": 2, "id": "101954", "name": "Temptation"},
                    ],
                },
                {
                    "type": "Ally",
                    "count": 2,
                    "cards": [{"count": 2, "id": "101602", "name": "Renegade Garou"}],
                },
                {
                    "type": "Retainer",
                    "count": 7,
                    "cards": [
                        {"count": 1, "id": "101015", "name": "J. S. Simmons, Esq."},
                        {"count": 2, "id": "101249", "name": "Mr. Winthrop"},
                        {"count": 3, "id": "101550", "name": "Raven Spy"},
                        {"count": 1, "id": "101943", "name": "Tasha Morgan"},
                    ],
                },
                {
                    "type": "Action Modifier",
                    "count": 4,
                    "cards": [{"count": 4, "id": "100600", "name": "Earth Control"}],
                },
                {
                    "type": "Reaction",
                    "count": 15,
                    "cards": [
                        {"count": 2, "id": "100610", "name": "Ecstasy"},
                        {"count": 12, "id": "100760", "name": "Forced Awakening"},
                        {"count": 1, "id": "101730", "name": "Set's Call"},
                    ],
                },
                {
                    "type": "Combat",
                    "count": 34,
                    "cards": [
                        {"count": 22, "id": "100601", "name": "Earth Meld"},
                        {"count": 6, "id": "100771", "name": "Form of Mist"},
                        {"count": 6, "id": "101530", "name": "Quick Meld"},
                    ],
                },
            ],
        },
    }
    assert caplog.record_tuples == []


def test_2k8TempleConcordance(caplog):
    """Multiline comments with card names inside decklist"""
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(
        os.path.join(os.path.dirname(__file__), "2k8TempleConcordance.html")
    ) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2k8TempleConcordance"].__getstate__() == {
        "date": "2008-02-01",
        "event": "TempleConcordance",
        "event_link": None,
        "id": "2k8TempleConcordance",
        "name": "Howling Anarchs",
        "place": "Providence, Rhode Island",
        "player": "Matt Morgan",
        "players_count": 12,
        "raven": 0,
        "score": None,
        "tournament_format": "2R+F",
        "author": None,
        "cards": collections.OrderedDict(
            [
                ("Howler", 4),
                ("The Siamese", 2),
                ("Cynthia Ingold", 1),
                ("Nettie Hale", 1),
                ("Bobby Lemon", 1),
                ("Juanita Santiago", 1),
                ("Dani", 1),
                ("Gillian Krader", 1),
                ("The Anarch Free Press", 1),
                ("Anarch Revolt", 4),
                ("Animalism", 1),
                ("Direct Intervention", 2),
                ("Fame", 1),
                ("Giant's Blood", 1),
                ("Guardian Angel", 1),
                ("The Rack", 1),
                ("Seattle Committee", 1),
                ("Smiling Jack, The Anarch", 1),
                ("Vessel", 5),
                ("Aranthebes, The Immortal", 1),
                ("Enchant Kindred", 6),
                ("Nose of the Hound", 4),
                ("Swiftness of the Stag", 5),
                ("Flak Jacket", 1),
                ("Dragonbound", 1),
                ("Cats' Guidance", 4),
                ("Falcon's Eye", 4),
                ("On the Qui Vive", 3),
                ("Sense the Savage Way", 3),
                ("Speak with Spirits", 8),
                ("Murder of Crows", 6),
                ("Owl Companion", 1),
                ("Raven Spy", 4),
                ("Aid from Bats", 5),
                ("Canine Horde", 2),
                ("Carrion Crows", 3),
                ("Pack Alpha", 8),
                ("Taste of Vitae", 2),
            ]
        ),
        "cards_comments": {},
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
            '[    80][2k8TempleConcordance] discarded match "Ash Harrison" inside '
            'comment "Flash Harrison. */"',
        ),
    ]
