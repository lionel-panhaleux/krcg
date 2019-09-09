import collections
import os.path
import textwrap

from src import twda


def test_get_card():
    assert twda._get_card("deny") == ("deny", 1)
    assert twda._get_card("2 deny") == ("deny", 2)
    assert twda._get_card("deny 2") == ("deny", 2)
    assert twda._get_card("2x deny") == ("deny", 2)
    assert twda._get_card("2 x deny") == ("deny", 2)
    # 'x' is usually separated from card name, but '*' may not be
    assert twda._get_card("2*deny") == ("deny", 2)
    assert twda._get_card("deny *2") == ("deny", 2)
    assert twda._get_card("deny x2") == ("deny", 2)
    assert twda._get_card("deny x 2") == ("deny", 2)
    assert twda._get_card("deny (2)") == ("deny", 2)
    assert twda._get_card("deny [2]") == ("deny", 2)
    # many forms are used, with or without parenthesis, 'x', '=', etc.
    assert twda._get_card("deny (x2)") == ("deny", 2)
    assert twda._get_card("deny =2") == ("deny", 2)
    assert twda._get_card("deny /2") == ("deny", 2)
    # crypt needs special handling as we got a number in front and back
    text = "2x anvil			6   cel pot dom pre tha	 primogen  brujah:1"
    assert twda._get_card(text) == ("anvil", 2)
    # names beginning with an 'x' and parenthesied '(adv)' must be correctly matched
    assert twda._get_card(
        "2x xaviar (adv)		10  abo ani for pro aus cel pot	 gangrel:3"
    ) == ("xaviar (adv)", 2)
    # names beginning with a number are hard
    assert twda._get_card("2nd tradition") == ("2nd tradition", 1)
    # name ending with a number even harder
    assert twda._get_card("ak-47") == ("ak-47", 1)
    # channel 10 is unique: other cards will match 10 as the count
    assert twda._get_card("channel 10") == ("channel 10", 1)
    # pier 13 is hard to match fully, note there is no ',' atter card counts
    assert twda._get_card("2 pier 13, port of baltimore") == (
        "pier 13, port of baltimore",
        2,
    )
    # local 1111 is hard, card counts have less than 3 digits
    assert twda._get_card("local 1111 2") == ("local 1111", 2)
    assert twda._get_card("1x alia, god=92s messenger") == (
        "alia, god=92s messenger",
        1,
    )


