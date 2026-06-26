"""Model definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
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


@dataclass
class Occurence:
    """The occurrence of a print."""

    class Type(StrEnum):
        """The type of occurrence."""

        RARITY = "Rarity"
        SINGLE = "Single"
        PRECON = "Precon"

    type: Type


@dataclass(kw_only=True)
class Rarity(Occurence):
    """The rarity of a print."""

    class Frequency(StrEnum):
        """The frequency of a rarity."""

        COMMON = "C"
        UNCOMMON = "U"
        RARE = "R"
        VAMPIRE = "V"

    type: Occurence.Type = Occurence.Type.RARITY
    frequency: Frequency
    multiplier: float


@dataclass(kw_only=True)
class Precon(Occurence):
    """Card included in a fixed bundle."""

    type: Occurence.Type = Occurence.Type.PRECON
    bundle: str = ""
    copies: int


@dataclass(kw_only=True)
class Single(Occurence):
    """Card available as a single (promo, POD)."""

    type: Occurence.Type = Occurence.Type.SINGLE
    date: date


@dataclass(kw_only=True)
class SetMinimal:
    """A minimal set."""

    id: int = 0
    code: str


@dataclass(kw_only=True)
class Bundle:
    """A bundle."""

    code: str
    name: str
    size: int


@dataclass(kw_only=True)
class Set(SetMinimal):
    """A set."""

    name: str
    company: str = ""
    release_date: date | None = None
    bundles: dict[str, Bundle] = field(default_factory=dict)


@dataclass(kw_only=True)
class Print:
    """A specific print of a card."""

    set: SetMinimal
    occurrences: list[Occurence] = field(default_factory=list)
    url: str


class Lang(StrEnum):
    """A language."""

    EN = "en"
    FR = "fr"
    DE = "de"
    IT = "it"
    ES = "es"
    PT = "pt"


@dataclass(kw_only=True)
class Translation:
    """A translation of a card."""

    name: str
    text: str
    flavor: str = ""
    draft: str = ""


@dataclass
class Variant:
    """A variant of a card."""

    class Type(StrEnum):
        """The type of variant."""

        ADVANCED = "Advanced"
        BASE = "Base"
        EVOLUTION = "Evolution"
        PREVIOUS = "Previous"

    type: Type
    id: int
    suffix: str


@dataclass(kw_only=True)
class CardMinimal:
    """A minimal card."""

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
    references: list[Reference] = field(default_factory=list)
    cards: list[CardMinimal] = field(default_factory=list)
    symbols: list[Symbol] = field(default_factory=list)


# TODO: maybe remove and just trust the source content
# same as for clans and paths
class Discipline(StrEnum):
    """A discipline."""

    abombwe = "abo"
    animalism = "ani"
    auspex = "aus"
    celerity = "cel"
    chimerstry = "chi"
    daimoinon = "dai"
    dementation = "dem"
    dominate = "dom"
    flight = "fli"
    fortitude = "for"
    maleficia = "mal"
    melpominee = "mel"
    mytherceria = "myt"
    necromancy = "nec"
    obeah = "obe"
    obfuscate = "obf"
    oblivion = "obl"
    obtenebration = "obt"
    potence = "pot"
    presence = "pre"
    protean = "pro"
    quietus = "qui"
    sanguinus = "san"
    serpentis = "ser"
    spiritus = "spi"
    striga = "str"
    temporis = "tem"
    thanatosis = "thn"
    blood_sorcery = "tha"
    valeren = "val"
    vicissitude = "vic"
    visceratika = "vis"
    vengeance = "ven"
    defense = "def"
    innocence = "inn"
    judgment = "jud"
    martyrdom = "mar"
    redemption = "red"
    vision = "viz"


class DisciplineLevel(StrEnum):
    """A discipline, with level distinction."""

    abombwe = "abo"
    animalism = "ani"
    auspex = "aus"
    celerity = "cel"
    chimerstry = "chi"
    daimoinon = "dai"
    dementation = "dem"
    dominate = "dom"
    flight = "fli"
    fortitude = "for"
    maleficia = "mal"
    melpominee = "mel"
    mytherceria = "myt"
    necromancy = "nec"
    obeah = "obe"
    obfuscate = "obf"
    oblivion = "obl"
    obtenebration = "obt"
    potence = "pot"
    presence = "pre"
    protean = "pro"
    quietus = "qui"
    sanguinus = "san"
    serpentis = "ser"
    spiritus = "spi"
    striga = "str"
    temporis = "tem"
    thanatosis = "thn"
    blood_sorcery = "tha"
    valeren = "val"
    vicissitude = "vic"
    visceratika = "vis"
    vengeance = "ven"
    defense = "def"
    innocence = "inn"
    judgment = "jud"
    martyrdom = "mar"
    redemption = "red"
    vision = "viz"
    ABOMBWE = "ABO"
    ANIMALISM = "ANI"
    AUSPEX = "AUS"
    CELERITY = "CEL"
    CHIMERSTRY = "CHI"
    DAIMOINON = "DAI"
    DEMENTATION = "DEM"
    DOMINATE = "DOM"
    FORTITUDE = "FOR"
    MALFICIA = "MAL"
    MELPOMINEE = "MEL"
    MYTHERCERIA = "MYT"
    NECROMANCY = "NEC"
    OBEAH = "OBE"
    OBFUSCATE = "OBF"
    OBLIVION = "OBL"
    OBTENEBRATION = "OBT"
    POTENCE = "POT"
    PRESENCE = "PRE"
    PROTEAN = "PRO"
    QUIETUS = "QUI"
    SANGINUS = "SAN"
    SERPENTIS = "SER"
    SPIRITUS = "SPI"
    STRIGA = "STR"
    TEMPORIS = "TEM"
    THANATOSIS = "THN"
    BLOOD_SORCERY = "THA"
    VALEREN = "VAL"
    VICISSITUDE = "VIC"
    VISCERATIKA = "VIS"


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
    disciplines: list[Discipline] = field(default_factory=list)


class Title(StrEnum):
    """A title."""

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
    """A cost."""

    class Type(StrEnum):
        """The type of cost."""

        POOL = "Pool"
        BLOOD = "Blood"
        CONVICTION = "Conviction"

    type: Type
    value: int | Literal["X"]


@dataclass(kw_only=True)
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
    text: str = ""
    draft: str = ""
    flavor: str = ""
    legal: date | None = None
    banned: date | None = None

    def __post_init__(self) -> None:
        """Convert string types to Type enum members."""
        if self.types:
            self.types = [
                self.Type(t.strip()) if isinstance(t, str) else t
                for t in self.types
                if t  # Filter out empty strings
            ]

    def __hash__(self) -> int:
        """Hash (so the card can be used as a key in a dictionary)."""
        return super().__hash__()

    def __eq__(self, other: object) -> bool:
        """Equality (so the card can be used as a key in a dictionary)."""
        return super().__eq__(other)

    def __str__(self) -> str:
        """String representation of a card."""
        return f"{self.id}|{self.unique_name}"


@dataclass(kw_only=True)
class CryptCard(Card):
    """A VTES crypt card."""

    kind: Card.Kind = Card.Kind.CRYPT
    clan: str = ""
    path: str = ""
    advanced: bool = False
    capacity: int | None = None
    group: Group | None = None
    disciplines: list[DisciplineLevel] = field(default_factory=list)
    title: Title | None = None

    def __hash__(self) -> int:
        """Hash (so the card can be used as a key in a dictionary)."""
        return super().__hash__()

    def __eq__(self, other: object) -> bool:
        """Equality (so the card can be used as a key in a dictionary)."""
        return super().__eq__(other)

    def __str__(self) -> str:
        """String representation of a card."""
        return f"{self.id}|{self.unique_name}"

    def __repr__(self) -> str:
        """Don't go verbose on repr."""
        return str(self)


