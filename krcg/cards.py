from typing import Callable, Dict, Generator, Tuple, Union
import collections
import copy
import csv
import datetime
import functools
import io
import itertools
import pkg_resources
import re
import requests
import tempfile
import warnings
import yaml
import zipfile

from . import config
from . import utils


class Card(utils.i18nMixin, utils.JsonMixin, utils.NamedMixin):
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
        "vision": "vin",  # avoid coollision with visceratika
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
            # "An": "Anathema",
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
    }
    _REPRINTS_RELEASE_DATE = {
        ("KoT", "Reprint Bundle 1"): datetime.date(2018, 5, 5),
        ("KoT", "Reprint Bundle 2"): datetime.date(2018, 5, 5),
        ("HttB", "Reprint Bundle 1"): datetime.date(2018, 7, 14),
        ("HttB", "Reprint Bundle 2"): datetime.date(2018, 7, 14),
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
        self.banned = None
        self.artist = []
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

    @functools.cached_property
    def vekn_name(self) -> str:
        assert self.id, "Card is not initialized"
        ret = self._name
        if self.adv:
            ret += " (ADV)"
        return ret

    @functools.cached_property
    def name(self) -> str:
        assert self.id, "Card is not initialized"
        ret = self._name
        if ret[-5:] == ", The":
            ret = "The " + ret[:-5]
        ret = ret.replace("(TM)", "™")
        if self.adv:
            ret += " (ADV)"
        return ret

    @functools.cached_property
    def crypt(self) -> bool:
        return set(self.types) & {"Imbued", "Vampire"}

    @property
    def library(self) -> bool:
        return not self.crypt

    @classmethod
    def _from_vekn(cls, setmap: dict, data: dict):
        ret = cls()

        def split(field, sep):
            return [s for s in map(str.strip, data[field].split(sep)) if s]

        def str_or_none(field):
            return data[field].lower() or None if field in data else None

        def bool_or_none(field):
            return bool(data[field]) if field in data else None

        def int_or_none(field):
            try:
                return int(data[field]) if data.get(field) else None
            except ValueError:
                warnings.warn(f"expected an integer for {field}: {data}")

        ret.id = int(data["Id"])
        ret._name = data["Name"]
        ret.aka = split("Aka", ";")
        ret.types = split("Type", "/")
        ret.clans = split("Clan", "/")
        capacity = data.get("Capacity")
        if capacity and re.search(r"^[^\d]", capacity):
            ret.capacity_change = capacity
        else:
            ret.capacity = int_or_none("Capacity")
        # disciplines
        discipline_key = "Discipline" if "Discipline" in data else "Disciplines"
        if "/" in data[discipline_key]:
            ret.multidisc = True
        if "&" in data[discipline_key]:
            ret.combo = True
        for s in re.split(r"[\s/&]+", data[discipline_key]):
            # distinguish vision (vin) from visceratika (vis)
            if s.lower() == "vis" and "Imbued" in ret.types:
                s = "vin"
            s = Card._DISC_MAP.get(s.lower(), s)
            if s:
                ret.disciplines.append(s)
        ret.card_text = (
            data["Card Text"].replace("(D)", "Ⓓ").replace("{", "").replace("}", "")
        )
        ret.sets = dict(
            Card._decode_set(setmap, rarity)
            for rarity in map(str.strip, data["Set"].split(","))
            if rarity
        )
        if not ret.sets:
            warnings.warn(f"no set found for {ret}")
        ret.banned = cls._BAN_MAP[data["Banned"]] if data["Banned"] else None
        ret.artists = [
            cls._ARTISTS_FIXES.get(s, s)
            for s in map(str.strip, re.split(r"[;,&]+(?!\sJr\.)", data["Artist"]))
            if s
        ]
        ret.adv = bool_or_none("Adv")
        # group can be "any"
        ret.group = str_or_none("Group")
        ret.title = str_or_none("Title")
        ret.pool_cost = str_or_none("Pool Cost")  # can be X
        ret.blood_cost = str_or_none("Blood Cost")  # can be X
        ret.conviction_cost = str_or_none("Conviction Cost")  # str for consistency
        ret.burn_option = bool_or_none("Burn Option")
        ret.flavor_text = data["Flavor Text"] if "Flavor Text" in data else None
        ret.draft = data["Draft"] if "Draft" in data else None
        # computations last: some properties (ie. name) are cached,
        # only use them once everything else is set
        ret.url = ret._compute_url()
        return ret

    def _compute_url(self, lang: str = None):
        return (
            config.KRCG_STATIC_SERVER
            + "/data/"
            + (f"{lang[:2]}/" if lang else "")
            + re.sub(r"[^\w\d]", "", utils.normalize(self.name).lower())
            + ".jpg"
        )

    @staticmethod
    def _decode_set(setmap: dict, expansion: str) -> str:
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
            date = setmap[abbrev].release_date
        except KeyError:
            warnings.warn(f"unknown set: {abbrev}")
            date = None
        rarities = (match["rarity"] or "").split("/")
        ret = [
            r
            for r in map(lambda a: Card._decode_rarity(a, abbrev, date), rarities)
            if r
        ]
        return setmap[abbrev].name, ret

    @staticmethod
    def _decode_rarity(rarity: str, abbrev: str, date: datetime.date) -> dict:
        match = re.match(
            r"^(?P<base>[a-zA-Z]+)?(?P<count>[0-9½]+)?$",
            rarity,
        )
        ret = {"Release Date": date}
        if not match:
            warnings.warn(f"unknown rarity {rarity}")
            return
        base = match.group("base")
        count = match.group("count")
        if not base:
            ret["Copies"] = int(count or 1)
            return ret
        code = Card._RARITY_BOOSTER_CODES.get(base)
        if code:
            ret["Rarity"] = code
        else:
            code = Card._RARITY_PRECON_CODES.get(abbrev, {}).get(base)
            if code:
                ret["Precon"] = code
            elif code is None:
                warnings.warn(f"unknown base: {base} in {rarity}")
                return
        # fix release date for reprints
        if (abbrev, code) in Card._REPRINTS_RELEASE_DATE:
            ret["Release Date"] = Card._REPRINTS_RELEASE_DATE[(abbrev, code)]
        count = match["count"]
        if not count and "Precon" in ret:
            count = 1
        # thank Aye/Orun for this "½" frequency
        if count == "½":
            count = 0.5
        if count:
            count = int(count)
            if "Rarity" in ret:
                try:
                    ret["Frequency"] = count
                except KeyError:
                    warnings.warn(f"unknown frequency {count} in {rarity}")
            else:
                ret["Copies"] = count
        return ret


class CardMap(utils.FuzzyDict):
    _StrGenerator = Generator[str, None, None]
    _CardReference = Union[str, int]

    def __init__(self, aliases: Dict[str, str] = None):
        super().__init__(aliases=config.REMAP if aliases is None else aliases)

    def __iter__(self):
        for key, card in self.items():
            if isinstance(key, int):
                yield card

    def __len__(self):
        return len([c for c in self])

    def load(self):
        r = requests.request("GET", config.KRCG_STATIC_SERVER + "/data/vtes.json")
        r.raise_for_status()
        self.clear()
        self.__setstate__(r.json())

    def add(self, card: Card):
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
        sets = _SetMap()
        CardMap._load_vekn_zip(
            config.VEKN_VTES_URL,
            [
                (
                    config.VEKN_VTES_SETS_FILENAME,
                    lambda line: sets.add(Set._from_vekn(line)),
                ),
                (
                    config.VEKN_VTES_LIBRARY_FILENAME,
                    lambda line: self.add(Card._from_vekn(sets, line)),
                ),
                (
                    config.VEKN_VTES_CRYPT_FILENAME,
                    lambda line: self.add(Card._from_vekn(sets, line)),
                ),
            ],
        )

        for lang, url in config.VEKN_VTES_I18N_URLS.items():
            CardMap._load_vekn_zip(
                url,
                [
                    (
                        config.VEKN_VTES_I18N_SETS_FILENAME % lang,
                        CardMap._load_set_i18n(sets, lang),
                    ),
                    (
                        config.VEKN_VTES_I18N_LIBRARY_FILENAME % lang,
                        self._load_card_i18n(sets, lang),
                    ),
                    (
                        config.VEKN_VTES_I18N_CRYPT_FILENAME % lang,
                        self._load_card_i18n(sets, lang),
                    ),
                ],
            )

    def load_cards_rulings(self) -> None:
        reader = _RulingReader(
            yaml.safe_load(
                pkg_resources.resource_string("rulings", "rulings-links.yaml")
            )
        )
        for ruling in itertools.chain(
            reader._from_krcg(
                yaml.safe_load(
                    pkg_resources.resource_string("rulings", "cards-rulings.yaml")
                )
            ),
            reader._from_krcg(
                yaml.safe_load(
                    pkg_resources.resource_string("rulings", "general-rulings.yaml")
                )
            ),
        ):
            for cid, name in ruling.cards:
                if self[cid].name != name:
                    warnings.warn(f"Rulings: {name} does not match {self[cid]}")
                self[cid].rulings["text"].append(ruling.text)
                for ref, link in ruling.links.items():
                    self[cid].rulings["links"][ref] = link

    def __getstate__(self):
        return [card.__getstate__() for card in self]

    def __setstate__(self, state):
        for dic in state:
            card = Card()
            card.__setstate__(dic)
            self.add(card)

    def _add_variants(self, name: str, card: Card):
        self._add_name_and_shortcuts(name, card)
        if name[-5:].lower() == ", the":
            self._add_name_and_shortcuts("the " + name[:-5], card)

    def _add_name_and_shortcuts(self, name: str, card: Card, alias: bool = False):
        suffix = " (ADV)" if card.adv else ""
        while True:
            if alias:
                self.add_alias(name + suffix, card)
            else:
                self[name + suffix] = card
            name = name.rsplit(",", 1)
            if len(name) < 2:
                return
            name = name[0]
            if len(name) <= self.threshold:
                return

    @staticmethod
    def _load_set_i18n(sets, lang):
        def load_line(line):
            line.pop("Release Date", None)
            line.pop("Company", None)
            abbrev = line.pop("Abbrev")
            sets[abbrev].i18n_set(lang, {"name": line["Full Name"]})

        return load_line

    def _load_card_i18n(self, sets, lang):
        def load_line(line):
            name = line.pop("Name")
            cid = int(line.pop("Id"))
            line["Name"] = line.pop("Name " + lang)
            c = self[cid]
            if c._name != name:
                warnings.warn(f"{name} does not match {cid} in {lang} translation")
            trans = {
                "name": line["Name"],
                "url": c._compute_url(lang),
                "card_text": line["Card Text"],
                "sets": {
                    set_name: sets[set_name].i18n(lang, "name")
                    for set_name in c.sets.keys()
                    if set_name in sets
                },
            }
            if "Flavor Text" in line:
                trans["flavor_text"] = line["Flavor Text"]
            c.i18n_set(lang, trans)

        return load_line

    @staticmethod
    def _load_vekn_zip(url, path_func: Dict[str, Callable]):
        r = requests.request("GET", url)
        r.raise_for_status()
        with tempfile.NamedTemporaryFile("wb", suffix=".zip") as f:
            f.write(r.content)
            f.flush()
            z = zipfile.ZipFile(f.name)
            for path, func in path_func:
                with z.open(path) as bytestream:
                    for line in csv.DictReader(io.TextIOWrapper(bytestream)):
                        func(line)


class CardTrie:
    def __init__(self, attribute):
        self.attribute = attribute
        self.tries = collections.defaultdict(utils.Trie)

    def clear(self):
        self.tries.clear()

    def add(self, card: Card):
        self.tries["en"].add(getattr(card, self.attribute, ""), card)
        for lang, trans in card.i18n_variants(self.attribute):
            self.tries[lang].add(trans, card)

    def search(self, text: str, lang: str = None):
        base_search = self.completion.search(text)
        lang_search = collections.Counter()
        if lang in self.tries:
            lang_search = self.tries[lang].search(text)
        for k in base_search & lang_search:
            del base_search[k]
        return base_search + lang_search


class CardSearch:
    _TRAITS = [
        "black hand",
        "seraph",
        "red list",
        "infernal",
        "slave",
        "scarce",
        "sterile",
    ]
    _TITLES = {
        "camarilla": {"primogen", "prince", "justicar", "inner circle", "imperator"},
        "sabbat": {"bishop", "archbishop", "cardinal", "regent", "priscus"},
        "anarch": {"baron"},
        "laibon": {"magaji", "kholo"},
    }
    _ALL_TITLES = sum(map(list, _TITLES.values()), [])
    TRIE_DIMENSIONS = [
        "name",
        "text",
        "flavor_text",
    ]
    SET_DIMENSIONS = [
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
    NORMALIZED_DIMENSIONS = [
        "type",
        "sect",
        "clan",
        "title",
        "city",
        "trait",
        "rarity",
        "bonus",
    ]

    def __init__(self):
        for attr in self.TRIE_DIMENSIONS:
            setattr(self, attr, CardTrie(attr))
        for attr in self.SET_DIMENSIONS:
            setattr(self, attr, collections.defaultdict(set))
        self._all = set()

    def clear(self):
        for attr in self.SET_DIMENSIONS + self.TRIE_DIMENSIONS:
            try:
                getattr(self, attr).clear()
            except TypeError:
                pass

    def add(self, card: Card):
        self._all.add(card)
        self.name.add(card)
        for type_ in card.types:
            self.type[type_.lower()].add(card)
        for artist in card.artists:
            self.artist[artist].add(card)
        for set_, rarities in card.sets.items():
            self.set[set_].add(card)
            for rarity in rarities:
                if "Precon" in rarity:
                    self.precon[": ".join([set_, rarity["Precon"]])].add(card)
                if "Rarity" in rarity:
                    self.rarity[rarity["Rarity"]].add(card)
        if "Master" in card.types and re.search(r"(t|T)rifle", card.card_text):
            self.bonus["trifle"].add(card)
        if card.crypt:
            self.type["crypt"].add(card)
        else:
            self.type["library"].add(card)
        for clan in card.clans:
            self.clan[clan.lower()].add(card)
        if not card.clans:
            self.clan["none"].add(card)
        if card.group:
            try:
                self.group[int(card.group)].add(card)
            except ValueError:  # group "any"
                for i in range(1, 7):
                    self.group[i].add(card)
        if card.capacity:
            self.capacity[card.capacity].add(card)
        if card.capacity_change:
            self.bonus["capacity"].add(card)
        if re.search(r"\+(\d|X)\s+(b|B)leed", card.card_text):
            self.bonus["bleed"].add(card)
        for trait in re.findall(f"({'|'.join(self._TRAITS)})", card.card_text.lower()):
            self.trait[trait].add(card)
        self._handle_text(card)
        self._handle_disciplines(card)
        self._handle_sect(card)
        self._handle_stealth_intercept(card)
        self._handle_titles(card)
        self._handle_exceptions(card)

    def dimensions(self):
        return {attr: set(getattr(self, attr).keys()) for attr in self.SET_DIMENSIONS}

    def __call__(self, **kwargs):
        if "any_text" in kwargs:
            result = set()
            for dim in self.TRIE_DIMENSIONS:
                result |= set(x[0] for x in getattr(self, dim).search(kwargs.get(dim)))
        else:
            result = copy.copy(self._all)
        for dim in self.TRIE_DIMENSIONS:
            if dim in kwargs:
                result &= set(x[0] for x in getattr(self, dim).search(kwargs.get(dim)))
        for dim in self.SET_DIMENSIONS:
            for value in kwargs.get(dim) or []:
                if dim in self.NORMALIZED_DIMENSIONS:
                    value = utils.normalize(value)
                result &= getattr(self, dim).get(value, set())
        return result

    def _handle_text(self, card):
        self.text.add(card)
        if card.flavor_text:
            self.flavor_text.add(card)
        if card.draft:
            self.bonus["draft"].add(card.draft, card)

    def _handle_disciplines(self, card):
        for discipline in card.disciplines:
            self.discipline[discipline].add(card)
        if not card.disciplines:
            self.discipline["none"].add(card)
        if card.library and len(card.disciplines) > 1:
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
        if card.crypt:
            if re.search(r"^(\[MERGED\] )?Sabbat", card.card_text):
                self.sect["sabbat"].add(card)
            if re.search(r"^(\[MERGED\] )?Camarilla", card.card_text):
                self.sect["camarilla"].add(card)
            if re.search(r"^(\[MERGED\] )?Laibon", card.card_text):
                self.sect["laibon"].add(card)
            if re.search(r"^(\[MERGED\] )?Anarch", card.card_text):
                self.sect["anarch"].add(card)
            if re.search(r"^(\[MERGED\] )?Independent", card.card_text):
                self.sect["independent"].add(card)
        else:
            if re.search(r"Requires a( ready)? (S|s)abbat", card.card_text):
                self.sect["sabbat"].add(card)
            if re.search(r"Requires a( ready)? (C|c)amarilla", card.card_text):
                self.sect["camarilla"].add(card)
            if re.search(r"Requires a( ready)? (L|l)aibon", card.card_text):
                self.sect["laibon"].add(card)
            if re.search(
                r"Requires a( ready|n)( (I|i)ndependent or)? (A|a)narch",
                card.card_text,
            ):
                self.sect["anarch"].add(card)
            if re.search(r"Requires a( ready|n) (I|i)ndependent", card.card_text):
                self.sect["independent"].add(card)

    def _handle_stealth_intercept(self, card):
        if re.search(r"\+(\d|X)\s+(i|I)ntercept", card.card_text):
            self.bonus["intercept"].add(card)
        # do not include stealthed actions as stealth cards
        if re.search(r"\+(\d|X)\s+(s|S)tealth (?!Ⓓ|action|political)", card.card_text):
            self.bonus["stealth"].add(card)
        # stealth/intercept maluses count has bonus of the other
        if not set(card.types) & {"master", "vampire", "imbued"}:
            if re.search(r"-(\d|X)\s+(s|S)tealth", card.card_text):
                self.bonus["intercept"].add(card)
            if re.search(r"-(\d|X)\s+(i|I)ntercept", card.card_text):
                self.bonus["stealth"].add(card)
        # list reset stealth as intercept
        if re.search(r"stealth .* to 0", card.card_text):
            self.bonus["intercept"].add(card)
        # list block denials as stealth
        if re.search(r"attempt fails", card.card_text):
            self.bonus["stealth"].add(card)

    def _handle_titles(self, card):
        if card.title:
            self.title[card.title].add(card)
            self.bonus["votes"].add(card)
        if re.search(r"(\d|X)\s+(v|V)ote", card.card_text):
            self.bonus["votes"].add(card)
        for title in re.findall(
            f"({'|'.join(self._ALL_TITLES)})", card.card_text.lower()
        ):
            self.title[title].add(card)
            for sect, titles in self._TITLES.items():
                if title in titles:
                    self.sect[sect].add(card)
        if card.crypt:
            city = re.search(
                r"(?:Prince|Baron|Archbishop) of ((?:[A-Z][A-Za-z\s-]{3,})+)",
                card.card_text,
            )
            if city:
                city = city.group(1).lower()
                if city[-5:] == "as a ":
                    city = city[:-5]
                if city == "washington":
                    city = "washington, d.c."
                self.city[city].add(card)
                self.bonus["votes"].add(card)
        else:
            if re.search(r"Requires a( ready)? titled (S|s)abbat", card.card_text):
                self.sect["sabbat"].add(card)
                for title in self._TITLES["sabbat"]:
                    self.title[title].add(card)
            if re.search(r"Requires a( ready)? titled (C|c)amarilla", card.card_text):
                self.sect["camarilla"].add(card)
                for title in self._TITLES["camarilla"]:
                    self.title[title].add(card)
            if re.search(r"Requires a( ready)? titled vampire", card.card_text):
                for title in self._ALL_TITLES + ["1 vote", "2 votes"]:
                    self.title[title].add(card)
            if re.search(r"Requires a( ready)? (M|m)agaji", card.card_text):
                self.title["magaji"].add(card)
                self.sect["laibon"].add(card)

    def _handle_exceptions(self, card):
        if card.name == "The Baron":
            self.sect["anarch"].remove(card)
        elif card.name == "Gwen Brand":
            self.discipline["ANI"].add(card)
            self.discipline["AUS"].add(card)
            self.discipline["CHI"].add(card)
            self.discipline["FOR"].add(card)


class Set(utils.i18nMixin, utils.JsonMixin, utils.NamedMixin):
    def __init__(self, **kwargs):
        super().__init__()
        self.id = 0
        self.abbrev = kwargs.pop("abbrev", None)
        self.release_date = kwargs.pop("release_date", None)
        self.name = kwargs.pop("full_name", None)
        self.company = kwargs.pop("abbrev", None)

    @classmethod
    def _from_vekn(cls, data: dict):
        ret = cls()
        ret.id = int(data["Id"])
        ret.abbrev = data["Abbrev"]
        ret.release_date = datetime.datetime.strptime(
            data["Release Date"], "%Y%m%d"
        ).date()
        ret.name = data["Full Name"]
        ret.company = data["Company"]
        return ret


class _SetMap(dict):
    _PROMOS = [
        ["Promo-20191123", "2020 GP Promo", "20201123"],
        ["Promo-20191123", "2020 GP Promo", "20201123"],
        ["Promo-20201030", "V5 Polish Edition promo", "20201030"],
        ["Promo-20201123", "2020 GP Promo", "20201123"],
        ["Promo-20200511", "2020 Promo Pack 2", "20200511"],
        ["Promo-20191027", "2019 ACC Promo", "20191027"],
        ["Promo-20191005", "2019 AC Promo", "20191005"],
        ["Promo-20190818", "2019 EC Promo", "20190818"],
        ["Promo-20190816", "2019 DriveThruCards Promo", "20190816"],
        ["Promo-20190614", "2019 Promo", "20190614"],
        ["Promo-20190601", "2019 SAC Promo", "20190601"],
        ["Promo-20190615", "2019 NAC Promo", "20190615"],
        ["Promo-20190629", "2019 Grand Prix Promo", "20190615"],
        ["Promo-20190408", "2019 Promo Pack 1", "20190408"],
        ["Promo-20181004", "2018 Humble Bundle", "20181004"],
        ["Promo-20150219", "2015 Storyline Rewards", "20150219"],
        ["Promo-20150221", "2015 Storyline Rewards", "20150221"],
        ["Promo-20150214", "2015 Storyline Rewards", "20150214"],
        ["Promo-20150211", "2015 Storyline Rewards", "20150211"],
        ["Promo-20150216", "2015 Storyline Rewards", "20150216"],
        ["Promo-20150220", "2015 Storyline Rewards", "20150220"],
        ["Promo-20150218", "2015 Storyline Rewards", "20150218"],
        ["Promo-20150217", "2015 Storyline Rewards", "20150217"],
        ["Promo-20150213", "2015 Storyline Rewards", "20150213"],
        ["Promo-20150212", "2015 Storyline Rewards", "20150212"],
        ["Promo-20100510", "2010 Storyline promo", "20100510"],
        ["Promo-20090929", "2009 Tournament / Storyline promo", "20090929"],
        ["Promo-20090401", "2009 Tournament / Storyline promo", "20090401"],
        ["Promo-20081119", "2008 Tournament promo", "20081119"],
        ["Promo-20081023", "2008 Tournament promo", "20081023"],
        ["Promo-20080810", "2008 Storyline promo", "20080810"],
        ["Promo-20080203", "2008 Tournament promo", "20080810"],
        ["Promo-20070601", "2007 Promo", "20070601"],
        ["Promo-20070101", "Sword of Caine promo", "20070101"],
        ["Promo-20061126", "2006 EC Tournament promo", "20061126"],
        ["Promo-20061101", "2006 Storyline promo", "20061101"],
        ["Promo-20061026", "2006 Tournament promo", "20061026"],
        ["Promo-20060902", "2006 Tournament promo", "20060902"],
        ["Promo-20060710", "Third Edition promo", "20060710"],
        ["Promo-20060417", "2006 Championship promo", "20060417"],
        ["Promo-20060213", "2006 Tournament promo", "20060213"],
        ["Promo-20060123", "2006 Tournament promo", "20060123"],
        ["Promo-20051026", "Legacies of Blood promo", "20051026"],
        ["Promo-20051001", "2005 Storyline promo", "20051001"],
        ["Promo-20050914", "Legacies of Blood promo", "20050914"],
        ["Promo-20050611", "2005 Tournament promo", "20050611"],
        ["Promo-20050122", "2005 Tournament promo", "20050122"],
        ["Promo-20050115", "Kindred Most Wanted promo", "20050115"],
        ["Promo-20041015", "Fall 2004 Storyline promo", "20041015"],
        ["Promo-20040411", "Gehenna promo", "20040411"],
        ["Promo-20040409", "2004 promo", "20040409"],
        ["Promo-20040301", "Prophecies league promo", "20040301"],
        ["Promo-20031105", "Black Hand promo", "20031105"],
        ["Promo-20030901", "Summer 2003 Storyline promo", "20030901"],
        ["Promo-20030307", "Anarchs promo", "20030307"],
        ["Promo-20021201", "2003 Tournament promo", "20021201"],
        ["Promo-20021101", "Fall 2002 Storyline promo", "20021101"],
        ["Promo-20020811", "Sabbat War promo", "20020811"],
        ["Promo-20020704", "Camarilla Edition promo", "20020704"],
        ["Promo-20020201", "Winter 2002 Storyline promo", "20020201"],
        ["Promo-20011201", "Bloodlines promo", "20011201"],
        ["Promo-20010428", "Final Nights promo", "20010428"],
        ["Promo-20010302", "Final Nights promo", "20010302"],
        ["Promo-19960101", "1996 Promo", "19960101"],
    ]

    def __init__(self):
        super().__init__()
        self.add(Set(abbrev="POD", full_name="Print on Demand"))
        for abbrev, full_name, release_date in self._PROMOS:
            release_date = datetime.datetime.strptime(release_date, "%Y%m%d").date()
            self.add(Set(abbrev=abbrev, full_name=full_name, release_date=release_date))

    def add(self, set_: Set) -> None:
        self[set_.abbrev] = set_
        self[set_.name] = set_

    def i18n_set(self, set_: Set) -> None:
        self[set_.abbrev].i18n_set()


class _Ruling:
    def __init__(self):
        self.cards = []
        self.text = ""
        self.links = {}


class _RulingReader:
    def __init__(self, links):
        self.links = links

    def _get_link(self, text: str) -> Generator[Tuple[str, str], None, None]:
        references = re.findall(r"\[[a-zA-Z]+\s[0-9-]+\]", text)
        if not references:
            warnings.warn(f"no reference in ruling: {text}")
        for reference in references:
            yield reference, self.links[reference[1:-1]]

    def _from_krcg(self, data: Union[dict, list]) -> None:
        if isinstance(data, dict):
            for card, rulings in data.items():
                ret = _Ruling()
                ret.cards = [_RulingReader._card_id_name(card)]
                for ruling in rulings:
                    ret.text = ruling
                    ret.links = dict(self._get_link(ret.text))
                yield ret
        elif isinstance(data, list):
            for ruling in data:
                ret = _Ruling()
                ret.cards = [
                    _RulingReader._card_id_name(card) for card in ruling["cards"]
                ]
                ret.text = ruling["ruling"]
                ret.links = dict(self._get_link(ret.text))
                yield ret

    def _add_to_card(card, ruling):
        card.rulings.append(ruling)

    @staticmethod
    def _card_id_name(text: str) -> Tuple[int, str]:
        card_id, card_name = text.split("|")
        card_id = int(card_id)
        return card_id, card_name
