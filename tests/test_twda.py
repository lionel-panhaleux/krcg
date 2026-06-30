"""Parser fidelity against hand-picked TWDA decks (current source, as .txt).

Each ``twd_<id>.txt`` is a frozen real deck chosen for a format peculiarity, so
these are core tests — a failure is a parser regression. The bundle snapshot at
the end is a baseline test (amber on source-data drift).
"""

import io
import pathlib
import zipfile

import msgspec.json
import pytest

from krcg import collections
from krcg import models
from krcg import parser
from krcg import providers
from krcg import twda

FIXTURES = pathlib.Path(__file__).parent


def _parse(cards: collections.CardDict, deck_id: str) -> models.Deck:
    """Parse a frozen .txt fixture and mark the win, as the TWDA loader does."""
    text = (FIXTURES / f"twd_{deck_id}.txt").read_text(encoding="utf-8")
    deck = parser.deck_from_txt(io.StringIO(text), cards, id=deck_id, twda=True)
    if deck.score:
        deck.score.win = True
    return deck


def _count(deck: models.Deck, kind: models.Card.Kind) -> int:
    """Total copies of a card kind in the deck."""
    return sum(c.count for c in deck.cards if c.kind == kind)


# each fixture stresses a distinct format quirk (see the per-feature tests below)
HEADERS = {
    "10842": {
        "name": "Malkavians Go Fast",
        "player": "Lotte Siebert",
        "event": "Irish NC 2023",
        "place": "Dungeons and Donuts, Galway, Ireland",
        "country": "IE",
        "online": False,
        "date": "2023-08-19",
        "end_date": None,
        "rounds": 3,
        "finals": False,
        "players_count": 7,
        "score": "2GW8!",
        "crypt": 12,
        "library": 75,
    },
    "13259": {
        "name": "Lasombra bleed & friends",
        "player": "Lukáš Simandl",
        "event": "5th Road to Pulled Fang #15",
        "place": "Olomouc, Czech Republic",
        "country": "CZ",
        "online": False,
        "date": "2026-05-16",
        "end_date": None,
        "rounds": 3,
        "finals": True,
        "players_count": 20,
        "score": "1GW7+2.5!",
        "crypt": 12,
        "library": 90,
    },
    "10792": {
        "name": "Carna & friends",
        "player": "Jorge Delgado",
        "event": "Pressing Flesh",
        "place": "Paris, France",
        "country": "FR",
        "online": False,
        "date": "2023-06-24",
        "end_date": None,
        "rounds": 3,
        "finals": True,
        "players_count": 15,
        "score": None,
        "crypt": 12,
        "library": 80,
    },
    "10073": {
        "name": "Ministério da Safadeza [#0]",
        "player": "Delmar Sittoni",
        "event": "Sede de Vitae Part 29",
        "place": "Online",
        "country": None,
        "online": True,
        "date": "2022-02-07",
        "end_date": "2022-02-10",
        "rounds": 2,
        "finals": True,
        "players_count": 14,
        "score": None,
        "crypt": 12,
        "library": 65,
    },
    "2k2amstelveen": {
        "name": "Protect and Serve",
        "player": "Tim Eijpe",
        "event": "Praxis Seizure: Amstelveen",
        "place": "Amstelveen, Netherlands",
        "country": "NL",
        "online": False,
        "date": "2002-04-28",
        "end_date": None,
        "rounds": 0,
        "finals": True,
        "players_count": 22,
        "score": None,
        "crypt": 12,
        "library": 90,
    },
}


@pytest.mark.parametrize("deck_id", list(HEADERS))
def test_parse_headers(cards: collections.CardDict, deck_id: str) -> None:
    """Each fixture parses to its expected header fields and card counts."""
    exp = HEADERS[deck_id]
    deck = _parse(cards, deck_id)
    event = deck.event
    assert event is not None
    assert deck.name == exp["name"]
    assert deck.player == exp["player"]
    assert event.name == exp["event"]
    assert event.place == exp["place"]
    assert (event.country.code if event.country else None) == exp["country"]
    assert event.online == exp["online"]
    assert str(event.date) == exp["date"]
    assert (str(event.end_date) if event.end_date else None) == exp["end_date"]
    assert event.rounds == exp["rounds"]
    assert event.finals == exp["finals"]
    assert event.players_count == exp["players_count"]
    assert (str(deck.score) if deck.score else None) == exp["score"]
    assert _count(deck, models.Card.Kind.CRYPT) == exp["crypt"]
    assert _count(deck, models.Card.Kind.LIBRARY) == exp["library"]


def test_rounds_no_final(cards: collections.CardDict) -> None:
    """10842: 'NR (no final)' rounds, score across rounds, quoted crypt name."""
    deck = _parse(cards, "10842")
    assert deck.event is not None
    assert deck.event.rounds == 3 and deck.event.finals is False
    assert str(deck.score) == "2GW8!"
    assert any(c.unique_name == 'Jason "Son" Newberry' for c in deck.cards)


