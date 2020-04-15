"""This module provides the `VTES` singleton: the VTES cards library.

If it has not been initialized, VTES will evaluate to False.
VTES must be configured with `VTES.configure()` before being used.
"""
import csv
import functools
import difflib
import io
import itertools
import logging
import pickle
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


class _VTES(dict):
    """VTES cards database that matches incomplete or misspelled card names.

    Keys are lower case card names and card Ids.
    Contains both crypt and library cards in a single dict.
    """

    def _yaml_get_card(self, text):
        """Get a card from a YAML card reference (id|Name)
        """
        card_id, card_name = text.split("|")
        card_id = int(card_id)
        if self.get_name(self[card_id]) != card_name:
            warnings.warn(
                f"rulings: {card_id} listed as {card_name} "
                f"instead of {self.get_name(self[card_id])}"
            )
        return self[card_id]

    def load_from_vekn(self, save=True):
        """Load the card database from vekn.net, with rulings

        Args:
            save (bool) : If True, card list is pickled to be retrieved faster later on.
        """
        self.clear()
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
        links = yaml.safe_load(open(config.RULINGS_LINK_FILE, "r"))
        cards_rulings = yaml.safe_load(open(config.CARDS_RULINGS_FILE, "r"))
        general_rulings = yaml.safe_load(open(config.GENERAL_RULINGS_FILE, "r"))
        for card, rulings in cards_rulings.items():
            card = self._yaml_get_card(card)
            card.setdefault("Rulings", []).extend(rulings)
            card.setdefault("Rulings Links", [])
            for i, ruling in enumerate(rulings):
                for reference, link in _get_runling_links(links, ruling):
                    card.setdefault("Rulings Links", []).append(
                        {"Reference": reference, "URL": link}
                    )
        for ruling in general_rulings:
            for card in ruling["cards"]:
                card = self._yaml_get_card(card)
                card.setdefault("Rulings", []).append(ruling["ruling"])
                card.setdefault("Rulings Links", [])
                for reference, link in _get_runling_links(links, ruling["ruling"]):
                    card.setdefault("Rulings Links", []).append(
                        {"Reference": reference, "URL": link}
                    )
        pickle.dump(self, open(config.VTES_FILE, "wb"))

    def __getitem__(self, key):
        """Get a card, try to find a good matching.

        It uses lowercase only, plus config.REMAP for common errors and abbreviations.
        It also uses difflib to match incomplete or misspelled names

        Args:
            key (str): the card to search for
        """
        if isinstance(key, str):
            key = key.lower()
        try:
            return super().__getitem__(key)
        except KeyError:
            # REMAP must match exactly
            if key in config.REMAP:
                return self[config.REMAP[key]]
            match = self._fuzzy_match(key)
            if match:
                return self[match]
            raise

    def __contains__(self, key):
        """Also use config.REMAP and difflib on "in" tests
        """
        if isinstance(key, str):
            key = key.lower()
        return (
            super().__contains__(key) or key in config.REMAP or self._fuzzy_match(key)
        )

    def __setitem__(self, key, value):
        return super().__setitem__(key.lower() if isinstance(key, str) else key, value)

    def __delitem__(self, key, value):
        return super().__setitem__(key.lower() if isinstance(key, str) else key, value)

    def configure(self):
        """Add alternative names for some cards
        """
        # we difflib match on AKA but not on REMAP
        # some items on REMAP are too short and match too many things.
        for alternative, card in config.AKA.items():
            self[alternative] = self[card]

    def __hash__(self):
        return id(self)

    @functools.lru_cache()
    def all_card_names_variants(self):
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

    @staticmethod
    def get_name_variants(card):
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
                if len(alternative) > 6:
                    yield from name_variants(alternative)

        yield from name_variants(card["Name"])
        # multiple aliases are separated by semicolumn
        for alias in card.get("Aka", "").split(";"):
            yield from name_variants(alias.strip())

    def load_csv(self, stream, save=True):
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
            self[int(card["Id"])] = card
            for name in self.get_name_variants(card):
                self[name] = card
            card["Name"] = self.get_name(card)

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
    VTES = pickle.load(open(config.VTES_FILE, "rb"))
except (FileNotFoundError, EOFError):
    VTES = _VTES()  # evaluates to False as it is empty
