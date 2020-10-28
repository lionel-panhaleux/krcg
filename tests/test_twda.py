import collections
import logging
import os.path
import textwrap

from krcg import twda


def test_get_card():
    assert twda._get_card("deny") == ("deny", 1, False, "")
    assert twda._get_card("2 deny") == ("deny", 2, True, "")
    assert twda._get_card("deny 2") == ("deny", 2, False, "")
    assert twda._get_card("2x deny") == ("deny", 2, True, "")
    assert twda._get_card("2 x deny") == ("deny", 2, True, "")
    # 'x' is usually separated from card name, but '*' may not be
    assert twda._get_card("2*deny") == ("deny", 2, True, "")
    assert twda._get_card("deny *2") == ("deny", 2, True, "")
    assert twda._get_card("deny x2") == ("deny", 2, True, "")
    assert twda._get_card("deny x 2") == ("deny", 2, True, "")
    assert twda._get_card("deny (2)") == ("deny", 2, False, "")
    assert twda._get_card("deny [2]") == ("deny", 2, False, "")
    # many forms are used, with or without parenthesis, 'x', '=', etc.
    assert twda._get_card("deny (x2)") == ("deny", 2, True, "")
    assert twda._get_card("deny =2") == ("deny", 2, False, "")
    assert twda._get_card("deny /2") == ("deny", 2, False, "")
    # spurious tail: multiple cards with post count on the same line
    assert twda._get_card("deny x2, confusion x4") == (
        "deny",
        2,
        True,
        ", confusion x4",
    )
    # crypt needs special handling as we got a number in front and back
    text = "2x anvil			6   cel pot dom pre tha	 primogen  brujah:1"
    assert twda._get_card(text) == (
        "anvil",
        2,
        True,
        "",
    )
    # names beginning with an 'x' and parenthesied '(adv)' must be correctly matched
    assert twda._get_card(
        "2x xaviar (adv)		10  abo ani for pro aus cel pot	 gangrel:3"
    ) == ("xaviar (adv)", 2, True, "")
    # names with a comman and parenthesied '(adv)' must be correctly matched
    assert twda._get_card(
        "5x sascha vykos, the angel of caine (adv) 8   "
        "aus tha vic ani dom  archbishop	tzimisce:2"
    ) == (
        "sascha vykos, the angel of caine (adv)",
        5,
        True,
        "",
    )
    # names beginning with a number are hard
    assert twda._get_card("2nd tradition") == ("2nd tradition", 1, False, "")
    # name ending with a number even harder
    assert twda._get_card("ak-47") == ("ak-47", 1, False, "")
    # channel 10 is unique: other cards will match 10 as the count
    assert twda._get_card("channel 10") == ("channel 10", 1, False, "")
    # pier 13 is hard to match fully, note there is no ',' atter card counts
    assert twda._get_card("2 pier 13, port of baltimore") == (
        "pier 13, port of baltimore",
        2,
        True,
        "",
    )
    # local 1111 is hard, card counts have less than 3 digits
    assert twda._get_card("local 1111 2") == ("local 1111", 2, False, "")
    assert twda._get_card("1x alia, god=92s messenger") == (
        "alia, god=92s messenger",
        1,
        True,
        "",
    )


def test_2019grdojf(caplog):
    """Recent classic layout, we must get everything seamlessly"""
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2019grdojf.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2019grdojf"].__getstate__() == {
        "date": "June 29th 2019",
        "event": "Garou Rim: Dawn Operation",
        "event_link": "http://www.vekn.net/event-calendar/event/9292",
        "place": "Joensuu, Finland",
        "players_count": 10,
        "player": "Esa-Matti Smolander",
        "tournament_format": "3R+F",
        "score": "1gw3.5 + 4vp in the final",
        "name": "Parliament of Shadows precon with no changes.",
        "author": None,
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
        "event": "Gothcon",
        "event_link": None,
        "place": "Goteborg, Sweden",
        "date": "March 26th 2016",
        "players_count": 16,
        "player": "Hugh Angseesing",
        "tournament_format": "3R+F",
        "score": None,
        "name": "DoC Swedish Sirens",
        "author": None,
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
            "Description : 2GW9 and winner in Sweden qualifier 26th March 2016\n"
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
        "event": "Spanish NCQ",
        "event_link": None,
        "place": "Alboraya (Valencia), Spain",
        "date": "February 12th 2005",
        "players_count": 34,
        "player": "Jose Vicente Coll",
        "tournament_format": "3R+F",
        "score": None,
        "name": None,
        "author": None,
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
        "event": "Atlantic Regional Qualifier",
        "event_link": None,
        "place": "Washington, D.C.",
        "date": "June 12th 2004",
        "players_count": 33,
        "player": "Matt Morgan",
        "tournament_format": None,
        "score": None,
        "name": "Call me Julio",
        "author": None,
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
    assert caplog.record_tuples == []


