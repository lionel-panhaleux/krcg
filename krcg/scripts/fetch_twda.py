#!/usr/bin/env python3
"""Fetch TWDA files from GitHub."""

import argparse
import lzma
import msgspec.json
import pathlib
import sys

from krcg import collections
from krcg import loader
from krcg import parser
from krcg import twda


def fetch_twda(path: pathlib.Path, cards: collections.CardDict) -> None:
    """Fetch the TWDA deck files from GitHub and write the compressed snapshot."""
    archive = twda.fetch_from_source(cards)
    with path.open("wb") as target:
        target.write(lzma.compress(msgspec.json.encode(archive), preset=9))


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
