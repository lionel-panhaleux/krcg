"""Configuration"""

#: static KRCG server
KRCG_STATIC_SERVER = "https://static.krcg.org"
SUPPORTED_LANGUAGES = ["fr", "es"]
VEKN_TWDA_URL = "http://www.vekn.fr/decks/twd.htm"
#: aliases to match players abbreviations and typos in the TWDA
ALIASES = {
    # parsing will consider the legacy double dash "--" as a comment mark
    "bang nakh": "Bang Nakh — Tiger's Claws",
    # common HTML decoding failures
    "alia, god=92s messenger": "Alia, God's Messenger",
    "pentex=99 subversion": "Pentex™ Subversion",
    # traditions
    "the first tradition": "First Tradition: The Masquerade",
    "first tradition": "First Tradition: The Masquerade",
    "1st tradition": "First Tradition: The Masquerade",
    "the second tradition": "Second Tradition: Domain",
    "second tradition": "Second Tradition: Domain",
    "2nd trad": "Second Tradition: Domain",
    "2nd tradition": "Second Tradition: Domain",
    "2nd tradition: domain": "Second Tradition: Domain",
    "the third tradition": "Third Tradition: Progeny",
    "third tradition": "Third Tradition: Progeny",
    "3rd tradition": "Third Tradition: Progeny",
    "the fourth tradition": "Fourth Tradition: The Accounting",
    "fourth tradition": "Fourth Tradition: The Accounting",
    "4th tradition": "Fourth Tradition: The Accounting",
    "4th tradition: accounting": "Fourth Tradition: The Accounting",
    "the fifth tradition": "Fifth Tradition: Hospitality",
    "fifth tradition": "Fifth Tradition: Hospitality",
    "5th tradition": "Fifth Tradition: Hospitality",
    "the sixth tradition": "Sixth Tradition: Destruction",
    "sixth tradition": "Sixth Tradition: Destruction",
    "6th tradition": "Sixth Tradition: Destruction",
    # hunting grounds
    "academic hg": "Academic Hunting Ground",
    "amusement park hg": "Amusement Park Hunting Ground",
    "asylum hg": "Asylum Hunting Ground",
    "base hg": "Base Hunting Ground",
    "campground hg": "Campground Hunting Ground",
    "corporate hg": "Corporate Hunting Ground",
    "fetish club hg": "Fetish Club Hunting Ground",
    "fetish hg": "Fetish Club Hunting Ground",
    "institution hg": "Institution Hunting Ground",
    "jungle hg": "Jungle Hunting Ground",
    "library hg": "Library Hunting Ground",
    "morgue hg": "Morgue Hunting Ground",
    "palace hg": "Palace Hunting Ground",
    "park hg": "Park Hunting Ground",
    "poacher's hg": "Poacher's Hunting Ground",
    "political hg": "Political Hunting Ground",
    "port hg": "Port Hunting Ground",
    "shanty Town hg": "Shanty Town Hunting Ground",
    "slum hg": "Slum Hunting Ground",
    "society hg": "Society Hunting Ground",
    "temple hg": "Temple Hunting Ground",
    "underworld hg": "Underworld Hunting Ground",
    "university hg": "University Hunting Ground",
    "uptown hg": "Uptown Hunting Ground",
    "warzone hg": "Warzone Hunting Ground",
    "zoo hg": "Zoo Hunting Ground",
    "academic h.g.": "Academic Hunting Ground",
    "amusement park h.g.": "Amusement Park Hunting Ground",
    "asylum h.g.": "Asylum Hunting Ground",
    "base h.g.": "Base Hunting Ground",
    "campground h.g.": "Campground Hunting Ground",
    "corporate h.g.": "Corporate Hunting Ground",
    "fetish club h.g.": "Fetish Club Hunting Ground",
    "institution h.g.": "Institution Hunting Ground",
    "jungle h.g.": "Jungle Hunting Ground",
    "library h.g.": "Library Hunting Ground",
    "morgue h.g.": "Morgue Hunting Ground",
    "palace h.g.": "Palace Hunting Ground",
    "park h.g.": "Park Hunting Ground",
    "poacher's h.g.": "Poacher's Hunting Ground",
    "political h.g.": "Political Hunting Ground",
    "port h.g.": "Port Hunting Ground",
    "shanty Town h.g.": "Shanty Town Hunting Ground",
    "slum h.g.": "Slum Hunting Ground",
    "society h.g.": "Society Hunting Ground",
    "temple h.g.": "Temple Hunting Ground",
    "underworld h.g.": "Underworld Hunting Ground",
    "university h.g.": "University Hunting Ground",
    "uptown h.g.": "Uptown Hunting Ground",
    "warzone h.g.": "Warzone Hunting Ground",
    "zoo h.g.": "Zoo Hunting Ground",
    "acad. hg": "Academic Hunting Ground",
    "univ. hg": "University Hunting Ground",
    "univ hg": "University Hunting Ground",
    # powerbases
    "pb: barranquilla": "Powerbase: Barranquilla",
    "pb: berlin": "Powerbase: Berlin",
    "pb: cape verde": "Powerbase: Cape Verde",
    "pb: chicago": "Powerbase: Chicago",
    "pb: los angeles": "Powerbase: Los Angeles",
    "pb: luanda": "Powerbase: Luanda",
    "pb: madrid": "Powerbase: Madrid",
    "pb:madrid": "Powerbase: Madrid",
    "pb: mexico city": "Powerbase: Mexico City",
    "pb: montreal": "Powerbase: Montreal",
    "pb:montreal": "Powerbase: Montreal",
    "pb: new york": "Powerbase: New York",
    "pb: rome": "Powerbase: Rome",
    "pb: savannah": "Powerbase: Savannah",
    "pb: tshwane": "Powerbase: Tshwane",
    "pb: washington, d.c.": "Powerbase: Washington, D.C.",
    "pb: zurich": "Powerbase: Zürich",
    "pb barranquilla": "Powerbase: Barranquilla",
    "pb berlin": "Powerbase: Berlin",
    "pb cape verde": "Powerbase: Cape Verde",
    "pb chicago": "Powerbase: Chicago",
    "pb los angeles": "Powerbase: Los Angeles",
    "pb luanda": "Powerbase: Luanda",
    "pb madrid": "Powerbase: Madrid",
    "pb mexico city": "Powerbase: Mexico City",
    "pb montreal": "Powerbase: Montreal",
    "pb new york": "Powerbase: New York",
    "pb rome": "Powerbase: Rome",
    "pb savannah": "Powerbase: Savannah",
    "pb tshwane": "Powerbase: Tshwane",
    "pb washington, d.c.": "Powerbase: Washington, D.C.",
    "pb zurich": "Powerbase: Zürich",
    "powerbase zurich": "Powerbase: Zürich",
    # punctuation
    "behind you": "Behind You!",
    "psyche": "Psyche!",
    # too short to be registered as alternate name automatically
    "call": "Call, The",
    "coven": "Coven, The",
    "rack": "Rack, The",
    "talaq": "Talaq, The Immortal",
    # known abbreviations
    "antediluvian a.": "Antediluvian Awakening",
    "anthelios, the": "Anthelios, The Red Star",
    "archon inv.": "Archon Investigation",
    "carlton": "Carlton Van Wyk",
    "carver's meat packing": "Carver's Meat Packing and Storage",
    "con ag": "Conservative Agitation",
    "direct": "Direct Intervention",
    "delaying": "Delaying Tactics",
    "dreams": "Dreams of the Sphinx",
    "dreams of the s.": "Dreams of the Sphinx",
    "effective": "Effective Management",
    "elysium": "Elysium: The Arboretum",
    "elysium: versailles": "Elysium: The Palace of Versailles",
    "entice": "Enticement",
    "felix fix": 'Felix "Fix" Hessian (Wraith)',
    "forced": "Forced Awakening",
    "forced aw": "Forced Awakening",
    "foreshadowing": "Foreshadowing Destruction",
    "golconda": "Golconda: Inner Peace",
    "govern": "Govern the Unaligned",
    "gtu": "Govern the Unaligned",
    "heidelberg": "Heidelberg Castle, Germany",
    "heidelburg": "Heidelberg Castle, Germany",
    "info highway": "Information Highway",
    "infohighway": "Information Highway",
    "info hwy": "Information Highway",
    "js simmons": "J. S. Simmons, Esq.",
    "js simmons esq": "J. S. Simmons, Esq.",
    "krc": "Kine Resources Contested",
    "krcg": "KRCG News Radio",
    "krcg news": "KRCG News Radio",
    "laptop": "Laptop Computer",
    "laptops": "Laptop Computer",
    "laptop comp": "Laptop Computer",
    "laptop comp.": "Laptop Computer",
    "legal manip": "Legal Manipulations",
    "london eve star": "London Evening Star, Tabloid Newspaper",
    "london evening star, tabloid": "London Evening Star, Tabloid Newspaper",
    "malk. dementia": "Malkavian Dementia",
    "masquer": "Masquer (Wraith)",
    "mister winthrop": "Mr. Winthrop",
    "molotov": "Molotov Cocktail",
    "ohoyo hopoksia": "Ohoyo Hopoksia (Bastet)",
    "owl": "Owl Companion",
    "patagia: flaps": "Patagia: Flaps Allowing Limited Flight",
    "pentex": "Pentex(TM) Subversion",
    "pto": "Protect Thine Own",
    "pulse": "Pulse of the Canaille",
    "storage": "Storage Annex",
    "sudden": "Sudden Reversal",
    "telepathic misdir.": "Telepathic Misdirection",
    "true love's kiss": "True Love's Face",
    "temptation of g.p.": "Temptation of Greater Power",
    "ventrue hq": "Ventrue Headquarters",
    "voter cap": "Voter Captivation",
    "wake with ef": "Wake with Evening's Freshness",
    "wake with e.f": "Wake with Evening's Freshness",
    "wake wef": "Wake with Evening's Freshness",
    "wwef": "Wake with Evening's Freshness",
    "wake...": "Wake with Evening's Freshness",
    "wake w/eve. freshness": "Wake with Evening's Freshness",
    "wake w/evening...": "Wake with Evening's Freshness",
    "wake": "Wake with Evening's Freshness",
    "wakes": "Wake with Evening's Freshness",
    "wakeys": "Wake with Evening's Freshness",
    "waste man op": "Waste Management Operation",
    "wmrh": "WMRH Talk Radio",
    "wwstick": "Weighted Walking Stick",
    # misspellings not fixed by difflib
    "2th tradition": "Second Tradition: Domain",
    "ancient influnse": "Ancient Influence",
    "blodd doll": "Blood Doll",
    "carver's meat packing plant": "Carver's Meat Packing and Storage",
    "deflekion": "deflection",
    "denys": "Deny",
    "divine intervention": "Direct Intervention",
    "dogde": "Dodge",
    "dominat skill": "Dominate",
    "dominate: skillcard": "Dominate",
    "eagle sight": "Eagle's Sight",
    "sprit touch": "Spirit's Touch",
    "guard dog": "Guard Dogs",
    "golgonda": "Golconda: Inner Peace",
    "info superhighway": "Information Highway",
    "j.s. simons": "J. S. Simmons, Esq.",
    "judgement": "Judgment: Camarilla Segregation",
    "krcg newspaper": "KRCG News Radio",
    "krcg radio station": "KRCG News Radio",
    "lost in the crowd": "Lost in Crowds",
    "lost n the crowds": "Lost in Crowds",
    "milicent smith: vampire hunter": "Millicent Smith, Puritan Vampire Hunter",
    "obfuscate skill": "Obfuscate",
    "ps: istanbul": "Praxis Seizure: Istanbul",
    "rejuvenation": "Rejuvenate",
    "rumour mill tabloid": "The Rumor Mill, Tabloid Newspaper",
    "rumor mill, the": "The Rumor Mill, Tabloid Newspaper",
    "soul gems": "Soul Gem of Etrius",
    "tomb of rameses the cheesemonger": "Tomb of Rameses III",
    "truth of a 1000 lies": "Truth of a Thousand Lies",
    "veil of legions": "Veil the Legions",
    # 🥚
    "enkil cock": "enkil cog",
    "parity shit": "Parity Shift",
    "heart of cheating": "Heart of Nizchetus",
}
#: type order for deck display
TYPE_ORDER = [
    "Master",
    "Conviction",
    "Action",
    "Action/Combat",
    "Action/Reaction",
    "Ally",
    "Equipment",
    "Political Action",
    "Retainer",
    "Power",
    "Action Modifier",
    "Action Modifier/Combat",
    "Action Modifier/Reaction",
    "Reaction",
    "Combat",
    "Combat/Reaction",
    "Event",
]
#: some decks in the TWDA do not respect the rules when it comes to deck size
TWDA_CHECK_DECK_FAILS = {
    "2k9avangarda",  # 59 cards listed
    "2k8glqmich",  # 91 cards listed
    "2k8sanfranqual",  # 59 cards listed
    "2k8pwbsla2",  # 91 cards listed
    "2k6faceaface",  # 91 cards listed
    "2k4virolaxboston",  # 91 cards listed
    "2k4edith",  # 91 cards listed
    "2k4pariscup",  # 11 crypt cards listed
    "2k3nycanarch",  # 91 cards listed
    "ckgc2k",  # 91 cards listed
    "saveface2k1",  # 91 cards listed
    "genconuk2k1-treasure",  # 91 cards listed
    "jd32000",  # 91 cards listed
    "dog",  # 100 cards listed
    "matt-alamut",  # 91 cards listed
    "stevewampler",  # 59 cards listed
}
