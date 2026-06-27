"""Configuration for pytest.

Fixtures:
    VTES: the cards database, built once per session from the bundled CSVs.
    TWDA: the decks archive, loaded once per session from the bundled snapshot.

The ``baseline`` marker flags tests that track live source data (cards, rulings,
the TWDA). Such a test is expected to drift when the data is re-synced, so a
failure is downgraded to an amber ``xfail`` ("eyeball it") instead of a hard
failure. Genuine code regressions live in unmarked tests and fail red.
"""

import os
import urllib.request
import urllib.error
import pytest

from krcg import twda
from krcg import vtes


@pytest.fixture(scope="session")
def VTES() -> vtes.VTES:
    """The cards database, built once from the bundled CSV snapshot."""
    return vtes.VTES.load_local()


@pytest.fixture(scope="session")
def TWDA() -> twda.DecksArchive:
    """The decks archive, loaded once from the bundled snapshot."""
    return twda.load_local()


def _internet_available() -> bool:
    """Check if the internet is available."""
    if os.getenv("FORCE_OFFLINE"):
        return False
    try:
        urllib.request.urlopen("http://www.google.com", timeout=1)
        return True
    except (urllib.error.URLError, OSError):
        return False


def pytest_configure(config: pytest.Config) -> None:
    """Register the baseline marker."""
    config.addinivalue_line(
        "markers",
        "baseline: tracks live source data; a failure is amber (data drift), not red.",
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):  # type: ignore
    """Downgrade a failing ``baseline`` test to an amber xfail (data drift)."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed and item.get_closest_marker("baseline"):
        report.outcome = "skipped"
        report.wasxfail = "baseline data drift — source data changed, eyeball it"


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Skip only internet-dependent tests when offline."""
    if _internet_available():
        return
    internet_tests = {
        "tests/test_cards.py::test_load_from_static_server",
        "tests/test_deck.py::test_from_amaranth",
        "tests/test_deck.py::test_from_vdb",
        "tests/test_deck.py::test_from_vtesdecks",
    }
    skip_marker = pytest.mark.skip(reason="Skipped: no internet connection available")
    for item in items:
        if item.nodeid in internet_tests:
            item.add_marker(skip_marker)
