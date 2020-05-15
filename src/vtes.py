"""This module provides the `VTES` singleton: the VTES cards library.

If it has not been initialized, VTES will evaluate to False.
VTES must be configured with `VTES.configure()` before being used.
"""
import collections
import copy
import csv
import functools
import difflib
import io
import itertools
import logging
import os
import pickle
import pkg_resources
import re
import requests
import tempfile
import textwrap
import warnings
import zipfile

import unidecode
import yaml

from . import config

logger = logging.getLogger()


def _get_runling_links(links_dict, text):
    """Yield ruling references and links from a dict of links and a ruling text

    Args:
        links_dict (dict): {reference: url} of rulings
        text (str): A ruling with one or more ruling references like [ZZZ 20000101]
    """
    references = re.findall(r"\[[a-zA-Z]+\s[0-9-]+\]", text)
    if not references:
        warnings.warn(f"no reference in ruling: {text}")
    for reference in references:
        reference = reference[1:-1]
        yield reference, links_dict[reference]


class _Trie(collections.defaultdict):
    """A Trie structure for text search
    """

    def __init__(self):
        super().__init__(lambda: collections.defaultdict(int))

    def add(self, text, reference):
        """Add text to the Trie

        Args:
            text (str): The text to add.
            reference (any): The reference to return on a match
        """
        for e, part in enumerate(text.lower().split()):
            for i in range(1, len(part) + 1):
                self[part[:i]][reference] += (
                    # double score for matching name start
                    i
                    * (2 if e == 0 else 1)
                )

    def search(self, text):
        """Search text into the Trie

        The match is case-insensitive but otherwise exact.
        Matches on start of words score higher.

        Args:
            text (str): The text to search
        Returns:
            list: References ordered by score
        """
        ret = None
        for part in text.split():
            part_match = {}
            for match, score in self.get(part.lower(), dict()).items():
                part_match[match] = max(part_match.get(match, 0), score)
            if ret:
                ret = collections.Counter(
                    {k: v + part_match[k] for k, v in ret.items() if k in part_match}
                )
            else:
                ret = collections.Counter(part_match)
        return [x[0] for x in sorted(ret.items(), key=lambda x: (-x[1], x[0]),)]


