"""TWDA: the Tournament Winning Decks Archive.

The archive is a ``dict[str, models.Deck]`` keyed by deck id. A compressed
snapshot ships with the package, so ``load_local()`` works offline; online
tools can use ``load_online()`` to fetch the latest archive from KRCG static.
"""

import importlib.resources
import io
import logging
import lzma
import os.path
import urllib.request
import zipfile

import aiohttp
import msgspec.json

from . import collections
from . import models
from . import parser

logger = logging.getLogger("krcg")


DecksArchive = dict[str, models.Deck]

#: upstream archive of TWDA decks as ``.txt`` files (default branch zip)
TWD_SOURCE_URL = "https://github.com/GiottoVerducci/TWD/archive/refs/heads/master.zip"


def _mark_winners(archive: DecksArchive) -> DecksArchive:
    """Flag every scored deck as a tournament win (the WD in TWDA)."""
    for deck in archive.values():
        if deck.score:
            deck.score.win = True
    return archive


def load() -> DecksArchive:
    """Load the TWDA, fast and offline (the bundled snapshot).

    Mirrors `loader.load` for the cards; the archive needs no cache (one decode).
    """
    return load_local()


def load_local() -> DecksArchive:
    """Load the TWDA from the bundled (compressed) snapshot."""
    path = importlib.resources.files("krcg.cards").joinpath("twda.json.xz")
    with path.open("rb") as f:
        archive = msgspec.json.decode(lzma.decompress(f.read()), type=DecksArchive)
    return _mark_winners(archive)


async def load_online(session: aiohttp.ClientSession) -> DecksArchive:
    """Load the TWDA from KRCG static, falling back to the bundled snapshot.

    https://static.krcg.org/data/v5/twda.json
    """
    try:
        async with session.get("https://static.krcg.org/data/v5/twda.json") as response:
            data = await response.read()
        return msgspec.json.decode(data, type=DecksArchive)
    except Exception:
        logger.warning("Failed to load TWDA from KRCG static", exc_info=True)
        return load_local()


def fetch_from_source(
    cards: collections.CardDict, url: str = TWD_SOURCE_URL
) -> DecksArchive:
    """Build a fresh TWDA from the upstream GiottoVerducci/TWD ``.txt`` files.

    Downloads the source archive and parses every deck, so callers track the
    live TWDA without waiting for a package release. Returns a ready-to-use
    archive (winners marked), like `load_local`. Needs the network; callers that
    must stay offline should catch failures and fall back to `load_local`.
    """
    with urllib.request.urlopen(url) as response:
        zip_data = response.read()
    return _mark_winners(_decks_from_zip(zip_data, cards))


def _decks_from_zip(zip_data: bytes, cards: collections.CardDict) -> DecksArchive:
    """Parse every ``TWD-master/decks/*`` deck file from the source zip bytes."""
    archive: DecksArchive = {}
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_file:
        for name in zip_file.namelist():
            if not name.startswith("TWD-master/decks/") or name.endswith("/"):
                continue
            deck_id = os.path.splitext(os.path.basename(name))[0]
            with zip_file.open(name) as source:
                text = io.TextIOWrapper(source, encoding="utf-8")
                deck = parser.deck_from_txt(text, cards, id=deck_id, twda=True)
            archive[deck.id] = deck
    return archive
