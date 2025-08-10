"""Test tournament archive."""

import datetime
import logging
import os
import pytest

from krcg import deck


def test_202207_EC_Day1_1(caplog: pytest.LogCaptureFixture) -> None:
    """The reference format for tournament extended archive decks."""
    caplog.set_level(logging.WARNING)
    with open(os.path.join(os.path.dirname(__file__), "202207_EC_Day1_1.txt")) as f:
        dek = deck.Deck.from_txt(f)
    assert dek
    assert dek.to_json() == {
        "name": "202207_EC_Day1_1",
        "player": "VtesEC2022",
        "score": "2GW6.5",
        "date": datetime.date.today().isoformat(),
        "crypt": {
            "cards": [
                {"count": 3, "id": 200781, "name": "Khurshid"},
                {"count": 2, "id": 201009, "name": "Mordechai Ben-Nun"},
                {"count": 2, "id": 200119, "name": "Anu Diptinatpa"},
                {"count": 5, "id": 200076, "name": "Anarch Convert"},
            ],
            "count": 12,
        },
        "library": {
            "cards": [
                {
                    "cards": [
                        {"count": 3, "id": 100545, "name": "Direct Intervention"},
                        {
                            "count": 1,
                            "id": 100785,
                            "name": "Fragment of the Book of Nod",
                        },
                        {"count": 1, "id": 100897, "name": "Haven Uncovered"},
                        {"count": 6, "id": 101112, "name": "Liquidation"},
                        {"count": 5, "id": 101401, "name": "Piper"},
                        {"count": 4, "id": 102121, "name": "Villein"},
                        {"count": 1, "id": 102180, "name": "Wider View"},
                    ],
                    "count": 21,
                    "type": "Master",
                },
                {
                    "cards": [
                        {"count": 4, "id": 100813, "name": "Gear Up"},
                        {"count": 2, "id": 101831, "name": "Soul Feasting"},
                    ],
                    "count": 6,
                    "type": "Action",
                },
                {
                    "cards": [
                        {"count": 10, "id": 100634, "name": "Emerald Legionnaire"}
                    ],
                    "count": 10,
                    "type": "Ally",
                },
                {
                    "cards": [{"count": 2, "id": 102107, "name": "Vengeful Spirit"}],
                    "count": 2,
                    "type": "Retainer",
                },
                {
                    "cards": [{"count": 2, "id": 102026, "name": "Trochomancy"}],
                    "count": 2,
                    "type": "Action Modifier",
                },
                {
                    "cards": [
                        {
                            "count": 3,
                            "id": 100628,
                            "name": "Eluding the Arms of Morpheus",
                        },
                        {"count": 9, "id": 100680, "name": "Eyes of Argus"},
                        {"count": 5, "id": 100868, "name": "Guardian Vigil"},
                        {"count": 3, "id": 101259, "name": "My Enemy's Enemy"},
                        {"count": 7, "id": 101949, "name": "Telepathic Misdirection"},
                    ],
                    "count": 27,
                    "type": "Reaction",
                },
                {
                    "cards": [
                        {"count": 3, "id": 100113, "name": "Aura Reading"},
                        {"count": 6, "id": 100918, "name": "Hidden Strength"},
                        {"count": 2, "id": 101649, "name": "Rolling with the Punches"},
                        {"count": 6, "id": 101942, "name": "Target Vitals"},
                        {"count": 2, "id": 101945, "name": "Taste of Vitae"},
                    ],
                    "count": 19,
                    "type": "Combat",
                },
                {
                    "cards": [
                        {
                            "count": 1,
                            "id": 100709,
                            "name": "FBI Special Affairs Division",
                        },
                        {"count": 2, "id": 102079, "name": "The Unmasking"},
                    ],
                    "count": 3,
                    "type": "Event",
                },
            ],
            "count": 90,
        },
    }
