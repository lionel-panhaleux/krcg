"""Sets (expansions) information
"""

import datetime
from typing import Hashable

from . import utils


class Set(utils.i18nMixin, utils.NamedMixin):
    """A class representing a V:tES Set (expansion)."""

    def __init__(self, **kwargs):
        super().__init__()
        self.id = 0
        self.abbrev = kwargs.get("abbrev", None)
        self.release_date = kwargs.get("release_date", None)
        self.name = kwargs.get("name", None)
        self.company = kwargs.get("abbrev", None)

    def from_vekn(self, data: dict):
        """Load info from VEKN CSV dict."""
        self.id = int(data["Id"])
        self.abbrev = data["Abbrev"]
        self.release_date = (
            datetime.datetime.strptime(data["Release Date"], "%Y%m%d")
            .date()
            .isoformat()
        )
        self.name = data["Full Name"]
        self.company = data["Company"]


class SetMap(dict):
    """A dict of all sets, index by Abbreviation and English name."""

    PROMOS = {
        "Promo-20231007": ["2023 Mineiro Promo", "2023-10-07"],
        "Promo-20230916": ["2023 Zaragosa Promo", "2023-09-16"],
        "Promo-20230729": ["2023 Ropecon Promo", "2023-07-29"],
        "Promo-20230603": ["2023 Andalusian Open Promo", "2023-06-03"],
        "Promo-20230501": ["2023 War of the Ages Promo", "2023-05-01"],
        "Promo-20230531": ["2023 Chapters Promo", "2023-05-31"],
        "Promo-20230507": ["2023 Belgian Championship Promo", "2023-05-07"],
        "Promo-20230325": ["2023 Spanish National Promo", "2023-03-25"],
        "Promo-20221105": ["2022 EC Promo", "2022-11-05"],
        "Promo-20221101": ["2022 Fee Stake Promo", "2022-11-01"],
        "Promo-20221022": ["2022 Promo", "2022-10-22"],
        "HttBR": ["Heirs to the Blood Reprint", "2018-07-14"],
        "KoTR": ["Keepers of Tradition Reprint", "2018-05-05"],
    }

    def __init__(self):
        super().__init__()
        self.add(Set(abbrev="POD", name="Print on Demand"))
        for abbrev, (name, release_date) in self.PROMOS.items():
            self.add(Set(abbrev=abbrev, name=name, release_date=release_date))

    def add(self, set_: Set) -> None:
        """Add a set to the map."""
        self[set_.abbrev] = set_
        self[set_.name] = set_

    def i18n_set(self, set_: Set) -> None:
        """Add a translation for a set."""
        self[set_.abbrev].i18n_set()


class DefaultSetMap(dict):
    """A default map with no information other than the set abbreviation.

    Can be used to enable card information parsing when no set info is available.
    """

    def __getitem__(self, k: Hashable) -> Set:
        return Set(id=1, abbrev=k, name=k)


#: Use the default set map to parse cards information with no set information available
DEFAULT_SET_MAP = DefaultSetMap()