@dataclass(kw_only=True)
class LibraryCard(Card):
    """A VTES library card."""

    kind: Card.Kind = Card.Kind.LIBRARY
    cost: Cost | None = None
    burn_option: bool = False
    trifle: bool = False
    clan_requirement: list[str] = field(default_factory=list)
    path_requirement: list[str] = field(default_factory=list)
    discipline_requirement: DisciplineRequirement | None = None

    def __hash__(self) -> int:
        """Hash (so the card can be used as a key in a dictionary)."""
        return super().__hash__()

    def __eq__(self, other: object) -> bool:
        """Equality (so the card can be used as a key in a dictionary)."""
        return super().__eq__(other)

    def __str__(self) -> str:
        """String representation of a card."""
        return f"{self.id}|{self.unique_name}"

    def __repr__(self) -> str:
        """Don't go verbose on repr."""
        return str(self)


@dataclass(kw_only=True)
class CardInDeck(CardMinimal):
    """A card in a deck."""

    count: int
    kind: Card.Kind
    types: list[Card.Type]
    comment: str = field(default="")

    def __hash__(self) -> int:
        """Hash (so the card can be used as a key in a dictionary)."""
        return super().__hash__()

    def __eq__(self, other: object) -> bool:
        """Equality (so the card can be used as a key in a dictionary)."""
        return super().__eq__(other)


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


class RoundFormat(StrEnum):
    """A round format."""

    NA = "N/A"
    R2F = "2R+F"
    R3F = "3R+F"


@dataclass(kw_only=True)
class Event:
    """An event."""

    name: str = ""
    date: date | None = None
    end_date: date | None = None
    online: bool = False
    format: Format = Format.STANDARD
    players_count: int = 0
    rounds: RoundFormat = RoundFormat.NA
    place: str = ""
    country: Country | None = None
    url: str = ""


@dataclass(kw_only=True)
class Score:
    """A score."""

    round_gw: int = 0
    round_vp: float = 0
    finals_vp: float = 0
    win: bool = False

    def __str__(self) -> str:
        """String representation of a score."""
        ret = ""
        if self.round_gw:
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
    """A deck."""

    id: str = ""
    name: str = ""
    cards: list[CardInDeck] = field(default_factory=list)
    comment: str = ""
    author: str = ""
    event: Event | None = None
    player: str = ""
    score: Score | None = None


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
    """A search dimension."""

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
