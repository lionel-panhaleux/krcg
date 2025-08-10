"""Configuration for pytest."""

import os
import requests
import pytest


from krcg import config


def _internet_available() -> bool:
    """Check if the internet is available."""
    if os.getenv("FORCE_OFFLINE"):
        return False
    try:
        requests.get("http://www.google.com", timeout=1)
        requests.get(config.KRCG_STATIC_SERVER, timeout=1)
        return True
    except requests.exceptions.RequestException:
        return False


def pytest_sessionstart(session: pytest.Session) -> None:
    """Initialize VTES from local packaged CSVs; avoid network in tests."""
    # Prefer local CSVs packaged under the `cards` package only when offline
    if _internet_available():
        os.environ.pop("LOCAL_CARDS", None)
    else:
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


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Skip only internet-dependent tests when offline."""
    if _internet_available():
        return
    internet_tests = {
        # Static server and remote CSV paths
        "tests/test_cards.py::test_load_from_static_server",
        "tests/test_cards.py::test_load_from_vekn_github_default",
        "tests/test_cards.py::test_load_from_vekn_vekn_net",
        # External deck providers
        "tests/test_deck.py::test_from_amaranth",
        "tests/test_deck.py::test_from_vdb",
        "tests/test_deck.py::test_from_vtesdecks",
        # i18n assertions
        "tests/test_vtes.py::test_i18n",
        "tests/test_vtes.py::test_search_i18n",
    }
    skip_marker = pytest.mark.skip(reason="Skipped: no internet connection available")
    for item in items:
        nodeid = item.nodeid
        if nodeid in internet_tests or nodeid.startswith("tests/test_states.py::"):
            item.add_marker(skip_marker)
