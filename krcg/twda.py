"""This module provides the `TWDA` singleton: Tournament Wining Decks Archive.

If it has not been initialized, TWDA will evaluate to False.
TWDA must be configured with `TWDA.configure()` before being used.
"""

import importlib.resources
import json
import logging
import msgspec.json

from . import models

logger = logging.getLogger("krcg")


DecksArchive = dict[str, models.Deck]


def load_twda() -> DecksArchive:
    """Load the TWDA from local data."""
    with importlib.resources.files("krcg.cards").joinpath("twda.json").open("rb") as f:
        return msgspec.json.decode(f.read(), type=DecksArchive)


TWDA = load_twda()
