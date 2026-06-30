"""Load the cards library: a ready-to-use `collections.CardDict`.

Three entry points, all returning an indexed `CardDict` (look cards up by id or
name, run `search`/`complete`):

- `load()`: fast default — a version-keyed pickle cache, else `load_local()`.
- `load_local()`: build from the packaged VEKN CSVs and rulings (offline).
- `load_online(session)`: fetch the pre-built JSON from KRCG static (async).
"""

from typing import cast
import importlib.metadata
import logging
import os
import pickle
import tempfile

import aiohttp
import msgspec

from . import collections
from . import models
from . import rulings
from . import vekn_csv


VERSION = importlib.metadata.version("krcg")
PICKLE_FILE = os.path.join(tempfile.gettempdir(), f"krcg_cards_{VERSION}.pkl")
logger = logging.getLogger("krcg")


def load_local(available: set[str] | None = None) -> collections.CardDict:
    """Build the cards library from the packaged VEKN CSVs and rulings.

    ``available`` is forwarded to `vekn_csv.compute_urls` to publish only image
    URLs that resolve; when given, the version cache is left untouched (the
    pruned build is specialized and must not become the default `load()`).
    """
    raw, sets = vekn_csv.from_files(available)
    cards = collections.CardDict(raw)
    cards.sets = sets
    rulings.load_local(cards)
    cards.index()
    if available is None:
        _cache(cards)
    return cards


def load() -> collections.CardDict:
    """Load the cards library fast: a version-keyed pickle cache, else `load_local`."""
    try:
        with open(PICKLE_FILE, "rb") as f:
            return cast(collections.CardDict, pickle.load(f))
    except Exception:
        logger.warning("no usable cards cache, building from local data", exc_info=True)
        return load_local()


async def load_online(session: aiohttp.ClientSession) -> collections.CardDict:
    """Fetch the pre-built cards library from KRCG static, else fall back to `load`.

    https://static.krcg.org/data/v5/vtes.json
    https://static.krcg.org/data/v5/expansions.json
    """
    try:
        cards = collections.CardDict()
        async with session.get("https://static.krcg.org/data/v5/vtes.json") as response:
            data = await response.json()
        for card in data:
            # dispatch on kind: a bare Card silently drops crypt/library fields
            cls_ = (
                models.CryptCard
                if card["kind"] == models.Card.Kind.CRYPT
                else models.LibraryCard
            )
            cards.add(msgspec.convert(card, type=cls_))
        async with session.get(
            "https://static.krcg.org/data/v5/expansions.json"
        ) as response:
            data = await response.json()
        for item in data:
            expansion = msgspec.convert(item, type=models.Set)
            for key in (expansion.id, expansion.code, expansion.name):
                if key:
                    cards.sets[key] = expansion
        cards.index()
        _cache(cards)
        return cards
    except Exception:
        logger.warning("failed to load cards from KRCG static", exc_info=True)
        return load()


def _cache(cards: collections.CardDict) -> None:
    """Write the version-keyed pickle cache used by `load`."""
    with open(PICKLE_FILE, "wb") as f:
        pickle.dump(cards, f)
