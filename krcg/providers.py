"""External tools providers: Deck building, archive, online play."""

from typing import Any
import aiohttp
import arrow
import itertools
import logging
import urllib.parse

from . import models
from . import utils
from . import collections

LOG = logging.getLogger("krcg")


async def get_amaranth_cards_map(
    session: aiohttp.ClientSession, cards_dict: collections.CardDict
) -> dict[str, models.Card]:
    """Get the Amaranth cards map."""
    async with session.get("http://static.krcg.org/data/amaranth_ids.json") as response:
        data = await response.json()
        return {k: cards_dict[v] for k, v in data.items()}


async def fetch(
    session: aiohttp.ClientSession,
    url: str,
    cards_dict: collections.CardDict,
) -> models.Deck:
    """Fetch a deck from a supported deckbuilding website."""
    result = urllib.parse.urlparse(url)
    match result.netloc:
        case "amaranth.vtes.co.nz":
            return await fetch_amaranth(session, result, cards_dict)
        case "vdb.im":
            return await fetch_vdb(session, result, cards_dict)
        case "vtesdecks.com":
            return await fetch_vtesdecks(session, result, cards_dict)
        case _:
            raise ValueError("Unknown deck URL provider")


async def fetch_vdb(
    session: aiohttp.ClientSession,
    url: urllib.parse.ParseResult,
    cards_dict: collections.CardDict,
) -> models.Deck:
    """Fetch a deck from VDB."""
    if not url.path.startswith("/decks"):
        raise ValueError("Unknown VDB URL path")
    params = urllib.parse.parse_qs(url.query)
    if "id" in params:
        uid = params["id"][0]
    elif url.path.startswith("/decks/"):
        uid = url.path[7:]
    # no ID in paramse, try to parse "deck in URL" format
    elif url.fragment:
        ret = models.Deck(
            id="",
            name=params.get("name", [None])[0] or "",
            author=params.get("author", [None])[0] or "",
            comment=params.get("description", [""])[0],
        )
        for item in url.fragment.split(";"):
            cid, count_str = item.split("=", 1)
            count = int(count_str)
            if count <= 0:
                continue
            utils.add_card(ret, cards_dict[int(cid)], count)
        return ret
    fetch_url = "https://vdb.im/api/deck/" + uid
    async with session.get(fetch_url) as response:
        data = await response.json()
        LOG.debug("VDB replied: %s", data, extra={"url": fetch_url})
    ret = models.Deck(
        id=uid,
        author=data.get("author", data.get("owner", None)),
        name=data.get("name", None),
        comment=data.get("description", ""),
    )
    for cid, count in data["cards"].items():
        count = int(count)
        if count <= 0:
            continue
        utils.add_card(ret, cards_dict[int(cid)], count)
    utils.sort_cards(ret)
    return ret


async def fetch_amaranth(
    session: aiohttp.ClientSession,
    url: urllib.parse.ParseResult,
    cards_dict: collections.CardDict,
) -> models.Deck:
    """Fetch a deck from Amaranth."""
    async with session.get("http://static.krcg.org/data/amaranth_ids.json") as response:
        amaranth_map = await response.json()
    if not url.path.startswith("/deck/"):
        raise ValueError("Invalid URL")
    uid = url.path[6:]
    fetch_url = "https://amaranth.vtes.co.nz/api/deck?id=" + uid
    async with session.get(fetch_url) as response:
        response.raise_for_status()
        data = await response.json()
        LOG.debug("Amaranth replied: %s", data, extra={"url": fetch_url})
    result = data["result"]
    ret = models.Deck(
        id=uid,
        author=result.get("author", None),
        name=result.get("title", None),
        comment=result.get("description", ""),
    )
    for cid, count in result["cards"].items():
        count = int(count)
        if count <= 0:
            continue
        utils.add_card(ret, cards_dict[amaranth_map[cid]], count)
    utils.sort_cards(ret)
    return ret


async def fetch_vtesdecks(
    session: aiohttp.ClientSession,
    url: urllib.parse.ParseResult,
    cards_dict: collections.CardDict,
) -> models.Deck:
    """Fetch a deck from VTESDecks."""
    if not url.path.startswith("/deck/"):
        raise ValueError("Invalid URL")
    uid = url.path[6:]
    fetch_url = "https://api.vtesdecks.com/1.0/decks/" + uid
    async with session.get(fetch_url) as response:
        response.raise_for_status()
        data = await response.json()
        LOG.debug("VTESDecks replied: %s", data, extra={"url": fetch_url})
        ret = models.Deck(
            id=uid,
            author=data.get("author", None),
            name=data.get("name", None),
            comment=data.get("description", ""),
        )
        for card in itertools.chain(data["crypt"], data["library"]):
            count = int(card["number"])
            if count <= 0:
                continue
            utils.add_card(ret, cards_dict[int(card["id"])], count)
        utils.sort_cards(ret)
        return ret


