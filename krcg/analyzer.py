"""Statistics and card affinity over a collection of decks (e.g. the TWDA).

A deck collection is treated as a statistical sample. ``played``, ``stats`` and
``affinity`` are read-only summaries; ``build_deck`` synthesizes a new TWDA-like
decklist from the sample. Cards are resolved through a loaded ``CardDict`` and
results are keyed by ``models.Card`` (``played(decks, cards)[cards["Villein"]]``).
"""

from collections.abc import Iterable, Iterator
import collections
import logging
import random

from . import models
from .collections import CardDict

logger = logging.getLogger("krcg")

Candidates = list[tuple[models.Card, float]]


class AnalysisError(Exception):
    """Raised when an analysis cannot be completed (e.g. an empty sample)."""


def _ranked(scores: dict[models.Card, float]) -> Candidates:
    """Sort a score map by decreasing value."""
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)


def _cards_in(
    deck: models.Deck, cards: CardDict, kind: models.Card.Kind | None = None
) -> Iterator[tuple[models.Card, int]]:
    """Yield (resolved card, count) for each deck entry of the given kind."""
    for entry in deck.cards:
        if kind and entry.kind != kind:
            continue
        card = cards.get(entry.id)
        if card:
            yield card, entry.count


def _spoilers(
    decks: list[models.Deck], cards: CardDict, threshold: float = 0.25
) -> dict[models.Card, float]:
    """Cards present in more than ``threshold`` of the decks, by frequency.

    Such cards carry little signal: affinity excludes nothing on their account
    but the deck builder avoids them as a seed and when measuring similarity.
    Samples of 50 decks or fewer yield none.
    """
    if len(decks) <= 50:
        return {}
    counts = collections.Counter(
        card for deck in decks for card, _ in _cards_in(deck, cards)
    )
    return {
        card: count / len(decks)
        for card, count in counts.items()
        if count > len(decks) * threshold
    }


def _similar(
    decks: list[models.Deck],
    cards: CardDict,
    reference: set[models.Card],
    similarity: float,
    spoilers: dict[models.Card, float],
) -> list[models.Deck]:
    """Decks playing at least ``similarity`` of the reference cards.

    Spoiler cards are ignored unless they are part of the reference.
    """
    if not reference:
        return list(decks)
    return [
        deck
        for deck in decks
        if len(
            reference
            & {
                card
                for card, _ in _cards_in(deck, cards)
                if card in reference or card not in spoilers
            }
        )
        / len(reference)
        >= similarity
    ]


def _affinity(
    examples: list[models.Deck],
    card: models.Card,
    cards: CardDict,
    kind: models.Card.Kind | None = None,
) -> dict[models.Card, float]:
    """Fraction of ``examples`` playing ``card`` that also play each other card."""
    ret: dict[models.Card, float] = collections.defaultdict(float)
    for example in examples:
        if not any(entry.id == card.id for entry in example.cards):
            continue
        for friend, _ in _cards_in(example, cards, kind):
            ret[friend] += 1 / len(examples)
    return ret


def _candidates(
    affinities: dict[models.Card, dict[models.Card, float]],
    references: Iterable[models.Card],
) -> Candidates:
    """Rank cards by summed affinity to the references, excluding them and bans."""
    references = list(references)
    exclude = set(references)
    scores: dict[models.Card, float] = collections.defaultdict(float)
    for card in references:
        for candidate, score in affinities.get(card, {}).items():
            if not (candidate.banned or candidate in exclude):
                scores[candidate] += score
    return _ranked(scores)


def played(
    decks: Iterable[models.Deck],
    cards: CardDict,
    kind: models.Card.Kind | None = None,
) -> collections.Counter[models.Card]:
    """Count how many of the decks play each card.

    Args:
        decks: The deck sample.
        cards: A loaded cards database.
        kind: Restrict to a card kind (crypt or library) if given.

    Returns:
        A counter of cards by number of decks playing them.
    """
    ret = collections.Counter[models.Card]()
    for deck in decks:
        ret.update(card for card, _ in _cards_in(deck, cards, kind))
    return ret


def stats(
    decks: Iterable[models.Deck],
    cards: CardDict,
    kind: models.Card.Kind | None = None,
) -> dict[models.Card, tuple[float, float]]:
    """Average and variance of the count played, per card.

    Both are measured over the decks that play the card; decks not playing it do
    not count as zeroes.

    Args:
        decks: The deck sample.
        cards: A loaded cards database.
        kind: Restrict to a card kind (crypt or library) if given.

    Returns:
        A mapping of card to (average, variance) of its played count.
    """
    decks = list(decks)
    count = played(decks, cards, kind)
    average: dict[models.Card, float] = collections.defaultdict(float)
    for deck in decks:
        for card, n in _cards_in(deck, cards, kind):
            average[card] += n / count[card]
    variance: dict[models.Card, float] = collections.defaultdict(float)
    for deck in decks:
        for card, n in _cards_in(deck, cards, kind):
            variance[card] += (n - average[card]) ** 2 / count[card]
    return {card: (average[card], variance[card]) for card in count}


