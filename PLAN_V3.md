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

### 4.B seating.py port — ✅ DONE (no code changes needed)
- ✅ **No deck/card dependency** — the plan's "against the new `models.Deck`" was wrong: seating is self-contained (numpy + multiprocessing over player indices; no `models`/`vtes`/`twda` import). ty + ruff already clean.
- ✅ **Verified end-to-end**: all 7 `tests/test_seating.py` pass (get_rounds, Round, measure/Measure, Score, optimise, optimise_table), and `archon_seating(12, 3)` runs the ProcessPoolExecutor path → 3 rounds × 3 tables, all 12 players seated.
- ✅ **Done in 4.F**: README seating examples now use `seating.get_rounds(...)` (was `permutations`); the rename is also called out in the offspring migration section.

### 4.C Test migration — ✅ DONE (suite now truth-bearing; `just quality` fully green; 47 passed)
- ✅ **`conftest.py`**: session-scoped `VTES` (`load_local()`) + `TWDA` (`twda.load_local()`) fixtures; offline-skip trimmed to the genuinely internet-dependent tests (static-server load, external deck providers) — i18n and the old `test_states` now run offline (translations/rulings load from the bundle).
- ✅ **Amber/baseline mechanism** (per request): a `@pytest.mark.baseline` marker + a `pytest_runtest_makereport` hook that downgrades a baseline failure to an `xfail` ("source data drifted — eyeball it"). Data-tracking tests are amber (non-blocking, in CI too); logic regressions on frozen fixtures stay red.
- ✅ **`test_twda.py` rewritten**: HTML parsing is gone, so the 15 `.html`+`to_json` per-deck tests were replaced by **5 frozen `tests/twd_*.txt` fixtures** re-generated from the *current* TWDA source, hand-picked for peculiarities (10842 no-final + quoted name + score-across-rounds; 13259 Sabbat path + accents + 2026; 10792 rich comments + `&`; 10073 date-range + online; 2k2amstelveen legacy no-rounds-header). Dense header/feature tests + a parametrized round-trip (core) + one `test_bundle_integrity` (baseline).
- ✅ **`test_parser.py`**: `Parser()` → `Parser(cards_db, twda=…)`; `get_card` now returns `CardInDeck|None` (adapter `gc()` keeps the `(Card, count)` assertions); TWDA-mode discipline-warning split into its own test. Dropped the dead `"Mask of 1000 Faces"` alias assertion (missing from v3 `config.ALIASES` — see follow-up).
- ✅ **`test_deck.py`**: serializer tests use a frozen `twd_2010tcdbng.txt` fixture (vdb/minimal exact; txt/twd/jol/lackey structural) — core; provider fetch tests migrated off `utils.jsonize` to key-fact assertions, internet-gated.
- ✅ **`test_tournament_archive.py`**: `deck_from_txt(f, cards)` + structural assertions (no `to_json`).
- ✅ **`test_vtes.py`**: search **mechanics** (raises/empty/trigram + in/not-in classification cornercases) and i18n/dimensions are core; exact-result-list searches → `test_search_results` (count + spot card, baseline); one `test_card_snapshot` baseline via `tests/snapshots/*.json`; `json_encode`/`_VTES` gone.
- ✅ **`test_states.py`**: now a ruling test — core `test_ruling_structure` (references/symbols parse) + baseline ruling-card snapshots (`tests/snapshots/`).
- ✅ **`test_cards.py`**: `test_card_variants` marked baseline (translation-dependent), uses the `VTES` fixture; dropped debug-print cruft.
- ✅ `test_analyzer.py`: ported with 4.A.
- ✅ **Follow-up done**: re-added `"Mask of 1000 Faces"` to `vekn_csv.ALIASES` (not `config.ALIASES` — that module is gone in V3) with its parser-test assertion restored (commit `687b69e`).

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

### 4.E′ Drop the `VTES` class — ✅ DONE (commit `f0d281a`)
- ✅ **`collections.CardDict` is the single cards handle** (option b): it owns the search index and sets, and exposes `index()` / `complete()` / `search()` / `search_dimensions` directly. Deck ops stay free functions (`parser.deck_from_txt`, `providers.serialize_twd`); the `VTES.parse` / `VTES.to_twd` wrappers and the `_cards` leak are gone. New `loader.py` (`load` / `load_local` / `load_online` → `CardDict`, re-exported as `krcg.load*`); `vtes.py` deleted; `twda.load()` added to mirror; `search` coerces a bare string to a one-element list.
- ✅ **Test suite re-migrated** to the loader/`CardDict` API (f0d281a had updated the package but not the tests, breaking collection): `VTES` fixture → `cards` (`loader.load_local()`); `VTES.parse/to_twd` → `parser.deck_from_txt`/`providers.serialize_twd`; `VTES._cards` → `cards`; `list(VTES)` → `cards.cards()`. `just quality` green; **47 passed**.

