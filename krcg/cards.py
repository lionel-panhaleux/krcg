from typing import Dict, List, Set, Tuple
import collections
import collections.abc
import copy
import datetime
import functools
import itertools
import re
import requests
import urllib.request
import warnings

from . import config
from . import rulings
from . import sets
from . import utils


class Card(utils.i18nMixin, utils.NamedMixin):
    #: official cards renaming not registered in cards "Aka" field
    _AKA = {
        "Mask of a Thousand Faces": ["mask of 1,000 faces"],
    }
    #: Actual ban dates
    _BAN_MAP = {
        "1995": datetime.date(1995, 11, 1),  # RTR 19951006
        "1997": datetime.date(1997, 7, 1),  # RTR 19970701
        "1999": datetime.date(1999, 4, 1),  # RTR 19990324
        "2005": datetime.date(2005, 1, 1),  # RTR 20041205
        "2008": datetime.date(2008, 1, 1),  # RTR 20071204
        "2013": datetime.date(2013, 5, 22),  # RTR 20130422
        "2016": datetime.date(2016, 2, 16),  # RTR 20160119
        "2020": datetime.date(2020, 8, 1),  # RTR 20200705
    }
    _DISC_MAP = {
        # special case for vampires with no discipline (eg. Anarch Convert)
        "-none-": None,
        # these are not disciplines but treat them that way
        "striga": "striga",
        "maleficia": "maleficia",
        "flight": "flight",
        "vision": "vin",  # avoid collision with visceratika
        # standard list
        "judgment": "jud",
        "innocence": "inn",
        "martyrdom": "mar",
        "defense": "def",
        "redemption": "red",
        "vengeance": "ven",
        "abombwe": "abo",
        "animalism": "ani",
        "auspex": "aus",
        "celerity": "cel",
        "chimerstry": "chi",
        "daimoinon": "dai",
        "dementation": "dem",
        "dominate": "dom",
        "fortitude": "for",
        "melpominee": "mel",
        "mytherceria": "myt",
        "necromancy": "nec",
        "obeah": "obe",
        "obfuscate": "obf",
        "obtenebration": "obt",
        "potence": "pot",
        "presence": "pre",
        "protean": "pro",
        "quietus": "qui",
        "sanguinus": "san",
        "serpentis": "ser",
        "spiritus": "spi",
        "temporis": "tem",
        "thaumaturgy": "tha",
        "thanatosis": "thn",
        "valeren": "val",
        "vicissitude": "vic",
        "visceratika": "vis",
    }
    _RARITY_BOOSTER_CODES = {
        "R": "Rare",
        "U": "Uncommon",
        "C": "Common",
        "V": "Vampire",
    }
    _RARITY_PRECON_CODES = {
        "SP": {
            "PwN": "Pact with Nephandi",
            "PoS": "Parliament of Shadows",
            "DoF": "Den of Fiends",
            "LB": "Libertine Ball",
        },
        "Anarchs": {
            "PAB": "Anarch Barons",
            "PAG": "Anarch Gang",
            "PG": "Gangrel",
        },
        "CE": {
            "PTo": "Toreador",
            "PTr": "Tremere",
            "PV": "Ventrue",
            "PB": "Brujah",
            "PM": "Malkavian",
            "PN": "Nosferatu",
        },
        "KMW": {
            "PG": "Gangrel antitribu",
            "PB": "Baali",
            "PAn": "Anathema",
            "PAl": "Alastors",
        },
        "KoT": {
            "PV": "Ventrue",
            "PB": "Brujah",
            "PM": "Malkavian",
            "PT": "Toreador",
            "A": "Reprint Bundle 1",
            "B": "Reprint Bundle 2",
        },
        "V5": {
            "PV": "Ventrue",
            "PM": "Malkavian",
            "PTo": "Toreador",
            "PN": "Nosferatu",
            "PTr": "Tremere",
        },
        "FB": {
            "PV": "Ventrue",
            "PM": "Malkavian",
            "PTo": "Toreador",
            "PN": "Nosferatu",
            "PTr": "Tremere",
        },
        "LoB": {
            "PO": "Osebo",
            "PG": "Guruhi",
            "PI": "Ishtarri",
            "PA": "Akunanse",
        },
        "LotN": {
            "PS": "Followers of Set",
            "PA": "Assamite",
            "PR": "Ravnos",
            "PG": "Giovanni",
        },
        "FN": {
            "PS": "Followers of Set",
            "PA": "Assamite",
            "PR": "Ravnos",
            "PG": "Giovanni",
        },
        "SW": {
            "PL": "Lasombra",
            "PB": "Brujah antitribu",
            "PT": "Tzimisce",
            "PV": "Ventrue antitribu",
        },
        "HttB": {
            "PSal": "Salubri antitribu",
            "PGar": "Gargoyles",
            "PKia": "Kiasyd",
            "PSam": "Samedi",
            "A": "Reprint Bundle 1",
            "B": "Reprint Bundle 2",
        },
        "BH": {
            "PN": "Nosferatu antitribu",
            "PTo": "Toreador antitribu",
            "PTr": "Tremere antitribu",
            "PM": "Malkavian antitribu",
        },
        "Third": {
            "PTr": "Tremere antitribu",
            "PB": "Brujah antitribu",
            "PM": "Malkavian antitribu",
            "PTz": "Tzimisce",
        },
        "Tenth": {"A": "Tin A", "B": "Tin B"},
        "Anthology": {"LARP": "EC Berlin Edition"},
        "BSC": {"X": ""},
        "POD": {
            "DTC": "DriveThruCards",
        },
        "Promo-20181004": {"HB": "Humble Bundle"},
        "TU": {
            "A": "Bundle 1",
            "B": "Bundle 2",
        },
    }
    _REPRINTS_RELEASE_DATE = {
        ("KoT", "Reprint Bundle 1"): datetime.date(2018, 5, 5),
        ("KoT", "Reprint Bundle 2"): datetime.date(2018, 5, 5),
        ("HttB", "Reprint Bundle 1"): datetime.date(2018, 7, 14),
        ("HttB", "Reprint Bundle 2"): datetime.date(2018, 7, 14),
        ("TU", "Bundle 1"): datetime.date(2021, 7, 9),
        ("TU", "Bundle 2"): datetime.date(2021, 7, 9),
    }
    _ARTISTS_FIXES = {
        "Alejandro Collucci": "Alejandro Colucci",
        "Chet Masterz": "Chet Masters",
        "Dimple": 'Nicolas "Dimple" Bigot',
        "EM Gist": "E.M. Gist",
        "G. Goleash": "Grant Goleash",
        "Ginés Quiñonero": "Ginés Quiñonero-Santiago",
        "Glenn Osterberger": "Glen Osterberger",
        "Heather Kreiter": "Heather V. Kreiter",
        "Jeff Holt": 'Jeff "el jefe" Holt',
        "L. Snelly": "Lawrence Snelly",
        "Martín de Diego Sábada": "Martín de Diego",
        "Mathias Tapia": "Matias Tapia",
        "Mattias Tapia": "Matias Tapia",
        "Matt Mitchell": "Matthew Mitchell",
        "Mike Gaydos": "Michael Gaydos",
        "Mike Weaver": "Michael Weaver",
        "Nicolas Bigot": 'Nicolas "Dimple" Bigot',
        "Pat McEvoy": "Patrick McEvoy",
        "Ron Spenser": "Ron Spencer",
        "Sam Araya": "Samuel Araya",
        "Sandra Chang": "Sandra Chang-Adair",
        "T. Bradstreet": "Tim Bradstreet",
        "Tom Baxa": "Thomas Baxa",
        "zelgaris": 'Tomáš "zelgaris" Zahradníček',
    }

    def __init__(self):
        super().__init__()
        self.id = 0
        #: use `vekn_name` or `name` properties instead
        self._name = ""
        self.url = ""
        self.aka = []
        self.types = []
        self.clans = []
        self.capacity = None
        self.capacity_change = None
        self.disciplines = []
        self.combo = None
        self.multidisc = None
        self.card_text = ""
        self.sets = {}
        self.scans = {}
        self.banned = None
        self.artists = []
        self.adv = None
        self.group = None
        self.title = None
        self.pool_cost = None
        self.blood_cost = None
        self.conviction_cost = None
        self.burn_option = None
        self.flavor_text = None
        self.draft = None
        self.rulings = {"text": [], "links": {}}

    def diff(self, rhs):
        res = {}
        if self.name != rhs.name:
            res["name"] = [self.name, rhs.name]
        if self.card_text != rhs.card_text:
            res["card_text"] = [self.card_text, rhs.card_text]
        if set(self.types) != set(rhs.types):
            res["types"] = [self.types, rhs.types]
        if set(self.clans) != set(rhs.clans):
            res["clans"] = [self.clans, rhs.clans]
        if set(self.disciplines) - {"viz", "vin"} != set(rhs.disciplines) - {"viz", "vin"}:
            res["disciplines"] = [self.disciplines, rhs.disciplines]
        if (self.capacity or 0) != (rhs.capacity or 0):
            res["capacity"] = [self.capacity, rhs.capacity]
        if bool(self.adv) != bool(rhs.adv):
            res["adv"] = [self.adv, rhs.adv]
        if bool(self.banned) != bool(rhs.banned):
            res["banned"] = [self.banned, rhs.banned]
        if self.group != rhs.group:
            res["group"] = [self.group, rhs.group]
        if self.pool_cost != rhs.pool_cost:
            res["pool_cost"] = [self.pool_cost, rhs.pool_cost]
        if self.blood_cost != rhs.blood_cost:
            res["blood_cost"] = [self.blood_cost, rhs.blood_cost]
        if self.conviction_cost != rhs.conviction_cost:
            res["conviction_cost"] = [self.conviction_cost, rhs.conviction_cost]
        if bool(self.burn_option) != bool(rhs.burn_option):
            res["burn_option"] = [self.burn_option, rhs.burn_option]
        if (self.flavor_text or "") != (rhs.flavor_text or ""):
            res["flavor_text"] = [self.flavor_text, rhs.flavor_text]
        return res

    @property
    @functools.lru_cache(1)
    def vekn_name(self) -> str:
        """VEKN names as used in legacy decklists tools."""
        assert self.id, "Card is not initialized"
        ret = self._name
        if self.adv:
            ret += " (ADV)"
        return ret

    @property
    @functools.lru_cache(1)
    def name(self) -> str:
        """Actual real name printed on the card."""
        assert self.id, "Card is not initialized"
        ret = self._name
        if ret[-5:] == ", The":
            ret = "The " + ret[:-5]
        ret = ret.replace("(TM)", "™")
        if self.adv:
            ret += " (ADV)"
        return ret

    @property
    @functools.lru_cache(1)
    def crypt(self) -> bool:
        """True if this is a crypt card."""
        return set(self.types) & {"Imbued", "Vampire"}

    @property
    def library(self) -> bool:
        """True if this is a library card."""
        return not self.crypt

    def to_json(self) -> Dict:
        """Return a compact dict representation of the card, for JSON serialization."""
        return utils.json_pack(
            {
                k: v
                for k, v in list(self.__dict__.items()) + [("name", self.name)]
                if k not in ["crypt", "library", "vekn_name"]
            }
        )

    def from_json(self, state: Dict) -> None:
        """Get the card form a dict."""
        state.pop("name")
        self.__dict__.update(state)

    def from_vekn(
        self, data: Dict[str, str], set_dict: Dict[str, sets.Set] = sets.DEFAULT_SET_MAP
    ) -> None:
        """Read a card from a dict generated from a VEKN official CSV.

        Args:
            set_dict: A map of the sets, indexed by abbreviation
            data: Dict of the CSV line
        """

        def split(field, sep):
            return [s for s in map(str.strip, data[field].split(sep)) if s]

        def str_or_none(field):
            return data[field] or None if field in data else None

        def bool_or_none(field):
            return bool(data[field]) if field in data else None

        def int_or_none(field):
            try:
                return int(data[field]) if data.get(field) else None
            except ValueError:
                warnings.warn(f"expected an integer for {field}: {data}")

        self.id = int(data["Id"])
        self._name = data["Name"]
        self.aka = split("Aka", ";")
        self.types = split("Type", "/")
        self.clans = split("Clan", "/")
        capacity = data.get("Capacity")
        if capacity and re.search(r"^[^\d]", capacity):
            self.capacity_change = capacity
        else:
            self.capacity = int_or_none("Capacity")
        # disciplines
        discipline_key = "Discipline" if "Discipline" in data else "Disciplines"
        if "/" in data[discipline_key]:
            self.multidisc = True
        if "&" in data[discipline_key]:
            self.combo = True
        for s in re.split(r"[\s/&]+", data[discipline_key]):
            # distinguish vision (vin) from visceratika (vis)
            if s.lower() == "vis" and "Imbued" in self.types:
                s = "vin"
            s = Card._DISC_MAP.get(s.lower(), s)
            if s:
                self.disciplines.append(s)
        # braces have been used in the CSV to denote last card text change
        self.card_text = (
            data["Card Text"].replace("(D)", "Ⓓ").replace("{", "").replace("}", "")
        )
        self.banned = (
            self._BAN_MAP[data["Banned"]].isoformat() if data["Banned"] else None
        )
        self.artists = sorted(  # some cards have duplicated artists, eg. Ashur Tablets
            set(
                self._ARTISTS_FIXES.get(s, s)
                for s in map(str.strip, re.split(r"[;,&]+(?!\sJr\.)", data["Artist"]))
                if s
            )
        )
        self.adv = bool_or_none("Adv")
        # group can be "any"
        self.group = str_or_none("Group")
        self.title = str_or_none("Title")
        if self.title and self.title[0] not in ["1", "2", "3", "4", "5"]:
            self.title = self.title.title()
        self.pool_cost = str_or_none("Pool Cost")  # can be X
        self.blood_cost = str_or_none("Blood Cost")  # can be X
        self.conviction_cost = str_or_none("Conviction Cost")  # str for consistency
        self.burn_option = bool_or_none("Burn Option")
        self.flavor_text = data["Flavor Text"] if "Flavor Text" in data else None
        self.draft = data["Draft"] if "Draft" in data else None
        # computations last: some properties (ie. name) are cached,
        # only use them once everything else is set
        self.sets = dict(
            Card._decode_set(set_dict, rarity)
            for rarity in map(
                str.strip,
                itertools.chain.from_iterable(
                    s.split(";") for s in data["Set"].split(",")
                ),
            )
            if rarity
        )
        if not self.sets:
            warnings.warn(f"no set found for {self}")
        self.scans = {
            name: self._compute_url(
                expansion=(
                    {
                        "2019 Promo Pack 1": "promo-pack-1",
                        "2020 Promo Pack 2": "promo-pack-2",
                        "2021 Kickstarter Promo": "kickstarter-promo",
                        "2018 Humble Bundle": "humble-bundle",
                    }.get(name, "promo")
                    if set_dict[name].abbrev in set(sets.SetMap.PROMOS)
                    else name.lower().replace(":", "").replace(" ", "-")
                )
            )
            for name in self.sets.keys()
        }
        self.url = self._compute_url()

    def _compute_url(self, lang: str = None, expansion: str = None):
        """Compute image URL for given language."""
        return (
            config.KRCG_STATIC_SERVER
            + "/card/"
            + (f"set/{expansion}/" if expansion else "")
            + (f"{lang[:2]}/" if lang else "")
            + re.sub(r"[^\w\d]", "", utils.normalize(self.vekn_name))
            + ".jpg"
        )

    @staticmethod
    def _decode_set(
        set_dict: Dict[str, sets.Set], expansion: str
    ) -> Tuple[str, List[Dict]]:
        """Decode a set string from official CSV.

        From Jyhad:R2 to {"Jyhad": {"rarity": "Rare", "frequency": 2}}
        """
        match = re.match(
            r"^(?P<abbrev>[a-zA-Z0-9-]+):?(?P<rarity>[a-zA-Z0-9/½]+)?$",
            expansion,
        )
        if not match:
            warnings.warn(f"failed to parse set: {expansion}")
            return expansion, []
        match = match.groupdict()
        abbrev = match["abbrev"]
        try:
            date = set_dict[abbrev].release_date
        except KeyError:
            warnings.warn(f"unknown set: {abbrev}")
            date = None
        rarities = (match["rarity"] or "").split("/")
        ret = [
            r
            for r in map(lambda a: Card._decode_rarity(a, abbrev, date), rarities)
            if r
        ]
        return set_dict[abbrev].name, ret

    @staticmethod
    def _decode_rarity(rarity: str, abbrev: str, date: str) -> dict:
        """Decode the rarity tag after expansion abbreviation."""
        match = re.match(
            r"^(?P<base>[a-zA-Z]+)?(?P<count>[0-9½]+)?$",
            rarity,
        )
        ret = {"release_date": date}
        if not match:
            warnings.warn(f"unknown rarity {rarity}")
            return
        base = match.group("base")
        count = match.group("count")
        if not base:
            ret["copies"] = int(count or 1)
            return ret
        code = Card._RARITY_BOOSTER_CODES.get(base)
        if code:
            ret["rarity"] = code
        else:
            code = Card._RARITY_PRECON_CODES.get(abbrev, {}).get(base)
            if code:
                ret["precon"] = code
            elif code is None:
                warnings.warn(f"unknown base: {base} in {abbrev}:{rarity}")
                return
        # fix release date for reprints
        if (abbrev, code) in Card._REPRINTS_RELEASE_DATE:
            ret["release_date"] = Card._REPRINTS_RELEASE_DATE[
                (abbrev, code)
            ].isoformat()
        count = match["count"]
        if not count and "precon" in ret:
            count = 1
        # thank Aye/Orun for this "½" frequency
        if count == "½":
            count = 0.5
        if count:
            count = int(count)
            if "rarity" in ret:
                try:
                    ret["frequency"] = count
                except KeyError:
                    warnings.warn(f"unknown frequency {count} in {rarity}")
            else:
                ret["copies"] = count
        return ret


