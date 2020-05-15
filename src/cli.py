"""Command-line interface.
"""
import argparse
import logging
import math
import sys

import arrow
import requests

from . import analyzer
from . import config
from . import twda
from . import vtes

logger = logging.getLogger()

# VTES configure must be done before parsing args
if vtes.VTES:
    vtes.VTES.configure()


def init(args):
    if args.cards:
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
            vtes.VTES.load_from_vekn()
            vtes.VTES.configure()
            twda.TWDA.load_from_vekn()
        except requests.exceptions.ConnectionError as e:
            logger.critical(
                "failed to connect to {}"
                " - check your Internet connection and firewall settings".format(
                    e.request.url
                )
            )
            exit(1)


def typical_copies(A, card_name):
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


def affinity(args):
    # build a condition matching options
    def condition(card):
        return (not args.crypt or vtes.VTES.is_crypt(card)) and (
            not args.library or vtes.VTES.is_library(card)
        )

    twda.TWDA.configure(args.date_from, args.date_to, args.players)
    A = analyzer.Analyzer()
    A.refresh(*args.cards, condition=condition, similarity=1)
    if len(A.examples) < 4:
        print("Too few example in TWDA.")
        if len(A.examples) > 0:
            print(
                "To see them:\n\tkrcg deck {}".format(
                    " ".join('"' + name + '"' for name in args.cards)
                )
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


def top(args):
    result = set(card["Id"] for card in vtes.VTES.original_cards.values())
    for type_ in args.type or []:
        result &= vtes.VTES.search["type"].get(type_.lower(), set())
    for clan in args.clan or []:
        clan = config.CLANS_AKA.get(clan.lower()) or clan
        result &= vtes.VTES.search["clan"].get(clan.lower(), set())
    # for group in data.get("group") or []:
    #     result &= vtes.VTES.search["group"].get(group.lower(), set())
    for trait in args.trait or []:
        result &= vtes.VTES.search["trait"].get(trait.lower(), set())
    for discipline in args.disc or []:
        discipline = config.DIS_MAP.get(discipline) or discipline
        result &= vtes.VTES.search["discipline"].get(discipline, set())
    for exclude in args.exclude_type or []:
        result -= vtes.VTES.search["type"].get(exclude.lower(), set())

    twda.TWDA.configure(args.date_from, args.date_to, args.players)
    A = analyzer.Analyzer()
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


def build(args):
    twda.TWDA.configure(args.date_from, args.date_to, args.players)
    print(vtes.VTES.deck_to_txt(analyzer.Analyzer().build_deck(*args.cards)))


def deck_(args):
    twda.TWDA.configure(args.date_from, args.date_to, args.players, spoilers=False)
    decks = {i: twda.TWDA[i] for i in args.cards_or_id if i in twda.TWDA}
    cards = [
        vtes.VTES.get_name(vtes.VTES[c]) for c in args.cards_or_id if c not in twda.TWDA
    ]
    if not decks:
        A = analyzer.Analyzer()
        try:
            A.refresh(*cards, similarity=1)
        except analyzer.AnalysisError:
            exit(1)
        decks.update(A.examples)
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
            print(vtes.VTES.deck_to_txt(example))
        else:
            print("[{}] {}".format(twda_id, example))


def card(args):
    for i, name in enumerate(args.cards):
        if i > 0:
            print()
        try:
            name = int(name)
        except ValueError:
            pass
        try:
            card = vtes.VTES[name]
        except KeyError:
            logger.critical("Card not found: {}".format(name))
            exit(1)
        print(vtes.VTES.get_name(card))
        if args.short:
            continue
        print(_card_text(card))
        print(_card_rulings(args, vtes.VTES.get_name(card)))


def _card_text(card):
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


def _card_rulings(args, card_name):
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


def complete(args):
    for name in vtes.VTES.complete(args.name.lower()):
        print(name)


# ############################################################################# argparse
def add_deck_boundaries(parser):
    """Common arguments: --from and --to to control year boundaries of TWDA analysis.
    """
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
        "--players",
        type=int,
        default=0,
        help="do not consider decks with less players than this",
    )


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
add_deck_boundaries(parser)
parser.add_argument(
    "-n", "--number", type=int, default=0, metavar="N", help="Number of cards to print",
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
    type=lambda a: vtes.VTES.get_name(vtes.VTES[a]),
    help="reference cards",
)
parser.set_defaults(func=affinity)


# ################################################################################## top
class NARGS_CHOICE_WITH_ALIASES(argparse.Action):
    # choices with nargs +/* : this is a known issue for argparse
    # cf. https://bugs.python.org/issue9625
    CHOICES = []
    ALIASES = {}

    def __call__(self, parser, namespace, values, option_string=None):
        values = [v.lower() for v in values]
        if values:
            for value in values:
                if value not in self.ALIASES:
                    raise argparse.ArgumentError(
                        self, f"invalid choice: {value} (choose from {self.CHOICES})"
                    )
        setattr(namespace, self.dest, [self.ALIASES[value] for value in values])


class DisciplineChoice(NARGS_CHOICE_WITH_ALIASES):
    CHOICES = vtes.VTES.search.get("discipline", {}).keys()
    ALIASES = dict(
        [(k.lower(), k) for k in vtes.VTES.search.get("discipline", {}).keys()]
        + list(config.DIS_MAP.items())
    )


class ClanChoice(NARGS_CHOICE_WITH_ALIASES):
    CHOICES = vtes.VTES.search.get("clan", {}).keys()
    ALIASES = dict(
        [(k.lower(), k) for k in vtes.VTES.search.get("clan", {}).keys()]
        + list(config.CLANS_AKA.items())
    )


class TypeChoice(NARGS_CHOICE_WITH_ALIASES):
    CHOICES = vtes.VTES.search.get("type", {}).keys()
    ALIASES = {k.lower(): k for k in vtes.VTES.search.get("type", {}).keys()}


class TraitChoice(NARGS_CHOICE_WITH_ALIASES):
    CHOICES = vtes.VTES.search.get("trait", {}).keys()
    ALIASES = {k.lower(): k for k in vtes.VTES.search.get("trait", {}).keys()}


parser = subparsers.add_parser(
    "top", help="display top cards (played in most TW decks)"
)
add_deck_boundaries(parser)
parser.add_argument(
    "-n", "--number", type=int, default=10, help="Number of cards to print (default 10)"
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
    metavar="Trait",
    nargs="+",
    help="Filter by trait ({})".format(
        ", ".join(vtes.VTES.search.get("trait", {}).keys())
    ),
)
parser.add_argument("-f", "--full", action="store_true", help="display card text")
parser.set_defaults(func=top)

# ################################################################################ build
parser = subparsers.add_parser("build", help="build a deck")
add_deck_boundaries(parser)
parser.add_argument(
    "cards",
    metavar="CARD",
    nargs="*",
    type=lambda a: vtes.VTES.get_name(vtes.VTES[a]),
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
    "cards_or_id", metavar="TXT", nargs="*", help="list TWDA decks from ID or cards"
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


def main():
    args = root_parser.parse_args(sys.argv[1:])
    logger.addHandler(logging.StreamHandler(sys.stderr))
    logger.setLevel(
        {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}[
            args.verbosity
        ]
    )
    if not args.subcommand:
        root_parser.print_help()
        return
    if args.subcommand != "init":
        if not vtes.VTES:
            logger.critical('VTES cards database is not initialized. Use "krcg init"')
            exit(1)
        if not twda.TWDA:
            logger.critical('TWDA database is not initialized. Use "krcg init"')
            exit(1)
    args.func(args)
