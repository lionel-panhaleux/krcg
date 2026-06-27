"""Collections of cards."""

from collections.abc import Generator, Hashable
import collections
import msgspec
import re

from . import models
from . import utils

#: a set-dimension index: value (or None) -> matching cards
type SetIndex = collections.defaultdict[str | None, set[models.Card]]


class CardDict(utils.FuzzyDict[int | str, models.Card]):
    """A smart dictionary of cards.

    int keys are card IDs
    str keys are card names and variants (old name, translation, nickname)
    """

    def __init__(self, cards: dict[int, models.Card] | None = None) -> None:
        """Index the given cards by id and by every name variant.

        The search index stays empty until `index()` runs; the loaders call it
        once cards and rulings are in place.
        """
        super().__init__()
        self.sets: dict[int | str, models.Set] = {}
        self.search_index = CardSearch()
        for card in (cards or {}).values():
            self.add(card)

    def cards(self) -> Generator[models.Card]:
        """Iterate over cards (values) once each (int keys are the card ids)."""
        for key, card in self.items():
            if isinstance(key, int):
                yield card

    def __len__(self) -> int:
        """Return the number of distinct cards in the map."""
        return sum(1 for _ in self.cards())

    def add(self, card: models.Card) -> None:
        """Add a card."""
        self[card.id] = card
        # always unique: for vampires, includes group and advanced suffix
        self[card.full_name] = card
        if card.unique_name != card.full_name:
            # this is the printed name if it's unique
            self[card.unique_name] = card
        for variant in card.name_variants:
            if variant.type == models.NameVariant.Type.LEXICOGRAPHICAL:
                self[variant.name] = card
            else:
                self.add_alias(variant.name, card.id)

    def pack(self) -> dict[str, models.Card]:
        """Pack for export."""
        return {str(card.id): card for card in self.cards()}

    def card_in_deck(self, card_id: int | str, count: int) -> models.CardInDeck:
        """Get a card for a deck."""
        return msgspec.convert(
            msgspec.to_builtins(self[int(card_id)]) | {"count": count},
            models.CardInDeck,
        )

    def index(self) -> None:
        """Build the search index over the current cards.

        Call this after loading (or mutating) the cards; the loaders do it for
        you. `complete` and `search` return nothing until it has run.
        """
        self.search_index = CardSearch()
        for card in self.cards():
            self.search_index.add(card)

    def complete(self, text: str, lang: str = models.Lang.EN) -> list[models.Card]:
        """Complete a card name.

        Matches on the start of the name come first, the rest alphabetically.

        Args:
            text: Part of the name (may contain spaces).
            lang: Preferred language code (defaults to English).

        Returns:
            Matching cards, most likely first.
        """
        return self.search_index.name.search_flat(text, 10, lang)

    def search(
        self,
        *,
        n: int | None = 100,
        lang: models.Lang = models.Lang.EN,
        **criteria: list[str],
    ) -> list[models.Card]:
        """Search cards across the available dimensions.

        Args:
            n: Maximum number of cards to return (defaults to 100).
            lang: Language to search text dimensions in (defaults to English).
            **criteria: Dimension filters, e.g. `clan=["Brujah"], sect=["Sabbat"]`.
                See `search_dimensions` for the valid keys and their values.

        Returns:
            The matching cards, sorted by name.
        """
        return self.search_index.search(
            {models.SearchDimension(k): v for k, v in criteria.items()}, n, lang
        )

    @property
    def search_dimensions(self) -> dict[str, list[str | None]]:
        """The set dimensions and their possible values.

        Text (trie) dimensions are excluded as they have no enumerable choices.

        Returns:
            A mapping of dimension name to its choices (None marks "no value").
        """
        return {
            dimension.value: self.search_index.choices(dimension)
            for dimension in models.SearchDimension
            if dimension not in self.search_index._TRIE_DIMENSIONS
        }


