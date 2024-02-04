"""Rulings parsing.
"""
from typing import Any, Generator, Tuple
import collections
import dataclasses
import importlib.resources
import re
import warnings
import yaml
from yaml.constructor import _Scalar
from yaml.nodes import MappingNode, ScalarNode, SequenceNode


class RulingsError(yaml.MarkedYAMLError):
    pass


class RulingsLoader(yaml.SafeLoader):
    def __init__(self, cards: "krcg.cards.CardMap"):
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
        self.cards = cards

    def load(self) -> None:
        self.safe_load(
            importlib.resources.files("rulings")
            .joinpath("rulings.yaml")
            .read_text("utf-8")
        )

    def construct_mapping(
        self, node: MappingNode, deep: bool = False
    ) -> dict[collections.abc.Hashable, Any]:
        if isinstance(node, MappingNode):
            self.flatten_mapping(node)
        if not isinstance(node, MappingNode):
            raise yaml.ConstructorError(
                None,
                None,
                "expected a mapping node, but found %s" % node.id,
                node.start_mark,
            )
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str):
                raise RulingsError(
                    "while reading rulings",
                    node.start_mark,
                    "found invalid key",
                    key_node.start_mark,
                )
            # key must be a card or group
            value = self.construct_object(value_node, deep=deep)

            mapping[key] = value
        return mapping

    def construct_sequence(self, node: SequenceNode, deep: bool = False) -> list[Any]:
        return super().construct_sequence(node, deep)

    def construct_scalar(self, node: ScalarNode) -> _Scalar:
        ret = super().construct_scalar(node)
        return ret


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
                if key not in self.groups:
                    warnings.warn(
                        RulingsWarning(f"Invalid group reference in rulings: {key}")
                    )
                    cards = {}
                else:
                    cards = {_id_name(k): v for k, v in self.groups[key].items()}
            else:
                cards = {(id_, name): []}
            for ruling in rulings:
                clean_text = re.subn(r"\[[a-zA-Z]+\s[0-9-]+\]", "", ruling)[0]
                clean_text = re.subn(r"\[[a-zA-Z ]+\]", "", clean_text)[0].strip()
                symbols = re.findall(r"\[[a-zA-Z ]+\]", ruling)
                symbols = [symbol[1:-1] for symbol in symbols]
                invalid = [s for s in symbols if s not in SYMBOLS_MAP]
                if invalid:
                    warnings.warn(
                        RulingsWarning(
                            f'invalid symbol(s) {", ".join(invalid)} '
                            f"in ruling: {ruling}"
                        )
                    )
                    symbols = [s for s in symbols if s in SYMBOLS_MAP]
                links = re.findall(r"\[[a-zA-Z]+\s[0-9-]+\]", ruling)
                if not links:
                    warnings.warn(RulingsWarning(f"no reference in ruling: {ruling}"))
                    continue
                unmatched = [ref for ref in links if ref[1:-1] not in self.links]
                if unmatched:
                    warnings.warn(
                        RulingsWarning(
                            f'unmatched reference(s) {(", ").join(unmatched)} '
                            f"in ruling: {ruling}"
                        )
                    )
                links = {
                    ref: self.links[ref[1:-1]]
                    for ref in links
                    if ref[1:-1] in self.links
                }
                for (id_, name), card_symbols in cards.items():
                    card_symbols = symbols + card_symbols
                    yield id_, name, Ruling(
                        clean_text,
                        links,
                        symbols_txt=[f"[{s}]" for s in card_symbols],
                        symbols_ankha=[SYMBOLS_MAP[s] for s in card_symbols],
                    )

    def load_on_cards(self, cards: "krcg.cards.CardMap") -> None:
        for card_id, card_name, ruling in self:
            if self[card_id].name != card_name:
                warnings.warn(
                    RulingsWarning(
                        f"Rulings: {card_name} does not match {self[card_id]}"
                    )
                )
            self[card_id].rulings.append(dataclasses.asdict(ruling))
            for card_reference in re.findall(r"{[^}]+}", ruling.text):
                card_reference = card_reference[1:-1]
                if card_reference not in self:
                    warnings.warn(
                        RulingsWarning(
                            f"Ruling on {card_id}|{card_name} "
                            f"mentions unknown card {card_reference}"
                        )
                    )
                if self[card_reference].usual_name != card_reference:
                    warnings.warn(
                        RulingsWarning(
                            f"Rulings on {card_id}|{card_name} mentions "
                            f'{card_reference} instead of "{self[card_reference].name}"'
                        )
                    )


def _id_name(text: str) -> Tuple[int, str]:
    """Decode (id, name) from YAML "id|name" format."""
    try:
        id_, name = text.split("|")
    except ValueError:
        warnings.warn(RulingsWarning(f"Bad card/group ID: {text}"))
        raise
    id_ = int(id_)
    return id_, name
