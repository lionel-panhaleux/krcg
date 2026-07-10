"""Test the decklist parser (line-level: counts, names, comments, disciplines)."""

import logging

import pytest

from krcg import collections
from krcg import models
from krcg import parser


def gc(
    p: parser.Parser, cards: collections.CardDict, line: str
) -> tuple[models.Card | None, int]:
    """Parse a line and return it as a (resolved card | None, count) pair."""
    entry = p.get_card(line)
    return (cards[entry.id], entry.count) if entry else (None, 0)


def check_comment(
    p: parser.Parser,
    cards: collections.CardDict,
    comment: str | None = None,
    card: models.Card | None = None,
) -> None:
    """Assert the parser's pending comment (and optionally the card it targets)."""
    if comment:
        assert p.current_comment
        assert p.current_comment.string == comment
        if card:
            assert p.current_comment.card is not None
            assert cards[p.current_comment.card.id] is card
        p.current_comment = None
    else:
        assert p.current_comment is None


def test_get_card(
    cards: collections.CardDict, caplog: pytest.LogCaptureFixture
) -> None:
    """Card name & count parsing across the many real-world spellings."""
    caplog.set_level(logging.DEBUG)
    p = parser.Parser(cards)

    # ante count, with assorted markers
    assert gc(p, cards, "2x deny") == (cards["Deny"], 2)
    assert gc(p, cards, "2xx deny") == (cards["Deny"], 2)
    assert gc(p, cards, "x2 deny") == (cards["Deny"], 2)
    assert gc(p, cards, "xx2 deny") == (cards["Deny"], 2)
    assert gc(p, cards, "2* deny") == (cards["Deny"], 2)
    assert gc(p, cards, "2*deny") == (cards["Deny"], 2)
    assert gc(p, cards, "2 deny") == (cards["Deny"], 2)
    assert gc(p, cards, "*2 deny") == (cards["Deny"], 2)
    assert gc(p, cards, "deny") == (cards["Deny"], 1)
    # post count
    assert gc(p, cards, "deny 2") == (cards["Deny"], 2)
    assert gc(p, cards, "deny *2") == (cards["Deny"], 2)
    assert gc(p, cards, "deny x2") == (cards["Deny"], 2)
    assert gc(p, cards, "deny x2,") == (cards["Deny"], 2)
    assert gc(p, cards, "deny x 2") == (cards["Deny"], 2)
    assert gc(p, cards, "deny - 2") == (cards["Deny"], 2)
    assert gc(p, cards, "deny -- 2") == (cards["Deny"], 2)
    assert gc(p, cards, "deny (2)") == (cards["Deny"], 2)
    assert gc(p, cards, "deny (x2)") == (cards["Deny"], 2)
    assert gc(p, cards, "deny [2]") == (cards["Deny"], 2)
    assert gc(p, cards, "deny =2") == (cards["Deny"], 2)
    assert gc(p, cards, "deny / 2") == (cards["Deny"], 2)
    assert gc(p, cards, "deny // 2") == (cards["Deny"], 2)
    # headers are ignored
    caplog.clear()
    assert gc(p, cards, "library (90)") == (None, 0)
    assert gc(p, cards, "combat [15]") == (None, 0)
    assert gc(p, cards, "combo [7]") == (None, 0)
    assert gc(p, cards, "action (9):") == (None, 0)
    assert gc(p, cards, "mod/combat (9)") == (None, 0)
    assert gc(p, cards, "misc 12") == (None, 0)
    assert gc(p, cards, "total: 90") == (None, 0)
    assert caplog.record_tuples == []
    # old-style trait in allies name are not comments
    assert gc(p, cards, "carlton van wyk (hunter)") == (cards["Carlton Van Wyk"], 1)
    assert gc(p, cards, "ohoyo hopoksia (bastet)") == (
        cards["Ohoyo Hopoksia (Bastet)"],
        1,
    )
    # clan, discipline and trifle are often found
    caplog.clear()
    assert gc(p, cards, "art museum     toreador") == (cards["Art Museum"], 1)
    assert gc(p, cards, "villein     trifle") == (cards["Villein"], 1)
    assert gc(p, cards, "3x conditioning     dominate") == (cards["Conditioning"], 3)
    # disciplines are a particularily difficult case: if properly counted, ok
    assert gc(p, cards, "3x dominate") == (cards["Dominate"], 3)
    # post count and mentions by default are parsed as cards
    assert gc(p, cards, "dominate") == (cards["Dominate"], 1)
    assert gc(p, cards, "dominate (4)") == (cards["Dominate"], 4)
    assert caplog.record_tuples == [
        ("krcg", logging.DEBUG, 'naked discipline (no count) "dominate"'),
        ("krcg", logging.DEBUG, 'naked discipline (no count) "dominate (4)"'),
    ]
    # but don't mess with Valeren or Oblivion
    assert gc(p, cards, "6x touch of valeren") == (cards["Touch of Valeren"], 6)
    assert gc(p, cards, "6x touch of oblivion") == (cards["Touch of Oblivion"], 6)
    # specific card names containing numbers
    assert gc(p, cards, "ak-47") == (cards["AK-47"], 1)
    assert gc(p, cards, "kpist m/45") == (cards["Kpist m/45"], 1)
    assert gc(p, cards, "pier 13, port of baltimore") == (
        cards["Pier 13, Port of Baltimore"],
        1,
    )
    assert gc(p, cards, "pier 13 port of baltimore") == (
        cards["Pier 13, Port of Baltimore"],
        1,
    )
    assert gc(p, cards, "419 operation") == (cards["419 Operation"], 1)

    # crypt needs special handling as we got a number in front and back
    assert gc(
        p, cards, "2x anvil		6   cel pot dom pre tha	 primogen  brujah:1"
    ) == (
        cards["Anvil"],
        2,
    )
    # names beginning with an 'x' and parenthesied '(adv)' must be matched
    assert gc(
        p, cards, "2x xaviar (adv)		10  abo ani for pro aus cel pot	 gangrel:3"
    ) == (cards["Xaviar (ADV)"], 2)
    # names with a comma and parenthesied '(adv)' must be matched
    assert gc(
        p,
        cards,
        "5x sascha vykos, the angel of caine (adv) 8   "
        "aus tha vic ani dom  archbishop	tzimisce:2",
    ) == (cards["Sascha Vykos, The Angel of Caine (ADV)"], 5)
    # the same group / advanced qualifiers must resolve WITHOUT a crypt tail: the
    # parenthesised form VDB, Amaranth and card exports emit, where the qualifier
    # sits where a comment would and must not be stripped as one
    assert gc(p, cards, "2x xaviar (g3 adv)") == (cards["Xaviar (G3 ADV)"], 2)
    assert gc(p, cards, "1x alan sovereign (g3 adv)") == (
        cards["Alan Sovereign (G3 ADV)"],
        1,
    )
    assert gc(p, cards, "alan sovereign (adv)") == (cards["Alan Sovereign (ADV)"], 1)
    # a bare group qualifier picks the right printing, not the base/default
    assert gc(p, cards, "3x theo bell (g6)") == (cards["Theo Bell (G6)"], 3)
    assert gc(p, cards, "2x theo bell (g2)") == (cards["Theo Bell (G2)"], 2)
    # a real trailing comment is still stripped, the qualifier kept
    assert gc(p, cards, "2x alan sovereign (g3 adv) (great card)") == (
        cards["Alan Sovereign (G3 ADV)"],
        2,
    )

    caplog.clear()
    # names beginning with a number are hard
    assert gc(p, cards, "2nd tradition") == (cards["Second Tradition: Domain"], 1)
    check_comment(p, cards)
    # name ending with a number even harder
    assert gc(p, cards, "ak-47") == (cards["AK-47"], 1)
    check_comment(p, cards)
    # channel 10 is unique: other cards will match 10 as the count
    assert gc(p, cards, "channel 10") == (cards["Channel 10"], 1)
    check_comment(p, cards)
    # card names with numbers are tricky
    assert gc(p, cards, "pier 13, port of baltimore") == (
        cards["Pier 13, Port of Baltimore"],
        1,
    )
    check_comment(p, cards)
    assert gc(p, cards, "local 1111 2") == (cards["Local 1111"], 2)
    check_comment(p, cards)
    assert gc(p, cards, "419 operation") == (cards["419 Operation"], 1)
    check_comment(p, cards)
    assert gc(p, cards, "bang nakh -- tiger's claws") == (
        cards["Bang Nakh — Tiger's Claws"],
        1,
    )
    check_comment(p, cards)
    # quote encoding may be an issue
    assert gc(p, cards, "1x alia, god=92s messenger") == (
        cards["Alia, God's Messenger"],
        1,
    )
    check_comment(p, cards)

    # cards with a clan / virtue / discipline in the name
    assert gc(p, cards, "create gargoyle") == (cards["Create Gargoyle"], 1)
    check_comment(p, cards)
    assert gc(p, cards, "shepherd's innocence") == (cards["Shepherd's Innocence"], 1)
    check_comment(p, cards)
    assert gc(p, cards, "return to innocence") == (cards["The Return to Innocence"], 1)
    check_comment(p, cards)
    assert gc(p, cards, "joseph pander") == (cards["Joseph Pander"], 1)
    check_comment(p, cards)
    # player shorthand resolves via the ALIASES map
    assert gc(p, cards, "1x Mask of 1000 Faces") == (
        cards["Mask of a Thousand Faces"],
        1,
    )
    check_comment(p, cards)
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
    assert gc(p, cards, "1x Vozhd of Sofia, The") == (cards["Vozhd of Sofia"], 1)
    check_comment(p, cards)


