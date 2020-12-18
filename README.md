# KRCG

[![PyPI version](https://badge.fury.io/py/krcg.svg)](https://badge.fury.io/py/krcg)
[![Validation](https://github.com/lionel-panhaleux/krcg/workflows/Validation/badge.svg)](https://github.com/lionel-panhaleux/krcg/actions)
[![Coverage](https://api.codacy.com/project/badge/Grade/32d1b809494e4935967608f13f52004a)](https://app.codacy.com/manual/lionel-panhaleux/krcg?utm_source=github.com&utm_medium=referral&utm_content=lionel-panhaleux/krcg&utm_campaign=Badge_Grade_Dashboard)
[![Python version](https://img.shields.io/badge/python-3.8-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-blue)](https://opensource.org/licenses/MIT)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

A web API and command-line interface based on
the VEKN [official card texts](http://www.vekn.net/card-lists)
and the [Tournament Winning Deck Archive (TWDA)](http://www.vekn.fr/decks/twd.htm)

Portions of the materials are the copyrights and trademarks of Paradox Interactive AB,
and are used with permission. All rights reserved.
For more information please visit [white-wolf.com](http://www.white-wolf.com).

![Dark Pack](dark-pack.png)

## Online API

KRCG is available as an [online API](https://api.krcg.org/).
Feel free to use it.

## Discord BOT

KRCG is available as a
[Discord Bot](https://discordapp.com/oauth2/authorize?client_id=703921850270613505&scope=bot).
Feel free to use it in your server.

It lets you retrieve cards official text, image and rulings:
![Bot Example](https://raw.githubusercontent.com/lionel-panhaleux/krcg/master/bot-example.png)

## Static Files

KRCG provides normalized static files for third parties, they can be found in the
[static](https://github.com/lionel-panhaleux/krcg/blob/master/static) folder:

-   `amaranth-twda.json`: The TWDA in JSON format for Amaranth (card IDs are Amaranth specific).
-   `standard-rulings.json`: The rulings in JSON format
-   `twd.htm`: A normalized version of the TWDA

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
[rulings-links.yaml](https://github.com/lionel-panhaleux/krcg/blob/master/rulings/rulings-links.yaml),
and the ruling itself to
[cards-rulings.yaml](https://github.com/lionel-panhaleux/krcg/blob/master/rulings/cards-rulings.yaml) or
[general-rulings.yaml](https://github.com/lionel-panhaleux/krcg/blob/master/rulings/general-rulings.yaml)
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

### Using the library

KRCG is a Python library for VTES.
The code is well-documented and can be explored using Python's built-in `help` function.

Here are a few quickstart examples to showcase how the library can be used:

```python
>>> from krcg.vtes import VTES
>>> VTES.load_from_vekn()
>>> VTES.configure()
>>> VTES["Alastor"]
{'Id': '100038',
 'Name': 'Alastor',
 'Aka': '',
 'Type': ['Political Action'],
 'Clan': [],
 'Discipline': [],
 'Pool Cost': '',
 'Blood Cost': '',
 'Conviction Cost': '',
 'Burn Option': False,
 'Card Text': 'Requires a justicar or Inner Circle member.\nChoose a ready Camarilla vampire. If this referendum is successful, search your library for an equipment card and place this card and the equipment on the chosen vampire. Pay half the cost (round down) of the equipment. This vampire may enter combat with any vampire controlled by another Methuselah as a +1 stealth Ⓓ  action. This vampire cannot commit diablerie. A vampire may have only one Alastor.',
 'Flavor Text': '',
 'Set': ['Gehenna:R', 'KMW:PAl', 'KoT:R'],
 'Requirement': ['justicar', 'inner circle'],
 'Banned': '',
 'Artist': 'Monte Moore',
 'Capacity': '',
 'Draft': ''}
>>> VTES.rulings["Alastor"]
{'Rulings': ['If the given weapon costs blood, the target Alastor pays the cost. [LSJ 20040518]',
  'Requirements do not apply. [ANK 20200901]'],
 'Rulings Links': [{'Reference': 'LSJ 20040518',
   'URL': 'https://groups.google.com/d/msg/rec.games.trading-cards.jyhad/4emymfUPwAM/B2SCC7L6kuMJ'},
  {'Reference': 'ANK 20200901',
   'URL': 'http://www.vekn.net/forum/rules-questions/78830-alastor-and-ankara-citadel#100653'}]}
>>> VTES.complete("pentex")
['Pentex™ Loves You!',
 'Pentex™ Subversion',
 'Enzo Giovanni, Pentex Board of Directors',
 'Enzo Giovanni, Pentex Board of Directors (ADV)',
 'Harold Zettler, Pentex Director']
```

### Hosting the web API

To host the web API, you need to install the `web` version of krcg:

```bash
pip install "krcg[web]"
```

No wsgi server is installed by default, you need to install one.
HTTP web servers can then easily be configured to serve WSGI applications,
check the documentation of your web server.

The API can be served with [uWSGI](https://uwsgi-docs.readthedocs.io):

```bash
uwsgi --module krcg.wsgi:application
```

or [Gunicorn](https://gunicorn.org):

```bash
gunicorn krcg.wsgi:application
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
environment variable `DISCORD_TOKEN`.
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

For development, the environment variable `DISCORD_TOKEN` can be provided
by a personal `.env` file at the root of the krcg folder (ignored by git):

```bash
export DISCORD_TOKEN="discord_token_of_your_bot"
```
