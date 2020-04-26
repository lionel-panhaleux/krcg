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


DEFAULT_COLOR = int("FFFFFF", 16)
COLOR_MAP = {
    "Master": int("35624E", 16),
    "Action": int("2A4A5D", 16),
    "Modifier": int("4B4636", 16),
    "Reaction": int("455773", 16),
    "Combat": int("6C221C", 16),
    "Retainer": int("9F613C", 16),
    "Ally": int("413C50", 16),
    "Equipment": int("806A61", 16),
    "Political Action": int("805A3A", 16),
    "Event": int("E85949", 16),
    "Imbued": int("F0974F", 16),
    "Abomination": int("30183C", 16),
    "Ahrimane": int("868A91", 16),
    "Akunanse": int("744F4E", 16),
    "Assamite": int("E9474A", 16),
    "Baali": int("A73C38", 16),
    "Blood Brother": int("B65A47", 16),
    "Brujah": int("2C2D57", 16),
    "Brujah antitribu": int("39282E", 16),
    "Caitiff": int("582917", 16),
    "Daughter of Cacophony": int("FCEF9B", 16),
    "Follower of Set": int("AB9880", 16),
    "Gangrel": int("2C342E", 16),
    "Gangrel antitribu": int("2A171A", 16),
    "Gargoyle": int("574B45", 16),
    "Giovanni": int("1F2229", 16),
    "Guruhi": int("1F2229", 16),
    "Harbinger of Skulls": int("A2A7A6", 16),
    "Ishtarri": int("865043", 16),
    "Kiasyd": int("916D32", 16),
    "Lasombra": int("C5A259", 16),
    "Malkavian": int("C5A259", 16),
    "Malkavian antitribu": int("C5A259", 16),
    "Nagaraja": int("D17D58", 16),
    "Nosferatu": int("5C5853", 16),
    "Nosferatu antitribu": int("442B23", 16),
    "Osebo": int("6B5C47", 16),
    "Pander": int("714225", 16),
    "Ravnos": int("82292F", 16),
    "Salubri": int("DA736E", 16),
    "Salubri antitribu": int("D3CDC9", 16),
    "Samedi": int("D28F3E", 16),
    "Toreador": int("DF867F", 16),
    "Toreador antitribu": int("C13B5E", 16),
    "Tremere": int("3F2F45", 16),
    "Tremere antitribu": int("3F2448", 16),
    "True Brujah": int("A12F2E", 16),
    "Tzimisce": int("67724C", 16),
    "Ventrue": int("430F28", 16),
    "Ventrue antitribu": int("5D4828", 16),
}


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
    card_type = "/".join(card["Type"])
    clan = "/".join(card.get("Clan", []))
    fields = [{"name": "Type", "value": card_type, "inline": True}]
    if card.get("Clan"):
        text = clan
        if card.get("Burn Option"):
            text += " (Burn Option)"
        if card.get("Capacity"):
            text += f" - Capacity {card['Capacity']}"
        if card.get("Group"):
            text += f" - Group {card['Group']}"
        fields.append({"name": "Clan", "value": text, "inline": True})
    if card.get("Pool Cost"):
        fields.append(
            {"name": "Cost", "value": f"{card['Pool Cost']} Pool", "inline": True}
        )
    if card.get("Blood Cost"):
        fields.append(
            {"name": "Cost", "value": f"{card['Blood Cost']} Blood", "inline": True}
        )
    if card.get("Conviction Cost"):
        fields.append(
            {
                "name": "Cost",
                "value": f"{card['Conviction Cost']} Conviction",
                "inline": True,
            }
        )
    if card.get("Disciplines"):
        fields.append(
            {
                "name": "Disciplines",
                "value": " ".join(card["Disciplines"]) or "None",
                "inline": False,
            }
        )
    fields.append(
        {
            "name": "Card Text",
            "value": card["Card Text"].replace("{", "").replace("}", ""),
            "inline": False,
        }
    )
    footer = ""
    if card.get("Banned") or card.get("Rulings"):
        rulings = ""
        if card.get("Banned"):
            rulings += f"**BANNED in {card['Banned']}**\n"
        links = {l["Reference"]: l["URL"] for l in card.get("Rulings Links", {})}
        for ruling in card.get("Rulings", []):
            ruling, _ = re.subn(r"{|}", "*", ruling)
            for reference in re.findall(r"\[\w+\s[0-9-]+\]", ruling):
                ruling = ruling.replace(
                    f"{reference}", f"[{reference}]({links[reference[1:-1]]})"
                )
            if len(rulings) + len(ruling) > 1020:
                rulings += "..."
                footer = "More rulings available, click the title to see them."
                break
            rulings += f"- {ruling}\n"
        fields.append({"name": "Rulings", "value": rulings, "inline": False})
    card_name = vtes.VTES.get_name(card)
    file_name = unidecode.unidecode(card_name).lower()
    file_name = file_name[4:] + "the" if file_name[:4] == "the " else file_name
    file_name, _ = re.subn(r"""\s|,|\.|-|—|'|:|\(|\)|"|!""", "", file_name)
    codex_url = "http://www.codex-of-the-damned.org/card-search/index.html?"
    codex_url += urllib.parse.urlencode({"card": card_name})
    image_url = f"http://www.codex-of-the-damned.org/card-images/{file_name}.jpg"
    color = COLOR_MAP.get(card_type, DEFAULT_COLOR)
    if card_type == "Vampire":
        color = COLOR_MAP.get(clan, DEFAULT_COLOR)
    embed = {
        "type": "rich",
        "title": card_name,
        "url": codex_url,
        "color": color,
        "fields": fields,
        "image": {"url": image_url},
        "footer": {"text": footer},
    }
    logger.info(embed)
    return {
        "content": "",
        "embed": discord.Embed.from_dict(embed),
    }


def main():
    logger.addHandler(logging.StreamHandler(sys.stderr))
    logger.setLevel(logging.INFO)
    vtes.VTES.load_from_vekn()
    vtes.VTES.configure()
    client.run(os.getenv("DISCORD_TOKEN"))
