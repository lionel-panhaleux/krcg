"""Rulings parsing.
"""

from typing import Generator, Tuple
import datetime
import re


ANKHA_SYMBOLS = {
    "abo": "w",
    "ani": "i",
    "aus": "a",
    "cel": "c",
    "chi": "k",
    "dai": "y",
    "dem": "e",
    "dom": "d",
    "for": "f",
    "mal": "<",
    "mel": "m",
    "myt": "x",
    "nec": "n",
    "obe": "b",
    "obf": "o",
    "obl": "ø",
    "obt": "$",
    "pot": "p",
    "pre": "r",
    "pro": "j",
    "qui": "q",
    "san": "g",
    "ser": "s",
    "spi": "z",
    "str": "+",
    "tem": "?",
    "thn": "h",
    "tha": "t",
    "val": "l",
    "vic": "v",
    "vis": "u",
    "ABO": "W",
    "ANI": "I",
    "AUS": "A",
    "CEL": "C",
    "CHI": "K",
    "DAI": "Y",
    "DEM": "E",
    "DOM": "D",
    "FOR": "F",
    "MAL": ">",
    "MEL": "M",
    "MYT": "X",
    "NEC": "N",
    "OBE": "B",
    "OBF": "O",
    "OBL": "Ø",
    "OBT": "£",
    "POT": "P",
    "PRE": "R",
    "PRO": "J",
    "QUI": "Q",
    "SAN": "G",
    "SER": "S",
    "SPI": "Z",
    "STR": "=",
    "TEM": "!",
    "THN": "H",
    "THA": "T",
    "VAL": "L",
    "VIC": "V",
    "VIS": "U",
    "viz": ")",
    "def": "@",
    "jud": "%",
    "inn": "#",
    "mar": "&",
    "ven": "(",
    "red": "*",
    "ACTION": "0",
    "POLITICAL ACTION": "2",
    "ALLY": "3",
    "RETAINER": "8",
    "EQUIPMENT": "5",
    "ACTION MODIFIER": "1",
    "REACTION": "7",
    "COMBAT": "4",
    "REFLEX": "6",
    "POWER": "§",
    "FLIGHT": "^",
    "MERGED": "µ",
    "CONVICTION": "¤",
}


RULING_AUTHORS = {
    "TOM": (
        "Thomas R Wylie",
        datetime.date.fromisoformat("1994-12-15"),
        datetime.date.fromisoformat("1996-07-29"),
    ),
    "SFC": (
        "Shawn F. Carnes",
        datetime.date.fromisoformat("1996-07-29"),
        datetime.date.fromisoformat("1996-10-18"),
    ),
    "JON": (
        "Jon Wilkie",
        datetime.date.fromisoformat("1996-10-18"),
        datetime.date.fromisoformat("1997-02-24"),
    ),
    "LSJ": (
        "L. Scott Johnson",
        datetime.date.fromisoformat("1997-02-24"),
        datetime.date.fromisoformat("2011-07-06"),
    ),
    "PIB": (
        "Pascal Bertrand",
        datetime.date.fromisoformat("2011-07-06"),
        datetime.date.fromisoformat("2016-12-04"),
    ),
    "ANK": ('Vincent "Ankha" Ripoll', datetime.date.fromisoformat("2016-12-04"), None),
    "RTR": ("Rules Team Ruling", None, None),
    "RBK": ("Rulebook", None, None),
}


RE_RULING_REFERENCE = re.compile(
    r"\[(?:" + r"|".join(RULING_AUTHORS) + r")\s[\w0-9-]+\]"
)
RE_SYMBOL = re.compile(r"\[(?:" + r"|".join(ANKHA_SYMBOLS) + r")\]")
RE_CARD = re.compile(r"{[^}]+}")


def parse_symbols(text: str) -> Generator[Tuple[str, str], None, None]:
    """Yield all symbols in the given text."""
    for symbol in RE_SYMBOL.findall(text):
        yield symbol, ANKHA_SYMBOLS[symbol[1:-1]]


def parse_cards(text: str) -> Generator[Tuple[str, str], None, None]:
    """Yield all cards in the given text."""
    for token in RE_CARD.findall(text):
        yield token, token[1:-1]


def parse_references(text: str) -> Generator[Tuple[str, str], None, None]:
    """Yield all references in the given text."""
    for reference in RE_RULING_REFERENCE.findall(text):
        yield reference, reference[1:-1]
