# KRCG

[![PyPI version](https://badge.fury.io/py/krcg.svg)](https://badge.fury.io/py/krcg)
[![Validation](https://github.com/lionel-panhaleux/krcg/actions/workflows/validation.yml/badge.svg)](https://github.com/lionel-panhaleux/krcg/actions/workflows/validation.yml)
[![Coverage](https://api.codacy.com/project/badge/Grade/32d1b809494e4935967608f13f52004a)](https://app.codacy.com/manual/lionel-panhaleux/krcg?utm_source=github.com&utm_medium=referral&utm_content=lionel-panhaleux/krcg&utm_campaign=Badge_Grade_Dashboard)
[![Python version](https://img.shields.io/badge/python-3.12+-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-blue)](https://opensource.org/licenses/MIT)
[![Code Quality](https://img.shields.io/badge/style-ruff-46aef7?logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)

A Python package built to serve as an interface for
the VEKN [official card texts](http://www.vekn.net/card-lists)
and the [Tournament Winning Deck Archive (TWDA)](http://www.vekn.fr/decks/twd.htm).

It also contains an ever-growing list of cards rulings, that is kept up to date
thanks to the hard work of our contributors.

Portions of the materials are the copyrights and trademarks of Paradox Interactive AB,
and are used with permission. All rights reserved.
For more information please visit [white-wolf.com](http://www.white-wolf.com).

![Dark Pack](https://raw.githubusercontent.com/lionel-panhaleux/krcg/main/dark-pack.png)

> **Upgrading from 4.x?** 5.0 is a ground-up rewrite with a new, handle-based
> API (no module-level singletons). See [Migrating from 4.x](#migrating-from-4x).

## Offspring projects

The KRCG library has been used in multiple _offspring_ projects:

-   [krcg-cli](https://github.com/lionel-panhaleux/krcg-cli) is a convenient
    Command Line Interface over the library

-   [krcg-static](https://github.com/lionel-panhaleux/krcg-static)
    is used to generate easy-to-use static files for web developers.
    It is available online at [static.krcg.org](https://static.krcg.org)

-   [krcg-api](https://github.com/lionel-panhaleux/krcg-api)
    is a free RESTful web API to get the most out of the library for web projects.
    It is available online at [v2.api.krcg.org](https://v2.api.krcg.org)

-   [krcg-bot](https://github.com/lionel-panhaleux/krcg-bot) is a friendly Discord bot
    that provides official card text and rulings for free.
    It is [available for free](https://discordapp.com/oauth2/authorize?client_id=703921850270613505&scope=bot).

Rulings have been outsourced to a separated, community-maintained project:
[`vtes-rulings`](https://github.com/vtes-biased/vtes-rulings)

## Installation

[Python 3](https://www.python.org/downloads/) (>=3.12) is required.

Use pip to install the `krcg` tool:

```bash
pip install krcg
```

## Using the library

KRCG is a Python library for VTES. There are no global singletons: you **load**
the cards (and, optionally, the deck archive) and hold the returned handle. The
code is well-documented and can be explored with Python's built-in `help`.

### Loading the cards

`krcg.load()` returns a `CardDict` — the cards library. There are three loaders:

| Function                      | Source                                        | Sync/async |
| ----------------------------- | --------------------------------------------- | ---------- |
| `krcg.load()`                 | version-keyed cache, else the packaged data   | sync       |
| `krcg.load_local()`           | always the packaged data (fully offline)      | sync       |
| `krcg.load_online(session)`   | the pre-built JSON on [static.krcg.org][s]    | async      |

[s]: https://static.krcg.org

```python
>>> import krcg
>>> cards = krcg.load()
>>> cards["Alastor"].full_name
'Alastor'
>>> cards["Alastor"].url
'https://static.krcg.org/card/alastor.jpg'
>>> cards[100038] is cards["Alastor"]      # look up by id or by any name variant
True
```

The packaged snapshot ships with the wheel, so `load_local()` works offline (no
environment variable needed); translations and rulings are included. Online
tools should prefer `load_online`, which is async and needs an
[`aiohttp`](https://docs.aiohttp.org) session:

```python
>>> import aiohttp, asyncio
>>> async def fetch_cards():
...     async with aiohttp.ClientSession() as session:
...         return await krcg.load_online(session)
>>> cards = asyncio.run(fetch_cards())
```

### Completion and search

`CardDict` owns the name-completion and search index:

```python
>>> [c.full_name for c in cards.complete("pentex")]
['Pentex™ Subversion',
 'Pentex™ Loves You!',
 'Enzo Giovanni, Pentex Board of Directors (G2)',
 'Enzo Giovanni, Pentex Board of Directors (G2 ADV)',
 'Harold Zettler, Pentex Director (G4)']
>>> # search takes keyword dimensions, each a list of values; returns a list of cards
>>> cards.search(type=["Political Action"], sect=["Anarch"], artist=["Drew Tucker"])
[100790|Free States Rant]
>>> cards.search(clan=["Banu Haqim"], title=["Justicar"])
[201598|Kasim Bayar, 201353|Tegyrius, Vizier (G2 ADV)]
>>> # the available dimensions and their possible values
>>> sorted(cards.search_dimensions)
['artist', 'bonus', 'capacity', 'city', 'clan', 'discipline', 'group', 'kind',
 'path', 'precon', 'rarity', 'sect', 'set', 'title', 'trait', 'type']
>>> # values may include None (cards with no value in that dimension)
>>> [d for d in cards.search_dimensions["discipline"] if d][:5]
['ABO', 'ANI', 'AUS', 'CEL', 'CHI']
```

Within a dimension, multiple values are OR'd (except `trait` / `discipline` /
`bonus`, which intersect); chain calls and combine the result lists for finer
control. Text dimensions (`name`, `card_text`, `flavor_text`) do prefix search
and accept a `lang` (English plus French/Spanish where translated).

### TWDA and decks

`krcg.twda` mirrors the cards loaders and returns a plain `dict[str, Deck]` keyed
by deck id (`load()` / `load_local()` / `load_online(session)`):

```python
>>> from krcg import twda
>>> decks = twda.load()
>>> len(decks)
4538
>>> deck = decks["2019ecday2pf"]
>>> deck.name, deck.player
('Finnish Politics', 'Otso Saariluoma')
>>> deck.event.name, deck.event.date, deck.event.players_count
('EC 2019 - Day 2', datetime.date(2019, 8, 18), 50)
```

A `Deck` is a dataclass: its `cards` is a `list[CardInDeck]` (filter by
`card.kind`), plus metadata (`name`, `author`, `player`, `comment`, `event`,
`score`). Serialize it with `krcg.providers` — `serialize_twd` renders the full
TWD format and needs the cards handle; the others don't:

```python
>>> from krcg import providers
>>> from krcg.models import Card
>>> sum(c.count for c in deck.cards if c.kind == Card.Kind.CRYPT)
12
>>> sum(c.count for c in deck.cards if c.kind == Card.Kind.LIBRARY)
65
>>> print(providers.serialize_twd(deck, cards))
EC 2019 - Day 2
Paris, France
August 18th 2019
3R+F
50 players
Otso Saariluoma
https://www.vekn.net/event-calendar/event/9327

-- 2GW8.5+1.5!

Deck Name: Finnish Politics

Crypt (12 cards, min=4, max=38, avg=5.75)
...
>>> providers.serialize_json_minimal(deck)["name"]      # also: serialize_txt/vdb/lackey/jol
'Finnish Politics'
```

For full JSON, encode the dataclass directly with `msgspec` (used internally, not
imposed on you): `msgspec.json.encode(deck)`.

Parse a decklist from any text source with `krcg.parser.deck_from_txt` (pass
`twda=True` for the positional TWDA tournament headers):

```python
>>> from krcg import parser
>>> decklist = """\
... Deck Name: First Blood: Nosferatu
...
... Crypt (12 cards)
... 2x Gustaphe Brunnelle
... 2x Harold Tanner
... 2x Jeremy "Wix" Wyzchovsky
... 2x Petra
... 2x Beetleman
... 2x Benjamin Rose
...
... Library (12 cards)
... 2x Fame
... 2x Animalism
... 6x Aid from Bats
... 2x Cloak the Gathering
... """
>>> deck = parser.deck_from_txt(decklist.splitlines(), cards)
>>> deck.name
'First Blood: Nosferatu'
>>> sum(c.count for c in deck.cards if c.kind == Card.Kind.LIBRARY)
12
>>> # a file object works too: parser.deck_from_txt(open("deck.txt"), cards)
```

Fetch a deck from a supported site (Amaranth, VDB, VTESDecks) with
`providers.fetch` (async):

```python
>>> async def grab(url):
...     async with aiohttp.ClientSession() as session:
...         return await providers.fetch(session, url, cards)
>>> deck = asyncio.run(grab("https://amaranth.vtes.co.nz/deck/4d3aa426-70da-44b7-8cb7-92377a1a0dbd"))
>>> deck.name
'First Blood: Tremere'
```

### Analyzer

`krcg.analyzer` provides statistics and card affinity over **any** collection of
decks — the whole TWDA, a slice of it, or your own decks. Each function takes the
cards handle to resolve cards, so results are keyed by `Card`:

```python
>>> from krcg import analyzer
>>> from datetime import date
>>> sample = [d for d in decks.values()
...           if d.event and date(2019, 1, 1) < d.event.date < date(2020, 1, 1)]
>>> # how many of the decks play each card
>>> analyzer.played(sample, cards).most_common(3)
[(100588|Dreams of the Sphinx, 107),
 (101384|Pentex™ Subversion, 101),
 (101321|On the Qui Vive, 94)]
>>> # average and variance of the copies played, among decks that play the card
>>> analyzer.stats(sample, cards)[cards["Villein"]]
(4.441860465116283, 3.6884802595997837)
>>> # cards most often sharing a deck with a reference card
>>> # (similarity=1 restricts to decks that actually play it)
>>> analyzer.affinity(sample, cards, cards["Aid from Bats"], similarity=1)[:3]
[(100515|Deep Song, 1.0), (100301|Carrion Crows, 1.0), (101945|Taste of Vitae, 0.818)]
>>> # synthesize a TWDA-like deck around one or more seed cards
>>> built = analyzer.build_deck(sample, cards, cards["Aid from Bats"])
```

### Seating

`krcg.seating` computes optimal tournament seatings against the nine official
VEKN criteria. Build the base rounds for your players, then optimise:

```python
>>> from krcg import seating
>>> # the base rounds for 12 players over 3 rounds (handles the 6/7/11 edge cases)
>>> rounds = seating.get_rounds(list(range(1, 13)), 3)
>>> list(rounds[0].iter_tables())
[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
>>> # pre-compute a full seating when attendance is fixed: fixed=1 keeps the
>>> # (arbitrary) first round and optimises the rest. The default (fixed=len-1)
>>> # only re-seats the last round — for building rounds one at a time as
>>> # attendance changes round to round.
>>> result, score = seating.optimise(rounds, iterations=50000, fixed=1)
>>> score.R1          # the mandatory predator-prey rule: no violations
[]
>>> score.rules       # one value per rule R1..R9 (minor rules R4/R8/R9 may remain)
[0, 0, 0.0, 9, 0, 0, 0, 0.37, 2]
>>> help(seating.Score)   # the full Score structure (R1..R9, deviations, totals)
```

## Migrating from 4.x

5.0 is a hard break. The headline changes:

- **No singletons.** `krcg.vtes.VTES` (the class and the module-level instance)
  is gone. Load a `CardDict` with `krcg.load()` / `load_local()` /
  `load_online(session)` and pass it where you need it. Likewise `krcg.twda.TWDA`
  is gone — `krcg.twda.load*()` returns a plain `dict[str, Deck]`.
- **Search / complete** moved onto the `CardDict`: `cards.search(...)`,
  `cards.complete(...)`, `cards.search_dimensions`. `search` returns a `list`.
- **Deck operations are free functions**, not methods:
  - `VTES.parse(...)` → `parser.deck_from_txt(source, cards, ...)`
  - `deck.to_txt("twd")` → `providers.serialize_twd(deck, cards)` (and
    `serialize_txt` / `serialize_vdb` / `serialize_lackey` / `serialize_jol` /
    `serialize_json_minimal`)
  - `Deck.from_amaranth/from_vdb/from_vtesdecks(...)` →
    `await providers.fetch(session, url, cards)`
- **Models are plain dataclasses.** `Deck` is no longer a `collections.Counter`:
  its cards are a `list[CardInDeck]` — filter by `card.kind` instead of the old
  `deck.crypt` / `deck.library` views. Cards expose `full_name` / `unique_name` /
  `printed_name` (there is no `.name`).
- **JSON:** `Deck.to_json()` / `from_json()` are gone — use `msgspec`
  (`msgspec.json.encode(deck)`), or `providers.serialize_json_minimal(deck)`.
- **Network I/O is async** (`aiohttp`); `load_online` / `fetch` take a session.
- **Offline mode** no longer uses `LOCAL_CARDS` — `load_local()` is the offline
  path. HTML scraping of the TWDA is gone (the archive ships bundled).
- **Renames:** `seating.permutations` → `seating.get_rounds`; the `analyzer.Analyzer`
  class → the free functions `played` / `stats` / `affinity` / `build_deck`.
- TWD scores now serialize in krcg's canonical form.

See the [CHANGELOG](CHANGELOG.rst) for the full list.

## Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and packaging, with
`just` recipes for common tasks.

### Setup

1. Install `uv` if you haven't already:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone the repository and install dependencies:

   ```bash
   git clone https://github.com/lionel-panhaleux/krcg.git
   cd krcg
   uv sync --group dev
   ```

### Development Commands

- `just quality` - Run code quality checks (ruff check, ruff format --check, ty check)
- `just test` - Run tests (includes quality)
- `just update` - Update dependencies and sync external CSV/YAML data
- `just clean` - Clean build artifacts
- `just sync-cards` - Sync CSV files from vtescsv and rulings from vtes-biased/vtes-rulings
- `just build` - Build the package
- `just release` - Bump version (minor), tag, push, and publish to PyPI

Publishing uses `uv publish` and reads the token from a `.pypi_token` file at the repository root.

## Contribute

Feel free to submit pull requests, they will be merged as long as they pass the tests.
Do not hesitate to submit issues or vote on them if you want a feature implemented.

### Design considerations

The package uses no database by design.
The TWDA, search engine and cards dict are kept in memory for better performances.
The whole library generates a memory footprint between 128MB and 256MB.

The package uses external data sources for card list, so that it needs not be updated
when new sets are released or official VEKN CSV files are changed: it can use
new data sets as soon as they're available.

### Rulings

Rulings are sourced from the community-maintained repository
[`vtes-biased/vtes-rulings`](https://github.com/vtes-biased/vtes-rulings).
Please submit changes there. This library consumes those YAML files directly
(a current copy is synced upon each release under the `cards/` package).
