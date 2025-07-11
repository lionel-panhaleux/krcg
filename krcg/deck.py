"""Deck class: serialization and card access under conditions"""

from typing import Callable, Generator, Optional, TextIO
import arrow
import collections
import datetime
import email.utils
import itertools
import logging
import re
import requests
import unidecode
import urllib.parse

from . import config
from . import parser
from . import vtes
from . import utils


logger = logging.getLogger("krcg")


class Deck(collections.Counter):
    """A VTES deck, including meta information such as date, author and comments."""

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
        # corner case: counting the number of "Raven" in "Camille Devereux" copies
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
        preface: bool = True,
    ):
        """Parse input and generate a Deck instance.

        Compatible with most text input formats (TWD, JOL, LackeyCCG, ...)

        Set the `twda` arg to True when parsing TWDA entries, or it won't be perfect.
        Set the `preface` arg to False when parsing pure cards lists (eg. no count)

        Provide the offset when parsing a multi-deck stream for meaningful parsing logs.
        """
        p = parser.Parser(cls(id=id, author=author))
        p.parse(input, offset, twda, preface)
        return p.deck

    @classmethod
    def from_amaranth(cls, uid: str):
        """Fetch a deck from Amaranth."""
        r = requests.post("https://amaranth.vtes.co.nz/api/deck", data={"id": uid})
        r.raise_for_status()
        r = r.json()["result"]
        ret = cls(id=uid, author=r.get("author", None))
        ret.name = r.get("title", None)
        ret.comments = r.get("description", "")
        ret.date = arrow.get(r["modified"]).date()
        if not vtes.VTES:
            vtes.VTES.load()
        for cid, count in r["cards"].items():
            count = int(count)
            if count <= 0:
                continue
            ret[vtes.VTES.amaranth[cid]] = count
        return ret

    @classmethod
    def from_vdb(cls, uid: str):
        """Fetch a deck from VDB."""
        r = requests.get("https://vdb.im/api/deck/" + uid)
        r.raise_for_status()
        r = r.json()
        logger.debug("VDB replied: %s", r)
        ret = cls(id=uid, author=r.get("author", r.get("owner", None)))
        ret.name = r.get("name", None)
        ret.comments = r.get("description", "")
        ret.date = (
            email.utils.parsedate_to_datetime(r["timestamp"]).date()
            if ("timestamp" in r)
            else None
        )
        if not vtes.VTES:
            vtes.VTES.load()
        for cid, count in r["cards"].items():
            count = int(count)
            if count <= 0:
                continue
            ret[vtes.VTES[int(cid)]] = count
        return ret

    @classmethod
    def from_vtesdecks(cls, uid: str):
        """Fetch a deck from VTESDecks."""
        r = requests.get("https://api.vtesdecks.com/1.0/decks/" + uid)
        r.raise_for_status()
        r = r.json()
        logger.debug("VTESDecks replied: %s", r)
        ret = cls(id=uid, author=r.get("author", r.get("owner", None)))
        ret.name = r.get("name", None)
        ret.comments = r.get("description", "")
        ret.date = datetime.datetime.fromisoformat(r.get("modifyDate")).date()
        if not vtes.VTES:
            vtes.VTES.load()
        for card in itertools.chain(r["crypt"], r["library"]):
            count = int(card["number"])
            if count <= 0:
                continue
            ret[vtes.VTES[int(card["id"])]] = count
        return ret

    @classmethod
    def from_url(cls, url: str):
        """Fetch from any deckbuilding website"""
        result = urllib.parse.urlparse(url)
        if result.netloc == "amaranth.vtes.co.nz":
            if result.fragment.startswith("deck/"):
                return cls.from_amaranth(result.fragment[5:])
            raise ValueError("Unknown Amaranth URL format")
        elif result.netloc in {"vdb.smeea.casa", "vdb.im"}:
            if not result.path.startswith("/decks"):
                raise ValueError("Unknown VDB URL path")
            params = urllib.parse.parse_qs(result.query)
            if "id" in params:
                return cls.from_vdb(params["id"][0])
            elif result.fragment:
                ret = cls()
                ret.name = params.get("name", [None])[0]
                ret.author = params.get("author", [None])[0]
                ret.comments = params.get("description", [""])[0]
                if not vtes.VTES:
                    vtes.VTES.load()
                for item in result.fragment.split(";"):
                    card, count = item.split("=", 1)
                    count = int(count)
                    if count <= 0:
                        continue
                    ret[vtes.VTES[int(card)]] = count
                return ret
            elif result.path.startswith("/decks/"):
                return cls.from_vdb(result.path[7:])
            raise ValueError("Unknown VDB URL format")
        elif result.netloc == "vtesdecks.com":
            if not result.path.startswith("/deck"):
                raise ValueError("Unknown VTESDecks URL path")
            return cls.from_vtesdecks(result.path[5:])
        raise ValueError("Unknown deck URL provider")

    def check(self) -> bool:
        """Check a deck conforms to the rules IRT cards count

        Does not check grouping nor banished cards

        Returns:
            True if the deck checks out
        """
        res = True
        library_count = self.cards_count(lambda c: c.library)
        crypt_count = self.cards_count(lambda c: c.crypt)
        if library_count < 60:
            logger.warning(
                "deck %s has too few cards (%s) [%s]",
                self.id,
                library_count,
                self,
            )
            res = False
        if library_count > 90:
            logger.warning(
                "deck %s has too many cards (%s) [%s]",
                self.id,
                library_count,
                self,
            )
            res = False
        if crypt_count < 12:
            logger.warning(
                "deck %s is missing crypt cards (%s) [%s]",
                self.id,
                crypt_count,
                self,
            )
            res = False
        return res

    def to_json(self) -> dict:
        """Return a compact dict representation for JSON serialization."""
        ret = {
            "id": self.id,
            "event": self.event,
            "event_link": self.event_link,
            "place": self.place,
            "date": self.date.isoformat() if self.date else None,
            "tournament_format": self.tournament_format,
            "players_count": self.players_count,
            "player": self.player,
            "score": str(self.score) if self.score else None,
            "name": self.name,
            "author": self.author,
            "comments": self.comments,
            "crypt": {
                "count": self.cards_count(lambda c: c.crypt),
                "cards": [
                    {
                        "id": card.id,
                        "count": count,
                        "name": card.usual_name,
                        "comments": self.cards_comments.get(card),
                    }
                    for card, count in self.cards(lambda c: c.crypt)
                ],
            },
            "library": {"count": self.cards_count(lambda c: c.library), "cards": []},
        }

        # form a section for each type with a header displaying the total
        for kind, cards in self._sorted_library():
            ret["library"]["cards"].append(
                {
                    "type": config.TYPE_ORDER[kind],
                    "count": sum(count for _card, count in cards),
                    "cards": [],
                }
            )
            for card, count in cards:
                ret["library"]["cards"][-1]["cards"].append(
                    {
                        "id": card.id,
                        "count": count,
                        "name": card.name,
                        "comments": self.cards_comments.get(card),
                    }
                )
        return utils.json_pack(ret)

    def to_minimal_json(self) -> dict:
        ret = {
            "id": self.id,
            "name": self.name,
            "cards": {str(card.id): count for card, count in self.cards() if count},
        }
        return utils.json_pack(ret)

    def from_json(self, state) -> None:
        """Initialize from a JSON dict generated by the `to_json()` method."""
        self.id = state.get("id")
        self.event = state.get("event")
        self.place = state.get("place")
        if "date" in state:
            self.date = datetime.date.fromisoformat(state["date"])
        self.tournament_format = state.get("tournament_format")
        self.players_count = state.get("players_count")
        self.player = state.get("player")
        self.score = DeckScore(state.get("score")) if state.get("score") else None
        self.name = state.get("name")
        self.author = state.get("author")
        self.comments = state.get("comments")
        for card_id, count in state.get("cards", {}).items():
            c = vtes.VTES[int(card_id)]
            self[c] = count
        for card in state.get("crypt", {}).get("cards", []):
            c = vtes.VTES[card["id"]]
            self[c] = card["count"]
            if card.get("comments"):
                self.cards_comments[c] = card["comments"]
        for section in state.get("library", {}).get("cards", []):
            for card in section["cards"]:
                c = vtes.VTES[card["id"]]
                self[c] = card["count"]
                if card.get("comments"):
                    self.cards_comments[c] = card["comments"]

    def __str__(self):
        return self.name or "(No Name)"

    def __repr__(self):
        return f"<Deck #{self.id}: {self.name}>"

    @property
    def crypt(self):
        """For convenience, list of crypt (card, count)."""
        return list(self.cards(lambda c: c.crypt))

    @property
    def library(self):
        """For convenience, list of library (card, count)."""
        return list(self.cards(lambda c: c.library))

    def cards(self, condition: Optional[Callable] = None) -> Generator:
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

    def card_names(self, condition: Optional[Callable] = None) -> Generator:
        """Generator yielding card names with an optional filter.

        Args:
            condition: Condition each card must validate to be selected

        Yields:
            card_name
        """
        for card, _count in self.cards(condition):
            yield card

    def cards_count(self, condition: Optional[Callable] = None) -> int:
        """Card counts with an optional filter.

        Args:
            condition: Condition each card must validate to be selected

        Returns:
            The count of cards (matching the condition if any)
        """
        return sum(count for _card, count in self.cards(condition))

    def _sorted_library(self) -> Generator:
        """A generator that yields library cards sorted by type and name.

        Yields:
            "type", [{card_name: count}]
        """

        def _type_index(card_count):
            return config.TYPE_ORDER.index("/".join(sorted(card_count[0].types)))

        library_cards = sorted(
            self.library,
            key=lambda a: (
                _type_index(a),
                utils.normalize(a[0].vekn_name),
            ),
        )
        for kind, cards in itertools.groupby(library_cards, key=_type_index):
            # return a list so it can be iterated over multiple times
            yield kind, list(cards)

    def to_txt(self, format: str = "twd") -> str:
        """Format to text. Default is TWD format."""
        return {
            "twd": self._to_txt_twd,
            "jol": self._to_txt_jol,
            "lackey": self._to_txt_lackey,
        }.get(format, self._to_txt_twd)()

    def _to_txt_twd(self) -> str:
        """A consistent deck display matching the most recent format used in TWDA.html

        Cards are displayed in the order given by the config.TYPE_ORDER list.
        The output matches the newest TWDA entries format exactly.
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
        if lines:
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
            lines.append(self.comments)
        elif lines and lines[-1] != "":
            lines.append("")
        cap = sorted(
            itertools.chain.from_iterable(
                [card.capacity] * count for card, count in self.crypt
            )
        )
        cap_min = sum(cap[:4])
        cap_max = sum(cap[-4:])
        cap_avg = sum(cap) / len(cap)
        lines.append(
            f"Crypt ({self.cards_count(lambda c: c.crypt)} cards, "
            f"min={cap_min}, max={cap_max}, avg={round(cap_avg, 2):g})"
        )
        lines.append("-" * len(lines[-1]))
        max_name = max(len(card.vekn_name) for card, _ in self.crypt) + 1
        max_disc = max(len(" ".join(card.disciplines)) for card, _ in self.crypt) + 1
        max_title = max(len(card.title or "") for card, _ in self.crypt) + 1
        CRYPT_FMT = (
            f"{{count}}x {{name:<{max_name}}} {{capacity:>2}} "
            f"{{disciplines:<{max_disc}}} {{title:<{max_title}}} {{clan}}:{{group}}"
        )
        for card, count in self.crypt:
            official_name = card.vekn_name
            if official_name == "Camille Devereux, The Raven" and self.raven:
                lines.append(
                    CRYPT_FMT.format(
                        count=count - self.raven,
                        name="Camille Devereux",
                        capacity=5,
                        disciplines="FOR PRO ani",
                        title="",
                        clan="Gangrel",
                        group="1",
                    )
                )
                official_name = "Raven"
                count = self.raven
            lines.append(
                CRYPT_FMT.format(
                    count=count,
                    name=official_name,
                    capacity=card.capacity,
                    # use legacy vis trigram for vision
                    disciplines=(
                        " ".join(
                            sorted({"vin": "vis"}.get(d, d) for d in card.disciplines)
                        )
                        or "-none-"
                    ),
                    title=card.title.lower() if card.title else "",
                    clan=card.clans[0],
                    group=card.group.upper(),
                )
            )
            if card in self.cards_comments:
                comment = self.cards_comments[card].replace("\n", " ").strip()
                lines[-1] += f" -- {comment}"
        lines.append(f"\nLibrary ({self.cards_count(lambda c: c.library)} cards)")
        # form a section for each type with a header displaying the total
        for i, (type_index, cards) in enumerate(self._sorted_library()):
            trifle_count = ""
            if type_index == 0:  # Master
                trifle_count = sum(
                    count
                    for card, count in cards
                    if card in vtes.VTES.search(bonus=["trifle"])
                )
                trifle_count = f"; {trifle_count} trifle" if trifle_count else ""
            cr = "\n" if i > 0 else ""
            lines.append(
                f"{cr}{config.TYPE_ORDER[type_index]} "
                f"({sum(count for _, count in cards)}{trifle_count})"
            )
            for card, count in cards:
                if card in self.cards_comments:
                    comment = self.cards_comments[card].replace("\n", " ").strip()
                    lines.append(f"{count}x {card.vekn_name:<23}" f" -- {comment}")
                else:
                    lines.append(f"{count}x {card.vekn_name}")
        return "\n".join(lines)

    def _to_txt_jol(self) -> str:
        """Format used by Jyhad Online."""
        lines = []
        for card, count in self.crypt:
            lines.append(f"{count}x {card.vekn_name}")
        lines.append("")
        for _, cards in self._sorted_library():
            for card, count in cards:
                lines.append(f"{count}x {card.vekn_name}")
        return "\n".join(lines)

    def _to_txt_lackey(self) -> str:
        """Format used by LackeyCCG."""

        def lackerize(name):
            return unidecode.unidecode(card.vekn_name)

        lines = []
        for _, cards in self._sorted_library():
            for card, count in cards:
                lines.append(f"{count}\t{lackerize(card.vekn_name)}")
        lines.append("Crypt:")
        for card, count in self.crypt:
            lines.append(f"{count}\t{lackerize(card.vekn_name)}")
        return "\n".join(lines)

    def to_vdb(self) -> str:
        """Generating vdb.im link to deck"""
        link = "https://vdb.im/decks/deck?"
        params = {}
        if self.name:
            params["name"] = self.name
        if self.author:
            params["author"] = self.name
        if params:
            link += urllib.parse.urlencode(params)
        link += "#"
        for card, count in self.crypt:
            link += f"{card.id}={count};"
        for _, cards in self._sorted_library():
            for card, count in cards:
                link += f"{card.id}={count};"
        return link[:-1]  # remove trailing semicolumn


class DeckScore:
    def __init__(self, s: Optional[str] = None):
        self.game_wins = None
        self.round_vps = None
        self.finals_vps = None
        if s is None:
            return
        score = re.match(
            r"(\s*-?-?\s*(?P<game_wins>\d)\s*gw\s*"
            r"(?P<round_vps>\d+(\.|,)?\d?)\s*(vp)?\s*)?"
            r"(\s*-?-?\s*(?P<plus_mark>\+)?\s*(?P<finals_vps>\d(\.|,)?\d?)\s*"
            r"(?(plus_mark).?|vp))?",
            s.lower(),
        )
        if score.end() < 1:
            raise ValueError("No score information")
        self.game_wins = score.group("game_wins")
        self.round_vps = score.group("round_vps")
        self.finals_vps = score.group("finals_vps")

    def __str__(self):
        ret = ""
        if self.game_wins:
            ret += f"{self.game_wins}GW"
        if self.round_vps:
            ret += f"{self.round_vps}"
        if self.finals_vps:
            ret += f"+{self.finals_vps}"
        return ret
