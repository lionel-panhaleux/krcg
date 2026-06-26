"""Rulings parsing."""

from __future__ import annotations

import collections.abc
import datetime
import importlib.resources
import re
import typing
import urllib.request

import yaml

from . import models
from .collections import CardDict

RULINGS_GITHUB = (
    "https://raw.githubusercontent.com/vtes-biased/vtes-rulings/main/rulings/"
)

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


def parse_symbols(text: str) -> collections.abc.Generator[tuple[str, str]]:
    """Yield all symbols in the given text."""
    for symbol in RE_SYMBOL.findall(text):
        yield symbol, ANKHA_SYMBOLS[symbol[1:-1]]


def parse_cards(text: str) -> collections.abc.Generator[tuple[str, str]]:
    """Yield all cards in the given text."""
    for token in RE_CARD.findall(text):
        yield token, token[1:-1]


def parse_references(text: str) -> collections.abc.Generator[tuple[str, str]]:
    """Yield all references in the given text."""
    for reference in RE_RULING_REFERENCE.findall(text):
        yield reference, reference[1:-1]


def load_local(cards: CardDict) -> None:
    """Load rulings from local files."""
    with (
        importlib.resources.files("krcg.cards")
        .joinpath("rulings.yaml")
        .open(encoding="utf-8") as rulings,
        importlib.resources.files("krcg.cards")
        .joinpath("groups.yaml")
        .open(encoding="utf-8") as groups,
        importlib.resources.files("krcg.cards")
        .joinpath("references.yaml")
        .open(encoding="utf-8") as references,
    ):
        load_from_files(cards, rulings, groups, references)


def load_online(cards: CardDict) -> None:
    """Load rulings from online repository."""
    try:
        rulings_f, _ = urllib.request.urlretrieve(RULINGS_GITHUB + "rulings.yaml")
        groups_f, _ = urllib.request.urlretrieve(RULINGS_GITHUB + "groups.yaml")
        ref_f, _ = urllib.request.urlretrieve(RULINGS_GITHUB + "references.yaml")
        with (
            open(rulings_f, encoding="utf-8") as rulings,
            open(groups_f, encoding="utf-8") as groups,
            open(ref_f, encoding="utf-8") as references,
        ):
            load_from_files(cards, rulings, groups, references)
    finally:
        urllib.request.urlcleanup()


def load_from_files(
    cards: CardDict,
    rulings_file: typing.IO[str],
    groups_file: typing.IO[str],
    references_file: typing.IO[str],
) -> None:
    """Load rulings from files."""
    all_rulings = yaml.safe_load(rulings_file)
    groups = yaml.safe_load(groups_file)
    references = yaml.safe_load(references_file)
    for nid, rulings_list in all_rulings.items():
        id_, name = nid.split("|")
        if id_.startswith("G"):
            # group ruling: applies to each member card, prefixed with its symbol
            members = [
                (cards[int(member.split("|")[0])], prefix, name)
                for member, prefix in groups[nid].items()
            ]
        else:
            members = [(cards[int(id_)], "", "")]
        for text in rulings_list:
            for card, prefix, group_name in members:
                ruling = _parse_text(cards, prefix + text, references)
                ruling.group = group_name
                card.rulings.append(ruling)


def _parse_text(
    cards: CardDict, text: str, references: dict[str, str]
) -> models.Ruling:
    """Parse the text of a ruling."""
    ruling = models.Ruling(
        text=text,
    )
    for token, ref in parse_references(text):
        ruling.references.append(
            models.Ruling.Reference(text=token, label=ref, url=references[ref])
        )
    for token, name in parse_cards(text):
        ruling.cards.append(models.CardMinimal.from_card(cards[name]))
    for token, substitute in parse_symbols(text):
        ruling.symbols.append(models.Ruling.Symbol(text=token, symbol=substitute))
    return ruling