class CardMap(utils.FuzzyDict):
    """A fuzzy dict specialized for cards.

    Cards are index both by ID (int) and a number of name variations (str).
    Iterating over the CardMap will return each card (values) once, not the keys.
    len() will also return the number of unique cards, not the count of name variations.
    """

    _VEKN_CSV = [
        "http://www.vekn.net/images/stories/downloads/vtescsv_utf8.zip",
        [
            "vtessets.csv",
            "vtescrypt.csv",
            "vteslib.csv",
        ],
    ]
    _VEKN_CSV_I18N = {
        "fr-FR": (
            "http://www.vekn.net/images/stories/downloads/"
            "french/vtescsv_utf8.fr-FR.zip",
            [
                "vtessets.fr-FR.csv",
                "vtescrypt.fr-FR.csv",
                "vteslib.fr-FR.csv",
            ],
        ),
        "es-ES": (
            "http://www.vekn.net/images/stories/downloads/"
            "spanish/vtescsv_utf8.es-ES.zip",
            [
                "vtessets.es-ES.csv",
                "vtescrypt.es-ES.csv",
                "vteslib.es-ES.csv",
            ],
        ),
    }

    def __init__(self, aliases: Dict[str, str] = None):
        """Use config.ALIASES as aliases"""
        super().__init__(aliases=config.ALIASES if aliases is None else aliases)

    def __iter__(self):
        """When iterating only, return each card once."""
        for key, card in self.items():
            if isinstance(key, int):
                yield card

    def __len__(self):
        """Count the number of different cards in Map."""
        return len([c for c in self])

    def load(self) -> None:
        """Load VTES cards from KRCG static."""
        r = requests.request("GET", config.KRCG_STATIC_SERVER + "/data/vtes.json")
        r.raise_for_status()
        self.clear()
        self.from_json(r.json())

    def add(self, card: Card) -> None:
        """Add a card to the map, with all name variatoins.

        Can be called multiple times for a single card, for translations.
        """
        self[card.id] = card
        self._add_variants(card._name, card)
        for name in card.aka:
            self._add_variants(name, card)
        for _lang, name in card.i18n_variants("name"):
            # to avoid fuzzy matching translated names, they're added as aliases only
            self._add_name_and_shortcuts(name, card, alias=True)
        for aka in Card._AKA.get(card.name, []):
            self[aka] = card

    def load_from_vekn(self):
        """Load from official VEKN CSV files."""
        set_dict = sets.SetMap()
        # download the zip files containing the official CSV
        main_files = utils.get_zip_csv(self._VEKN_CSV[0], *self._VEKN_CSV[1])
        i18n_files = {
            lang: utils.get_zip_csv(url, *filenames)
            for lang, (url, filenames) in self._VEKN_CSV_I18N.items()
        }
        # load sets
        for line in main_files[0]:
            set_ = sets.Set()
            set_.from_vekn(line)
            set_dict.add(set_)
        for lang, files in i18n_files.items():
            for line in files[0]:
                set_dict[line["Abbrev"]].i18n_set(lang, {"name": line["Full Name"]})
        # load cards
        for line in itertools.chain.from_iterable(main_files[1:]):
            card = Card()
            card.from_vekn(line, set_dict)
            self.add(card)
        for lang, files in i18n_files.items():
            for line in itertools.chain.from_iterable(files[1:]):
                name = line.pop("Name")
                cid = int(line.pop("Id"))
                line["Name"] = line.pop("Name " + lang)
                card = self[cid]
                if card._name != name:
                    warnings.warn(f"{name} does not match {cid} in {lang} translation")
                trans = {
                    "name": line["Name"],
                    "url": card._compute_url(lang[:2]),
                    "card_text": line["Card Text"].replace("(D)", "Ⓓ"),
                    "sets": {
                        set_name: set_dict[set_name].i18n(lang[:2], "name")
                        for set_name in card.sets.keys()
                        if set_name in set_dict
                    },
                }
                if "Flavor Text" in line:
                    trans["flavor_text"] = line["Flavor Text"]
                card.i18n_set(lang[:2], trans)
                self.add(card)
        urllib.request.urlcleanup()

    def load_rulings(self) -> None:
        """Load card rulings from package YAML files."""
        for ruling in rulings.RulingReader():
            for cid, name in ruling.cards:
                if self[cid].name != name:
                    warnings.warn(f"Rulings: {name} does not match {self[cid]}")
                self[cid].rulings["text"].append(ruling.text)
                for ref, link in ruling.links.items():
                    self[cid].rulings["links"][ref] = link

    def to_json(self) -> Dict:
        """Return a compact dict representation for JSON serialization."""
        return [card.to_json() for card in self]

    def from_json(self, state: Dict):
        """Initialize from a JSON dict."""
        for dict_ in state:
            card = Card()
            card.from_json(dict_)
            self.add(card)

    def _add_variants(self, name: str, card: Card):
        """Add all variants of the name."""
        self._add_name_and_shortcuts(name, card)
        if name[-5:].lower() == ", the":
            self._add_name_and_shortcuts("the " + name[:-5], card)

    def _add_name_and_shortcuts(self, name: str, card: Card, alias: bool = False):
        """Add the name and shortcuts (splitting comma-separated qualifiers)."""
        suffix = " (ADV)" if card.adv else ""
        while True:
            if alias:
                self.add_alias(name + suffix, card.name)
            else:
                self[name + suffix] = card
            name = name.rsplit(",", 1)
            if len(name) < 2:
                return
            name = name[0]
            if len(name) <= self.threshold:
                return


