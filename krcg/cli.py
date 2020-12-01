"""Command-line interface (CLI).
"""
from typing import Mapping, Set
import argparse
import json
import math
import sys

import arrow
import requests
import unidecode

from . import analyzer
from . import config
from . import deck
from . import logging
from . import twda
from . import utils
from . import vtes

logger = logging.logger

# VTES configure must be done before parsing args
if vtes.VTES:
    vtes.VTES.configure()


def init(args: argparse.Namespace) -> int:
    """Initialize the CLI, loads VTES cards list, rulings and TWDA."""
    if args.cards:
        if args.file:
            vtes.VTES.load_csv(args.file)
        else:
            vtes.VTES.load_from_vekn()
    elif args.twda:
        if not vtes.VTES:
            logger.critical(
                "VTES cards database must be initialized before TWDA database."
            )
            return 1
        vtes.VTES.configure()
        if args.file:
            twda.TWDA.load_html(args.file)
        else:
            twda.TWDA.load_from_vekn()
    else:
        try:
            vtes.VTES.load_from_vekn()
            vtes.VTES.configure()
            twda.TWDA.load_from_vekn()
        except requests.exceptions.ConnectionError as e:
            logger.critical(
                "failed to connect to {} - check your Internet connection",
                e.request.url,
            )
            return 1
    return 0


def typical_copies(A: analyzer.Analyzer, card_name: str) -> str:
    """Given a card, returns a string telling the usual number of copies included.

    Example:
        >>> typical_copies(a, "Fame")
        1-2 copies
    """
    deviation = math.sqrt(A.variance[card_name])
    min_copies = max(1, round(A.average[card_name] - deviation))
    max_copies = round(A.average[card_name] + deviation)
    if min_copies == max_copies:
        ret = f"{min_copies}"
    else:
        ret = f"{min_copies}-{max_copies}"
    if max_copies > 1:
        ret += " copies"
    else:
        ret += " copy"
    return ret


def affinity(args: argparse.Namespace) -> int:
    """Compute cards affinity"""
    # build a condition matching options
    def condition(card):
        return (not args.crypt or vtes.VTES.is_crypt(card)) and (
            not args.library or vtes.VTES.is_library(card)
        )

    twda.TWDA.configure(args.date_from, args.date_to, args.players)
    A = analyzer.Analyzer(twda.TWDA)
    A.refresh(*args.cards, condition=condition, similarity=1)
    if len(A.examples) < 4:
        print("Too few example in TWDA.")
        if len(A.examples) > 0:
            print(
                "To see them:\n\tkrcg deck "
                + " ".join('"' + name + '"' for name in args.cards)
            )
        return
    for name, score in A.candidates(*args.cards, no_filter=True)[: args.number or None]:
        score = round(score * 100 / len(args.cards))
        if args.minimum and args.minimum > score:
            break
        # do not include spoilers if affinity is within 50% of natural occurence
        if score < twda.TWDA.spoilers.get(name, 0) * 150:
            continue
        print(
            f"{name:<30} (in {score:.0f}% of decks, typically "
            f"{typical_copies(A, name)})"
        )
    return 0


def _search(args: argparse.Namespace) -> Set[int]:
    result = set(card["Id"] for card in vtes.VTES.original_cards.values())
    for type_ in args.type or []:
        result &= vtes.VTES.search["type"].get(type_.lower(), set())
    for clan in args.clan or []:
        clan = config.CLANS_AKA.get(clan.lower()) or clan
        result &= vtes.VTES.search["clan"].get(clan.lower(), set())
    for group in args.group or []:
        result &= vtes.VTES.search["group"].get(group.lower(), set())
    for bonus in args.bonus or []:
        result &= vtes.VTES.search.get(bonus.lower(), set())
    for trait in args.trait or []:
        result &= vtes.VTES.search["trait"].get(trait.lower(), set())
    for discipline in args.disc or []:
        discipline = config.DIS_MAP.get(discipline) or discipline
        result &= vtes.VTES.search["discipline"].get(discipline, set())
    for exclude in args.exclude_type or []:
        result -= vtes.VTES.search["type"].get(exclude.lower(), set())
    return result


