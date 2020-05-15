"""This module provides the `TWDA` singleton: Tournament Wining Decks Archive.

If it has not been initialized, TWDA will evaluate to False.
TWDA must be configured with `TWDA.configure()` before being used.
"""
import collections
import io
import itertools
import logging
import os
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
        spoilers (dict): cards played in over 25% of decks
        tail_re (str): regexp used to parse tail part of card line
    """

    def load_from_vekn(self, limit=None, save=True):
        """Load from vekn.net

        Args:
            limit: Maximum number of decks to load (used to speed up tests)
        """
        r = requests.request("GET", config.VEKN_TWDA_URL)
        r.raise_for_status()
        self.load_html(io.StringIO(r.content.decode("utf-8")), limit, save)

    def load_html(self, source, limit=None, save=True):
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
        for count, (lines, twda_id) in enumerate(self._get_decks_html(source), 1):
            try:
                self[twda_id] = self._load_deck_html(lines, twda_id)
            except arrow.parser.ParserError as e:
                logger.error(e)
            if limit and count >= limit:
                break
        logger.info("TWDA loaded")
        if save:
            pickle.dump(TWDA, open(config.TWDA_FILE, "wb"))

    def configure(self, date_from=None, date_to=None, min_players=0, spoilers=True):
        """Prepare the TWDA, taking date and players count filters into account.

        Also compute `self.spoilers`.

        Args:
            date_from (datetime): filter out decks before this date
            date_to (datetime): filter out decks after this date
            min_players (int): if > 0, filter out decks with less players
            spoilers (bool): if True, compute spoilers to filter them out for analysis
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
        if spoilers and len(self) > 50:
            self.spoilers = {
                name: count / len(self)
                for name, count in collections.Counter(
                    itertools.chain.from_iterable(d.keys() for d in self.values())
                ).items()
                if count > len(self) / 4
            }
            logger.debug("Spoilers: {}".format(self.spoilers))
        else:
            self.spoilers = {}

    @staticmethod
    def _get_decks_html(source):
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
            players_count = re.match(r"^(\d+|\?+)\s*player", lines[start][1]).group(1)
            start += 1
            current.players_count = int(players_count)
        except (AttributeError, ValueError):
            pass
        # Player is always set, but after tournament format and count if any
        current.player = lines[start][1]
        start += 1
        # Ignore Organizer line (rare inclusion)
        try:
            if re.match(r"^\s*(O|o)rgani(s|z)er", lines[start][1]):
                start += 1
        except AttributeError:
            pass
        # Newer lists provide an event link
        try:
            current.event_link = re.match(r"^(https?://.*)$", lines[start][1]).group(1)
            start += 1
        except AttributeError:
            pass
        # After this stable header, comments and format tricks happen
        for line_num, original_line in lines[start + 1 :]:
            # remove misplaced spaces around punctuation for easy parsing
            line = original_line.strip()
            line = line.replace(" :", ":")
            line = line.replace("( ", "(")
            line = line.replace(" )", ")")
            line = line.replace(" /", "/")
            line = line.replace("/ ", "/")
            if not line:
                current.comment_end()
                continue
            # separtor lines ("---" or "===") are used to detect the beginning of the
            # actual deck list: this is the most reliable method as the "Crypt" word
            # can appear in deck comments.
            if line and len(line) > 2 and set(line).issubset({"=", "-"}):
                current.comment_end()
                current.separator = True
                continue
            # if we did not hit any separator (e.g. "=============="),
            # try to find deck name, author and comments
            if not current.separator:
                if not current.score:
                    try:
                        score = re.match(
                            r"-?-?\s*((?P<round_wins>\d)\s*(G|g)(W|w)\s*"
                            r"(?P<round_vps>\d(\.|,)?\d?)\s*((v|V)(p|P))?\s*\+?\s*)?"
                            r"(?P<final>\d(\.|,)?\d?)\s*(v|V)(p|P)",
                            line,
                        )
                        if score.group("round_wins"):
                            current.score = "{}gw{} + {}vp in the final".format(
                                score.group("round_wins"),
                                score.group("round_vps"),
                                score.group("final"),
                            )
                        else:
                            current.score = "{}vp in the final".format(
                                score.group("final")
                            )
                        continue
                    except AttributeError:
                        pass
                if not current.name:
                    try:
                        current.name = re.match(
                            r"^\s*(?:(?:d|D)eck)?\s?(?:n|N)ame\s*:\s*(.*)$", line
                        ).group(1)
                        continue
                    except AttributeError:
                        pass
                if not current.author:
                    try:
                        current.author = re.match(
                            r"(?:(?:(?:(?:c|C)reated)|(?:(?:d|D)eck))"
                            r"\s*(?:b|B)y|(?:a|A)uthors?|(?:c|C)reators?)\s*:?\s*(.*)$",
                            line,
                        ).group(1)
                        continue
                    except AttributeError:
                        pass
                if not line:
                    continue
                # Do not consider the "Crypt" line as part of the comments
                if re.match(r"^(c|C)rypt", line):
                    continue
                # Anything else is considered a comment until a separator is hit
                current.maybe_comment_line(line_num, original_line)
                continue

            # comments detection
            # wait for card identification for all trailing comments
            comment = ""
            multiline = False
            if "/*" in line:
                line, comment = line.split("/*", 1)
                multiline = True
            if "*/" in comment:
                comment, tail = comment.split("*/", 1)
                line = line + tail
                multiline = False
            if "*/" in line:
                comment_tail, line = line.split("*/", 1)
                current.maybe_comment_line(line_num, comment_tail)
                current.comment_end()
            if line and line[0] in "([/" and line[-1] in "/])":
                current.comment_begin(line_num, " " + line[1:-1].strip(), marker=True)
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
                comment = match.group("comment")
            if not line:
                if comment:
                    current.comment_begin(
                        line_num, comment, marker=True, multiline=multiline
                    )
                continue
            # lower all chars for easier parsing
            name, count, explicit = _get_card(line.lower())
            if name and count:
                if name in HEADERS:
                    # discard comment on header line (most likely card count)
                    continue
                if not explicit and name in set(
                    a.lower() for a in vtes.VTES.clans + vtes.VTES.disciplines
                ):
                    logger.warning(f"[{line_num}] improper discipline [{line}]")
                    continue
                card = None
                try:
                    card = vtes.VTES[name]
                except KeyError:
                    match = re.match(self.tail_re, name)
                    if match:
                        name = match.group("card_name")
                        tail = match.group("comment")
                        if comment and tail:
                            comment += " "
                        if tail:
                            comment += tail.rstrip(" )]-/\\")
                    try:
                        card = vtes.VTES[name]
                        logger.info(
                            f"[{line_num:<6}] fuzzy [{card['Name']}] - [{line}]"
                        )
                    except KeyError:
                        pass
                finally:
                    if card:
                        name = vtes.VTES.get_name(card)
                        current.update({name: count})
                        if comment:
                            current.comment_begin(
                                line_num,
                                comment,
                                name,
                                marker=True,
                                multiline=multiline,
                            )
                        else:
                            # if no blank line, comments on following lines are
                            # attached to his card
                            current.comment_begin(line_num, "", name)
                    else:
                        current.maybe_comment_line(line_num, line)
            # should not happen: by default the whole line is captured by _get_card()
            else:
                current.maybe_comment_line(line_num, line)

        current.comment_end()
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
    Returns:
        name (str): name of the card
        count (int): number of exemplaries
        explicit (bool): if False, count was not explicit
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
        r"((\s|\(|\[|\s/|:)+|\s=+)(?P<post_count_symbol>-|x|\*|\s)*"
        # sometimes (old deck lists) count is after the card name
        # for vampires, this is the capacity of the vampire
        r"(?P<count_or_capacity>\d{1,2})"
        # negative lookahead to avoid matching part of a card name (2nd, 3rd, 4th, ...)
        # also ignore blood ("b") / pool ("p") cost sometimes indicated after card name
        # also special exception for "Pier 13, Port of Baltimore"
        r"(?!((st)|(nd)|(rd)|(th)|(.?\d)|b|p|(..?port)))"
        # closing parentheses for tail expression (separated for clarity)
        r")|\s*$)",
        line,
    )
    if not card_match:
        return None, None, False
    name = card_match.group("name").strip()
    # when count is not given on the line, default to 1 (common in old deck lists)
    count = int(card_match.group("count") or 0)
    explicit = True
    if not count:
        count = int(card_match.group("count_or_capacity") or 1)
        if not card_match.group("post_count_symbol"):
            explicit = False
    return name, count, explicit


try:
    if not os.path.exists(config.TWDA_FILE) or os.stat(config.TWDA_FILE).st_size == 0:
        raise FileNotFoundError(config.TWDA_FILE)
    TWDA = pickle.load(open(config.TWDA_FILE, "rb"))
except (FileNotFoundError, EOFError):
    TWDA = _TWDA()  # evaluates to False as it is empty
