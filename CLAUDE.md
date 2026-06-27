# CLAUDE.md

This file provides guidance to **all AI agents** (Claude Code and others — `AGENTS.md` is a symlink to it) working with code in this repository.

## What this is

KRCG is a Python library (>=3.12) that provides an interface to the VTES (Vampire: The Eternal Struggle) card game data: the VEKN official card texts, the Tournament Winning Deck Archive (TWDA), and a community-maintained rulings database. It is the foundation for several offspring projects (krcg-cli, krcg-static, krcg-api, krcg-bot) and is published to PyPI as `krcg`.

The README contains extensive usage examples — consult it for the public API surface. This file focuses on architecture and the development workflow.

## Development commands

This project uses [`uv`](https://github.com/astral-sh/uv) for dependencies and [`just`](https://github.com/casey/just) for tasks. Setup: `uv sync --group dev`.

- `just quality` — runs `ruff check`, `ruff format --check`, and `ty check krcg`
- `just test` — runs `quality` then `uv run pytest -vvs` (quality runs first; tests won't run if it fails)
- `just sync-cards` — refresh packaged data (`cards/*.csv` and `cards/*.yaml`) from the external `vtescsv` and `vtes-rulings` GitHub repos
- `just update` — `sync-cards` + `uv sync --upgrade --dev`
- `just build` / `just clean` / `just release` (release bumps minor version, tags, pushes, and publishes to PyPI using `.pypi_token`)

Run a single test: `uv run pytest tests/test_parser.py::test_get_card -vvs`

Lint config lives in `pyproject.toml`: ruff selects `E,D,F,W,UP` with Google docstring convention; type-checking is `ty check krcg` (Astral's `ty`, which replaced mypy). **All new functions need type annotations and Google-style docstrings** — ruff enforces the docstrings; full annotations are the project convention (ty checks them where present). Prefer fixing types over `# ty: ignore`.

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

### No singletons, no database

By design there is no database: the cards library, its search index, the TWDA, and the rulings all live in memory (~128–256 MB). Nothing is a module-level singleton — load what you need and hold the handle:

- `krcg.load()` / `load_local()` / `load_online(session)` (in `loader.py`) each return a `collections.CardDict` — the one cards handle. It looks cards up by id or name and owns `search` / `complete` / `search_dimensions`.
- `krcg.twda.load()` / `load_local()` / `load_online(session)` each return a plain `dict[str, models.Deck]` (`DecksArchive`) keyed by deck id.

### Data-loading paths

1. **`load_online(session)`** — async; fetches pre-built JSON from the KRCG static server (`https://static.krcg.org`). The fast path for online consumers; falls back on failure (cards → `load()`, TWDA → `load_local()`).
2. **`load()`** (cards only) — reads a version-keyed pickle cache (written by the loaders), else builds via `load_local()`. For the TWDA, `load()` is just `load_local()` (a single decode, no cache).
3. **`load_local()`** — builds offline from the snapshot packaged under `krcg/cards/` (via `importlib.resources`): CSV/YAML for the cards & rulings, the compressed `twda.json.xz` for the archive. No network, **no environment variable**. `just sync-cards` refreshes the snapshot.

External data is intentionally decoupled so new sets/cards work without a library release.

### Module map

- `models.py` — the data types: `Card` / `CryptCard` / `LibraryCard` (and `CardInDeck`), `Deck`, `Set`, rulings, and the enums (`Lang`, `Card.Kind`, `SearchDimension`, …). All **plain dataclasses** — msgspec is used for (de)serialization but never imposed on the model objects. `Deck.cards` is a `list[CardInDeck]` (no `Counter`, no `.crypt`/`.library` views — filter by `card.kind`).
- `collections.py` — `CardDict`, the cards library: a `FuzzyDict` indexing cards by integer id *and* many name variants/aliases, plus the search engine (`CardSearch` + the i18n trie). Iterate distinct cards with `.cards()` (bare iteration yields keys).
- `loader.py` — the three cards loaders (`load` / `load_local` / `load_online`), re-exported as `krcg.load*`. (Loaders can't live on `CardDict` — `vekn_csv`/`rulings` import `collections`, which would cycle.)
- `twda.py` — the TWDA loaders (same three names); `DecksArchive = dict[str, Deck]`.
- `vekn_csv.py` — build cards from the packaged VEKN CSVs; holds the `ALIASES` map (player typos & card-name shorthands seen in the TWDA).
- `parser.py` — the decklist parser handling legacy TWDA and many third-party text formats. **Header comment warns: only modify if you know what you're doing.** `deck_from_txt(source, cards, *, id, twda)` is the entry point.
- `providers.py` — fetch decks from external sites (`fetch(session, url, cards)`, async, network-only) and serialize them (`serialize_twd` / `serialize_txt` / `serialize_vdb` / `serialize_lackey` / `serialize_jol` / `serialize_json_minimal`).
- `analyzer.py` — free functions over a deck collection (typically the TWDA), each taking a `CardDict` to resolve cards: `played` (decks per card), `stats` (average/variance of copies), `affinity` (co-occurrence ranking), and `build_deck` (synthesize a TWDA-like deck).
- `seating.py` — tournament seating optimisation against 9 weighted official rules (`R1`–`R9`); numpy + multiprocessing. `get_rounds` builds the base rounds; `optimise` searches.
- `rulings.py` — parses ruling text: discipline/type symbols (`ANKHA_SYMBOLS`), card references (`{...}`), and source references (`[LSJ ...]`), with the authoritative `RULING_AUTHORS` timeline.
- `utils/` — `fuzzy_dict.py` (`FuzzyDict`, difflib-backed fuzzy lookup), `trie.py` (`Trie`), `string.py` (`normalize`, …), `csv.py`, and `deck.py` (deck sorting/serialization helpers).

### Relevant environment variables

The library itself reads no environment variables (`load_local()` is the offline path). Only the test suite uses one:

- `FORCE_OFFLINE` — make the suite behave as if there's no internet (skips the network-dependent tests).

## Testing notes

Test philosophy:

- **Don't add tests systematically.** Favor a few dense tests with broad coverage over many small unit tests — a single test function should exercise a whole feature, not go function-by-function.
- **Bug fixes don't automatically earn a test.** Add one only for a genuinely uncovered niche case that could plausibly regress unnoticed if we're not careful.
- **No mocks, no mirror tests.** Never write a test that just restates the implementation or asserts the code does what it literally says — that duplication slows development instead of supporting it.
- **A few tests deliberately track external data** (cards, rulings, TWDA content). Don't rewrite them to swallow changes: their job is to surface card-database and ruling changes so we can eyeball how they settle. Keep these to a bare minimum — most tests must be stable against source-data changes; only a couple are broad "list everything" snapshots.
- **Mark data-tracking tests `@pytest.mark.baseline`.** A `baseline` failure is downgraded to an amber `xfail` ("source data drifted — eyeball it") by a `conftest` hook, so it never fails the build; genuine code regressions live in unmarked tests and fail red. Use it for live-data snapshots/counts (e.g. `test_card_snapshot`, `test_search_results`, `test_bundle_integrity`), not for logic tested against frozen fixtures.

`tests/conftest.py` provides session-scoped `cards` (`loader.load_local()`) and `TWDA` (`twda.load_local()`) fixtures, so tests don't hit the network for card or deck data (translations and rulings load from the bundled snapshot too). When offline, it **skips** the few genuinely internet-dependent tests (static-server load, external deck providers). Parser fidelity is checked against frozen `tests/twd_*.txt` decks — real decks from the current TWDA source, hand-picked for format peculiarities (no-final rounds, Sabbat path, date ranges, accents, rich comments, legacy headers). Re-baselined `msgspec.to_builtins` snapshots live as JSON under `tests/snapshots/`.

## Rulings are external

Rulings are sourced from the community repo [`vtes-biased/vtes-rulings`](https://github.com/vtes-biased/vtes-rulings) and synced into `cards/` on each release. **Do not edit rulings here** — submit changes upstream.
