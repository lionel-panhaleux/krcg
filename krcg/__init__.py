"""KRCG: VTES cards, rulings, and the Tournament Winning Decks Archive (TWDA).

VTES: Vampire: The Eternal Struggle.
TWDA: The Tournament Winning Decks Archive.
VEKN: The VTES Elder Kindred Network, the international players organization.

Load the cards library with `krcg.load()`; it returns a `collections.CardDict`
that looks cards up by id or name and runs searches. Load the deck archive with
`krcg.twda.load()`.

Modules:

- models.py: the data types (cards, decks, sets, rulings, enums).
- collections.py: `CardDict`, the cards library, with its search index.
- loader.py: load the cards library (`load` / `load_local` / `load_online`).
- twda.py: the Tournament Winning Decks Archive.
- vekn_csv.py: build cards from the packaged VEKN CSVs.
- rulings.py: parse the rulings data.
- parser.py: parse decklists from text.
- providers.py: fetch decks from external sites; serialize decks.
- analyzer.py: statistics over a deck collection (e.g. the TWDA).
- seating.py: tournament seating optimisation.
"""

from .loader import load, load_local, load_online

__all__ = ["load", "load_local", "load_online"]
