"""This module provides the `TWDA` singleton: Tournament Wining Decks Archive.

If it has not been initialized, TWDA will evaluate to False.
TWDA must be configured with `TWDA.configure()` before being used.
"""
from typing import List, TextIO
import collections
import html
import io
import logging
import pkg_resources  # part of setuptools
import re

import requests

from . import config
from . import deck
from . import utils
from . import vtes

logger = logging.getLogger("krcg")


class _TWDA(collections.OrderedDict):
    """An OrderedDict of the TWDA. Parsing TWDA.html is the hard part.

    Attributes:
        by_author (dict): Decks indexed by author
    """

    def __init__(self):
        super().__init__()
        self.by_author = collections.defaultdict(list)

    def to_json(self) -> List:
        return [d.to_json() for d in self.values()]

    def from_json(self, state) -> None:
        self.clear()
        for data in state:
            d = deck.Deck()
            d.from_json(data)
            self[d.id] = d
        self._init()

    def load_from_vekn(self) -> None:
        """Load from vekn.net"""
        r = requests.request("GET", config.VEKN_TWDA_URL)
        r.raise_for_status()
        self.load_html(io.StringIO(r.content.decode("utf-8")))

    def load(self) -> None:
        """Load from KRCG static"""
        if not vtes.VTES:
            vtes.VTES.load()
        r = requests.request("GET", config.KRCG_STATIC_SERVER + "/data/twda.json")
        r.raise_for_status()
        self.clear()
        self.from_json(r.json())
        self._init()

    def load_html(self, source: TextIO) -> None:
        """Load from TWDA.html"""
        self.clear()
        id_, buffer, offset = "", None, 0
        for index, line in enumerate(source, 1):
            try:
                id_ = re.match(r"^<a id=([^\s]*)\s", line).group(1)
            except AttributeError:
                pass
            # new decklist
            if re.match(r"^<hr><pre>$", line):
                buffer = io.StringIO()
                offset = index
            # whole decklist fetched, parse it
            elif re.match(r"^</pre>", line):
                buffer.seek(0)
                # replace with a version of our own for the worst cases
                if pkg_resources.resource_exists("twda_fix", f"{id_}.html"):
                    buffer = io.StringIO(
                        html.unescape(
                            pkg_resources.resource_string(
                                "twda_fix", f"{id_}.html"
                            ).decode("utf-8")
                        )
                    )
                self[id_] = deck.Deck.from_txt(buffer, id=id_, offset=offset, twda=True)
            elif buffer:
                buffer.write(html.unescape(line))
        self._init()
        logger.info("TWDA loaded")

    def _init(self) -> None:
        """Prepare the TWDA."""
        self.by_author.clear()
        for id, d in self.items():
            if d.author:
                author = re.sub(r"\(.*\)", "", d.author)
                author = re.sub(r'".*"', "", author)
                author = author.split(",")[0]
                author = author.split("&")[0]
                author = author.split(" and ")[0]
                self.by_author[utils.normalize(author)].append(id)
            if d.player:
                self.by_author[utils.normalize(d.player)].append(id)


TWDA = _TWDA()
