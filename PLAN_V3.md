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

### Done so far (commits on `lip/v3`)
- ✅ **models**: dataclass model + msgspec round-trip; `CardMinimal.from_card`, `CardInDeck.of`, `Deck.raven`; `datetime.date` (no field/type shadow); `Lang` trimmed to en/fr/es.
- ✅ **rulings** wired into `VTES.load_local()`; `_parse_text` uses `CardMinimal.from_card`; group rulings carry `Ruling.group`. `load_online` does not double-load (static JSON embeds rulings).
- ✅ **vtes.py**: `load()` / `load_local()` / `load_online(session)`; `load_online` control-flow + `kind` dispatch fixed; `VTES.parse()` / `VTES.to_twd()` convenience.
- ✅ **twda.py**: ported to a **bundled compressed snapshot** (`krcg/cards/twda.json.xz`, 1.35 MB lzma, ~0.28 s decode) — **decision reversed from §5.2**: bundled, not network-only. `load_local()` (offline default) + `load_online(session)` (static, falls back to bundled). No import-time global; 52 MB `twda.json` removed. `DecksArchive = dict[str, models.Deck]`.
- ✅ **parser.py**: `deck_from_txt(source: Iterable[str], cards: CardDict, *, id="", twda=False)`; dropped `offset`/`preface` param/`**kwargs`; `vtes` import removed (broke the cycle).
- ✅ **TWD serialization fidelity** (`providers.serialize_twd`): crypt comments, exact columns, accents kept / symbols folded, library sort by VEKN name, date ranges. Validated by round-trip vs GiottoVerducci/TWD: **100% cards, 99.8% semantic, 100% card comments**; ~33% byte-exact ignoring score (rest are justifiable canonicalizations — score uses our format, will PR the archive to realign).
- ✅ **deleted** `sets.py` and the dead legacy `__cards/__deck/__utils/__config`.
- ✅ **lint/types**: ruff fully clean; mypy clean on every module **except `analyzer.py`**.