class i18nTrie[H: Hashable](dict[str, utils.Trie[H]]):
    """A Trie structure for text search with i18n support."""

    def add(self, text: str, item: H, lang: str = models.Lang.EN) -> None:
        """Add text to the trie.

        Args:
            text: The text to add.
            item: The item to return on a match.
            lang: The language of the text.
        """
        if lang not in self:
            self[lang] = utils.Trie[H]()
        self[lang].add(text, item)

    def search(self, text: str, lang: str = models.Lang.EN) -> collections.Counter[H]:
        """Search text in the trie.

        Args:
            text: The text to search.
            lang: The language of the text.
        """
        result = self[models.Lang.EN].search(text)
        if lang != models.Lang.EN and lang in self:
            result.update(self[lang].search(text))
        return result

    def search_flat(
        self, text: str, n: int | None = None, lang: str = models.Lang.EN
    ) -> list[H]:
        """Search text, return n items as a flat list in order of score.

        Args:
            text: The text to search.
            n: The number of items to return, dfaults to None to return all items.
            lang: The language of the text.
        """
        return [a[0] for a in self.search(text, lang).most_common(n)]


class CardSearch:
    """A class indexing cards over multiple dimensions, for search purposes.

    Set dimensions are simple sets indexing specific values.
    They can be searched for any combination of values.
    They are all case insensitive, except for the `discipline` dimension.
    Only cards matching all values are returned (AND combination),
    combined successive calls to get OR combinations.

    Trie dimensions provide prefix-based case insensitive text search.
    As for set dimensions, only card with words matching all prefixes are returned.
    """

    _TRIE_DIMENSIONS = [
        models.SearchDimension.NAME,
        models.SearchDimension.CARD_TEXT,
        models.SearchDimension.FLAVOR_TEXT,
    ]
    # for those dimensions, all values must match, for others, any value can match (or).
    _INTERSECT_SET_DIMENSIONS = ["trait", "discipline", "bonus"]

    def __init__(self) -> None:
        """Constructor."""
        self.name = i18nTrie[models.Card]()
        self.card_text = i18nTrie[models.Card]()
        self.flavor_text = i18nTrie[models.Card]()
        self.kind: SetIndex = collections.defaultdict(set)
        self.type: SetIndex = collections.defaultdict(set)
        self.sect: SetIndex = collections.defaultdict(set)
        self.clan: SetIndex = collections.defaultdict(set)
        self.path: SetIndex = collections.defaultdict(set)
        self.title: SetIndex = collections.defaultdict(set)
        self.city: SetIndex = collections.defaultdict(set)
        self.trait: SetIndex = collections.defaultdict(set)
        self.group: SetIndex = collections.defaultdict(set)
        self.capacity: SetIndex = collections.defaultdict(set)
        self.discipline: SetIndex = collections.defaultdict(set)
        self.artist: SetIndex = collections.defaultdict(set)
        self.set: SetIndex = collections.defaultdict(set)
        self.rarity: SetIndex = collections.defaultdict(set)
        self.precon: SetIndex = collections.defaultdict(set)
        self.bonus: SetIndex = collections.defaultdict(set)

    def add(self, card: models.Card) -> None:
        """Add a card to the right search indexes."""
        for dimension in models.SearchDimension:
            values = get_dimension_values(card, dimension)
            if dimension in self._TRIE_DIMENSIONS:
                assert isinstance(values, dict)
                for lang, values_list in values.items():
                    for value in values_list:
                        getattr(self, dimension.value).add(value, card, lang)
            else:
                assert isinstance(values, list)
                if not values:
                    getattr(self, dimension.value)[None].add(card)
                else:
                    for value in values:
                        getattr(self, dimension.value)[value].add(card)

    def choices(self, dimension: models.SearchDimension) -> list[str | None]:
        """Get the choices for a dimension (None marks cards with no value)."""
        if dimension in self._TRIE_DIMENSIONS:
            raise ValueError(f"{dimension.value} is a trie dimension")
        else:
            res: list[str | None] = (
                [None] if None in getattr(self, dimension.value) else []
            )
            res.extend(
                sorted(
                    k for k in getattr(self, dimension.value).keys() if k is not None
                )
            )
            return res

    def search(
        self,
        filters: dict[models.SearchDimension, list[str]],
        n: int | None = None,
        lang: models.Lang = models.Lang.EN,
    ) -> list[models.Card]:
        """Search for a value in a dimension.

        Args:
            filters: The filters to apply.
            n: The number of cards to return, defaults to None to return all cards.
            lang: The language to search in (only matters for trie dimensions).

        Returns:
            The list of cards matching the filters.
        """
        ret = set[models.Card]()
        first = True
        for dimension, values in filters.items():
            # allow dim="value" as shorthand for dim=["value"]
            if isinstance(values, str):
                values = [values]
            sub_result = set[models.Card]()
            # for trie dimensions, multiple values is an OR
            # Trie does intersection when multiple words are in a single value
            if dimension in self._TRIE_DIMENSIONS:
                for value in values:
                    if not value:
                        continue
                    sub_result.update(
                        getattr(self, dimension.value).search_flat(value, n, lang)
                    )
            else:
                sub_first = True
                for value in values:
                    if not value and value is not None:
                        continue
                    internal_result = getattr(self, dimension.value)[value]
                    if sub_first:
                        sub_result = set(internal_result)
                    elif dimension in self._INTERSECT_SET_DIMENSIONS:
                        sub_result &= internal_result
                    else:
                        sub_result |= internal_result
                    sub_first = False
            if first:
                ret = set(sub_result)
            else:
                ret &= sub_result
            first = False
        return sorted(ret, key=lambda x: x.printed_name)[:n]


