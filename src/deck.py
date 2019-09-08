"""Deck class: pickling and card access under conditions.
"""
import collections

import arrow
import arrow.parser


class Deck(collections.Counter):
    """A VTES deck, including meta information such as author and decription.

    Meta information:
        - name: Name of the deck
        - author: Deck author
        - comments: Comments on the deck
        - event: Event (for TWD)
        - place: Place where the event was held
        - date: Date on which the event was held
        - score: Score of the deck at the event
        - players_count: Count of players at the event
        - player: Player who played the deck
    """

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop("author", None)
        super().__init__(*args, **kwargs)
        self.event = None
        self.place = None
        self.date = None
        self.score = None
        self.players_count = 0
        self.player = None
        self.name = None
        self.comments = ""

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
            "score": self.score,
            "players_count": self.players_count,
            "player": self.player,
            "name": self.name,
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
        self.score = state.get("score")
        self.players_count = int(state.get("players_count", 0))
        self.player = state.get("player")
        self.name = state.get("name")
        self.comments = state.get("comments", "")
        self.update(state.get("cards", {}))

    def __reduce__(self):
        """For pickle serialization.
        """
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
        for card, count in self.cards(condition):
            yield card

    def cards_count(self, condition=None):
        """Card counts with an optional filter.

        Args:
            condition (func): (opt.) Condition each card must validate to be selected

        Returns:
            int: the count of all cards (matching the condition if any)
        """
        return sum(count for card, count in self.cards(condition))
