"""Test the decklist parser (line-level: counts, names, comments, disciplines)."""

import logging

import pytest

from krcg import models
from krcg import parser
from krcg import vtes


def gc(p: parser.Parser, VTES: vtes.VTES, line: str) -> tuple[models.Card | None, int]:
    """Parse a line and return it as a (resolved card | None, count) pair."""
    entry = p.get_card(line)
    return (VTES[entry.id], entry.count) if entry else (None, 0)


def check_comment(
    p: parser.Parser,
    VTES: vtes.VTES,
    comment: str | None = None,
    card: models.Card | None = None,
) -> None:
    """Assert the parser's pending comment (and optionally the card it targets)."""
    if comment:
        assert p.current_comment
        assert p.current_comment.string == comment
        if card:
            assert p.current_comment.card is not None
            assert VTES[p.current_comment.card.id] is card
        p.current_comment = None
    else:
        assert p.current_comment is None


def test_get_card(VTES: vtes.VTES, caplog: pytest.LogCaptureFixture) -> None:
    """Card name & count parsing across the many real-world spellings."""
    caplog.set_level(logging.DEBUG)
    p = parser.Parser(VTES._cards)

    # ante count, with assorted markers
    assert gc(p, VTES, "2x deny") == (VTES["Deny"], 2)
    assert gc(p, VTES, "2xx deny") == (VTES["Deny"], 2)
    assert gc(p, VTES, "x2 deny") == (VTES["Deny"], 2)
    assert gc(p, VTES, "xx2 deny") == (VTES["Deny"], 2)
    assert gc(p, VTES, "2* deny") == (VTES["Deny"], 2)
    assert gc(p, VTES, "2*deny") == (VTES["Deny"], 2)
    assert gc(p, VTES, "2 deny") == (VTES["Deny"], 2)
    assert gc(p, VTES, "*2 deny") == (VTES["Deny"], 2)
    assert gc(p, VTES, "deny") == (VTES["Deny"], 1)
    # post count
    assert gc(p, VTES, "deny 2") == (VTES["Deny"], 2)
    assert gc(p, VTES, "deny *2") == (VTES["Deny"], 2)
    assert gc(p, VTES, "deny x2") == (VTES["Deny"], 2)
    assert gc(p, VTES, "deny x2,") == (VTES["Deny"], 2)
    assert gc(p, VTES, "deny x 2") == (VTES["Deny"], 2)
    assert gc(p, VTES, "deny - 2") == (VTES["Deny"], 2)
    assert gc(p, VTES, "deny -- 2") == (VTES["Deny"], 2)
    assert gc(p, VTES, "deny (2)") == (VTES["Deny"], 2)
    assert gc(p, VTES, "deny (x2)") == (VTES["Deny"], 2)
    assert gc(p, VTES, "deny [2]") == (VTES["Deny"], 2)
    assert gc(p, VTES, "deny =2") == (VTES["Deny"], 2)
    assert gc(p, VTES, "deny / 2") == (VTES["Deny"], 2)
    assert gc(p, VTES, "deny // 2") == (VTES["Deny"], 2)
    # headers are ignored
    caplog.clear()
    assert gc(p, VTES, "library (90)") == (None, 0)
    assert gc(p, VTES, "combat [15]") == (None, 0)
    assert gc(p, VTES, "combo [7]") == (None, 0)
    assert gc(p, VTES, "action (9):") == (None, 0)
    assert gc(p, VTES, "mod/combat (9)") == (None, 0)
    assert gc(p, VTES, "misc 12") == (None, 0)
    assert gc(p, VTES, "total: 90") == (None, 0)
    assert caplog.record_tuples == []
    # old-style trait in allies name are not comments
    assert gc(p, VTES, "carlton van wyk (hunter)") == (VTES["Carlton Van Wyk"], 1)
    assert gc(p, VTES, "ohoyo hopoksia (bastet)") == (
        VTES["Ohoyo Hopoksia (Bastet)"],
        1,
    )
    # clan, discipline and trifle are often found
    caplog.clear()
    assert gc(p, VTES, "art museum     toreador") == (VTES["Art Museum"], 1)
    assert gc(p, VTES, "villein     trifle") == (VTES["Villein"], 1)
    assert gc(p, VTES, "3x conditioning     dominate") == (VTES["Conditioning"], 3)
    # disciplines are a particularily difficult case: if properly counted, ok
    assert gc(p, VTES, "3x dominate") == (VTES["Dominate"], 3)
    # post count and mentions by default are parsed as cards
    assert gc(p, VTES, "dominate") == (VTES["Dominate"], 1)
    assert gc(p, VTES, "dominate (4)") == (VTES["Dominate"], 4)
    assert caplog.record_tuples == [
        ("krcg", logging.DEBUG, 'naked discipline (no count) "dominate"'),
        ("krcg", logging.DEBUG, 'naked discipline (no count) "dominate (4)"'),
    ]
    # but don't mess with Valeren or Oblivion
    assert gc(p, VTES, "6x touch of valeren") == (VTES["Touch of Valeren"], 6)
    assert gc(p, VTES, "6x touch of oblivion") == (VTES["Touch of Oblivion"], 6)
    # specific card names containing numbers
    assert gc(p, VTES, "ak-47") == (VTES["AK-47"], 1)
    assert gc(p, VTES, "kpist m/45") == (VTES["Kpist m/45"], 1)
    assert gc(p, VTES, "pier 13, port of baltimore") == (
        VTES["Pier 13, Port of Baltimore"],
        1,
    )
    assert gc(p, VTES, "pier 13 port of baltimore") == (
        VTES["Pier 13, Port of Baltimore"],
        1,
    )
    assert gc(p, VTES, "419 operation") == (VTES["419 Operation"], 1)

    # crypt needs special handling as we got a number in front and back
    assert gc(
        p, VTES, "2x anvil		6   cel pot dom pre tha	 primogen  brujah:1"
    ) == (
        VTES["Anvil"],
        2,
    )
    # names beginning with an 'x' and parenthesied '(adv)' must be matched
    assert gc(
        p, VTES, "2x xaviar (adv)		10  abo ani for pro aus cel pot	 gangrel:3"
    ) == (VTES["Xaviar (ADV)"], 2)
    # names with a comma and parenthesied '(adv)' must be matched
    assert gc(
        p,
        VTES,
        "5x sascha vykos, the angel of caine (adv) 8   "
        "aus tha vic ani dom  archbishop	tzimisce:2",
    ) == (VTES["Sascha Vykos, The Angel of Caine (ADV)"], 5)

    caplog.clear()
    # names beginning with a number are hard
    assert gc(p, VTES, "2nd tradition") == (VTES["Second Tradition: Domain"], 1)
    check_comment(p, VTES)
    # name ending with a number even harder
    assert gc(p, VTES, "ak-47") == (VTES["AK-47"], 1)
    check_comment(p, VTES)
    # channel 10 is unique: other cards will match 10 as the count
    assert gc(p, VTES, "channel 10") == (VTES["Channel 10"], 1)
    check_comment(p, VTES)
    # card names with numbers are tricky
    assert gc(p, VTES, "pier 13, port of baltimore") == (
        VTES["Pier 13, Port of Baltimore"],
        1,
    )
    check_comment(p, VTES)
    assert gc(p, VTES, "local 1111 2") == (VTES["Local 1111"], 2)
    check_comment(p, VTES)
    assert gc(p, VTES, "419 operation") == (VTES["419 Operation"], 1)
    check_comment(p, VTES)
    assert gc(p, VTES, "bang nakh -- tiger's claws") == (
        VTES["Bang Nakh — Tiger's Claws"],
        1,
    )
    check_comment(p, VTES)
    # quote encoding may be an issue
    assert gc(p, VTES, "1x alia, god=92s messenger") == (
        VTES["Alia, God's Messenger"],
        1,
    )
    check_comment(p, VTES)

    # cards with a clan / virtue / discipline in the name
    assert gc(p, VTES, "create gargoyle") == (VTES["Create Gargoyle"], 1)
    check_comment(p, VTES)
    assert gc(p, VTES, "shepherd's innocence") == (VTES["Shepherd's Innocence"], 1)
    check_comment(p, VTES)
    assert gc(p, VTES, "return to innocence") == (VTES["The Return to Innocence"], 1)
    check_comment(p, VTES)
    assert gc(p, VTES, "joseph pander") == (VTES["Joseph Pander"], 1)
    check_comment(p, VTES)
    # player shorthand resolves via the ALIASES map
    assert gc(p, VTES, "1x Mask of 1000 Faces") == (
        VTES["Mask of a Thousand Faces"],
        1,
    )
    check_comment(p, VTES)
    # only fuzzy-match debug noise here, no parse warnings
    assert [r for r in caplog.record_tuples if r[1] >= logging.WARNING] == []

    # multiple cards with post count on the same line: registered as a comment,
    # logged as a parse failure when the comment closes on a blank line
    caplog.clear()
    p.get_card("deny x2, confusion x4")
    p.get_card("")
    assert caplog.record_tuples == [
        ("krcg", logging.WARNING, 'failed to parse "deny x2, confusion x4"')
    ]

    # name ending with ", The"
    caplog.clear()
    assert gc(p, VTES, "1x Vozhd of Sofia, The") == (VTES["Vozhd of Sofia"], 1)
    check_comment(p, VTES)