def test_2k4dcqualifier():
    """A lot of comments, in description, at the end, plus inline C-style card comment
    """
    with open(os.path.join(os.path.dirname(__file__), "2k4dcqualifier.html")) as f:
        twda.TWDA.load_html(f)
    assert len(twda.TWDA) == 1
    assert twda.TWDA["2k4dcqualifier"].__getstate__() == {
        "event": "Atlantic Regional Qualifier",
        "place": "Washington, D.C.",
        "date": "June 12th 2004",
        "players_count": 33,
        "player": "Matt Morgan",
        "tournament_format": None,
        "name": "Call me Julio",
        "author": None,
        "comments": textwrap.dedent(
            """
    POT/DOM is always good.  Let's add permanent rush, +strength,
    Nosferatu Kingdom and a bad attitude!

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
    is nearly as good, right?
    """
            )[1:],
            "Blood Doll": "Not enough unless you're lucky (like I was).\n",
            "Govern the Unaligned": "Almost always played superior.\n",
            "Conditioning": ("Because Colin said it was a good idea (he's right).\n"),
            "Information Network": "Played it, but never tapped it.\n",
            "Nosferatu Kingdom": (
                "Absolutely essential.  Always got one after the other, though.\n"
            ),
            "Wake with Evening's Freshness": (
                "Replace one with Mylan Horseed as soon as Gehenna is legal.\n"
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


def test_2010tcdbng():
    """Card-level parenthesised commends (common)
    """
    with open(os.path.join(os.path.dirname(__file__), "2010tcdbng.html")) as f:
        twda.TWDA.load_html(f)
    assert len(twda.TWDA) == 1
    assert twda.TWDA["2010tcdbng"].__getstate__() == {
        "event": "Trading Card Day",
        "place": "Bad Naumheim, Germany",
        "date": "May 8th 2010",
        "players_count": 10,
        "player": "Rudolf Scholz",
        "tournament_format": "2R+F",
        "name": "The Storage Procurers",
        "author": None,
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
                ("Unmasking, The", 1),
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
            "Conditioning": "should be more!\n",
            "Flash Grenade": (
                "brings fear to the methuselahs rather than to minions\n"
            ),
            "Storage Annex": "great card! usually underestimated\n",
        },
        "comments": textwrap.dedent(
            """
    4vp in final
    Allies with Flash Grenades to keep troubles at bay.
    Storage Annex for card efficiency and a structured hand. Weenies and
    Midcaps with Obfuscate and/or Dominate to oust via Conditionings and
    Deflections.
    """
        )[1:],
    }


def test_2012pslp():
    """Discipline included after card names (common)
    """
    with open(os.path.join(os.path.dirname(__file__), "2012pslp.html")) as f:
        twda.TWDA.load_html(f)
    assert len(twda.TWDA) == 1
    assert twda.TWDA["2012pslp"].__getstate__() == {
        "event": "Praxis Seizure: Leiria",
        "place": "Leiria, Portugal",
        "date": "October 13th 2012",
        "players_count": 12,
        "player": "Patrick Gordo",
        "tournament_format": "2R+F",
        "name": "Shadowfang",
        "author": None,
        "cards": collections.OrderedDict(
            [
                ("Morel", 3),
                ("Gem Ghastly", 2),
                ("Hagar Stone", 2),
                ("Arthur Denholm", 2),
                ("Drusilla Euphemia", 1),
                ("Apache Jones", 1),
                ("Bela", 1),
                ("Barrens, The", 1),
                ("Blood Doll", 1),
                ("Dreams of the Sphinx", 2),
                ("Giant's Blood", 1),
                ("Pentex(TM) Subversion", 1),
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
                ("Dementation", 3),
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


def test_2k7campeonatojuizforano():
    """Very hard to parse comments (line braks, few markers)
    """
    with open(
        os.path.join(os.path.dirname(__file__), "2k7campeonatojuizforano.html")
    ) as f:
        twda.TWDA.load_html(f)
    assert len(twda.TWDA) == 1
    assert twda.TWDA["2k7campeonatojuizforano"].__getstate__() == {
        "event": "Campeonato Juizforano 2007",
        "place": "Juiz de Fora, Brazil",
        "date": "December 16th 2007",
        "players_count": 23,
        "player": "Pedro Paulo de Sousa Mendes (Pepê)",
        "tournament_format": None,
        "name": "Imbued at Last",
        "author": None,
        "cards": collections.OrderedDict(
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
                ("Crusader Sword, The", 1),
                ("Heart of Nizchetus", 1),
                ("Ivory Bow", 1),
                ("Anthelios, The Red Star", 1),
                ("Edge Explosion", 1),
                ("Unmasking, The", 1),
                ("Angel of Berlin", 2),
                ("Barrens, The", 1),
                ("Church of Vindicated Faith, The", 1),
                ("Direct Intervention", 1),
                ("Fortschritt Library", 1),
                ("Memories of Mortality", 6),
                ("Millicent Smith, Puritan Vampire Hunter", 1),
                ("Parthenon, The", 3),
                ("Rötschreck", 1),
                ("Slaughterhouse, The", 4),
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
                "saved me a lot of times, unfortunately\n"
                "I couldn't pack more than one.\n"
            ),
            "Ivory Bow": (
                "Heart is no good when it shows up late, but this is a small price\n"
                "to pay when compared to how good it is when I draw it early (it was\n"
                "decisive in the final table).\n"
            ),
            "Millicent Smith, Puritan Vampire Hunter": "no comments needed\n",
            "Slaughterhouse, The": (
                "useful either to speed deck depletion\n"
                "or to trade for something useful under Anthelios.\n"
            ),
            "Smiling Jack, The Anarch": "crucial contest in the final table\n",
            "Strike with Conviction": "It was enough. I never needed more than this.\n",
            "Unmasking, The": (
                "I only packed the extremely necessary events, so I wouldn't draw\n"
                "any extra table hate, and was lucky enough to put all 3 in play in\n"
                "every game. The decks runs wonderfully with those 3 on the table.\n"
            ),
            "Vigilance": "i started to win a game when i had those three in play\n",
            "Wash": (
                "not as effective as i expected, but also not a hassle\n"
                "because it's trifle.\n"
            ),
        },
        "comments": textwrap.dedent(
            """
            The deck's goal is to setup as fast as you can by
            depleting your library and to use Unity/Anthelios to cycle back
            whatever master you need the most at the time.
            """
        )[1:],
    }


def test_2010pwbla1():
    """Very hard to parse comments (line braks, few markers)
    """
    with open(os.path.join(os.path.dirname(__file__), "2010pwbla1.html")) as f:
        twda.TWDA.load_html(f)
    assert len(twda.TWDA) == 1
    assert twda.TWDA["2010pwbla1"].__getstate__() == {
        "event": "Powerbase: Los Angeles Event #1",
        "place": "Strategicon - GAMEX 2010, Los Angeles, California",
        "date": "May 29th 2010",
        "players_count": 12,
        "player": "Darby Keeney",
        "tournament_format": "2R+F",
        "name": "[2010 TW] The World's Biggest Small Multirushers",
        "author": None,
        "cards": collections.OrderedDict(
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
                ("Sargon Fragment, The", 1),
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
                'eradicate your prey and call as a "spare"\n' "Tupdog action\n"
            ),
            "As the Crow": "makes my Tuppers freaky.\n",
            "Ashur Tablets": "tune late-game combat as needed.\n",
            "Carver's Meat Packing and Storage": "anti-weenie.\n",
            "Dive Bomb": 'stealth multi-rush as a "spare" Tupdog ' "action\n",
            "Dreams of the Sphinx": "combat support or free Tupdogs.\n",
            "Goblinism": 'destroy location as a "spare" Tupdog ' "action.\n",
            "Hand of Conrad": "recycle Tupdogs, should probably be " "duplicated.\n",
            "Lead Fist": 'critical to circumvent "prevent 1" decks\n',
            "Nephandus": "safe removal of torporized minions.\n",
            "Powerbase: Montreal": "free Tupdogs\n",
            "Raking Talons": "probably should be 10.\n",
            "Raw Recruit": 'additional slaves from a "spare" Tupdog ' "action.\n",
            "Reins of Power": (
                'eradicate your predator and call as a "spare"\n' "Tupdog action\n"
            ),
            "Sargon Fragment, The": "recycle everything else\n",
            "Secure Haven": "to contest and to save a slave master.\n",
            "Stonestrength": (
                'a "good" combat ran "set close and agg hands, grapple, prevent and\n'
                'untap"\n'
            ),
            "Thin-Blooded Seer": 'Tupdog "spare" actions.\n',
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
            """
        )[1:],
    }
