"""Rulings parsing.
"""
from typing import Generator, Tuple
import dataclasses
import importlib.resources
import re
import warnings
import yaml


@dataclasses.dataclass
class Ruling:
    """Simple class representing a ruling."""

    text: str
    links: dict[str, str]
    symbols_txt: list[str]
    symbols_ankha: list[str]


SYMBOLS_MAP = {
    "CONVICTION": "¤",
    "ACTION": "0",
    "ACTION MODIFIER": "1",
    "POLITICAL ACTION": "2",
    "ALLY": "3",
    "COMBAT": "4",
    "EQUIPMENT": "5",
    "REFLEX": "6",
    "REACTION": "7",
    "RETAINER": "8",
    "FLIGHT": "^",
    "MERGED": "µ",
    "POWER": "§",
    "EVENT": "[",
    "ADVANCED": "|",
    "BURN OPTION": "~",
    "abo": "w",
    "ABO": "W",
    "ani": "i",
    "ANI": "I",
    "aus": "a",
    "AUS": "A",
    "cel": "c",
    "CEL": "C",
    "chi": "k",
    "CHI": "K",
    "dai": "y",
    "DAI": "Y",
    "dem": "e",
    "DEM": "E",
    "dom": "d",
    "DOM": "D",
    "for": "f",
    "FOR": "F",
    "mal": "â",
    "MAL": "ã",
    "mel": "m",
    "MEL": "M",
    "myt": "x",
    "MYT": "X",
    "nec": "n",
    "NEC": "N",
    "obe": "b",
    "OBE": "B",
    "obf": "o",
    "OBF": "O",
    "obt": "$",
    "OBT": "£",
    "pot": "p",
    "POT": "P",
    "pre": "r",
    "PRE": "R",
    "pro": "j",
    "PRO": "J",
    "qui": "q",
    "QUI": "Q",
    "san": "g",
    "SAN": "G",
    "ser": "s",
    "SER": "S",
    "spi": "z",
    "SPI": "Z",
    "str": "à",
    "STR": "á",
    "tem": "?",
    "TEM": "!",
    "thn": "h",
    "THN": "H",
    "tha": "t",
    "THA": "T",
    "val": "l",
    "VAL": "L",
    "vic": "v",
    "VIC": "V",
    "vis": "u",
    "VIS": "U",
    "vin": ")",
    "def": "@",
    "jus": "%",
    "inn": "#",
    "mar": "&",
    "ven": "(",
    "red": "*",
}


class RulingReader:
    """Reader to load KRCG YAML rulings files."""

    def __init__(self):
        self.links = yaml.safe_load(
            importlib.resources.files("rulings")
            .joinpath("links.yaml")
            .read_text("utf-8")
        )
        self.groups = yaml.safe_load(
            importlib.resources.files("rulings")
            .joinpath("groups.yaml")
            .read_text("utf-8")
        )

    def __iter__(self) -> Generator[Ruling, None, None]:
        """Yield Ruling instances"""

        for key, rulings in yaml.safe_load(
            importlib.resources.files("rulings")
            .joinpath("rulings.yaml")
            .read_text("utf-8")
        ).items():
            id_, name = _id_name(key)
            if id_ > 900000:
                cards = {_id_name(k): v for k, v in self.groups[key].items()}
            else:
                cards = {(id_, name): []}
            for ruling in rulings:
                clean_text = re.subn(r"\[[a-zA-Z]+\s[0-9-]+\]", "", ruling)[0]
                clean_text = re.subn(r"\[[a-zA-Z ]+\]", "", clean_text)[0].strip()
                symbols = re.findall(r"\[[a-zA-Z ]+\]", ruling)
                symbols = [symbol[1:-1] for symbol in symbols]
                if any(s for s in symbols if s not in SYMBOLS_MAP):
                    warnings.warn(f"invalid symbol in ruling: {ruling}")
                links = re.findall(r"\[[a-zA-Z]+\s[0-9-]+\]", ruling)
                if not links:
                    warnings.warn(f"no reference in ruling: {ruling}")
                if any(ref for ref in links if ref[1:-1] not in self.links):
                    warnings.warn(f"unmatched reference in ruling: {ruling}")
                links = {ref: self.links[ref[1:-1]] for ref in links}
                for (id_, name), card_symbols in cards.items():
                    card_symbols = symbols + card_symbols
                    yield id_, name, Ruling(
                        clean_text,
                        links,
                        symbols_txt=[f"[{s}]" for s in card_symbols],
                        symbols_ankha=[SYMBOLS_MAP[s] for s in card_symbols],
                    )


def _id_name(text: str) -> Tuple[int, str]:
    """Decode (id, name) from YAML "id|name" format."""
    try:
        id_, name = text.split("|")
    except ValueError:
        warnings.warn(f"Bad card/group ID: {text}")
        raise
    id_ = int(id_)
    return id_, name