def search(args: argparse.Namespace) -> int:
    """Search for cards matching filters"""
    result = _search(args)
    for card_id in sorted(list(result))[: args.number]:
        card = vtes.VTES[int(card_id)]
        name = vtes.VTES.get_name(card)
        print(name)
        if args.full:
            print(_card_text(card))
            print()
    if len(result) > args.number:
        print(f"... ({len(result)} results available, use the -n option)")
    return 0


def top(args: argparse.Namespace) -> int:
    """Most played cards matching filters"""
    result = _search(args)
    twda.TWDA.configure(args.date_from, args.date_to, args.players)
    A = analyzer.Analyzer(twda.TWDA)
    A.refresh(condition=lambda c: vtes.VTES[c]["Id"] in result)
    for card_name, count in A.played.most_common()[: args.number]:
        card = vtes.VTES[card_name]
        print(
            f"{card_name:<30} (played in {count} decks, typically "
            f"{typical_copies(A, card_name)})"
        )
        if args.full:
            print(_card_text(card))
            print()
    return 0


def build(args: argparse.Namespace) -> int:
    """Build a deck based on TWDA examples"""
    twda.TWDA.configure(args.date_from, args.date_to, args.players)
    print(vtes.VTES.deck_to_txt(analyzer.Analyzer().build_deck(*args.cards)))
    return 0


def deck_(args: argparse.Namespace) -> int:
    """Display TWDA decks"""
    twda.TWDA.configure(args.date_from, args.date_to, args.players, spoilers=False)
    decks = {i: twda.TWDA[i] for i in args.cards_or_id if i in twda.TWDA}
    by_author = [
        set(twda.TWDA.by_author[unidecode.unidecode(name).lower()])
        for name in args.cards_or_id
        if unidecode.unidecode(name).lower() in twda.TWDA.by_author
    ]
    if by_author:
        decks.update({i: twda.TWDA[i] for i in set.union(*by_author)})
    cards = [vtes.VTES.get_name(c) for c in args.cards_or_id if c in vtes.VTES]
    if cards:
        A = analyzer.Analyzer(twda.TWDA)
        try:
            A.refresh(*cards, similarity=1)
        except analyzer.AnalysisError:
            exit(1)
        decks.update(A.examples)
    elif not args.cards_or_id:
        decks = twda.TWDA
    if len(decks) == 1:
        args.full = True
    if not args.full:
        print(f"-- {len(decks)} decks --")
    for twda_id, example in sorted(decks.items(), key=lambda a: a[1].date):
        if args.full:
            print(
                "[{:<15}]===================================================".format(
                    twda_id
                )
            )
            print(example.to_txt())
        else:
            print(f"[{twda_id}] {example}")
    return 0


def card(args: argparse.Namespace) -> int:
    """Display cards, their text and rulings"""
    for i, name in enumerate(args.cards):
        if not args.short and i > 0:
            print()
        try:
            name = int(name)
        except ValueError:
            pass
        try:
            card = vtes.VTES[name]
        except KeyError:
            logger.critical("Card not found: {}", name)
            exit(1)
        print(vtes.VTES.get_name(card))
        if args.short:
            continue
        print(_card_text(card))
        print(_card_rulings(args, vtes.VTES.get_name(card)))
    return 0


def _card_text(card: Mapping) -> str:
    """Full text of a card (id, title, traits, costs, ...) for display purposes"""
    text = "[{}]".format("/".join(card["Type"]))
    if card.get("Clan"):
        text += "[{}]".format("/".join(card["Clan"]))
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
        text += " -- BANNED in " + card["Banned"]
    text += " -- ({} - #{})".format(", ".join(card["Set"]), card["Id"])
    if "Disciplines" in card:
        text += "\n{}".format("/".join(card["Disciplines"]) or "-- No discipline")
    text += "\n{}".format(card["Card Text"])
    return text


def _card_rulings(args: argparse.Namespace, card_name: str):
    """Text of a card's rulings"""
    rulings = vtes.VTES.rulings.get(card_name)
    if args.text or not rulings:
        return ""
    text = "\n-- Rulings\n"
    for ruling in rulings["Rulings"]:
        text += ruling + "\n"
    if args.links:
        for link in rulings["Rulings Links"]:
            text += f"[{link['Reference']}]: {link['URL']}\n"
    return text


