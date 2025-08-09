# KRCG

[![PyPI version](https://badge.fury.io/py/krcg.svg)](https://badge.fury.io/py/krcg)
[![Validation](https://github.com/lionel-panhaleux/krcg/actions/workflows/validation.yml/badge.svg)](https://github.com/lionel-panhaleux/krcg/actions/workflows/validation.yml)
[![Coverage](https://api.codacy.com/project/badge/Grade/32d1b809494e4935967608f13f52004a)](https://app.codacy.com/manual/lionel-panhaleux/krcg?utm_source=github.com&utm_medium=referral&utm_content=lionel-panhaleux/krcg&utm_campaign=Badge_Grade_Dashboard)
[![Python version](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-blue)](https://opensource.org/licenses/MIT)
[![Code Quality](https://img.shields.io/badge/style-ruff-46aef7?logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)

A Python package build to serve as an interface for
the VEKN [official card texts](http://www.vekn.net/card-lists)
and the [Tournament Winning Deck Archive (TWDA)](http://www.vekn.fr/decks/twd.htm).

It also contains an ever-growing list of cards rulings, that is kept up to date
thanks to the hard work of our contributors.

Portions of the materials are the copyrights and trademarks of Paradox Interactive AB,
and are used with permission. All rights reserved.
For more information please visit [white-wolf.com](http://www.white-wolf.com).

![Dark Pack](https://raw.githubusercontent.com/lionel-panhaleux/krcg/master/dark-pack.png)

## Offspring projects

The KRCG library has been used in multiple _offpsring_ projects:

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

[Python 3](https://www.python.org/downloads/) (>=3.10) is required.

Use pip to install the `krcg` tool:

```bash
pip install krcg
```

## Using the library

KRCG is a Python library for VTES.
The code is well-documented and can be explored using Python's built-in `help` function.

Here are a few quickstart examples to showcase how the library can be used:

### VTES

`krcg.vtes.VTES` is the cards library. Load it with `VTES.load()`.
This pulls data from the [KRCG static](https://static.krcg.org) server, where
it's already published in JSON.

Alternatively, use `VTES.load_from_vekn()` to load directly from the official
[VEKN CSV files](https://www.vekn.net/card-lists). This is slower and mainly
used for generating the static JSON.

Then you can access cards, complete card names, or search.

```python
>>> from krcg.vtes import VTES
>>> VTES.load()
>>> VTES["Alastor"].name
'Alastor'
>>> VTES["Alastor"].url
'https://static.krcg.org/card/alastor.jpg'
>>> VTES.complete("pentex")
['Pentex™ Loves You!',
 'Pentex™ Subversion',
 'Enzo Giovanni, Pentex Board of Directors',
 'Enzo Giovanni, Pentex Board of Directors (ADV)',
 'Harold Zettler, Pentex Director']
 >>> VTES.search(type=["political action"], sect=["anarch"], artist=["Drew Tucker"])
{<#100790 Free States Rant>}
>>> VTES.search(precon=["Fifth Edition: Nosferatu"])
{<#201534 Aunt Linda>,
 <#201536 Baixinho>,
 <#201537 Belinde>,
 <#100301 Carrion Crows>,
 <#100308 Cats' Guidance>,
 <#102213 Creeping Sabotage>,
 <#100515 Deep Song>,
 <#100698 Fame>,
 <#100863 Guard Dogs>,
 <#100866 Guardian Angel>,
 <#100897 Haven Uncovered>,
 <#201549 Horace Radcliffe>,
 <#100959 Immortal Grapple>,
 <#100995 Instinctive Reaction>,
 <#201553 Larissa Moreira>,
 <#201555 Lenny Burkhead>,
 <#101125 Lost in Crowds>,
 <#101254 Murder of Crows>,
 <#101321 On the Qui Vive>,
 <#101483 Preternatural Strength>,
 <#102214 Protected District>,
 <#101550 Raven Spy>,
 <#101564 Rebel>,
 <#102215 Roundhouse>,
 <#201568 Ryan>,
 <#101808 Slum Hunting Ground>,
 <#101811 Smiling Jack, The Anarch>,
 <#101945 Taste of Vitae>,
 <#201545 The Dowager>,
 <#101070 The Labyrinth>,
 <#102216 The Warrens>,
 <#102065 Underbridge Stray>,
 <#102113 Vessel>,
 <#102149 Warsaw Station>,
 <#201573 Wauneka>}
 >>> VTES.search(set=["Sword of Caine"], rarity=["Rare"])
{<#100167 Black Hand Emissary>,
 <#100314 Census Taker>,
 <#100360 Cloak of Blood>,
 <#100589 Drink the Blood of Ahriman>,
 <#100590 Drop Point Network>,
 <#100655 Epiphany>,
 <#100757 Follow the Blood>,
 <#100787 Framing an Ancient Grudge>,
 <#100865 Guarded Rubrics>,
 <#101024 Joseph Pander>,
 <#101111 Liquefy the Mortal Coil>,
 <#101161 Mantle of the Bestial Majesty>,
 <#101446 Praetorian Backer>,
 <#101489 Prison of the Mind>,
 <#101658 Ruins of Ceoris>,
 <#101724 Seraph's Second>,
 <#102057 The Uncoiling>,
 <#102022 Tribunal Judgment>,
 <#102027 Trophy: Chosen>,
 <#102158 Watchtower: The Wolves Feed>}
```

### Offline mode (LOCAL_CARDS=1)

You can use the library fully offline for cards and rulings by leveraging the
packaged CSV/YAML data.

- Set the environment variable `LOCAL_CARDS=1`.
- Load cards with `VTES.load_from_vekn()` (not `VTES.load()`).
- Cards and rulings will be loaded from the packaged YAML automatically.

Notes:

- The PyPI package includes a snapshot of CSV/YAML files at release time. For
  development from source, run `just sync-cards` to refresh them before packaging.
- Translations from VEKN are skipped in offline mode; only English text is
  available.
- TWDA still requires a local source: use a previously saved JSON via
  `TWDA.from_json(...)` or parse a downloaded `TWDA.html` with
  `TWDA.load_html(open("TWDA.html", encoding="utf-8"))`.
- Network-dependent helpers like `Deck.from_amaranth`, `Deck.from_vdb`,
  and `Deck.from_vtesdecks` are not available offline.

Example:

```python
>>> import os
>>> os.environ["LOCAL_CARDS"] = "1"
>>> from krcg.vtes import VTES
>>> VTES.load_from_vekn()
>>> VTES["Villein"].name
'Villein'
```

### TWDA, Analyzer and Deck

`krcg.twda.TWDA` interfaces the TWDA. Load it with `TWDA.load()` (from KRCG static).
`TWDA.load_from_vekn()` loads directly from VEKN and is considerably slower.

Once loaded, it can be used to browse the decks in it.

```python
>>> from krcg.twda import TWDA
>>> TWDA.load()
>>> TWDA["2019ecday2pf"]
<Deck #2019ecday2pf: Finnish Politics>
>>> print(TWDA["2019ecday2pf"].to_txt())
EC 2019 - Day 2
Paris, France
August 18th 2019
3R+F
50 players
Otso Saariluoma

-- 2GW3+1

Deck Name: Finnish Politics

Crypt (12 cards, min=4, max=38, avg=5.75)
-----------------------------------------
4x Anarch Convert     1 -none-                     Caitiff:ANY
3x Nana Buruku        8 ANI POT PRE                Guruhi:4
2x Nangila Were       9 ANI POT PRE obf ser        Guruhi:4
1x Enkidu, The Noah  11 ANI CEL OBF POT PRO for    Gangrel antitribu:4
1x Black Annis        9 OBF POT ani pro            Nosferatu antitribu:4
1x Andre LeRoux       3 aus                        Toreador:5

Library (65 cards)
Master (26; 6 trifle)
4x Anarch Revolt
1x Archon Investigation
6x Ashur Tablets
1x Dreams of the Sphinx
1x Fame
1x Giant's Blood
1x Information Highway
1x Mbare Market, Harare
2x Pentex(TM) Subversion
1x Powerbase: Luanda
1x Powerbase: Montreal
5x Villein
1x Wider View

Action (5)
3x Deep Song
1x Entrancement
1x Well-Marked

Retainer (1)
1x Mr. Winthrop

Reaction (6)
1x Cats' Guidance
1x Delaying Tactics
2x On the Qui Vive
2x Sense the Savage Way

Combat (26)
1x Canine Horde
5x Carrion Crows
1x Glancing Blow
5x Immortal Grapple
1x Mighty Grapple
1x Slam
1x Stunt Cycle
4x Taste of Vitae
2x Thrown Sewer Lid
4x Torn Signpost
1x Undead Strength

Event (1)
1x Dragonbound

>>> from datetime import date
>>> len([d for d in TWDA.values() if date(2019, 1, 1) < d.date < date(2020, 1, 1) and d.players_count >= 25])
27
```

The `krcg.analyzer` can provide statistics over a collection of decks:

```python
>>> from krcg.analyzer import Analyzer
>>> # You can analyze the whole TWDA, or a fragment of it, or any collection of decks
>>> A = Analyzer([d for d in TWDA.values() if date(2019, 1, 1) < d.date < date(2020, 1, 1)])
>>> # A blank refresh will provide basic statistics
>>> A.refresh()
>>> A.played.most_common(5)
[(<#100588 Dreams of the Sphinx>, 101),
 (<#101384 Pentex™ Subversion>, 96),
 (<#101321 On the Qui Vive>, 86),
 (<#102121 Villein>, 83),
 (<#100824 Giant's Blood>, 74)]
>>> A.average[VTES["Villein"]]
4.409638554216869
>>> A.variance[VTES["Villein"]]
3.6876179416461032
>>> # Refreshing with a list of cards computes card affinity using similar decks.
>>> # similarity=1 selects only decks that contain all provided cards.
>>> A.refresh(VTES["Aid from Bats"], similarity=1)
>>> # Now the candidates method can be used
>>> A.candidates(VTES["Aid from Bats"])[:5]
[(<#100515 Deep Song>, 1.0000000000000002),
 (<#100301 Carrion Crows>, 1.0000000000000002),
 (<#101945 Taste of Vitae>, 0.7777777777777779),
 (<#200185 Beetleman>, 0.6666666666666667),
 (<#100698 Fame>, 0.6666666666666667)]
```

The `krcg.seating` module provides functions to compute optimal seatings:

```python
>>> from krcg import seating
>>> # permutations gives you the list of players for each round
>>> seating.permutations(12, 3)
[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]
>>> # things get funny when you have 6, 7 or 11 players: you need more rounds
>>> # but not all players play every round
>>> seating.permutations(7, 3)
[[4, 5, 6, 7],
 [1, 2, 3, 7],
 [3, 4, 5, 6],
 [1, 2, 6, 7],
 [1, 2, 3, 4, 5]]
>>> # you can use the Round class to get tables from the permutations
>>> [seating.Round(p) for p in seating.permutations(14, 3)]
[[[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14]],
 [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14]],
 [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14]]]
>>> # and the optimise function to search for an optimal seating
>>> result, score = seating.optimise(seating.permutations(12, 3), iterations=50000)
>>> result
[[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
 [[2, 9, 6, 10], [12, 8, 1, 5], [3, 7, 4, 11]],
 [[11, 5, 10, 1], [6, 4, 12, 7], [8, 3, 9, 2]]]
>>> # score.rules gives a score over the nine official rules for optimal seating
>>> score.rules
[0, 0, 0.0, 9, 0, 0, 0, 1.118033988749895, 2]
>>> # you can inspect violations individually, e.g. pairs of players for R4:
>>> score.R4  # list of PairViolation(player_1=..., player_2=...)
>>> # for more details about the Score structure, check the docstring
>>> help(seating.Score)
```

And finally, the `krcg.deck.Deck` class can parse and manipulate decks.

```python
>>> from krcg.deck import Deck
>>> with open("First_Blood_Nosferatu.txt") as f:
>>>     deck = Deck.from_txt(f)
>>> deck.crypt
[(<#200549 Gustaphe Brunnelle>, 2),
 (<#200571 Harold Tanner>, 2),
 (<#200696 Jeremy "Wix" Wyzchovsky>, 2),
 (<#201116 Petra>, 2),
 (<#200185 Beetleman>, 2),
 (<#200190 Benjamin Rose>, 2)]
>>> deck.library
[(<#100698 Fame>, 2),
 (<#100070 Animalism>, 2),
 (<#101015 J. S. Simmons, Esq.>, 1),
 (<#101070 The Labyrinth>, 1),
 (<#101073 Laptop Computer>, 2),
 (<#101125 Lost in Crowds>, 6),
 (<#100093 Army of Rats>, 2),
 (<#101550 Raven Spy>, 4),
 (<#101808 Slum Hunting Ground>, 1),
 (<#100199 Blood Doll>, 6),
 (<#100029 Aid from Bats>, 12),
 (<#100308 Cats' Guidance>, 4),
 (<#100362 Cloak the Gathering>, 6),
 (<#100390 Computer Hacking>, 4)]
>>> # fetch a deck from Amaranth UID
>>> deck = Deck.from_amaranth("4d3aa426-70da-44b7-8cb7-92377a1a0dbd")
>>> deck.name
'First Blood: Tremere'
>>> deck.crypt
[(<Card #201020 Muhsin Samir>, 2),
 (<Card #201213 Rutor>, 2),
 (<Card #201388 Troius>, 2),
 (<Card #201501 Zane>, 2),
 (<Card #200025 Aidan Lyle>, 2),
 (<Card #200280 Claus Wegener>, 2)]
>>> print(deck.to_txt("lackey"))
1	Academic Hunting Ground
1	Arcane Library
4	Blood Doll
1	Chantry
2	Vast Wealth
12	Govern the Unaligned
1	Thadius Zho
4	.44 Magnum
1	Ivory Bow
2	Sport Bike
1	Charnas the Imp
6	Bonding
4	Enhanced Senses
5	Forced Awakening
5	On the Qui Vive
4	Precognition
4	Spirit's Touch
8	Telepathic Misdirection
8	Apportation
10	Theft of Vitae
2	Walk of Flame
Crypt:
2	Muhsin Samir
2	Rutor
2	Troius
2	Zane
2	Aidan Lyle
2	Claus Wegener
```

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

- `just quality` - Run code quality checks (ruff check, ruff format --check, mypy, pydoclint)
- `just test` - Run tests (includes quality)
- `just update` - Update dependencies and sync external CSV/YAML data
- `just clean` - Clean build artifacts
- `just sync-cards` - Sync CSV files from vtescsv and rulings from vtes-biased/vtes-rulings
- `just build` - Build the package
- `just release` - Bump version (minor), tag, push, and publish to PyPI

Publishing uses `uv publish` and reads the token from a `.pypi_token` file at the repository root.

## Contribute

Feel free to submit pull requests, they will be merged as long as they pass the tests.
Do not hestitate to submit issues or vote on them if you want a feature implemented.

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
