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
            completion (dict): used for card name completion in web API and discord bot
            fuzzy_threshold (int): do not try to fuzzy match text shorter than this
            safe_variants (bool): do not use card name variants shorter than the
                                  fuzzy threshold (avoids errors when parsing the TWDA)
        """
        self.original_cards = {}
        self.rulings = {}
        self.cards = {}
        self.completion = collections.defaultdict(lambda: collections.defaultdict(int))
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

    def __delitem__(self, key, value):
        return self.cards.__setitem__(
            key.lower() if isinstance(key, str) else key, value
        )

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
            for e, part in enumerate(name.lower().split()):
                for i in range(1, len(part) + 1):
                    self.completion[part[:i]][self.get_name(card)] += (
                        # double score for matching name start
                        i
                        * (2 if e == 0 else 1)
                    )

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
        ret = None
        for part in partial_name.split():
            part_match = {}
            for match, score in self.completion.get(part.lower(), dict()).items():
                part_match[match] = max(part_match.get(match, 0), score)
            if ret:
                ret = collections.Counter(
                    {k: v + part_match[k] for k, v in ret.items() if k in part_match}
                )
            else:
                ret = collections.Counter(part_match)
        return [x[0] for x in sorted(ret.items(), key=lambda x: (-x[1], x[0]),)]

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
            logger.info("misspelled [{}] matched [{}]".format(name, match))
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

        def get_traits(traits):
            for trait_value in traits:
                if "&" in trait_value:
                    yield "Combo"
                else:
                    yield trait_value

        return set(
            itertools.chain.from_iterable(
                get_traits(card[trait]) for card in self.values() if card.get(trait)
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
                    d.strip() for d in card["Discipline"].split("/") if d.strip()
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
    def is_crypt(self, card):
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

    def is_disc(self, card, discipline):
        """A function to check if a card is of given discipline

        Handles multi-valued cards too (combo or outferior option).

        Args:
            card (str): card name
            discipline (str): a discipline name

        Returns:
            bool: true if the card is of the given discipline
        """
        if discipline in ["Combo", "combo"]:
            return any("&" in d for d in VTES[card].get("Discipline", []))
        return {discipline.strip().lower()} & {
            disc.strip().lower()
            for d in VTES[card].get("Discipline", [])
            for disc in d.split("&")
        }

    def no_disc(self, card):
        """A function to check if a card requires no discipline

        Args:
            card (str): card name

        Returns:
            bool: true if the card requires no discipline
        """
        return not VTES[card].get("Discipline", [])

    def is_type(self, card, type_):
        """A function to check if a card is of the given type

        Handles multiple types too (e.g. Modifier/Reaction)

        Args:
            card (str): card name
            type_ (str): a card type

        Returns:
            bool: true if the card has the given type
        """
        return {type_.strip().lower()} & {t.strip().lower() for t in VTES[card]["Type"]}

    def is_clan(self, card, clan):
        """A function to check if a card is of the given clan (or requires said clan)

        Handles multiple clans too (e.g. Gangrel/Gangrel Antitribu)

        Args:
            card (str): card name
            clan (str): a clan

        Returns:
            bool: true if the card is of the given clan.
        """
        return {clan.strip().lower()} & {t.strip().lower() for t in VTES[card]["Clan"]}

    def deck_to_txt(self, deck):
        """A consistent deck display matching our parsing rules of TWDA.html

        Cards are displayed in the order given by the config.TYPE_ORDER list.

        Args:
            deck (deck.Deck): A deck

        Returns:
            str: The normalized text version of the deck
        """

        def _type(card):
            return config.TYPE_ORDER.index("/".join(self[card[0]]["Type"]))

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
        lines.append("")
        if deck.score:
            lines.append(f"-- {deck.score}")
            lines.append("")
        if deck.name:
            lines.append(f"Deck Name: {deck.name}")
        if deck.author:
            lines.append(f"Created by: {deck.author}")
        if deck.comments:
            if any(len(line) > 100 for line in deck.comments.splitlines()):
                lines.extend(textwrap.wrap(deck.comments, 90))
            else:
                lines.append(deck.comments)
        lines.append("")
        lines.append(f"-- Crypt: ({deck.cards_count(self.is_crypt)} cards)")
        lines.append("---------------------------------------")
        for card, count in deck.cards(self.is_crypt):
            lines.append(
                "{:<2} {:<35} {:<2} {:<25} {}:{}".format(
                    count,
                    card + (" (ADV)" if self[card]["Adv"] else ""),
                    self[card]["Capacity"],
                    " ".join(self[card]["Disciplines"]),
                    self[card]["Clan"][0],
                    self[card]["Group"],
                )
            )
        lines.append(f"-- Library ({deck.cards_count(self.is_library)})")
        # sort by type, count (descending), name
        # note ordering must match the `itertools.groupby` function afterwards.
        library_cards = sorted(
            deck.cards(self.is_library), key=lambda a: (_type(a), -a[1], a[0])
        )
        # form a section for each type with a header displaying the total
        for kind, cards in itertools.groupby(library_cards, key=_type):
            c1, c2 = itertools.tee(cards)
            lines.append(
                f"-- {config.TYPE_ORDER[kind]} ({sum(count for card, count in c1)})"
            )
            for card, count in c2:
                if card in deck.cards_comments:
                    comment = deck.cards_comments[card].replace("\n", " ").strip()
                    lines.append(f"{count:<2} {card:<23} -- {comment}")
                else:
                    lines.append(f"{count:<2} {card}")
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
            return config.TYPE_ORDER.index("/".join(self[card[0]]["Type"]))

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
