import logging
import os
import re
import sys
import urllib.parse

import discord
import unidecode

from . import vtes

logger = logging.getLogger()
client = discord.Client()


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("krcg "):
        logger.info(f"Received: {message.content[5:]}")
        await message.channel.send(**handle_message(message.content[5:]))


def handle_message(message):
    message = message.lower()
    try:
        message = int(message)
    except ValueError:
        pass
    try:
        card = vtes.VTES[message]
    except KeyError:
        return {"content": f"Card not found: {message}"}
    text = f"[{'/'.join(card['Type'])}]"
    if card.get("Clan"):
        text += f"[{'/'.join(card['Clan'])}]"
    if card.get("Pool Cost"):
        text += f"[{card['Pool Cost']} Pool]"
    if card.get("Blood Cost"):
        text += f"[{card['Blood Cost']} Blood]"
    if card.get("Conviction Cost"):
        text += f"[{card['Conviction Cost']} Conviction]"
    if card.get("Capacity"):
        # strange bug: discord removes one pair of brackets
        text += f"[[Capacity {card['Capacity']}]]"
    if card.get("Group"):
        text += f"(g.{card['Group']})"
    if card.get("Burn Option"):
        text += "(Burn Option)"
    if card.get("Banned"):
        text += f" -- **BANNED in {card['Banned']}**"
    if "Disciplines" in card:
        text += "\n"
        text += " ".join(f"[{d}]" for d in card["Disciplines"]) or "-- No discipline"
    text += "\n"
    text += card["Card Text"].replace("{", "").replace("}", "")
    if "Rulings" in card:
        text += "\n\n---\n"
        for ruling in card["Rulings"]:
            text += ruling + "\n\n"
    # check max embed description lenght
    if len(text) > 2048:
        text = text[:2040] + "\n..."
    card_name = vtes.VTES.get_name(card)
    file_name = unidecode.unidecode(card_name).lower()
    file_name = file_name[4:] + "the" if file_name[:4] == "the " else file_name
    file_name, _ = re.subn(r"""\s|,|\.|-|—|'|:|\(|\)|"|!""", "", file_name)
    embed = discord.Embed(
        title=card_name,
        description=text,
        url="http://www.codex-of-the-damned.org/card-search/index.html?"
        + urllib.parse.urlencode({"card": card_name}),
    )
    embed.set_image(
        url=f"http://www.codex-of-the-damned.org/card-images/{file_name}.jpg"
    )
    return {
        "content": "",
        "embed": embed,
    }


def main():
    logger.addHandler(logging.StreamHandler(sys.stderr))
    logger.setLevel(logging.INFO)
    vtes.VTES.load_from_vekn()
    vtes.VTES.configure()
    client.run(os.getenv("DISCORD_TOKEN"))
