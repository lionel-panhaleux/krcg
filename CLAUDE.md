# CLAUDE.md

This file provides guidance to **all AI agents** (Claude Code and others — `AGENTS.md` is a symlink to it) working with code in this repository.

## What this is

KRCG is a Python library (>=3.10) that provides an interface to the VTES (Vampire: The Eternal Struggle) card game data: the VEKN official card texts, the Tournament Winning Deck Archive (TWDA), and a community-maintained rulings database. It is the foundation for several offspring projects (krcg-cli, krcg-static, krcg-api, krcg-bot) and is published to PyPI as `krcg`.

The README contains extensive usage examples — consult it for the public API surface. This file focuses on architecture and the development workflow.

## Development commands

This project uses [`uv`](https://github.com/astral-sh/uv) for dependencies and [`just`](https://github.com/casey/just) for tasks. Setup: `uv sync --group dev`.

- `just quality` — runs `ruff check`, `ruff format --check`, and `mypy krcg`
- `just test` — runs `quality` then `uv run pytest -vvs` (quality runs first; tests won't run if it fails)
- `just sync-cards` — refresh packaged data (`cards/*.csv` and `cards/*.yaml`) from the external `vtescsv` and `vtes-rulings` GitHub repos
- `just update` — `sync-cards` + `uv sync --upgrade --dev`
- `just build` / `just clean` / `just release` (release bumps minor version, tags, pushes, and publishes to PyPI using `.pypi_token`)

Run a single test: `uv run pytest tests/test_cards.py::test_load -vvs`

Lint config lives in `pyproject.toml`: ruff selects `E,D,F,W` with Google docstring convention; mypy runs in strict mode (`disallow_untyped_defs`, `no_implicit_optional`, etc.) — **all new functions need type annotations and Google-style docstrings** or quality fails.

## Code style

Favor compact, functional code over OO ceremony and design patterns:

- Keep changes minimal and the code tight — shorter and denser beats longer and more abstract.
- Prefer plain-old-data and free functions to classes-with-methods; lean functional rather than object-oriented.
- Don't split out a function used in only one place — inline it. Reserve helpers for genuine reuse.
- **Comments are exceptional.** Default to none. The code says *what* it does — a comment that restates, names, or paraphrases the code (e.g. `# sort last`) is noise; delete it. Write a comment *only* to supply indispensable context that cannot be read from the code: an external constraint, a data-format/protocol quirk, a citation, or reasoning that is genuinely surprising. If in doubt, leave it out. Public classes and functions still get a Google-style docstring (lint requires it — see above); keep it to the minimum that serves the user.
- **Import whole modules at the top of the file, reference qualified.** `import collections` / `from . import cards`, then write `collections.Counter`, `cards.Card`. Don't import bare symbols (only `typing` and relative `from . import …` use `from`), and never import inside a function body — all imports live at module top.
- **Log, don't print.** Each module defines `logger = logging.getLogger("krcg")`; pass args lazily (`logger.debug("got %s", x)`) rather than interpolating into the message.
- **Modern typing:** use builtin generics and union syntax — `list`, `dict`, `X | None` — not `typing.List`, `typing.Dict`, `Optional[X]`. The codebase is mid-migration off the old `typing` forms; switch them as you touch the surrounding code.

## Architecture

### Two in-memory singletons, no database

By design there is no database. The card list, search engine, TWDA, and rulings are all loaded into memory (128–256MB footprint). The two entry points are module-level singletons:

- `krcg.vtes.VTES` (`_VTES`) — the cards library. Wraps a `cards.CardMap` and a `cards.CardSearch`.
- `krcg.twda.TWDA` (`_TWDA`) — the deck archive, an `OrderedDict` of `Deck` keyed by deck id, with a `by_author` index.

Both evaluate as falsy until loaded. `TWDA.load()` will auto-load `VTES` if needed.

### Three data-loading paths

Understanding these is key to working with the library:

1. **`load()`** — fetches pre-built JSON from the KRCG static server (`https://static.krcg.org`). Fast; the normal path for consumers.
2. **`load_from_vekn()`** — builds from raw CSVs (VEKN or the `vtescsv` GitHub mirror) plus rulings YAML. Slow; used to *generate* the static JSON and to test incoming card-data changes.
3. **Offline / `LOCAL_CARDS=1`** — `load_from_vekn()` reads the CSV/YAML snapshot packaged under `cards/` (via `importlib.resources`) instead of the network. The PyPI package ships this snapshot; `just sync-cards` refreshes it.

External data is intentionally decoupled so new sets/cards work without a library release.

### Module map

- `cards.py` (largest, ~1700 lines) — the core. `Card` model, `CardMap` (a `FuzzyDict` indexing cards by integer id *and* many name variants/aliases), and the search engine (`CardSearch` + `CardTrie`). All CSV/JSON/rulings loading lives here. Iterating a `CardMap` yields each card once (by int key); string keys are name aliases.
- `deck.py` — `Deck` is a `collections.Counter[Card]` plus metadata (event, date, author, score, comments). Serialization (`from_txt`/`to_txt` in many formats, `to_json`) and remote fetchers (`from_amaranth`, `from_vdb`, `from_vtesdecks` — network-only).
- `parser.py` — the deck-list parser handling legacy TWDA and many third-party text formats. **Header comment warns: only modify if you know what you're doing.** Tightly coupled to the messy real-world data; lots of special-casing.
- `twda.py` — TWDA singleton; `load_html` does the hard work of slicing `TWDA.html` into individual decklists and parsing each via `Deck.from_txt(..., twda=True)`.
- `analyzer.py` — `Analyzer` over a deck collection (typically the TWDA): card "affinity" (co-occurrence), averages/variance, and candidate suggestions for deck building.
- `seating.py` — tournament seating optimisation against 9 weighted official rules (`R1`–`R9`); uses numpy + multiprocessing for the search.
- `rulings.py` — parses ruling text: discipline/type symbols (`ANKHA_SYMBOLS`), card references (`{...}`), and source references (`[LSJ ...]`), with the authoritative `RULING_AUTHORS` timeline.
- `sets.py` — expansion/set metadata.
- `config.py` — static-server URLs, supported languages, deck `TYPE_ORDER`, the large `ALIASES` map (player typos & card-name shorthands seen in the TWDA), and `TWDA_CHECK_DECK_FAILS` (known-malformed decks to skip validation on).
- `utils.py` — `FuzzyDict` (difflib-backed fuzzy lookup), `i18nMixin`/`NamedMixin`, `normalize`, zip/CSV helpers.

### Relevant environment variables

- `LOCAL_CARDS=1` — offline mode (load packaged `cards/` data; see above). Translations are skipped offline.
- `VTESCSV_GITHUB_BRANCH` — point CSV loading at a different `vtescsv` branch to test incoming card data.
- `NO_TRANSLATIONS` — skip fetching translations from vekn.net.
- `VEKN_NET_CSV` — force the official VEKN zip instead of the GitHub mirror.
- `FORCE_OFFLINE` — used by tests to behave as if there's no internet.

## Testing notes

Test philosophy:

- **Don't add tests systematically.** Favor a few dense tests with broad coverage over many small unit tests — a single test function should exercise a whole feature, not go function-by-function.
- **Bug fixes don't automatically earn a test.** Add one only for a genuinely uncovered niche case that could plausibly regress unnoticed if we're not careful.
- **No mocks, no mirror tests.** Never write a test that just restates the implementation or asserts the code does what it literally says — that duplication slows development instead of supporting it.
- **A few tests deliberately track external data** (cards, rulings, TWDA content). Don't rewrite them to swallow changes: their job is to surface card-database and ruling changes so we can eyeball how they settle. Keep these to a bare minimum — most tests must be stable against source-data changes; only a couple are broad "list everything" snapshots.

`tests/conftest.py` builds `VTES` once per session from the **local packaged CSVs** (`load_from_vekn()`), so tests don't hit the network for card data. When offline, it auto-sets `LOCAL_CARDS=1` and **skips** internet-dependent tests (static-server loads, external deck providers, i18n, and all of `test_states.py`). The `TWDA` pytest fixture loads `tests/TWDA.html`, a ~20-deck snapshot. Test HTML/txt files in `tests/` are real archive fixtures used to verify the parser against historical formats.

## Rulings are external

Rulings are sourced from the community repo [`vtes-biased/vtes-rulings`](https://github.com/vtes-biased/vtes-rulings) and synced into `cards/` on each release. **Do not edit rulings here** — submit changes upstream.
