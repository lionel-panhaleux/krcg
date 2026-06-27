"""A prefix tree for scored, case-insensitive text search."""

from typing import Any, SupportsIndex, cast
from collections.abc import Hashable, Mapping
import collections
import logging
import re

from .string import normalize

LOG = logging.getLogger("krcg")


def _default_trie_factory() -> "collections.defaultdict[Any, int]":
    """Factory function for Trie default values."""
    return collections.defaultdict(int)


class Trie[H: Hashable](collections.defaultdict[str, dict[H, int]]):
    """A Trie structure for text search.

    It relies on a Python dict with following structure:
    {prefix: {reference: score}}.

    When a (text, reference) couple is entered in the Trie,
    every prefix of every word of the text is added to the Trie,
    pointing to the reference with a score depending on the length
    of the prefix and the position in the text (matching first word is worth double).

    The matches are case-insensitive and use unidecode to handle unicode characters.
    """

    def __init__(self, data: Mapping[str, dict[H, int]] | None = None) -> None:
        """Constructor."""
        super().__init__(_default_trie_factory)
        # If args provided, update with them (for unpickling)
        if data:
            self.update(data)

    def __reduce_ex__(self, protocol: SupportsIndex) -> tuple[Any, ...]:
        """Custom pickle support to avoid issues with defaultdict."""
        return (
            self.__class__,
            (dict(self),),
            None,
            None,
            None,
        )

    @staticmethod
    def _split(text: str) -> list[str]:
        """Normalize input text and split into words."""
        text = normalize(text)
        if not text:
            return []
        return re.sub(r"[/:,\(\)'\"]", " ", text).split()

    def add(self, text: str, reference: H) -> None:
        """Add text to the trie.

        Args:
            text: The text to add.
            reference: The reference to return on a match.
        """
        if reference is None:
            reference = cast(H, text)
        for e, part in enumerate(Trie._split(text)):
            for i in range(1, len(part) + 1):
                self[part[:i]][reference] += (
                    # double score for matching name start
                    i * (2 if e == 0 else 1)
                )

    def search(self, text: str) -> collections.Counter[H]:
        """Search text in the trie.

        The match is case-insensitive and uses unidecode, but is otherwise exact.
        Matching on the first word of a key scores double. Only candidates matching
        all words are returned.

        Args:
            text: The text to search.

        Returns:
            Scored references.
        """
        ret: collections.Counter[H] | None = None
        for part in Trie._split(text):
            # a word can match multiple parts of a key to one reference
            # take the highest score
            matches: dict[H, int] = {}
            for reference, score in self.get(part, {}).items():
                matches[reference] = max(matches.get(reference, 0), score)
            # match all words of given text
            if ret is not None:
                ret = collections.Counter[H](
                    {k: v + matches[k] for k, v in ret.items() if k in matches}
                )
            else:
                ret = collections.Counter[H](matches)
        if ret is None:
            ret = collections.Counter[H]()
        return ret
