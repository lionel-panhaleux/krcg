Changelog
=========

2.17 (2021-08-22)
-----------------

- Take VEKN CSV changes into account (sets renamed)
- Add a diff feature for cards, to compare CSV versions.


2.16 (2021-07-22)
-----------------

- Additional rulings
- VDB "deck in URL" format for decks
- Fixed an error when loading a VDB deck


2.15 (2021-07-09)
-----------------

- Fix logging properly: logging is not configured by the lib anymore


2.14 (2021-07-08)
-----------------

- Fix logging issue (quickfix)


2.13 (2021-07-08)
-----------------

- Additional rulings
- Parser is now FELDB compatible


2.12 (2021-04-02)
-----------------

- Added a seating module to compute optimal seatings for tournaments
- Additional rulings

2.11 (2021-03-18)
-----------------

- Fix Talley, The Hound card name


2.10 (2021-03-02)
-----------------

- Fix Lackey format: now handles quotes in names properly
- Additional rulings

2.9 (2021-02-16)
----------------

- Additional rulings


2.8 (2021-02-01)
----------------

- Additional rulings


2.7 (2021-01-29)
----------------

- Handle HTML escaping when parsing TWDA (eg. &amp; character)
- Additional rulings
- Improved Author parsing in TWDA

2.6 (2021-01-11)
----------------

- Fix TWDA parsing for plama2k1
- Add card scans URLs
- Rulings update

2.5 (2020-12-31)
----------------

- Minor fixes on TWDA parsing (2 decklists fixed)


2.4 (2020-12-30)
----------------

- Add a method to import a deck from VDB
- RTR 20201130

2.3 (2020-12-21)
----------------

- Change the way cards search work. Multi-valued queries make more sense now.


2.2 (2020-12-21)
----------------

- Minor fix for python retro-compatibility


2.1 (2020-12-21)
----------------

- Ensure Python 3.7 compatibility


2.0 (2020-12-20)
----------------

- BREAKING CHANGES:
  
  * No more pickling, the init phase is new
  * Static files generation is now performed in a separated project: krcg-static
  * Projects using this library (CLI, API, bot, ...) are now in separate repositories

- Use JSON files from static.krcg.org for fast init (see krcg-static)
- Use VEKN sets CSV to parse and provide clear set information on cards
- Retrieve a deck list from an Amaranth UID
- Improved search engine, with many more dimensions, including sets and artists
- Use int IDs consistently everywhere

1.11 (2020-12-09)
-----------------

- Fix (D) symbol in translations


1.10 (2020-12-09)
-----------------

- i18n fixes


1.9 (2020-12-08)
----------------

- Fix setup


1.8 (2020-12-07)
----------------

- Minor fixes to TWD parsing
- Cards translations (es, fr) are now included
- API endpoints to complete and search over translated name and text
- CLI option to display a card translations
- Additional rulings.

1.7 (2020-12-02)
----------------

- API: Fix the /deck POST endpoint (again)


1.6 (2020-12-02)
----------------

- API: Fix the /deck POST endpoint


1.5 (2020-12-01)
----------------

- Heavy parser improvements. Now all decks since 1994 are properly parsed and included.
- Modified the web API to return decks from 1994 by default (instead of 2008)
- Modified the CLI to work with decks from 1994 by default (instead of 2008)
- New CLI Command to parse decklists and output a standard JSON format
- New script to synchronise cards images

1.4 (2020-10-30)
----------------

- Improve TWDA parsing for postfix card counts notation
- Improve TWDA HTML rendering: include crypt cards comments
- CLI: Allow for precise dates to be used as --from and --to parameters, not just year
- Improve logging
- Additional rulings

1.3 (2020-10-13)
----------------

- Additional rulings.
- Improved deck JSON serialisation


1.2 (2020-09-26)
----------------

- Additional rulings.


1.1 (2020-09-08)
----------------

- Additional rulings.


1.0 (2020-08-13)
----------------

- Missing 2017 rulings have been included. All rulings from 2015 onward are now included.
- Prepare for the new VEKN CSV files format
- Stable production version

0.57 (2020-07-28)
-----------------

- Discord bot: fix link to the codex


0.56 (2020-07-19)
-----------------

- Use Pentex™ (real card name) instead of Pentex(TM) (vekn cards reference file)
- Fix index.html

0.55 (2020-07-17)
-----------------

- Add sync-images make command
- Bot: new hosts for card page/image (avoid unnecessary redirections)
- API: add card image URL
- API: fix card search documentation
- API: added search command

0.54 (2020-07-12)
-----------------

- Improved rulings.


0.53 (2020-07-05)
-----------------

- Improved rulings.


0.52 (2020-06-25)
-----------------

- Improved rulings.


0.51 (2020-06-22)
-----------------

- Discord bot: Cache busting for card images


0.50 (2020-06-22)
-----------------

- Additional rulings.


0.49 (2020-06-12)
-----------------

- Added part of 2017 rulings (thx n11c0w)


0.48 (2020-06-11)
-----------------

- 2016 & 2015 rulings included


0.47 (2020-05-30)
-----------------

- Additional rulings.


0.46 (2020-05-21)
-----------------

- Additional rulings
- Remove unofficial rulings (from RD before official office)


0.45 (2020-05-18)
-----------------

- All 2018 to 2020 rulings included
- Additional rulings


0.44 (2020-05-15)
-----------------

