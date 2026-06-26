"""Deck list parser.

Handles legacy TWDA formats and other deck list idiosyncrasies.
Only modify this file if you know what you're doing, and proceed with caution.
"""

from typing import Any
import collections.abc
import enum
import logging
import math
import re

import arrow

from .collections import CardDict
from . import models
from . import utils


LOG = logging.getLogger("krcg")


def setup_parser_logging(include_deck_id: bool = True):
    """Configure logging for the parser module.

    This displays line number and optionally deck ID in the log messages.
    """
    if include_deck_id:
        formatter = logging.Formatter(
            "[%(levelname)s][%(deck_id)s][%(line)s] %(message)s"
        )
    else:
        formatter = logging.Formatter("[%(levelname)s][%(line)s] %(message)s")
    for handler in LOG.handlers:
        handler.setFormatter(formatter)


def deck_from_txt(
    source: collections.abc.Iterable[str],
    cards: CardDict,
    /,
    *,
    id: str = "",
    twda: bool = False,
) -> models.Deck:
    """Parse a deck list and return a Deck instance.

    Use setup_parser_logging() first to get line# logging.
    """
    return Parser(cards, twda=twda, id=id).parse(source)


#: classic headers in deck lists
_HEADERS = [
    "actin",
    "action",
    "acton",
    "average",
    "burn option",
    "capacity",
    "card",
    "combat",
    "comment",
    "conviction",
    "convinction",
    "crypt",
    "deck",
    "description",
    "disciplineless",
    "combo",
    "double",
    "equip",
    "equipament",
    "equipment",
    "equiptment",
    "equpment",
    "event",
    "librairie",
    "library",
    "master",
    "minion",
    "misc",
    "miscellaneous",
    "mixed",
    "mod",
    "modifier",
    "multitype",
    "non-skilled",
    "other",
    "politcal",
    "politic",
    "political",
    "power",
    "reaction",
    "rection",
    "retainer",
    "skill-less",
    "total",
    "trifle",
    "vote",
    "and",
]
# headers if first word only (do not match "political ally" as a header)
_HEADERS_FIRST_WORD = [
    "allies",
    "ally",
]
_DISCIPLINES = {
    "abombwe",
    "animalism",
    "auspex",
    "celerity",
    "chimerstry",
    "daimoinon",
    "dementation",
    "dominate",
    "fortitude",
    "melpominee",
    "mytherceria",
    "necromancy",
    "obeah",
    "obfuscate",
    "oblivion",
    "obtenebration",
    "potence",
    "presence",
    "protean",
    "quietus",
    "sanguinus",
    "serpentis",
    "spiritus",
    "temporis",
    "thaumaturgy",
    "thanatosis",
    "valeren",
    "vicissitude",
    "visceratika",
}
_HEADERS_RE = (
    "(" + "|".join(re.escape(utils.normalize(h)) + "s?" for h in _HEADERS) + ")"
)
_HEADERS_FIRST_RE = (
    "("
    + "|".join(
        re.escape(utils.normalize(h)) + "s?" for h in _HEADERS + _HEADERS_FIRST_WORD
    )
    + ")"
)
_HEADERS_RE = (
    r"^(\s|/|-|\d|_)*{0}((\s|/|-)*{1})*".format(_HEADERS_FIRST_RE, _HEADERS_RE)
    + r"(\s|\d|:|;|\.|\(|\)|\[|\]|/|-|=|,|"
    + r"cards?|carta|cars|total|min|max|avg|masters?|minions?|trifles?)*$"
)

# ######################################################################################
# Card count line regular expression (tricky one, core of the parser)

