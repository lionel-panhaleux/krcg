"""Generic utilities used by the library."""

from typing import (
    Any,
    Generic,
    Hashable,
    ItemsView,
    Iterator,
    List,
    Optional,
    Sequence,
    TypeVar,
    Mapping,
    MutableMapping,
)
import collections
import csv
import dataclasses
import difflib
import enum
import functools
import datetime
import io
import logging
import re
import unidecode
import urllib.request
import zipfile


logger = logging.getLogger("krcg")


def normalize(s: Any) -> Any:
    """Normalize a string for indexing: unidecode and lowercase."""
    if not isinstance(s, str):
        return s
    return unidecode.unidecode(s).lower().strip()


def get_zip_csv(url: str, *args: str) -> List[csv.DictReader]:
    """Return CSV readers for files inside a remote ZIP archive.

    Files are fully read into memory to ensure underlying file descriptors are
    closed immediately.
    """
    local_filename, _headers = urllib.request.urlretrieve(url)
    readers: List[csv.DictReader] = []
    with zipfile.ZipFile(local_filename) as z:
        for arg in args:
            data = z.read(arg).decode("utf-8-sig")
            readers.append(csv.DictReader(io.StringIO(data)))
    return readers


def get_github_csv(url: str, *args: str) -> List[csv.DictReader]:
    """Return CSV readers for files hosted under a base URL (e.g., GitHub).

    Files are fully read into memory to ensure underlying file descriptors are
    closed immediately.
    """
    readers: List[csv.DictReader] = []
    for arg in args:
        local_filename, _headers = urllib.request.urlretrieve(url + arg)
        with open(local_filename, encoding="utf-8-sig") as f:
            data = f.read()
        readers.append(csv.DictReader(io.StringIO(data)))
    return readers


T = TypeVar("T")
H = TypeVar("H", bound=Hashable)


class FuzzyDict(MutableMapping[H, T], Generic[H, T]):
    """A dict providing "fuzzy matching" of its keys.

    It matches keys that are "close enough" if there is no exact match, and
    provides the ability to specify aliases for certain keys. Aliases are only
    matched exactly (not closely like normal keys).
    """

    def __init__(
        self,
        *args: Any,
        threshold: int = 6,
        cutoff: float = 0.85,
        aliases: Optional[Mapping[Any, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            threshold: Minimum string length for fuzzy matching.
            cutoff: Minimum similarity to consider a close candidate a match.
            aliases: Optional mapping of alias keys to canonical keys.
            *args: Additional mapping args passed to internal _dict.
            **kwargs: Additional mapping kwargs passed to internal _dict.
        """
        self._threshold = threshold
        self._cutoff = cutoff
        self._aliases: dict[Hashable, H] = dict(aliases) if aliases else {}
        self._dict: dict[H, T] = dict(*args, **kwargs)

    def _fuzzy_match(self, key: Hashable) -> Optional[H]:
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
            result = matches[0]
            logger.info('"%s" matched "%s"', key, result)
            self.add_alias(key, result)
            return result  # type: ignore
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

    def get(self, key: H, default: Any = None) -> Any:
        """Get a key, or default."""
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key: object) -> bool:
        """Check if a key is in the dict (does fuzzy match)."""
        try:
            self.__getitem__(key)  # type: ignore
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


def _default_trie_factory():
    """Factory function for Trie default values."""
    return collections.defaultdict(int)


class Trie(collections.defaultdict[str, dict[H, int]], Generic[H]):
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

    def __reduce_ex__(self, protocol):
        """Custom pickle support to avoid issues with defaultdict."""
        # Return a tuple: (callable, args) where callable(*args) recreates the object
        return (
            self.__class__,
            (dict(self),),  # Pass the dict data as a single argument
            None,
            None,
            None,
        )

    @staticmethod
    def _split(text: str) -> List[str]:
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
            reference = text
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
            matches: dict[str, int] = {}
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


@functools.singledispatch
def json_encode(x: Any) -> Any:
    """Encode a value for JSON."""
    if dataclasses.is_dataclass(x):
        return json_encode(dataclasses.asdict(x))
    return x


@json_encode.register(dict)
def _encode_dict(x: dict) -> dict:
    ret = {k: json_encode(v) for k, v in x.items()}
    return {k: v for k, v in ret.items() if v}


@json_encode.register(FuzzyDict)
def _encode_fuzzy_dict(x: FuzzyDict) -> dict:
    ret = {k: json_encode(v) for k, v in x.items()}
    return {k: v for k, v in ret.items() if v}


@json_encode.register(list)
def _encode_list(x: list) -> list:
    ret = [json_encode(v) for v in x]
    return [v for v in ret if v]


@json_encode.register(enum.Enum)
def _encode_list(x: enum.Enum) -> str:
    return x.value


@json_encode.register(datetime.datetime)
@json_encode.register(datetime.date)
def _encode_datetime(x: datetime.date | datetime.datetime) -> str:
    return x.isoformat()
