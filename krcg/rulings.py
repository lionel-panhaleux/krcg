"""Rulings parsing.
"""

from typing import Generator, Tuple
import importlib.resources
import re
import warnings
import yaml


class Ruling:
    """Simple class representing a ruling."""

    def __init__(self):
        self.cards = []
        self.text = ""
        self.clean_text = ""
        self.links = {}
        self.symbols = []


class RulingReader:
    """Reader to load KRCG YAML rulings files."""

    def __init__(self):
        self.links = yaml.safe_load(
            importlib.resources.files("rulings")
            .joinpath("rulings-links.yaml")
            .read_text("utf-8")
        )

    def __iter__(self):
        """Yield Ruling instances"""
        for card, rulings in yaml.safe_load(
            importlib.resources.files("rulings")
            .joinpath("cards-rulings.yaml")
            .read_text("utf-8")
        ).items():
            for ruling in rulings:
                ret = Ruling()
                ret.cards = [_card_id_name(card)]
                ret.text = ruling
                if not ret.text or not isinstance(ret.text, str):
                    warnings.warn(f"absent or misformed text in '{card}' ruling")
                try:
                    ret.links = dict(self._get_link(ret.text))
                except KeyError:
                    warnings.warn(f"Ruling: link not found for `{card}`")
                    raise
                ret.symbols = list(self._get_symbols(ret.text))
                ret.clean_text = self._clean_text(ret.text)
                yield ret
        for ruling in yaml.safe_load(
            importlib.resources.files("rulings")
            .joinpath("general-rulings.yaml")
            .read_text("utf-8")
        ):
            ret = Ruling()
            ret.cards = [_card_id_name(card) for card in ruling["cards"]]
            ret.text = ruling["ruling"]
            if not ret.text or not isinstance(ret.text, str):
                warnings.warn(
                    f"absent or misformed text in general ruling for {ret.cards}"
                )
            try:
                ret.links = dict(self._get_link(ret.text))
            except KeyError:
                warnings.warn(f"Ruling: link not found for general ruling `{ret.text}`")
                raise
            ret.symbols = list(self._get_symbols(ret.text))
            ret.clean_text = self._clean_text(ret.text)
            yield ret

    def _get_link(self, text: str) -> Generator:
        """Yield (reference, link) tuples from rulink text."""
        references = re.findall(r"\[[a-zA-Z]+\s[0-9-]+\]", text)
        if not references:
            warnings.warn(f"no reference in ruling: {text}")
        for reference in references:
            yield reference, self.links[reference[1:-1]]

    def _get_symbols(self, text: str) -> Generator:
        """Yield symbols from ruling text."""
        symbols = re.findall(r"\[[a-zA-Z ]+\]", text)
        for symbol in symbols:
            yield symbol[1:-1]

    def _clean_text(self, text: str) -> None:
        text = re.subn(r"\[[a-zA-Z]+\s[0-9-]+\]", "", text)[0]
        text = re.subn(r"\[[a-zA-Z ]+\]", "", text)[0]
        return text


def _card_id_name(text: str) -> Tuple[int, str]:
    """Decode (id, name) from YAML "id|name" format."""
    try:
        card_id, card_name = text.split("|")
    except ValueError:
        warnings.warn(f"Bad card ID: {text}")
        raise
    card_id = int(card_id)
    return card_id, card_name
