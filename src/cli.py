"""Command-line interface.
"""
import argparse
import io
import logging
import sys
import tempfile
import zipfile

import arrow
import requests

from . import analyzer
from . import config
from . import twda
from . import vtes
from . import deck

logger = logging.getLogger()


def init(args):
    if args.vtes:
        vtes.VTES.load_csv(args.file)
    elif args.twda:
        if not vtes.VTES:
            logger.critical(
                "VTES cards database must be initialized before TWDA database."
            )
            exit(1)
        vtes.VTES.configure()
        twda.TWDA.load_html(args.file)
    else:
        try:
            with tempfile.NamedTemporaryFile("wb", suffix=".zip") as f:
                r = requests.request("GET", config.VEKN_VTES_URL)
                f.write(r.content)
                f.flush()
                z = zipfile.ZipFile(f.name)
                with z.open(config.VEKN_VTES_LIBRARY_FILENAME) as c:
                    vtes.VTES.load_csv(io.TextIOWrapper(c, encoding="utf_8_sig"))
                with z.open(config.VEKN_VTES_CRYPT_FILENAME) as c:
                    vtes.VTES.load_csv(io.TextIOWrapper(c, encoding="utf_8_sig"))
                vtes.VTES.configure()
            r = requests.request("GET", config.VEKN_TWDA_URL)
            twda.TWDA.load_html(io.BytesIO(r.content), binary=True)
        except requests.exceptions.ConnectionError as e:
            logger.critical(
                "failed to connect to {}"
                " - check your Internet connection and firewall settings".format(
                    e.request.url
                )
            )
            exit(1)


def affinity(args):
    # build a condition matching options
    def condition(card):
        return (
            (args.spoilers or twda.TWDA.no_spoil(card))
            and (not args.crypt or vtes.VTES.is_crypt(card))
            and (not args.library or vtes.VTES.is_library(card))
        )

    twda.TWDA.configure(args.date_from, args.date_to)
    A = analyzer.Analyzer()
    A.refresh(*args.cards, condition=condition)
    for candidate in A.candidates(*args.cards)[: args.number]:
        print("{0[0]:<30} (score: {0[1]:.2f})".format(candidate))


def top(args):
    # build a condition matching options
    def condition(card):
        return (
            (not args.clan or vtes.VTES.is_clan(card, args.clan))
            and (not args.type or vtes.VTES.is_type(card, args.type))
            and (not args.disc or vtes.VTES.is_disc(card, args.disc))
            and (
                not args.exclude_type or not vtes.VTES.is_type(card, args.exclude_type)
            )
        )

    twda.TWDA.configure(args.date_from, args.date_to)
    A = analyzer.Analyzer()
    A.refresh(condition=condition)
    for card_name, count in A.played.most_common()[: args.number]:
        card = vtes.VTES[card_name]
        print("{:<30} (played in {} decks)".format(_card_name(card), count))
        if args.full:
            print(_card_text(card))
            print()


def build(args):
    twda.TWDA.configure()
    print(vtes.VTES.deck_to_txt(analyzer.Analyzer().build_deck(*args.cards)))


def deck_(args):
    twda.TWDA.configure(args.date_from, args.date_to, min_players=args.players)
    decks = {i: twda.TWDA[i] for i in args.cards_or_id if i in twda.TWDA}
    cards = [vtes.VTES[c]["Name"] for c in args.cards_or_id if c not in twda.TWDA]
    if not decks:
        A = analyzer.Analyzer()
        try:
            A.refresh(*cards, similarity=1)
        except analyzer.AnalysisError:
            exit(1)
        decks.update(A.examples)
    if len(decks) == 1:
        args.full = True
    for twda_id, example in sorted(decks.items(), key=lambda a: a[1].date):
        if args.full:
            print(
                "[{:<15}]===================================================".format(
                    twda_id
                )
            )
            print(vtes.VTES.deck_to_txt(example))
        else:
            print("[{}] {}".format(twda_id, example))


