"""This module provides the `TWDA` singleton: Tournament Wining Decks Archive.

If it has not been initialized, TWDA will evaluate to False.
TWDA must be configured with `TWDA.configure()` before being used.
"""
from typing import TextIO
import collections
import io
import itertools
import os
import pkg_resources  # part of setuptools
import pickle
import re

import arrow
import requests

from . import config
from . import logging
from . import deck
from . import utils

logger = logging.logger


class _TWDA(collections.OrderedDict):
    """An OrderedDict of the TWDA. Parsing TWDA.html is the hard part.

    Attributes:
        spoilers (dict): cards played in over 25% of decks
        tail_re (str): regexp used to parse tail part of card line
    """

    def load_from_vekn(self, limit: int = None, save: bool = True) -> None:
        """Load from vekn.net

        Args:
            limit: Maximum number of decks to load (used to speed up tests)
        """
        r = requests.request("GET", config.VEKN_TWDA_URL)
        r.raise_for_status()
        self.load_html(io.StringIO(r.content.decode("utf-8")), limit, save)

    def load_html(self, source: TextIO, limit: int = None, save: bool = True) -> None:
        """Load from TWDA.html

        The TWDA is then pickled for future use, to avoid loading it too often.

        Args:
            source (file): The HTML
            limit: Maximum number of decks to load (used to speed up tests)
        """
        self.clear()
        id_, buffer, offset = "", None, 0
        for index, line in enumerate(source, 1):
            try:
                id_ = re.match(r"^<a id=([^\s]*)\s", line).group(1)
            except AttributeError:
                pass
            if re.match(r"^<hr><pre>$", line):
                buffer = io.StringIO()
                offset = index
            elif re.match(r"^</pre>", line):
                buffer.seek(0)
                # p = parser.Parser(id=id_)
                # self[id_] = p.deck
                if pkg_resources.resource_exists("twda_fix", f"{id_}.html"):
                    buffer = io.StringIO(
                        pkg_resources.resource_string("twda_fix", f"{id_}.html").decode(
                            "utf-8"
                        )
                    )
                self[id_] = deck.Deck.from_txt(buffer, id=id_, offset=offset, twda=True)
                # p.parse(buffer, offset=offset, twda=True)
                # self[id_].parse(buffer, offset=offset, twda=True)
                if limit and len(self) >= limit:
                    break
            elif buffer:
                buffer.write(line)
        logger.info("TWDA loaded")
        if save:
            pickle.dump(TWDA, open(config.TWDA_FILE, "wb"))

    def configure(
        self,
        date_from: arrow.Arrow = None,
        date_to: arrow.Arrow = None,
        min_players: int = 0,
        spoilers: bool = True,
    ) -> None:
        """Prepare the TWDA, taking date and players count filters into account.

        Args:
            date_from: filter out decks before this date
            date_to: filter out decks after this date
            min_players: if > 0, filter out decks with less players
            spoilers: if True, compute spoilers to filter them out for analysis
        """
        if date_from:
            for key in [
                key for key, value in self.items() if value.date < date_from.date()
            ]:
                del self[key]
        if date_to:
            for key in [
                key for key, value in self.items() if value.date >= date_to.date()
            ]:
                del self[key]
        if min_players:
            for key in [
                key
                for key, value in self.items()
                if value.players_count and value.players_count < min_players
            ]:
                del self[key]
        if spoilers and len(self) > 50:
            self.spoilers = {
                name: count / len(self)
                for name, count in collections.Counter(
                    itertools.chain.from_iterable(d.keys() for d in self.values())
                ).items()
                if count > len(self) / 4
            }
            logger.debug("Spoilers: {}", self.spoilers)
        else:
            self.spoilers = {}
        self.by_author = collections.defaultdict(list)
        for id, d in self.items():
            if d.author:
                self.by_author[utils.normalize(d.author)].append(id)
            if d.player:
                self.by_author[utils.normalize(d.author)].append(id)


try:
    if not os.path.exists(config.TWDA_FILE) or os.stat(config.TWDA_FILE).st_size == 0:
        raise FileNotFoundError(config.TWDA_FILE)
    TWDA = pickle.load(open(config.TWDA_FILE, "rb"))
except (FileNotFoundError, EOFError):
    TWDA = _TWDA()  # evaluates to False as it is empty
