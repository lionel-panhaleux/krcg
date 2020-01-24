Changelog
=========

0.8 (unreleased)
----------------

- API: add cards comments
- API: add cards official ID
- API: deck endpoint now returns all TWDA decks by default
- Add tests for the API

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