def card(args):
    for name in args.cards:
        try:
            card = vtes.VTES[name]
        except KeyError:
            logger.critical("Card not found: {}".format(name))
            exit(1)
        print(_card_name(card))
        print(_card_text(card))


def _card_name(card):
    return card["Name"] + (" (ADV)" if card.get("Adv") else "")


def _card_text(card):
    text = "[{}]".format(card["Type"])
    if card.get("Clan"):
        text += "[{}]".format(card["Clan"])
    if card.get("Pool Cost"):
        text += "[{}P]".format(card["Pool Cost"])
    if card.get("Blood Cost"):
        text += "[{}B]".format(card["Blood Cost"])
    if card.get("Conviction Cost"):
        text += "[{}C]".format(card["Conviction Cost"])
    if card.get("Capacity"):
        text += "[{}]".format(card["Capacity"])
    if card.get("Group"):
        text += "(g.{})".format(card["Group"])
    if card.get("Burn Option"):
        text += "(Burn Option)"
    if card.get("Banned"):
        text += " -- BANNED"
    text += " -- ({})".format(card["Set"])
    if "Disciplines" in card:
        text += "\n{}".format(card["Disciplines"] or "-- No discipline")
    text += "\n{}".format(card["Card Text"])
    return text


def test(args):
    import doctest

    doctest.testmod(vtes)
    doctest.testmod(deck)
    doctest.testmod(twda)
    doctest.testmod(analyzer)


