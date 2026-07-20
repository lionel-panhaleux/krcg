"""Model definitions."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
import datetime
from enum import StrEnum
from typing import Literal

FILING_PREFIXES = ["A", "An", "The", "El", "La", "Le", "Un", "Une", "Les", "Una"]


@dataclass
class NameVariant:
    """A variant of a card name."""

    class Type(StrEnum):
        """The type of name variant."""

        # note translations (i18n) offer additional variants
        VERNACULAR = "Vernacular"
        HISTORICAL = "Historical"
        LEXICOGRAPHICAL = "Lexicographical"

    type: Type
    name: str


@dataclass(kw_only=True)
class Occurrence:
    """How a card appears in a print.

    A single flat type discriminated by `type` (so it round-trips through
    msgspec natively); the trailing comments mark which kind uses each field.
    """

    class Type(StrEnum):
        """The type of occurrence."""

        RARITY = "Rarity"
        SINGLE = "Single"
        PRECON = "Precon"

    class Frequency(StrEnum):
        """The frequency of a rarity."""

        COMMON = "C"
        UNCOMMON = "U"
        RARE = "R"
        VAMPIRE = "V"

    type: Type
    frequency: Frequency | None = None  # RARITY
    multiplier: float = 0.0  # RARITY
    bundle: str = ""  # PRECON
    copies: int = 0  # PRECON
    date: datetime.date | None = None  # SINGLE


@dataclass(kw_only=True)
class SetMinimal:
    """A minimal set."""

    id: int = 0
    code: str


@dataclass(kw_only=True)
class Bundle:
    """A product within a set (e.g. a preconstructed deck)."""

    code: str
    name: str
    size: int
    release_date: datetime.date | None = None


@dataclass(kw_only=True)
class Set(SetMinimal):
    """A VTES expansion."""

    name: str
    company: str = ""
    release_date: datetime.date | None = None
    bundles: dict[str, Bundle] = field(default_factory=dict)


@dataclass(kw_only=True)
class Print:
    """A specific print of a card."""

    set: SetMinimal
    occurrences: list[Occurrence] = field(default_factory=list)
    url: str


class Lang(StrEnum):
    """A language (only those with synced data)."""

    EN = "en"
    FR = "fr"
    ES = "es"


@dataclass(kw_only=True)
class Translation:
    """A translation of a card."""

    name: str
    text: str
    flavor: str = ""
    draft: str = ""
    url: str = ""
    #: cards named in `text`, which marks each one `<Card Name>`
    cards: list[CardMinimal] = field(default_factory=list)


@dataclass
class Variant:
    """A link to a related form of the card (advanced, base, evolution)."""

    class Type(StrEnum):
        """The type of variant."""

        ADVANCED = "Advanced"
        BASE = "Base"
        EVOLUTION = "Evolution"
        PREVIOUS = "Previous"

    type: Type
    id: int
    suffix: str


@dataclass(kw_only=True, eq=False)
class CardMinimal:
    """A card reduced to its id and names (shared by Card and CardInDeck)."""

    id: int
    printed_name: str = ""
    unicity_suffix: str = ""
    suffix: str = ""

    @property
    def unique_name(self) -> str:
        """The unique name of a card (suffixed as needed for unicity)."""
        if self.unicity_suffix:
            return f"{self.printed_name} ({self.unicity_suffix})"
        return self.printed_name

    @property
    def full_name(self) -> str:
        """The full name of a card (group / advanced suffix included)."""
        if self.suffix:
            return f"{self.printed_name} ({self.suffix})"
        return self.printed_name

    @property
    def filing_name(self) -> str:
        """The unique name without prefix (for filing order)."""
        if len(self.unique_name) < 9:
            return self.unique_name
        for prefix in FILING_PREFIXES:
            if self.unique_name.startswith(prefix + " "):
                return self.unique_name[len(prefix) + 1 :]
        return self.unique_name

    def __hash__(self) -> int:
        """Hash the card."""
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        """Check if the card is equal to another object."""
        if not isinstance(other, CardMinimal):
            return False
        return self.id == other.id

    def __str__(self) -> str:
        """String representation of a card."""
        return f"{self.id}|{self.unique_name}"

    def __repr__(self) -> str:
        """Concise repr (don't dump every field)."""
        return str(self)

    @classmethod
    def from_card(cls, card: CardMinimal) -> CardMinimal:
        """Project a fuller card down to a minimal one, dropping extra fields."""
        return cls(**{f.name: getattr(card, f.name) for f in fields(cls)})


@dataclass(kw_only=True)
class Ruling:
    """A ruling on a card."""

    @dataclass(kw_only=True)
    class Reference:
        """A reference to a ruling."""

        text: str
        label: str
        url: str

    @dataclass(kw_only=True)
    class Symbol:
        """A symbol referenced in a ruling."""

        text: str
        symbol: str

    text: str
    group: str = ""
    reminder: bool = False
    references: list[Reference] = field(default_factory=list)
    cards: list[CardMinimal] = field(default_factory=list)
    symbols: list[Symbol] = field(default_factory=list)


class Group(StrEnum):
    """A crypt card group."""

    G1 = "G1"
    G2 = "G2"
    G3 = "G3"
    G4 = "G4"
    G5 = "G5"
    G6 = "G6"
    G7 = "G7"
    Any = "Any"


class Format(StrEnum):
    """A VTES tournament format."""

    STANDARD = "Standard"
    V5 = "V5"
    LIMITED = "Limited"


@dataclass
class DisciplineRequirement:
    """A discipline requirement."""

    class Type(StrEnum):
        """The type of combination."""

        COMBO = "Combo"
        CHOICE = "Choice"
        MONO = "Mono"

    type: Type
    # library requirements are level-agnostic: lowercase trigrams (e.g. "dom")
    disciplines: list[str] = field(default_factory=list)


class Title(StrEnum):
    """A political title (Prince, Justicar, Baron, …)."""

    PRIMOGEN = "Primogen"
    PRINCE = "Prince"
    JUSTICAR = "Justicar"
    INNER_CIRCLE = "Inner Circle"
    IMPERATOR = "Imperator"
    BISHOP = "Bishop"
    ARCHBISHOP = "Archbishop"
    CARDINAL = "Cardinal"
    REGENT = "Regent"
    PRISCUS = "Priscus"
    BARON = "Baron"
    MAGAJI = "Magaji"
    KHOLO = "Kholo"
    VOTE_1 = "1 Vote"
    VOTE_2 = "2 Votes"


@dataclass
class Cost:
    """A card cost in pool, blood, or conviction (value may be "X")."""

    class Type(StrEnum):
        """The type of cost."""

        POOL = "Pool"
        BLOOD = "Blood"
        CONVICTION = "Conviction"

    type: Type
    value: int | Literal["X"]


@dataclass(kw_only=True, eq=False, repr=False)
class Card(CardMinimal):
    """A VTES card."""

    class Kind(StrEnum):
        """The kind of card."""

        CRYPT = "Crypt"
        LIBRARY = "Library"

    class Type(StrEnum):
        """The type of a card."""

        ACTION = "Action"
        MODIFIER = "Action Modifier"
        REACTION = "Reaction"
        POLITICAL = "Political Action"
        ALLY = "Ally"
        RETAINER = "Retainer"
        EQUIPMENT = "Equipment"
        POWER = "Power"
        EVENT = "Event"
        COMBAT = "Combat"
        VAMPIRE = "Vampire"
        MASTER = "Master"
        CONVICTION = "Conviction"
        IMBUED = "Imbued"

    kind: Kind
    name_variants: list[NameVariant] = field(default_factory=list)
    prints: list[Print] = field(default_factory=list)
    i18n: dict[Lang, Translation] = field(default_factory=dict)
    url: str = ""
    types: list[Type] = field(default_factory=list)
    formats: list[Format] = field(default_factory=list)
    artists: list[str] = field(default_factory=list)
    variants: list[Variant] = field(default_factory=list)
    rulings: list[Ruling] = field(default_factory=list)
    #: cards named in `text`, which marks each one `<Card Name>`
    cards: list[CardMinimal] = field(default_factory=list)
    text: str = ""
    draft: str = ""
    flavor: str = ""
    legal: datetime.date | None = None
    banned: datetime.date | None = None

    def __post_init__(self) -> None:
        """Convert string types to Type enum members."""
        if self.types:
            self.types = [
                self.Type(t.strip()) if isinstance(t, str) else t
                for t in self.types
                if t
            ]


@dataclass(kw_only=True, eq=False, repr=False)
class CryptCard(Card):
    """A VTES crypt card."""

    kind: Card.Kind = Card.Kind.CRYPT
    clan: str = ""
    path: str = ""
    advanced: bool = False
    capacity: int | None = None
    group: Group | None = None
    # crypt disciplines encode level by case: lower=inferior, UPPER=superior
    disciplines: list[str] = field(default_factory=list)
    title: Title | None = None


@dataclass(kw_only=True, eq=False, repr=False)
class LibraryCard(Card):
    """A VTES library card."""

    kind: Card.Kind = Card.Kind.LIBRARY
    cost: Cost | None = None
    burn_option: bool = False
    trifle: bool = False
    clan_requirement: list[str] = field(default_factory=list)
    path_requirement: list[str] = field(default_factory=list)
    discipline_requirement: DisciplineRequirement | None = None


@dataclass(kw_only=True, eq=False)
class CardInDeck(CardMinimal):
    """A card in a deck."""

    count: int
    kind: Card.Kind
    types: list[Card.Type]
    comment: str = field(default="")

    def __repr__(self) -> str:
        """Concise repr including the count."""
        return f"{self.count}x {self.id}|{self.unique_name}"

    @classmethod
    def of(cls, card: Card, count: int, comment: str = "") -> CardInDeck:
        """Build a deck entry from a card, a count, and an optional comment."""
        return cls(
            id=card.id,
            printed_name=card.printed_name,
            unicity_suffix=card.unicity_suffix,
            suffix=card.suffix,
            count=count,
            kind=card.kind,
            types=card.types,
            comment=comment,
        )


class Continent(StrEnum):
    """A continent."""

    EUROPE = "EU"
    ASIA = "AS"
    NORTH_AMERICA = "NA"
    SOUTH_AMERICA = "SA"
    AFRICA = "AF"
    OCEANIA = "OC"
    ANTARCTICA = "AN"


@dataclass(kw_only=True)
class Country:
    """A country."""

    name: str = ""
    code: str = ""
    flag: str = ""
    continent: Continent


@dataclass(kw_only=True)
class Event:
    """A tournament."""

    name: str = ""
    date: datetime.date | None = None
    end_date: datetime.date | None = None
    online: bool = False
    format: Format = Format.STANDARD
    players_count: int = 0
    rounds: int = 0
    finals: bool = True
    place: str = ""
    country: Country | None = None
    url: str = ""


@dataclass(kw_only=True)
class Score:
    """A deck's tournament result (game wins and victory points)."""

    round_gw: int = 0
    round_vp: float = 0
    finals_vp: float = 0
    win: bool = False

    def __str__(self) -> str:
        """String representation of a score."""
        ret = ""
        # emit the GW count whenever there is a rounds VP: a bare leading VP
        # would otherwise parse back as a finals VP (round-trip safety).
        if self.round_gw or self.round_vp:
            ret += f"{self.round_gw}GW"
        if self.round_vp:
            ret += f"{self.round_vp:g}"
        if self.finals_vp:
            ret += f"+{self.finals_vp:g}"
        if self.win:
            ret += "!"
        return ret


@dataclass(kw_only=True)
class Deck:
    """A decklist with its tournament metadata."""

    id: str = ""
    name: str = ""
    cards: list[CardInDeck] = field(default_factory=list)
    comment: str = ""
    author: str = ""
    event: Event | None = None
    player: str = ""
    score: Score | None = None
    # copies written as the pre-merge "Raven" crypt card (now Camille Devereux,
    # The Raven); kept so historical TWD lists re-serialize to their original form
    raven: int = 0


class Trait(StrEnum):
    """A trait."""

    BLACK_HAND = "Black Hand"
    INFERNAL = "Infernal"
    RED_LIST = "Red List"
    SCARCE = "Scarce"
    SERAPH = "Seraph"
    SLAVE = "Slave"
    STERILE = "Sterile"
    COMBO = "Combo"
    CHOICE = "Choice"


class Bonus(StrEnum):
    """A bonus."""

    BLEED = "Bleed"
    CAPACITY = "Capacity"
    HUNT = "Hunt"
    INTERCEPT = "Intercept"
    STEALTH = "Stealth"
    STRENGTH = "Strength"
    TORPOR = "Torpor"
    TRIFLE = "Trifle"
    VOTES = "Votes"


class Sect(StrEnum):
    """A sect."""

    ANARCH = "Anarch"
    CAMARILLA = "Camarilla"
    INDEPENDENT = "Independent"
    LAIBON = "Laibon"
    SABBAT = "Sabbat"


class SearchDimension(StrEnum):
    """A card search dimension (a keyword key accepted by CardDict.search)."""

    NAME = "name"
    CARD_TEXT = "card_text"
    FLAVOR_TEXT = "flavor_text"
    KIND = "kind"
    TYPE = "type"
    DISCIPLINE = "discipline"
    ARTIST = "artist"
    BONUS = "bonus"
    CAPACITY = "capacity"
    CITY = "city"
    CLAN = "clan"
    GROUP = "group"
    PATH = "path"
    PRECON = "precon"
    RARITY = "rarity"
    SECT = "sect"
    SET = "set"
    TITLE = "title"
    TRAIT = "trait"
