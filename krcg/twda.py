"""This module provides the `TWDA` singleton: Tournament Wining Decks Archive.

If it has not been initialized, TWDA will evaluate to False.
TWDA must be configured with `TWDA.configure()` before being used.
"""
from typing import TextIO
import collections
import io
import pkg_resources  # part of setuptools
import re

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

    def __init__(self):
        self.by_author = collections.defaultdict(list)

    def __getstate__(self) -> list:
        return [d.__getstate__() for d in self.values()]

    def __setstate__(self, state) -> None:
        for data in state:
            d = deck.Deck()
            d.__setstate__(data)
            self[d.id] = d

    def load_from_vekn(self) -> None:
        """Load from vekn.net"""
        r = requests.request("GET", config.VEKN_TWDA_URL)
        r.raise_for_status()
        self.load_html(io.StringIO(r.content.decode("utf-8")))

    def load(self) -> None:
        """Loaf from KRCG static"""
        r = requests.request("GET", config.KRCG_STATIC_SERVER + "/data/twda.json")
        r.raise_for_status()
        self.clear()
        self.__setstate__(r.json())
        self._init()

    def load_html(self, source: TextIO) -> None:
        """Load from TWDA.html

        Args:
            source (stream): The HTML
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
                if pkg_resources.resource_exists("twda_fix", f"{id_}.html"):
                    buffer = io.StringIO(
                        pkg_resources.resource_string("twda_fix", f"{id_}.html").decode(
                            "utf-8"
                        )
                    )
                self[id_] = deck.Deck.from_txt(buffer, id=id_, offset=offset, twda=True)
            elif buffer:
                buffer.write(line)
        self._init()
        logger.info("TWDA loaded")

    def _init(self) -> None:
        """Prepare the TWDA."""
        self.by_author.clear()
        for id, d in self.items():
            if d.author:
                self.by_author[utils.normalize(d.author)].append(id)
            if d.player:
                self.by_author[utils.normalize(d.author)].append(id)


TWDA = _TWDA()
