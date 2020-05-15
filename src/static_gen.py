"""Static files generator for third parties

Produces static files for use in third parties softwares
"""

import argparse
import collections
import hashlib
import json
import logging
import os.path
import re
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


def standard_twda():
    content = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>TWDA</title></head>

<body>
<center>
<h1>Tournament Winning Deck Archive</h1>
<h2>Formerly hosted on the Lasombra</h2>

<p>
This is a chronological archive of decks that have won tournaments that were<br>
sanctioned by the Vampire: Elder Kindred Network and had 10 or more players.<br>
National and Continental Championship are included as well, irrelatively to their attendance.<br>
To be included in this list, a tournament report had to be made on the official V:EKN Player's Forum:<br>
<a href="http://www.vekn.net/index.php/forum/9-event-reports-and-twd">http://www.vekn.net/index.php/forum/9-event-reports-and-twd</a><br>
This archive will not include the Storyline Tournament Winning Decks.<br>
Unless otherwise noted, each deck was the winning player's creation.<br>
<br>
The original <a href="http://www.thelasombra.com/hall_of_fame.htm">Hall of Fame</a> and the <a href="http://www.veknfrance.com/decks/twd.htm">Tournament Winning Deck Archive</a> were closed as of October 26, 2013.<br>
Many thanks to Jeff Thompson for maintaining them for all these years.
</p>
<table width="500" align="center" border="2" cellpadding="0">
<tbody><tr align="center">
<td colspan="10">You can jump to the end of a year that interests you:</td>
</tr>
<tr align="center">
<td colspan="4"></td>
<td><a href="#Year2020">2020</a></td>
<td><a href="#Year2019">2019</a></td>
<td><a href="#Year2018">2018</a></td>
<td><a href="#Year2017">2017</a></td>
<td colspan="3"></td>
</tr><tr align="center">
<td><a href="#Year2016">2016</a></td>
<td><a href="#Year2015">2015</a></td>
<td><a href="#Year2014">2014</a></td>
<td><a href="#Year2013">2013</a></td>
<td><a href="#Year2012">2012</a></td>
<td><a href="#Year2011">2011</a></td>
<td><a href="#Year2010">2010</a></td>
<td><a href="#Year2009">2009</a></td>
<td><a href="#Year2008">2008</a></td>
<td><a href="#Year2007">2007</a></td>
</tr><tr align="center">
<td><a href="#Year2006">2006</a></td>
<td><a href="#Year2005">2005</a></td>
<td><a href="#Year2004">2004</a></td>
<td><a href="#Year2003">2003</a></td>
<td><a href="#Year2002">2002</a></td>
<td><a href="#Year2001">2001</a></td>
<td><a href="#Year2000">2000</a></td>
<td><a href="#Year1999">1999</a></td>
<td><a href="#Year1998">1998</a></td>
<td><a href="#Year1997">1997</a></td>
</tr>
</tbody></table>
<p>Some abbreviations are used throughout the archive:
<table>
<tr><td>NC</td><td>National Championship</td><td>NAC</td><td>North American (Continental) Championship</td></tr>
<tr><td>NCQ</td><td>National Championship Qualifier</td><td>SAC</td><td>South American (Continental) Championship</td></tr>
<tr><td>ECQ</td><td>European Championship Qualifier</td><td>EC</td><td>European (Continental) Championship</td></tr>
<tr><td>CCQ</td><td>Continental Championship Qualifier</td><td>ACC</td><td>Asian Continental Championship</td></tr>
</table>"""  # noqa: E501
    decks = sorted(twda.TWDA.items(), key=lambda a: a[1].date, reverse=True)
    current_year = None
    for twda_id, deck in decks:
        if current_year != deck.date.year:
            current_year = deck.date.year
            content += f'\n<h3><a id="Year{current_year}">{current_year}</a></h3>\n\n'
        player = deck.player
        player = re.sub(r"\s*\([^\)]*\)", "", player)
        player = re.sub(r"\s*--\s+.*", "", player)
        if player[-1] != "s":
            player += "'s"
        else:
            player += "'"
        event = deck.event
        event = re.sub(r"\s*--\s+.*", "", event)
        place = deck.place
        place = re.sub(r"\s*,", ",", place)
        place = re.sub(r",,", ",", place)
        place = [x.strip() for x in place.split(",")[-2:]]
        event = event.strip().strip(":")
        if event[-len(place[0]) :] == place[0]:
            place = place[1:]
            event = event.strip().strip(":") + ","
        else:
            event = event.strip().strip(":") + ":"
        place = ", ".join(place)
        content += f"<a href=#{twda_id}>{player} {event} {place} {deck.date.strftime('%B %Y')}</a><br>\n"  # noqa: E501
    content += "</center>\n"
    for twda_id, deck in decks:
        content += f"<a id={twda_id} href=#>Top</a>\n<hr><pre>\n"
        content += vtes.VTES.deck_to_txt(deck, wrap=False)
        content += "\n</pre>\n"
    return content


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
        with open(
            os.path.join(out_folder, "twd.htm"), "w", encoding="utf-8-sig",
        ) as out_file:
            out_file.write(standard_twda())
    if "amaranth" in args.formats:
        with open(
            os.path.join(out_folder, "amaranth-twda.json"), "w", encoding="utf-8",
        ) as out_file:
            json.dump(amaranth_twda(), out_file, indent=2)