### 4.A analyzer.py port — ✅ DONE (`just quality` now fully green)
- ✅ **Dropped the `Analyzer` class for free functions** over a deck collection, each taking a loaded `VTES` to resolve `CardInDeck.id` → `models.Card` (mirrors `serialize_twd(deck, cards_dict)`): `played(decks, VTES, kind=)`, `stats(decks, VTES, kind=)` → `(mean, variance)`, `affinity(decks, VTES, *ref, similarity=1.0, kind=)` (folds v2's `refresh(sim=1)` + `candidates` into one ranked call). Float accumulators are `defaultdict[Card, float]` (Counter values are int-typed under mypy-strict).
- ✅ **`build_deck` kept** (per decision) as a single self-contained function with the build-session state as locals/closures (`refresh`/`build_part` nested), reusing the shared `_spoilers`/`_similar`/`_affinity` helpers. Faithful to v2 (similarity 0.6, crypt-then-library, average-count fill, periodic re-sample); v2's `cursor=0` first-refresh trick replaced by an explicit up-front `refresh` per part. Verified: `build_deck(..., Nana Buruku)` → 12-card crypt + 90-card library.
- ✅ **README + `test_analyzer.py`** updated to the functional API (2019-slice numbers are unchanged by the port — same data, same math).

### 4.B seating.py port
- [ ] Imports clean and mypy-clean already, but **not verified to run** against the new `models.Deck`. Confirm end-to-end and restore `tests/test_seating.py`.

### 4.C Test migration (tests are NOT yet truth-bearing)
- [ ] `conftest.py`: session-scoped `VTES` (via `load_local()`) and TWDA fixture. TWDA is now bundled (xz) → tests can use `twda.load_local()`; no network needed.
- [ ] `test_parser.py`: old `Parser()` no-arg + `deck_from_txt(f)` (no cards) signatures → new API.
- [ ] `test_twda.py` / `test_states.py` / `test_deck.py`: fail at fixture setup on removed `twda.TWDA` / `_TWDA` singleton → migrate to `twda.load_local()` + `providers.*` serializers.
- [ ] `test_vtes.py`: `vtes.VTES` is now a class; `search()` is keyword-only, returns a **sorted list** (not set), `n` default 100; `complete()` returns `list[Card]`; `search_dimensions` values are `list[str | None]`.
- ✅ `test_analyzer.py`: ported with 4.A (dense test over the bundled TWDA: played/affinity/stats + a build_deck round-trip).

### 4.D Latent bugs & robustness follow-ups — ✅ DONE
- ✅ **`Translation.url`** — added `url: str = ""` to `models.Translation` (per-language card URL); removed the `# type: ignore[attr-defined]` in `vekn_csv.py`.
- ✅ **Non-standard TWD headers / faithful rounds** — root cause was a rigid `RoundFormat` enum (`N/A`/`2R+F`/`3R+F`) that couldn't hold `4R+F` or `3R (no final)`, so the line fell through `parse_twda_headers` and poisoned the `player` field (decks 10842, 2015camb). Fixed by replacing the enum with `Event.rounds: int` + `Event.finals: bool` (faithful: round-trips `3R (no final)` byte-perfect). Parser now consumes any `NR…` line so `player` is never poisoned; `serialize_twd`/`serialize_txt` render from count+finals. Verified against VEKN event pages + forum: `10842` = genuine "3 rounds, no finals" (Lotte Siebert, 7 players); `8226`/`2015camb` `4R+F` is a **TWD-report typo**, real = `3R+F` (see 4.D follow-up below).
- ✅ **`serialize_txt` date ranges** — mirrors `serialize_twd` (`start -- end`).
- ✅ **`parser.py` `# type: ignore`** — removed; narrowed `self.current_comment is not None` (after the create step, a truthy comment guarantees a current comment).

### 4.D′ Found & fixed during the card re-sync (needed to regenerate the TWDA under the new model)
- ✅ **`vekn_csv` empty-occurrences crash** — a set tag with no rarity/date (e.g. `"Gehenna:U1, POD"` → the `POD` tag) yields a `Print` with empty `occurrences`; `prints_from_vekn` sort key and `card.legal` both did `occurrences[0]` → `IndexError`. Fixed: empty prints sort **last** (so real dated prints lead `card.legal`); `card.legal` guards empty occurrences.
- ✅ **Sabbat path support in parser + serializer** — recent group-6/7 crypts show a path word (`Caine`/`Cathari`/`Death`/`Power`) in a column between disciplines and title. The parser's `_CRYPT_TAIL` choked on it (29 crypt cards dropped across the newest decks); `serialize_twd` didn't emit it. Added `_PATH` to the crypt-tail alternation and a path column to the crypt serializer (`disc · path · title · clan`). Path decks now round-trip byte-identical.
- ✅ **Card + rulings + TWDA re-sync** — refreshed `vtescrypt.csv`/`vteslib.csv`, `groups/references/rulings.yaml`, and regenerated `twda.json.xz` (now **4538** decks, up from 4375; new `rounds`/`finals` schema). Zero parse failures.

### 4.D follow-up (upstream, external)
- [ ] **PR GiottoVerducci/TWD: `4R+F` → `3R+F` for deck `2015camb`** (event 8226, Campeonato Alagoano 2015). VEKN records "3 + Final" and the recorded scores are consistent with 3R+F — the `4R+F` in the TWD report is a typo. Until merged, the bundle faithfully re-serializes `4R+F`; after the next `just sync-cards` it becomes `3R+F`. Bundle with the planned TWD score-format PR.

### 4.E Tooling & build — ✅ DONE
- ✅ **Type checker → `ty`** (decision: switch off mypy). `justfile` + CI `validation.yml` now run `ty check krcg`; dropped `[tool.mypy]` and the `types-PyYAML` stub dep (ty vends its own typeshed); removed `.mypy_cache` from `just clean` + `.gitignore`. **Zero `ty: ignore`** — the 3 errors ty surfaced that mypy tolerated were fixed properly: `FuzzyDict.__init__` simplified (the unused `*args/**kwargs`→`dict()` passthrough that forced `H | str` keys → single `data: Mapping | None`), the redundant `FuzzyDict.get` override deleted (inherit `MutableMapping.get`, which also gives callers `Card | None` instead of `Any`), and `CardDict.__iter__`-yields-values turned into an explicit `.cards()` method (internal-only; the public `for c in VTES` still yields cards via `VTES.__iter__`). 2 now-stale mypy `# type: ignore` removed.
- ✅ **`requires-python` → `>=3.12`** (per request; code is PEP 695 but no 3.13-only syntax — verified). Classifiers now 3.12/3.13/3.14; **CI matrix fixed** `3.10–3.13` → `3.12–3.14` (the old matrix could never pass: PEP 695 needs ≥3.12).
- ✅ **pytest-asyncio**: all 4 async tests already carry `@pytest.mark.asyncio`; no async fixtures so no `loop_scope` warning. Added explicit `asyncio_mode = "strict"` for clarity/future-proofing.
- ✅ **Packaging verified**: built wheel ships all 15 `krcg/cards/**` files **including `twda.json.xz`** (no stray uncompressed `twda.json`); `Requires-Python: >=3.12`; `setuptools` dropped from runtime deps (nothing imports it / `pkg_resources`; numpy stays — used by seating).
- ✅ **`pydoclint` / `types-requests`**: types-requests already gone (no `requests` import); removed the stale `pydoclint`/`mypy` mentions from README + CLAUDE.md.
- Regression check: full suite is 40 failed / 11 passed / 2 errors **identical** with and without these changes — the CardDict/FuzzyDict refactor added zero regressions (all failures are pre-existing 4.C test debt).

### 4.F Docs
- [ ] Rewrite README for the new API (explicit loaders, async, `providers`, no module singleton, `VTES.parse`/`to_twd`).
- [ ] CHANGELOG under **5.0**; bump `pyproject` version 4.x → 5.0.
- [ ] Migration notes for offspring (krcg-cli, krcg-api, krcg-static, krcg-bot) — they consume the old singleton / `Deck`-as-`Counter` API. Note the **TWD score format change** (we emit our canonical form) and that a PR to GiottoVerducci/TWD will realign the archive.

## 5. Decisions (resolved)

1. **Version** — V3 ships as **`5.0`** (major break). Update `pyproject` + CHANGELOG.
2. **TWDA distribution** — **bundled, compressed** (`krcg/cards/twda.json.xz`, lzma, 1.35 MB) — *reversed from the original "not bundled" plan* once compression made it package-sized; gives offline parity with the cards/rulings data. `load_local()` is the offline default; `load_online(session)` fetches static.krcg.org and falls back to the bundled snapshot. `fetch_twda.py` regenerates the `.xz` (and still publishes to static for online tools). No pickle cache for TWDA (one ~0.28 s decode).
3. **Pickle cache (VTES only)** — `load_online` invalidates systematically (always rebuilds/overwrites the version-keyed pickle); `load()` reads cache → falls back to bundled CSVs via `load_local()`.
4. **Languages** — trim `models.Lang` to **en/fr/es** (only synced data).
5. **Back-compat** — **clean break**, documented in a migration guide. A thin deprecated shim (e.g., a lazy module-level `VTES`/`TWDA`) is a *nice-to-have* only if low-effort; not required.

## 6. Explicitly in / out of scope

- **In scope for V3:** models, collections/search, vekn_csv loading, vtes/twda loaders, providers, rulings wiring, parser, **analyzer + seating port**, tests, packaging, docs.
- **Out of scope / follow-up:** none committed yet — list here as they come up.
