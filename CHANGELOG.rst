Changelog
=========

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
