import os
import requests
import pytest


from krcg import vtes


def pytest_sessionstart(session):
    """Do not launch tests is there is no proper Internet connection.

    This is not very graceful
    """
    try:
        requests.get("http://www.google.com", timeout=1)
    except requests.exceptions.RequestException:
        pytest.fail("No internet connection")
    try:
        requests.get("http://www.vekn.net", timeout=1)
    except requests.exceptions.RequestException:
        pytest.fail("VEKN website not available")
    vtes.VTES.load_from_vekn(save=False)
    vtes.VTES.configure()


@pytest.fixture
def twda():
    """Use to initialize the twda to the 20 decks test snapshot."""
    from krcg import twda

    TWDA = twda._TWDA()
    with open(os.path.join(os.path.dirname(__file__), "TWDA.html")) as f:
        TWDA.load_html(f, save=False)
    TWDA.configure()
    twda.TWDA = TWDA
    return TWDA
