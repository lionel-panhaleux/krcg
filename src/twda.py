"""This module provides the `TWDA` singleton: Tournament Wining Decks Archive.

If it has not been initialized, TWDA will evaluate to False.
TWDA must be configured with `TWDA.configure()` before being used.
"""
import collections
import io
import itertools
import logging
import pickle
import re

import arrow
import arrow.parser
import requests

from . import config
from . import deck
from . import vtes

logger = logging.getLogger()


class AnalysisError(Exception):
    pass


# Headers used in TWDA, e.g. "Action modifiers/Combat cards total: (4)"
HEADERS = set()
HEADERS.update(config.HEADERS)
HEADERS.update([h + "s" for h in config.HEADERS] + ["ally", "allies"])
HEADERS.update(
    ["{}/{}".format(h1, h2) for h1, h2 in itertools.permutations(HEADERS, 2)]
)
HEADERS.update(config.ADDITIONAL_HEADERS)
HEADERS.update([h + " card" for h in HEADERS] + [h + " cards" for h in HEADERS])
HEADERS.update(["card", "cards", "deck"])
HEADERS.update([h + " total" for h in HEADERS])
HEADERS.update([h + ":" for h in HEADERS])


class _TWDA(collections.OrderedDict):
    """ An OrderedDict of the TWDA. Parsing TWDA.html is the hard part.

    Attributes:
        spoilers (set): cards played in over 25% of decks
        tail_re (str): regexp used to parse tail part of card line
    """

    def load_from_vekn(self, limit=None):
        """Load from vekn.net

        Args:
            limit: Maximum number of decks to load (used to speed up tests)
        """
        r = requests.request("GET", config.VEKN_TWDA_URL)
        self.load_html(io.StringIO(r.content.decode("utf-8")), limit)

    def load_html(self, source, limit=None):
        """Load from TWDA.html

        The TWDA is then pickled for future use, to avoid loading it too often.

        Args:
            source (file): The HTML
            limit: Maximum number of decks to load (used to speed up tests)
        """
        self.clear()
        # used to match a card even if a comment, discipline or clan has been added.
        self.tail_re = r"(?P<card_name>.+?)\s+(((\(|\[|-|/)(?P<comment>.+))|(({})\s*$))"
        self.tail_re = self.tail_re.format(
            "|".join(
                re.escape(s.lower())
                for s in vtes.VTES.clans + vtes.VTES.disciplines + ["trifle"]
            )
        )
        for count, (lines, twda_id) in enumerate(self._get_decks_html(source)):
            try:
                self[twda_id] = self._load_deck_html(lines, twda_id)
            except arrow.parser.ParserError as e:
                logger.error(e)
            if limit and count >= limit:
                break
        logger.info("TWDA loaded")
        pickle.dump(TWDA, open(config.TWDA_FILE, "wb"))

    def configure(self, date_from=None, date_to=None, min_players=0):
        """Prepare the TWDA, taking date and players count filters into account.

        Also compute `self.spoilers`.

        Args:
            date_from (datetime): filter out decks before this date
            date_to (datetime): filter out decks after this date
            min_players (int): if > 0, filter out decks with less players
        """
        if date_from:
            for key in [key for key, value in self.items() if value.date < date_from]:
                del self[key]
        if date_to:
            for key in [key for key, value in self.items() if value.date >= date_to]:
                del self[key]
        if min_players:
            for key in [
                key
                for key, value in self.items()
                if value.players_count and value.players_count < min_players
            ]:
                del self[key]
        if len(self) > 50:
            self.spoilers = {
                name
                for name, count in collections.Counter(
                    itertools.chain.from_iterable(d.keys() for d in self.values())
                ).items()
                if count > len(self) / 4
            }
            logger.debug("Spoilers: {}".format(self.spoilers))
        else:
            self.spoilers = {}

    def _get_decks_html(self, source):
        """Get lines for each deck, using HTML tags as separators.

        Args:
            source (file): HTML source file-like object implementing `readlines()`
        """
        lines = []
        for line_num, line in enumerate(source.readlines(), start=1):
            try:
                twda_id = re.match(r"^<a id=([^\s]*)\s", line).group(1)
            except AttributeError:
                pass
            if re.match(r"^<hr><pre>$", line):
                lines = []
            elif re.match(r"^</pre>", line):
                yield lines, twda_id
            else:
                lines.append((line_num, line[:-1]))

    @staticmethod
    def _assign_comment(separator, line_num, current_deck, comment, card):
        if not comment:
            return
        if card:
            current_deck.cards_comments[card["Name"]] = comment
            return
        # careful: many single lines inside decklist are undetected headers
        if separator and len(comment.strip("\n").split("\n")) < 2:
            comment = comment.strip("\n")
            logger.warning(f"[{line_num - 1}] failed to parse: {comment}")
        current_deck.comments += comment

    def _load_deck_html(self, lines, twda_id):
        """Parse TWDA.html lines to build a deck.

        Args:
            lines (list): lines of the deck as a list of `str`
            twda_id (str): the TWDA ID for this deck
        """
        current = deck.Deck()
        # First three lines are stable throughout TWDA
        current.event = lines[0][1]
        current.place = lines[1][1]
        current.date = arrow.get(lines[2][1], "MMMM Do YYYY")
        start = 3
        # tournament format and players count are not always set
        try:
            regexp = r"^(\d+R\+F)"
            current.tournament_format = re.match(regexp, lines[start][1]).group(1)
            start += 1
        except AttributeError:
            pass
        try:
            current.players_count = int(
                re.match(r"^(\d+)\s*player", lines[start][1]).group(1)
            )
            start += 1
        except AttributeError:
            pass
        # Player is always set, but after tournament format and count if any
        current.player = lines[start][1]
        start += 1
        # After this stable header, comments and format tricks happen
        current_comment = ""
        previous_comment = ""
        last_card = None
        separator = False
        for line_num, line in lines[start + 1 :]:
            if current_comment:
                previous_comment += current_comment.strip(" ()[]-/*") + "\n"
                current_comment = ""
            # remove misplaced spaces around punctuation for easy parsing
            line = line.strip()
            line = line.replace(" :", ":")
            line = line.replace("( ", "(")
            line = line.replace(" )", ")")
            line = line.replace(" /", "/")
            line = line.replace("/ ", "/")
            # blank lines are considered separation between comments blocks
            # so a comment after a block line is not affected to the previous card
            if not line:
                self._assign_comment(
                    separator, line_num, current, previous_comment, last_card
                )
                previous_comment = ""
                last_card = None
                continue
            # separtor lines ("---" or "===") are used to detect the beginning of the
            # actual deck list: this is the most reliable method as the "Crypt" word
            # can appear in deck comments.
            if line and set(line).issubset({"=", "-"}):
                separator = True
                continue
            # comments detection
            if "/*" in line:
                line, current_comment = line.split("/*", 1)
            if "*/" in current_comment:
                current_comment, tail = current_comment.split("*/", 1)
                line = line + tail
            if "*/" in line:
                current_comment, line = line.split("*/", 1)
            if line and line[0] == "[" and line[-1] == "]":
                current_comment += " " + line[1:-1].strip()
                line = ""
            # inline comments "--" or "//"
            # special case for "Bang Nakh -- Tiger's Claws"
            comment_re = (
                r"^(?P<line>.*?)\s*"
                r"(--|//)\s*"
                r"(?!(T|t)iger'?s? (C|c)laws?)"
                r"(?P<comment>.*?)\s*$"
            )
            match = re.match(comment_re, line)
            if match:
                line = match.group("line")
                current_comment += " " + match.group("comment")
            if not line:
                continue
            # if we did not hit any separator (e.g. "=============="),
            # try to find deck name, author and comments
            if not separator:
                try:
                    current.name = re.match(
                        r"^\s*(?:d|D)eck\s?(?:n|N)ame\s*:\s*(.*)$", line
                    ).group(1)
                    continue
                except AttributeError:
                    pass
                try:
                    current.author = re.match(
                        r"(?:(?:(?:c|C)reated)|(?:(?:d|D)eck))"
                        r"\s*(?:b|B)y\s*:?\s*(.*)$",
                        line,
                    ).group(1)
                    continue
                except AttributeError:
                    pass
                try:
                    line = re.match(
                        r"^(?:(?:d|D)eck)?"
                        r"\s*(?:(?:(?:d|D)escription)|(?:(?:n|N)otes?))\s*"
                        r":?\s*(.*)$",
                        line,
                    ).group(1)
                except AttributeError:
                    pass
                if not line:
                    continue
                # Do not consider the "Crypt" line as part of the comments or deck name
                if re.match(r"^(c|C)rypt", line):
                    continue
                # more often than not, first comment line is the deck name
                # they tend to be relatively short, though
                if not current.name and len(line) < 70:
                    current.name = line
                    continue
                # Anything else is considered a comment until a separator is hit
                current_comment += " " + line
                continue
            # lower all chars for easier parsing
            maybe_comment = ""
            name, count = _get_card(line.lower())
            if name and count:
                if name in HEADERS:
                    continue
                new_card = None
                try:
                    new_card = vtes.VTES[name]
                except KeyError:
                    match = re.match(self.tail_re, name)
                    if match:
                        name = match.group("card_name")
                        maybe_comment = match.group("comment")
                    try:
                        new_card = vtes.VTES[name]
                        logger.info(
                            f"[{line_num:<6}] fuzzy [{new_card['Name']}] - [{line}]"
                        )
                    except KeyError:
                        pass
                finally:
                    if new_card:
                        current.update({new_card["Name"]: count})
                        self._assign_comment(
                            separator, line_num, current, previous_comment, last_card
                        )
                        previous_comment = ""
                        last_card = new_card
                        if maybe_comment:
                            current_comment = maybe_comment + " " + current_comment
                    else:
                        # most common case: unidentified line is a continuation comment
                        current_comment += " " + line
            # should not happen: by default the whole line is captured by _get_card()
            else:
                current_comment += " " + line

        # tail comments
        if current_comment:
            previous_comment += current_comment.strip(" ()[]-/*") + "\n"
            current_comment = ""
            line_num += 1
        self._assign_comment(separator, line_num, current, previous_comment, last_card)

        # check deck composition rules
        library_count = current.cards_count(vtes.VTES.is_library)
        if library_count < 60:
            logger.warning(
                "[{:<6}] Deck #{} is missing library cards [{}]".format(
                    line_num, twda_id, current
                )
            )
        if library_count > 90:
            logger.warning(
                "[{:<6}] Deck #{} has too many cards [{}]".format(
                    line_num, twda_id, current
                )
            )
        if current.cards_count(vtes.VTES.is_crypt) < 12:
            logger.warning(
                "[{:<6}] Deck #{} is missing crypt cards [{}]".format(
                    line_num, twda_id, current
                )
            )
        return current

    def no_spoil(self, card):
        return not getattr(self, "spoilers", None) or card not in self.spoilers


