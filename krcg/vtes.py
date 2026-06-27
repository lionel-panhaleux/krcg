"""This module provides the `VTES` singleton: the VTES cards library.

If it has not been initialized, VTES will evaluate to False.
VTES must be configured with `VTES.configure()` before being used.
"""

from typing import Self, cast
from collections.abc import Generator
from collections.abc import Iterable
import aiohttp
import importlib.metadata
import logging
import msgspec
import os
import pickle
import tempfile

from . import collections
from . import models
from . import parser
from . import providers
from . import rulings
from . import vekn_csv


VERSION = importlib.metadata.version("krcg")
PICKLE_FILE = pickle_file = os.path.join(
    tempfile.gettempdir(), f"krcg_vtes_{VERSION}.pkl"
)
LOG = logging.getLogger("krcg")


class VTES:
    """VTES cards database."""

    def __init__(self) -> None:
        """Cards database.

        Use the classmethods to load the database:

            - VTES.load(): default load, fast and local
            - VTES.load_local(): load from local CSV files
            - VTES.load_online(): load from KRCG static, advised for online tools,
            to keep up to date without having to use the latest krcg patch version.
        """
        self._cards = collections.CardDict()
        self._sets = dict[int | str, models.Set]()
        self._search = collections.CardSearch()

    @classmethod
    def load_local(cls) -> Self:
        """Load VTES cards from local CSV files."""
        ret = cls()
        ret._search = collections.CardSearch()
        cards, ret._sets = vekn_csv.from_files()
        ret._cards = collections.CardDict(cards)
        rulings.load_local(ret._cards)
        ret._setup()
        return ret

    @classmethod
    def load(cls) -> Self:
        """Default load: fast and local."""
        try:
            with open(PICKLE_FILE, "rb") as f:
                return cast(Self, pickle.load(f))
        except (pickle.UnpicklingError, EOFError, FileNotFoundError):
            LOG.warning("Failed to load pickled VTES data", exc_info=True)
            return cls.load_local()

    @classmethod
    async def load_online(cls, session: aiohttp.ClientSession) -> Self:
        """Load VTES cards from KRCG static.

        https://static.krcg.org/data/vtes.json
        https://static.krcg.org/data/expansions.json
        """
        try:
            ret = cls()
            async with session.get(
                "https://static.krcg.org/data/vtes.json"
            ) as response:
                data = await response.json()
            for card in data:
                # dispatch on kind: a bare Card silently drops crypt/library fields
                cls_ = (
                    models.CryptCard
                    if card["kind"] == models.Card.Kind.CRYPT
                    else models.LibraryCard
                )
                ret._cards.add(msgspec.convert(card, type=cls_))
            async with session.get(
                "https://static.krcg.org/data/expansions.json"
            ) as response:
                data = await response.json()
            for item in data:
                expansion = msgspec.convert(item, type=models.Set)
                if expansion.id:
                    ret._sets[expansion.id] = expansion
                if expansion.code:
                    ret._sets[expansion.code] = expansion
                if expansion.name:
                    ret._sets[expansion.name] = expansion
            ret._setup()
            return ret
        except Exception:
            LOG.warning("Failed to load VTES from KRCG static", exc_info=True)
            return cls.load()

    def _setup(self) -> None:
        for card in self._cards.cards():
            self._search.add(card)
        with open(PICKLE_FILE, "wb") as f:
            pickle.dump(self, f)

    def __bool__(self) -> bool:
        """Check if the database is not empty."""
        return bool(self._cards)

    def __getitem__(self, key: int | str) -> models.Card:
        """Get a card by ID or name."""
        return self._cards[key]

    def __contains__(self, key: int | str) -> bool:
        """Check if a card is in the database."""
        return key in self._cards

    def __len__(self) -> int:
        """Get the number of cards in the database."""
        return len(self._cards)

    def __iter__(self) -> Generator[models.Card]:
        """Iterate over the cards in the database."""
        return self._cards.cards()

    def get(
        self, key: int | str, default: models.Card | None = None
    ) -> models.Card | None:
        """Get a card by ID or name, or a default value if not found."""
        return self._cards.get(key) or default

    def complete(self, text: str, lang: str = "en") -> list[models.Card]:
        """Card name completion.

        Matches on the start of the name are returned first,
        other matches are returned alphabetically.

        Args:
            text: Parts of the name (can contain spaces).
            lang: Preferred language code (defaults to English).

        Returns:
            Matching cards, sorted from most likely to less likely.
        """
        return self._search.name.search_flat(text, 10, lang)

    @property
    def search_dimensions(self) -> dict[str, list[str | None]]:
        """Get the search dimensions.

        Returns:
            A dictionary of search dimensions and their choices.
            It does not include trie dimensions (text, flavor text, etc.)
        """
        return {
            dimension.value: self._search.choices(dimension)
            for dimension in models.SearchDimension
            if dimension not in self._search._TRIE_DIMENSIONS
        }

    def search(
        self,
        *,
        n: int | None = 100,
        lang: models.Lang = models.Lang.EN,
        **kwargs: list[str],
    ) -> list[models.Card]:
        """Search for cards.

        Args:
            n: The number of cards to return, defaults to 100.
            lang: The language to search in (defaults to English).
            **kwargs: Filter criteria matching the available dimensions.
        """
        return self._search.search(
            {models.SearchDimension(k): v for k, v in kwargs.items()}, n, lang
        )

    def parse(
        self, source: Iterable[str], *, id: str = "", twda: bool = False
    ) -> models.Deck:
        """Parse a deck list, resolving card names against this database.

        Args:
            source: The deck list lines.
            id: The deck id.
            twda: If True, parse the positional TWDA tournament headers.
        """
        return parser.deck_from_txt(source, self._cards, id=id, twda=twda)

    def to_twd(self, deck: models.Deck) -> str:
        """Serialize a deck to TWD (Tournament Winning Deck) text format."""
        return providers.serialize_twd(deck, self._cards)
