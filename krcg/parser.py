"""Deck list parser.

It handles the legacy TWDA as much as possible.
They are many tricky formats used throughout this historic document.
"""
from typing import TextIO, Tuple, Union
import enum
import math
import re

import arrow

from . import config
from . import logging
from . import vtes
from . import utils


logger = logging.logger

# # Headers used in TWDA, e.g. "Action modifiers/Combat cards total: (4)"
# HEADERS = set()
# HEADERS.update(config.HEADERS)
# HEADERS.update([h + "s" for h in config.HEADERS] + ["ally", "allies"])
# HEADERS.update([f"{h1}/{h2}" for h1, h2 in itertools.permutations(HEADERS, 2)])
# HEADERS.update(config.ADDITIONAL_HEADERS)
# HEADERS.update([h + " card" for h in HEADERS] + [h + " cards" for h in HEADERS])
# HEADERS.update(["card", "cards", "deck"])
# # HEADERS.update([h + " total" for h in HEADERS])
# HEADERS.update([h + ":" for h in HEADERS])

HEADERS = (
    "(" + "|".join(re.escape(utils.normalize(h)) + "s?" for h in config.HEADERS) + ")"
)
HEADERS_RE = (
    r"^(\s|/|-|\d|_)*{0}((\s|/|-)*{0})*".format(HEADERS)
    + r"(\s|\d|:|;|\.|\(|\)|\[|\]|/|-|=|,|"
    + r"cards?|carta|cars|total|min|max|avg|masters?|minions?|trifles?)*$"
)

# ######################################################################################
# Card count line regular expression (tricky one)

