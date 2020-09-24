import requests
import pytest

from krcg import twda
from krcg import vtes


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
    vtes.VTES.load_from_vekn(save=False)
    vtes.VTES.configure()
    twda.TWDA.load_from_vekn(limit=100, save=False)
    twda.TWDA.configure()
