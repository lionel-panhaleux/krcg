import os.path
import requests
import pytest

from src import twda
from src import vtes


def pytest_sessionstart(session):
    """Do not launch tests is there is no proper Internet connection.

    This is not very graceful
    """
    try:
        requests.get("http://www.google.com")
    except requests.exceptions.RequestException:
        pytest.fail("No internet connection")
    try:
        requests.get("http://www.vekn.net")
    except requests.exceptions.RequestException:
        pytest.fail("VEKN website not available")


def load_twda_file(file_name):
    path = os.path.join(os.path.dirname(__file__), file_name)
    with open(path, "r", encoding="utf-8") as source:
        for lines, twda_id in twda.TWDA._get_decks_html(source):
            twda.TWDA[twda_id] = twda.TWDA._load_deck_html(lines, twda_id)


# speed up the tests: parse the first 100 decks only to avoid useless 25 seconds.
@pytest.fixture(scope="session")
def krcg():
    vtes.VTES.load_from_vekn(save=False)
    twda.TWDA.load_from_vekn(limit=100, save=False)
    vtes.VTES.configure()
    twda.TWDA.configure()
