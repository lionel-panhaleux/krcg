"""Deck utilities."""

from typing import Generator
import arrow
import itertools
import msgspec
import unidecode

from .. import models
from .string import normalize


#: type order for deck display
TYPE_ORDER = [
    "Master",
    "Conviction",
    "Action",
    "Action/Combat",
    "Action/Reaction",
    "Ally",
    "Equipment",
    "Political Action",
    "Retainer",
    "Power",
    "Action Modifier",
    "Action Modifier/Combat",
    "Action Modifier/Reaction",
    "Reaction",
    "Combat",
    "Combat/Reaction",
    "Event",
]


def _type_index(card: models.CardInDeck) -> int:
    return TYPE_ORDER.index("/".join(sorted(card.types)))


def sorted_library(
    deck: models.Deck,
) -> Generator[tuple[str, list[models.CardInDeck]], None, None]:
    """A generator that yields library cards sorted by type and name.

    Yields:
        Tuples of (type, list[(card, count)]).
    """
    library_cards = sorted(
        (c for c in deck.cards if c.kind == models.Card.Kind.LIBRARY),
        key=lambda a: (
            _type_index(a),
            normalize(a.filing_name),
        ),
    )
    for kind, cards_ in itertools.groupby(library_cards, key=_type_index):
        # return a list so it can be iterated over multiple times
        yield TYPE_ORDER[kind], list(cards_)


def vekn_name(card: models.CardMinimal) -> str:
    """Get the VEKN name of a card (for retrocompatibility with legacy tools)."""
    name = unidecode.unidecode(card.printed_name)
    if name.startswith("The "):
        name = name[4:] + ", The"
    if card.unicity_suffix:
        name += f" ({card.unicity_suffix})"
    return name


def sorted_crypt(deck: models.Deck) -> list[models.CardInDeck]:
    """For convenience, list of crypt cards."""
    return sorted(
        (c for c in deck.cards if c.kind == models.Card.Kind.CRYPT),
        key=lambda c: (c.count, vekn_name(c)),
    )


def to_txt(deck: models.Deck) -> str:
    """Serialize a deck to TWD-like format, without card database info."""
    lines = []
    if deck.event and deck.event.name:
        lines.append(deck.event.name)
    if deck.event and deck.event.place:
        lines.append(deck.event.place)
    if deck.event and deck.event.date:
        lines.append(arrow.get(deck.event.date).format("MMMM Do YYYY"))
    if deck.event and deck.event.format:
        lines.append(deck.event.format)
    if deck.event and deck.event.players_count:
        lines.append(f"{deck.event.players_count} players")
    if deck.player:
        lines.append(deck.player)
    if deck.event and deck.event.url:
        lines.append(deck.event.url)
    if lines:
        lines.append("")
    if deck.score:
        lines.append(f"-- {deck.score}")
        lines.append("")
    if deck.name:
        lines.append(f"Deck Name: {deck.name}")
    if deck.author:
        lines.append(f"Created by: {deck.author}")
    if deck.comment:
        if deck.name or deck.author:
            lines.append("")
        lines.append(deck.comment)
    elif lines and lines[-1] != "":
        lines.append("")
    crypt = sorted_crypt(deck)
    lines.append(f"Crypt ({sum(c.count for c in crypt)} cards)")
    lines.append("-" * len(lines[-1]))
    max_name = max(len(card.unique_name) for card in crypt) + 1
    for card, count in crypt:
        lines.append(f"{card.count}x {card.unique_name:<{max_name}}")
    library_count = sum(
        c.count for c in deck.cards if c.kind == models.Card.Kind.LIBRARY
    )
    lines.append(f"\nLibrary ({library_count} cards)")
    # form a section for each type with a header displaying the total
    for i, (type_, cards_) in enumerate(sorted_library(deck)):
        cr = "\n" if i > 0 else ""
        lines.append(f"{cr}{type_} ({sum(count for _, count in cards_)})")
        for card in cards_:
            if card.comment:
                comment = card.comment.replace("\n", " ").strip()
                lines.append(f"{count}x {card.unique_name:<23} -- {comment}")
            else:
                lines.append(f"{count}x {card.unique_name}")
    return "\n".join(lines)


def add_card(
    deck: models.Deck, card: models.Card, count: int = 1, comment: str = ""
) -> None:
    """Add a card to the deck."""
    deck.cards.append(
        msgspec.convert(
            msgspec.to_builtins(card) | {"count": count, "comment": comment},
            models.CardInDeck,
        )
    )


def sort_cards(deck: models.Deck) -> None:
    """Sort the cards in the deck."""
    deck.cards.sort(key=lambda c: (c.kind, normalize(c.filing_name)))
