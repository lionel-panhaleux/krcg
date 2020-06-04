# KRCG

[![PyPI version](https://badge.fury.io/py/krcg.svg)](https://badge.fury.io/py/krcg)
[![Validation](https://github.com/lionel-panhaleux/krcg/workflows/Validation/badge.svg)](https://github.com/lionel-panhaleux/krcg/actions)
[![Coverage](https://api.codacy.com/project/badge/Grade/32d1b809494e4935967608f13f52004a)](https://app.codacy.com/manual/lionel-panhaleux/krcg?utm_source=github.com&utm_medium=referral&utm_content=lionel-panhaleux/krcg&utm_campaign=Badge_Grade_Dashboard)
[![Python version](https://img.shields.io/badge/python-3.8-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-blue)](https://opensource.org/licenses/MIT)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

A command-line interface based on
the VEKN [official card texts](http://www.vekn.net/card-lists)
and the [Tournament Winning Deck Archive (TWDA)](http://www.vekn.fr/decks/twd.htm)

Portions of the materials are the copyrights and trademarks of Paradox Interactive AB,
and are used with permission. All rights reserved.
For more information please visit [white-wolf.com](http://www.white-wolf.com).

![Dark Pack](dark-pack.png)

## Online API

KRCG is available as an [online API](https://api.krcg.org/).
Feel free to use it. Beware that this is still a beta, so breaking change can happen without notice.

## Discord BOT

KRCG is available as a
[Discord Bot](https://discordapp.com/oauth2/authorize?client_id=703921850270613505&scope=bot).
Feel free to use it in your server.

It lets you retrieve cards official text, image and rulings:
![Bot Example](https://raw.githubusercontent.com/lionel-panhaleux/krcg/master/bot-example.png)

## Static Files

KRCG provides normalized static files for third parties, they can be found in the
[static](https://github.com/lionel-panhaleux/krcg/blob/master/static) folder:

- `amaranth-twda.json`: The TWDA in JSON format for Amaranth (card IDs are Amaranth specific).
- `standard-rulings.json`: The rulings in JSON format
- `twd.htm`: A normalized version of the TWDA

The schemas for the JSON files can be found in the
[schemas](https://github.com/lionel-panhaleux/krcg/blob/master/schemas) folder.

## Contribute

Feel free to submit pull requests, they will be merged as long as they pass the tests.
Do not hestitate to submit issues or vote on them if you want a feature implemented.

### Contribute Rulings (non-developers)

Please do not hestitate to contribute rulings: all help is welcome.

Open an [issue](https://github.com/lionel-panhaleux/krcg/issues)
with a ruling you think should be added,
provide a link to an online post by one of the rules directors:

-   From 2016-12-04 onward, [Vincent Ripoll (ANK)](http://www.vekn.net/forum/news-and-announcements/75402-new-inner-circle-vekn-board-of-directors#79470)
-   From 2011-07-06 onward, [Pascal Bertrand (PIB)](https://groups.google.com/d/msg/rec.games.trading-cards.jyhad/VzRGZO_Iuto/BjJGRVvJ5Z8J)
-   From 1998-06-22 onward, [L. Scott Johnson (LSJ)](https://groups.google.com/d/msg/rec.games.trading-cards.jyhad/RIX1tLgOFjg/xKikfSarfd8J)
-   From 1994-12-15 onward, [Thomas R Wylie (TOM)](https://groups.google.com/d/msg/rec.games.trading-cards.jyhad/Dm_gIP3YvUs/qTyKyq2NWv4J)

### Contribute Rulings (developers)

Feel free to contribute rulings as Pull Requests directly, this is very appreciated.

Add the ruling link to
[rulings-links.yaml](https://github.com/lionel-panhaleux/krcg/blob/master/src/rulings-links.yaml),
and the ruling itself to
[cards-rulings.yaml](https://github.com/lionel-panhaleux/krcg/blob/master/src/cards-rulings.yaml) or
[general-rulings.yaml](https://github.com/lionel-panhaleux/krcg/blob/master/src/general-rulings.yaml)
depending on the case.

The format is mostly self-explanatory:

-   Cards are reference by ID and name in the format `ID|Name`.

-   Card names inside rulings text should be between bracers, eg. `{.44 Magnum}`

-   Individual rulings in `cards-rulings.yaml` must provide one or more references
    to ruling links at the end of the text, between brackets, eg `[LSJ 20100101]`

In doing so, please follow the following guidelines:

-   Keep the YAML files clean and alphabetically sorted (you can use a YAML formatter)

-   Make the rulings as concise as possible

-   Prefix the ruling with the discipline level and/or type the ruling applies to (if any),
    eg. prefix with `[PRO] [COMBAT]` if the ruling applies only to the card played in combat at superior Protean.

-   Adapt the ruling wording to the cards it applies to (ie. use masculine/feminin forms)

-   You can run the tests with the `pytest` command to check everything is OK

## Installation

[Python 3](https://www.python.org/downloads/) is required.

Use pip to install the `krcg` tool:

```bash
pip install krcg
```

### Hosting the web API

To host the web API, you need to install the `web` version of krcg:

```bash
pip install krcg[web]
```

No wsgi server is installed by default, you need to install one.
HTTP web servers can then easily be configured to serve WSGI applications,
check the documentation of your web server.

The API can be served with [uWSGI](https://uwsgi-docs.readthedocs.io):

```bash
uwsgi --module src.wsgi:application
```

or [Gunicorn](https://gunicorn.org):

```bash
gunicorn src.wsgi:application
```

Two environment variables are expected: `GITHUB_USERNAME` and `GITHUB_TOKEN`,
to allow the API to connect to Github as a user in order to post new rulings
as issues on the repository (`/submit-ruling` endpoint).

See the [Github help](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)
on how to generate a personal token for the account you want KRCG to use.

#### Development

The development version of KRCG installs uWSGI to serve the API,
this is the preferred WSGI server for now.

```bash
$ pip install -e ".[dev,web]"
$ make serve
...
uwsgi socket 0 bound to TCP address 127.0.0.1:8000
```

You can check the API is running by using your browser
on the provided address [http://127.0.0.1:8000](http://127.0.0.1:8000).

The environment variables `GITHUB_USERNAME` and `GITHUB_TOKEN` can be provided
by a personal `.env` file at the root of the krcg folder (ignored by git):

```bash
export GITHUB_USERNAME="dedicated_github_username_for_the_api"
export GITHUB_TOKEN="the_matching_github_token"
```

### Hosting the bot

If you need to host a new version of the bot yourself,
[Python 3](https://www.python.org/downloads/) is required, as well as an
environment variable `DISCORD_TOKEN`, for the bot to run.
The token can be found on your
[Discord applications page](https://discord.com/developers/applications).

The preferred way to run the bot is to use a python virtualenv:

```bash
/usr/bin/python3 -m venv venv
source venv/bin/activate
pip install krcg
DISCORD_TOKEN=discord_token_of_your_bot
krcg-bot
```

A [systemd](https://en.wikipedia.org/wiki/Systemd) unit can be used
to configure the bot as a system service:

```ini
[Unit]
Description=krcg-bot
After=network-online.target

[Service]
Type=simple
Restart=always
WorkingDirectory=directory_where_krcg_is_installed
Environment=DISCORD_TOKEN=discord_token_of_your_bot
ExecStart=/bin/bash -c 'source venv/bin/activate && krcg-bot'

[Install]
WantedBy=multi-user.target
```

In development the environment variable `DISCORD_TOKEN` can be provided
by a personal `.env` file at the root of the krcg folder (ignored by git):

```bash
export DISCORD_TOKEN="discord_token_of_your_bot"
```

### Command line

An internet connection is required to initialize krcg with official VEKN data
(cards list and TWDA).

```bash
krcg init
```

Use the help command for a full documentation of the tool:

```bash
krcg --help
```

And also extensive help on each sub-command:

```bash
krcg [COMMAND] --help
```

Note most commands only take decks from 2008 on in consideration.
You can use the `--from` and `--to` parameters to control the date range.

#### Examples

Get a card text (case is not relevant,
some abbreviations and minor misspellings will be understood):

```bash
$ krcg card krcg
KRCG News Radio
[Master][2P] -- (Jyhad:U, VTES:U, CE:U, LoB:PA, LotN:PG, KoT:U/PB, SP:PwN1 - #101067)
Unique location.
Lock to give a minion you control +1 intercept.
Lock and burn 1 pool to give a minion controlled by another Methuselah +1 intercept.
```

This provides rulings, if any:

```bash
$ krcg card ".44 magnum"
.44 Magnum
[Equipment][2P] -- (Jyhad:C, VTES:C, Sabbat:C, SW:PB, CE:PTo3, LoB:PO3, FB:PTr2 - #100001)
Weapon: gun.
Strike: 2R damage, with 1 optional maneuver each combat.

-- Rulings
Provides only ony maneuver each combat, even if the bearer changes. [LSJ 19980302-2]
```

Use the `-l` option to get ruling links:

```bash
$ krcg card -l ".44 magnum"
.44 Magnum
[Equipment][2P] -- (Jyhad:C, VTES:C, Sabbat:C, SW:PB, CE:PTo3, LoB:PO3, FB:PTr2 - #100001)
Weapon: gun.
Strike: 2R damage, with 1 optional maneuver each combat.

-- Rulings
Provides only ony maneuver each combat, even if the bearer changes. [LSJ 19980302-2]
[LSJ 19980302-2]: https://groups.google.com/d/msg/rec.games.trading-cards.jyhad/9YVFkeiL3Js/4UZXMyicluwJ
```

List TWDA decks containing a card:

```bash
$ krcg deck "Fame"
[2016gncbg] weenie animalism minimal: "Ich bin eine von wir"
[2016amfb] Gangrel e Garou
[2016ukncle] (No Name)
[2016ecday1gi] (No Name)
[2016saclcqspb] "Choquinho"
...
```

Display any TWDA deck:

```bash
$ krcg deck 2016gncbg
German NC 2016
Bochum, Germany
December 3rd 2016
3R+F
19 players
Bram van Stappen

Deck Name: weenie animalism minimal: "Ich bin eine von wir"
Description:
played (untested) at the German Nationals 03.12.2016, Bochum


-- Crypt: (12 cards)
---------------------------------------
2  Stick                               3  ANI                       Nosferatu antitribu:4
1  Janey Pickman                       6  for ANI PRO               Gangrel antitribu:4
1  Célèste Lamontagne                  5  for ANI PRO               Gangrel antitribu:4
1  Effie Lowery                        5  obf ANI SPI               Ahrimane:4
1  Sahana                              5  pre pro spi ANI           Ahrimane:4
1  Yuri Kerezenski                     5  aus for vic ANI           Tzimisce:4
1  Beetleman                           4  obf ANI                   Nosferatu:4
1  Bobby Lemon                         4  pro ANI                   Gangrel:3
1  Mouse                               2  ani                       Nosferatu:3
1  Zip                                 2  ani                       Ravnos:3
1  Lisa Noble                          1  ani                       Caitiff:3
-- Library (90)
-- Master (12)
5  Blood Doll
2  Powerbase: Montreal
1  Direct Intervention
1  Fame
1  KRCG News Radio
1  Pentex(TM) Subversion
1  Rack, The
-- Action (14)
10 Deep Song
2  Abbot
1  Aranthebes, The Immortal
1  Army of Rats
-- Combat (38)
16 Aid from Bats
11 Carrion Crows
6  Taste of Vitae
2  Canine Horde
2  Terror Frenzy
1  Pack Alpha
-- Reaction (18)
5  Cats' Guidance
5  On the Qui Vive
4  Forced Awakening
3  Delaying Tactics
1  Wake with Evening's Freshness
-- Equipment (1)
1  Sniper Rifle
-- Retainer (7)
6  Raven Spy
1  Mr. Winthrop
```

Display all decks that won a tournament of 50 players or more in 2018:

```bash
$ krcg deck --players 50 --from 2018 --to 2019
[2018igpadhs] (No Name)
[2018eclcqwp] Dear diary, today I feel like a wraith.. Liquidation
[2018ecday1wp] MMA.MPA (EC 2018)
[2018ecday2wp] EC 2018 win
[2018pncwp] Deadly kittens
```

List cards most associated with a given card in TWD:

```bash
$ krcg affinity "Fame"
Fame                           (in 100% of decks, typically 1-2 copies)
Taste of Vitae                 (in 59% of decks, typically 3-6 copies)
Dragonbound                    (in 38% of decks, typically 1 copy)
Powerbase: Montreal            (in 34% of decks, typically 1 copy)
```

List most played cards of a given type, clan or discipline:

```bash
$ krcg top -d Animalism
Carrion Crows                  (played in 252 decks, typically 5-10 copies)
Cats' Guidance                 (played in 222 decks, typically 2-5 copies)
Canine Horde                   (played in 195 decks, typically 1-3 copies)
Deep Song                      (played in 194 decks, typically 3-10 copies)
Raven Spy                      (played in 182 decks, typically 2-6 copies)
Sense the Savage Way           (played in 167 decks, typically 2-6 copies)
Aid from Bats                  (played in 152 decks, typically 6-14 copies)
Army of Rats                   (played in 137 decks, typically 1-2 copies)
Guard Dogs                     (played in 83 decks, typically 1-3 copies)
Terror Frenzy                  (played in 73 decks, typically 1-4 copies)
```

Build a deck from any given cards based on TWDA:

```bash
$ krcg build "Fame" "Carrion Crows"

Created by: KRCG
Inspired by:
 - 2020mdmlf            Nanarch Buruku
 - 2019r6vh             Aksinya+Nana+Anarch+Ani 4.0
 - 2019bncfb            Resistência Anarch
 ...

-- Crypt: (12 cards)
---------------------------------------
1  Stick                               3  ANI                       Nosferatu antitribu:4
1  Beetleman                           4  obf ANI                   Nosferatu:4
1  Bobby Lemon                         4  pro ANI                   Gangrel:3
3  Nana Buruku                         8  ANI POT PRE               Guruhi:4
1  Céleste Lamontagne                  5  for ANI PRO               Gangrel antitribu:4
1  Petra                               5  aus ANI OBF               Nosferatu:4
4  Anarch Convert                      1  -none-                    Caitiff:ANY
-- Library (90)
-- Master (30)
8  Ashur Tablets
7  Anarch Revolt
3  Liquidation
3  Vessel
2  Dreams of the Sphinx
2  Haven Uncovered
1  Archon Investigation
1  Direct Intervention
1  Fame
1  Pentex(TM) Subversion
1  Wider View
-- Action (11)
10 Deep Song
1  Army of Rats
-- Combat (36)
13 Aid from Bats
10 Carrion Crows
4  Target Vitals
4  Taste of Vitae
3  Terror Frenzy
2  Canine Horde
-- Reaction (9)
4  Cats' Guidance
3  On the Qui Vive
2  Delaying Tactics
-- Retainer (4)
4  Raven Spy
```

### Static files generator

In its development version, KRCG also offers a tool for generating static files
for third parties, `krcg-gen`.

```bash
krcg init
krcg-gen standard amaranth
```

will generate files in the
[static](https://github.com/lionel-panhaleux/krcg/blob/master/static) folder
for `standard` and `amaranth` third parties.

Some generated files are in JSON format, their schemas can be found in the
[schemas](https://github.com/lionel-panhaleux/krcg/blob/master/schemas) folder.
The standard TWDA file is a rewrite of the
[original TWDA](https://github.com/GiottoVerducci/TWD) in the same HTML format.