# optional punctuation
_PUNCTUATION = r"\s*-?((x|X)+\s)?(\*|_)*\s*"
# 2 digits maximum to avoid miscounting "419 Operation" and such
# negative lookahead to avoid matching part of a card name (eg. 2nd)
_ANTE_COUNT = r"(x|X|\*)*(?P<ante_count>\d{1,2})(?!(\d|st|nd|rd|th))"
# PUNCTUATION = r"\s*((x|X|-)\s)?\*?\s*"
# non-greedy qualifier for card name,
# matches what the tail expression does not
# special case for "channel 10" to avoid parsing 10x "channel".
# "local 1111" and such are OK: we only consider max 2 digits as valid.
_NAME = r"(?P<name>channel 10|.+?)(,\s*$)?"
# only match a crypt tail if a card count was present in the head
_DISCIPLINE_TRIGRAM = "|".join(
    [
        "-none-",
        "none",
        "abo",
        "ani",
        "aus",
        "cel",
        "chi",
        "dai",
        "def",
        "dem",
        "dom",
        "for",
        "inn",
        "jud",
        "mar",
        "mel",
        "myt",
        "nec",
        "obe",
        "obf",
        "obl",
        "obt",
        "pot",
        "pre",
        "pro",
        "qui",
        "red",
        "san",
        "ser",
        "spi",
        "tem",
        "tha",
        "thn",
        "val",
        "ven",
        "vic",
        "vin",
        "vis",
        "viz",
    ]
)
_TITLE = "|".join(
    [
        "primogen",
        "prince",
        "justicar",
        "inner circle",
        "imperator",
        "bishop",
        "archbishop",
        "cardinal",
        "regent",
        "priscus",
        "baron",
        "magaji",
        "kholo",
        # number before "vote(s)" that are swallowed by preceding re expression
        "vote",
        "votes",
    ]
)
_CLAN = "|".join(
    [
        "none",
        "osebo",
        "lasombra",
        "tremere",
        "harbinger of skulls",
        "blood brother",
        "toreador",
        "giovanni",
        "hecata",
        "ahrimane",
        "akunanse",
        "brujah",
        "assamite",
        "banu haqim",
        "ministry",
        "follower of set",
        "brujah antitribu",
        "guruhi",
        "toreador antitribu",
        "tzimisce",
        "malkavian",
        "gangrel",
        "gangrel antitribu",
        "daughter of cacophony",
        "salubri antitribu",
        "samedi",
        "baali",
        "ravnos",
        "kiasyd",
        "nagaraja",
        "pander",
        "ventrue antitribu",
        "nosferatu antitribu",
        "malkavian antitribu",
        "tremere antitribu",
        "ishtarri",
        "nosferatu",
        "ventrue",
        "gargoyle",
        "salubri",
        "avenger",
        "true brujah",
        "visionary",
        "defender",
        "caitiff",
        "abomination",
        "martyr",
        "innocent",
        "judge",
        "redeemer",
    ]
)
_CRYPT_TAIL = r"(?(ante_count)(?P<crypt_tail>\s+(\d{{1,2}}|{})\s+".format(
    _DISCIPLINE_TRIGRAM
) + r"({}|{}|{}|\s|:|g?\d{{1,2}}|any|g\*)*)|%NOMATCH%)?".format(
    _DISCIPLINE_TRIGRAM, _TITLE, _CLAN
)
_PUNCTUATED_TRAIT = "|".join(
    [
        "defense",
        "fligh",
        "gargoyle",
        "innocence",
        "judgment",
        "martyrdom",
        "pander",
        "presence",
        # appears in name "touch of valeren"
        "valeren",
        "vengeance",
        "vision",
        "mage",
        "mummy",
        "bane mummy",
        "wraith",
        "hunter",
        "giovanni",
        "goblin",
        "changeling",
        # this one often appears after double dashes in legacy deck lists:
        # Bang Nakh -- Tiger's Claws
        # catch it here to avoid putting it in comments,
        # there's a matching alias in config.ALIASES
        "tiger's claws",
        # this one is still in the card name !
        # "bastet",
    ]
)
_NAKED_TRAIT = "|".join(
    [
        "trifle",
        "abomination",
        "ahrimane",
        "akunanse",
        "assamite",
        "baali",
        "blood brother",
        "brujah",
        "brujah antitribu",
        "caitiff",
        "daughter of cacophony",
        "follower of set",
        "gangrel",
        "gangrel antitribu",
        "guruhi",
        "harbinger of skulls",
        "ishtarri",
        "kiasyd",
        "lasombra",
        "malkavian",
        "malkavian antitribu",
        "nagaraja",
        "nosferatu",
        "nosferatu antitribu",
        "osebo",
        "ravnos",
        "salubri",
        "salubri antitribu",
        "samedi",
        "toreador",
        "toreador antitribu",
        "tremere",
        "tremere antitribu",
        "true brujah",
        "tzimisce",
        "ventrue",
        "ventrue antitribu",
        "abombwe",
        "animalism",
        "auspex",
        "celerity",
        "chimerstry",
        "daimoinon",
        "dementation",
        "dominate",
        "fortitude",
        "maleficia",
        "melpominee",
        "mytherceria",
        "necromancy",
        "obeah",
        "obfuscate",
        "obtenebration",
        "potence",
        "protean",
        "quietus",
        "sanguinus",
        "serpentis",
        "spiritus",
        "striga",
        "temporis",
        "thanatosis",
        "thaumaturgy",
        "vicissitude",
        "visceratika",
    ]
)
_TRAIT = (
    r"\s+((\s|-|\(|\[|/|\*)+({0})|(\s|-|\(|\[|/|\*)*({1}))(\s|\)|\]|/|\*)*$".format(
        _PUNCTUATED_TRAIT, _NAKED_TRAIT
    )
)
_POST_COUNT = (
    # mandatory punctuation (beware of "AK-47", "Kpist m/45", ...)
    r"(\s|\(|\[|:|cards?|total|,)+"
    r"(?P<count_mark>-*\s|x*|\**|=*|/*)\s*(?P<post_count>\d{1,2})"
    # negative lookahead to avoid matching part of a card name (eg. 2nd)
    # also ignore blood ("b") / pool ("p") cost sometimes indicated there
    # also special exception for "Pier 13, Port of Baltimore"
    r"(?!(st|nd|rd|th|.?\d|b|p|(..?port)))"
    r"(\s|\(|\)|\[|\]|:|cards?|total|\d|trifles?|,)*"
)
# three card names have parentheses - do not parse as comment
_BRACED_COMMENT = (
    r"\s+(\((?!bastet|endless night|olaf holte)(?P<parenthesis_comment>[^\)]+)\)"
    r"|\[(?P<bracket_comment>[^\]]+?)\s*\])"
)
_LINE_COMMENT = (
    r"\s+(?P<comment_mark>--*|//*\**|\*\**)\s*" r"(?P<line_comment>.+?)(-|/|\*|\s)*"
)
_COMMENT = f"({_BRACED_COMMENT}|{_LINE_COMMENT})"
# The full-fledged regular expression used to parse a line in a decklist
_RE = (
    f"^{_PUNCTUATION}({_ANTE_COUNT})?{_PUNCTUATION}{_NAME}{_CRYPT_TAIL}"
    f"({_POST_COUNT})?({_TRAIT})?{_COMMENT}?\\s*$"
)


