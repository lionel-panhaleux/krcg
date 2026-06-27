"""Test the analyzer."""

from krcg import analyzer
from krcg import models
from krcg import twda
from krcg import vtes


def test_analyzer() -> None:
    """Stats, affinity and deck building over the bundled TWDA."""
    VTES = vtes.VTES.load_local()
    decks = list(twda.load_local().values())
    nana = VTES["Nana Buruku"]
    aksinya = VTES["Aksinya Daclau"]

    assert analyzer.played(decks, VTES)[nana] >= 2
    affine = dict(analyzer.affinity(decks, VTES, nana, similarity=1))
    assert affine[aksinya] > 0
    mean, variance = analyzer.stats(decks, VTES)[VTES["Villein"]]
    assert mean > 1 and variance > 0

    deck = analyzer.build_deck(decks, VTES, nana)
    crypt = sum(c.count for c in deck.cards if c.kind == models.Card.Kind.CRYPT)
    library = sum(c.count for c in deck.cards if c.kind == models.Card.Kind.LIBRARY)
    assert crypt >= 12
    assert 60 <= library <= 90
