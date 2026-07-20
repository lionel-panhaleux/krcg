"""Test the card references parsed from card text."""

import re

import pytest

from krcg import card_references
from krcg import collections
from krcg import models
from krcg.utils import string
from krcg.scripts import fix_csv


def test_references_resolve(cards: collections.CardDict) -> None:
    """Every marker left in a text names a card in `cards`, and never that card."""
    annotated = [c for c in cards.cards() if c.cards]
    assert annotated, "no card references parsed"
    index = card_references._index(cards)
    for card in cards.cards():
        for lang, text, references in [(None, card.text, card.cards)] + [
            (lang, t.text, t.cards) for lang, t in card.i18n.items()
        ]:
            marked = card_references.RE_CARD_REFERENCE.findall(text)
            assert len(set(marked)) == len(references), f"{card} ({lang}): {marked}"
            for name in marked:
                target = index[lang].get(string.normalize(name))
                assert target is not None, f"{card} ({lang}) marks unknown {name!r}"
                assert target.id != card.id, f"{card} ({lang}) references itself"
                assert target.id in {r.id for r in references}


def test_known_references(cards: collections.CardDict) -> None:
    """References from both sources: upstream markup and the fix_csv additions."""
    # upstream marks this one, on the Lost in Crowds side only
    assert [r.printed_name for r in cards["Lost in Crowds"].cards] == ["Into Thin Air"]
    assert "cards named <Into Thin Air>" in cards["Lost in Crowds"].text
    # ... so the reciprocal side comes from CARD_REFERENCES
    assert [r.printed_name for r in cards["Into Thin Air"].cards] == ["Lost in Crowds"]
    assert [r.printed_name for r in cards["Disengage"].cards] == [
        "Immortal Grapple",
        "Mighty Grapple",
    ]
    # the bare "Frenzy" is the card here; "Terror Frenzy" must survive it intact
    assert [r.printed_name for r in cards["Sire's Index Finger"].cards] == [
        "Brujah Frenzy",
        "Drawing Out the Beast",
        "Frenzy",
        "Rötschreck",
        "Terror Frenzy",
    ]
    # only the [MERGED] text names Helena, and a bare name means every printing,
    # so it resolves to the earliest — never to whichever difflib returned first
    assert not cards["Menele"].cards
    (helena,) = cards["Menele (ADV)"].cards
    assert helena.id == 200586
    assert [r.id for r in cards["Mithraic Cultist"].cards] == [201001]
    # a card naming itself is not a reference
    assert not cards["Ashur Tablets"].cards
    # "Frenzy cards" is the family, not the card
    assert not cards["Aleister Crowley"].cards


def test_fix_card_text_marks_references() -> None:
    """Upstream slashes become markers; the slash of 'and/or' is left alone."""
    row = fix_csv.fix_card_text(
        {
            "Id": "101125",
            "Name": "Lost in Crowds",
            "Card Text": "cards named /Into Thin Air/ and",
        }
    )
    assert row["Card Text"] == "cards named <Into Thin Air> and"
    row = fix_csv.fix_card_text(
        {"Id": "100039", "Name": "Alia", "Card Text": "basic Auspex and/or basic Obeah"}
    )
    assert row["Card Text"] == "basic Auspex and/or basic Obeah"
    row = fix_csv.fix_card_text(
        {
            "Id": "100554",
            "Name": "Disengage",
            "Card Text": "such as Immortal Grapple or Mighty Grapple)",
        }
    )
    assert row["Card Text"] == "such as <Immortal Grapple> or <Mighty Grapple>)"


def test_unknown_marker_does_not_fuzzy_match(cards: collections.CardDict) -> None:
    """A marker naming no card is dropped, not bound to its nearest neighbour."""
    card = cards["Anachronism"]
    card.cards.clear()
    text = card_references._resolve(
        card_references._index(cards)[None], card, None, "burn <the Path>", card.cards
    )
    assert text == "burn the Path"  # unwrapped, not bound to The Oath
    assert not card.cards


def test_translated_references(cards: collections.CardDict) -> None:
    """A translation names its target in its own language, and never itself."""
    card = cards["Preternatural Strength"]
    assert [r.printed_name for r in card.i18n[models.Lang.FR].cards] == [
        "Torn Signpost"
    ]
    assert "<Panneau arraché>" in card.i18n[models.Lang.FR].text
    assert [r.printed_name for r in card.i18n[models.Lang.ES].cards] == [
        "Torn Signpost"
    ]
    assert "<Poste arrancado>" in card.i18n[models.Lang.ES].text
    # the target is not translated, so the marker is unwrapped rather than left dangling
    assert not cards["Victor Donaldson"].i18n[models.Lang.FR].cards
    assert "<" not in cards["Victor Donaldson"].i18n[models.Lang.FR].text
    # a translation marks a card naming itself; unwrapped too
    assert not cards["Trap"].i18n[models.Lang.ES].cards


@pytest.mark.baseline
def test_translated_text_is_clean(cards: collections.CardDict) -> None:
    """The slash of 'et/ou' survives translation, as 'and/or' does in English."""
    assert "and/or" in cards["Alia, God's Messenger"].text
    slashed = [
        t.text
        for c in cards.cards()
        for t in c.i18n.values()
        if re.search(r"\w/\w", t.text)
    ]
    assert slashed, "no translated text kept an intra-word slash"