def complete(args: argparse.Namespace) -> int:
    """Card names completion"""
    for name in vtes.VTES.complete(args.name.lower()):
        print(name)
    return 0


def deck_to_json(args: argparse.Namespace) -> int:
    d = deck.Deck.from_txt(args.file)
    json.dump(d.to_dict(), sys.stdout, indent=2)
    return 0


# ############################################################################# argparse
def add_deck_boundaries(parser, default_date_from="1994-01-01"):
    """Common arguments: --from and --to to control year boundaries of TWDA analysis."""
    parser.add_argument(
        "--from",
        type=lambda s: arrow.get(s),
        default=arrow.get(default_date_from),
        dest="date_from",
        help=(
            "do not consider decks that won before this year "
            f"(default {default_date_from})"
        ),
    )
    parser.add_argument(
        "--to",
        type=lambda s: arrow.get(s),
        default=arrow.get(),
        dest="date_to",
        help="do not consider decks that won after this year",
    )
    parser.add_argument(
        "--players",
        type=int,
        default=0,
        help="do not consider decks with less players than this",
    )


class DisciplineChoice(utils.NargsChoiceWithAliases):
    CHOICES = vtes.VTES.search.get("discipline", {}).keys()
    ALIASES = config.DIS_MAP
    CASE_SENSITIVE = True


class ClanChoice(utils.NargsChoiceWithAliases):
    CHOICES = vtes.VTES.search.get("clan", {}).keys()
    ALIASES = config.CLANS_AKA


class TypeChoice(utils.NargsChoiceWithAliases):
    CHOICES = vtes.VTES.search.get("type", {}).keys()


class TraitChoice(utils.NargsChoiceWithAliases):
    CHOICES = vtes.VTES.search.get("trait", {}).keys()


class GroupChoice(utils.NargsChoiceWithAliases):
    CHOICES = vtes.VTES.search.get("group", {}).keys()


class BonusChoice(utils.NargsChoiceWithAliases):
    CHOICES = set(vtes.VTES.search.keys()) - {
        "trait",
        "type",
        "capacity",
        "group",
        "discipline",
        "clan",
        "text",
    }


def add_search(parser):
    """Common search arguments for top and search commands"""
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        default=10,
        help="Number of cards to print (default 10)",
    )
    parser.add_argument(
        "-d",
        "--discipline",
        action=DisciplineChoice,
        dest="disc",
        metavar="DISC",
        nargs="+",
        help="Filter by discipline ({})".format(
            ", ".join(vtes.VTES.search.get("discipline", {}).keys())
        ),
    )
    parser.add_argument(
        "-c",
        "--clan",
        action=ClanChoice,
        metavar="CLAN",
        nargs="+",
        help="Filter by clan ({})".format(
            ", ".join(vtes.VTES.search.get("clan", {}).keys())
        ),
    )
    parser.add_argument(
        "-t",
        "--type",
        action=TypeChoice,
        metavar="TYPE",
        nargs="+",
        help="Filter by type ({})".format(
            ", ".join(vtes.VTES.search.get("type", {}).keys())
        ),
    )
    parser.add_argument(
        "-g",
        "--group",
        action=GroupChoice,
        metavar="GROUP",
        nargs="+",
        help="Filter by group ({})".format(
            ", ".join(vtes.VTES.search.get("group", {}).keys())
        ),
    )
    parser.add_argument(
        "-e",
        "--exclude-type",
        action=TypeChoice,
        metavar="TYPE",
        nargs="+",
        help="Exclude given type ({})".format(
            ", ".join(vtes.VTES.search.get("type", {}).keys())
        ),
    )
    parser.add_argument(
        "-r",
        "--trait",
        action=TraitChoice,
        metavar="TRAIT",
        nargs="+",
        help="Filter by trait ({})".format(
            ", ".join(vtes.VTES.search.get("trait", {}).keys())
        ),
    )
    parser.add_argument(
        "-b",
        "--bonus",
        action=BonusChoice,
        metavar="BONUS",
        nargs="+",
        help="Filter by bonus ({})".format(", ".join(BonusChoice.CHOICES)),
    )
    parser.add_argument("-f", "--full", action="store_true", help="display card text")


