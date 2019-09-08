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
import requests
import tempfile
import zipfile

from . import config


logger = logging.getLogger()


class _VTES(dict):
    """VTES cards database that matches incomplete or misspelled card names.

    Keys are lower case card names.
    """

    def load_from_vekn(self):
        self.clear()
        r = requests.request("GET", config.VEKN_VTES_URL)
        with tempfile.NamedTemporaryFile("wb", suffix=".zip") as f:
            f.write(r.content)
            f.flush()
            z = zipfile.ZipFile(f.name)
            with z.open(config.VEKN_VTES_LIBRARY_FILENAME) as c:
                self.load_csv(io.TextIOWrapper(c, encoding="utf_8_sig"))
            with z.open(config.VEKN_VTES_CRYPT_FILENAME) as c:
                self.load_csv(io.TextIOWrapper(c, encoding="utf_8_sig"))

    def __getitem__(self, key):
        """Get a card, try to find a good matching.

        Use lowercase only, config.REMAP for common errors and abbreviations.
        Use difflib to match incomplete or misspelled names
        """
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
            try:
                while key:
                    key, _ = key.rsplit(maxsplit=1)
                    if key in self:
                        return self[key]
            except ValueError:
                pass
            raise

    def __contains__(self, key):
        """Also use config.REMAP and difflib on "in" tests
        """
        key = key.lower()
        return (
            super().__contains__(key) or key in config.REMAP or self._fuzzy_match(key)
        )

    def __setitem__(self, key, value):
        return super().__setitem__(key.lower(), value)

    def __delitem__(self, key, value):
        return super().__setitem__(key.lower(), value)

    def __contains__(self, item):
        return super().__contains__(item.lower())

    def configure(self):
        """Add alternative names for some cards
        """
        # note we difflib match on AKA but not on REMAP.
        for alternative, card in config.AKA.items():
            self[alternative] = self[card]

    def __hash__(self):
        return id(self)

    @functools.lru_cache()
    def _fuzzy_match(self, name):
        """Use a cache to accelerate matching of common misspellings.
        """
        # 0.8 is an empirical value, seems to work nice
        result = difflib.get_close_matches(name, self.keys(), n=1, cutoff=0.8)
        if result:
            match = result[0]
            logger.info("misspelled [{}] matched [{}]".format(name, match))
            return match

    def trait_choices(self, trait):
        """Get all registered values for a given card trait.

        Empty values are removed.

        >>> sorted(VTES.trait_choices('Banned'))
        ['1995', '1997', '1999', '2005', '2008', '2013']
        """

        def get_traits(trait_value):
            if "/" in trait_value:
                for value in trait_value.split("/"):
                    yield value.strip()
            elif "&" in trait_value:
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
        return sorted(self.trait_choices("Discipline"))

    @property
    def types(self):
        return sorted(self.trait_choices("Type"))

    @property
    def clans(self):
        return sorted(self.trait_choices("Clan"))

    def load_csv(self, stream):
        for card in csv.DictReader(stream):
            if card.get("Adv"):
                name = card["Name"] + " (ADV)"
            else:
                name = card["Name"]
            self[name] = card
            if card.get("Aka"):
                self[card["Aka"]] = card
                if card["Aka"][-5:] == ", The":
                    self[("The " + card["Name"][:-5])] = card
            if ", The" in name:
                name = name.split(", The")[0]
                self["The " + name] = card
                self[name] = card
            # add name without suffix if any
            # ':' can not be seen as a suffix marker, e.g. Praxis Seizure:
            if "," in name:
                alternative = name.split(",")[0]
                if len(alternative) > 6:  # e.g. Pier 13, Port of Baltimore
                    self[alternative] = card
            if "(" in card["Name"]:
                alternative = name.split("(")[0].strip()
                # e.g. Pentex(TM) Subversion
                if len(alternative) > 6:
                    self[alternative] = card

        # pickle this
        pickle.dump(VTES, open(config.VTES_FILE, "wb"))

    # usual traits selectors
    def is_crypt(self, card):
        return VTES[card]["Type"] in ("Vampire", "Imbued")

    def is_library(self, card):
        return VTES[card]["Type"] not in ("Vampire", "Imbued")

    # handle multi valued traits
    def is_disc(self, card, discipline):
        if discipline == "Combo":
            return "&" in VTES[card].get("Discipline", "")
        return {discipline} & {
            disc.strip()
            for d in VTES[card].get("Discipline", "").split("/")
            for disc in d.split("&")
        }

    def is_type(self, card, type_):
        return {type_} & {t.strip() for t in VTES[card]["Type"].split("/")}

    def is_clan(self, card, clan):
        return {clan} & {t.strip() for t in VTES[card]["Clan"].split("/")}

    # a consistent deck display matching our parsing rules of TWDA.html
    def deck_to_txt(self, deck):
        def _type(card):
            return config.TYPE_ORDER.index(self[card[0]]["Type"])

        lines = []
        if deck.event:
            lines.append(deck.event)
        if deck.place:
            lines.append(deck.place)
        if deck.date:
            lines.append(deck.date.format("MMMM Do YYYY"))
        if deck.score:
            lines.append(deck.score + "R+F")
        if deck.players_count:
            lines.append("{} players".format(deck.players_count))
        if deck.player:
            lines.append(deck.player)
        lines.append("")
        if deck.name:
            lines.append("Deck Name: " + deck.name)
        if deck.author:
            lines.append("Created by: " + deck.author)
        if deck.comments:
            lines.append("Description:")
            lines.append(deck.comments)
        lines.append("")
        lines.append("-- Crypt: ({} cards)".format(deck.cards_count(self.is_crypt)))
        lines.append("---------------------------------------")
        for card, count in deck.cards(self.is_crypt):
            lines.append(
                "{:<2} {:<35} {:<2} {:<25} {}:{}".format(
                    count,
                    card + (" (ADV)" if self[card]["Adv"] else ""),
                    self[card]["Capacity"],
                    self[card]["Disciplines"],
                    self[card]["Clan"],
                    self[card]["Group"],
                )
            )
        lines.append("-- Library ({})".format(deck.cards_count(self.is_library)))
        # sort by type, count (dec.), name
        library_cards = sorted(
            deck.cards(self.is_library), key=lambda a: (_type(a), -a[1], a[0])
        )
        for kind, cards in itertools.groupby(library_cards, key=_type):
            c1, c2 = itertools.tee(cards)
            lines.append(
                "-- {} ({})".format(
                    config.TYPE_ORDER[kind], sum(count for card, count in c1)
                )
            )
            for card, count in c2:
                lines.append("{:<2} {}".format(count, card))
        return "\n".join(lines)


try:
    VTES = pickle.load(open(config.VTES_FILE, "rb"))
except (FileNotFoundError, EOFError):
    VTES = _VTES()  # evaluates to False as it is empty
