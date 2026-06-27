"""Test the analyzer."""

from krcg import analyzer
from krcg import loader
from krcg import models
from krcg import twda


def test_analyzer() -> None:
    """Stats, affinity and deck building over the bundled TWDA."""
    cards = loader.load_local()
    decks = list(twda.load_local().values())
    nana = cards["Nana Buruku"]
    aksinya = cards["Aksinya Daclau"]

    assert analyzer.played(decks, cards)[nana] >= 2
    affine = dict(analyzer.affinity(decks, cards, nana, similarity=1))
    assert affine[aksinya] > 0
    mean, variance = analyzer.stats(decks, cards)[cards["Villein"]]
    assert mean > 1 and variance > 0

    deck = analyzer.build_deck(decks, cards, nana)
    crypt = sum(c.count for c in deck.cards if c.kind == models.Card.Kind.CRYPT)
    library = sum(c.count for c in deck.cards if c.kind == models.Card.Kind.LIBRARY)
    assert crypt >= 12
    assert 60 <= library <= 90