root_parser = argparse.ArgumentParser(prog="krcg", description="VTES tool")
root_parser.add_argument(
    "-v",
    "--verbosity",
    type=int,
    default=1,
    metavar="N",
    help="0: none, 1: errors, 2: info, 3: debug",
)
subparsers = root_parser.add_subparsers(
    metavar="", title="subcommands", dest="subcommand"
)
# ######################################################################### init
parser = subparsers.add_parser("init", help="initialize the local TWDA database")
parser.add_argument(
    "-v", "--vtes", action="store_true", help="Initialize VTES cards database"
)
parser.add_argument(
    "-t", "--twda", action="store_true", help="Initialize TWDA database"
)
parser.add_argument(
    "file",
    type=argparse.FileType("r", encoding="utf-8"),
    nargs="?",
    help="vtes.csv or TWDA.html file",
)
parser.set_defaults(func=init)
# ##################################################################### affinity
parser = subparsers.add_parser(
    "affinity", help="display cards with the most affinity to given cards"
)
parser.add_argument(
    "-n",
    "--number",
    type=int,
    default=10,
    metavar="N",
    help="Number of cards to print (default 10)",
)
parser.add_argument(
    "--from",
    type=lambda s: arrow.get(s, "YYYY"),
    default=arrow.get(2008, 1, 1),
    dest="date_from",
    help="do not consider decks that won before this year (default 2008-01-01)",
)
parser.add_argument(
    "--to",
    type=lambda s: arrow.get(s, "YYYY"),
    default=arrow.get(),
    dest="date_to",
    help="do not consider decks that won after this year",
)
parser.add_argument(
    "-s",
    "--spoilers",
    action="store_true",
    help="Display spoiler cards in affinity list (not included by default)",
)
parser.add_argument("-c", "--crypt", action="store_true", help="Only crypt cards")
parser.add_argument("-l", "--library", action="store_true", help="Only library cards")
parser.add_argument(
    "cards",
    metavar="CARD",
    nargs="+",
    type=lambda a: vtes.VTES[a]["Name"],
    help="reference cards",
)
parser.set_defaults(func=affinity)
# ########################################################################## top
parser = subparsers.add_parser(
    "top", help="display top cards (played in most TW decks)"
)
parser.add_argument(
    "-n", "--number", type=int, default=10, help="Number of cards to print (default 10)"
)
parser.add_argument(
    "--from",
    type=lambda s: arrow.get(s, "YYYY"),
    default=arrow.get(2008, 1, 1),
    dest="date_from",
    help="do not consider decks that won before this year (default 2008-01-01)",
)
parser.add_argument(
    "--to",
    type=lambda s: arrow.get(s, "YYYY"),
    default=arrow.get(),
    dest="date_to",
    help="do not consider decks that won after this year",
)
parser.add_argument(
    "-d",
    "--discipline",
    choices=vtes.VTES.disciplines,
    dest="disc",
    metavar="DISC",
    help="Filter by discipline ({})".format(", ".join(vtes.VTES.disciplines)),
)
parser.add_argument(
    "-c",
    "--clan",
    choices=vtes.VTES.clans,
    metavar="CLAN",
    help="Filter by clan ({})".format(", ".join(vtes.VTES.clans)),
)
parser.add_argument(
    "-t",
    "--type",
    choices=vtes.VTES.types,
    metavar="TYPE",
    help="Filter by type ({})".format(", ".join(vtes.VTES.types)),
)
parser.add_argument(
    "-e",
    "--exclude-type",
    choices=vtes.VTES.types,
    metavar="TYPE",
    help="Exclude given type ({})".format(", ".join(vtes.VTES.types)),
)
parser.add_argument("-f", "--full", action="store_true", help="display card text")
parser.set_defaults(func=top)
# ######################################################################## build
parser = subparsers.add_parser("build", help="build a deck")
parser.add_argument(
    "-d",
    "--date",
    type=arrow.get,
    default=arrow.get(2008, 1, 1),
    help="do not consider decks that won before this date (default 2008-01-01)",
)
parser.add_argument(
    "cards",
    metavar="CARD",
    nargs="*",
    type=lambda a: vtes.VTES[a]["Name"],
    help="reference cards",
)
parser.set_defaults(func=build)
# ######################################################################### deck
parser = subparsers.add_parser("deck", help="show TWDA decks")
parser.add_argument(
    "-f", "--full", action="store_true", help="display each deck content"
)
parser.add_argument(
    "cards_or_id", metavar="TXT", nargs="*", help="list TWDA decks from ID or cards"
)
parser.add_argument(
    "--from",
    type=lambda s: arrow.get(s, "YYYY"),
    default=arrow.get(2008, 1, 1),
    dest="date_from",
    help="do not consider decks that won before this year (default 2008-01-01)",
)
parser.add_argument(
    "--to",
    type=lambda s: arrow.get(s, "YYYY"),
    default=arrow.get(),
    dest="date_to",
    help="do not consider decks that won after this year",
)
parser.add_argument(
    "-p",
    "--players",
    type=int,
    default=0,
    help="minimum number of players in tournament to consider this deck",
)
parser.set_defaults(func=deck_)
# ######################################################################### card
parser = subparsers.add_parser("card", help="show VTES cards")
parser.add_argument("-s", "--short", action="store_true", help="display only card name")
parser.add_argument("cards", metavar="CARD", nargs="+", help="list these cards")
parser.set_defaults(func=card)
# ######################################################################### test
parser = subparsers.add_parser("test", help="unit test")
parser.set_defaults(func=test)


def main():
    args = root_parser.parse_args(sys.argv[1:])
    if args.verbosity > 0:
        logger.addHandler(logging.StreamHandler(sys.stderr))
        logger.setLevel(
            {1: logging.ERROR, 2: logging.INFO, 3: logging.DEBUG}[args.verbosity]
        )
    if not args.subcommand:
        root_parser.print_help()
        return
    if args.subcommand != "init":
        if not vtes.VTES:
            logger.critical("VTES cards database is not initialized. Use vtes init")
            exit(1)
        vtes.VTES.configure()
        if not twda.TWDA:
            logger.critical("TWDA database is not initialized. Use vtes init")
            exit(1)
        twda.TWDA.configure()
    args.func(args)