# optional punctuation
PUNCTUATION = r"\s*-?((x|X)+\s)?(\*|_)*\s*"
# 2 digits maximum to avoid miscounting "419 Operation" and such
# negative lookahead to avoid matching part of a card name (eg. 2nd)
ANTE_COUNT = r"(x|X|\*)*(?P<ante_count>\d{1,2})(?!(\d|st|nd|rd|th))"
# PUNCTUATION = r"\s*((x|X|-)\s)?\*?\s*"
# non-greedy qualifier for card name,
# matches what the tail expression does not
# special case for "channel 10" to avoid parsing 10x "channel".
# "local 1111" and such are OK: we only consider max 2 digits as valid.
NAME = r"(?P<name>channel 10|.+?)(,\s*$)?"
# only match a crypt tail if a card count was present in the head
DISCIPLINE_TRIGRAM = "|".join(set(utils.normalize(d) for d in config.DIS_MAP))
CRYPT_TRAIT = "|".join(
    set(utils.normalize(t) for t in config.TRAITS + ["vote", "votes"])
)
CLAN = "|".join(
    [
        "none",
        "osebo",
        "lasombra",
        "tremere",
        "harbinger of skulls",
        "blood brother",
        "toreador",
        "giovanni",
        "ahrimane",
        "akunanse",
        "brujah",
        "assamite",
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
CRYPT_TAIL = (
    r"(?P<crypt_tail>(?(ante_count)\s+\d{1,2}\s+"
    + r"({}|{}|{}|\s|:|\d{{1,2}}|any)*))?".format(DISCIPLINE_TRIGRAM, CRYPT_TRAIT, CLAN)
)
PUNCTUATED_TRAIT = "|".join(
    [
        "defense",
        "fligh",
        "gargoyle",
        "innocence",
        "judgment",
        "martyrdom",
        "pander",
        "presence",
        "vengeance",
        "vision",
        "mage",
        "mummy",
        "bane mummy",
        "wraith",
        "hunter",
        "goblin",
        "changeling",
        "tiger's claws",
        # these two are still in the card name,
        # but we have matching aliases in the config
        "bastet",
        "endless night",
    ]
)
NAKED_TRAIT = "|".join(
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
        "giovanni",
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
        "valeren",
        "vicissitude",
        "visceratika",
    ]
)
TRAIT = r"\s+((\s|-|\(|\[|/|\*)+({0})|(\s|-|\(|\[|/|\*)*({1}))(\s|\)|\]|/|\*)*$".format(
    PUNCTUATED_TRAIT, NAKED_TRAIT
)
POST_COUNT = (
    # mandatory punctuation (beware of "AK-47", "Kpist m/45", ...)
    r"(\s|\(|\[|:|cards?|total|,)+"
    r"(?P<count_mark>-*\s|x*|\**|=*|/*)\s*(?P<post_count>\d{1,2})"
    # negative lookahead to avoid matching part of a card name (eg. 2nd)
    # also ignore blood ("b") / pool ("p") cost sometimes indicated there
    # also special exception for "Pier 13, Port of Baltimore"
    r"(?!(st|nd|rd|th|.?\d|b|p|(..?port)))"
    r"(\s|\(|\)|\[|\]|:|cards?|total|\d|trifles?|,)*"
)
BRACED_COMMENT = (
    r"\s+(\((?P<parenthesis_comment>[^\)]+)\)|\[(?P<bracket_comment>[^\]]+?)\s*\])"
)
LINE_COMMENT = (
    r"\s+(?P<comment_mark>--*|//*\**|\*\**)\s*" r"(?P<line_comment>.+?)(-|/|\*|\s)*"
)
COMMENT = f"({BRACED_COMMENT}|{LINE_COMMENT})"
# full card count line regular expression
# RE = f"^{HEAD}{ANTE_COUNT}?{PUNCTUATION}{NAME}({CLASS}|{POST_COUNT}|{COMMENT})\\s*$"
RE = (
    f"^{PUNCTUATION}({ANTE_COUNT})?{PUNCTUATION}{NAME}{CRYPT_TAIL}"
    f"({POST_COUNT})?({TRAIT})?{COMMENT}?\\s*$"
)


class Mark(enum.Enum):
    LINE = enum.auto()
    MULTILINE = enum.auto()
    PREFACE = enum.auto()
    END = enum.auto()


class Comment:
    """Helper for comments parsing."""

    def __init__(
        self,
        comment: str = "",
        card_name: str = "",
        mark: Union[None, Mark] = None,
    ):
        self.card_name = card_name
        self.mark = mark
        self.string = comment

    def __iadd__(self, comment: str):
        """Add a comment line to self"""
        comment = comment.rstrip()
        if self.string:
            self.string += "\n"
            if comment[-2:] == "*/" and self.string[:2] != "/*":
                comment = comment[:-2].rstrip()
        else:
            comment.lstrip()
        self.string += comment
        return self

    def __bool__(self):
        return bool(self.string)

    def __str__(self):
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
        # if may be a parsing error
        if not self.mark:
            match = re.match(
                f"{PUNCTUATION}{ANTE_COUNT}(x|X|\\*|-|_|\\s)+(\\w|\\d|\\s|:|'|,)+\\(",
                self.string.split("\n", 1)[0],
            )
            if match:
                logger.warning('failed to parse "{}"', self.log)
                self.string = ""

    @property
    def log(self) -> str:
        """Log-friendly version of the comment (cropped at 83 chars)"""
        res = self.string.replace("\n", " ").strip()
        if len(res) > 83:
            res = res[:80] + "..."
        return res

    @property
    def multiline(self) -> bool:
        """True if the comment is multiline"""
        return len(self.string.split("\n")) > 1


class Parser:
    """Deck list parser. Holds the parsing context.

    Attributes:
        deck (deck.Deck): the result, filled by the parsing operation
        preface (bool): stays True until the beginning of the actual cards list
        current_comment (Comment|None): current comment if any
    """

    def __init__(self, deck):
        self.current_comment = None
        self.preface = True
        self.separator = False  # used only for additional checks on the TWDA
        self.deck = deck

    def parse(self, input: TextIO, offset: int = 0, twda: bool = False) -> None:
        """Parse given stream.

        Args:
            offset: offset to add when parsing part of a bigger stream (for logs)
            twda: if true, parse for TWDA headers
        """
        for index, line in enumerate(input, 1):
            logger.extra["line"] = index + offset
            logger.extra["deck"] = self.deck.id
            self.parse_line(index, line, twda)
        # finalize current_comment if any
        self.comment("", mark=Mark.END)

        # Legacy
        # kept here in case we need to rework the TWDA at some point
        # used to include config.TWDA_FIXUP fixes
        # if twda and self.deck.id in config.TWDA_FIXUP:
        #     fixup = config.TWDA_FIXUP[self.deck.id]
        #     for card, count in fixup.get("cards", {}).items():
        #         self.deck[card] = count
        #     for card, comment in fixup.get("cards_comments", {}).items():
        #         self.deck.cards_comments[card] = comment
        #     if "comments" in fixup:
        #         self.deck.comments = fixup["comments"]
        #     if "author" in fixup:
        #         self.deck.author = fixup["author"]
        #     logger.info("fixed up deck")

        # a wrong card count can be a good indication of a parsing error
        if not twda or self.deck.id not in config.TWDA_CHECK_DECK_FAILS:
            self.deck.check()
        logger.extra["line"] = None
        logger.extra["deck"] = None

    def parse_line(self, index: int, line: str, twda: bool):
        """Parse a line of text."""
        # remove head/tail and misplaced spaces around punctuation for easy parsing
        line = line.rstrip()
        line = line.replace(" :", ":")
        line = line.replace("( ", "(")
        line = line.replace(" )", ")")
        if twda and self.preface:
            if self.parse_twda_headers(index, line):
                return
        # import ipdb

        # if index > 34:
        #     ipdb.set_trace()

        name, count = self.get_card(line, twda)
        if name and count:
            self.deck.update({name: count})

    def parse_twda_headers(self, index: int, line: str):
        """Parse a line of text for TWDA headers."""
        if index < 4:
            if index == 1:
                self.deck.event = line
            elif index == 2:
                self.deck.place = line
            elif index == 3:
                self.deck.date = arrow.get(line, "MMMM Do YYYY").date()
            return True
        if not self.deck.tournament_format:
            try:
                self.deck.tournament_format = re.match(r"^\s*(\d+R\+F)", line).group(1)
                return True
            except AttributeError:
                pass
        if not self.deck.players_count:
            try:
                players_count = re.match(r"^\s*(\d+|\?+)\s*player", line).group(1)
                self.deck.players_count = int(players_count)
                return True
            except (AttributeError, ValueError):
                pass
        # Player is always indicated, but after tournament format and count if any
        if not self.deck.player:
            self.deck.player = line
            return True
        # Ignore Organizer line (rare inclusion)
        try:
            if re.match(r"^\s*(O|o)rgani(s|z)er", line):
                return True
        except AttributeError:
            pass
        # Newer lists provide an event link
        if not self.deck.event_link:
            try:
                self.deck.event_link = re.match(r"^\s*(https?://.*)$", line).group(1)
                return True
            except AttributeError:
                pass
        if not self.deck.score:
            try:
                score = re.match(
                    r"-?-?\s*((?P<round_wins>\d)\s*(G|g)(W|w)\s*"
                    r"(?P<round_vps>\d(\.|,)?\d?)\s*((v|V)(p|P))?\s*\+?\s*)?"
                    r"(?P<final>\d(\.|,)?\d?)\s*(v|V)(p|P)",
                    line,
                )
                if score.group("round_wins"):
                    self.deck.score = "{}gw{} + {}vp in the final".format(
                        score.group("round_wins"),
                        score.group("round_vps"),
                        score.group("final"),
                    )
                else:
                    self.deck.score = "{}vp in the final".format(score.group("final"))
                return True
            except AttributeError:
                pass
        if not self.deck.name:
            try:
                self.deck.name = re.match(
                    r"^\s*((d|D)eck)?\s?(n|N)ame\s*:\s*(?P<name>.*)$", line
                ).group("name")
                return True
            except AttributeError:
                pass
        if not self.deck.author:
            try:
                self.deck.author = re.match(
                    r"(((c|C)reated)|((d|D)eck)\s*(b|B)y)|"
                    r"((a|A)uthors?)|((c|C)reators?)\s*:?\s*(?P<author>.*)$",
                    line,
                ).group("author")
                return True
            except AttributeError:
                pass

    def get_card(self, line: str, twda: bool = False) -> Tuple[str, int]:
        """Try to find a card and count, register possible comment."""
        if re.match(HEADERS_RE, utils.normalize(line)):
            return None, 0
        name, count, comment, mark = None, 0, "", None
        match = re.match(RE, utils.normalize(line))
        # count before a card name is most common and easier to parse
        if match:
            name = match.group("name")
            count = int(match.group("ante_count") or 0)
        if name:
            if not count:
                # do not match name with no count prefix during the preface
                # since card names are often found in preface comments and
                # we expect a clean first line, either a prefixed crypt card (TWDA)
                # or a prefixed card anyway (Lackey, JOL, etc.)
                if self.preface:
                    name = None
                else:
                    count = int(match.group("post_count") or 1)
                    if not match.group("count_mark"):
                        # Be wary of disciplines: they are sometimes headers, but
                        # distinguishing them from actual Master discipline cards
                        # is not decidable so we log and ignore the line
                        if name.strip(" :()[]-_*=") in set(
                            a.lower() for a in vtes.VTES.disciplines
                        ):
                            logger.warning('improper discipline "{}"', line)
                            return None, 0
            try:
                official_name = vtes.VTES.get_name(name)
                if name == "raven" and official_name == "Camille Devereux, The Raven":
                    self.deck.raven = count
                name = official_name
            except KeyError:
                name, count = None, 0
        # do not match a card inside a marked multiline comment
        if (
            name
            and self.current_comment
            and self.current_comment.mark == Mark.MULTILINE
        ):
            logger.warning('discarded match "{}" inside comment "{}"', name, line)
            name, count = None, 0
        # do not match crypt tail expression on a library card
        if name and match.group("crypt_tail") and not vtes.VTES.is_crypt(name):
            name, count = None, 0
        # do not match post count on a crypt card
        if name and match.group("post_count") and vtes.VTES.is_crypt(name):
            name, count = None, 0
        # Too many preface comments parse like cards in the TWDA
        if twda and name and not self.separator:
            name, count = None, 0
        # if no card was found, the whole line is a comment
        # if a card was found, a comment might still be present as a suffix
        if name:
            comment = max(
                match.span("parenthesis_comment"),
                match.span("bracket_comment"),
                match.span("line_comment"),
            )
            # extract the original comment, not the "normalized" parsed version
            if comment > (-1, -1):
                comment = line[comment[0] : comment[1]]
            else:
                comment = ""
            mark = match.group("comment_mark") or ""
            if mark[:2] == "/*":
                if "*/" in line:
                    mark = Mark.LINE
                else:
                    mark = Mark.MULTILINE
            else:
                mark = Mark.LINE
        else:
            if not line or set(line).issubset(set("-=_0123456789")):
                comment = ""
                if twda and line and set(line).issubset(set("-=_")):
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
        self.comment(comment, card_name=name or None, mark=mark)
        self.preface = self.preface and not bool(name)
        return name, count

    def comment(self, comment: str, card_name: str = None, mark: Mark = None) -> None:
        """Handle a comment.

        Log if we suspect the potential comment to be a parsing error
        """
        if not (comment or self.current_comment):
            return
        if comment:
            comment = comment.rstrip()
        # warn on unmarked single line comments in the middle of the cards list:
        # they are candidates for parsing errors
        if (
            (card_name or not comment)
            and not self.preface
            and self.current_comment
            and not self.current_comment.multiline
            and not self.current_comment.mark
        ):
            logger.warning(
                'failed to parse "{}"',
                self.current_comment.log,
                extra={"line": (logger.extra.get("line") or 1) - 1},
            )
            self.current_comment = None
        # log unmarked multiline comments in the middle of the list
        # they happen a lot in the TWDA, but checking them may be needed
        if (
            (card_name or mark)
            and self.current_comment
            and self.current_comment.multiline
            and self.current_comment.mark != Mark.MULTILINE
            and not self.preface
        ):
            logger.debug(
                'unexpected multiline comment "{}"',
                self.current_comment.log,
                extra={"line": (logger.extra.get("line") or 1) - 1},
            )
        # if this is a new comment block, register the previous comment on the deck
        if self.current_comment and (
            mark == Mark.END
            or (
                (card_name or not self.preface)
                # if the comment is multiline and we did not parse a new card, continue
                and (card_name or not self.current_comment.mark == Mark.MULTILINE)
                # distinguish between a follow-up after a card comment and a new block
                and (
                    # a new card means a new comment
                    # an unparsed line (no card name) after non-multiline-marked comment
                    # on a card is also viewed as new comment (may be a parsing error)
                    (self.current_comment.card_name != card_name)
                    # a blank line after a card comment means a new comment
                    or (not comment and self.current_comment.card_name)
                )
            )
        ):
            if mark == Mark.END:
                self.current_comment += comment
                comment = None
            self.current_comment.finalize()
            if self.current_comment:
                current_card = self.current_comment.card_name
                if current_card:
                    self.deck.cards_comments[current_card] = str(self.current_comment)
                else:
                    # leave a blank line between separated comments
                    if self.deck.comments:
                        self.deck.comments += "\n"
                    self.deck.comments += str(self.current_comment) + "\n"
            self.current_comment = None
        # start a new comment if we have a non-blank line
        if comment and not self.current_comment:
            self.current_comment = Comment(card_name=card_name, mark=mark)
        # append the parsed comment, even if it is a blank line
        if comment or self.current_comment:
            self.current_comment += comment
        # do nothing on a blank line if we don't have a current comment
