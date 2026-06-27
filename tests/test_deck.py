"""Test deck serialization (provider formats) and remote deck fetching."""

import io
import pathlib

import aiohttp
import pytest

from krcg import collections
from krcg import parser
from krcg import providers

FIXTURE = pathlib.Path(__file__).parent / "twd_2010tcdbng.txt"

VDB_URL = (
    "https://vdb.im/decks/deck?name=The+Storage+Procurers#"
    "101250=1;101125=2;101896=3;100745=8;100362=6;101388=2;201231=1;200343=1;"
    "200346=1;201503=1;100516=1;100518=7;100519=2;100392=8;100401=7;102202=1;"
    "102079=1;201027=1;200517=1;101321=7;100298=1;101067=1;100944=1;102097=4;"
    "101333=1;100444=1;200161=1;200929=1;102113=3;100709=1;100966=1;200295=1;"
    "100327=1;201065=1;100332=2;200173=1;101614=1;201073=1;101491=6;101877=6;"
    "100855=1"
)


def test_serialize_formats(cards: collections.CardDict) -> None:
    """Each provider format renders a parsed deck as expected."""
    deck = parser.deck_from_txt(
        io.StringIO(FIXTURE.read_text()), cards, id="2010tcdbng", twda=True
    )

    # compact, fully-deterministic formats: assert exactly
    assert providers.serialize_vdb(deck) == VDB_URL
    minimal = providers.serialize_json_minimal(deck)
    assert minimal["id"] == "2010tcdbng"
    assert minimal["name"] == "The Storage Procurers"
    assert minimal["cards"]["100745"] == 8  # Storage Annex
    assert len(minimal["cards"]) == 41

    # text formats: assert the distinctive structure
    twd = providers.serialize_twd(deck, cards)
    assert twd.startswith(
        "Trading Card Day\nBad Nauheim, Germany\nMay 8th 2010\n2R+F\n"
    )
    assert "Deck Name: The Storage Procurers" in twd
    assert "Crypt (12 cards, min=7, max=24, avg=3.75)" in twd
    assert "Library (87 cards)" in twd

    txt = providers.serialize_txt(deck)
    assert "Standard 2R+F" in txt  # serialize_txt keeps the format prefix

    lackey = providers.serialize_lackey(deck)
    assert "6\tStorage Annex" in lackey

    jol = providers.serialize_jol(deck)
    assert "1x Badr al-Budur" in jol


@pytest.mark.asyncio
async def test_from_amaranth(cards: collections.CardDict) -> None:
    """Fetch and parse a deck from Amaranth (skipped offline, cf. conftest)."""
    async with aiohttp.ClientSession() as session:
        deck = await providers.fetch(
            session,
            "https://amaranth.vtes.co.nz/deck/4d3aa426-70da-44b7-8cb7-92377a1a0dbd",
            cards,
        )
    assert deck.name == "First Blood: Tremere"
    assert deck.author == "BCP"
    assert "blackchantry.com" in deck.comment
    assert {c.id: c.count for c in deck.cards}[200025] == 2  # Aidan Lyle


@pytest.mark.asyncio
async def test_from_vdb(cards: collections.CardDict) -> None:
    """Fetch and parse a deck from VDB (skipped offline, cf. conftest)."""
    async with aiohttp.ClientSession() as session:
        deck = await providers.fetch(session, "https://vdb.im/decks/5b4312a1f", cards)
    assert deck.name == "First Blood Tremere"
    assert deck.author == "BCP"
    assert "blackchantry.com" in deck.comment
    assert {c.id: c.count for c in deck.cards}[200025] == 2  # Aidan Lyle


@pytest.mark.asyncio
async def test_from_vtesdecks(cards: collections.CardDict) -> None:
    """Fetch and parse a deck from VTESDecks (skipped offline, cf. conftest)."""
    async with aiohttp.ClientSession() as session:
        deck = await providers.fetch(
            session,
            "https://vtesdecks.com/deck/user-lionelpx-bf26e06e078348e8b5852d4e86dbdf6c",
            cards,
        )
    assert deck.name == "Test"
    assert deck.author == "lionelpx"
    assert deck.comment == "Here goes my description!"
    assert {c.id: c.count for c in deck.cards}[200001] == 7  # Aabbt Kindred
