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
        "Promo-20210709": ["2021 Kickstarter Promo", "2021-07-09"],
        "Promo-20210701": ["2021 Kickstarter Promo", "2021-07-01"],
        "Promo-20210331": ["2021 Mind’s Eye Theatre Promo", "2021-03-31"],
        "Promo-20210310": ["2021 Resellers Promo", "2021-03-31"],
        "Promo-20191123": ["2020 GP Promo", "2020-11-23"],
        "Promo-20201030": ["V5 Polish Edition promo", "2020-10-30"],
        "Promo-20201123": ["2020 GP Promo", "2020-11-23"],
        "Promo-20200511": ["2020 Promo Pack 2", "2020-05-11"],
        "Promo-20191027": ["2019 ACC Promo", "2019-10-27"],
        "Promo-20191005": ["2019 AC Promo", "2019-10-05"],
        "Promo-20190818": ["2019 EC Promo", "2019-08-18"],
        "Promo-20190816": ["2019 DriveThruCards Promo", "2019-08-16"],
        "Promo-20190614": ["2019 Promo", "2019-06-14"],
        "Promo-20190601": ["2019 SAC Promo", "2019-06-01"],
        "Promo-20190615": ["2019 NAC Promo", "2019-06-15"],
        "Promo-20190629": ["2019 Grand Prix Promo", "2019-06-15"],
        "Promo-20190408": ["2019 Promo Pack 1", "2019-04-08"],
        "Promo-20181004": ["2018 Humble Bundle", "2018-10-04"],
        "Promo-20150219": ["2015 Storyline Rewards", "2015-02-19"],
        "Promo-20150221": ["2015 Storyline Rewards", "2015-02-21"],
        "Promo-20150215": ["2015 Storyline Rewards", "2015-02-15"],
        "Promo-20150214": ["2015 Storyline Rewards", "2015-02-14"],
        "Promo-20150211": ["2015 Storyline Rewards", "2015-02-11"],
        "Promo-20150216": ["2015 Storyline Rewards", "2015-02-16"],
        "Promo-20150220": ["2015 Storyline Rewards", "2015-02-20"],
        "Promo-20150218": ["2015 Storyline Rewards", "2015-02-18"],
        "Promo-20150217": ["2015 Storyline Rewards", "2015-02-17"],
        "Promo-20150213": ["2015 Storyline Rewards", "2015-02-13"],
        "Promo-20150212": ["2015 Storyline Rewards", "2015-02-12"],
        "Promo-20100510": ["2010 Storyline promo", "2010-05-10"],
        "Promo-20090929": ["2009 Tournament / Storyline promo", "2009-09-29"],
        "Promo-20090401": ["2009 Tournament / Storyline promo", "2009-04-01"],
        "Promo-20081119": ["2008 Tournament promo", "2008-11-19"],
        "Promo-20081023": ["2008 Tournament promo", "2008-10-23"],
        "Promo-20080810": ["2008 Storyline promo", "2008-08-10"],
        "Promo-20080203": ["2008 Tournament promo", "2008-08-10"],
        "Promo-20070601": ["2007 Promo", "2007-06-01"],
        "Promo-20070101": ["Sword of Caine promo", "2007-01-01"],
        "Promo-20061126": ["2006 EC Tournament promo", "2006-11-26"],
        "Promo-20061101": ["2006 Storyline promo", "2006-11-01"],
        "Promo-20061026": ["2006 Tournament promo", "2006-10-26"],
        "Promo-20060902": ["2006 Tournament promo", "2006-09-02"],
        "Promo-20060710": ["Third Edition promo", "2006-07-10"],
        "Promo-20060417": ["2006 Championship promo", "2006-04-17"],
        "Promo-20060213": ["2006 Tournament promo", "2006-02-13"],
        "Promo-20060123": ["2006 Tournament promo", "2006-01-23"],
        "Promo-20051026": ["Legacies of Blood promo", "2005-10-26"],
        "Promo-20051001": ["2005 Storyline promo", "2005-10-01"],
        "Promo-20050914": ["Legacies of Blood promo", "2005-09-14"],
        "Promo-20050611": ["2005 Tournament promo", "2005-06-11"],
        "Promo-20050122": ["2005 Tournament promo", "2005-01-22"],
        "Promo-20050115": ["Kindred Most Wanted promo", "2005-01-15"],
        "Promo-20041015": ["Fall 2004 Storyline promo", "2004-10-15"],
        "Promo-20040411": ["Gehenna promo", "2004-04-11"],
        "Promo-20040409": ["2004 promo", "2004-04-09"],
        "Promo-20040301": ["Prophecies league promo", "2004-03-01"],
        "Promo-20031105": ["Black Hand promo", "2003-11-05"],
        "Promo-20030901": ["Summer 2003 Storyline promo", "2003-09-01"],
        "Promo-20030307": ["Anarchs promo", "2003-03-07"],
        "Promo-20021201": ["2003 Tournament promo", "2002-12-01"],
        "Promo-20021101": ["Fall 2002 Storyline promo", "2002-11-01"],
        "Promo-20020811": ["Sabbat War promo", "2002-08-11"],
        "Promo-20020704": ["Camarilla Edition promo", "2002-07-04"],
        "Promo-20020201": ["Winter 2002 Storyline promo", "2002-02-01"],
        "Promo-20011201": ["Bloodlines promo", "2001-12-01"],
        "Promo-20010428": ["Final Nights promo", "2001-04-28"],
        "Promo-20010302": ["Final Nights promo", "2001-03-02"],
        "Promo-19960101": ["1996 Promo", "1996-01-01"],
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
