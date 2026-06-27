"""Test ruling parsing and the full serialized form of ruling-bearing cards."""

import json
import pathlib

import msgspec.json
import pytest

from krcg import collections

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