class CardTrie:
    """A helper class for text search inside a card.

    Combines results from multiple languages
    """

    def __init__(self, attribute: str):
        """Arg attribute is usually name, card_text, flavor_text or draft."""
        self.attribute = attribute
        self.tries = collections.defaultdict(utils.Trie)

    def clear(self) -> None:
        """Clear content."""
        self.tries.clear()

    def add(self, card: Card) -> None:
        """Add a card to the tries."""
        self.tries["en"].add(getattr(card, self.attribute, ""), card)
        for lang, trans in card.i18n_variants(self.attribute):
            self.tries[lang[:2]].add(trans, card)

    def search(self, text: str, lang: str = None) -> Dict[str, collections.Counter]:
        """Search for `text`, in english and optional `lang`.

        Returns:
            A dict of scored results as {lang: Counter}, with no duplicates.
            If the same card is matched in multiple both `lang` and english,
            prefer the `lang` version.
        """
        base_search = self.tries["en"].search(text)
        lang_search = collections.Counter()
        if lang in self.tries:
            lang_search = self.tries[lang].search(text)
        for k in base_search & lang_search:
            del base_search[k]
        ret = {"en": base_search}
        if lang:
            ret[lang] = lang_search
        return ret


class CardSearch:
    """A class indexing cards over multiple dimensions, for search purposes.

    Set dimensions are simple sets indexing specific values.
    They can be searched for any combination of values.
    They are all case insensitive, except for the `discipline` dimension.
    Only cards matching all values are returned (AND combination),
    combined successive calls to get OR combinations.

    Trie dimensions provide prefix-based case insensitive text search.
    As for set dimensions, only card with words matching all prefixes are returned.

    Usage:
        >>> # init is pretty straightforward
        >>> search = CardSearch()
        >>> for card in some_collection:
        >>>     search.add(card)

        >>> # call search to search anything, beware to provide lists for set dimensions
        >>> search(text="equip loc")
        >>> search(type=["equipment"])
        >>> search(type=["Crypt"], discipline=["ANI", "aus"], clan=["Tzimisce"])

        >>> # easily check dimensions and available values
        >>> print(search.dimensions)
        >>> print(search.set_dimensions_enums)

    Subclassing for search improvement should be pretty straightforward:

    ```
    MySearch(CardSearch):
        set_dimensions = CardSearch.set_dimensions + ["additional_dimension"]

        def add(self, card):
            super().add(card)
            if re.search(r"something interesting", card):
                self.additional_dimension.add(card)
    ```
    """

    _MAX_GROUP = 6
    _TRAITS = [
        "Black Hand",
        "Seraph",
        "Red List",
        "Infernal",
        "Slave",
        "Scarce",
        "Sterile",
    ]
    _TITLES = {
        "Camarilla": {"Primogen", "Prince", "Justicar", "Inner Circle", "Imperator"},
        "Sabbat": {"Bishop", "Archbishop", "Cardinal", "Regent", "Priscus"},
        "Anarch": {"Baron"},
        "Laibon": {"Magaji", "Kholo"},
    }
    _ALL_TITLES = sum(map(list, _TITLES.values()), [])
    trie_dimensions = [
        "name",
        "card_text",
        "flavor_text",
    ]
    set_dimensions = [
        "type",
        "sect",
        "clan",
        "title",
        "city",
        "trait",
        "group",
        "capacity",
        "discipline",
        "artist",
        "set",
        "rarity",
        "precon",
        "bonus",
    ]
    # for those dimensions, all values must match
    # in other dimensions, any value can match.
    intersect_set_dimensions = ["trait", "discipline", "bonus"]

    def __init__(self):
        for attr in self.trie_dimensions:
            setattr(self, attr, CardTrie(attr))
        for attr in self.set_dimensions:
            setattr(self, attr, collections.defaultdict(set))
        # caches
        self._all = set()
        self._set_dimensions_enums = None
        self._normalized_set_enum_map = None

    def __bool__(self):
        return bool(self._all)

    def clear(self):
        """Clear content."""
        for attr in self.set_dimensions + self.trie_dimensions:
            try:
                getattr(self, attr).clear()
            except TypeError:
                pass

    def add(self, card: Card):
        """Add a card to the engine."""
        self._set_dimensions_enums = None
        self._normalized_set_enum_map = None
        self._all.add(card)
        self.name.add(card)
        for type_ in card.types:
            self.type[type_].add(card)
        for artist in card.artists:
            self.artist[artist].add(card)
        for set_, rarities in card.sets.items():
            self.set[set_].add(card)
            for rarity in rarities:
                if "precon" in rarity:
                    self.precon[": ".join([set_, rarity["precon"]])].add(card)
                if "rarity" in rarity:
                    self.rarity[rarity["rarity"]].add(card)
        if "Master" in card.types and re.search(r"(t|T)rifle", card.card_text):
            self.bonus["Trifle"].add(card)
        if card.crypt:
            self.type["Crypt"].add(card)
        else:
            self.type["Library"].add(card)
        for clan in card.clans:
            self.clan[clan].add(card)
        if not card.clans:
            self.clan["none"].add(card)
        if card.group:
            try:
                self.group[int(card.group)].add(card)
            except ValueError:  # group "any"
                for i in range(1, self._MAX_GROUP + 1):
                    self.group[i].add(card)
        if card.capacity:
            self.capacity[card.capacity].add(card)
        if card.capacity_change:
            self.bonus["Capacity"].add(card)
        if re.search(r"\+(\d|X)\s+(b|B)leed", card.card_text):
            self.bonus["Bleed"].add(card)
        for trait in re.findall(
            f"({'|'.join(t.lower() for t in self._TRAITS)})", card.card_text.lower()
        ):
            trait = trait.title()
            self.trait[trait].add(card)
        # more complex classifications in subfunctions for readability
        self._handle_text(card)
        self._handle_disciplines(card)
        self._handle_sect(card)
        self._handle_stealth_intercept(card)
        self._handle_titles(card)
        self._handle_exceptions(card)

    @property
    def dimensions(self):
        return self.trie_dimensions + self.set_dimensions + ["text"]

    @property
    def set_dimensions_enums(self):
        if not self._set_dimensions_enums:
            self._set_dimensions_enums = {
                attr: sorted(set(getattr(self, attr).keys()))
                for attr in self.set_dimensions
            }
        return self._set_dimensions_enums

    def __call__(self, **kwargs) -> Set[Card]:
        """Actual search."""
        lang = kwargs.pop("lang", "en")[:2]
        keys = set(kwargs.keys())
        invalid_keys = keys - set(self.dimensions)
        if invalid_keys:
            raise ValueError(
                f"Invalid search dimension{'s' if len(invalid_keys) > 1 else ''}: "
                f"{', '.join(invalid_keys)}. "
                f"Valid dimensions are: {', '.join(self.dimensions)}"
            )
        if "text" in keys:
            result = set()
            for dim in self.trie_dimensions:
                result |= self._text_search(dim, kwargs["text"], lang)
        else:
            result = copy.copy(self._all)
        for dim in self.trie_dimensions:
            if kwargs.get(dim):
                result &= self._text_search(dim, kwargs.get(dim), lang)
        for dim in self.set_dimensions:
            values = kwargs.get(dim, None)
            if not values:
                continue
            # allow providing providing dim=value instead of dim=[value]
            if isinstance(values, str):
                values = [values]
            if not isinstance(values, collections.abc.Iterable):
                values = [values]
            dim_result = None
            for value in values:
                # normalize value if it is not a discipline: those are case sensitive
                if dim != "discipline":
                    value = self._normalized_map.get(dim, {}).get(
                        utils.normalize(value)
                    )
                if dim_result is None:
                    dim_result = copy.copy(getattr(self, dim, {}).get(value, set()))
                elif dim in self.intersect_set_dimensions:
                    dim_result &= getattr(self, dim, {}).get(value, set())
                else:
                    dim_result |= getattr(self, dim, {}).get(value, set())
            result &= dim_result
        return result

    def _text_search(self, dim: str, text: str, lang: str = "en") -> Set[Card]:
        """Helper that combines english and provided language results."""
        result = set()
        result |= set(
            itertools.chain.from_iterable(
                m.keys() for m in getattr(self, dim).search(text).values()
            )
        )
        if lang != "en":
            result |= set(
                itertools.chain.from_iterable(
                    m.keys()
                    for m in getattr(self, dim).search(text, lang=lang).values()
                )
            )
        return result

    @property
    def _normalized_map(self):
        """Used by __call__ (the search itself) to match set dimensions values

        This allows to match values case insensitively
        but still return the value with the original case.

        This way, self.set_dimensions_enums has proper casing and can be displayed
        to a user without additional processing.
        """
        if not self._normalized_set_enum_map:
            self._normalized_set_enum_map = {
                dim: {utils.normalize(v): v for v in getattr(self, dim)}
                for dim in self.set_dimensions
            }
        return self._normalized_set_enum_map

    def _handle_text(self, card):
        """Helper handling card text."""
        self.card_text.add(card)
        if card.flavor_text:
            self.flavor_text.add(card)
        if card.draft:
            self.bonus["draft"].add(card.draft, card)

    def _handle_disciplines(self, card):
        """Helper handling card disciplines."""
        for discipline in card.disciplines:
            self.discipline[discipline].add(card)
            self.discipline[discipline.lower()].add(card)
        if not card.disciplines:
            self.discipline["none"].add(card)
        elif card.library and len(card.disciplines) > 1:
            self.discipline["multi"].add(card)
        else:
            self.discipline["mono"].add(card)
        if "[FLIGHT]" in card.card_text:
            self.discipline["flight"].add(card)
        if card.combo:
            self.discipline["combo"].add(card)
        if card.multidisc:
            self.discipline["choice"].add(card)

    def _handle_sect(self, card):
        """Helper handling sects."""
        if card.crypt:
            if re.search(r"^(\[MERGED\] )?Sabbat", card.card_text):
                self.sect["Sabbat"].add(card)
            if re.search(r"^(\[MERGED\] )?Camarilla", card.card_text):
                self.sect["Camarilla"].add(card)
            if re.search(r"^(\[MERGED\] )?Laibon", card.card_text):
                self.sect["Laibon"].add(card)
            if re.search(r"^(\[MERGED\] )?Anarch", card.card_text):
                self.sect["Anarch"].add(card)
            if re.search(r"^(\[MERGED\] )?Independent", card.card_text):
                self.sect["Independent"].add(card)
        else:
            if re.search(r"Requires a( ready)? (S|s)abbat", card.card_text):
                self.sect["Sabbat"].add(card)
            if re.search(r"Requires a( ready)? (C|c)amarilla", card.card_text):
                self.sect["Camarilla"].add(card)
            if re.search(r"Requires a( ready)? (L|l)aibon", card.card_text):
                self.sect["Laibon"].add(card)
            if re.search(
                r"Requires a( ready|n)( (I|i)ndependent or)? (A|a)narch",
                card.card_text,
            ):
                self.sect["Anarch"].add(card)
            if re.search(r"Requires a( ready|n) (I|i)ndependent", card.card_text):
                self.sect["Independent"].add(card)

    def _handle_stealth_intercept(self, card):
        """Helper handling stealth and intercept."""
        if re.search(r"\+(\d|X)\s+(i|I)ntercept", card.card_text):
            self.bonus["Intercept"].add(card)
        # do not include stealthed actions as stealth cards
        if re.search(r"\+(\d|X)\s+(s|S)tealth (?!Ⓓ|action|political)", card.card_text):
            self.bonus["Stealth"].add(card)
        # stealth/intercept maluses count has bonus of the other
        if not set(card.types) & {"Master", "Vampire", "Imbued"}:
            if re.search(r"-(\d|X)\s+(s|S)tealth", card.card_text):
                self.bonus["Intercept"].add(card)
            if re.search(r"-(\d|X)\s+(i|I)ntercept", card.card_text):
                self.bonus["Stealth"].add(card)
        # list reset stealth as intercept
        if re.search(r"stealth .* to 0", card.card_text):
            self.bonus["Intercept"].add(card)
        # list block denials as stealth
        if re.search(r"attempt fails", card.card_text):
            self.bonus["Stealth"].add(card)

    def _handle_titles(self, card):
        """Helper handling titles, votes and city."""
        if card.title:
            self.title[card.title].add(card)
            self.bonus["Votes"].add(card)
        if re.search(r"(\d|X)\s+(v|V)ote", card.card_text):
            self.bonus["Votes"].add(card)
        for title in re.findall(
            f"({'|'.join(t.lower() for t in self._ALL_TITLES)})", card.card_text.lower()
        ):
            title = title.title()
            self.title[title].add(card)
            for sect, titles in self._TITLES.items():
                if title in titles:
                    self.sect[sect].add(card)

        city = re.search(
            r"(?:Prince|Baron|Archbishop) of ((?:[A-Z][A-Za-z\s-]{3,})+)",
            card.card_text,
        )
        if city:
            city = city.group(1)
            if city[-6:] == " as a ":
                city = city[:-6]
            if city == "Washington":
                city = "Washington, D.C."
            self.city[city].add(card)
            self.bonus["Votes"].add(card)
        if card.library:
            if re.search(r"Requires a( ready)? titled (S|s)abbat", card.card_text):
                self.sect["Sabbat"].add(card)
                for title in self._TITLES["Sabbat"]:
                    self.title[title].add(card)
            if re.search(r"Requires a( ready)? titled (C|c)amarilla", card.card_text):
                self.sect["Camarilla"].add(card)
                for title in self._TITLES["Camarilla"]:
                    self.title[title].add(card)
            if re.search(r"Requires a( ready)? titled vampire", card.card_text):
                for title in self._ALL_TITLES + ["1 vote", "2 votes"]:
                    self.title[title].add(card)
            if re.search(r"Requires a( ready)? (M|m)agaji", card.card_text):
                self.title["Magaji"].add(card)
                self.sect["Laibon"].add(card)

    def _handle_exceptions(self, card):
        """Search exceptions not handled automatically."""
        # The Baron has his name in card text, but is not an Anarch Baron.
        if card.name == "The Baron":
            self.sect["Anarch"].remove(card)
            self.title["Baron"].remove(card)
        # Gwen has another set of disciplines under condition
        elif card.name == "Gwen Brand":
            self.discipline["ANI"].add(card)
            self.discipline["AUS"].add(card)
            self.discipline["CHI"].add(card)
            self.discipline["FOR"].add(card)