def test_comments(VTES: vtes.VTES, caplog: pytest.LogCaptureFixture) -> None:
    """Comment parsing: line, multiline, card-attached, parenthesised."""
    p = parser.Parser(VTES._cards)

    # proper line comments
    assert gc(p, VTES, "// this is a comment") == (None, 0)
    check_comment(p, VTES, "// this is a comment")
    assert gc(p, VTES, "-- this is a comment") == (None, 0)
    check_comment(p, VTES, "-- this is a comment")
    assert gc(p, VTES, "/* this is a comment */") == (None, 0)
    check_comment(p, VTES, "/* this is a comment */")

    # multiline comment
    assert gc(p, VTES, "/* this is a comment") == (None, 0)
    assert gc(p, VTES, "it spans multiple lines") == (None, 0)
    assert gc(p, VTES, "so it's a multiline comment") == (None, 0)
    check_comment(
        p,
        VTES,
        "/* this is a comment\nit spans multiple lines\nso it's a multiline comment",
    )

    # naked comments in the middle of nowhere happen a lot
    assert gc(p, VTES, "this is a comment") == (None, 0)
    check_comment(p, VTES, "this is a comment")
    # sometimes they refer to a card
    assert gc(p, VTES, "deny is a good card") == (None, 0)
    check_comment(p, VTES, "deny is a good card")
    # sometimes even with count
    assert gc(p, VTES, "2x deny is probably not enough") == (None, 0)
    check_comment(p, VTES, "2x deny is probably not enough")

    # basic card comment
    assert gc(p, VTES, "2x deny  -- this is a comment") == (VTES["Deny"], 2)
    check_comment(p, VTES, "this is a comment", VTES["Deny"])
    assert gc(p, VTES, "2x deny  // this is a comment") == (VTES["Deny"], 2)
    check_comment(p, VTES, "this is a comment", VTES["Deny"])
    assert gc(p, VTES, "2x deny  /* this is a comment */") == (VTES["Deny"], 2)
    check_comment(p, VTES, "this is a comment", VTES["Deny"])

    # parenthesised comments are common, and can start with a number
    # (not to be confused with a count)
    assert gc(p, VTES, "deny (2 would have been better)") == (VTES["Deny"], 1)
    check_comment(p, VTES, "2 would have been better")

    # multiline card comment
    assert gc(p, VTES, "2x deny  /* this is a comment ") == (VTES["Deny"], 2)
    assert gc(p, VTES, "        it spans multiple lines") == (None, 0)
    check_comment(p, VTES, "this is a comment\n        it spans multiple lines")

    # poorly marked multiline comment
    caplog.clear()
    assert gc(p, VTES, "2x deny  -- this is a comment ") == (VTES["Deny"], 2)
    assert gc(p, VTES, "        it spans multiple lines") == (None, 0)
    p.get_card("")
    assert caplog.record_tuples == [
        ("krcg", logging.WARNING, 'failed to parse "it spans multiple lines"')
    ]

    # properly marked single line comments close cleanly
    caplog.clear()
    assert gc(p, VTES, "/* this is a comment */") == (None, 0)
    p.get_card("")
    assert caplog.record_tuples == []
    assert gc(p, VTES, "-- this is a comment") == (None, 0)
    p.get_card("")
    assert caplog.record_tuples == []
    assert gc(p, VTES, "1x deny") == (VTES["Deny"], 1)
    assert gc(p, VTES, "(this is a comment)") == (None, 0)
    assert gc(p, VTES, "1x deny") == (VTES["Deny"], 1)
    assert caplog.record_tuples == []

    # clan, discipline and trifle are not comments
    assert gc(p, VTES, "art museum     toreador") == (VTES["Art Museum"], 1)
    assert gc(p, VTES, "villein     trifle") == (VTES["Villein"], 1)
    assert gc(p, VTES, "3x conditioning     dominate") == (VTES["Conditioning"], 3)
    check_comment(p, VTES)


