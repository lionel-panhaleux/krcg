"""Test the VTES cards database: fuzzy lookup, translations, and search."""

import json
import pathlib

import msgspec.json
import pytest

from krcg import collections
from krcg import models

SNAPSHOTS = pathlib.Path(__file__).parent / "snapshots"


def test_fuzzy_match(cards: collections.CardDict) -> None:
    """Fuzzy matching resolves a misspelled card name."""
    assert "enchant kidnred" in cards
    assert cards["enchant kidnred"].printed_name == "Enchant Kindred"


def test_i18n(cards: collections.CardDict) -> None:
    """A card resolves by its translated name."""
    assert "Corneilles noires" in cards
    assert cards["Corneilles noires"].printed_name == "Carrion Crows"


def test_search_mechanics(cards: collections.CardDict) -> None:
    """Search input handling and the classification rules behind the dimensions."""
    # no parameter returns nothing; unknown dimension raises; unknown value is empty
    assert len(cards.search()) == 0
    with pytest.raises(ValueError):
        cards.search(foo="bar")
    assert len(cards.search(bonus="foo")) == 0
    # discipline trigrams are not matched inside card text
    assert not cards.search(card_text="thn")
    # a stealth *action* is not a "stealth" bonus, but its intercept is
    assert cards["Tracker's Mark"] in cards.search(bonus=["Intercept"], type=["Combat"])
    assert cards["Tracker's Mark"] not in cards.search(
        bonus=["Stealth"], type=["Combat"]
    )
    assert cards["Brainwash"] not in cards.search(bonus=["Stealth"], type=["Master"])
    # inferior disciplines still match a superior-discipline query
    assert cards["Gwen Brand"] in cards.search(
        discipline=["AUS", "CHI", "FOR", "ANI"], clan=["Ravnos"], group=["G5"]
    )
    # sect is resolved per-card: the Baron is not Anarch
    assert cards["The Baron"] not in cards.search(sect=["Anarch"], clan=["Samedi"])


def test_search_i18n(cards: collections.CardDict) -> None:
    """Text search matches the requested language in addition to English."""
    fr = cards.search(
        card_text="cette carte d'équipement représente un lieu", lang=models.Lang.FR
    )
    assert fr == [cards["Living Manse"], cards["The Ankara Citadel, Turkey"]]
    # a language query does not match another language's translation
    assert (
        cards.search(
            card_text="esta carta de equipo representa un lugar", lang=models.Lang.FR
        )
        == []
    )
    es = cards.search(
        card_text="esta carta de equipo representa un lugar", lang=models.Lang.ES
    )
    assert es == [cards["Living Manse"], cards["The Ankara Citadel, Turkey"]]


def test_search_dimensions(cards: collections.CardDict) -> None:
    """The search dimensions expose the expected facets and sample choices."""
    dims = cards.search_dimensions
    assert sorted(dims) == [
        "artist",
        "bonus",
        "capacity",
        "city",
        "clan",
        "discipline",
        "group",
        "kind",
        "path",
        "precon",
        "rarity",
        "sect",
        "set",
        "title",
        "trait",
        "type",
    ]
    assert "Brujah" in dims["clan"]
    assert "AUS" in dims["discipline"]
    assert "Imperator" in dims["title"]


@pytest.mark.baseline
def test_search_results(cards: collections.CardDict) -> None:
    """Result sizes + a spot card per dimension; drift in the card pool is amber."""
    loc = cards.search(card_text="this equipment card represents a location")
    assert cards["Catacombs"] in loc and len(loc) == 15
    flavor = cards.search(flavor_text="Baudelaire")
    assert cards["Shade"] in flavor and len(flavor) == 18
    chicago = cards.search(city=["Chicago"])
    assert cards["Crusade: Chicago"] in chicago and len(chicago) == 10
    imperator = cards.search(title=["Imperator"])
    assert cards["Confiscation"] in imperator and len(imperator) == 8
    stealth_votes = cards.search(bonus=["Stealth", "Votes"])
    assert cards["Loki's Gift"] in stealth_votes and len(stealth_votes) == 3
    justicar = cards.search(clan=["Banu Haqim"], title=["Justicar"])
    assert cards["Kasim Bayar"] in justicar and len(justicar) == 2
    kiasyd = cards.search(group=["G1", "G2", "G3"], clan=["Kiasyd"])
    assert cards["Marconius"] in kiasyd and len(kiasyd) == 6
    assert cards.search(clan=["Nagaraja"], trait=["Black Hand"]) == [
        cards["Sennadurek"]
    ]


@pytest.mark.baseline
def test_card_snapshot(cards: collections.CardDict) -> None:
    """Full serialized form of a rich crypt card (Theo Bell G2) — data tracker."""
    expected = json.loads((SNAPSHOTS / "card_theo_bell_g2.json").read_text())
    assert json.loads(msgspec.json.encode(cards[201362])) == expected


def test_serialization_smoke(cards: collections.CardDict) -> None:
    """The whole card database serializes through msgspec without error."""
    assert len(cards) > 4000
    assert len(msgspec.json.encode(list(cards.cards()))) > 0
