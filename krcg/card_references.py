"""Cards named in other cards' card text.

Upstream marks a referenced name with slashes ("cards named /Choir/"), which is
ambiguous with the slash of "and/or"; `scripts/fix_csv.py` resolves that at sync
time and rewrites every reference as `<Card Name>`. The marker stays in the text,
as `{Card Name}` does in a ruling, so a reader knows where each name sits; a
marker that resolves to nothing is unwrapped, so every one left names a card in
`cards`.
"""

import logging
import re

from . import collections
from . import models
from .utils import string

logger = logging.getLogger("krcg")

RE_CARD_REFERENCE = re.compile(r"<([^<>\n]+)>")


def load(cards: collections.CardDict) -> None:
    """Resolve the `<Card Name>` markers of every card text, in every language."""
    index = _index(cards)
    for card in cards.cards():
        card.text = _resolve(index[None], card, None, card.text, card.cards)
        for lang, translation in card.i18n.items():
            translation.text = _resolve(
                index.get(lang, {}), card, lang, translation.text, translation.cards
            )


def _index(
    cards: collections.CardDict,
) -> dict[models.Lang | None, dict[str, models.Card]]:
    """Map every name to a card, per language (`None` being English).

    Not `CardDict`, which fuzzy-matches: a marker that names no card must fail
    rather than bind to its nearest neighbour. A bare vampire name covers every
    printing (Mithras, Victoria Ash), so the earliest one is the target.
    """
    index: dict[models.Lang | None, dict[str, models.Card]] = {None: {}}
    for card in cards.cards():
        for name in (card.printed_name, card.unique_name, card.full_name):
            _add(index[None], name, card)
        for lang, translation in card.i18n.items():
            _add(index.setdefault(lang, {}), translation.name, card)
    return index


def _add(index: dict[str, models.Card], name: str, card: models.Card) -> None:
    """Index a card name, earliest printing winning."""
    key = string.normalize(name)
    if key not in index or card.id < index[key].id:
        index[key] = card


def _resolve(
    index: dict[str, models.Card],
    card: models.Card,
    lang: models.Lang | None,
    text: str,
    references: list[models.CardMinimal],
) -> str:
    """Append the cards named in `text` and return it with dead markers unwrapped."""
    seen: set[int] = set()
    dead: set[str] = set()
    for name in dict.fromkeys(RE_CARD_REFERENCE.findall(text)):
        target = index.get(string.normalize(name))
        if target is None:
            # a translation can name a card that language does not translate yet
            logger.log(
                logging.DEBUG if lang else logging.WARNING,
                "%s (%s) references unknown card %s",
                card,
                lang or "en",
                name,
            )
            dead.add(name)
        elif target.id == card.id:
            # a translation marks a card naming itself; that is not a reference
            dead.add(name)
        elif target.id not in seen:
            seen.add(target.id)
            references.append(models.CardMinimal.from_card(target))
    if dead:
        text = RE_CARD_REFERENCE.sub(
            lambda m: m.group(1) if m.group(1) in dead else m.group(0), text
        )
    return text
