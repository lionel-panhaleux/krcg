"""Generic utilities used by the library.
"""
from typing import (
    Any,
    Dict,
    Generator,
    Hashable,
    ItemsView,
    List,
    Optional,
    Sequence,
    Tuple,
)
import collections
import csv
import difflib
import io
import logging
import re
import unidecode
import urllib.request
import zipfile


logger = logging.getLogger("krcg")


def normalize(s: Any):
    """Normalize a string for indexing: unidecode and lowercase."""
    if not isinstance(s, str):
        return s
    return unidecode.unidecode(s).lower().strip()


def get_zip_csv(url: str, *args: str) -> List[Generator[Dict[str, str], None, None]]:
    """Given a zipfile URL and list of CSV files in it, returns matching CSV readers."""
    local_filename, _headers = urllib.request.urlretrieve(url)
    z = zipfile.ZipFile(local_filename)
    return [csv.DictReader(io.TextIOWrapper(z.open(arg))) for arg in args]


class FuzzyDict:
    """A dict providing "fuzzy matching" of its keys.

    It matches keys that are "close enough" if there are no exact match,
    and provides athe ability to specify aliases for certain keys.

    Aliases are only matched exactly (not closely like normal keys).

    Attributes:
        threshold: minimum string length for fuzzy matching
        cutoff: minimum similarity to consider a close candidate an actual match
        aliases: {alias_key: actual_key} adding not-so-closes aliases
    """

    def __init__(
        self,
        threshold: int = 6,
        cutoff: float = 0.85,
        aliases: dict = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.threshold = threshold
        self.cutoff = cutoff
        self.aliases = aliases
        self._dict = dict()
        self._keys_cache = None

    def _fuzzy_match(self, key: Hashable) -> Any:
        """Use difflib to match incomplete or misspelled keys"""
        if not isinstance(key, collections.abc.Sequence):
            return None
        if len(key) < self.threshold:
            return None
        result = difflib.get_close_matches(
            key, self._sequence_keys(), n=1, cutoff=self.cutoff
        )
        if result:
            result = result[0]
            logger.info('"%s" matched "%s"', key, result)
            return result
        return None

    def _sequence_keys(self) -> List[Sequence]:
        """Return all keys that are sequences and can be fuzzy matched."""
        if not self._keys_cache:
            self._keys_cache = [
                k for k in self._dict.keys() if isinstance(k, collections.abc.Sequence)
            ]
        return self._keys_cache

    def add_alias(self, alias: Hashable, value: Hashable) -> None:
        """Add an alias to the dict.

        The value must be a key in the dict.
        """
        alias = normalize(alias)
        if alias in self.aliases:
            self._clear_cache()
        self.aliases[alias] = value

    def clear(self) -> None:
        """Clear the dict."""
        self._dict.clear()
        self._clear_cache()

    def items(self) -> ItemsView:
        """Return the dict items.

        The keys have been normalized (unidecode lowercase), so they may not match
        the keys used for input.

        Aliases are not included.
        """
        return self._dict.items()

    def __getitem__(self, key: Hashable) -> Any:
        """Get a key, try to find a good matching.

        It uses lowercase only, plus the provided aliases,
        and uses difflib to fuzzy match incomplete or misspelled keys
        """
        key = normalize(key)
        try:
            return self._dict[key]
        except KeyError:
            # aliases must match exactly
            if key in self.aliases:
                return self._dict[normalize(self.aliases[key])]
            fuzzy_match = self._fuzzy_match(key)
            if fuzzy_match:
                return self._dict[fuzzy_match]
            raise

    def get(self, key: Hashable, default=None) -> Any:
        """Get a key, or default."""
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key: Hashable) -> bool:
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False

    def __setitem__(self, key: Hashable, value: Any) -> None:
        # testing for cache validity to avoid clearing it is premature optimization
        # doing a fuzzy match at each insertion is costly
        # the FuzzyDict is more likely to be filled once then used
        self._clear_cache()
        self._dict[normalize(key)] = value

    def __delitem__(self, key: Hashable) -> None:
        self._clear_cache()
        del self._dict[normalize(key)]

    def _clear_cache(self) -> None:
        """Clear the keys cache."""
        self._keys_cache = None


