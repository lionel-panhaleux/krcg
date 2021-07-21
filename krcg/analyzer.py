"""TWDA analyzer: compute cards affinity and build decks based on TWDA.
"""
from typing import Callable, Iterable, List, Tuple
import collections
import itertools
import random

from . import deck
import logging

Candidates = List[Tuple[str, float]]

logger = logging.getLogger("krcg")


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

    def __init__(self, decks: Iterable, spoilers: bool = True):
        self.decks = decks
        if spoilers and len(self.decks) > 50:
            self.spoilers = {
                name: count / len(self.decks)
                for name, count in collections.Counter(
                    itertools.chain.from_iterable(d.keys() for d in self.decks)
                ).items()
                if count > len(self.decks) / 4
            }
            logger.debug("Spoilers: %s", self.spoilers)
        else:
            self.spoilers = {}
        self.examples = None
        self.played = None
        self.average = None
        self.variance = None
        self.affinity = None
        self.refresh_cursor = 0
        self.deck = None

    def build_deck(self, *args: str) -> deck.Deck:
        """Build a deck, using optional card names as reference.

        The analyzer samples the TWDA and builds a deck similar to TWDs.
        It includes reference decks in the description.

        If no card name is given, a random first-tier card is chosen for seed.

        Args:
            *args: card names as reference for deck building

        Returns:
            The deck built
        """
        self.deck = deck.Deck(author="KRCG")
        self.refresh(*args, condition=Analyzer.is_crypt)
        # if no seed is given, choose one of the 100 most played cards,
        # but do not pick a spoiler (card played in more than 25% decks).
        if not args:
            args = [
                [c for c, _ in self.played.most_common() if c not in self.spoilers][
                    random.randrange(100)
                ]
            ]
            logger.info("Randomly selected %s", args[0])
        # build crypt first, then library
        self.build_deck_part(*args, condition=Analyzer.is_crypt)
        self.refresh(condition=Analyzer.is_library)
        self.build_deck_part(condition=Analyzer.is_library)
        # add example decks reference in description
        self.deck.comments = "Inspired by:\n" + "\n".join(
            f" - {example.id:<20} {example.name or '(No Name)'}"
            for example in self.examples
        )
        return self.deck

    @staticmethod
    def is_crypt(card):
        return card.crypt

    @staticmethod
    def is_library(card):
        return card.library

    def refresh(
        self, *args, similarity: float = 0.6, condition: Callable = None
    ) -> None:
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
            args: card names, choose decks containing them
            similarity: matching cards proportion for selection
            condition: filter on card types, clans, etc.
        """
        if args:
            reference = set(args)
        else:
            reference = set()
        if self.deck:
            reference |= set(
                [
                    card
                    for card, _count in self.deck.cards(
                        lambda c: c not in self.spoilers
                    )
                ]
            )
        self.refresh_cursor = len(reference) * len(reference)
        # examples are similar (jaccard index > similarity) decks chosen from TWDA
        # spoilers (cards played in more than 25% decks) are not considered
        if reference:
            self.examples = [
                example
                for example in self.decks
                if len(
                    reference
                    & set(
                        [
                            card
                            for card, _count in example.cards(
                                lambda c: c in reference or c not in self.spoilers
                            )
                        ]
                    )
                )
                / len(reference)
                >= similarity
            ]
        else:
            self.examples = self.decks
        if not self.examples:
            logger.error("No example in TWDA")
            raise AnalysisError()
        logger.info("Refresh examples (%s)", len(self.examples))
        self.played = collections.Counter()
        for example in self.examples:
            self.played.update(card for card, _ in example.cards(condition))
        self.affinity = collections.defaultdict(collections.Counter)
        for card in reference:
            self.refresh_affinity(card, condition)
        # compute average number played for each card
        self.average = collections.Counter()
        self.variance = collections.Counter()
        for example in self.examples:
            self.average.update(
                {
                    card: count / self.played[card]
                    for card, count in example.cards(condition)
                }
            )
        for example in self.examples:
            self.variance.update(
                {
                    card: pow(count - self.average[card], 2) / self.played[card]
                    for card, count in example.cards(condition)
                }
            )
        if self.deck is not None:
            # compute number of cards left to find for this deck
            self.cards_left = round(
                sum(example.cards_count(condition) for example in self.examples)
                / len(self.examples)
            )
            # make sure cards_left count respects rules
            if condition == Analyzer.is_library:
                # averaging examples counts often get us close to 90 without
                # reaching it, so we push for it
                if self.cards_left > 82:
                    self.cards_left = 90
                self.cards_left = max(self.cards_left, 60)
                self.cards_left = min(self.cards_left, 90)
            if condition == Analyzer.is_crypt:
                self.cards_left = max(self.cards_left, 12)
            self.cards_left -= self.deck.cards_count(condition)

    def refresh_affinity(self, card: str, condition: Callable = None) -> None:
        """Add a card to `self.affinity` using current examples.

        Args:
            card: The card for which to refresh affinity
            condition: The conditional function candidates have to validate
        """
        self.affinity[card] = collections.Counter()
        for example in self.examples:
            if card not in example:
                continue
            self.affinity[card].update(
                {
                    friend: 1 / len(self.examples)
                    for friend, _ in example.cards(condition)
                }
            )

    def candidates(self, *args: str, spoiler_multiplier: float = 0) -> Candidates:
        """Select candidates using `self.affinity`. Filter banned cards out.

        Args:
            *args: Reference cards
            limit: Maximum number of candidates to return

        Returns:
            List of (card, affinity_score) candidates by decreasing affinity
        """
        # score candidates by affinity
        candidates = collections.Counter()
        for card in args:
            candidates.update(
                {
                    candidate: score / len(args)
                    for candidate, score in self.affinity.get(card, {}).items()
                    if not (
                        candidate.banned
                        or candidate in args
                        or score < self.spoilers.get(candidate, 0) * spoiler_multiplier
                    )
                }
            )
        return candidates.most_common()

    def build_deck_part(self, *args: str, condition: Callable = None) -> None:
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
                # adjust count of previously selected cards
                for card, count in list(self.deck.items()):
                    if count != round(self.average[card]):
                        # can be negative
                        adjust = min(self.cards_left, round(self.average[card]) - count)
                        self.deck[card] += adjust
                        self.cards_left -= adjust
                # refresh can change the number of cards left
                if self.cards_left <= 0:
                    break
            # score candidates by affinity
            candidates = self.candidates(*(self.deck.keys() or args))
            if not candidates:
                logger.info("No more candidates")
                return
            next_card, score = candidates[0]
            logger.info("Selected %s (%.2f)", next_card, score)
            count = min(self.cards_left, round(self.average[next_card]))
            self.deck.update({next_card: count})
            self.cards_left -= count
            self.refresh_affinity(next_card, condition)
