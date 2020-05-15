"""Deck class: pickling and card access under conditions."""
import collections
import logging

import arrow
import arrow.parser

logger = logging.getLogger()


class Deck(collections.Counter):
    """A VTES deck, including meta information such as author and decription.

    Meta information:
        - name: Name of the deck
        - author: Deck author
        - comments: Comments on the deck
        - event: Event (for TWD)
        - place: Place where the event was held
        - date: Date on which the event was held
        - tournament_format: Format of the event
        - players_count: Count of players at the event
        - player: Player who played the deck
    """

    def __init__(self, *args, **kwargs):
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

        # for comments parsing
        self.separator = False
        self.comment = None
        self.card_name = None
        self.line_num = None
        self.multiline = False
        self.marker = False

    def comment_begin(
        self, line_num, comment, card_name=None, multiline=False, marker=False
    ):
        if self.comment:
            self._assign_comment()
        self.line_num = line_num
        if not self.separator or marker:
            self.comment = comment.strip(" ")
        else:
            self.comment = comment.strip(" ()[]-/*")
        self.card_name = card_name
        self.multiline = multiline
        self.marker = marker

    def maybe_comment_line(self, line_num, comment, card_name=None):
        if self.comment:
            if self.separator:
                comment = comment.strip(" ()[]-/*")
            self.comment += "\n" + comment
        else:
            self.comment_begin(
                line_num,
                comment,
                card_name or self.card_name,
                not self.separator,
                not self.separator,
            )

    def comment_end(self):
        if self.comment:
            self._assign_comment()
        self.comment = None
        self.card_name = None
        self.line_num = None
        self.multiline = False
        self.marker = False

    def _assign_comment(self):
        self.comment = self.comment.strip("\n")
        if not self.comment:
            return
        log_version = self.comment.replace("\n", " ").strip()
        multiline = len(self.comment.split("\n")) > 1
        if not self.marker:
            if not multiline:
                logger.warning(f"[{self.line_num}] failed to parse [{log_version}]")
                return
            logger.debug(f"[{self.line_num}] unmarked comment [{log_version}]")
        if multiline and not self.multiline:
            logger.debug(
                f"[{self.line_num}] unexpected multiline comment [{log_version}]"
            )
        comment = self.comment + "\n"
        if self.card_name:
            self.cards_comments[self.card_name] = comment
            return
        if self.comments:
            self.comments += "\n"
        self.comments += comment

    def __getstate__(self):
        """For pickle serialization.

        Deck inherits `dict` and its special handling of pickle.
        """
        return {
            "cards": collections.OrderedDict(self.cards()),
            "author": self.author,
            "event": self.event,
            "place": self.place,
            "date": self.date.format("MMMM Do YYYY") if self.date else None,
            "tournament_format": self.tournament_format,
            "score": self.score,
            "players_count": self.players_count,
            "player": self.player,
            "event_link": self.event_link,
            "name": self.name,
            "cards_comments": self.cards_comments,
            "comments": self.comments,
        }

    def __setstate__(self, state):
        """For pickle deserialization.
        """
        self.author = state.get("author")
        self.event = state.get("event")
        self.place = state.get("place")
        try:
            self.date = arrow.get(state.get("date"), "MMMM Do YYYY")
        except arrow.parser.ParserError:
            pass
        self.tournament_format = state.get("tournament_format")
        self.score = state.get("score")
        self.players_count = int(state.get("players_count", 0))
        self.player = state.get("player")
        self.event_link = state.get("event_link")
        self.name = state.get("name")
        self.comments = state.get("comments", "")
        self.cards_comments = state.get("cards_comments", {})
        self.update(state.get("cards", {}))

    def __reduce__(self):
        """For pickle serialization."""
        return (Deck, (), self.__getstate__())

    def __str__(self):
        return self.name or "(No Name)"

    def cards(self, condition=None):
        """Generator yielding (card_name, count), with an optional filter.

        Args:
            condition (func): (opt.) Condition each card must validate to be selected

        Yields:
            card, count (str, int)
        """
        for card, count in self.items():
            if condition and not condition(card):
                continue
            yield card, count

    def card_names(self, condition=None):
        """Generator yielding card names with an optional filter.

        Args:
            condition (func): (opt.) Condition each card must validate to be selected

        Yields:
            card (str)
        """
        for card, _count in self.cards(condition):
            yield card

    def cards_count(self, condition=None):
        """Card counts with an optional filter.

        Args:
            condition (func): (opt.) Condition each card must validate to be selected

        Returns:
            int: the count of all cards (matching the condition if any)
        """
        return sum(count for _card, count in self.cards(condition))
