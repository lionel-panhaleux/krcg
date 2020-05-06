"""Static files generator for third parties

Produces static files for use in third parties softwares
"""

import argparse
import collections
import hashlib
import json
import logging
import os.path
import sys

import requests

from . import twda
from . import vtes

logger = logging.getLogger()

parser = argparse.ArgumentParser(prog="krcg", description="VTES tool")


class FormatChoice(argparse.Action):
    # choices with nargs +/* : this is a known issue for argparse
    # cf. https://bugs.python.org/issue9625
    CHOICES = ["standard", "amaranth"]

    def __call__(self, parser, namespace, values, option_string=None):
        values = [v.lower() for v in values]
        if values:
            for value in values:
                if value not in self.CHOICES:
                    raise argparse.ArgumentError(
                        self, f"invalid choice: {value} (choose from {self.CHOICES})"
                    )
        setattr(namespace, self.dest, values)


parser.add_argument(
    "formats",
    metavar="FORMAT",
    nargs="+",
    action=FormatChoice,
    help="Generate static files in given formats",
)


def standard_rulings():
    result = {
        "rulings": {},
        "references": {},
        "cards": collections.defaultdict(list),
    }
    for key, data in vtes.VTES.items():
        if not isinstance(key, int):
            continue
        ruling_data = vtes.VTES.rulings.get(vtes.VTES.get_name(data))
        if not ruling_data:
            continue
        for ruling in ruling_data.get("Rulings", []):
            h = hashlib.sha3_256(ruling.encode("utf-8")).hexdigest()[-12:]
            result["rulings"].setdefault(h, ruling)
            result["cards"][key].append(h)
        for link in ruling_data.get("Rulings Links", []):
            result["references"].setdefault("[" + link["Reference"] + "]", link["URL"])
    return result


def amaranth_twda():
    try:
        amaranth_ids = {
            vtes.VTES.get_name(vtes.VTES[card["name"]]): card["id"]
            for card in (
                requests.get("http://amaranth.vtes.co.nz/api/cards").json()["result"]
            )
            if card["name"] in vtes.VTES
        }
    except requests.exceptions.ConnectionError as e:
        logger.exception("failed to connect to %s", e.request.url)
        exit(1)
    ret = []
    for twda_id, deck in twda.TWDA.items():
        try:
            ret.append(
                {
                    "author": deck.player,
                    "date": deck.date.format("YYYY-MM-DD"),
                    "title": deck.name or "",
                    "twda_key": twda_id,
                    "description": deck.event + ", " + deck.place,
                    "cards": {amaranth_ids[k]: v for k, v in deck.items()},
                }
            )
        except KeyError as e:
            logger.error(
                f"TWDA: {e.args[0]} not referenced in Amaranth, skipping {twda_id}"
            )
            continue
    return ret


def main():
    args = parser.parse_args(sys.argv[1:])
    logger.addHandler(logging.StreamHandler(sys.stderr))
    try:
        if not vtes.VTES:
            vtes.VTES.load_from_vekn(save=False)
        vtes.VTES.configure()
        if not twda.TWDA:
            twda.TWDA.load_from_vekn(save=False)
        twda.TWDA.configure(spoilers=False)
    except requests.exceptions.ConnectionError as e:
        logger.exception("failed to connect to %s", e.request.url)
        exit(1)
    out_folder = os.path.join(os.path.dirname(__file__), "..", "static")
    if "standard" in args.formats:
        with open(
            os.path.join(out_folder, "standard-rulings.json"), "w", encoding="utf-8",
        ) as out_file:
            json.dump(standard_rulings(), out_file, indent=2)
    if "amaranth" in args.formats:
        with open(
            os.path.join(out_folder, "amaranth-twda.json"), "w", encoding="utf-8",
        ) as out_file:
            json.dump(amaranth_twda(), out_file, indent=2)