def get_dimension_values(
    card: models.Card, dimension: models.SearchDimension
) -> dict[models.Lang, list[str]] | list[str]:
    """Get the values of a dimension for a card.

    Trie dimensions (name, card/flavor text) return a per-language dict;
    set dimensions return a flat list.
    """
    match dimension:
        case models.SearchDimension.NAME:
            ret = {
                models.Lang.EN: [card.full_name, card.unique_name, card.printed_name]
            }
            for variant in card.name_variants:
                ret[models.Lang.EN].append(variant.name)
            for lang, translation in card.i18n.items():
                ret[lang] = [translation.name]
            return ret
        case models.SearchDimension.CARD_TEXT:
            ret = {models.Lang.EN: [card.text]}
            for lang, translation in card.i18n.items():
                ret[lang] = [translation.text]
            return ret
        case models.SearchDimension.FLAVOR_TEXT:
            ret = {models.Lang.EN: [card.flavor] if card.flavor else []}
            for lang, translation in card.i18n.items():
                if translation.flavor:
                    ret[lang] = [translation.flavor]
            return ret
        case models.SearchDimension.KIND:
            return [card.kind.value]
        case models.SearchDimension.TYPE:
            return [t.value for t in card.types]
        case models.SearchDimension.CLAN:
            if isinstance(card, models.LibraryCard):
                return card.clan_requirement
            if isinstance(card, models.CryptCard):
                return [card.clan]
            return []
        case models.SearchDimension.DISCIPLINE:
            if isinstance(card, models.LibraryCard):
                req = card.discipline_requirement
                return req.disciplines if req else []
            if not isinstance(card, models.CryptCard):
                return []
            disciplines = set(card.disciplines)
            if card.id == 200553:  # Gwen Brand: superior disciplines from merged forms
                disciplines |= {"ANI", "AUS", "CHI", "FOR"}
            # also index the inferior base of each (maybe superior) discipline,
            # so a search for "ani" matches superior-only "ANI" too
            return sorted(disciplines | {d.lower() for d in disciplines})
        case models.SearchDimension.GROUP:
            if isinstance(card, models.CryptCard) and card.group:
                return [card.group.value]
            return []
        case models.SearchDimension.SECT:
            return [s.value for s in _get_sects(card)]
        case models.SearchDimension.PATH:
            if isinstance(card, models.LibraryCard):
                return card.path_requirement
            if isinstance(card, models.CryptCard) and card.path:
                return [card.path]
            return []
        case models.SearchDimension.BONUS:
            return [b.value for b in _get_bonus(card)]
        case models.SearchDimension.TITLE:
            return [t.value for t in _get_titles(card)]
        case models.SearchDimension.CITY:
            city = _get_city(card)
            return [city] if city else []
        case models.SearchDimension.TRAIT:
            return [t.value for t in _get_traits(card)]
        case models.SearchDimension.ARTIST:
            return [a for a in card.artists]
        case models.SearchDimension.SET:
            return [p.set.code for p in card.prints]
        case models.SearchDimension.RARITY:
            return [
                o.frequency.value
                for p in card.prints
                for o in p.occurrences
                if o.type == models.Occurrence.Type.RARITY and o.frequency
            ]
        case models.SearchDimension.PRECON:
            return [
                f"{p.set.code}:{o.bundle}"
                for p in card.prints
                for o in p.occurrences
                if o.type == models.Occurrence.Type.PRECON and o.bundle
            ]
        case models.SearchDimension.CAPACITY:
            if isinstance(card, models.CryptCard) and card.capacity:
                return [str(card.capacity)]
            return []