class _VTES:
    """VTES cards database that matches incomplete or misspelled card names.

    Keys are lower case card names and card Ids.
    Contains both crypt and library cards in a single dict.
    """

    def __init__(self):
        """Initialize the cards map

        `original_cards` and `rulings` are filled when loading the instance
        (either by Pickling or using self.load_from_vekn()).
        Other attributes are set on self.configure() call.


        Attributes:
            original_cards (dict): dict of original {id: card}
            rulings (dict): dict of {
                id: {
                    "Rulings": [ruling],
                    "Rulings Links": {
                        "Reference": "XXX YYYMMDD"
                        "URL": "http://www.example.com"
                    }
                }
            }
            cards (dict): dict of {card_name: card}
            completion (_Trie): used for card name completion in web API and discord bot
            search (dict): used for structured card search (cf. web API)
            fuzzy_threshold (int): do not try to fuzzy match text shorter than this
            safe_variants (bool): do not use card name variants shorter than the
                                  fuzzy threshold (avoids errors when parsing the TWDA)
        """
        self.original_cards = {}
        self.rulings = {}
        self.cards = {}
        self.completion = _Trie()
        self.search = {}
        self.fuzzy_threshold = 6
        self.safe_variants = True

    def __getstate__(self):
        """For pickle serialization.
        """
        return {"cards": self.original_cards, "rulings": self.rulings}

    def __setstate__(self, state):
        """For pickle deserialization.
        """
        self.original_cards = state.get("cards")
        self.rulings = state.get("rulings")

    def __reduce__(self):
        """For pickle serialization.
        """
        return (_VTES, (), self.__getstate__())

    def __bool__(self):
        """Test for emptyness
        """
        return bool(self.original_cards)

    def _yaml_get_card(self, text):
        """Get a card from a YAML card reference (id|Name)

        This is used before self.configure() is called: self.cards is empty,
        self.original_cards is used.
        """
        card_id, card_name = text.split("|")
        card_id = int(card_id)
        card = self.original_cards[card_id]
        if self.get_name(card) != card_name:
            warnings.warn(
                f"rulings: {card_id} listed as {card_name} "
                f"instead of {self.get_name(card)}"
            )
        return card

    def load_from_vekn(self, save=True, safe_variants=True):
        """Load the card database from vekn.net, with rulings

        Args:
            save (bool): If True, card list is pickled to be retrieved faster later on.
            safe_variants (bool): If True, use more card name variants
                                  (unsafe for TWDA parsing)
        """
        self.original_cards.clear()
        self.rulings.clear()
        r = requests.request("GET", config.VEKN_VTES_URL)
        r.raise_for_status()
        with tempfile.NamedTemporaryFile("wb", suffix=".zip") as f:
            f.write(r.content)
            f.flush()
            z = zipfile.ZipFile(f.name)
            with z.open(config.VEKN_VTES_LIBRARY_FILENAME) as c:
                self.load_csv(io.TextIOWrapper(c, encoding="utf_8_sig"), save)
            with z.open(config.VEKN_VTES_CRYPT_FILENAME) as c:
                self.load_csv(io.TextIOWrapper(c, encoding="utf_8_sig"), save)
        # load rulings from local yaml files
        links = yaml.safe_load(
            pkg_resources.resource_string("rulings", "rulings-links.yaml")
        )
        cards_rulings = yaml.safe_load(
            pkg_resources.resource_string("rulings", "cards-rulings.yaml")
        )
        general_rulings = yaml.safe_load(
            pkg_resources.resource_string("rulings", "general-rulings.yaml")
        )
        for card, rulings in cards_rulings.items():
            card_name = self.get_name(self._yaml_get_card(card))
            self.rulings.setdefault(card_name, {"Rulings": [], "Rulings Links": []})
            self.rulings[card_name]["Rulings"].extend(rulings)
            self.rulings[card_name]["Rulings Links"].extend(
                {"Reference": reference, "URL": link}
                for ruling in rulings
                for reference, link in _get_runling_links(links, ruling)
            )
        for ruling in general_rulings:
            for card in ruling["cards"]:
                card_name = self.get_name(self._yaml_get_card(card))
                self.rulings.setdefault(card_name, {"Rulings": [], "Rulings Links": []})
                self.rulings[card_name]["Rulings"].append(ruling["ruling"])
                self.rulings[card_name]["Rulings Links"].extend(
                    {"Reference": reference, "URL": link}
                    for reference, link in _get_runling_links(links, ruling["ruling"])
                )
        pickle.dump(self, open(config.VTES_FILE, "wb"))

    def __getitem__(self, key):
        """Get a card, try to find a good matching.

        It uses lowercase only, plus config.REMAP for common errors and abbreviations.
        It also uses difflib to fuzzy match incomplete or misspelled names

        Args:
            key (str): the card to search for
        """
        if isinstance(key, str):
            key = key.lower()
        try:
            return self.cards.__getitem__(key)
        except KeyError:
            # REMAP must match exactly
            if key in config.REMAP:
                return self.cards[config.REMAP[key].lower()]
            match = self._fuzzy_match(key)
            if match:
                return self.cards[match]
            raise

    def __contains__(self, key):
        # Must have the same logic than self.__getitem__(): self.cards, REMAP, _fuzzy
        if isinstance(key, str):
            key = key.lower()
        return (
            self.cards.__contains__(key)
            or key in config.REMAP
            or self._fuzzy_match(key)
        )

    def __setitem__(self, key, value):
        return self.cards.__setitem__(
            key.lower() if isinstance(key, str) else key, value
        )

    def __delitem__(self, key):
        return self.cards.__delitem__(key.lower() if isinstance(key, str) else key)

    def items(self):
        return self.cards.items()

    def keys(self):
        return self.cards.keys()

    def values(self):
        return self.cards.values()

    def configure(self, fuzzy_threshold=6, safe_variants=True):
        """Add alternative names for cards, set up completion

        Args:
            fuzzy_match (int): min text length to try fuzzy matching on.
        """
        self.cards.clear()
        self.completion.clear()
        self.fuzzy_threshold = fuzzy_threshold
        self.safe_variants = safe_variants
        # fill self.cards dict with all card names variants (including card ID)
        for card_id, card in self.original_cards.items():
            self[card_id] = card
            for name in self.get_name_variants(card, safe_variants):
                self[name] = card
        # we difflib match on AKA but not on REMAP
        # some items on REMAP are too short and match too many things.
        for alternative, card in config.AKA.items():
            self[alternative] = self[card]
        # build the completion trie for card names
        for name, card in self.cards.items():
            if isinstance(name, int):
                continue
            self.completion.add(name, self.get_name(card))
        # build the cards map for structured search
        # text is a completion trie, other dicts just contain a set of the cards IDs
        self.search = {
            "text": _Trie(),
            "type": collections.defaultdict(set),
            "clan": collections.defaultdict(set),
            "trait": collections.defaultdict(set),
            "group": collections.defaultdict(set),
            "capacity": collections.defaultdict(set),
            "discipline": collections.defaultdict(set),
            "votes": set(),
            "intercept": set(),
            "bleed": set(),
            "stealth": set(),
        }
        for card in self.original_cards.values():
            self.add_card_to_search(card)
        # manual fixups
        card = self["Gwen Brand"]
        self.search["discipline"]["ANIMALISM"].add(card["Id"])
        self.search["discipline"]["AUSPEX"].add(card["Id"])
        self.search["discipline"]["CHIMERSTRY"].add(card["Id"])
        self.search["discipline"]["FORTITUDE"].add(card["Id"])

    def add_card_to_search(self, card):
        """Add a card to self.search

        The card["Id"] is added to all matching sets.

        Args:
            card (dict): A card dict
        """
        self.search["text"].add(card["Card Text"], card["Id"])
        for type_ in card["Type"]:
            self.search["type"][type_.lower()].add(card["Id"])
        if set(card["Type"]) & {"Vampire", "Imbued"}:
            self.search["type"]["crypt"].add(card["Id"])
            if re.search(r"^(\[MERGED\] )?Sabbat", card["Card Text"]):
                self.search["trait"]["sabbat"].add(card["Id"])
            if re.search(r"^(\[MERGED\] )?Camarilla", card["Card Text"]):
                self.search["trait"]["camarilla"].add(card["Id"])
            if re.search(r"^(\[MERGED\] )?Laibon", card["Card Text"]):
                self.search["trait"]["laibon"].add(card["Id"])
            if re.search(r"^(\[MERGED\] )?Anarch", card["Card Text"]):
                self.search["trait"]["anarch"].add(card["Id"])
            if re.search(r"^(\[MERGED\] )?Independent", card["Card Text"]):
                self.search["trait"]["independent"].add(card["Id"])
        else:
            self.search["type"]["library"].add(card["Id"])
        if card.get("Clan"):
            for clan in card.get("Clan", []):
                self.search["clan"][clan.lower()].add(card["Id"])
        else:
            self.search["clan"]["none"].add(card["Id"])
        if card.get("Sect"):
            self.search["trait"][card["Sect"].lower()].add(card["Id"])
        if card.get("Title"):
            self.search["trait"][card["Title"].lower()].add(card["Id"])
        if card.get("Group"):
            self.search["group"][card["Group"].lower()].add(card["Id"])
            if card["Group"].lower() == "any":
                for i in range(1, 7):
                    self.search["group"][str(i)].add(card["Id"])
        if card.get("Capacity"):
            capacity = card["Capacity"].lower()
            if len(card["Capacity"]) > 2:
                capacity = "+1"
            self.search["capacity"][capacity].add(card["Id"])
        if re.search(r"(\d|X)\s+(v|V)ote", card["Card Text"]):
            self.search["votes"].add(card["Id"])
        if re.search(r"\+(\d|X)\s+(b|B)leed", card["Card Text"]):
            self.search["bleed"].add(card["Id"])
        if re.search(r"\+(\d|X)\s+(i|I)ntercept", card["Card Text"]):
            self.search["intercept"].add(card["Id"])
        if re.search(
            r"\+(\d|X)\s+(s|S)tealth (?!Ⓓ|action|political)", card["Card Text"]
        ):
            self.search["stealth"].add(card["Id"])
        if not set(card["Type"]) & {"Master", "Vampire", "Imbued"}:
            if re.search(r"-(\d|X)\s+(s|S)tealth", card["Card Text"]):
                self.search["intercept"].add(card["Id"])
            if re.search(r"-(\d|X)\s+(i|I)ntercept", card["Card Text"]):
                self.search["stealth"].add(card["Id"])
        if re.search(r"stealth .* to 0", card["Card Text"]):
            self.search["intercept"].add(card["Id"])
        if re.search(r"attempt fails", card["Card Text"]):
            self.search["stealth"].add(card["Id"])
        for discipline in card.get("Discipline", []):
            self.search["discipline"][discipline.lower()].add(card["Id"])
        # add vampires with superior disciplines to both inf and sup sets
        for discipline in card.get("Disciplines", []):
            # Visceratika and Vision have the same trigram
            if discipline.lower() == "vis" and "Imbued" in card["Type"]:
                discipline = "vin"
            self.search["discipline"][config.DIS_MAP[discipline.lower()]].add(
                card["Id"]
            )
            if discipline in config.DIS_MAP:
                self.search["discipline"][config.DIS_MAP[discipline]].add(card["Id"])
        if not card.get("Disciplines") and not card.get("Discipline"):
            self.search["discipline"]["none"].add(card["Id"])
        if len(card.get("Discipline", [])) > 1:
            self.search["discipline"]["*"].add(card["Id"])
        city = re.search(
            r"(?:Prince|Baron|Archbishop) of ((?:[A-Z][A-Za-z\s-]{3,})+)",
            card["Card Text"],
        )
        if city:
            city = city.group(1).lower()
            if city[-5:] == "as a ":
                city = city[:-5]
            if city == "washington":
                city = "washington, d.c."
            self.search["trait"][city].add(card["Id"])
        if re.search(r"Requires a( ready)? titled (S|s)abbat", card["Card Text"]):
            self.search["trait"]["bishop"].add(card["Id"])
            self.search["trait"]["archbishop"].add(card["Id"])
            self.search["trait"]["cardinal"].add(card["Id"])
            self.search["trait"]["regent"].add(card["Id"])
            self.search["trait"]["priscus"].add(card["Id"])
            self.search["trait"]["sabbat"].add(card["Id"])
        if re.search(r"Requires a( ready)? titled (C|c)amarilla", card["Card Text"]):
            self.search["trait"]["primogen"].add(card["Id"])
            self.search["trait"]["prince"].add(card["Id"])
            self.search["trait"]["justicar"].add(card["Id"])
            self.search["trait"]["inner circle"].add(card["Id"])
            self.search["trait"]["imperator"].add(card["Id"])
            self.search["trait"]["camarilla"].add(card["Id"])
        if re.search(r"Requires a( ready)? titled vampire", card["Card Text"]):
            self.search["trait"]["primogen"].add(card["Id"])
            self.search["trait"]["prince"].add(card["Id"])
            self.search["trait"]["justicar"].add(card["Id"])
            self.search["trait"]["inner circle"].add(card["Id"])
            self.search["trait"]["imperator"].add(card["Id"])
            self.search["trait"]["bishop"].add(card["Id"])
            self.search["trait"]["archbishop"].add(card["Id"])
            self.search["trait"]["cardinal"].add(card["Id"])
            self.search["trait"]["regent"].add(card["Id"])
            self.search["trait"]["priscus"].add(card["Id"])
            self.search["trait"]["baron"].add(card["Id"])
            self.search["trait"]["liaison"].add(card["Id"])
            self.search["trait"]["magaji"].add(card["Id"])
            self.search["trait"]["kholo"].add(card["Id"])
        if re.search(r"Requires a( ready)? (M|m)agaji", card["Card Text"]):
            self.search["trait"]["magaji"].add(card["Id"])
            self.search["trait"]["laibon"].add(card["Id"])
        # consider sects as traits,
        # but do not match them just anywhere in the card text
        if re.search(r"Requires a( ready)? (S|s)abbat", card["Card Text"]):
            self.search["trait"]["sabbat"].add(card["Id"])
        if re.search(r"Requires a( ready)? (C|c)amarilla", card["Card Text"]):
            self.search["trait"]["camarilla"].add(card["Id"])
        if re.search(r"Requires a( ready)? (L|l)aibon", card["Card Text"]):
            self.search["trait"]["laibon"].add(card["Id"])
        if re.search(
            r"Requires a( ready|n)( (I|i)ndependent or)? (A|a)narch", card["Card Text"],
        ):
            self.search["trait"]["anarch"].add(card["Id"])
        if re.search(r"Requires an (I|i)ndependent", card["Card Text"]):
            self.search["trait"]["independent"].add(card["Id"])
        for trait in re.findall(
            f"({'|'.join(config.TRAITS)})", card["Card Text"].lower()
        ):
            self.search["trait"][trait].add(card["Id"])
            if trait in {"primogen", "prince", "justicar", "inner circle", "imperator"}:
                self.search["trait"]["camarilla"].add(card["Id"])
            if trait in {"bishop", "archbishop", "cardinal", "regent", "priscus"}:
                self.search["trait"]["sabbat"].add(card["Id"])
            if trait in {"baron"}:
                self.search["trait"]["anarch"].add(card["Id"])
            if trait in {"magaji", "kholo"}:
                self.search["trait"]["laibon"].add(card["Id"])
        if "[FLIGHT]" in card["Card Text"]:
            self.search["discipline"]["flight"].add(card["Id"])

    def complete(self, partial_name):
        """Card name completion.

        It uses a very basic Trie to match trigrams.
        Matches on the start of the name are returned first,
        other matches are returned alphabetically.

        Args:
            partial_name (str): Parts of the name (can contain spaces)

        Returns:
            (list): A sorted list of results, from most likely to less likely
        """
        return self.completion.search(partial_name)

    @functools.lru_cache()
    def all_card_names_variants(self):
        """Return all cards names.

        Used by self._fuzzy_match(), it uses a cache to accelerate matching.

        Returns:
            (list): All cards name and variants in no specific order
        """
        return [k for k in self.keys() if isinstance(k, str)]

    @functools.lru_cache()
    def _fuzzy_match(self, name):
        """Use difflib to match incomplete or misspelled names

        It uses a cache to accelerate matching of common misspellings.

        Args:
            name (str): the card name

        Returns:
            The matched card name, or None
        """
        if not isinstance(name, str):
            return
        if len(name) < self.fuzzy_threshold:
            return
        # 0.8 is an empirical value, seems to work nicely
        result = difflib.get_close_matches(
            name, self.all_card_names_variants(), n=1, cutoff=0.8
        )
        if result:
            match = result[0]
            logger.debug("misspelled [{}] matched [{}]".format(name, match))
            return match

    def trait_choices(self, trait):
        """Get all registered values for a given card trait.

        Available traits:
        - Adv
        - Aka
        - Artist
        - Banned
        - Blood Cost
        - Burn Option
        - Capacity
        - Card Text
        - Clan
        - Conviction Cost
        - Discipline (Library card)
        - Disciplines (Crypt card)
        - Draft
        - Flavor Text
        - Group
        - Id
        - Name
        - Pool Cost
        - Requirement
        - Set
        - Title
        - Type

        Empty values are removed.

        Args:
            trait (str): The trait to get choices for.

        Yields:
            All possible values
        """
        return set(
            itertools.chain.from_iterable(
                card[trait] for card in self.values() if card.get(trait)
            )
        )

    @property
    def disciplines(self):
        """Return a list of disciplines
        """
        return sorted(self.trait_choices("Discipline"))

    @property
    def types(self):
        """Return a list of card types
        """
        return sorted(self.trait_choices("Type"))

    @property
    def clans(self):
        """Return a list of clans
        """
        return sorted(self.trait_choices("Clan"))

    @staticmethod
    def get_name(card):
        """Returns main name for a card
        """
        name = card["Name"]
        if name[-5:] == ", The":
            name = "The " + name[:-5]
        if name[-6:] != " (ADV)" and card.get("Adv"):
            name = name + " (ADV)"
        return name

    @staticmethod
    def vekn_name(card):
        """Returns VEKN style name for a card (suffix The)
        """
        name = card["Name"]
        if name[:4] == "The ":
            name = name[4:] + ", The"
        if name[-6:] != " (ADV)" and card.get("Adv"):
            name = name + " (ADV)"
        return name

    def normalized(self, card):
        """Fix the card name
        """
        data = copy.copy(card)
        name = self.get_name(card)
        data["Name"] = name
        data.update(self.rulings.get(name, {}))
        return data

    @staticmethod
    def get_name_variants(card, safe=True):
        """Yields all name variants for a card

        Add the " (ADV)" suffix for advanced vampires
        Yield an ASCII variant for non-ASCII names
        Yield a straightforward name for deported article:
            "Second Tradition, The" -> "The Second Tradition"
        Yield a shorten version for comma names:
            "Akhenaten, The Sun Pharaoh" -> "Akhenaten"
        Apply all of the above for official "Aka" variants

        Important examples are in test.

        Args:
            card (dict): the card
            safe (bool): if True, yield more variants (unsafe for TWDA parsing)

        Yields:
            str: all name variants
        """
        advanced_suffix = " (ADV)" if card.get("Adv") else ""

        def name_variants(name):
            if not name:
                return
            yield name + advanced_suffix
            ascii_variant = unidecode.unidecode(name)
            if ascii_variant != name:
                yield ascii_variant + advanced_suffix
            if name[-5:] == ", The":
                yield from name_variants("The " + name[:-5])
            # suffix removal
            # --------------
            # Note the following code also removes the ", The" particle.
            # Calling it multiple times can get all particles removed,
            # eg. "Rumor Mill, Tabloid Newspaper, The" will yield:
            # - "Rumor Mill, Tabloid Newspaper"
            # - "Rumor Mill"
            #
            # ':' can not be seen as a suffix marker,
            # because we would miss with "Praxis Seizure:" and "Crusade:" cards.
            # Too bad, because we would like to get the "Second tradition:" variants.
            # Henceforth, these variants are handled manually in config.REMAP.
            if "," in name:
                alternative = name.rsplit(",", 1)[0]
                # We do not shorten too much or anything will fuzzy match
                # eg. "Line" (without ", The") could mismatch "Redline" or "Zip Line".
                # Still, "Gunther" should match "Gunther, Beast Lord'
                if not safe or len(alternative) > 6:
                    yield from name_variants(alternative)

        yield from name_variants(card["Name"])
        # multiple aliases are separated by semicolumn
        for alias in card.get("Aka", "").split(";"):
            yield from name_variants(alias.strip())

    def load_csv(self, stream, save=True, safe_variants=True):
        """Load a crypt or library CSV (VEKN format)

        The VTES card list is pickled for future use.
        """
        for card in csv.DictReader(stream):
            card["Set"] = [s.strip() for s in card["Set"].split(",") if s.strip()]
            card["Clan"] = [c.strip() for c in card["Clan"].split("/") if c.strip()]
            card["Type"] = [t.strip() for t in card["Type"].split("/") if t.strip()]
            card["Card Text"] = card["Card Text"].replace("{", "")
            card["Card Text"] = card["Card Text"].replace("}", "")
            card["Card Text"] = card["Card Text"].replace("(D)", "Ⓓ ")
            if "Disciplines" in card:
                card["Disciplines"] = [
                    d.strip() for d in card["Disciplines"].split(" ") if d.strip()
                ]
            if "Requirement" in card:
                card["Requirement"] = [
                    r.strip() for r in card["Requirement"].split(",") if r.strip()
                ]
            if "Discipline" in card:
                card["Discipline"] = [
                    d.strip()
                    for p in card["Discipline"].split("/")
                    for d in p.split("&")
                    if d.strip()
                ]
            if "Burn Option" in card:
                card["Burn Option"] = bool(card["Burn Option"])
            if "Adv" in card:
                card["Adv"] = bool(card["Adv"])
            self.original_cards[int(card["Id"])] = card
        # pickle this
        if save:
            pickle.dump(self, open(config.VTES_FILE, "wb"))

    # usual traits selectors
    @staticmethod
    def is_crypt(card):
        """A function to check if a card is a crypt card

        Args:
            card (str): card name

        Returns:
            bool: true if the card is a crypt card
        """
        return set(VTES[card]["Type"]) & {"Vampire", "Imbued"}

    def is_library(self, card):
        """A function to check if a card is a library card

        Args:
            card (str): card name

        Returns:
            bool: true if the card is a library card
        """
        return not self.is_crypt(card)

    @staticmethod
    def is_disc(card, discipline):
        """A function to check if a card is of given discipline

        Handles multi-valued cards too (combo or outferior option).

        Args:
            card (str): card name
            discipline (str): a discipline name

        Returns:
            bool: true if the card is of the given discipline
        """
        return {discipline.strip().lower()} & {
            d.strip().lower() for d in VTES[card].get("Discipline", [])
        }

    @staticmethod
    def no_disc(card):
        """A function to check if a card requires no discipline

        Args:
            card (str): card name

        Returns:
            bool: true if the card requires no discipline
        """
        return not VTES[card].get("Discipline", [])

    @staticmethod
    def is_type(card, type_):
        """A function to check if a card is of the given type

        Handles multiple types too (e.g. Modifier/Reaction)

        Args:
            card (str): card name
            type_ (str): a card type

        Returns:
            bool: true if the card has the given type
        """
        return {type_.strip().lower()} & {t.strip().lower() for t in VTES[card]["Type"]}

    @staticmethod
    def is_clan(card, clan):
        """A function to check if a card is of the given clan (or requires said clan)

        Handles multiple clans too (e.g. Gangrel/Gangrel Antitribu)

        Args:
            card (str): card name
            clan (str): a clan

        Returns:
            bool: true if the card is of the given clan.
        """
        return {clan.strip().lower()} & {t.strip().lower() for t in VTES[card]["Clan"]}

    def deck_to_txt(self, deck, wrap=True):
        """A consistent deck display matching our parsing rules of TWDA.html

        Cards are displayed in the order given by the config.TYPE_ORDER list.

        Args:
            deck (deck.Deck): A deck

        Returns:
            str: The normalized text version of the deck
        """

        def _type(card):
            return config.TYPE_ORDER.index("/".join(sorted(self[card[0]]["Type"])))

        lines = []
        if deck.event:
            lines.append(deck.event)
        if deck.place:
            lines.append(deck.place)
        if deck.date:
            lines.append(deck.date.format("MMMM Do YYYY"))
        if deck.tournament_format:
            lines.append(deck.tournament_format)
        if deck.players_count:
            lines.append(f"{deck.players_count} players")
        if deck.player:
            lines.append(deck.player)
        if deck.event_link:
            lines.append(deck.event_link)
        lines.append("")
        if deck.score:
            lines.append(f"-- {deck.score}")
            lines.append("")
        if deck.name:
            lines.append(f"Deck Name: {deck.name}")
        if deck.author:
            lines.append(f"Created by: {deck.author}")
        if deck.comments:
            if deck.name or deck.author:
                lines.append("")
            if wrap and any(len(line) > 100 for line in deck.comments.splitlines()):
                lines.extend(textwrap.wrap(deck.comments, 90))
            else:
                lines.append(deck.comments)
        elif lines[-1] != "":
            lines.append("")
        cap = sorted(
            itertools.chain.from_iterable(
                [int(self[card]["Capacity"])] * count
                for card, count in deck.cards(self.is_crypt)
            )
        )
        cap_min = sum(cap[:4])
        cap_max = sum(cap[-4:])
        cap_avg = sum(cap) / len(cap)
        lines.append(
            f"Crypt ({deck.cards_count(self.is_crypt)} cards, "
            f"min={cap_min}, max={cap_max}, avg={cap_avg:.3g})"
        )
        lines.append("-" * len(lines[-1]))
        max_name = (
            max(
                len(self.vekn_name(self[card]))
                for card, _count in deck.cards(self.is_crypt)
            )
            + 1
        )
        max_disc = (
            max(
                len(" ".join(self[card]["Disciplines"]))
                for card, _count in deck.cards(self.is_crypt)
            )
            + 1
        )
        max_title = (
            max(
                len(self[card].get("Title", ""))
                for card, _count in deck.cards(self.is_crypt)
            )
            + 1
        )
        for card, count in deck.cards(self.is_crypt):
            lines.append(
                f"{{}}x {{:<{max_name}}} {{:>2}} {{:<{max_disc}}} "
                f"{{:<{max_title}}} {{}}:{{}}".format(
                    count,
                    self.vekn_name(self[card]),
                    self[card]["Capacity"],
                    " ".join(self[card]["Disciplines"]),
                    self[card].get("Title", ""),
                    self[card]["Clan"][0],
                    self[card]["Group"],
                )
            )
        lines.append(f"\nLibrary ({deck.cards_count(self.is_library)} cards)")
        # sort by type, name
        # note ordering must match the `itertools.groupby` function afterwards.
        library_cards = sorted(
            deck.cards(self.is_library),
            key=lambda a: (_type(a), self.vekn_name(self[a[0]])),
        )
        # form a section for each type with a header displaying the total
        for i, (kind, cards) in enumerate(itertools.groupby(library_cards, key=_type)):
            cards = list(cards)
            trifle_count = ""
            if kind == 0:
                trifle_count = sum(
                    count
                    for card, count in cards
                    if re.search(r"(t|T)rifle", self[card]["Card Text"])
                )
                if trifle_count:
                    trifle_count = f"; {trifle_count} trifle"
                else:
                    trifle_count = ""
            cr = "\n" if i > 0 else ""
            lines.append(
                f"{cr}{config.TYPE_ORDER[kind]} "
                f"({sum(count for card, count in cards)}{trifle_count})"
            )
            for card, count in cards:
                if card in deck.cards_comments:
                    comment = deck.cards_comments[card].replace("\n", " ").strip()
                    lines.append(
                        f"{count}x {self.vekn_name(self[card]):<23} -- {comment}"
                    )
                else:
                    lines.append(f"{count}x {self.vekn_name(self[card])}")
        return "\n".join(lines)

    def deck_to_dict(self, deck, twda_id):
        """A consistent deck serialization for the API

        Cards are listed in the order given by the config.TYPE_ORDER list.

        Args:
            deck (deck.Deck): A deck
            twda_id (str): The deck TWDA ID

        Returns:
            dict: The serialized deck
        """
        ret = {
            "twda_id": twda_id,
            "event": deck.event,
            "place": deck.place,
            "date": deck.date.date().isoformat(),
            "tournament_format": deck.tournament_format,
            "players_count": deck.players_count,
            "player": deck.player,
            "score": deck.score,
            "name": deck.name,
            "author": deck.author,
            "comments": deck.comments,
            "crypt": {
                "count": deck.cards_count(self.is_crypt),
                "cards": [
                    {
                        "id": self[card]["Id"],
                        "count": count,
                        "name": card,
                        "comments": deck.cards_comments.get(card),
                    }
                    for card, count in deck.cards(self.is_crypt)
                ],
            },
            "library": {"count": deck.cards_count(self.is_library), "cards": []},
        }

        def _type(card):
            return config.TYPE_ORDER.index("/".join(sorted(self[card[0]]["Type"])))

        # sort by type, count (descending), name
        # note ordering must match the `itertools.groupby` function afterwards.
        library_cards = sorted(
            deck.cards(self.is_library), key=lambda a: (_type(a), -a[1], a[0])
        )
        # form a section for each type with a header displaying the total
        for kind, cards in itertools.groupby(library_cards, key=_type):
            c1, c2 = itertools.tee(cards)
            ret["library"]["cards"].append(
                {
                    "type": config.TYPE_ORDER[kind],
                    "count": sum(count for card, count in c1),
                    "cards": [],
                }
            )
            for card, count in c2:
                ret["library"]["cards"][-1]["cards"].append(
                    {
                        "id": self[card]["Id"],
                        "count": count,
                        "name": card,
                        "comments": deck.cards_comments.get(card),
                    }
                )
        return ret


try:
    if not os.path.exists(config.VTES_FILE) or os.stat(config.VTES_FILE).st_size == 0:
        raise FileNotFoundError(config.VTES_FILE)
    VTES = pickle.load(open(config.VTES_FILE, "rb"))
except (FileNotFoundError, EOFError):
    VTES = _VTES()  # evaluates to False as it is empty
