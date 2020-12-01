import logging

from krcg import deck
from krcg import parser


def check_comment(p, comment=None, card_name=None):
    if comment:
        assert p.current_comment.string == comment
        if card_name:
            assert p.current_comment.card_name == card_name
        p.current_comment = None
    else:
        assert p.current_comment is None


def test_get_card(caplog):
    p = parser.Parser(deck.Deck())

    # basic match
    assert p.get_card("2x deny") == ("Deny", 2)
    assert p.get_card("2xx deny") == ("Deny", 2)
    assert p.get_card("x2 deny") == ("Deny", 2)
    assert p.get_card("xx2 deny") == ("Deny", 2)
    assert p.get_card("2* deny") == ("Deny", 2)
    assert p.get_card("2*deny") == ("Deny", 2)
    assert p.get_card("2 deny") == ("Deny", 2)
    assert p.get_card("*2 deny") == ("Deny", 2)
    assert p.get_card("deny") == ("Deny", 1)
    # post count
    assert p.get_card("deny 2") == ("Deny", 2)
    assert p.get_card("deny *2") == ("Deny", 2)
    assert p.get_card("deny x2") == ("Deny", 2)
    assert p.get_card("deny x2,") == ("Deny", 2)
    assert p.get_card("deny x 2") == ("Deny", 2)
    assert p.get_card("deny - 2") == ("Deny", 2)
    assert p.get_card("deny -- 2") == ("Deny", 2)
    assert p.get_card("deny (2)") == ("Deny", 2)
    assert p.get_card("deny (x2)") == ("Deny", 2)
    assert p.get_card("deny [2]") == ("Deny", 2)
    assert p.get_card("deny =2") == ("Deny", 2)
    assert p.get_card("deny / 2") == ("Deny", 2)
    assert p.get_card("deny // 2") == ("Deny", 2)
    # headers are ignored
    caplog.clear()
    assert p.get_card("library (90)") == (None, 0)
    assert p.get_card("combat [15]") == (None, 0)
    assert p.get_card("combo [7]") == (None, 0)
    assert p.get_card("action (9):") == (None, 0)
    assert p.get_card("mod/combat (9)") == (None, 0)
    assert p.get_card("misc 12") == (None, 0)
    assert p.get_card("total: 90") == (None, 0)
    assert caplog.record_tuples == []
    # old-style trait in allies name are not comments
    assert p.get_card("carlton van wyk (hunter)") == ("Carlton Van Wyk", 1)
    assert p.get_card("ohoyo hopoksia (bastet)") == ("Ohoyo Hopoksia (Bastet)", 1)
    # clan, discipline and trifle are often found
    caplog.clear()
    assert p.get_card("art museum     toreador") == ("Art Museum", 1)
    assert p.get_card("villein     trifle") == ("Villein", 1)
    assert p.get_card("3x conditioning     dominate") == ("Conditioning", 3)
    # disciplines are a particularily difficult case: if properly counted, ok
    assert p.get_card("3x dominate") == ("Dominate", 3)
    # post counts and naked mention should be ignored and logged:
    # we can't decide if they're header or actual discipline cards inclusions
    assert p.get_card("dominate") == (None, 0)
    assert p.get_card("dominate (4)") == (None, 0)
    assert caplog.record_tuples == [
        ("krcg", logging.WARNING, 'improper discipline "dominate"'),
        ("krcg", logging.WARNING, 'improper discipline "dominate (4)"'),
    ]
    # specific card names containing numbers
    assert p.get_card("ak-47") == ("AK-47", 1)
    assert p.get_card("kpist m/45") == ("Kpist m/45", 1)
    assert p.get_card("pier 13, port of baltimore") == ("Pier 13, Port of Baltimore", 1)
    assert p.get_card("pier 13 port of baltimore") == ("Pier 13, Port of Baltimore", 1)
    assert p.get_card("419 operation") == ("419 Operation", 1)
    assert p.get_card("1x Mask of 1000 Faces") == ("Mask of a Thousand Faces", 1)

    # crypt needs special handling as we got a number in front and back
    assert p.get_card("2x anvil		6   cel pot dom pre tha	 primogen  brujah:1") == (
        "Anvil",
        2,
    )
    # names beginning with an 'x' and parenthesied '(adv)' must be correctly matched
    assert p.get_card(
        "2x xaviar (adv)		10  abo ani for pro aus cel pot	 gangrel:3"
    ) == ("Xaviar (ADV)", 2)
    # names with a comma and parenthesied '(adv)' must be correctly matched
    assert p.get_card(
        "5x sascha vykos, the angel of caine (adv) 8   "
        "aus tha vic ani dom  archbishop	tzimisce:2"
    ) == ("Sascha Vykos, The Angel of Caine (ADV)", 5)

    caplog.clear()
    # names beginning with a number are hard
    assert p.get_card("2nd tradition") == ("Second Tradition: Domain", 1)
    check_comment(p)
    # name ending with a number even harder
    assert p.get_card("ak-47") == ("AK-47", 1)
    check_comment(p)
    # channel 10 is unique: other cards will match 10 as the count
    assert p.get_card("channel 10") == ("Channel 10", 1)
    check_comment(p)
    # card names with numbers are tricky
    assert p.get_card("pier 13, port of baltimore") == (
        "Pier 13, Port of Baltimore",
        1,
    )
    check_comment(p)
    assert p.get_card("local 1111 2") == ("Local 1111", 2)
    check_comment(p)
    assert p.get_card("419 operation") == ("419 Operation", 1)
    check_comment(p)
    assert p.get_card("bang nakh -- tiger's claws") == ("Bang Nakh — Tiger's Claws", 1)
    check_comment(p)
    # quote encoding may be an issue
    assert p.get_card("1x alia, god=92s messenger") == ("Alia, God's Messenger", 1)
    check_comment(p)

    # cards with a clan / virtue / discipline in the name
    assert p.get_card("create gargoyle") == ("Create Gargoyle", 1)
    check_comment(p)
    assert p.get_card("shepherd's innocence") == ("Shepherd's Innocence", 1)
    check_comment(p)
    assert p.get_card("return to innocence") == ("The Return to Innocence", 1)
    check_comment(p)
    assert p.get_card("joseph pander") == ("Joseph Pander", 1)
    check_comment(p)
    assert caplog.record_tuples == []

    # should fail: multiple cards with post count on the same line
    # the line is registered as comment, nonce it reaches a blank line it should log
    caplog.clear()
    p.get_card("deny x2, confusion x4")
    p.get_card("")
    assert caplog.record_tuples == [
        ("krcg", logging.WARNING, 'failed to parse "deny x2, confusion x4"')
    ]


