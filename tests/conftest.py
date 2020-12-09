import os
import requests
import pytest


from krcg import config
from krcg import twda
from krcg import vtes


def pytest_sessionstart(session):
    """Do not launch tests is there is no proper Internet connection."""
    try:
        requests.get("http://www.google.com", timeout=1)
    except requests.exceptions.RequestException:
        pytest.fail("No internet connection")
    try:
        requests.get(config.KRCG_STATIC_SERVER, timeout=1)
    except requests.exceptions.RequestException:
        pytest.fail("KRCG website not available")
    vtes.VTES.load_from_vekn()


@pytest.fixture(scope="session")
def TWDA():
    """Use to initialize the twda to the 20 decks test snapshot."""
    with open(os.path.join(os.path.dirname(__file__), "TWDA.html")) as f:
        twda.TWDA.load_html(f)
        return twda.TWDA
