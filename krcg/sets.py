"""Sets (expansions) information
"""

import datetime
from typing import Hashable

from . import utils

# We might want to rework sets and rarity presentation
# See https://gamingwithbs.wordpress.com/vtes-set-information/
# and https://en.wikipedia.org/wiki/Vampire:_The_Eternal_Struggle
#
# From Duelist no. #12, p. 71, September 1996
# Ancient Hearh cards are printed on three types of sheets: common, uncommon/vampire,
# and uncommon/rare. The projected average distribution for an Ancient Hearts booster is
# six cards from the common sheet, four cards from the uncommon vampire sheet, and
# two cards from the uncommon/rare sheet
# in CSV the unco/rares are listed as U and the unco/vamp are listed as V
# totals are clean but probably uncos should simply be listed as rares
# {'Common': 100, 'Vampire': 200, 'Uncommon': 126, 'Rare': 74}
#
# Also "The Sabbat" rarities are probably wrong, cf. Duelist #14
# https://archive.org/details/the-duelist-14/page/n75/mode/2up
# And the totals don't match sheet size (probably 100)
# {'Vampire': 110, 'Common': 112, 'Rare': 97, 'Uncommon': 91}
# eg. "Awe" listed as R in CSV, U in Duelist.
# Same with Bestial Visage, Bloodbath, Breath of the Dragon...
#
# Bloodlines is missing 2 uncos
# {'Common': 100, 'Rare': 100, 'Uncommon': 98}
#
# Black Hand has a crap total, with 8 commons too many, and missing frequency on C
# {'Common': 39, 'Uncommon': 108, 'Rare': 50}
#
# LoB numbers suggeset some "commons" were in fact printed on unco sheets
# {'Common': 125, 'Rare': 100, 'Uncommon': 75}
#
# Ebony Kingdom has Aye and Orun "half common" _on top_ of the printed sheets,
# which explains the strange totals, but does not explain how we should count:
# given Aye and Oruns were also included in the box (out of boosters),
# maybe list them as promo or something.
# See https://www.vekn.net/card-lists/142-ebony-kingdom
# {'Uncommon': 20, 'Common': 22, 'Rare': 20}
#
# Heirs to the Blood also showcases stupid totals
# {'Rare': 60, 'Uncommon': 60, 'Common': 56}
# Maybe check https://web.archive.org/web/20131029173730/http://www.secretlibrary.info/index.php?checklist=HttB
#
# Small code snippet for when we want to dig into this:
# from krcv.vtes import VTES
# VTES.load()
# total = {}
# for card in VTES.search(set=curset):
#     for rarity in card.sets[curset]:
#         if "rarity" not in rarity: continue
#         total.setdefault(rarity["rarity"], 0)
#         total[rarity["rarity"]] += rarity.get("frequency", 1)


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

    _UNLISTED = {
        "Promo": ["Promo", ""],
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
        for abbrev, (name, release_date) in self._UNLISTED.items():
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
