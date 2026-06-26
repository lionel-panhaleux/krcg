# KRCG V3 — Plan

Status: **draft / in progress** (branch `lip/v3`, commit `DRAFT - v3`).
This document is the working plan to finish the V3 refactor and reach a shippable release.
Audience: maintainer + contributors working this branch.

## 1. Goals

V3 is a ground-up rewrite of the core, driven by four goals:

1. **Performance** — `msgspec` for decode/encode + a pickle cache (`krcg_vtes_<version>.pkl` in the temp dir) for fast startup.
2. **Typed, explicit models** — `dataclasses` + `StrEnum`s (`models.py`) replace the old mixin/`FuzzyDict`-of-dicts `Card`. Better typing, IDE support, and validation.
3. **Offline-first bundling** — card data, translations, and rulings ship inside the package under `krcg/cards/`, so cards work with no network. (The TWDA is the exception: lazily downloaded from static.krcg.org — see §3.)
4. **Async for online tools** — `aiohttp` so consumers (api, bot) can load from KRCG static and fetch decks without blocking.

Toolchain also moves to **Python ≥3.13**, drops `requests` (→ `aiohttp`), and switches type-checking toward `ty`.

## 2. Architecture (new shape)

| Module | Role |
| --- | --- |
| `models.py` | All data types: `CardMinimal → Card → CryptCard/LibraryCard`, `CardInDeck`, `Deck`, `Event`, `Score`, `Set`/`Print`/`Bundle`, `Ruling`, and enums (`Discipline`, `Title`, `Sect`, `Trait`, `Bonus`, `Group`, `Lang`, `SearchDimension`, …). `Deck` is now a dataclass holding `cards: list[CardInDeck]` — **no longer a `Counter`**. |
| `collections.py` | `CardDict` (id+name fuzzy index), `CardSearch` (set + trie dimensions), `i18nTrie`. Derived metadata (sect/title/bonus/trait/city) is computed by regex at index time in `get_dimension_values` + `_get_*`. |
| `vekn_csv.py` | Build `Card`/`Set` objects from the packaged VEKN CSVs; name-variant/unicity-suffix computation, URLs, translations, aliases. |
| `vtes.py` | `VTES` **class** with `load()` / `load_local()` / `load_online(session)`; wraps `CardDict` + `CardSearch` + sets. |
| `twda.py` | Loads the TWDA into `dict[str, models.Deck]` — lazily downloaded from static.krcg.org (`/data/twda.json`), **not bundled**. |
| `parser.py` | Legacy/loose deck-list text → `models.Deck` (`deck_from_txt`, `Parser`). "Only modify if you know what you're doing." |
| `providers.py` | Async fetchers (amaranth / vdb / vtesdecks) + serializers (`serialize_lackey/jol/vdb/twd/txt/json_minimal`). |
| `rulings.py` | Parse rulings YAML (symbols / card refs / source refs) into `models.Ruling`; `load_local` / `load_online`. |
| `analyzer.py` | Card affinity / deck suggestions over a deck collection. |
| `seating.py` | Tournament seating optimisation (unchanged logic). |
| `utils/` | Package: `fuzzy_dict`, `trie`, `string`, `csv`, `json`, `deck` helpers. |
| `scripts/` | Offline data pipeline: `fix_csv.py` (normalise VEKN CSVs), `fetch_twda.py` (build `twda.json` from GiottoVerducci/TWD). |

**Bundled data** (`krcg/cards/`): `vtes{sets,crypt,lib,libmeta}.csv`, `vtesbundles.csv`, `vtescsv-fr/`, `vtescsv-es/`, `groups.yaml`, `references.yaml`, `rulings.yaml`. Refreshed by `just sync-cards`. The TWDA is **not** bundled; `scripts/fetch_twda.py` generates `twda.json` for publishing to static.krcg.org, which the runtime fetches.

## 3. Public API decision

**Explicit loaders, no import-time work.** Consumers must load explicitly; importing `krcg` does nothing heavy.

```python
from krcg import vtes, twda
import aiohttp

V = vtes.VTES.load()                 # pickle cache → load_local() fallback
V = vtes.VTES.load_local()           # packaged CSVs
async with aiohttp.ClientSession() as s:
    V = await vtes.VTES.load_online(s)   # KRCG static JSON
```

This is a **hard break** from V2's module-level `vtes.VTES` / `twda.TWDA` singletons — acceptable for the `5.0` major (see §5).

Consequence: **`twda.py` must stop building `TWDA` at import time.** Replace the module-level `TWDA = load_twda()` with an explicit `load_online(session)` that fetches `https://static.krcg.org/data/twda.json` (the reference source) and `msgspec`-decodes it to `dict[str, models.Deck]`. The TWDA is no longer bundled, so there is no offline default — a `load_local(path)` may stay for dev/tests against a saved file.

## 4. Remaining work

### 4.1 Entry points & loading
- [ ] `twda.py`: remove the import-time global; add `load_online(session)` fetching `static.krcg.org/data/twda.json`, plus an optional `load_local(path)` for dev/tests. Stop bundling `twda.json`.
- [ ] `vtes.VTES.load_online`: fix error handling — on exception, `return ret` can hit `UnboundLocalError` and the `cls.load()` fallback result is discarded.
- [ ] **Pickle cache policy:** `load_online` always rebuilds and overwrites `krcg_vtes_<version>.pkl` (systematic invalidation — fresh online data becomes the cache). `load()` reads that cache, else builds from bundled CSVs via `load_local()`. Version-keyed filename already covers new package releases.
- [ ] Update `__init__.py` docstring to describe the explicit-load API.