def test_preface(VTES: vtes.VTES, caplog: pytest.LogCaptureFixture) -> None:
    """Preface parsing: headers ignored, naked names are comments not cards."""
    p = parser.Parser(VTES._cards)
    assert gc(p, VTES, "Comment:") == (None, 0)
    assert gc(p, VTES, "Description:") == (None, 0)
    assert gc(p, VTES, "Crypt:") == (None, 0)
    assert gc(p, VTES, "---------------------------") == (None, 0)
    assert gc(p, VTES, "===========================") == (None, 0)
    check_comment(p, VTES)

    # in the preface, card names without a count should not be matched:
    # a naked name before the decklist is part of a preface comment
    assert gc(p, VTES, "deny") == (None, 0)
    check_comment(p, VTES, "deny")
    # even discipline names
    caplog.clear()
    assert gc(p, VTES, "dominate") == (None, 0)
    check_comment(p, VTES, "dominate")
    assert caplog.record_tuples == []


def test_twda_improper_discipline(
    VTES: vtes.VTES, caplog: pytest.LogCaptureFixture
) -> None:
    """In TWDA mode, a naked discipline line is ambiguous and warns (vs. counted)."""
    p = parser.Parser(VTES._cards, twda=True)
    p.get_card("------------")  # a separator lets the deck list begin
    gc(p, VTES, "2x deny")  # a prefixed card ends the preface
    caplog.clear()
    caplog.set_level(logging.WARNING)
    assert p.get_card("dominate") is None
    assert p.get_card("dominate (4)") is None
    assert caplog.record_tuples == [
        ("krcg", logging.WARNING, 'improper discipline "dominate"'),
        ("krcg", logging.WARNING, 'improper discipline "dominate (4)"'),
    ]
