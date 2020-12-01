"""This module provides the `VTES` singleton: the VTES cards library.

If it has not been initialized, VTES will evaluate to False.
VTES must be configured with `VTES.configure()` before being used.
"""
from typing import Generator, List, Mapping, TextIO, Tuple, Union
import collections
import copy
import csv
import io
import itertools
import os
import pickle
import pkg_resources
import re
import requests
import tempfile
import typing
import warnings
import zipfile

import unidecode
import yaml

from . import config
from . import logging
from . import utils


StringGenerator = Generator[str, None, None]

logger = logging.logger


class _RulingsLinks(dict):
    def get_links(self, text: str) -> Generator[Tuple[str, str], None, None]:
        """Yield ruling references and links from a dict of links and a ruling text.

        Args:
            text: A ruling with one or more ruling references like [ZZZ 20000101].

        Yields:
            (reference, url) of the rulings contained in the text.
        """
        references = re.findall(r"\[[a-zA-Z]+\s[0-9-]+\]", text)
        if not references:
            warnings.warn(f"no reference in ruling: {text}")
        for reference in references:
            reference = reference[1:-1]
            yield reference, self[reference]


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
                        "Reference": "NNN YYYMMDD"
                        "URL": "http://www.example.com"
                    }
                }
            }
            cards (dict): dict of {card_name: card}
            completion (utils.Trie): used for card name completion
            search (dict): used for structured card search (cf. web API)
            fuzzy_threshold (int): do not try to fuzzy match text shorter than this
            safe_variants (bool): do not use card name variants shorter than the
                                  fuzzy threshold (avoids errors when parsing the TWDA)
        """
        self.original_cards = {}
        self.rulings = {}
        self.cards = utils.FuzzyDict(aliases=config.REMAP)
        self.completion = utils.Trie()
        self.search = {}
        self.fuzzy_threshold = 6
        self.safe_variants = True

    def __getstate__(self) -> dict:
        """For pickle serialization."""
        return {"cards": self.original_cards, "rulings": self.rulings}

    def __setstate__(self, state: typing.Mapping) -> None:
        """For pickle deserialization."""
        self.original_cards = state.get("cards")
        self.rulings = state.get("rulings")

    def __reduce__(self) -> tuple:
        """For pickle serialization."""
        return (_VTES, (), self.__getstate__())

    def __bool__(self) -> bool:
        """Test for emptyness"""
        return bool(self.original_cards)

    def __getitem__(self, key):
        return self.cards[key]

    def __contains__(self, key):
        return key in self.cards

    def __setitem__(self, key, value):
        self.cards[key] = value

    def __delitem__(self, key):
        del self.cards[key]

    def items(self):
        return self.cards.items()

    def keys(self):
        return self.cards.keys()

    def values(self):
        return self.cards.values()

    def _yaml_get_card(self, text: str) -> dict:
        """Get a card from a YAML card reference (id|Name)

        This is used before self.configure() is called: self.cards is empty,
        self.original_cards is used.

        Args:
            text: a YAML card refreence of the form "id|Name"
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

    def load_from_vekn(self, save: bool = True) -> None:
        """Load the card database from vekn.net, with rulings

        Args:
            save: If True, card list is pickled to be retrieved faster later on.
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
        links = _RulingsLinks(
            yaml.safe_load(
                pkg_resources.resource_string("rulings", "rulings-links.yaml")
            )
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
                for reference, link in links.get_links(ruling)
            )
        for ruling in general_rulings:
            for card in ruling["cards"]:
                card_name = self.get_name(self._yaml_get_card(card))
                self.rulings.setdefault(card_name, {"Rulings": [], "Rulings Links": []})
                self.rulings[card_name]["Rulings"].append(ruling["ruling"])
                self.rulings[card_name]["Rulings Links"].extend(
                    {"Reference": reference, "URL": link}
                    for reference, link in links.get_links(ruling["ruling"])
                )
        pickle.dump(self, open(config.VTES_FILE, "wb"))

    def configure(self, fuzzy_threshold: int = 6, safe_variants: bool = True) -> None:
        """Add alternative names for cards, set up completion

        Args:
            fuzzy_threshold: min text length to try fuzzy matching on.
            safe_variants: if False, more card name variants are used
                           (unsafe for TWDA parsing)
        """
        self.cards.clear()
        self.completion.clear()
        self.cards.threshold = fuzzy_threshold
        self.safe_variants = safe_variants
        # fill self.cards dict with all card names variants (including card ID)
        for card_id, card in self.original_cards.items():
            self[card_id] = card
            for name in self._get_name_variants(card, safe_variants):
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
            "text": utils.Trie(),
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
            self._add_card_to_search(card)
        # manual fixups
        for name, mods in config.SEARCH_EXCEPTIONS.items():
            for mod in mods:
                prefix = mod[0]
                key_path = mod[1:].split(":")
                try:
                    s = self.search
                    for key in key_path:
                        s = s[key]
                    if prefix == "+":
                        s.add(self[name]["Id"])
                    elif prefix == "-":
                        s.remove(self[name]["Id"])
                    else:
                        warnings.warn(f"{name} has an invalid prefix {prefix}")
                except KeyError:
                    warnings.warn(
                        f"{name} marked as exception for {key_path}, but is not listed."
                    )

    def _add_card_to_search(self, card: typing.Mapping) -> None:
        """Add a card to self.search

        The card["Id"] is added to all matching sets.
        What matches or not has a lot do to with players usage and are design decisions:
            - requiring a title is listed as matching the sect
            - removing stealth is considered as intercept
            - stealthed actions are not considered as stealth cards
            - making a block fail is considered stealth
            - MERGED text of an advanced is taken into account for sect and title
            - combo and anarch tri-discipline cards are all listed under "*"
            - Vision uses the "vin" trigtam to distinguish from "vis"ceratika
        Args:
            card: A card dict
        """
        self.search["text"].add(card["Card Text"], card["Id"])
        for type_ in card["Type"]:
            self.search["type"][type_.lower()].add(card["Id"])
        if set(card["Type"]) & {"Vampire", "Imbued"}:
            self.search["type"]["crypt"].add(card["Id"])
            # sect, including for MERGED versions
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
        # CSV-listed traits
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
        if card.get("Title"):
            self.search["votes"].add(card["Id"])
        if re.search(r"(\d|X)\s+(v|V)ote", card["Card Text"]):
            self.search["votes"].add(card["Id"])
        # bleed/stealth/intercept bonuses
        if re.search(r"\+(\d|X)\s+(b|B)leed", card["Card Text"]):
            self.search["bleed"].add(card["Id"])
        if re.search(r"\+(\d|X)\s+(i|I)ntercept", card["Card Text"]):
            self.search["intercept"].add(card["Id"])
        # do not include stealthed actions as stealth cards
        if re.search(
            r"\+(\d|X)\s+(s|S)tealth (?!Ⓓ|action|political)", card["Card Text"]
        ):
            self.search["stealth"].add(card["Id"])
        # stealth/intercept maluses count has bonus of the other (for library cards)
        # also list block denials as stealth
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
            # Visceratika and Vision have the same trigram, discriminate
            if discipline.lower() == "vis" and "Imbued" in card["Type"]:
                discipline = "vin"
            self.search["discipline"][config.DIS_MAP[discipline.lower()]].add(
                card["Id"]
            )
            if discipline in config.DIS_MAP:
                self.search["discipline"][config.DIS_MAP[discipline]].add(card["Id"])
        if not card.get("Disciplines") and not card.get("Discipline"):
            self.search["discipline"]["none"].add(card["Id"])
        # "Discipline" singular is a library-only key
        if len(card.get("Discipline", [])) > 1:
            self.search["discipline"]["*"].add(card["Id"])
        # FLIGHT is not listed as a discipline, treat it as such anyway
        if "[FLIGHT]" in card["Card Text"]:
            self.search["discipline"]["flight"].add(card["Id"])
        # city trait
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
            self.search["votes"].add(card["Id"])
        # add generic title requirements to all titles of the sect
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
        # this should match unnamed independant titles too, but we have no trait for it
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
            r"Requires a( ready|n)( (I|i)ndependent or)? (A|a)narch",
            card["Card Text"],
        ):
            self.search["trait"]["anarch"].add(card["Id"])
        if re.search(r"Requires an (I|i)ndependent", card["Card Text"]):
            self.search["trait"]["independent"].add(card["Id"])
        # match other traits anywhere in the text
        # add specific title requirements to the matching sect
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

    def complete(self, partial_name: str) -> List:
        """Card name completion.

        It uses a Trie to match trigrams.
        Matches on the start of the name are returned first,
        other matches are returned alphabetically.

        Args:
            partial_name: Parts of the name (can contain spaces)

        Returns:
            A sorted list of results, from most likely to less likely
        """
        return self.completion.search(partial_name)

    def trait_choices(self, trait: str) -> set:
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
            trait: The trait to get choices for.

        Returns:
            All possible values
        """
        return set(
            itertools.chain.from_iterable(
                card[trait] for card in self.values() if card.get(trait)
            )
        )

    @property
    def disciplines(self) -> list:
        """List of disciplines"""
        return sorted(self.trait_choices("Discipline"))

    @property
    def types(self) -> list:
        """List of card types"""
        return sorted(self.trait_choices("Type"))

    @property
    def clans(self) -> list:
        """List of clans"""
        return sorted(self.trait_choices("Clan"))

    def get_name(self, card: Union[str, Mapping]) -> str:
        """Returns official name for a card or card name."""
        if not isinstance(card, collections.abc.Mapping):
            card = self[card]
        name = card["Name"]
        if name[-5:] == ", The":
            name = "The " + name[:-5]
        if name[-6:] != " (ADV)" and card.get("Adv"):
            name = name + " (ADV)"
        name = name.replace("(TM)", "™")
        return name

    def vekn_name(self, card: Union[str, Mapping]) -> str:
        """Returns the VEKN name for a card (suffix The, (TM) instead of ™)."""
        if not isinstance(card, collections.abc.Mapping):
            card = self[card]
        name = card["Name"]
        if name[:4] == "The ":
            name = name[4:] + ", The"
        if name[-6:] != " (ADV)" and card.get("Adv"):
            name = name + " (ADV)"
        name = name.replace("™", "(TM)")
        return name

    def normalized(self, card: Union[str, Mapping]) -> Mapping:
        """Returns a JSON-serializable version of the card.

        It makes sure the name is the "standard" one (with (ADV) for advanced vampires)
        and adds a field with the card image URL and rulings.
        """
        if not isinstance(card, collections.abc.Mapping):
            card = self[card]
        data = copy.copy(card)
        name = self.get_name(card)
        data["Name"] = name
        file_name = utils.normalize(name)
        file_name = file_name[4:] + "the" if file_name[:4] == "the " else file_name
        file_name, _ = re.subn(r"""\s|,|\.|-|—|'|:|\(|\)|"|!""", "", file_name)
        data["Image"] = f"{config.IMAGES_ROOT}{file_name}.jpg"
        data.update(self.rulings.get(name, {}))
        return data

    @staticmethod
    def _get_name_variants(card: Mapping, safe: bool = True) -> StringGenerator:
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
            card: the card
            safe: if False, yield more variants (unsafe for TWDA parsing)

        Yields:
            All name variants
        """
        advanced_suffix = " (ADV)" if card.get("Adv") else ""

        def name_variants(name):
            if not name:
                return
            yield name + advanced_suffix
            if "(TM)" in name:
                yield name.replace("(TM)", "™") + advanced_suffix
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

    def load_csv(self, stream: TextIO, save: bool = True) -> None:
        """Load a crypt or library CSV (VEKN format)

        The VTES card list is pickled for future use.
        """
        for card in csv.DictReader(stream):
            if "Set" in card:
                card["Set"] = [s.strip() for s in card["Set"].split(",") if s.strip()]
            if "Clan" in card:
                card["Clan"] = [c.strip() for c in card["Clan"].split("/") if c.strip()]
            if "Type" in card:
                card["Type"] = [t.strip() for t in card["Type"].split("/") if t.strip()]
            if "Card Text" in card:
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
            card_id = int(card["Id"])
            if card_id not in self.original_cards:
                self.original_cards[card_id] = {}
            self.original_cards[int(card["Id"])].update(card)
        # pickle this
        if save:
            pickle.dump(self, open(config.VTES_FILE, "wb"))

    def is_crypt(self, card_name: str) -> bool:
        """A function to check if a card is a crypt card"""
        return set(self[card_name]["Type"]).issubset({"Vampire", "Imbued"})

    def is_library(self, card_name: str) -> bool:
        """A function to check if a card is a library card"""
        return not self.is_crypt(card_name)

    def is_disc(self, card_name: str, discipline: str) -> bool:
        """A function to check if a card is of given discipline

        Handles multi-valued cards too (combo or outferior option).
        """
        return utils.normalize(discipline) in {
            utils.normalize(d) for d in self[card_name].get("Discipline", [])
        }

    def no_disc(self, card_name: str) -> bool:
        """A function to check if a card requires no discipline"""
        return not self[card_name].get("Discipline", [])

    def is_type(self, card_name: str, type_: str) -> bool:
        """A function to check if a card is of the given type

        Handles multiple types too (e.g. Modifier/Reaction)
        """
        return utils.normalize(type_) in {
            utils.normalize(t) for t in self[card_name]["Type"]
        }

    def is_clan(self, card_name: str, clan: str) -> bool:
        """A function to check if a card is of the given clan (or requires said clan)

        Handles multiple clans too (e.g. Gangrel/Gangrel Antitribu)
        """
        return utils.normalize(clan) in {
            utils.normalize(c) for c in self[card_name]["Clan"]
        }

    def str_to_card_and_count(self, string: str) -> dict:
        string = string.lower()


try:
    if not os.path.exists(config.VTES_FILE) or os.stat(config.VTES_FILE).st_size == 0:
        raise FileNotFoundError(config.VTES_FILE)
    VTES = pickle.load(open(config.VTES_FILE, "rb"))
except (FileNotFoundError, EOFError):
    VTES = _VTES()  # evaluates to False as it is empty