class LineLogAdapter(logging.LoggerAdapter):
    """Logger adapter that prefixes messages with line and deck IDs."""

    def process(
        self, msg: str, kwargs: collections.abc.MutableMapping[str, Any]
    ) -> tuple[str, collections.abc.MutableMapping[str, Any]]:
        """Process a message.

        Args:
            msg: The message to process.
            kwargs: Additional keyword arguments.

        Returns:
            A tuple containing the processed message and the keyword arguments.
        """
        if not self.extra:
            self.extra = {}
        assert isinstance(self.extra, dict)
        self.extra.update(kwargs.get("extra", {}))
        return "[%6s][%s] %s" % (self.extra["line"], self.extra["deck"], msg), kwargs


class Mark(enum.Enum):
    """A comment mark type."""

    LINE = enum.auto()
    MULTILINE = enum.auto()
    PREFACE = enum.auto()
    END = enum.auto()


class Comment:
    """Helper class for comment parsing."""

    def __init__(
        self,
        comment: str = "",
        card: Any | None = None,
        mark: Mark | None = None,
    ):
        """Constructor.

        Args:
            comment: The comment string.
            card: The card associated with the comment.
            mark: The mark type.
        """
        self.card = card
        self.mark = mark
        self.string = comment

    def __iadd__(self, comment: str) -> "Comment":
        """Add a comment line to the current comment string."""
        comment = comment.rstrip()
        if self.string:
            self.string += "\n"
            if comment[-2:] == "*/" and self.string[:2] != "/*":
                comment = comment[:-2].rstrip()
        else:
            comment.lstrip()
        self.string += comment
        return self

    def __bool__(self) -> bool:
        """Return True if the comment is not empty."""
        return bool(self.string)

    def __str__(self) -> str:
        """Return the comment string."""
        return self.string

    def finalize(self) -> None:
        """Strip the comment string from spurious spaces and comment marks."""
        previous_length = math.inf
        while 1 < len(self.string) < previous_length:
            self.string = self.string.strip()
            previous_length = len(self.string)
            if self.string[:2] == "--":
                self.string = self.string[2:]
            if self.string[:2] == "//":
                self.string = self.string[2:]
            for size, lhs, rhs in [(1, "(", ")"), (1, "[", "]"), (2, "/*", "*/")]:
                if self.string[:size] == lhs and self.string[-size:] == rhs:
                    self.string = self.string[size:-size]
        # if comment begin with a count and has a prenthesis
        # it may be a parsing error
        if not self.mark:
            match = re.match(
                f"{_PUNCTUATION}{_ANTE_COUNT}(x|X|\\*|-|_|\\s)+(\\w|\\d|\\s|:|'|,)+\\(",
                self.string.split("\n", 1)[0],
            )
            if match:
                LOG.warning('failed to parse "%s"', self.log)
                self.string = ""

    @property
    def log(self) -> str:
        """Return a log-friendly version of the comment (cropped at 83 chars)."""
        res = self.string.replace("\n", " ").strip()
        if len(res) > 83:
            res = res[:80] + "..."
        return res

    @property
    def multiline(self) -> bool:
        """Return True if the comment is multiline."""
        return len(self.string.split("\n")) > 1