TITLES_RE = r"({})".format("|".join(t.value.lower() for t in models.Title))
TITLES_SECT = {
    models.Title.PRIMOGEN: models.Sect.CAMARILLA,
    models.Title.PRINCE: models.Sect.CAMARILLA,
    models.Title.JUSTICAR: models.Sect.CAMARILLA,
    models.Title.INNER_CIRCLE: models.Sect.CAMARILLA,
    models.Title.IMPERATOR: models.Sect.CAMARILLA,
    models.Title.BISHOP: models.Sect.SABBAT,
    models.Title.ARCHBISHOP: models.Sect.SABBAT,
    models.Title.CARDINAL: models.Sect.SABBAT,
    models.Title.REGENT: models.Sect.SABBAT,
    models.Title.PRISCUS: models.Sect.SABBAT,
    models.Title.BARON: models.Sect.ANARCH,
    models.Title.MAGAJI: models.Sect.LAIBON,
    models.Title.KHOLO: models.Sect.LAIBON,
    models.Title.VOTE_1: models.Sect.INDEPENDENT,
    models.Title.VOTE_2: models.Sect.INDEPENDENT,
}
SECT_TITLES = {
    s: [t for t, v in TITLES_SECT.items() if v == s] for s in set(TITLES_SECT.values())
}
CITY_RE = r"(?:Prince|Baron|Archbishop) of ((?:[A-Z][\w\s-]{3,})+)"
SECTS_RE = r"({}|\[merged\])".format("|".join(t.value.lower() for t in models.Sect))
CRYPT_TITLES_RE = SECTS_RE + r"\.?\s(\w|\s)*?" + TITLES_RE
LIBRARY_TITLES_RE = "({})".format(
    "|".join(
        t.value.lower()
        for t in models.Title
        if t not in [models.Title.VOTE_1, models.Title.VOTE_2]
    )
)


def _get_sects(card: models.Card) -> list[models.Sect]:
    """Index sect information for a card."""
    ret = set[models.Sect]()
    if card.kind == models.Card.Kind.CRYPT:
        if re.search(r"^(\[MERGED\] )?Sabbat", card.text):
            ret.add(models.Sect.SABBAT)
        if re.search(r"^(\[MERGED\] )?Camarilla", card.text):
            ret.add(models.Sect.CAMARILLA)
        if re.search(r"^(\[MERGED\] )?Laibon", card.text):
            ret.add(models.Sect.LAIBON)
        if re.search(r"^(\[MERGED\] )?Anarch", card.text):
            ret.add(models.Sect.ANARCH)
        if re.search(r"^(\[MERGED\] )?Independent", card.text):
            ret.add(models.Sect.INDEPENDENT)
    else:
        if re.search(r"Requires a( ready)?( titled)? (S|s)abbat", card.text):
            ret.add(models.Sect.SABBAT)
        if re.search(r"Requires a( ready)?( titled)? (C|c)amarilla", card.text):
            ret.add(models.Sect.CAMARILLA)
        if re.search(r"Requires a( ready)?( titled)? (L|l)aibon", card.text):
            ret.add(models.Sect.LAIBON)
        if re.search(
            r"Requires a( ready|n)( (I|i)ndependent or)?( titled)? (A|a)narch",
            card.text,
        ):
            ret.add(models.Sect.ANARCH)
        if re.search(r"Requires a( ready|n) (I|i)ndependent", card.text):
            ret.add(models.Sect.INDEPENDENT)
        match = re.search(LIBRARY_TITLES_RE, card.text.lower())
        if match:
            ret.add(TITLES_SECT[models.Title(match.group(1).title())])
    return sorted(ret)


