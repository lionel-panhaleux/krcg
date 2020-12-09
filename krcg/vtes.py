"""This module provides the `VTES` singleton: the VTES cards library.

If it has not been initialized, VTES will evaluate to False.
VTES must be configured with `VTES.configure()` before being used.
"""
from typing import Dict, List
import functools
import requests

from . import cards


class _VTES:
    """VTES cards database"""

    def __init__(self):
        self._cards = cards.CardMap()
        self._search = cards.CardSearch()

    def __bool__(self):
        return bool(self._cards and self._search)

    def __getitem__(self, key):
        return self._cards[key]

    def __contains__(self, key):
        return bool(self[key])

    def __len__(self) -> int:
        return len(self._cards)

    def __iter__(self):
        return self._cards.__iter__()

    def clear(self) -> None:
        self._cards.clear()
        self._search.clear()

    def load(self) -> None:
        """Loaf from KRCG static"""
        self.clear()
        self._cards.load()
        self._init()

    def load_from_vekn(self):
        """Load the card database from vekn.net, with translations and rulings"""
        self.clear()
        self._cards.load_from_vekn()
        self._cards.load_cards_rulings()
        self._init()

    @functools.cached_property
    def amaranth(self):
        """Amaranth IDs card map.

        Cached because Amaranth can take up to 5 seconds to answer that call.
        """
        return {
            int(card["id"]): self._cards[card["name"]]
            for card in (
                requests.get("http://amaranth.vtes.co.nz/api/cards").json()["result"]
            )
            if card["name"] in self._cards  # ignore storyline / experimental cards
        }

    def complete(self, text: str, lang: str = "en") -> List:
        """Card name completion.

        Matches on the start of the name are returned first,
        other matches are returned alphabetically.

        Args:
            text: Parts of the name (can contain spaces)

        Returns:
            A sorted list of results, from most likely to less likely
        """
        ret = self._search.name.search(text, lang)
        ret = [(self._cards[cid].name, score) for cid, score in ret]
        return [x[0] for x in sorted(ret, key=lambda x: (-x[1], x[0]))]

    def search_dimensions(self) -> Dict[str, List[str]]:
        return self._search.dimensions()

    def search(self, **kwargs):
        return self._search(**kwargs)

    def _init(self) -> None:
        """Initialize search and completion"""
        for c in self._cards:
            self._search.add(c)


VTES = _VTES()