root_parser = argparse.ArgumentParser(prog="krcg", description="VTES tool")
root_parser.add_argument(
    "-v",
    "--verbosity",
    type=int,
    default=0,
    metavar="N",
    help="0: errors, 1: warnings , 2: info, 3: debug",
)
subparsers = root_parser.add_subparsers(
    metavar="", title="subcommands", dest="subcommand"
)

# ################################################################################# init
parser = subparsers.add_parser("init", help="initialize the local TWDA database")
parser.add_argument(
    "-c", "--cards", action="store_true", help="Initialize VTES cards database"
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

# ############################################################################# affinity
parser = subparsers.add_parser(
    "affinity", help="display cards with the most affinity to given cards"
)
add_deck_boundaries(
    parser, default_date_from=arrow.get().shift(years=-5).date().isoformat()
)
parser.add_argument(
    "-n",
    "--number",
    type=int,
    default=0,
    metavar="N",
    help="Number of cards to print",
)
parser.add_argument(
    "-m",
    "--minimum",
    type=int,
    default=33,
    metavar="P",
    help="Minimum affinity to display (default 33)",
)
parser.add_argument("-c", "--crypt", action="store_true", help="Only crypt cards")
parser.add_argument("-l", "--library", action="store_true", help="Only library cards")
parser.add_argument(
    "cards",
    metavar="CARD",
    nargs="+",
    type=lambda a: vtes.VTES.get_name(a),
    help="reference cards",
)
parser.set_defaults(func=affinity)

# ################################################################################## top
parser = subparsers.add_parser(
    "top", help="display top cards (played in most TW decks)"
)
add_deck_boundaries(parser, arrow.get().shift(years=-5).date().isoformat())
add_search(parser)
parser.set_defaults(func=top)

# ################################################################################ build
parser = subparsers.add_parser("build", help="build a deck")
add_deck_boundaries(parser)
parser.add_argument(
    "cards",
    metavar="CARD",
    nargs="*",
    type=lambda a: vtes.VTES.get_name(a),
    help="reference cards",
)
parser.set_defaults(func=build)

# ################################################################################# deck
parser = subparsers.add_parser("deck", help="show TWDA decks")
add_deck_boundaries(parser)
parser.add_argument(
    "-f", "--full", action="store_true", help="display each deck content"
)
parser.add_argument(
    "cards_or_id",
    metavar="TXT",
    nargs="*",
    help="list TWDA decks from ID, author name or cards",
)
parser.set_defaults(func=deck_)

# ################################################################################# card
parser = subparsers.add_parser("card", help="show VTES cards")
parser.add_argument("-s", "--short", action="store_true", help="display only card name")
parser.add_argument(
    "-t", "--text", action="store_true", help="display card text only (no rulings)"
)
parser.add_argument("-l", "--links", action="store_true", help="display ruling links")
parser.add_argument("cards", metavar="CARD", nargs="+", help="card names or IDs")
parser.set_defaults(func=card)

# ############################################################################# complete
parser = subparsers.add_parser("complete", help="card name completion")
parser.add_argument("-f", "--full", action="store_true", help="display cards text")
parser.add_argument("name", metavar="NAME", help="partial name")
parser.set_defaults(func=complete)

# ############################################################################### search
parser = subparsers.add_parser("search", help="card search")
add_search(parser)
parser.set_defaults(func=search)
# ############################################################################### json
parser = subparsers.add_parser("json", help="Format a decklist to JSON")
parser.add_argument(
    "file",
    type=argparse.FileType("r", encoding="utf-8"),
    nargs="?",
    help="File containing the decklist",
)
parser.set_defaults(func=deck_to_json)


def execute(args):
    args = root_parser.parse_args(args)
    logger.setLevel(
        {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}[
            args.verbosity
        ]
    )
    if not args.subcommand:
        root_parser.print_help()
        return 0
    if args.subcommand != "init":
        if not vtes.VTES:
            logger.critical('VTES cards database is not initialized. Use "krcg init"')
            return 1
        if not twda.TWDA:
            logger.critical('TWDA database is not initialized. Use "krcg init"')
            return 1
    res = args.func(args)
    logger.setLevel(logging.NOTSET)  # reset log level so as to not mess up tests
    return res


def main():
    exit(execute(sys.argv[1:]))