def affinity(
    decks: Iterable[models.Deck],
    cards: CardDict,
    *reference: models.Card,
    similarity: float = 1.0,
    kind: models.Card.Kind | None = None,
) -> Candidates:
    """Rank cards by how often they share a deck with the reference cards.

    A deck is selected when it plays at least ``similarity`` of the reference
    cards (``similarity=1`` requires all of them). A candidate scores the
    fraction of selected decks that play it. Reference and banned cards are
    excluded.

    Args:
        decks: The deck sample.
        cards: A loaded cards database.
        *reference: The cards to find affinities for.
        similarity: Minimum fraction of reference cards a deck must play.
        kind: Restrict candidates to a card kind (crypt or library) if given.

    Returns:
        (card, score) pairs by decreasing affinity.
    """
    decks = list(decks)
    examples = _similar(
        decks, cards, set(reference), similarity, _spoilers(decks, cards)
    )
    scores: dict[models.Card, float] = collections.defaultdict(float)
    for card in reference:
        for friend, score in _affinity(examples, card, cards, kind).items():
            if not (friend.banned or friend in reference):
                scores[friend] += score
    return _ranked(scores)


def build_deck(
    decks: Iterable[models.Deck],
    cards: CardDict,
    *seeds: models.Card,
    similarity: float = 0.6,
) -> models.Deck:
    """Synthesize a TWDA-like deck from a deck sample.

    The sample is mined for decks similar to the cards selected so far, and the
    most affine card is added in turn, in a count averaged from those decks,
    until crypt then library reach sample-average sizes. Without seeds a random
    popular (non-spoiler) crypt card starts the build.

    Args:
        decks: The deck sample to mine (typically the TWDA).
        cards: A loaded cards database.
        *seeds: Optional cards to build around.
        similarity: Minimum fraction of the reference cards a deck must play to
            be used as an example.

    Returns:
        The synthesized deck.

    Raises:
        AnalysisError: If the sample yields no usable example deck.
    """
    decks = list(decks)
    spoilers = _spoilers(decks, cards)
    built = collections.Counter[models.Card]()
    examples: list[models.Deck] = []
    average: dict[models.Card, float] = collections.defaultdict(float)
    affinities: dict[models.Card, dict[models.Card, float]] = {}
    cursor = 0
    cards_left = 0

    def refresh(part_seeds: tuple[models.Card, ...], kind: models.Card.Kind) -> None:
        nonlocal examples, average, affinities, cursor, cards_left
        reference = set(part_seeds) | {c for c in built if c not in spoilers}
        cursor = len(reference) ** 2
        examples = _similar(decks, cards, reference, similarity, spoilers)
        if not examples:
            raise AnalysisError("no example deck in the sample")
        logger.info("refreshed examples (%d)", len(examples))
        affinities = {c: _affinity(examples, c, cards, kind) for c in reference}
        count = played(examples, cards, kind)
        average = collections.defaultdict(float)
        for example in examples:
            for card, n in _cards_in(example, cards, kind):
                average[card] += n / count[card]
        target = round(
            sum(sum(n for _, n in _cards_in(e, cards, kind)) for e in examples)
            / len(examples)
        )
        if kind == models.Card.Kind.LIBRARY:
            if target > 82:
                target = 90
            target = min(max(target, 60), 90)
        else:
            target = max(target, 12)
        cards_left = target - sum(n for c, n in built.items() if c.kind == kind)

    def build_part(part_seeds: tuple[models.Card, ...], kind: models.Card.Kind) -> None:
        nonlocal cards_left
        refresh(part_seeds, kind)
        while cards_left > 0:
            if len(built) >= cursor:
                refresh(part_seeds, kind)
                for card, n in list(built.items()):
                    if n != round(average[card]):
                        adjust = min(cards_left, round(average[card]) - n)
                        built[card] += adjust
                        cards_left -= adjust
                if cards_left <= 0:
                    break
            ranked = _candidates(affinities, built.keys() or part_seeds)
            if not ranked:
                logger.info("no more candidates")
                return
            next_card, score = ranked[0]
            logger.info("selected %s (%.2f)", next_card, score)
            n = min(cards_left, round(average[next_card]))
            built[next_card] += n
            cards_left -= n
            affinities[next_card] = _affinity(examples, next_card, cards, kind)

    chosen = seeds
    if not chosen:
        popular = [
            c
            for c, _ in played(decks, cards, models.Card.Kind.CRYPT).most_common()
            if c not in spoilers
        ]
        if not popular:
            raise AnalysisError("no crypt card in the sample")
        chosen = (popular[random.randrange(min(100, len(popular)))],)
        logger.info("seeded with %s", chosen[0])
    build_part(chosen, models.Card.Kind.CRYPT)
    build_part((), models.Card.Kind.LIBRARY)

    deck = models.Deck(author="KRCG")
    deck.cards = [models.CardInDeck.of(card, n) for card, n in built.items() if n > 0]
    deck.comment = "Inspired by:\n" + "\n".join(
        f" - {e.id:<20} {e.name or '(No Name)'}" for e in examples
    )
    return deck