- CLI: fix rulings display for card command
- Additional rulings


0.43 (2020-05-15)
-----------------

- krcg-gen: now generates a normalized standard TWD HTML file
- CLI: fixed init

0.42 (2020-05-13)
-----------------

- CLI: top command can now filter by sect


0.41 (2020-05-10)
-----------------

- Fix CLI commands


0.40 (2020-05-08)
-----------------

- Additional rulings


0.39 (2020-05-07)
-----------------

- Discord Bot: Fixed answers on card not found
- Discord Bot: Fixed fuzzy match on spelling errors


0.38 (2020-05-06)
-----------------

- Additional rulings
- krcg-gen: Fix  standard-rulings


0.37 (2020-05-05)
-----------------

- API: Submit ruling endpoint


0.36 (2020-05-04)
-----------------

- Discord Bot: Fix completion


0.35 (2020-05-04)
-----------------

- API: Improve search endpoint
- Discord Bot: Better card name search


0.34 (2020-05-03)
-----------------

- API: Add a card search endpoint "card/"
- Discord Bot: Will now answer if caps are used in his name.


0.33 (2020-04-30)
-----------------

- Proper data files handling


0.32 (2020-04-30)
-----------------

- Fix setup


0.31 (2020-04-30)
-----------------

- Additional rulings
- Now hosted on a dedicated server using uwsgi


0.30 (2020-04-28)
-----------------

- Discord bot: better card names matching


0.29 (2020-04-27)
-----------------

- Fix discord bot prefix value


0.28 (2020-04-27)
-----------------

- Improve discord bot: now handles card name completion


0.27 (2020-04-27)
-----------------

- Bot: fix disaply of cards with many rulings


0.26 (2020-04-27)
-----------------

- Better Discord bot


0.25 (2020-04-26)
-----------------

- Add Discord Bot


0.24 (2020-04-26)
-----------------

- CLI command build: deck author is now KRCG
- Improve README.md
- Add the krcg-gen tool, to generate static files for third parties
- Additional rulings

0.23 (2020-04-24)
-----------------

- Additional Rulings


0.22 (2020-04-21)
-----------------

- Additional Rulings


0.21 (2020-04-21)
-----------------

- 2019-2020 rulings included


0.20 (2020-04-20)
-----------------

- Improved rulings


0.19 (2020-04-20)
-----------------

- Additional rulings
- Fixed rulings pertaining to multi-target actions


0.18 (2020-04-18)
-----------------

- CLI card command: Ruling links are now optional
- CLI card command: Card text can be displayed without rulings
- CLI card command: Card IDs can be used
- Analyzer gets affinity computation: now a proportion of presence, with variance
- CLI affinity command: add expectation and deviance
- API complete: Fix completion for special chars

0.17 (2020-04-16)
-----------------

- Include 2020 rulings from VEKN forum.
- Fixed completion API: match all words, better match are returned first.
- API: Cards can now be fetched by ID
- Added general rulings applying to multiple cards

0.16 (2020-04-13)
-----------------

- Update rulings.

0.15 (2020-04-11)
-----------------

- Additional rulings.

0.14 (2020-04-10)
-----------------

- Upgrade runtime to Python 3.8.2

0.13 (2020-04-10)
-----------------

- API: The card/ endpoint now provides normalized card names
- Minor ruling fixes
- Added additional rulings
- Card search: Use card name as page title

0.12 (2020-04-08)
-----------------

- Use official ban list (now up to date)
- Include rulings
- Add an API endpoint to get official card text and rulings
- Update OpenAPI to 3.0.3 specification

0.11 (2020-02-27)
-----------------

- API: reintroduce the "Id" field for cards

0.10 (2020-02-27)
-----------------

- Fix OpenAPI /deck endpoint
- Update VEKN cards file (2020-02-27)

0.9 (2020-02-27)
----------------

- Check the validity of VEKN responses

0.8 (2020-01-24)
----------------

- API: add cards comments
- API: add cards official ID
- API: deck endpoint now returns all TWDA decks by default
- Add tests for the API
- Make the use of Python 3.8 official

0.7 (2020-01-24)
----------------

- New API, more RESTful, more consistent
- Fixed a 404 when searching for very widespread cards (eg. Pentex) would fail
- Now using OpenAPI & Swagger UI

0.6 (2020-01-21)
----------------

- Better parsing of Master: Discipline cards
- Keep blank lines in comments
- Punctuation was missing at the end of some comments
- Deck score in tournament is now correctly identified
- Better "top" command:
    + multiple clans & disciplines allowed
    + now case insensitive
    + common abbreviations accepted
- Better score parsing
- Fix Advanced vampires parsing
- Default card names now use "The" as a prefix (as on card)
  instead of as a suffix (as in official CSV)
- Basic JSON API for Heroku deployment

0.5 (2019-09-10)
----------------

- Advanced and base versions of vampires are now correctly identified
- Better parsing of comments in decks
- Inline cards comments are now retrieved and displayed

0.4 (2019-09-08)
----------------

- No more warning spam by default when loading TWDA (use the --verbose option)
- The build command now correctly uses --fom and --to options.

0.3 (2019-09-07)
----------------

- Fix "ModuleNotFoundError: No module named 'src'" error for pip install.

0.2 (2019-09-07)
----------------

- Fix setup classifier for a clean release

0.1 (2019-09-07)
----------------

- KRCG tool, initial version.