def test_comments(
    cards: collections.CardDict, caplog: pytest.LogCaptureFixture
) -> None:
    """Comment parsing: line, multiline, card-attached, parenthesised."""
    p = parser.Parser(cards)

    # proper line comments
    assert gc(p, cards, "// this is a comment") == (None, 0)
    check_comment(p, cards, "// this is a comment")
    assert gc(p, cards, "-- this is a comment") == (None, 0)
    check_comment(p, cards, "-- this is a comment")
    assert gc(p, cards, "/* this is a comment */") == (None, 0)
    check_comment(p, cards, "/* this is a comment */")

    # multiline comment
    assert gc(p, cards, "/* this is a comment") == (None, 0)
    assert gc(p, cards, "it spans multiple lines") == (None, 0)
    assert gc(p, cards, "so it's a multiline comment") == (None, 0)
    check_comment(
        p,
        cards,
        "/* this is a comment\nit spans multiple lines\nso it's a multiline comment",
    )

    # naked comments in the middle of nowhere happen a lot
    assert gc(p, cards, "this is a comment") == (None, 0)
    check_comment(p, cards, "this is a comment")
    # sometimes they refer to a card
    assert gc(p, cards, "deny is a good card") == (None, 0)
    check_comment(p, cards, "deny is a good card")
    # sometimes even with count
    assert gc(p, cards, "2x deny is probably not enough") == (None, 0)
    check_comment(p, cards, "2x deny is probably not enough")

    # basic card comment
    assert gc(p, cards, "2x deny  -- this is a comment") == (cards["Deny"], 2)
    check_comment(p, cards, "this is a comment", cards["Deny"])
    assert gc(p, cards, "2x deny  // this is a comment") == (cards["Deny"], 2)
    check_comment(p, cards, "this is a comment", cards["Deny"])
    assert gc(p, cards, "2x deny  /* this is a comment */") == (cards["Deny"], 2)
    check_comment(p, cards, "this is a comment", cards["Deny"])

    # parenthesised comments are common, and can start with a number
    # (not to be confused with a count)
    assert gc(p, cards, "deny (2 would have been better)") == (cards["Deny"], 1)
    check_comment(p, cards, "2 would have been better")

    # multiline card comment
    assert gc(p, cards, "2x deny  /* this is a comment ") == (cards["Deny"], 2)
    assert gc(p, cards, "        it spans multiple lines") == (None, 0)
    check_comment(p, cards, "this is a comment\n        it spans multiple lines")

    # poorly marked multiline comment
    caplog.clear()
    assert gc(p, cards, "2x deny  -- this is a comment ") == (cards["Deny"], 2)
    assert gc(p, cards, "        it spans multiple lines") == (None, 0)
    p.get_card("")
    assert caplog.record_tuples == [
        ("krcg", logging.WARNING, 'failed to parse "it spans multiple lines"')
    ]

    # properly marked single line comments close cleanly
    caplog.clear()
    assert gc(p, cards, "/* this is a comment */") == (None, 0)
    p.get_card("")
    assert caplog.record_tuples == []
    assert gc(p, cards, "-- this is a comment") == (None, 0)
    p.get_card("")
    assert caplog.record_tuples == []
    assert gc(p, cards, "1x deny") == (cards["Deny"], 1)
    assert gc(p, cards, "(this is a comment)") == (None, 0)
    assert gc(p, cards, "1x deny") == (cards["Deny"], 1)
    assert caplog.record_tuples == []

    # clan, discipline and trifle are not comments
    assert gc(p, cards, "art museum     toreador") == (cards["Art Museum"], 1)
    assert gc(p, cards, "villein     trifle") == (cards["Villein"], 1)
    assert gc(p, cards, "3x conditioning     dominate") == (cards["Conditioning"], 3)
    check_comment(p, cards)


