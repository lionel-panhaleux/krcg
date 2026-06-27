"""Resolve a structured country from a TWDA place line."""

import logging

from . import models

logger = logging.getLogger("krcg")

# canonical country name -> (ISO 3166-1 alpha-2 code, continent)
_COUNTRIES: dict[str, tuple[str, models.Continent]] = {
    "Australia": ("AU", models.Continent.OCEANIA),
    "Austria": ("AT", models.Continent.EUROPE),
    "Belarus": ("BY", models.Continent.EUROPE),
    "Belgium": ("BE", models.Continent.EUROPE),
    "Brazil": ("BR", models.Continent.SOUTH_AMERICA),
    "Canada": ("CA", models.Continent.NORTH_AMERICA),
    "Chile": ("CL", models.Continent.SOUTH_AMERICA),
    "Croatia": ("HR", models.Continent.EUROPE),
    "Czech Republic": ("CZ", models.Continent.EUROPE),
    "Denmark": ("DK", models.Continent.EUROPE),
    "Finland": ("FI", models.Continent.EUROPE),
    "France": ("FR", models.Continent.EUROPE),
    "Germany": ("DE", models.Continent.EUROPE),
    "Greece": ("GR", models.Continent.EUROPE),
    "Hungary": ("HU", models.Continent.EUROPE),
    "Iceland": ("IS", models.Continent.EUROPE),
    "Ireland": ("IE", models.Continent.EUROPE),
    "Italy": ("IT", models.Continent.EUROPE),
    "Japan": ("JP", models.Continent.ASIA),
    "Lithuania": ("LT", models.Continent.EUROPE),
    "Mexico": ("MX", models.Continent.NORTH_AMERICA),
    "Netherlands": ("NL", models.Continent.EUROPE),
    "New Zealand": ("NZ", models.Continent.OCEANIA),
    "Norway": ("NO", models.Continent.EUROPE),
    "Philippines": ("PH", models.Continent.ASIA),
    "Poland": ("PL", models.Continent.EUROPE),
    "Portugal": ("PT", models.Continent.EUROPE),
    "Russia": ("RU", models.Continent.EUROPE),
    "Serbia": ("RS", models.Continent.EUROPE),
    "Singapore": ("SG", models.Continent.ASIA),
    "Slovakia": ("SK", models.Continent.EUROPE),
    "Slovenia": ("SI", models.Continent.EUROPE),
    "South Africa": ("ZA", models.Continent.AFRICA),
    "Spain": ("ES", models.Continent.EUROPE),
    "Sweden": ("SE", models.Continent.EUROPE),
    "Switzerland": ("CH", models.Continent.EUROPE),
    "United Kingdom": ("GB", models.Continent.EUROPE),
    "United States": ("US", models.Continent.NORTH_AMERICA),
}

# spelling variants seen in the TWDA (lower-cased) -> canonical name
_ALIASES: dict[str, str] = {
    "usa": "United States",
    "united states of america": "United States",
    "england": "United Kingdom",
    "scotland": "United Kingdom",
    "wales": "United Kingdom",
    "uk": "United Kingdom",
    "great britain": "United Kingdom",
    "czechia": "Czech Republic",
    "russian federation": "Russia",
}

_INDEX = {name.lower(): name for name in _COUNTRIES} | _ALIASES


def _norm(text: str) -> str:
    """Lower-case and collapse the whitespace of a place fragment."""
    return " ".join(text.lower().split())


def from_place(place: str) -> models.Country | None:
    """Resolve the country named in a place line's last comma-separated field.

    Args:
        place: A TWDA place header, e.g. ``"Galway, Ireland"`` or ``"Online"``.

    Returns:
        The matching country, or ``None`` when the place names no known country
        (online events, or an unrecognised spelling — logged as a warning).
    """
    tail = _norm(place.rsplit(",", 1)[-1])
    name = _INDEX.get(tail)
    if not name:
        # a few lists drop the comma ("Columbus OH USA"): match a trailing country
        words = tail.split()
        for size in range(min(3, len(words)), 0, -1):
            if name := _INDEX.get(" ".join(words[-size:])):
                break
    if not name:
        if tail and tail != "online":
            logger.warning("Unknown country in place: %s", place)
        return None
    code, continent = _COUNTRIES[name]
    flag = "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in code)
    return models.Country(name=name, code=code, flag=flag, continent=continent)
