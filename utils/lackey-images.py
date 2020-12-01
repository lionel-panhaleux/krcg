#!/usr/bin/env python3
import aiofile
import aiohttp
import asyncio
import html.parser
import os


BASE_URL = "https://lackeyccg.com/vtes/high/cards/"


class IndexParser(html.parser.HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cards = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        url = dict(attrs)["href"]
        if url[-3:] != "jpg":
            return
        self.cards.append(url)


async def fetch_file(session, card):
    async with session.get(BASE_URL + card) as response:
        content = await response.read()
    async with aiofile.async_open("images/" + card, "wb") as afp:
        await afp.write(content)


async def fetch_all():
    parser = IndexParser()
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL) as response:
            index = await response.text()
            parser.feed(index)
        await asyncio.gather(*(fetch_file(session, card) for card in parser.cards))


def main():
    os.makedirs("images", exist_ok=True)
    asyncio.run(fetch_all())


if __name__ == "__main__":
    main()
