"""Configuration for pytest."""

from collections.abc import Generator
import itertools
import os
import requests
import pytest
from typing import Any


from krcg import config

# Bundled French translation CSVs (mirrors CardMap._VEKN_CSV_I18N["fr-FR"]).
# The i18n tests rely on the global VTES having these translations loaded, which
# only happens when the CSVs are bundled in the `cards` package.
_FR_I18N_FILES = ("vtessets.fr-FR.csv", "vtescrypt.fr-FR.csv", "vteslib.fr-FR.csv")


def _internet_available() -> bool:
    """Check if the internet is available.

    A reachable host that answers with an error status (e.g. a blocking proxy
    returning ``403``) is treated as *offline*: the request technically
    succeeds but we cannot actually fetch remote resources, so tests that need
    real network access must be skipped rather than left to fail.
    """
    if os.getenv("FORCE_OFFLINE"):
        return False
    try:
        for url in ("http://www.google.com", config.KRCG_STATIC_SERVER):
            if not requests.get(url, timeout=1).ok:
                return False
        return True
    except requests.exceptions.RequestException:
        return False


def _i18n_bundled() -> bool:
    """Return True if the French translation CSVs are bundled in `cards`."""
    from krcg import cards

    return all(cards._local_csv_exists(name) for name in _FR_I18N_FILES)


def pytest_sessionstart(session: pytest.Session) -> None:
    """Initialize VTES from local packaged CSVs; never touch the network.

    Building the global VTES deterministically from the bundled CSVs keeps the
    suite reproducible and avoids aborting collection when remote sources (e.g.
    the VEKN.net translation archives) are unreachable. Tests that genuinely
    need the network do their own loading and are skipped when offline.
    """
    os.environ["LOCAL_CARDS"] = "1"
    # Build VTES from local CSVs (includes sets from local vtessets.csv)
    from krcg import vtes  # delayed import so env is set before module init

    vtes.VTES.load_from_vekn()


@pytest.fixture(scope="session")
def TWDA():  # type: ignore
    """Use to initialize the twda to the 20 decks test snapshot."""
    from krcg import twda  # delayed import to avoid early vtes import

    with open(os.path.join(os.path.dirname(__file__), "TWDA.html")) as f:
        twda.TWDA.load_html(f)
        return twda.TWDA


@pytest.fixture(scope="session")
def vtes_with_translations() -> Generator[None, Any, None]:
    """Ensure VTES has i18n translations loaded for tests that need them.

    If bundled i18n CSVs are present they were already loaded in session_start.
    Otherwise download them from VEKN (requires internet) and apply them to the
    already-loaded cards, then clear translations on teardown so subsequent tests
    see a clean, translation-free VTES.
    """
    from krcg import cards as cards_module, sets as sets_module
    from krcg import utils, vtes as vtes_module

    if _i18n_bundled():
        yield
        return

    if not _internet_available():
        pytest.skip("Skipped: bundled i18n CSVs not available and no internet")
        return

    # Build a SetMap from the bundled vtessets.csv so we can translate set names.
    set_dict = sets_module.SetMap()
    for line in cards_module._local_csv_reader("vtessets.csv"):
        s = sets_module.Set()
        s.from_vekn(line)
        set_dict.add(s)

    translated_ids: list[int] = []
    for lang, (url, filenames) in cards_module.CardMap._VEKN_CSV_I18N.items():
        files = utils.get_zip_csv(url, *filenames)
        # Apply translated set names to set_dict.
        for row in files[0]:
            abbrev = row["Abbrev"]
            if abbrev in set_dict:
                set_dict[abbrev].i18n_set(lang, {"name": row["Full Name"]})
        # Apply card translations.
        for row in itertools.chain.from_iterable(files[1:]):
            name = row.pop("Name")
            cid = int(row.pop("Id"))
            row["Name"] = row.pop("Name " + lang, "")
            if cid not in vtes_module.VTES:
                continue
            card = vtes_module.VTES[cid]
            if card._name != name:
                continue
            trans: dict = {
                "name": row["Name"],
                "url": card._compute_url(lang[:2]),
                "card_text": row.get("Card Text", "").replace("(D)", "Ⓓ"),
                "sets": {
                    set_name: set_dict[set_name].i18n_field(lang[:2], "name")
                    for set_name in card.sets
                    if set_name in set_dict
                },
            }
            if row.get("Flavor Text"):
                trans["flavor_text"] = row["Flavor Text"]
            card.i18n_set(lang[:2], trans)
            if cid not in translated_ids:
                translated_ids.append(cid)

    yield

    # Clear added translations so later tests see a clean VTES.
    for card_id in translated_ids:
        if card_id in vtes_module.VTES:
            vtes_module.VTES[card_id]._i18n.clear()


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Skip tests whose prerequisites (network or bundled i18n) are unmet."""
    internet_available = _internet_available()
    i18n_bundled = _i18n_bundled()
    # Tests that reach out to the network and must be skipped when offline.
    internet_tests = {
        # Static server and remote CSV paths
        "tests/test_cards.py::test_load_from_static_server",
        "tests/test_cards.py::test_load_from_vekn_github_default",
        "tests/test_cards.py::test_load_from_vekn_vekn_net",
        # External deck providers
        "tests/test_deck.py::test_from_amaranth",
        "tests/test_deck.py::test_from_vdb",
        "tests/test_deck.py::test_from_vtesdecks",
        # TWDA snapshot is fetched from the KRCG static server
        "tests/test_twda.py::test_load_and_dump",
    }
    # Tests that need translations loaded into the global VTES. Since the
    # session builds VTES in LOCAL_CARDS mode, these depend on the bundled i18n
    # CSVs being present rather than on internet access.
    i18n_tests = {
        "tests/test_vtes.py::test_i18n",
        "tests/test_vtes.py::test_search_i18n",
    }
    no_internet = pytest.mark.skip(reason="Skipped: no internet connection available")
    no_i18n = pytest.mark.skip(reason="Skipped: bundled i18n CSVs not available")
    for item in items:
        nodeid = item.nodeid
        if nodeid in i18n_tests:
            if not i18n_bundled:
                item.add_marker(no_i18n)
            continue
        if not internet_available and (
            nodeid in internet_tests or nodeid.startswith("tests/test_states.py::")
        ):
            item.add_marker(no_internet)
