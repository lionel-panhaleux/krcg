"""TWDA: the Tournament Winning Decks Archive.

The archive is a ``dict[str, models.Deck]`` keyed by deck id. A compressed
snapshot ships with the package, so ``load_local()`` works offline; online
tools can use ``load_online()`` to fetch the latest archive from KRCG static.
"""

import importlib.resources
import logging
import lzma

import aiohttp
import msgspec.json

from . import models

logger = logging.getLogger("krcg")


DecksArchive = dict[str, models.Deck]


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
