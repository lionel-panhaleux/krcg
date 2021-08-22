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
        return bool(self._cards)

    def __getitem__(self, key):
        return self._cards[key]

    def __contains__(self, key):
        return key in self._cards

    def __len__(self) -> int:
        return len(self._cards)

    def __iter__(self):
        return self._cards.__iter__()

    def to_json(self):
        return [c.to_json() for c in self._cards]

    def from_json(self, state):
        self.clear()
        for c in state:
            card = cards.Card()
            card.from_json(c)
            self._cards.add(card)

    def get(self, key, default=None):
        return self._cards.get(key)

    def clear(self) -> None:
        self._cards.clear()
        self._search.clear()

    def load(self) -> None:
        """Load from KRCG static"""
        self.clear()
        self._cards.load()

    def load_from_vekn(self):
        """Load the card database from vekn.net, with translations and rulings"""
        self.clear()
        self._cards.load_from_vekn()
        self._cards.load_rulings()

    def diff(self, url):
        """Compute a diff from previous VEKN CSV files."""
        old_cards = cards.CardMap()
        old_cards._VEKN_CSV[0] = url
        old_cards.load_from_vekn()
        res = {
            c: "NEW"
            for c in self._cards if c.id not in old_cards
        }
        for c in self._cards:
            if c.id in old_cards:
                diff = old_cards[c.id].diff(c)
                if diff:
                    res[c] = diff
        return res

    @property
    @functools.lru_cache(1)
    def amaranth(self):
        """Amaranth IDs card map."""
        r = requests.get("http://static.krcg.org/data/amaranth_ids.json")
        r.raise_for_status()
        return {k: self[v] for k, v in r.json().items()}

    def complete(self, text: str, lang: str = "en") -> List:
        """Card name completion.

        Matches on the start of the name are returned first,
        other matches are returned alphabetically.

        Args:
            text: Parts of the name (can contain spaces)

        Returns:
            A sorted list of results, from most likely to less likely
        """
        self._init_search()
        ret = self._search.name.search(text, lang)
        ret = [
            (card.name if lang == "en" else card.i18n(lang, "name"), score)
            for lang, card_score in ret.items()
            for card, score in card_score.items()
        ]
        return [x[0] for x in sorted(ret, key=lambda x: (-x[1], x[0]))]

    @property
    def search_dimensions(self) -> Dict[str, List[str]]:
        self._init_search()
        return self._search.set_dimensions_enums

    def search(self, **kwargs):
        self._init_search()
        return self._search(**kwargs)

    def _init_search(self) -> None:
        """Initialize search and completion"""
        if not self._search:
            for c in self._cards:
                self._search.add(c)


VTES = _VTES()
