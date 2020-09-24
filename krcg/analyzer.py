"""TWDA analyzer: compute cards affinity and build decks based on TWDA.
"""
import collections
import logging
from random import randrange

from . import deck
from . import vtes
from . import twda

logger = logging.getLogger()


class AnalysisError(Exception):
    pass


class Analyzer(object):
    """Used to analyze TWDA, find affinity between cards and build decks.

    The "affinity" is the number of decks where two cards are played together.

    Attributes:
        examples (dict): Selected example decks from TWDA
        played (dict): For each card, number of decks playing it at least once
        average (dict): For each card, average number of copies played
        variance (dict): For each card, variance of the number of copies played
        affinity (dict): For each card, dict of cards and their affinity (int)
        refresh_cursor (int): Card count for next refresh (when building deck)
        deck (deck.Deck): Deck being built
    """

    def __init__(self):
        self.examples = None
        self.played = None
        self.average = None
        self.variance = None
        self.affinity = None
        self.refresh_cursor = 0
        self.deck = None

    def build_deck(self, *args):
        """Build a deck, using optional card names as reference.

        The analyzer samples the TWDA and builds a deck similar to TWDs.
        It includes reference decks in the description.

        If no card name is given, a random first-tier card is chosen for seed.

        Args:
            *args (str): (opt.) card names as reference for deck building

        Returns:
            deck.Deck: The deck built
        """
        self.deck = deck.Deck(author="KRCG")
        self.refresh(*args, condition=vtes.VTES.is_crypt)
        # if no seed is given, choose one of the 100 most played cards,
        # but do not pick a spoiler (card played in more than 25% decks).
        if not args:
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
        """Sample TWDA. This is the core method of the Analyzer.

        Fetch `self.examples` decks from TWDA.

        If card names are given as args, only examples containing similar cards
        are selected as examples and `self.affinity` is computed for all given cards.

        Similarity is used to select example decks from TWDA, using Jaccard index.
        similarity=1 can be used to ensure all cards given as args must be present
        in the deck for it to be selected as an example.

        `self.average` of number played is computed for each example card.

        If `self.deck` has been created (e.g. by calling `build_deck`),
        `self.cards_left` is set using an average of examples.
        `self.refresh_cursor` is set to the number of cards to attain before
        a new refresh is required. It is quadratic, so refreshs happen
        in O(log) of cards count.

        Args:
            args: (opt.) card names, choose decks containing them
            similarity: (opt.) matching cards proportion for selection
            condition: (opt.) filter on card types, clans, etc.
        """
        reference = []
        if args:
            reference += [a for a in args]
        if self.deck:
            reference += list(self.deck.card_names(twda.TWDA.no_spoil))
        self.refresh_cursor = len(reference) * len(reference)
        # examples are similar (jaccard index > similarity) decks chosen from TWDA
        # spoilers (cards played in more than 25% decks) are not considered
        if reference:
            self.examples = {
                twda_id: example
                for twda_id, example in twda.TWDA.items()
                if len(
                    set(reference)
                    & set(
                        example.card_names(
                            lambda c: c in reference or twda.TWDA.no_spoil(c)
                        )
                    )
                )
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
        # compute average number played for each card
        self.average = collections.Counter()
        self.variance = collections.Counter()
        for example in self.examples.values():
            self.average.update(
                {
                    card: count / self.played[card]
                    for card, count in example.cards(condition)
                }
            )
        for example in self.examples.values():
            self.variance.update(
                {
                    card: pow(count - self.average[card], 2) / self.played[card]
                    for card, count in example.cards(condition)
                }
            )
        if self.deck is not None:
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

        Args:
            card (str): The card for which to refresh affinity
            condition (func): The conditional function candidates have to validate
        """
        for example in self.examples.values():
            if card not in example:
                continue
            self.affinity[card].update(
                {
                    friend: 1 / len(self.examples)
                    for friend, _ in example.cards(condition)
                }
            )

    def candidates(self, *args, no_filter=False):
        """Select candidates using `self.affinity`. Filter banned cards out.

        Args:
            *args (str): Reference cards
            limit: Maximum number of candidates to return

        Returns:
            list: List of (card, affinity_score) candidates by decreasing affinity
        """
        # score candidates by affinity
        candidates = collections.Counter()
        for card in args:
            candidates.update(
                {
                    candidate: score
                    for candidate, score in self.affinity.get(card, {}).items()
                    if no_filter
                    or not (vtes.VTES[candidate].get("Banned") or candidate in args)
                }
            )
        return candidates.most_common()

    def build_deck_part(self, *args, condition=None):
        """Build a deck part using given condition

        Condition is usually `VTES.is_crypt` or `VTES.is_library` but any
        condition on cards will work.

        Args:
            *args: cards already selected for the deck
            condition: condition on the next card to select
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
