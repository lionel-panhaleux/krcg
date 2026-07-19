"""Test ruling parsing and the full serialized form of ruling-bearing cards."""

import io
import json
import pathlib

import msgspec.json
import pytest

from krcg import collections, rulings, vekn_csv

SNAPSHOTS = pathlib.Path(__file__).parent / "snapshots"


def test_ruling_structure(cards: collections.CardDict) -> None:
    """Rulings parse into structured references and symbols (rulings.py logic)."""
    card = cards["Toreador Grand Ball"]
    assert card.rulings
    for ruling in card.rulings:
        assert ruling.text
        for ref in ruling.references:
            assert ref.label and ref.url.startswith("http")
    # discipline/type symbol parsing works for at least one card in the database
    assert any(
        symbol.symbol for c in cards.cards() for r in c.rulings for symbol in r.symbols
    )


def test_new_format_parsing() -> None:
    """New ruling formats parse: reminders, the overrides map, and per-card overrides.

    A REMINDER ends its text with a [REMINDER] tag (surfaced as `reminder`); an override
    gives a member card its own wording. Uses a fresh ruling-free card DB so the shared
    session fixture isn't polluted.
    """
    raw, sets = vekn_csv.from_files()
    cards = collections.CardDict(raw)
    cards.sets = sets
    cards.index()
    rulings.load_from_files(
        cards,
        io.StringIO(
            "100038|Alastor:\n"
            "  - Plain ruling. [LSJ 20040518]\n"
            "  - Confirms the obvious. [REMINDER]\n"
            "G00008|Grp:\n"
            "  - text: Group text. [LSJ 20040518] [REMINDER]\n"
            "    overrides:\n"
            "      100015|Academic Hunting Ground: Special wording for this card.\n"
        ),
        io.StringIO(
            "G00008|Grp:\n"
            "  100015|Academic Hunting Ground: ''\n"
            "  100002|419 Operation: ''\n"
        ),
        io.StringIO("LSJ 20040518: https://groups.google.com/x\n"),
    )
    # plain card: the tag is stripped and surfaced, references still parse
    by_text = {r.text: r for r in cards[100038].rulings}
    assert by_text["Plain ruling. [LSJ 20040518]"].reminder is False
    assert by_text["Confirms the obvious."].reminder is True
    # overridden member gets its own wording; still a reminder (from the group text)
    (adapted,) = [r for r in cards[100015].rulings if r.group == "Grp"]
    assert adapted.text == "Special wording for this card."
    assert adapted.reminder is True
    # non-overridden member: group text (tag stripped), reminder flag, shared reference
    (inherited,) = [r for r in cards[100002].rulings if r.group == "Grp"]
    assert inherited.text == "Group text. [LSJ 20040518]"
    assert inherited.reminder is True
    assert [ref.label for ref in inherited.references] == ["LSJ 20040518"]


@pytest.mark.baseline
@pytest.mark.parametrize(
    "card_id, snapshot",
    [
        (101989, "card_toreador_grand_ball.json"),  # multiple references
        (101850, "card_spirits_touch.json"),  # several LSJ rulings
    ],
)
def test_ruling_card_snapshot(
    cards: collections.CardDict, card_id: int, snapshot: str
) -> None:
    """Full serialized form of a ruling-bearing card — data tracker (amber)."""
    expected = json.loads((SNAPSHOTS / snapshot).read_text())
    assert json.loads(msgspec.json.encode(cards[card_id])) == expected