def test_2010tcdbng(caplog):
    """Card-level parenthesised commends (common)"""
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2010tcdbng.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2010tcdbng"].__getstate__() == {
        "event": "Trading Card Day",
        "event_link": None,
        "place": "Bad Naumheim, Germany",
        "date": "May 8th 2010",
        "players_count": 10,
        "player": "Rudolf Scholz",
        "tournament_format": "2R+F",
        "score": "4vp in the final",
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
            "Conditioning": "should be more!\n",
            "Flash Grenade": (
                "brings fear to the methuselahs rather than to minions\n"
            ),
            "Storage Annex": "great card! usually underestimated\n",
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
        "event": "Praxis Seizure: Leiria",
        "event_link": None,
        "place": "Leiria, Portugal",
        "date": "October 13th 2012",
        "players_count": 12,
        "player": "Patrick Gordo",
        "tournament_format": "2R+F",
        "score": None,
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
        "event": "Campeonato Juizforano 2007",
        "event_link": None,
        "place": "Juiz de Fora, Brazil",
        "date": "December 16th 2007",
        "players_count": 23,
        "player": "Pedro Paulo de Sousa Mendes (Pepê)",
        "tournament_format": None,
        "score": None,
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
                "saved me a lot of times, unfortunately\n"
                "I couldn't pack more than one.\n"
            ),
            "Millicent Smith, Puritan Vampire Hunter": "no comments needed.\n",
            "The Slaughterhouse": (
                "useful either to speed deck depletion\n"
                "or to trade for something useful under Anthelios.\n"
            ),
            "Smiling Jack, The Anarch": "crucial contest in the final table.\n",
            "Vigilance": "i started to win a game when i had those three in play.\n",
            "Wash": (
                "not as effective as i expected, but also not a hassle\n"
                "because it's trifle.\n"
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
    assert caplog.record_tuples == []


def test_2010pwbla1(caplog):
    """Very hard to parse comments (line braks, few markers)"""
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2010pwbla1.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2010pwbla1"].__getstate__() == {
        "event": "Powerbase: Los Angeles Event #1",
        "event_link": None,
        "place": "Strategicon - GAMEX 2010, Los Angeles, California",
        "date": "May 29th 2010",
        "players_count": 12,
        "player": "Darby Keeney",
        "tournament_format": "2R+F",
        "score": None,
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
            "The Sargon Fragment": "recycle everything else\n",
            "Secure Haven": "to contest and to save a slave master.\n",
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

            a "good" combat ran "set close and agg hands, grapple, prevent and
            untap"
            """
        )[1:],
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
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2k5sharednun"].__getstate__() == {
        "event": "Shared Nightmare",
        "event_link": None,
        "place": "Utrecht, Netherlands",
        "date": "July 2nd 2005",
        "players_count": 16,
        "player": "Jeroen van Oort",
        "tournament_format": "3R+F",
        "score": None,
        "name": "Deeper Underground",
        "author": None,
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
        "comments": "Description:\n\"Look in the sky, it's a raven. No, it's a bat.\n"
        "No, it's a crow, No it's a swarm of them all!!!\"\n",
    }
    assert caplog.record_tuples == [
        ("krcg", logging.WARNING, "[    40] improper discipline [Obfuscate 17]"),
        ("krcg", logging.WARNING, "[    47] improper discipline [Animalism: 37]"),
        ("krcg", logging.WARNING, "[    58] failed to parse [Non-skilled: 22]"),
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
        "event": "EC WoN - Monday",
        "event_link": "http://www.vekn.net/event-calendar/event/9321",
        "place": "Paris, France",
        "date": "August 12th 2019",
        "players_count": 25,
        "player": "Randal Rudstam",
        "tournament_format": "2R+F",
        "score": "1gw4.5 + 1.5vp in the final",
        "name": "Sascha Vykos Toolbox",
        "author": None,
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
    Using long vampire name with comma and (ADV)
    """
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2020pihc.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2020pihc"].__getstate__() == {
        "event": "Personal Involvement",
        "event_link": "http://www.vekn.net/event-calendar/event/9566",
        "place": "Hamilton, Canada",
        "date": "February 22nd 2020",
        "player": "Jay Kristoff",
        "players_count": 10,
        "tournament_format": "2R+F",
        "score": "0gw2.5 + 1.5vp in the final",
        "author": None,
        "name": "Sauce or GTFO",
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
            "[   134] Deck #2020pihc has too few cards (59) [Sauce or GTFO]",
        ),
    ]


def test_2k8sequeenslandcq(caplog):
    """Discipline name as header must not be mistaken for the Master card
    Using long vampire name with comma and (ADV)
    """
    caplog.set_level(logging.WARNING)
    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "2k8sequeenslandcq.html")) as f:
        TWDA.load_html(f, save=False)
    assert len(TWDA) == 1
    assert TWDA["2k8sequeenslandcq"].__getstate__() == {
        "event": "Gencon SE Queensland CCQ",
        "event_link": None,
        "place": "Gencon Australia, Brisbane, Australia",
        "date": "July 5th 2008",
        "player": "Steven McRoy",
        "players_count": 13,
        "tournament_format": None,
        "score": None,
        "author": None,
        "name": "Arika Turbo",
        "cards": collections.OrderedDict(
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
                ("Praxis Seizure: Geneva", 4),
                ("Forgotten Labyrinth", 5),
                ("Elder Impersonation", 3),
                ("Seduction", 2),
            ]
        ),
        "cards_comments": {"Arika": "could have more, 15 was enough\n"},
        "comments": """Comments: Well the run is you get Arika out, wait a turn
hopefully no pentex, smash, or her getting torped), next
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
""",
    }
    assert caplog.record_tuples == [
        (
            "krcg",
            logging.WARNING,
            "[    24] spurious tail [, berlin x4, cairo x2] - "
            "[Praxis Seizure: Geneva x4, Berlin x4, Cairo x2]",
        ),
        (
            "krcg",
            logging.WARNING,
            "[    25] spurious tail [would add one more] - "
            "[Forgotten Labyrinth x5 (would add one more)]",
        ),
        (
            "krcg",
            logging.WARNING,
            "[    26] spurious tail [would exchange for faceless night x4] - "
            "[Elder Impersonation x3 (would exchange for Faceless Night x4]",
        ),
        (
            "krcg",
            logging.WARNING,
            "[    27] spurious tail [would delete] - [Seduction x2 (would delete)]",
        ),
        (
            "krcg",
            logging.WARNING,
            "[    44] failed to parse [repeat until you have wiped everyone out]",
        ),
    ]
