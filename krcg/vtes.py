"""This module provides the `VTES` singleton: the VTES cards library.

If it has not been initialized, VTES will evaluate to False.
VTES must be configured with `VTES.configure()` before being used.
"""

from typing import Dict, Generator, List, Optional, Set, BinaryIO, Literal
import functools
import requests

from . import cards


CardsDiff = Dict[cards.Card, cards.CardDiff | Literal["NEW"]]


class _VTES:
    """VTES cards database."""

    def __init__(self) -> None:
        self._cards = cards.CardMap()
        self._search = cards.CardSearch()

    def __bool__(self) -> bool:
        return bool(self._cards)

    def __getitem__(self, key: int | str) -> cards.Card:
        return self._cards[key]

    def __contains__(self, key: int | str) -> bool:
        return key in self._cards

    def __len__(self) -> int:
        return len(self._cards)

    def __iter__(self) -> Generator[cards.Card, None, None]:
        return self._cards.__iter__()

    def to_json(self) -> list:
        return self._cards.to_json()

    def from_json(self, state: list) -> None:
        self.clear()
        self._cards.from_json(state)

    def get(
        self, key: int | str, default: Optional[cards.Card] = None
    ) -> Optional[cards.Card]:
        return self._cards.get(key) or default

    def clear(self) -> None:
        self._cards.clear()
        self._search.clear()

    def load(self) -> None:
        """Load from KRCG static."""
        self.clear()
        self._cards.load()

    def load_from_vekn(self) -> None:
        """Load the card database from VEKN CSVs or local CSVs (LOCAL_CARDS=1)."""
        self.clear()
        self._cards.load_from_vekn()
        self._cards.load_rulings()

    def load_from_files(
        self, *files: BinaryIO, set_abbrev: Optional[str] = None
    ) -> None:
        self._cards.load_from_files(*files, set_abbrev=set_abbrev)

    def diff(self, url: str) -> CardsDiff:
        """Compute a diff from previous VEKN CSV files."""
        old_cards = cards.CardMap()
        old_cards._VEKN_CSV = (url, old_cards._VEKN_CSV[1])
        old_cards.load_from_vekn()
        res: CardsDiff = {c: "NEW" for c in self._cards if c.id not in old_cards}
        for c in self._cards:
            if c.id in old_cards:
                diff = old_cards[c.id].diff(c)
                if diff:
                    res[c] = diff
        return res

    @property
    @functools.lru_cache(1)
    def amaranth(self) -> Dict[int, cards.Card]:
        """Amaranth IDs card map."""
        r = requests.get("http://static.krcg.org/data/amaranth_ids.json")
        r.raise_for_status()
        return {k: self[v] for k, v in r.json().items()}

    def complete(self, text: str, lang: str = "en") -> List[str]:
        """Card name completion.

        Matches on the start of the name are returned first,
        other matches are returned alphabetically.

        Args:
            text: Parts of the name (can contain spaces).
            lang: Preferred language code (defaults to English).

        Returns:
            Sorted from most likely to less likely.
        """
        self._init_search()
        ret = self._search.name.search(text, lang)
        ret = [
            (card.usual_name if lang == "en" else card.i18n_field(lang, "name"), score)
            for lang, card_score in ret.items()
            for card, score in card_score.items()
        ]
        return [x[0] for x in sorted(ret, key=lambda x: (-x[1], x[0]))]

    @property
    def search_dimensions(self) -> Dict[str, List[str]]:
        self._init_search()
        return self._search.set_dimensions_enums

    def search(self, **kwargs: str | list[str]) -> Set[cards.Card]:
        self._init_search()
        return self._search(**kwargs)

    def _init_search(self) -> None:
        """Initialize search and completion."""
        if not self._search:
            for c in self._cards:
                self._search.add(c)


VTES = _VTES()
