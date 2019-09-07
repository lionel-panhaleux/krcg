"""TWDA analyzer: compute cards affinity and build decks based on TWDA.
"""
import collections
import logging
from random import randrange

from . import config
from . import deck
from . import vtes
from . import twda

logger = logging.getLogger()


class AnalysisError(Exception):
    pass


class Analyzer(object):
    """Used to analyze TWDA, find affinity between cards and build decks.

    Usage:
    >>> # Create analyzer and refresh - optionally, reference cards can be given
    >>> A = Analyzer()
    >>> A.refresh()
    >>> # Get the number of decks playing any given card
    >>> A.played["Octopod"]
    5
    >>> # Get affinity for cards given as argument to refresh
    >>> # The score is the number of TWD playing these cards together
    >>> A.refresh("Octopod")
    >>> A.affinity["Octopod"].most_common()[0]
    ('Immortal Grapple', 5)
    >>> # Use similarity of 1 to get all decks matching the full card list
    >>> A.refresh("Octopod", "Ivory Bow", similarity=1)
    >>> len(A.examples)
    1
    """

    def __init__(self):
        self.examples = None  # dict of example decks from TWDA
        self.played = None  # number of decks playing each card
        self.average = None  # average number of exemplaries played
        self.affinity = None  # affinity score of cards relative to each card
        self.refresh_cursor = 0  # when to refresh next
        self.deck = None  # deck being build

    def build_deck(self, *args):
        """Build a deck, using optional card names as reference.

        The analyzer samples the TWDA and builds a deck similar to TWDs.
        It includes reference decks in the description.

        If no card name is given, a random first-tier card is chosen for seed.
        """
        self.deck = deck.Deck(author="Fame")
        self.refresh(*args, condition=vtes.VTES.is_crypt)
        if not args:
            # do not consider spoilers when choosing the seed
            args = [
                [
                    c
                    for c, _ in self.played.most_common()
                    if c not in twda.TWDA.spoilers
                ][randrange(100)]
            ]
            logger.info("Randomly selected {}".format(args[0]))
        # build crypt first, then library
        self.build_deck_part(*args, condition=vtes.VTES.is_crypt)
        self.refresh(condition=vtes.VTES.is_library)
        self.build_deck_part(condition=vtes.VTES.is_library)
        # add example decks reference in description
        self.deck.comments = "Inspired by:\n" + "\n".join(
            " - {:<20} {}".format(twda_id, example.name or "(No Name)")
            for twda_id, example in self.examples.items()
        )
        return self.deck

    def refresh(self, *args, similarity=0.6, condition=None):
        """Sample TWDA.

        Fetch `self.examples` from TWDA.
        If card names are given as args, only examples containing similar cards
        are selected as examples. `self.affinity` is computed for given cards.

        If `self.deck` has been created (e.g. by calling `build_deck`),
        `self.average` of number played is computed for each example card
        and `self.cards_left` is set using an average of examples.

        `self.refresh_cursor` is set to the number of cards to attain before
        a new refresh is required. It is quadratic, so refreshs happen
        in O(log) of cards count.

        Args:
            - args: (opt.) card names, choose decks containing them
            - similarity: (opt.) matching cards proportion for selection
            - condition: (opt.) filter on card types, clans, etc.
        """
        reference = []
        if args:
            reference += [a for a in args]
        if self.deck:
            reference += list(self.deck.card_names(twda.TWDA.no_spoil))
        self.refresh_cursor = len(reference) * len(reference)
        # examples are similar (jaccard) decks chosen from TWDA
        # spoilers (cards played in more than 25% decks) are not considered
        if reference:
            self.examples = {
                twda_id: example
                for twda_id, example in twda.TWDA.items()
                if len(set(reference) & set(example.card_names(twda.TWDA.no_spoil)))
                / len(reference)
                >= similarity
            }
        else:
            self.examples = twda.TWDA
        if not self.examples:
            logger.error("No example in TWDA")
            raise AnalysisError()
        logger.info("Refresh examples ({})".format(len(self.examples)))
        self.played = collections.Counter()
        for example in self.examples.values():
            self.played.update(card for card, _ in example.cards(condition))
        self.affinity = collections.defaultdict(collections.Counter)
        for card in reference:
            self.refresh_affinity(card, condition)

        if self.deck is not None:
            # compute average number played for each card
            self.average = collections.Counter()
            for example in self.examples.values():
                self.average.update(
                    {
                        card: count / self.played[card]
                        for card, count in example.cards(condition)
                    }
                )
            # compute number of cards left to find for this deck
            self.cards_left = round(
                sum(
                    example.cards_count(condition) for example in self.examples.values()
                )
                / len(self.examples)
            )
            # make sure cards_left count respects rules
            if condition == vtes.VTES.is_library:
                # averaging examples counts often get us close to 90 without
                # reaching it, so we push for it
                if self.cards_left > 82:
                    self.cards_left = 90
                self.cards_left = max(self.cards_left, 60)
                self.cards_left = min(self.cards_left, 90)
            if condition == vtes.VTES.is_crypt:
                self.cards_left = max(self.cards_left, 12)
            self.cards_left -= self.deck.cards_count(condition)

    def refresh_affinity(self, card, condition=None):
        """Add a card to `self.affinity` using current examples.
        """
        for example in self.examples.values():
            if card not in example:
                continue
            self.affinity[card].update(
                friend for friend, _ in example.cards(condition) if friend != card
            )

    def candidates(self, *args):
        """Select candidates using `self.affinity`. Filter banned cards out.
        """
        # score candidates by affinity
        candidates = collections.Counter()
        for card in args:
            candidates.update(
                {
                    candidate: score
                    for candidate, score in self.affinity.get(card, {}).items()
                    if not (candidate in config.BANNED or candidate in args)
                }
            )
        return candidates.most_common()

    def build_deck_part(self, *args, condition=None):
        """Build a deck part using given condition

        Condition is usually `VTES.is_crypt` or `VTES.is_library` nut any
        condition on cards will work.
        """
        while self.cards_left > 0:
            if len(self.deck) >= self.refresh_cursor:
                self.refresh(*args, condition=condition)
                # refresh can change the number of cards left
                if self.cards_left <= 0:
                    break
            # score candidates by affinity
            candidates = self.candidates(*(self.deck.keys() or args))
            if not candidates:
                logger.info("No more candidates")
                return
            next_card, score = candidates[0]
            logger.info("Selected {} ({:.2f})".format(next_card, score))
            count = min(self.cards_left, round(self.average[next_card]))
            self.deck.update({next_card: count})
            self.cards_left -= count
            self.refresh_affinity(next_card, condition)