### 4.2 Rulings (the `# TODO: add rulings` in `vekn_csv.from_files`)
- [ ] Wire `rulings.load_local(cards)` into `VTES.load_local()` (and decide online behaviour: KRCG static JSON already embeds rulings; `load_online` should not double-load).
- [ ] Fix `rulings._parse_text`: `models.CardMinimal(**dataclasses.asdict(card))` passes full-`Card` fields into `CardMinimal` → `TypeError`. Copy only minimal fields.
- [ ] Verify group-ruling handling in `load_from_files` (inner comprehension rebinds `nid`).

### 4.3 analyzer.py (port — in scope)
- [ ] Rewrite for `models.Deck` (`.cards` list of `CardInDeck`) instead of `Counter` semantics (`d.keys()`, `d[card]`). Key counters by `models.Card`; thread a cards DB through for `candidates()` output.

### 4.4 seating.py (port — in scope)
- [ ] Confirm it imports/builds under the new package (only 4 lines changed) and restore `tests/test_seating.py` to green.

### 4.5 parser.py
- [ ] `Parser.__init__` signature changed; ensure `deck_from_txt(...)` is the supported entry and update callers/tests. Confirm it emits `models.Deck` end-to-end.

### 4.6 Tests (currently 13 passed / 37 failed / 3 errors)
- [ ] Add a **session-scoped fixture** in `conftest.py` providing a loaded `VTES` and `TWDA` (each test calling `load_local()` is slow and inconsistent). Since the TWDA is no longer bundled, commit a small `twda.json` sample under `tests/` and load it via `twda.load_local(path)` (don't hit the network in unit tests).
- [ ] `test_vtes.py`: migrate tests that use `vtes.VTES` as an instance; update `search()` expectations (now keyword-only filters, returns a sorted list, `n` default 100) and `search_dimensions`.
- [ ] `test_twda.py`, `test_states.py`, `test_tournament_archive.py`, `test_analyzer.py`: update to new TWDA loader / analyzer / serialization.
- [ ] `test_deck.py`: align with `providers.*` serializers (`serialize_vdb`, `serialize_json_minimal` mismatches).
- [ ] `test_parser.py`: update to new `Parser`/`deck_from_txt` signature.

### 4.7 Cleanup
- [ ] Delete leftover `krcg/__cards.py`, `__config.py`, `__deck.py`, `__utils.py` once fully ported (confirm nothing imports them; old `config.ALIASES` now lives in `vekn_csv.ALIASES`).
- [ ] Decide the fate of `sets.py` (legacy; much of it is commentary) now that `models.Set` + `vtessets.csv` exist — trim or remove.
- [ ] Trim `models.Lang` to `EN`/`FR`/`ES` (the only synced data); drop `DE`/`IT`/`PT` until their data exists.

### 4.8 Tooling & build
- [ ] Reconcile type checker: dev deps use **`ty`**, but `justfile quality` runs `mypy krcg` and `pyproject` still has `[tool.mypy]`. Pick one (likely `ty`), update `justfile` + remove stale config; `clean` still references `.mypy_cache`.
- [ ] Confirm `pytest-asyncio` config (tests use explicit `@pytest.mark.asyncio`; no `asyncio_mode` set — fine, but make it intentional).
- [ ] Confirm the wheel ships `krcg/cards/**` (CSV/YAML + translation dirs) and **excludes** `twda.json` (it's downloaded at runtime). `MANIFEST.in` uses `graft krcg`; verify hatch includes the data and that any locally-synced `twda.json` is kept out of the build.
- [ ] `pydoclint` and `types-requests` removed — make sure nothing in CI/docs still calls them.

### 4.9 Docs
- [ ] Rewrite README usage for the new API (explicit loaders, async, `providers`, no module singleton).
- [ ] CHANGELOG entry under **5.0**; bump `pyproject` version from 4.x to 5.0.
- [ ] Migration notes for offspring projects (krcg-cli, krcg-api, krcg-static, krcg-bot) — they all consume the old singleton/`Deck`-as-`Counter` API.

## 5. Decisions (resolved)

1. **Version** — V3 ships as **`5.0`** (major break). Update `pyproject` + CHANGELOG.
2. **TWDA distribution** — **not** bundled. Lazily downloaded from **static.krcg.org** (the reference source); `fetch_twda.py` generates the json that gets published there.
3. **Pickle cache** — `load_online` invalidates systematically (always rebuilds/overwrites the version-keyed pickle); `load()` reads cache → falls back to bundled CSVs. See §4.1.
4. **Languages** — trim `models.Lang` to **en/fr/es** (only synced data).
5. **Back-compat** — **clean break**, documented in a migration guide. A thin deprecated shim (e.g., a lazy module-level `VTES`/`TWDA`) is a *nice-to-have* only if low-effort; not required.

## 6. Explicitly in / out of scope

- **In scope for V3:** models, collections/search, vekn_csv loading, vtes/twda loaders, providers, rulings wiring, parser, **analyzer + seating port**, tests, packaging, docs.
- **Out of scope / follow-up:** none committed yet — list here as they come up.
