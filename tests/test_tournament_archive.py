"""Test parsing the tournament extended-archive deck format."""

import logging
import pathlib

import pytest

from krcg import collections
from krcg import models
from krcg import parser

FIXTURE = pathlib.Path(__file__).parent / "202207_EC_Day1_1.txt"


def test_tournament_archive_format(
    cards: collections.CardDict, caplog: pytest.LogCaptureFixture
) -> None:
    """The reference tournament-archive deck parses without warnings."""
    caplog.set_level(logging.WARNING)
    with FIXTURE.open() as f:
        deck = parser.deck_from_txt(f, cards, id=FIXTURE.stem)
    assert caplog.record_tuples == []
    assert deck.player == "VtesEC2022"
    assert str(deck.score) == "2GW6.5"
    by_id = {c.id: c.count for c in deck.cards}
    crypt = {c.id: c.count for c in deck.cards if c.kind == models.Card.Kind.CRYPT}
    assert sum(crypt.values()) == 12
    assert by_id[200076] == 5  # Anarch Convert
    assert by_id[200781] == 3  # Khurshid
    library = sum(c.count for c in deck.cards if c.kind == models.Card.Kind.LIBRARY)
    assert library == 90
    assert by_id[100634] == 10  # Emerald Legionnaire
    assert by_id[100545] == 3  # Direct Intervention