def serialize_lackey(deck: models.Deck) -> str:
    """Serialize a deck to LackeyCCG format."""
    lines = []
    for _, cards_ in utils.sorted_library(deck):
        for card in cards_:
            lines.append(f"{card.count}\t{utils.vekn_name(card)}")
    lines.append("Crypt:")
    for card in utils.sorted_crypt(deck):
        lines.append(f"{card.count}\t{utils.vekn_name(card)}")
    return "\n".join(lines)


def serialize_jol(deck: models.Deck) -> str:
    """Serialize a deck to JOL format."""
    lines = []
    for card in utils.sorted_crypt(deck):
        lines.append(f"{card.count}x {utils.vekn_name(card)}")
    lines.append("")
    for _, cards_ in utils.sorted_library(deck):
        for card in cards_:
            lines.append(f"{card.count}x {utils.vekn_name(card)}")
    return "\n".join(lines)


def serialize_vdb(deck: models.Deck) -> str:
    """Serialize a deck to VDB "deck in URL" format."""
    ret = "https://vdb.im/decks/deck"
    params = {}
    if deck.name:
        params["name"] = deck.name
    if deck.author:
        params["author"] = deck.author
    if params:
        ret += "?" + urllib.parse.urlencode(params)
    ret += "#"
    ret += ";".join(f"{card.id}={card.count}" for card in deck.cards)
    return ret


def serialize_json_minimal(deck: models.Deck) -> dict[str, Any]:
    """Serialize a deck to a minimal JSON format."""
    ret: dict[str, Any] = {}
    if deck.id:
        ret["id"] = deck.id
    if deck.name:
        ret["name"] = deck.name
    if deck.author:
        ret["author"] = deck.author
    ret["cards"] = {str(card.id): card.count for card in deck.cards}
    return ret


def serialize_twd(deck: models.Deck, cards_dict: collections.CardDict) -> str:
    """Serialize a deck to TWD format.

    Args:
        deck: The deck to serialize.
        cards_dict: The cards database.
    """
    raven = deck.raven
    lines = []
    if deck.event and deck.event.name:
        lines.append(deck.event.name)
    if deck.event and deck.event.place:
        lines.append(deck.event.place)
    if deck.event and deck.event.date:
        date_str = arrow.get(deck.event.date).format("MMMM Do YYYY")
        if deck.event.end_date:
            date_str += " -- " + arrow.get(deck.event.end_date).format("MMMM Do YYYY")
        lines.append(date_str)
    if deck.event and deck.event.rounds:
        lines.append(
            f"{deck.event.rounds}R+F"
            if deck.event.finals
            else f"{deck.event.rounds}R (no final)"
        )
    if deck.event and deck.event.players_count:
        lines.append(f"{deck.event.players_count} players")
    if deck.player:
        lines.append(deck.player)
    if deck.event and deck.event.url:
        lines.append(deck.event.url)
    if lines:
        lines.append("")
    if deck.score:
        lines.append(f"-- {deck.score}")
        lines.append("")
    if deck.name:
        lines.append(f"Deck Name: {deck.name}")
    if deck.author:
        lines.append(f"Created by: {deck.author}")
    if deck.comment:
        if deck.name or deck.author:
            lines.append("")
        lines.append(deck.comment)
    elif lines and lines[-1] != "":
        lines.append("")
    crypt: list[tuple[models.CryptCard, int, str]] = []
    for c in deck.cards:
        if c.kind != models.Card.Kind.CRYPT:
            continue
        card = cards_dict[c.id]
        assert isinstance(card, models.CryptCard)
        crypt.append((card, c.count, c.comment))
    crypt.sort(key=lambda t: (-t[1], -(t[0].capacity or 0), utils.vekn_name(t[0])))
    cap = sorted(
        itertools.chain.from_iterable([card.capacity or 0] * n for card, n, _ in crypt)
    )
    cap_min = sum(cap[:4])
    cap_max = sum(cap[-4:])
    cap_avg = sum(cap) / len(cap)
    lines.append(
        f"Crypt ({sum(c[1] for c in crypt)} cards, "
        f"min={cap_min}, max={cap_max}, avg={round(cap_avg, 2):g})"
    )
    lines.append("-" * len(lines[-1]))
    # flatten to display rows, applying the legacy Camille/Raven split so
    # pre-merge lists re-serialize to their original two-line form
    rows = []
    for card, count, comment in crypt:
        name = utils.vekn_name(card, ascii=False)
        # superior (UPPER) before inferior (lower); legacy vis trigram for vision
        disc = (
            " ".join(sorted({"vin": "vis"}.get(d, d) for d in card.disciplines))
            or "-none-"
        )
        title = card.title.lower() if card.title else ""
        path = card.path.split()[0] if card.path else ""
        group = (
            "ANY"
            if not card.group or card.group == models.Group.Any
            else card.group.value[1:]
        )
        clan = f"{card.clan}:{group}"
        if name == "Camille Devereux, The Raven" and raven:
            rows.append(
                (count - raven, "Camille Devereux", 5, "FOR PRO ani", "", "", clan, "")
            )
            name, count = "Raven", raven
        rows.append((count, name, card.capacity or 0, disc, path, title, clan, comment))
    max_cnt = max(len(f"{r[0]}x") for r in rows)
    max_name = max(len(r[1]) for r in rows)
    cap_w = max(len(str(r[2])) for r in rows)
    max_disc = max(len(r[3]) for r in rows)
    max_path = max(len(r[4]) for r in rows)
    max_title = max(len(r[5]) for r in rows)
    max_clan = max(len(r[6]) for r in rows)
    for count, name, capacity, disc, path, title, clan, comment in rows:
        cnt = f"{count}x"
        line = (
            f"{cnt:<{max_cnt}} {name:<{max_name}}  "
            f"{capacity:>{cap_w}}  {disc:<{max_disc}}  "
        )
        if max_path:
            line += f"{path:<{max_path}}  "
        if max_title:
            line += f"{title:<{max_title}}  "
        if comment:
            line += f"{clan:<{max_clan}}  -- {comment.replace(chr(10), ' ').strip()}"
        else:
            line += clan
        lines.append(line)
    library_count = sum(
        c.count for c in deck.cards if c.kind == models.Card.Kind.LIBRARY
    )
    lines.append(f"\nLibrary ({library_count} cards)")
    for i, (type_, cards_) in enumerate(utils.sorted_library(deck)):
        trifle_count = ""
        if type_ == "Master":
            n_trifle = sum(
                c.count
                for c in cards_
                if isinstance((lib := cards_dict[c.id]), models.LibraryCard)
                and lib.trifle
            )
            trifle_count = f"; {n_trifle} trifle" if n_trifle else ""
        cr = "\n" if i > 0 else ""
        lines.append(f"{cr}{type_} ({sum(c.count for c in cards_)}{trifle_count})")
        for c in cards_:
            name = utils.vekn_name(c, ascii=False)
            if c.comment:
                comment = c.comment.replace("\n", " ").strip()
                lines.append(f"{c.count}x {name:<23} -- {comment}")
            else:
                lines.append(f"{c.count}x {name}")
    return "\n".join(lines)