def _get_card(line):
    """Find card name and count in a TWDA.html line

    There are a lot of circumvoluted cases to take into account, cf. tests.
    Capturing the card comments here has proven difficult,
    since comments take so many forms in TWDA.
    We just capture the whole line and try and extract the card number if possible.

    Args:
        line (str): Test line
    """
    card_match = re.match(
        # beginning of line, optional punctuation
        r"^\s*(-|_)?((x|X|\*|_)?\s*"
        # count
        # 2 digits maximum to avoid miscounting "419 Operation" and such
        # negative lookahead to avoid matching part of a card name (2nd, 3rd, 4th, ...)
        r"(?P<count>\d{1,2})(?!((st)|(nd)|(rd)|(th))))?"
        # optional punctuation
        r"\s*((x|X|-)\s)?\*?\s*"
        # non-greedy qualifier for card name, matches what the tail expression does not
        # special case for "channel 10" to avoid parsing 10x "channel".
        # "local 1111" and such are OK: we only consider 1 or 2 digits as valid count.
        r"(?P<name>((channel 10)|.+?))"
        # open parentheses for optional tail expression (separated for clarity)
        r"(("
        # mandatory punctuation (beware of "AK-47", "Kpist m/45", ...)
        r"((\s|\(|\[|\s/|:)+|\s=+)(-|x|\*|\s)*"
        # sometimes (old deck lists) count is after the card name
        # for vampires, this is the capacity of the vampire
        r"(?P<count_or_capacity>\d{1,2})"
        # negative lookahead to avoid matching part of a card name (2nd, 3rd, 4th, ...)
        # also ignore blood ("b") / pool ("p") cost sometimes indicated after card name
        # also special exception for "Pier 13, Port of Baltimore"
        r"(?!((st)|(nd)|(rd)|(th)|(.?\d)|b|p|(..?port)))"
        # closing parentheses for tail expression (separated for clarity)
        r")|(\.|,|\s)*$)",
        line,
    )
    if not card_match:
        return None, None
    name = card_match.group("name").strip()
    # when count is not given on the line, default to 1 (common in old deck lists)
    count = int(card_match.group("count") or card_match.group("count_or_capacity") or 1)
    return name, count


try:
    TWDA = pickle.load(open(config.TWDA_FILE, "rb"))
except (FileNotFoundError, EOFError):
    TWDA = _TWDA()  # evaluates to False as it is empty
