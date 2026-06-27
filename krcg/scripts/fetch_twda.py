#!/usr/bin/env python3
"""Fetch TWDA files from GitHub."""

import argparse
import io
import lzma
import msgspec.json
import os.path
import pathlib
import sys
import urllib.request
import zipfile

from krcg import collections
from krcg import loader
from krcg import models
from krcg import parser


def fetch_twda(path: pathlib.Path, cards: collections.CardDict) -> None:
    """Fetch the TWDA deck files from GitHub."""
    zip_url = "https://github.com/GiottoVerducci/TWD/archive/refs/heads/master.zip"

    with urllib.request.urlopen(zip_url) as response:
        zip_data = response.read()

    twd = dict[str, models.Deck]()
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_file:
        for file_info in zip_file.namelist():
            if file_info.startswith("TWD-master/decks/") and not file_info.endswith(
                "/"
            ):
                file_name = os.path.basename(file_info).split(".")[0]
                with zip_file.open(file_info) as source:
                    text_source = io.TextIOWrapper(source, encoding="utf-8")
                    deck = parser.deck_from_txt(
                        text_source, cards, id=file_name, twda=True
                    )
                    twd[deck.id] = deck
    with path.open("wb") as target:
        target.write(lzma.compress(msgspec.json.encode(twd), preset=9))


def main() -> None:
    """Command line to fetch TWDA files."""
    cli_parser = argparse.ArgumentParser(description="Fetch the TWDA.")
    cli_parser.add_argument(
        "--output", "-o", type=str, required=True, help="Output directory."
    )
    args = cli_parser.parse_args()
    output = pathlib.Path(args.output)
    try:
        output.touch()
    except OSError:
        print(f"Cannot create file {output}: {sys.exc_info()[1]}", file=sys.stderr)
        return
    cards = loader.load_local()
    parser.setup_parser_logging(True)
    fetch_twda(output, cards)


if __name__ == "__main__":
    main()
