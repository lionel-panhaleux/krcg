from src import deck


def test_cards():
    d = deck.Deck()
    d.update({"Fame": 3})
    assert list(d.cards()) == [("Fame", 3)]


def test_cards_count():
    d = deck.Deck()
    d.update({"Fame": 3, "Bum's Rush": 10, "Crusher": 4})
    assert d.cards_count() == 17