class Trie(collections.defaultdict):
    """A Trie structure for text search.

    It relies on a Python dict with following structure:
    {prefix: {reference: score}}.

    When a (text, reference) couple is entered in the Trie,
    every prefix of every word of the text is added to the Trie,
    pointing to the reference with a score depending on the length
    of the prefix and the position in the text (matching first word is worth double).

    The matches are case-insensitive and use unidecode to handle unicode characters.
    """

    def __init__(self):
        super().__init__(lambda: collections.defaultdict(int))

    @staticmethod
    def _split(text: str) -> List[str]:
        """Normalize the input text, split words"""
        text = normalize(text)
        if not text:
            return []
        return re.sub(r"[/:,\(\)'\"]", " ", text).split()

    def add(self, text: str, reference: Any = None) -> None:
        """Add text to the Trie

        Args:
            text: The text to add.
            reference: The reference to return on a match
        """
        if reference is None:
            reference = text
        for e, part in enumerate(Trie._split(text)):
            for i in range(1, len(part) + 1):
                self[part[:i]][reference] += (
                    # double score for matching name start
                    i
                    * (2 if e == 0 else 1)
                )

    def search(self, text: str) -> Optional[collections.Counter]:
        """Search text into the Trie

        The match is case-insensitive and use unidecode, but is otherwise exact.
        Matching on the first word of a key scores double.
        Only candidates matching all words are returned.

        Args:
            text: The text to search
        Returns:
            Scored references
        """
        ret = None
        for part in Trie._split(text):
            # a word can match multiple parts of a key to one reference
            # take the highest score
            matches = {}
            for reference, score in self.get(part, {}).items():
                matches[reference] = max(matches.get(reference, 0), score)
            # match all words of given text
            if ret is not None:
                ret = collections.Counter(
                    {k: v + matches[k] for k, v in ret.items() if k in matches}
                )
            else:
                ret = collections.Counter(matches)
        return ret


def json_pack(obj: Any) -> Any:
    """Remove empty values in depth.

    Used to prepare dicts or lists for a compact JSON serialization.
    """
    if isinstance(obj, dict):
        to_delete = []
        for k, v in obj.items():
            json_pack(v)
            if not v:
                to_delete.append(k)
        for k in to_delete:
            del obj[k]
    elif isinstance(obj, list):
        to_delete = []
        for i, v in enumerate(obj):
            json_pack(v)
            if not v:
                to_delete.append(i)
        for i in to_delete:
            obj.pop(i)
    return obj


class i18nMixin:
    """A mixin for translations.

    It add an `_i18n` attribute to the object,
    and provides simple methods to manipulate it.
    """

    def __init__(self):
        super().__init__()
        self._i18n = collections.defaultdict(dict)

    def i18n_set(self, lang: str, trans: Dict[str, str]) -> None:
        for field, value in trans.items():
            if value and not hasattr(self, field):
                raise ValueError(f'i18n: "{field}" not present on instance')
        self._i18n[lang[:2]].update(trans)

    def i18n_variants(self, field: str) -> Generator[Tuple[str, Any], None, None]:
        for lang, trans in self._i18n.items():
            if field in trans:
                yield lang, trans[field]

    def i18n(self, lang: str, field: str = None) -> Any:
        if lang[:2] == "en":
            if field:
                return getattr(self, field)
            else:
                return self
        ret = self._i18n.get(lang[:2], {})
        if not field:
            return ret
        return ret.get(field)


class NamedMixin:
    """A mixin for objects with name and ID.

    It provides bool, int, str and repr conversions for convenience,
    as well as hash and comparison operations so that the object can be indexed.
    """

    def __bool__(self):
        return bool(self.id)

    def __index__(self):
        return self.id

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__} #{self.id} {self.name}>"

    def __hash__(self):
        return self.id

    def __eq__(self, rhs: Any):
        return rhs and self.id == getattr(rhs, "id", None)

    def __lt__(self, rhs: Any):
        return rhs and hasattr(rhs, "name") and self.name < rhs.name