### 4.F Docs — ✅ DONE
- ✅ **README rewritten** for the new API: explicit loaders (sync `load`/`load_local`, async `load_online(session)`), `CardDict.search`/`complete`, `twda.load*` → `dict[str, Deck]`, `parser.deck_from_txt`, `providers.serialize_*`/`fetch`, analyzer free functions, `seating.get_rounds`. All examples run against the current bundled data. Added a **"Migrating from 4.x"** section (the offspring migration notes). Badge/installation → `>=3.12`.
- ✅ **CHANGELOG** `5.0` entry; `pyproject` version `4.19` → `5.0`.
- ✅ **CLAUDE.md** architecture rewritten (no-singletons, the real data-loading paths, current module map, env-vars trimmed to `FORCE_OFFLINE`); stale `config.py`/`load_html`/`load_from_vekn` references removed.
- ✅ **Re-added `"Mask of 1000 Faces"`** to `vekn_csv.ALIASES` (the 4.C follow-up) with its parser-test assertion restored (commit `687b69e`).
- ✅ **Removed obsolete/vestigial code**: `utils/csv.py` (dead network-CSV fetch), `utils/deck.py:to_txt` (superseded by `providers.serialize_txt`), the no-op `LOCAL_CARDS`/`VEKN_NET_CSV` test monkeypatch, and the stub `tests/__init__.py` / `profiling/__init__.py`.
- ✅ **`seating.optimise` "non-convergence" — diagnosed, not a bug.** The default `fixed=len-1` only re-seats the *last* round (by design: building rounds one at a time as attendance changes). A from-scratch call on a fresh `get_rounds(...)` therefore leaves the identical earlier rounds in place → `R1=12`. Pre-computing a full seating for fixed attendance uses **`fixed=1`** (fix the arbitrary first round, optimise the rest) → `[0,0,0,9,0,0,0,~0.37,~2]`, matching the old README. Decision: keep the default (last-round). Docs-only fix — README example now passes `fixed=1`; `optimise` docstring spells out both modes.
- ✅ Migration notes for offspring (krcg-cli, krcg-api, krcg-static, krcg-bot) — folded into the README **"Migrating from 4.x"** section (old singleton / `Deck`-as-`Counter` → loader/`CardDict`; free-function deck ops; async I/O; `seating.permutations` → `get_rounds`). The **TWD score format change** (we emit our canonical form) and the GiottoVerducci/TWD realign PR are tracked under the 4.D follow-up above.

## 5. Decisions (resolved)

1. **Version** — V3 ships as **`5.0`** (major break). Update `pyproject` + CHANGELOG.
2. **TWDA distribution** — **bundled, compressed** (`krcg/cards/twda.json.xz`, lzma, 1.35 MB) — *reversed from the original "not bundled" plan* once compression made it package-sized; gives offline parity with the cards/rulings data. `load_local()` is the offline default; `load_online(session)` fetches static.krcg.org and falls back to the bundled snapshot. `fetch_twda.py` regenerates the `.xz` (and still publishes to static for online tools). No pickle cache for TWDA (one ~0.28 s decode).
3. **Pickle cache (VTES only)** — `load_online` invalidates systematically (always rebuilds/overwrites the version-keyed pickle); `load()` reads cache → falls back to bundled CSVs via `load_local()`.
4. **Languages** — trim `models.Lang` to **en/fr/es** (only synced data).
5. **Back-compat** — **clean break**, documented in a migration guide. A thin deprecated shim (e.g., a lazy module-level `VTES`/`TWDA`) is a *nice-to-have* only if low-effort; not required.

## 6. Explicitly in / out of scope

- **In scope for V3:** models, collections/search, vekn_csv loading, vtes/twda loaders, providers, rulings wiring, parser, **analyzer + seating port**, tests, packaging, docs.
- **Out of scope / follow-up:** none committed yet — list here as they come up.
