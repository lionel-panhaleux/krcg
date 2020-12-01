"""Deck class: pickling and card access under conditions"""
from typing import Callable, Dict, Generator, List, Optional, TextIO, Tuple
import collections
import datetime
import itertools
import re
import textwrap

import arrow
import arrow.parser

from . import config
from . import logging
from . import parser
from . import vtes
from . import utils


Condition = Optional[Callable[[str], bool]]
CardsCount = Tuple[str, int]
CardsList = List[Dict[str, int]]
CardsBlock = Tuple[str, CardsList]

logger = logging.logger


class Deck(collections.Counter):
    """A VTES deck, including meta information such as author and decription.

    Attributes:
        - id (str): ID of the deck. Official TWDA id for TWDA decks
        - name (str): Name of the deck
        - author (str): Deck author
        - comments (str): Comments on the deck
        - event (str): Event (for TWD)
        - place (str): Place where the event was held
        - date (datetime.date): Date on which the event was held
        - tournament_format (str): Format of the event
        - players_count (int): Count of players at the event
        - player (str): Player who played the deck
        - event_link (str): Link to the event webpage
        - score (str): Score the deck achieved (XgwY - Zvp in the final)
    """

    def __init__(self, *args, **kwargs):
        self.id = kwargs.pop("id", None)
        self.author = kwargs.pop("author", None)
        super().__init__(*args, **kwargs)
        self.event = None
        self.place = None
        self.date = None
        self.tournament_format = None
        self.players_count = 0
        self.player = None
        self.event_link = None
        self.score = None
        self.name = None
        self.cards_comments = {}
        self.comments = ""
        # very corner case: counting the number of "Raven" in "Camille Devereux" copies
        self.raven = 0
        self.parser = parser.Parser(self)

    @classmethod
    def from_txt(
        cls,
        input: TextIO,
        id: str = None,
        author: str = None,
        offset: int = 0,
        twda: bool = False,
    ):
        p = parser.Parser(cls(id=id, author=author))
        p.parse(input, offset, twda)
        return p.deck

    def check(self) -> bool:
        """Check a deck conforms to the rules IRT cards count

        Does not check grouping nor banished cards

        Returns:
            True if the deck checks out
        """
        res = True
        library_count = self.cards_count(vtes.VTES.is_library)
        crypt_count = self.cards_count(vtes.VTES.is_crypt)
        if library_count < 60:
            logger.warning(
                "deck has too few cards ({count}) [{repr}]",
                id=self.id,
                count=library_count,
                repr=self,
            )
            res = False
        if library_count > 90:
            logger.warning(
                "deck has too many cards ({count}) [{repr}]",
                id=self.id,
                count=library_count,
                repr=self,
            )
            res = False
        if crypt_count < 12:
            logger.warning(
                "deck is missing crypt cards ({count}) [{repr}]",
                id=self.id,
                count=crypt_count,
                repr=self,
            )
            res = False
        return res

    def __getstate__(self):
        """For pickle serialization.

        Deck inherits `dict` and its special handling of pickle.
        """
        return {
            "id": self.id,
            "cards": collections.OrderedDict(self.cards()),
            "author": self.author,
            "event": self.event,
            "place": self.place,
            "date": self.date.isoformat() if self.date else None,
            "tournament_format": self.tournament_format,
            "score": self.score,
            "players_count": self.players_count,
            "player": self.player,
            "event_link": self.event_link,
            "name": self.name,
            "cards_comments": self.cards_comments,
            "comments": self.comments,
            "raven": self.raven,
        }

    def __setstate__(self, state):
        """For pickle deserialization."""
        self.id = state.get("id")
        self.author = state.get("author")
        self.event = state.get("event")
        self.place = state.get("place")
        try:
            self.date = datetime.date.fromisoformat(state.get("date") or "")
        except ValueError:
            pass
        self.tournament_format = state.get("tournament_format")
        self.score = state.get("score")
        self.players_count = int(state.get("players_count", 0))
        self.player = state.get("player")
        self.event_link = state.get("event_link")
        self.name = state.get("name")
        self.comments = state.get("comments", "")
        self.cards_comments = state.get("cards_comments", {})
        self.raven = state.get("raven", {})
        self.update(state.get("cards", {}))

    def __reduce__(self):
        """For pickle serialization."""
        return (Deck, (), self.__getstate__())

    def __str__(self):
        return self.name or "(No Name)"

    def cards(self, condition: Condition = None) -> Generator[CardsCount, None, None]:
        """Generator yielding (card_name, count), with an optional filter.

        Args:
            condition: Condition each card must validate to be selected

        Yields:
            card_name, count
        """
        for card, count in self.items():
            if condition and not condition(card):
                continue
            yield card, count

    def card_names(self, condition: Condition = None) -> Generator[str, None, None]:
        """Generator yielding card names with an optional filter.

        Args:
            condition: Condition each card must validate to be selected

        Yields:
            card_name
        """
        for card, _count in self.cards(condition):
            yield card

    def cards_count(self, condition: Condition = None) -> int:
        """Card counts with an optional filter.

        Args:
            condition: Condition each card must validate to be selected

        Returns:
            The count of cards (matching the condition if any)
        """
        return sum(count for _card, count in self.cards(condition))

    def _sorted_library(self) -> Generator[CardsBlock, None, None]:
        """A generator that yields library cards sorted by type and name.

        Yields:
            "type", [{card_name: count}]
        """

        def _type_index(card_count):
            return config.TYPE_ORDER.index(
                "/".join(sorted(vtes.VTES[card_count[0]]["Type"]))
            )

        library_cards = sorted(
            self.cards(vtes.VTES.is_library),
            key=lambda a: (
                _type_index(a),
                utils.normalize(vtes.VTES.vekn_name(vtes.VTES[a[0]])),
            ),
        )
        for kind, cards in itertools.groupby(library_cards, key=_type_index):
            # return a list so it can be iterated over multiple times
            yield kind, list(cards)

    def to_txt(self, wrap: int = 90) -> str:
        """A consistent deck display matching our parsing rules of TWDA.html

        Cards are displayed in the order given by the config.TYPE_ORDER list.
        The output is as closed as possible to the newest TWDA entries format.

        Args:
            wrap: If test should be wrapped (especially for comments )

        Returns:
            The normalized text version of the deck
        """
        lines = []
        if self.event:
            lines.append(self.event)
        if self.place:
            lines.append(self.place)
        if self.date:
            lines.append(arrow.get(self.date).format("MMMM Do YYYY"))
        if self.tournament_format:
            lines.append(self.tournament_format)
        if self.players_count:
            lines.append(f"{self.players_count} players")
        if self.player:
            lines.append(self.player)
        if self.event_link:
            lines.append(self.event_link)
        lines.append("")
        if self.score:
            lines.append(f"-- {self.score}")
            lines.append("")
        if self.name:
            lines.append(f"Deck Name: {self.name}")
        if self.author:
            lines.append(f"Created by: {self.author}")
        if self.comments:
            if self.name or self.author:
                lines.append("")
            if wrap and any(len(line) > wrap for line in self.comments.splitlines()):
                lines.extend(textwrap.wrap(self.comments, wrap))
            else:
                lines.append(self.comments)
        elif lines[-1] != "":
            lines.append("")
        cap = sorted(
            itertools.chain.from_iterable(
                [int(vtes.VTES[card]["Capacity"])] * count
                for card, count in self.cards(vtes.VTES.is_crypt)
            )
        )
        cap_min = sum(cap[:4])
        cap_max = sum(cap[-4:])
        cap_avg = sum(cap) / len(cap)
        lines.append(
            f"Crypt ({self.cards_count(vtes.VTES.is_crypt)} cards, "
            f"min={cap_min}, max={cap_max}, avg={round(cap_avg, 2):g})"
        )
        lines.append("-" * len(lines[-1]))
        max_name = (
            max(
                len(vtes.VTES.vekn_name(vtes.VTES[card]))
                for card, _count in self.cards(vtes.VTES.is_crypt)
            )
            + 1
        )
        max_disc = (
            max(
                len(" ".join(vtes.VTES[card]["Disciplines"]))
                for card, _count in self.cards(vtes.VTES.is_crypt)
            )
            + 1
        )
        max_title = (
            max(
                len(vtes.VTES[card].get("Title", ""))
                for card, _count in self.cards(vtes.VTES.is_crypt)
            )
            + 1
        )
        for card, count in self.cards(vtes.VTES.is_crypt):
            official_name = vtes.VTES.vekn_name(vtes.VTES[card])
            if official_name == "Camille Devereux, The Raven" and self.raven:
                lines.append(
                    f"{{}}x {{:<{max_name}}} {{:>2}} {{:<{max_disc}}} "
                    f"{{:<{max_title}}} {{}}:{{}}".format(
                        count - self.raven,
                        "Camille Devereux",
                        vtes.VTES[card]["Capacity"],
                        " ".join(sorted(vtes.VTES[card]["Disciplines"])),
                        vtes.VTES[card].get("Title", ""),
                        vtes.VTES[card]["Clan"][0],
                        vtes.VTES[card]["Group"],
                    )
                )
                official_name = "Raven"
                count = self.raven
            lines.append(
                f"{{}}x {{:<{max_name}}} {{:>2}} {{:<{max_disc}}} "
                f"{{:<{max_title}}} {{}}:{{}}".format(
                    count,
                    official_name,
                    vtes.VTES[card]["Capacity"],
                    " ".join(sorted(vtes.VTES[card]["Disciplines"])),
                    vtes.VTES[card].get("Title", ""),
                    vtes.VTES[card]["Clan"][0],
                    vtes.VTES[card]["Group"],
                )
            )
            if card in self.cards_comments:
                comment = self.cards_comments[card].replace("\n", " ").strip()
                lines[-1] += f" -- {comment}"
        lines.append(f"\nLibrary ({self.cards_count(vtes.VTES.is_library)} cards)")
        # form a section for each type with a header displaying the total
        for i, (kind, cards) in enumerate(self._sorted_library()):
            trifle_count = ""
            if kind == 0:
                trifle_count = sum(
                    count
                    for card, count in cards
                    if re.search(r"(t|T)rifle", vtes.VTES[card]["Card Text"])
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
                if card in self.cards_comments:
                    comment = self.cards_comments[card].replace("\n", " ").strip()
                    lines.append(
                        f"{count}x {vtes.VTES.vekn_name(vtes.VTES[card]):<23}"
                        f" -- {comment}"
                    )
                else:
                    lines.append(f"{count}x {vtes.VTES.vekn_name(vtes.VTES[card])}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """A consistent deck serialization for the API

        Cards are listed in the order given by the config.TYPE_ORDER list.

        Returns:
            The serialized deck
        """
        ret = {
            "twda_id": self.id,
            "event": self.event,
            "place": self.place,
            "date": self.date,
            "tournament_format": self.tournament_format,
            "players_count": self.players_count,
            "player": self.player,
            "score": self.score,
            "name": self.name,
            "author": self.author,
            "comments": self.comments,
            "crypt": {
                "count": self.cards_count(vtes.VTES.is_crypt),
                "cards": [
                    {
                        "id": vtes.VTES[card]["Id"],
                        "count": count,
                        "name": card,
                        "comments": self.cards_comments.get(card),
                    }
                    for card, count in self.cards(vtes.VTES.is_crypt)
                ],
            },
            "library": {"count": self.cards_count(vtes.VTES.is_library), "cards": []},
        }

        # form a section for each type with a header displaying the total
        for kind, cards in self._sorted_library():
            ret["library"]["cards"].append(
                {
                    "type": config.TYPE_ORDER[kind],
                    "count": sum(count for card, count in cards),
                    "cards": [],
                }
            )
            for card, count in cards:
                ret["library"]["cards"][-1]["cards"].append(
                    {
                        "id": vtes.VTES[card]["Id"],
                        "count": count,
                        "name": card,
                        "comments": self.cards_comments.get(card),
                    }
                )
        return utils.json_clean(ret)
