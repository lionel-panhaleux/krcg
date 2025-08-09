"""Generic utilities used by the library."""

from typing import (
    Any,
    Dict,
    Generator,
    Generic,
    Hashable,
    ItemsView,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Mapping,
    MutableMapping,
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


def get_zip_csv(url: str, *args: str) -> List[csv.DictReader[str]]:
    """Return CSV readers for files inside a remote ZIP archive.

    Files are fully read into memory to ensure underlying file descriptors are
    closed immediately.
    """
    local_filename, _headers = urllib.request.urlretrieve(url)
    readers: List[csv.DictReader[str]] = []
    with zipfile.ZipFile(local_filename) as z:
        for arg in args:
            data = z.read(arg).decode("utf-8-sig")
            readers.append(csv.DictReader(io.StringIO(data)))
    return readers


def get_github_csv(url: str, *args: str) -> List[csv.DictReader[str]]:
    """Return CSV readers for files hosted under a base URL (e.g., GitHub).

    Files are fully read into memory to ensure underlying file descriptors are
    closed immediately.
    """
    readers: List[csv.DictReader[str]] = []
    for arg in args:
        local_filename, _headers = urllib.request.urlretrieve(url + arg)
        with open(local_filename, encoding="utf-8-sig") as f:
            data = f.read()
        readers.append(csv.DictReader(io.StringIO(data)))
    return readers


T = TypeVar("T")


class FuzzyDict(MutableMapping[Hashable, T], Generic[T]):
    """A dict providing "fuzzy matching" of its keys.

    It matches keys that are "close enough" if there is no exact match, and
    provides the ability to specify aliases for certain keys. Aliases are only
    matched exactly (not closely like normal keys).

    Args:
        threshold: Minimum string length for fuzzy matching.
        cutoff: Minimum similarity to consider a close candidate a match.
        aliases: Optional mapping of alias keys to canonical keys.
        *args: Additional mapping args passed to ``Mapping``.
        **kwargs: Additional mapping kwargs passed to ``Mapping``.
    """

    def __init__(
        self,
        threshold: int = 6,
        cutoff: float = 0.85,
        aliases: Optional[Mapping[Any, Any]] = None,
        *args,
        **kwargs,
    ):
        self.threshold = threshold
        self.cutoff = cutoff
        self.aliases: dict[Hashable, T] = dict(aliases) if aliases else {}
        self._dict: dict[Hashable, T] = dict(*args, **kwargs)
        self._keys_cache: Optional[List[Sequence]] = None

    def _fuzzy_match(self, key: Hashable) -> Hashable:
        """Use difflib to match incomplete or misspelled keys."""
        if not isinstance(key, collections.abc.Sequence):
            return None
        if len(key) < self.threshold:
            return None
        matches = difflib.get_close_matches(
            key, self._sequence_keys(), n=1, cutoff=self.cutoff
        )
        if matches:
            result = matches[0]
            logger.info('"%s" matched "%s"', key, result)
            return result
        return None

    def _sequence_keys(self) -> List[Sequence]:
        """Return all keys that are sequences and can be fuzzy matched."""
        if not self._keys_cache:
            self._keys_cache = [k for k in self._dict.keys() if isinstance(k, Sequence)]
        return self._keys_cache

    def add_alias(self, alias: Hashable, value: T) -> None:
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

    def items(self) -> ItemsView[Hashable, T]:
        """Return the dict items.

        The keys have been normalized (unidecode lowercase), so they may not match
        the keys used for input.

        Aliases are not included.
        """
        return self._dict.items()

    def __getitem__(self, key: Hashable) -> Any:
        """Get a key, trying to find a good match.

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

    # Required by MutableMapping
    def __len__(self) -> int:  # type: ignore[override]
        return len(self._dict)

    def __iter__(self):  # type: ignore[override]
        return iter(self._dict)


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
        """Normalize input text and split into words."""
        text = normalize(text)
        if not text:
            return []
        return re.sub(r"[/:,\(\)'\"]", " ", text).split()

    def add(self, text: str, reference: Any = None) -> None:
        """Add text to the trie.

        Args:
            text: The text to add.
            reference: The reference to return on a match.
        """
        if reference is None:
            reference = text
        for e, part in enumerate(Trie._split(text)):
            for i in range(1, len(part) + 1):
                self[part[:i]][reference] += (
                    # double score for matching name start
                    i * (2 if e == 0 else 1)
                )

    def search(self, text: str) -> collections.Counter:
        """Search text in the trie.

        The match is case-insensitive and uses unidecode, but is otherwise exact.
        Matching on the first word of a key scores double. Only candidates matching
        all words are returned.

        Args:
            text: The text to search.
        Returns:
            Scored references.
        """
        ret: Optional[collections.Counter] = None
        for part in Trie._split(text):
            # a word can match multiple parts of a key to one reference
            # take the highest score
            matches: dict[str, int] = {}
            for reference, score in self.get(part, {}).items():
                matches[reference] = max(matches.get(reference, 0), score)
            # match all words of given text
            if ret is not None:
                ret = collections.Counter(
                    {k: v + matches[k] for k, v in ret.items() if k in matches}
                )
            else:
                ret = collections.Counter(matches)
        if ret is None:
            ret = collections.Counter()
        return ret


def json_pack(obj: Any) -> Any:
    """Remove empty values recursively.

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


Trans = str | dict[str, str] | list[str]


class i18nMixin:
    """A mixin for translations.

    It adds an `_i18n` attribute to the object,
    and provides simple methods to manipulate it.
    """

    def __init__(self):
        super().__init__()
        self._i18n = collections.defaultdict(dict)

    def i18n_set(self, lang: str, trans: Dict[str, Trans]) -> None:
        for field, value in trans.items():
            if value and not hasattr(self, field):
                raise ValueError(f'i18n: "{field}" not present on instance')
        self._i18n[lang[:2]].update(trans)

    def i18n_variants(self, field: str) -> Generator[Tuple[str, Trans], None, None]:
        for lang, trans in self._i18n.items():
            if field in trans:
                yield lang, trans[field]

    def i18n(self, lang: str) -> Dict[str, Trans]:
        if lang[:2] == "en":
            return self.__dict__
        return self._i18n.get(lang[:2], {})

    def i18n_field(self, lang: str, field: str) -> str:
        if lang[:2] == "en":
            return getattr(self, field)
        ret = self._i18n.get(lang[:2], {})
        return ret.get(field) or ""


class NamedMixin:
    """A mixin for objects with name and ID.

    It provides bool, int, str and repr conversions for convenience,
    as well as hash and comparison operations so that the object can be indexed.
    """

    def __bool__(self) -> bool:
        return bool(self.id)  # type: ignore

    def __index__(self) -> int:
        return self.id  # type: ignore

    def __str__(self) -> str:
        return self.name  # type: ignore

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} #{self.id} {self.name}>"  # type: ignore

    def __hash__(self) -> int:
        return self.id  # type: ignore

    def __eq__(self, rhs: Any) -> bool:
        return rhs and self.id == getattr(rhs, "id", None)  # type: ignore

    def __lt__(self, rhs: Any) -> bool:
        return rhs and hasattr(rhs, "name") and self.name < rhs.name  # type: ignore