def test_comments(caplog):
    p = parser.Parser(deck.Deck())

    # proper line comments
    assert p.get_card("// this is a comment") == (None, 0)
    check_comment(p, "// this is a comment")
    assert p.get_card("-- this is a comment") == (None, 0)
    check_comment(p, "-- this is a comment")
    assert p.get_card("/* this is a comment */") == (None, 0)
    check_comment(p, "/* this is a comment */")

    # multiline comment
    assert p.get_card("/* this is a comment") == (None, 0)
    assert p.get_card("it spans multiple lines") == (None, 0)
    assert p.get_card("so it's a multiline comment") == (None, 0)
    check_comment(
        p,
        "/* this is a comment\n"
        "it spans multiple lines\n"
        "so it's a multiline comment",
    )

    # naked comments in the middle of nowhere happen a lot
    assert p.get_card("this is a comment") == (None, 0)
    check_comment(p, "this is a comment")
    # sometimes they refer to a card
    assert p.get_card("deny is a good card") == (None, 0)
    check_comment(p, "deny is a good card")
    # sometimes even with count
    assert p.get_card("2x deny is probably not enough") == (None, 0)
    check_comment(p, "2x deny is probably not enough")

    # basic card comment
    assert p.get_card("2x deny  -- this is a comment") == ("Deny", 2)
    check_comment(p, "this is a comment", "Deny")
    assert p.get_card("2x deny  // this is a comment") == ("Deny", 2)
    check_comment(p, "this is a comment", "Deny")
    assert p.get_card("2x deny  /* this is a comment */") == ("Deny", 2)
    check_comment(p, "this is a comment", "Deny")

    # parenthesised comments are common and should be handled
    # they can start by a number, not to be confused with a count for cards
    assert p.get_card("deny (2 would have been better)") == ("Deny", 1)
    check_comment(p, "2 would have been better")

    # multiline card comment
    assert p.get_card("2x deny  /* this is a comment ") == ("Deny", 2)
    assert p.get_card("        it spans multiple lines") == (None, 0)
    check_comment(p, "this is a comment\n" "        it spans multiple lines")

    # poorly marked multiline comment
    caplog.clear()
    assert p.get_card("2x deny  -- this is a comment ") == ("Deny", 2)
    assert p.get_card("        it spans multiple lines") == (None, 0)
    assert p.get_card("")
    assert caplog.record_tuples == [
        ("krcg", logging.WARNING, 'failed to parse "it spans multiple lines"')
    ]

    # properly marked single line comment
    caplog.clear()
    assert p.get_card("/* this is a comment */") == (None, 0)
    assert p.get_card("")
    assert caplog.record_tuples == []
    assert p.get_card("-- this is a comment") == (None, 0)
    assert p.get_card("")
    assert caplog.record_tuples == []
    assert p.get_card("1x deny") == ("Deny", 1)
    assert p.get_card("(this is a comment)") == (None, 0)
    assert p.get_card("1x deny") == ("Deny", 1)
    assert caplog.record_tuples == []

    # clan, discipline and trifle are not comments
    assert p.get_card("art museum     toreador") == ("Art Museum", 1)
    assert p.get_card("villein     trifle") == ("Villein", 1)
    assert p.get_card("3x conditioning     dominate") == ("Conditioning", 3)
    check_comment(p)

    # but outside preface, a lonely discipline is undecidable: log a warning
    caplog.clear()
    assert p.get_card("dominate") == (None, 0)
    check_comment(p)
    assert caplog.record_tuples == [("krcg", 30, 'improper discipline "dominate"')]


def test_preface(caplog):
    # common TWDA headers that should be ignored (reset parser for preface)
    p = parser.Parser(deck.Deck())
    assert p.get_card("Comment:") == (None, 0)
    assert p.get_card("Description:") == (None, 0)
    assert p.get_card("Crypt:") == (None, 0)
    assert p.get_card("---------------------------") == (None, 0)
    assert p.get_card("===========================") == (None, 0)
    check_comment(p)

    # in the preface, card names without a count should not be matched
    # in TWDA, crypt card come first and have a count prefix
    # in other formats (Lackey, Amaranth, JOL), count is always a prefix
    # in all cases a naked name before the decklist is part of a preface comment
    assert p.get_card("deny") == (None, 0)
    check_comment(p, "deny")
    # even discipline names
    caplog.clear()
    assert p.get_card("dominate") == (None, 0)
    check_comment(p, "dominate")
    assert caplog.record_tuples == []
