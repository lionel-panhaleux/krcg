"""Configuration for pytest."""

import os
import urllib.request
import urllib.error
import pytest


def _internet_available() -> bool:
    """Check if the internet is available."""
    if os.getenv("FORCE_OFFLINE"):
        return False
    try:
        urllib.request.urlopen("http://www.google.com", timeout=1)
        return True
    except (urllib.error.URLError, OSError):
        return False


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