def test_preface(cards: collections.CardDict, caplog: pytest.LogCaptureFixture) -> None:
    """Preface parsing: headers ignored, naked names are comments not cards."""
    p = parser.Parser(cards)
    assert gc(p, cards, "Comment:") == (None, 0)
    assert gc(p, cards, "Description:") == (None, 0)
    assert gc(p, cards, "Crypt:") == (None, 0)
    assert gc(p, cards, "---------------------------") == (None, 0)
    assert gc(p, cards, "===========================") == (None, 0)
    check_comment(p, cards)

    # in the preface, card names without a count should not be matched:
    # a naked name before the decklist is part of a preface comment
    assert gc(p, cards, "deny") == (None, 0)
    check_comment(p, cards, "deny")
    # even discipline names
    caplog.clear()
    assert gc(p, cards, "dominate") == (None, 0)
    check_comment(p, cards, "dominate")
    assert caplog.record_tuples == []


def test_twda_improper_discipline(
    cards: collections.CardDict, caplog: pytest.LogCaptureFixture
) -> None:
    """In TWDA mode, a naked discipline line is ambiguous and warns (vs. counted)."""
    p = parser.Parser(cards, twda=True)
    p.get_card("------------")  # a separator lets the deck list begin
    gc(p, cards, "2x deny")  # a prefixed card ends the preface
    caplog.clear()
    caplog.set_level(logging.WARNING)
    assert p.get_card("dominate") is None
    assert p.get_card("dominate (4)") is None
    assert caplog.record_tuples == [
        ("krcg", logging.WARNING, 'improper discipline "dominate"'),
        ("krcg", logging.WARNING, 'improper discipline "dominate (4)"'),
    ]
