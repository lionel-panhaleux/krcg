import logging

from krcg import deck
from krcg import vtes
from krcg import parser

import pytest


def check_comment(p, comment=None, card=None):
    if comment:
        assert p.current_comment.string == comment
        if card:
            assert p.current_comment.card == card
        p.current_comment = None
    else:
        assert p.current_comment is None


def test_get_card(caplog: pytest.LogCaptureFixture):
    caplog.set_level(logging.DEBUG)
    p = parser.Parser(deck.Deck())

    # basic match
    assert p.get_card("2x deny") == (vtes.VTES["Deny"], 2)
    assert p.get_card("2xx deny") == (vtes.VTES["Deny"], 2)
    assert p.get_card("x2 deny") == (vtes.VTES["Deny"], 2)
    assert p.get_card("xx2 deny") == (vtes.VTES["Deny"], 2)
    assert p.get_card("2* deny") == (vtes.VTES["Deny"], 2)
    assert p.get_card("2*deny") == (vtes.VTES["Deny"], 2)
    assert p.get_card("2 deny") == (vtes.VTES["Deny"], 2)
    assert p.get_card("*2 deny") == (vtes.VTES["Deny"], 2)
    assert p.get_card("deny") == (vtes.VTES["Deny"], 1)
    # post count
    assert p.get_card("deny 2") == (vtes.VTES["Deny"], 2)
    assert p.get_card("deny *2") == (vtes.VTES["Deny"], 2)
    assert p.get_card("deny x2") == (vtes.VTES["Deny"], 2)
    assert p.get_card("deny x2,") == (vtes.VTES["Deny"], 2)
    assert p.get_card("deny x 2") == (vtes.VTES["Deny"], 2)
    assert p.get_card("deny - 2") == (vtes.VTES["Deny"], 2)
    assert p.get_card("deny -- 2") == (vtes.VTES["Deny"], 2)
    assert p.get_card("deny (2)") == (vtes.VTES["Deny"], 2)
    assert p.get_card("deny (x2)") == (vtes.VTES["Deny"], 2)
    assert p.get_card("deny [2]") == (vtes.VTES["Deny"], 2)
    assert p.get_card("deny =2") == (vtes.VTES["Deny"], 2)
    assert p.get_card("deny / 2") == (vtes.VTES["Deny"], 2)
    assert p.get_card("deny // 2") == (vtes.VTES["Deny"], 2)
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
    assert p.get_card("carlton van wyk (hunter)") == (vtes.VTES["Carlton Van Wyk"], 1)
    assert p.get_card("ohoyo hopoksia (bastet)") == (
        vtes.VTES["Ohoyo Hopoksia (Bastet)"],
        1,
    )
    # clan, discipline and trifle are often found
    caplog.clear()
    assert p.get_card("art museum     toreador") == (vtes.VTES["Art Museum"], 1)
    assert p.get_card("villein     trifle") == (vtes.VTES["Villein"], 1)
    assert p.get_card("3x conditioning     dominate") == (vtes.VTES["Conditioning"], 3)
    # disciplines are a particularily difficult case: if properly counted, ok
    assert p.get_card("3x dominate") == (vtes.VTES["Dominate"], 3)
    # post count and mentions by default are parsed as cards
    assert p.get_card("dominate") == (vtes.VTES["Dominate"], 1)
    assert p.get_card("dominate (4)") == (vtes.VTES["Dominate"], 4)
    assert caplog.record_tuples == [
        ("krcg", logging.DEBUG, 'naked discipline (no count) "dominate"'),
        ("krcg", logging.DEBUG, 'naked discipline (no count) "dominate (4)"'),
    ]
    # but don't mess with Valeren
    assert p.get_card("6x touch of valeren") == (vtes.VTES["Touch of Valeren"], 6)
    # post counts and naked mention should be ignored and logged in TWDA:
    # we can't decide if they're header or actual discipline cards inclusions
    caplog.clear()
    assert p.get_card("dominate", twda=True) == (None, 0)
    assert p.get_card("dominate (4)", twda=True) == (None, 0)
    assert caplog.record_tuples == [
        ("krcg", logging.WARNING, 'improper discipline "dominate"'),
        ("krcg", logging.WARNING, 'improper discipline "dominate (4)"'),
    ]
    # specific card names containing numbers
    assert p.get_card("ak-47") == (vtes.VTES["AK-47"], 1)
    assert p.get_card("kpist m/45") == (vtes.VTES["Kpist m/45"], 1)
    assert p.get_card("pier 13, port of baltimore") == (
        vtes.VTES["Pier 13, Port of Baltimore"],
        1,
    )
    assert p.get_card("pier 13 port of baltimore") == (
        vtes.VTES["Pier 13, Port of Baltimore"],
        1,
    )
    assert p.get_card("419 operation") == (vtes.VTES["419 Operation"], 1)
    assert p.get_card("1x Mask of 1000 Faces") == (
        vtes.VTES["Mask of a Thousand Faces"],
        1,
    )

    # crypt needs special handling as we got a number in front and back
    assert p.get_card("2x anvil		6   cel pot dom pre tha	 primogen  brujah:1") == (
        vtes.VTES["Anvil"],
        2,
    )
    # names beginning with an 'x' and parenthesied '(adv)' must be correctly matched
    assert p.get_card(
        "2x xaviar (adv)		10  abo ani for pro aus cel pot	 gangrel:3"
    ) == (vtes.VTES["Xaviar (ADV)"], 2)
    # names with a comma and parenthesied '(adv)' must be correctly matched
    assert p.get_card(
        "5x sascha vykos, the angel of caine (adv) 8   "
        "aus tha vic ani dom  archbishop	tzimisce:2"
    ) == (vtes.VTES["Sascha Vykos, The Angel of Caine (ADV)"], 5)

    caplog.clear()
    # names beginning with a number are hard
    assert p.get_card("2nd tradition") == (vtes.VTES["Second Tradition: Domain"], 1)
    check_comment(p)
    # name ending with a number even harder
    assert p.get_card("ak-47") == (vtes.VTES["AK-47"], 1)
    check_comment(p)
    # channel 10 is unique: other cards will match 10 as the count
    assert p.get_card("channel 10") == (vtes.VTES["Channel 10"], 1)
    check_comment(p)
    # card names with numbers are tricky
    assert p.get_card("pier 13, port of baltimore") == (
        vtes.VTES["Pier 13, Port of Baltimore"],
        1,
    )
    check_comment(p)
    assert p.get_card("local 1111 2") == (vtes.VTES["Local 1111"], 2)
    check_comment(p)
    assert p.get_card("419 operation") == (vtes.VTES["419 Operation"], 1)
    check_comment(p)
    assert p.get_card("bang nakh -- tiger's claws") == (
        vtes.VTES["Bang Nakh — Tiger's Claws"],
        1,
    )
    check_comment(p)
    # quote encoding may be an issue
    assert p.get_card("1x alia, god=92s messenger") == (
        vtes.VTES["Alia, God's Messenger"],
        1,
    )
    check_comment(p)

    # cards with a clan / virtue / discipline in the name
    assert p.get_card("create gargoyle") == (vtes.VTES["Create Gargoyle"], 1)
    check_comment(p)
    assert p.get_card("shepherd's innocence") == (vtes.VTES["Shepherd's Innocence"], 1)
    check_comment(p)
    assert p.get_card("return to innocence") == (
        vtes.VTES["The Return to Innocence"],
        1,
    )
    check_comment(p)
    assert p.get_card("joseph pander") == (vtes.VTES["Joseph Pander"], 1)
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
    assert p.get_card("2x deny  -- this is a comment") == (vtes.VTES["Deny"], 2)
    check_comment(p, "this is a comment", vtes.VTES["Deny"])
    assert p.get_card("2x deny  // this is a comment") == (vtes.VTES["Deny"], 2)
    check_comment(p, "this is a comment", vtes.VTES["Deny"])
    assert p.get_card("2x deny  /* this is a comment */") == (vtes.VTES["Deny"], 2)
    check_comment(p, "this is a comment", vtes.VTES["Deny"])

    # parenthesised comments are common and should be handled
    # they can start by a number, not to be confused with a count for cards
    assert p.get_card("deny (2 would have been better)") == (vtes.VTES["Deny"], 1)
    check_comment(p, "2 would have been better")

    # multiline card comment
    assert p.get_card("2x deny  /* this is a comment ") == (vtes.VTES["Deny"], 2)
    assert p.get_card("        it spans multiple lines") == (None, 0)
    check_comment(p, "this is a comment\n" "        it spans multiple lines")

    # poorly marked multiline comment
    caplog.clear()
    assert p.get_card("2x deny  -- this is a comment ") == (vtes.VTES["Deny"], 2)
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
    assert p.get_card("1x deny") == (vtes.VTES["Deny"], 1)
    assert p.get_card("(this is a comment)") == (None, 0)
    assert p.get_card("1x deny") == (vtes.VTES["Deny"], 1)
    assert caplog.record_tuples == []

    # clan, discipline and trifle are not comments
    assert p.get_card("art museum     toreador") == (vtes.VTES["Art Museum"], 1)
    assert p.get_card("villein     trifle") == (vtes.VTES["Villein"], 1)
    assert p.get_card("3x conditioning     dominate") == (vtes.VTES["Conditioning"], 3)
    check_comment(p)

    # but outside preface, a lonely discipline is undecidable when parsing TWDA:
    # log a warning
    caplog.clear()
    assert p.get_card("dominate", twda=True) == (None, 0)
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
