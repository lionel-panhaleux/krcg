# KRCG

[![PyPI version](https://badge.fury.io/py/krcg.svg)](https://badge.fury.io/py/krcg)
[![Build Status](https://travis-ci.org/lionel-panhaleux/krcg.svg?branch=master)](https://travis-ci.org/lionel-panhaleux/krcg)
[![Python version](https://img.shields.io/badge/python-3.8-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-blue)](https://opensource.org/licenses/MIT)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

A command-line interface based on
the VEKN [official card texts](http://www.vekn.net/card-lists)
and the [Tournament Winning Deck Archive (TWDA)](http://www.vekn.fr/decks/twd.htm)

## Installation

You need [Python 3](https://www.python.org/downloads/)
installed on your system to use this tool.

Use pip to install the ``krcg`` tool:

```shell
pip install krcg
```

Then initialize the tool using the ``init`` subcommand:

```shell
krcg init
```

## Usage

Use the help command for a full documentation of the tool:

```shell
krcg --help
```

And also extensive help on each sub-command:

```shell
krcg [COMMAND] --help
```

Note most commands only take decks from 2008 on in consideration.
You can use the `--from` and `--to` parameters to control the date range.

## Examples

Get a card text:

```shell
$> krcg card "Fame"
Fame
[Master] -- (Jyhad:U, VTES:U, SW:PB, CE:PB, Anarchs:PG, BH:PN2, KMW:PAl, Third:PTz, KoT:U/PT2, HttB:PGar/PSal)
Unique master.
Put this card on a ready vampire. If this vampire goes to torpor, his or her controller burns 3 pool. While this vampire is in torpor, each Methuselah burns 1 pool during his or her unlock phase.
```

List TWDA decks containing this card:

```shell
$> krcg deck "Fame"
[2016gncbg] weenie animalism minimal: "Ich bin eine von wir"
[2016amfb] Gangrel e Garou
[2016ukncle] (No Name)
[2016ecday1gi] (No Name)
[2016saclcqspb] "Choquinho"
...
```

Display any TWDA deck:

```shell
$> krcg deck 2016gncbg
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

```shell
$> krcg deck --players 50 --from 2018 --to 2019
[2018igpadhs] (No Name)
[2018eclcqwp] Dear diary, today I feel like a wraith.. Liquidation
[2018ecday1wp] MMA.MPA (EC 2018)
[2018ecday2wp] EC 2018 win
[2018pncwp] Deadly kittens
```

List cards most associated with a given card in TWD:

```shell
$> krcg affinity "Fame"
Taste of Vitae                 (score: 237.00)
Dragonbound                    (score: 153.00)
Powerbase: Montreal            (score: 131.00)
Target Vitals                  (score: 119.00)
Carrion Crows                  (score: 119.00)
Carlton Van Wyk                (score: 118.00)
Haven Uncovered                (score: 115.00)
Ashur Tablets                  (score: 111.00)
Archon Investigation           (score: 106.00)
Deep Song                      (score: 103.00)
```

List most played cards of a given type, clan or discipline:

```shell
$> krcg top -d Animalism
Carrion Crows                  (played in 240 decks)
Cats' Guidance                 (played in 211 decks)
Canine Horde                   (played in 187 decks)
Deep Song                      (played in 180 decks)
Raven Spy                      (played in 176 decks)
Sense the Savage Way           (played in 156 decks)
Aid from Bats                  (played in 144 decks)
Army of Rats                   (played in 131 decks)
Guard Dogs                     (played in 72 decks)
Terror Frenzy                  (played in 70 decks)
```

Build a deck from any given cards based on TWDA:

```shell
$> krcg build "Fame" "Carrion Crows"

Created by: KRCG
Description:
Inspired by:
 - 2016gncbg            weenie animalism minimal: "Ich bin eine von wir"
 - 2016sncss            Vampire-SM 2016. Field Training Bats v.3
 - 2016ecqmmf           Weenie Animalism v1.2
 - 2016ncqmmf           New Nana (27)
 - 2015saclcqfb         Cidade em Chamas
 ...

-- Crypt: (12 cards)
---------------------------------------
3  Nana Buruku                         8  ANI POT PRE               Guruhi:4
1  Stick                               3  ANI                       Nosferatu antitribu:4
1  Beetleman                           4  obf ANI                   Nosferatu:4
1  Bobby Lemon                         4  pro ANI                   Gangrel:3
1  Petra                               5  aus ANI OBF               Nosferatu:4
1  Célèste Lamontagne                  5  for ANI PRO               Gangrel antitribu:4
1  Zip                                 2  ani                       Ravnos:3
1  Lisa Noble                          1  ani                       Caitiff:3
1  Mouse                               2  ani                       Nosferatu:3
1  Fish                                5  pre ANI POT               Guruhi:4
-- Library (90)
-- Master (25)
8  Ashur Tablets
3  Blood Doll
2  Animalism
2  Dreams of the Sphinx
2  Haven Uncovered
2  Vessel
1  Archon Investigation
1  Direct Intervention
1  Fame
1  Pentex(TM) Subversion
1  Powerbase: Montreal
1  Wider View
-- Action (11)
10 Deep Song
1  Army of Rats
-- Combat (37)
13 Aid from Bats
10 Carrion Crows
5  Taste of Vitae
4  Target Vitals
3  Terror Frenzy
2  Canine Horde
-- Reaction (11)
4  Cats' Guidance
3  On the Qui Vive
2  Delaying Tactics
2  Sense the Savage Way
-- Retainer (5)
5  Raven Spy
-- Event (1)
1  Dragonbound
```

## Contribute

Feel free to submit pull requests, they will be merged as long as they pass the tests.
Do not hestitate to submit issues or vote on them if you want a feature implemented.

## Online API

KRCG is available as an [online API on Heroku](https://krcg.herokuapp.com/).
