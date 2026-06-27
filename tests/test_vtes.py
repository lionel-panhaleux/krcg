"""Test the VTES cards database: fuzzy lookup, translations, and search."""

import json
import pathlib

import msgspec.json
import pytest

from krcg import models
from krcg import vtes

SNAPSHOTS = pathlib.Path(__file__).parent / "snapshots"


def test_fuzzy_match(VTES: vtes.VTES) -> None:
    """Fuzzy matching resolves a misspelled card name."""
    assert "enchant kidnred" in VTES
    assert VTES["enchant kidnred"].printed_name == "Enchant Kindred"


def test_i18n(VTES: vtes.VTES) -> None:
    """A card resolves by its translated name."""
    assert "Corneilles noires" in VTES
    assert VTES["Corneilles noires"].printed_name == "Carrion Crows"


def test_search_mechanics(VTES: vtes.VTES) -> None:
    """Search input handling and the classification rules behind the dimensions."""
    # no parameter returns nothing; unknown dimension raises; unknown value is empty
    assert len(VTES.search()) == 0
    with pytest.raises(ValueError):
        VTES.search(foo="bar")
    assert len(VTES.search(bonus="foo")) == 0
    # discipline trigrams are not matched inside card text
    assert not VTES.search(card_text="thn")
    # a stealth *action* is not a "stealth" bonus, but its intercept is
    assert VTES["Tracker's Mark"] in VTES.search(bonus=["Intercept"], type=["Combat"])
    assert VTES["Tracker's Mark"] not in VTES.search(bonus=["Stealth"], type=["Combat"])
    assert VTES["Brainwash"] not in VTES.search(bonus=["Stealth"], type=["Master"])
    # inferior disciplines still match a superior-discipline query
    assert VTES["Gwen Brand"] in VTES.search(
        discipline=["AUS", "CHI", "FOR", "ANI"], clan=["Ravnos"], group=["G5"]
    )
    # sect is resolved per-card: the Baron is not Anarch
    assert VTES["The Baron"] not in VTES.search(sect=["Anarch"], clan=["Samedi"])


def test_search_i18n(VTES: vtes.VTES) -> None:
    """Text search matches the requested language in addition to English."""
    fr = VTES.search(
        card_text="cette carte d'équipement représente un lieu", lang=models.Lang.FR
    )
    assert fr == [VTES["Living Manse"], VTES["The Ankara Citadel, Turkey"]]
    # a language query does not match another language's translation
    assert (
        VTES.search(
            card_text="esta carta de equipo representa un lugar", lang=models.Lang.FR
        )
        == []
    )
    es = VTES.search(
        card_text="esta carta de equipo representa un lugar", lang=models.Lang.ES
    )
    assert es == [VTES["Living Manse"], VTES["The Ankara Citadel, Turkey"]]


def test_search_dimensions(VTES: vtes.VTES) -> None:
    """The search dimensions expose the expected facets and sample choices."""
    dims = VTES.search_dimensions
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
def test_search_results(VTES: vtes.VTES) -> None:
    """Result sizes + a spot card per dimension; drift in the card pool is amber."""
    loc = VTES.search(card_text="this equipment card represents a location")
    assert VTES["Catacombs"] in loc and len(loc) == 15
    flavor = VTES.search(flavor_text="Baudelaire")
    assert VTES["Shade"] in flavor and len(flavor) == 18
    chicago = VTES.search(city=["Chicago"])
    assert VTES["Crusade: Chicago"] in chicago and len(chicago) == 10
    imperator = VTES.search(title=["Imperator"])
    assert VTES["Confiscation"] in imperator and len(imperator) == 8
    stealth_votes = VTES.search(bonus=["Stealth", "Votes"])
    assert VTES["Loki's Gift"] in stealth_votes and len(stealth_votes) == 3
    justicar = VTES.search(clan=["Banu Haqim"], title=["Justicar"])
    assert VTES["Kasim Bayar"] in justicar and len(justicar) == 2
    kiasyd = VTES.search(group=["G1", "G2", "G3"], clan=["Kiasyd"])
    assert VTES["Marconius"] in kiasyd and len(kiasyd) == 6
    assert VTES.search(clan=["Nagaraja"], trait=["Black Hand"]) == [VTES["Sennadurek"]]


@pytest.mark.baseline
def test_card_snapshot(VTES: vtes.VTES) -> None:
    """Full serialized form of a rich crypt card (Theo Bell G2) — data tracker."""
    expected = json.loads((SNAPSHOTS / "card_theo_bell_g2.json").read_text())
    assert json.loads(msgspec.json.encode(VTES[201362])) == expected


def test_serialization_smoke(VTES: vtes.VTES) -> None:
    """The whole card database serializes through msgspec without error."""
    assert len(VTES) > 4000
    assert len(msgspec.json.encode(list(VTES))) > 0