def _get_bonus(card: models.Card) -> list[models.Bonus]:
    """Bonuses a card provides."""
    ret = set[models.Bonus]()
    if re.search(r"\+(\d|X)\s+(i|I)ntercept", card.text):
        ret.add(models.Bonus.INTERCEPT)
    # do not include stealthed actions as stealth cards
    if re.search(r"\+(\d|X)\s+(s|S)tealth (?!Ⓓ|action|political)", card.text):
        ret.add(models.Bonus.STEALTH)
    # stealth/intercept maluses count as bonus of the other
    if not set(card.types) & {"Master", "Vampire", "Imbued"}:
        if re.search(r"-(\d|X)\s+(s|S)tealth", card.text):
            ret.add(models.Bonus.INTERCEPT)
        if re.search(r"(s|S)tealth\s+to\s+(0|zero)", card.text):
            ret.add(models.Bonus.INTERCEPT)
        if re.search(r"-(\d|X)\s+(i|I)ntercept", card.text):
            ret.add(models.Bonus.STEALTH)
        if re.search(r"(i|I)ntercept\s+to\s+(0|zero)", card.text):
            ret.add(models.Bonus.STEALTH)
    # list reset stealth as intercept
    if re.search(r"stealth .* to 0", card.text):
        ret.add(models.Bonus.INTERCEPT)
    # list block denials as stealth
    if re.search(r"attempt fails", card.text):
        ret.add(models.Bonus.STEALTH)
    elif re.search(r"(\+|-)(\d|X) votes?", card.text):
        ret.add(models.Bonus.VOTES)
    elif re.search(r"abstain", card.text):
        ret.add(models.Bonus.VOTES)
    if re.search(r"title of " + TITLES_RE, card.text.lower()):
        ret.add(models.Bonus.VOTES)
    elif card.id in {100406}:
        ret.add(models.Bonus.VOTES)
    if re.search(r"rescu", card.text.lower()):
        ret.add(models.Bonus.TORPOR)
    if re.search(r"leaves? torpor", card.text.lower()):
        ret.add(models.Bonus.TORPOR)
    if re.search(r"\+(\d|X)\s+(c|C)apacity", card.text):
        ret.add(models.Bonus.CAPACITY)
    if re.search(r"\+(\d|X)\s+(s|S)trength", card.text):
        ret.add(models.Bonus.STRENGTH)
    if re.search(r"\+(\d|X)\s+(b|B)leed", card.text):
        ret.add(models.Bonus.BLEED)
    if re.search(r"\+(\d|X)\s+(h|H)unt", card.text):
        ret.add(models.Bonus.HUNT)
    if isinstance(card, models.LibraryCard) and card.trifle:
        ret.add(models.Bonus.TRIFLE)
    return sorted(ret)


def _get_titles(card: models.Card) -> list[models.Title]:
    """Index titles information for a card."""
    ret: set[models.Title] = set()
    if card.kind == models.Card.Kind.CRYPT:
        for match in re.findall(CRYPT_TITLES_RE, card.text.lower()):
            ret.add(models.Title(match[2].title()))
    if card.kind == models.Card.Kind.LIBRARY:
        # Find the section starting with "requires a" up to the next period
        match = re.search(r"requires a ([^.]*)", card.text.lower())
        if match:
            title_section = match.group(1)
            for title_match in re.findall(LIBRARY_TITLES_RE, title_section):
                ret.add(models.Title(title_match.title()))
        if re.search(r"Requires a( ready)? titled (S|s)abbat", card.text):
            ret.update(SECT_TITLES[models.Sect.SABBAT])
        if re.search(r"Requires a( ready)? titled (C|c)amarilla", card.text):
            ret.update(SECT_TITLES[models.Sect.CAMARILLA])
        if re.search(r"Requires a( ready)? titled vampire", card.text):
            ret.update(models.Title)
        if re.search(r"Requires a( ready)? (M|m)agaji", card.text):
            ret.update(SECT_TITLES[models.Sect.LAIBON])
    return sorted(ret)


def _get_city(card: models.Card) -> str | None:
    """Get the city of a card."""
    city = None
    match = re.search(CITY_RE, card.text)
    if match:
        city = match.group(1)
        if city[-6:] == " as a ":
            city = city[:-6]
        if city == "Washington":
            city = "Washington, D.C."
    return city


TRAITS_RE = f"({'|'.join(t.value.lower() for t in models.Trait)})"


def _get_traits(card: models.Card) -> list[models.Trait]:
    """Get the traits of a card."""
    ret = set[models.Trait]()
    for match in re.findall(TRAITS_RE, card.text.lower()):
        ret.add(models.Trait(match.title()))
    if isinstance(card, models.LibraryCard) and card.discipline_requirement:
        if card.discipline_requirement.type == models.DisciplineRequirement.Type.COMBO:
            ret.add(models.Trait.COMBO)
        if card.discipline_requirement.type == models.DisciplineRequirement.Type.CHOICE:
            ret.add(models.Trait.CHOICE)
    return sorted(ret)