def test_sabbat_path(cards: collections.CardDict) -> None:
    """13259: a Sabbat-path crypt card resolves to its path; accents kept."""
    deck = _parse(cards, "13259")
    assert deck.player == "Lukáš Simandl"
    monsenor = next(c for c in deck.cards if c.unique_name == "El Monseñor")
    assert cards[monsenor.id].path == "Death and the Soul"


def test_preface_and_card_comments(cards: collections.CardDict) -> None:
    """10792: '&' in the deck name, a multi-line preface, many card comments."""
    deck = _parse(cards, "10792")
    assert deck.name == "Carna & friends"
    assert "Carna Grinder" in deck.comment
    assert sum(1 for c in deck.cards if c.comment) >= 10
    assert any(c.unique_name == "Pentex™ Subversion" for c in deck.cards)


def test_date_range(cards: collections.CardDict) -> None:
    """10073: an event date range (start -- end) and accented deck name."""
    deck = _parse(cards, "10073")
    assert deck.event is not None
    assert str(deck.event.date) == "2022-02-07"
    assert str(deck.event.end_date) == "2022-02-10"


def test_legacy_no_rounds_header(cards: collections.CardDict) -> None:
    """2k2amstelveen: a 2002 deck with no rounds header and no event URL."""
    deck = _parse(cards, "2k2amstelveen")
    assert deck.event is not None
    assert str(deck.event.date) == "2002-04-28"
    assert deck.event.rounds == 0 and deck.event.finals is True
    assert not deck.event.url


@pytest.mark.parametrize("deck_id", list(HEADERS))
def test_round_trip(cards: collections.CardDict, deck_id: str) -> None:
    """Serializing a parsed deck and re-parsing preserves its key fields."""
    deck = _parse(cards, deck_id)
    again = parser.deck_from_txt(
        io.StringIO(providers.serialize_twd(deck, cards)), cards, id=deck_id, twda=True
    )
    assert again.event is not None and deck.event is not None
    assert again.name == deck.name
    assert again.event.date == deck.event.date
    assert again.event.end_date == deck.event.end_date
    assert again.event.rounds == deck.event.rounds
    assert again.event.finals == deck.event.finals
    assert (str(again.score) if again.score else None) == (
        str(deck.score) if deck.score else None
    )
    assert _count(again, models.Card.Kind.CRYPT) == _count(deck, models.Card.Kind.CRYPT)
    assert _count(again, models.Card.Kind.LIBRARY) == _count(
        deck, models.Card.Kind.LIBRARY
    )


def test_decks_are_winners(
    cards: collections.CardDict, TWDA: twda.DecksArchive
) -> None:
    """Scored decks load as wins (the WD in TWDA); the parser reads back the '!'."""
    scored = [d for d in TWDA.values() if d.score]
    assert scored and all(d.score and d.score.win for d in scored)
    # serialize emits the '!' marker, which the parser reads back as the win flag
    deck = TWDA["10842"]
    assert deck.score and str(deck.score).endswith("!")
    again = parser.deck_from_txt(
        io.StringIO(providers.serialize_twd(deck, cards)), cards, id="10842", twda=True
    )
    assert again.score and again.score.win is True


@pytest.mark.baseline
def test_bundle_integrity(TWDA: twda.DecksArchive) -> None:
    """The bundled archive loads, is well-formed, and round-trips through msgspec."""
    assert len(TWDA) > 4000
    assert all(deck.id and deck.cards for deck in TWDA.values())
    encoded = msgspec.json.encode(TWDA)
    restored = msgspec.json.decode(encoded, type=twda.DecksArchive)
    assert restored["10842"].player == "Lotte Siebert"


def test_fetch_from_source(cards: collections.CardDict, tmp_path: pathlib.Path) -> None:
    """`fetch_from_source` parses the upstream zip layout and marks winners.

    Served over a ``file://`` URL so the parsing path runs offline; only deck
    files under ``TWD-master/decks/`` are picked up.
    """
    zpath = tmp_path / "twd.zip"
    with zipfile.ZipFile(zpath, "w") as zf:
        for deck_id in ("10842", "2010tcdbng"):
            zf.writestr(
                f"TWD-master/decks/{deck_id}.txt",
                (FIXTURES / f"twd_{deck_id}.txt").read_text(encoding="utf-8"),
            )
        zf.writestr("TWD-master/README.md", "ignored: not under decks/")
        zf.writestr("TWD-master/decks/", "")  # directory entry, skipped

    archive = twda.fetch_from_source(cards, url=zpath.as_uri())

    assert set(archive) == {"10842", "2010tcdbng"}
    assert archive["10842"].player == "Lotte Siebert"
    assert archive["10842"].score and archive["10842"].score.win is True
