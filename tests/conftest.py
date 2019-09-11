import requests
import pytest


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