class Parser:
    """Deck list parser. Holds the parsing context."""

    def __init__(
        self,
        cards: CardDict,
        *,
        twda: bool = False,
        id: str = "",
    ) -> None:
        """Constructor.

        Args:
            cards: The cards database (name -> Card lookup).
            twda: If True, parse the positional TWDA tournament headers.
            id: The deck id.
        """
        self.cards_db: CardDict = cards
        self.twda: bool = twda
        self.preface: bool = True  # internal state: still in the preface region
        self.current_comment: Comment | None = None
        self.separator: bool = False  # used only for additional checks on the TWDA
        self.cards: set[models.CardInDeck] = set()
        self.logger: logging.Logger | logging.LoggerAdapter = LOG
        self.deck: models.Deck = models.Deck(id=id)

    @property
    def _previous_line(self) -> int:
        return (getattr(self.logger, "extra", {}).get("line") or 1) - 1

    def parse(self, source: collections.abc.Iterable[str]) -> models.Deck:
        """Parse a deck list and return the Deck."""
        for index, line in enumerate(source, 1):
            self.logger = LineLogAdapter(LOG, {"line": index, "deck": self.deck.id})
            self.parse_line(index, line)
        # finalize current_comment if any
        self.comment("", mark=Mark.END)
        self.deck.cards = list(self.cards)
        return self.deck

    def parse_line(self, index: int, line: str) -> None:
        """Parse a line of text."""
        # remove head/tail and misplaced spaces around punctuation for easy parsing
        line = line.rstrip()
        line = line.replace(" :", ":")
        line = line.replace("( ", "(")
        line = line.replace(" )", ")")
        if self.preface:
            if self.twda and self.parse_twda_headers(index, line):
                return
            if self.parse_headers(index, line):
                return
        else:
            # author is only set if different than player
            if self.deck.author and not self.deck.player:
                self.deck.player = self.deck.author
                self.deck.author = ""
            if self.deck.author == self.deck.player:
                self.deck.author = ""
        card = self.get_card(line)
        if card:
            self.cards.add(card)

    def parse_twda_headers(self, index: int, line: str) -> bool:
        """Parse a line of text for TWDA headers."""
        self.deck.event = self.deck.event or models.Event()
        if index == 1:
            self.deck.event.name = line
            return True
        # third line should always be the date, but it has happened that some
        # submissions lack this field, misformat it,
        # or omit the location (2nd line) for online events
        if not self.deck.event.date:
            try:
                self.deck.event.date = arrow.get(line, "MMMM Do YYYY").date()
                return True
            except arrow.parser.ParserMatchError:
                if index == 3:
                    self.logger.warning("Unable to parse date header: %s", line)
                pass
        if index == 2:
            self.deck.event.place = line
            return True
        if self.deck.event.rounds == models.RoundFormat.NA:
            try:
                self.deck.event.rounds = models.RoundFormat(
                    re.match(r"\s*(\d+R\+F)", line).group(1)
                )
                return True
            except (AttributeError, ValueError):
                pass
        if not self.deck.event.players_count:
            try:
                players_count = re.match(r"\s*(\d+|\?+)\s*player", line).group(1)
                self.deck.event.players_count = int(players_count)
                return True
            except AttributeError:
                pass
            except ValueError:
                return True
        # Ignore Organizer line (rare inclusion)
        try:
            if re.match(r"^\s*(O|o)rgani(s|z)er", line):
                return True
        except AttributeError:
            pass
        # Newer lists provide an event link
        if not self.deck.event.url:
            try:
                self.deck.event.url = re.match(r"^\s*(https?://.*)$", line).group(1)
                return True
            except AttributeError:
                pass
        # Player is always indicated, last entry before score
        # remove comments on player's name
        if not self.deck.player:
            player = re.sub(r"\s*\([^\)]*\)", "", line.strip())
            player = re.sub(r"\s*--\s+.*", "", player)
            if player:
                self.deck.player = player
            return True
        return False

    def parse_headers(self, index: int, line: str) -> bool:
        """Parse non-TWDA headers (name, author, score, etc.)."""
        description = re.match(r"^\s*(D|d)escription\s*:?\s*", line)
        if description:
            line = line[description.end() :]
        if not self.deck.score:
            try:
                self.deck.score = self.parse_score(index, line)
                return True
            except (AttributeError, ValueError):
                pass
        if not self.deck.name:
            try:
                self.deck.name = (
                    re.match(r"^\s*((d|D)eck)?\s?(n|N)ame\s*:\s*(?P<name>.*)$", line)
                    .group("name")
                    .strip()
                )
                return True
            except (AttributeError, ValueError):
                pass
        if not self.deck.author:
            try:
                self.deck.author = (
                    re.match(
                        r"\s*(((c|C)reated|(d|D)eck)\s*(b|B)y|"
                        r"(a|A)uthors?|(c|C)reators?)\s*(:|\s)\s*(?P<author>.*)$",
                        line,
                    )
                    .group("author")
                    .strip()
                )
                return True
            except AttributeError:
                pass
        if not self.deck.player:
            try:
                self.deck.player = (
                    re.match(
                        r"\s*((p|P)layed\s*(b|B)y)|((p|P)layer)\s*(:|\s)\s*"
                        r"(?P<player>.*)$",
                        line,
                    )
                    .group("player")
                    .strip()
                )
                return True
            except AttributeError:
                pass
        if not self.deck.event or not self.deck.event.date:
            try:
                date = arrow.get(line, "MMMM Do YYYY").date()
                # only add an Event if we manage to parse a date
                self.deck.event = self.deck.event or models.Event()
                self.deck.event.date = date
                return True
            except arrow.parser.ParserMatchError:
                pass
        return False

    def parse_score(self, index: int, line: str) -> models.Score:
        """Parse a line of text for a score."""
        score = re.match(
            r"(\s*-?-?\s*(?P<game_wins>\d)\s*gw\s*"
            r"(?P<round_vps>\d+(\.|,)?\d?)\s*(vp)?\s*)?"
            r"(\s*-?-?\s*(?P<plus_mark>\+)?\s*(?P<finals_vps>\d(\.|,)?\d?)\s*"
            r"(?(plus_mark).?|vp))?",
            line.lower(),
        )
        if score is None or score.end() < 1:
            raise ValueError("No score information")
        game_wins = score.group("game_wins")
        round_vps = score.group("round_vps")
        if round_vps:
            round_vps = round_vps.replace(",", ".")
        finals_vps = score.group("finals_vps")
        if finals_vps:
            finals_vps = finals_vps.replace(",", ".")
        return models.Score(
            round_gw=int(game_wins) if game_wins else 0,
            round_vp=float(round_vps) if round_vps else 0.0,
            finals_vp=float(finals_vps) if finals_vps else 0.0,
        )

    def get_card(self, line: str) -> models.CardInDeck | None:
        """Try to find a card and count; register possible comment."""
        if re.match(_HEADERS_RE, utils.normalize(line)):
            return None
        card, name, count, comment, mark = None, None, 0, "", None
        match = re.match(_RE, utils.normalize(line))
        # count before a card name is most common and easier to parse
        if match:
            name = match.group("name")
            count = int(match.group("ante_count") or 0)
            # get the group from the crypt tail
            group = None
            tail = match.group("crypt_tail")
            if tail:
                try:
                    group = int(tail[-1])
                except ValueError:
                    pass

        if name:
            if not count:
                # do not match name with no count prefix during the preface
                # since card names are often found in preface comments and
                # we expect a clean first line, either a prefixed crypt card (TWDA)
                # or a prefixed card anyway (Lackey, JOL, etc.)
                if self.preface:
                    name = None
                else:
                    count = int(match.group("post_count") or 1)  # type: ignore
                    if not match.group("count_mark"):  # type: ignore
                        # Be wary of disciplines: they are sometimes headers, but
                        # indistinguishable from actual Master discipline cards
                        if name.strip(" :()[]-_*=") in _DISCIPLINES:
                            # if parsing TWDA, ignore the line and warn
                            if self.twda:
                                self.logger.warning('improper discipline "%s"', line)
                                return None
                            # otherwise log as debug and count it as a discipline card
                            self.logger.debug('naked discipline (no count) "%s"', line)
            # for evolutions (eg. Theo Bell (G6)) the name in TWDA
            # might not contain the group, we need to rely on the group in crypt tail
            if name and group and name[-1] != ")":
                name += f" (g{group})"
            try:
                card = self.cards_db[name]  # type: ignore
                # special case for Camille / Raven to keep them distinct if the decklist
                # predates the merge of the two crypt cards
                if (
                    name in ["raven", "raven (g1)"]
                    and card.full_name == "Camille Devereux, The Raven (G1)"
                ):
                    self.deck.raven = count
            except KeyError:
                card, count = None, 0
        # do not match a card inside a marked multiline comment
        if (
            card
            and self.current_comment
            and self.current_comment.mark == Mark.MULTILINE
        ):
            self.logger.warning('discarded match "%s" inside comment "%s"', name, line)
            card, count = None, 0
        # do not match crypt tail expression on a library card
        if (
            card
            and match.group("crypt_tail")
            and not card.kind == models.Card.Kind.CRYPT
        ):
            card, count = None, 0
        # do not match post count on a crypt card
        if card and match.group("post_count") and card.kind == models.Card.Kind.CRYPT:
            card, count = None, 0
        # too many preface comments parse like cards in the TWDA
        if self.twda and name and not self.separator:
            card, count = None, 0
        # if no card was found, the whole line is a comment
        # if a card was found, a comment might still be present as a suffix
        if card:
            card_in_deck = models.CardInDeck.of(card, count)
            comment_span = max(
                match.span("parenthesis_comment"),  # type: ignore
                match.span("bracket_comment"),  # type: ignore
                match.span("line_comment"),  # type: ignore
            )
            # extract the original comment, not the "normalized" parsed version
            if comment_span > (-1, -1):
                comment = line[comment_span[0] : comment_span[1]]
            else:
                comment = ""
            mark_match = match.group("comment_mark") or ""  # type: ignore
            if mark_match[:2] == "/*":
                if "*/" in line:
                    mark = Mark.LINE
                else:
                    mark = Mark.MULTILINE
            else:
                mark = Mark.LINE
        else:
            card_in_deck = None
            if not line or set(line).issubset(set("-=_0123456789")):
                comment = ""
                if len(line) > 1 and set(line).issubset(set("-=_")):
                    self.separator = True
            else:
                comment = line
                # a marked lonely line is OK, but if not mark is found,
                # it may just be a parsing error
                # we decide later, when closing the potential comment
                # (see the comment() method)
                maybe_mark = line.lstrip()[:2]
                if maybe_mark in ["--", "//"]:
                    mark = Mark.LINE
                if line.lstrip()[:1] + line.rstrip()[-1:] in ["()", "[]"]:
                    mark = Mark.LINE
                if maybe_mark == "/*":
                    mark = Mark.MULTILINE
                if line.rstrip()[-2:] == "*/":
                    mark = Mark.END
        self.comment(comment, card=card_in_deck, mark=mark)
        self.preface = self.preface and not card
        return card_in_deck

    def comment(
        self,
        comment: str,
        card: models.CardInDeck | None = None,
        mark: Mark | None = None,
    ) -> None:
        """Handle a comment and possibly log suspected parsing errors."""
        if not (comment or self.current_comment):
            return
        if comment:
            comment = comment.rstrip()
        # warn on unmarked single line comments in the middle of the cards list:
        # they are candidates for parsing errors
        if (
            (card or not comment)
            and not self.preface
            and self.current_comment
            and not self.current_comment.multiline
            and not self.current_comment.mark
        ):
            # TODO use regexes
            if self.current_comment.string.startswith(
                "This deck was last saved"
            ) or self.current_comment.string.startswith("http"):
                self.logger.debug(
                    'ignoring tail comment "%s"',
                    self.current_comment.log,
                    extra={"line": self._previous_line},
                )
            else:
                self.logger.warning(
                    'failed to parse "%s"',
                    self.current_comment.log,
                    extra={"line": self._previous_line},
                )
            self.current_comment = None
        # log unmarked multiline comments in the middle of the list
        # they happen a lot in the TWDA, but checking them may be needed
        if (
            (card or mark)
            and self.current_comment
            and self.current_comment.multiline
            and self.current_comment.mark != Mark.MULTILINE
            and not self.preface
        ):
            self.logger.debug(
                'unexpected multiline comment "%s"',
                self.current_comment.log,
                extra={"line": self._previous_line},
            )
        # if this is a new comment block, register the previous comment on the deck
        if self.current_comment and (
            mark == Mark.END
            or (
                (card or not self.preface)
                # if the comment is multiline and we did not parse a new card, continue
                and (card or not self.current_comment.mark == Mark.MULTILINE)
                # distinguish between a follow-up after a card comment and a new block
                and (
                    # a new card means a new comment
                    # an unparsed line (no card name) after non-multiline-marked comment
                    # on a card is also viewed as new comment (may be a parsing error)
                    (self.current_comment.card != card)
                    # a blank line after a card comment means a new comment
                    or (not comment and self.current_comment.card)
                )
            )
        ):
            if mark == Mark.END:
                self.current_comment += comment
                comment = ""
            self.current_comment.finalize()
            if self.current_comment:
                if self.current_comment.card:
                    self.current_comment.card.comment = str(self.current_comment)
                else:
                    # leave a blank line between separated comments
                    if self.deck.comment:
                        self.deck.comment += "\n"
                    self.deck.comment += str(self.current_comment) + "\n"
            self.current_comment = None
        # start a new comment if we have a non-blank line
        if comment and not self.current_comment:
            self.current_comment = Comment(card=card, mark=mark)
        # append the parsed comment, even if it is a blank line
        if comment or self.current_comment:
            self.current_comment += comment  # type: ignore
        # do nothing on a blank line if we don't have a current comment