def serialize_txt(deck: models.Deck) -> str:
    """Serialize a deck to text. TWD-inspired, but no cards database is required.

    Args:
        deck: The deck to serialize.
    """
    lines = []
    if deck.event and deck.event.name:
        lines.append(deck.event.name)
    if deck.event and deck.event.place:
        lines.append(deck.event.place)
    if deck.event and deck.event.date:
        date_str = arrow.get(deck.event.date).format("MMMM Do YYYY")
        if deck.event.end_date:
            date_str += " -- " + arrow.get(deck.event.end_date).format("MMMM Do YYYY")
        lines.append(date_str)
    if deck.event and deck.event.format:
        lines.append(deck.event.format)
        if deck.event.rounds:
            lines[-1] += (
                f" {deck.event.rounds}R+F"
                if deck.event.finals
                else f" {deck.event.rounds}R (no final)"
            )
    if deck.event and deck.event.players_count:
        lines.append(f"{deck.event.players_count} players")
    if deck.player:
        lines.append(deck.player)
    if deck.event and deck.event.url:
        lines.append(deck.event.url)
    if lines:
        lines.append("")
    if deck.score:
        lines.append(f"-- {deck.score}")
        lines.append("")
    if deck.name:
        lines.append(f"Deck Name: {deck.name}")
    if deck.author:
        lines.append(f"Created by: {deck.author}")
    if deck.comment:
        if deck.name or deck.author:
            lines.append("")
        lines.append(deck.comment)
    elif lines and lines[-1] != "":
        lines.append("")
    crypt = utils.sorted_crypt(deck)
    lines.append(f"Crypt ({sum(card.count for card in crypt)} cards)")
    lines.append("-" * len(lines[-1]))
    for card in crypt:
        lines.append(f"{card.count}x {card.unique_name}")
    library = list(utils.sorted_library(deck))
    lines.append(
        f"\nLibrary ({sum(card.count for _, cards in library for card in cards)} cards)"
    )
    lines.append("-" * (len(lines[-1]) - 1))
    for type, cards in library:
        lines.append(f"\n--{type} ({sum(card.count for card in cards)})--")
        for card in cards:
            lines.append(f"{card.count}x {card.unique_name}")
            if card.comment:
                comment = card.comment.replace("\n", " ").strip()
                lines[-1] += f" -- {comment}"
    return "\n".join(lines)
