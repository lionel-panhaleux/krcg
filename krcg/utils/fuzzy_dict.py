"""Fuzzy dictionary."""

from typing import Any, cast
from collections.abc import (
    Hashable,
    ItemsView,
    Iterator,
    Sequence,
    Mapping,
    MutableMapping,
)
import collections
import difflib
import logging


from .string import normalize


LOG = logging.getLogger("krcg")


class FuzzyDict[H: Hashable, T](MutableMapping[H, T]):
    """A dict providing "fuzzy matching" of its keys.

    It matches keys that are "close enough" if there is no exact match, and
    provides the ability to specify aliases for certain keys. Aliases are only
    matched exactly (not closely like normal keys).
    """

    def __init__(
        self,
        data: Mapping[H, T] | None = None,
        *,
        threshold: int = 6,
        cutoff: float = 0.85,
        aliases: Mapping[Any, Any] | None = None,
    ) -> None:
        """Constructor.

        Args:
            data: Optional initial mapping of keys to values.
            threshold: Minimum string length for fuzzy matching.
            cutoff: Minimum similarity to consider a close candidate a match.
            aliases: Optional mapping of alias keys to canonical keys.
        """
        self._threshold = threshold
        self._cutoff = cutoff
        self._aliases: dict[Hashable, H] = dict(aliases) if aliases else {}
        self._dict: dict[H, T] = dict(data) if data else {}

    def _fuzzy_match(self, key: Hashable) -> H | None:
        """Use difflib to match incomplete or misspelled keys."""
        if not isinstance(key, collections.abc.Sequence):
            return None
        if len(key) < self._threshold:
            return None
        matches = difflib.get_close_matches(
            key,
            [k for k in self._dict.keys() if isinstance(k, Sequence)],
            n=1,
            cutoff=self._cutoff,
        )
        if matches:
            result = cast(H, matches[0])
            LOG.debug('"%s" matched "%s"', key, result)
            self.add_alias(key, result)
            return result
        return None

    def add_alias(self, alias: Hashable, value: H) -> None:
        """Add an alias to the dict.

        The value must be a key in the dict.
        """
        alias = normalize(alias)
        self._aliases[alias] = value

    def clear(self) -> None:
        """Clear the dict."""
        self._dict.clear()
        self._aliases.clear()

    def items(self) -> ItemsView[H, T]:
        """Return the dict items.

        The keys have been normalized (unidecode lowercase), so they may not match
        the keys used for input.

        Aliases are not included.
        """
        return self._dict.items()

    def __getitem__(self, key: H) -> T:
        """Get a key, trying to find a good match.

        It uses lowercase only, plus the provided aliases,
        and uses difflib to fuzzy match incomplete or misspelled keys
        """
        key = normalize(key)
        try:
            return self._dict[key]
        except KeyError:
            # aliases must match exactly
            if key in self._aliases:
                return self._dict[normalize(self._aliases[key])]
            fuzzy_match = self._fuzzy_match(key)
            if fuzzy_match:
                return self._dict[fuzzy_match]
            raise

    def __contains__(self, key: object) -> bool:
        """Check if a key is in the dict (does fuzzy match)."""
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False

    def __setitem__(self, key: H, value: Any) -> None:
        """Set a key."""
        self._dict[normalize(key)] = value

    def __delitem__(self, key: H) -> None:
        """Delete a key."""
        del self._dict[normalize(key)]

    # Required by MutableMapping
    def __len__(self) -> int:
        """Return the number of real keys (no aliases) in the dict."""
        return len(self._dict)

    def __iter__(self) -> Iterator[H]:
        """Iterate over the real keys in the dict (no duplicates from aliases)."""
        return iter(self._dict)
