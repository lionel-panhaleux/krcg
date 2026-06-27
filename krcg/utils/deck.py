"""Deck utilities."""

from collections.abc import Generator
import itertools
import msgspec
import unicodedata
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
) -> Generator[tuple[str, list[models.CardInDeck]]]:
    """A generator that yields library cards sorted by type and name.

    Yields:
        Tuples of (type, list[(card, count)]).
    """
    library_cards = sorted(
        (c for c in deck.cards if c.kind == models.Card.Kind.LIBRARY),
        key=lambda a: (
            _type_index(a),
            # sort by the displayed VEKN name ("The Rack" files as "Rack, The")
            normalize(vekn_name(a)),
        ),
    )
    for kind, cards_ in itertools.groupby(library_cards, key=_type_index):
        # return a list so it can be iterated over multiple times
        yield TYPE_ORDER[kind], list(cards_)


def vekn_name(card: models.CardMinimal, ascii: bool = True) -> str:
    """Get the VEKN name of a card (for retrocompatibility with legacy tools).

    Args:
        card: The card.
        ascii: If True (default), fold the whole name to ASCII (what Lackey/JOL
            expect); pass False to keep accented letters and fold only symbols
            (e.g. ™, em-dash) — TWD fidelity, and keeps the name length-stable
            under normalize() so the parser's comment spans stay aligned.
    """
    if ascii:
        name = unidecode.unidecode(card.printed_name)
    else:
        name = "".join(
            ch
            if ch.isascii() or unicodedata.category(ch).startswith("L")
            # fold symbols only (e.g. ™ -> (TM)), upper-cased as the archive writes them
            else unidecode.unidecode(ch).upper()
            for ch in card.printed_name
        )
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
