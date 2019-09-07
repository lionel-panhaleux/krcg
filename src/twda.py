"""This module provides the `TWDA` singleton: Tournament Wining Decks Archive.

If it has not been initialized, TWDA will evaluate to False.
TWDA must be configured with `TWDA.configure()` before being used.
"""
import collections
import itertools
import logging
import pickle
import re

import arrow
from arrow.parser import ParserError

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
    """

    def load_html(self, source, binary=False):
        """Load from TWDA.html
        """
        for lines, twda_id in self._get_decks_html(source, binary):
            try:
                self[twda_id] = self._load_deck_html(lines, twda_id)
            except ParserError as e:
                logger.error(e)
        logger.info("TWDA loaded")
        pickle.dump(TWDA, open(config.TWDA_FILE, "wb"))

    def configure(self, date_from=None, date_to=None, min_players=0):
        """Compute `self.spoilers`: cards played in over 25% of decks
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

    def _get_decks_html(self, source, binary):
        """Get lines for each deck, using HTML tags as separators.
        """
        lines = []
        for line_num, line in enumerate(source.readlines(), start=1):
            if binary:
                line = line.decode("utf-8")
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

    def _load_deck_html(self, lines, twda_id):
        """Parse TWDA.html lines to build a deck.
        """
        current = deck.Deck()
        headers = False
        # First three lines are stable throughout TWDA
        current.event = lines[0][1]
        current.place = lines[1][1]
        current.date = arrow.get(lines[2][1], "MMMM Do YYYY")
        start = 3
        # Score and players count are not always set
        try:
            current.score = re.match(r"^(\d+)R\+F", lines[start][1]).group(1)
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
        # Player is always set, but after score and count if any
        current.player = lines[start][1]
        start += 1
        # After this header, comments and format tricks happen
        comment = None
        for line_num, line in lines[start + 1 :]:
            # handle C-style multiline comments (very common) /* comment */
            if "*/" in line:
                comment = None
                continue
            if comment:
                continue
            if "/*" in line:
                line, comment = line.split("/*")
                if comment and "*/" in comment:
                    comment = None
                else:
                    comment = True
            if not line:
                continue
            # handle separtor lines
            if set(line).issubset({"=", "-"}):
                headers = True
                continue
            # monoline [comment] is also common
            if line[0] == "[" and line[-1] == "]":
                continue
            # "meaningful content -- comment" is widespread
            line = line.split("--", 1)[0]
            # as is C-style "meaningful content //comment"
            line = line.split("//", 1)[0]
            # remove misplaced spaces around punctuation for easy parsing
            line = line.replace(" :", ":")
            line = line.replace("( ", "(")
            line = line.replace(" )", ")")
            line = line.replace(" /", "/")
            line = line.replace("/ ", "/")
            # at this point we may not have a meaningful line anymore
            if not line:
                continue
            # if we did not hit any header (e.g. "Crypt"), try to find
            # deck name, author and comments
            if not headers:
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
                # if we hit the "Crypt" marker, deck list is beginning
                if not re.match(r"^(c|C)rypt", line):
                    # more often than not, first comment line is the deck name
                    # they tend to be relatively short, though
                    if not current.name and len(line) < 70:
                        current.name = line
                        continue
                    current.comments += line + "\n"
                    continue
            # lower all chars for easier parsing
            line = line.lower()
            name, count = _get_card(line)
            if name and count:
                if name.startswith("<a "):
                    continue
                if name in HEADERS:
                    continue
                if not headers and not current:
                    continue
                try:
                    card = vtes.VTES[name]
                except KeyError:
                    logger.error(
                        "[{:<6}] unknown card [{}] - [{}]".format(line_num, name, line)
                    )
                    continue
                current.update({card["Name"]: count})
            else:
                logger.error("[{:<6}] no card matched [{}]".format(line_num, line))
        library_count = current.cards_count(vtes.VTES.is_library)
        if library_count < 60:
            logger.info(
                "[{:<6}] Deck #{} is missing library cards [{}]".format(
                    line_num, twda_id, current
                )
            )
        if library_count > 90:
            logger.info(
                "[{:<6}] Deck #{} has too many cards [{}]".format(
                    line_num, twda_id, current
                )
            )
        if current.cards_count(vtes.VTES.is_crypt) < 12:
            logger.info(
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
    """
    card_match = re.match(
        r"^\s*(?:-|_)?(?:(?:x|X|\*|_)?\s*"
        r"(?P<count>\d{1,2})(?!(?:(?:st)|(?:nd)|(?:rd)|(?:th))))?"
        r"\s*(?:(?:x|X|-)\s)?\*?\s*"
        r"(?P<name>(?:(?:channel 10)|.+?))"
        r"(?:(?:"
        r"(?:\s|\(|\[|:|/|=)+(?:-|x|\*|\s)*"
        r"(?P<count_or_cap>\d{1,3})"
        r"(?!(?:(?:st)|(?:nd)|(?:rd)|(?:th)|(?:.?\d)|b|p|(?:..?port)))"
        r")|$)",
        line,
    )
    if not card_match:
        return None, None
    name = card_match.group("name").strip()
    count = int(card_match.group("count") or card_match.group("count_or_cap") or 1)
    return name, count


try:
    TWDA = pickle.load(open(config.TWDA_FILE, "rb"))
except (FileNotFoundError, EOFError):
    TWDA = _TWDA()  # evaluates to False as it is empty
