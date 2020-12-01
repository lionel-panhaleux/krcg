"""Configuration"""
import os.path
import tempfile

#: images server
IMAGES_ROOT = "https://images.krcg.org/"
#: what to download
VEKN_TWDA_URL = "http://www.vekn.fr/decks/twd.htm"
VEKN_VTES_URL = "http://www.vekn.net/images/stories/downloads/vtescsv_utf8.zip"
VEKN_VTES_LIBRARY_FILENAME = "vteslib.csv"
VEKN_VTES_CRYPT_FILENAME = "vtescrypt.csv"
VEKN_VTES_ENCODING = "utf-8"
#: where to store our data
TEMP_DIR = tempfile.gettempdir()
TWDA_FILE = os.path.join(TEMP_DIR, "krcg-twda.pkl")
VTES_FILE = os.path.join(TEMP_DIR, "krcg-vtes.pkl")
#: classic headers in deck lists
HEADERS = [
    "actin",
    "action",
    "acton",
    "allies",
    "ally",
    "average",
    "burn option",
    "capacity",
    "card",
    "combat",
    "comment",
    "conviction",
    "convinction",
    "crypt",
    "deck",
    "description",
    "disciplineless",
    "combo",
    "double",
    "equip",
    "equipament",
    "equipment",
    "equiptment",
    "equpment",
    "event",
    "librairie",
    "library",
    "master",
    "minion",
    "misc",
    "miscellaneous",
    "mixed",
    "mod",
    "modifier",
    "multitype",
    "non-skilled",
    "other",
    "politcal",
    "politic",
    "political",
    "power",
    "reaction",
    "rection",
    "retainer",
    "skill-less",
    "total",
    "trifle",
    "vote",
    "and",
]
#: official cards renaming
AKA = {
    # print change not registered in cards "Aka" field
    "mask of 1,000 faces": "Mask of a Thousand Faces",
}
#: widespread nicknames for clans
CLANS_AKA = {
    "!brujah": "Brujah antitribu",
    "!gangrel": "Gangrel antitribu",
    "!malkavian": "Malkavian antitribu",
    "!malk": "Malkavian antitribu",
    "!nosferatu": "Nosferatu antitribu",
    "!nosfe": "Nosferatu antitribu",
    "!salubri": "Salubri antitribu",
    "!salu": "Salubri antitribu",
    "!toreador": "Toreador antitribu",
    "!tore": "Toreador antitribu",
    "!tremere": "Tremere antitribu",
    "!trem": "Tremere antitribu",
    "!ventrue": "Ventrue antitribu",
    "brujah anti": "Brujah antitribu",
    "gangrel anti": "Gangrel antitribu",
    "malkavian anti": "Malkavian antitribu",
    "malk anti": "Malkavian antitribu",
    "nosferatu anti": "Nosferatu antitribu",
    "nosfe anti": "Nosferatu antitribu",
    "salubri anti": "Salubri antitribu",
    "salu anti": "Salubri antitribu",
    "toreador anti": "Toreador antitribu",
    "tore anti": "Toreador antitribu",
    "tremere anti": "Tremere antitribu",
    "trem anti": "Tremere antitribu",
    "ventrue anti": "Ventrue antitribu",
    "brother": "Blood Brother",
    "brothers": "Blood Brother",
    "giov": "Giovanni",
    "malk": "Malkavian",
    "naga": "Nagaraja",
    "nosfe": "Nosferatu",
    "salu": "Salubri",
    "tore": "Toreador",
    "trem": "Tremere",
    "cacophony": "Daughter of Cacophony",
    "daughter": "Daughter of Cacophony",
    "daughters": "Daughter of Cacophony",
    "set": "Follower of Set",
    "setite": "Follower of Set",
    "follower": "Follower of Set",
    "followers": "Follower of Set",
    "skulls": "Harbinger of Skulls",
    "harbinger": "Harbinger of Skulls",
    "harbingers": "Harbinger of Skulls",
    "trujah": "True Brujah",
}
#: disciplines nicknames/trigrams
DISC_AKA = {
    "abo": "Abombwe",
    "ani": "Animalism",
    "aus": "Auspex",
    "cel": "Celerity",
    "chi": "Chimerstry",
    "dai": "Daimoinon",
    "dem": "Dementation",
    "dom": "Dominate",
    "for": "Fortitude",
    "mal": "Maleficia",
    "mel": "Melpominee",
    "myt": "Mytherceria",
    "nec": "Necromancy",
    "obe": "Obeah",
    "obf": "Obfuscate",
    "obt": "Obtenebration",
    "pot": "Potence",
    "pre": "Presence",
    "pro": "Protean",
    "qui": "Quietus",
    "san": "Sanguinus",
    "ser": "Serpentis",
    "spi": "Spiritus",
    "str": "Striga",
    "tem": "Temporis",
    "tha": "Thaumaturgy",
    "than": "Thanatosis",
    "thau": "Thaumaturgy",
    "thn": "Thanatosis",
    "val": "Valeren",
    "vic": "Vicissitude",
    "vis": "Visceratika",
}
#: registered traits
TRAITS = [
    "primogen",
    "prince",
    "justicar",
    "inner circle",
    "imperator",
    "bishop",
    "archbishop",
    "cardinal",
    "regent",
    "priscus",
    "baron",
    "anarch",
    "laibon",
    "liaison",
    "magaji",
    "kholo",
    "black hand",
    "seraph",
    "red list",
    "infernal",
    "slave",
    "scarce",
    "sterile",
]
#: official disciplines trigrams used in crypt CSV
DIS_MAP = {
    "-none-": "none",
    "abo": "abombwe",
    "ani": "animalism",
    "aus": "auspex",
    "cel": "celerity",
    "chi": "chimerstry",
    "dai": "daimoinon",
    "def": "defense",
    "dem": "dementation",
    "dom": "dominate",
    "for": "fortitude",
    "inn": "innocence",
    "jud": "judgment",
    "mar": "martyrdom",
    "mel": "melpominee",
    "myt": "mytherceria",
    "nec": "necromancy",
    "obe": "obeah",
    "obf": "obfuscate",
    "obt": "obtenebration",
    "pot": "potence",
    "pre": "presence",
    "pro": "protean",
    "qui": "quietus",
    "red": "redemption",
    "san": "sanguinus",
    "ser": "serpentis",
    "spi": "spiritus",
    "tem": "temporis",
    "tha": "thaumaturgy",
    "thn": "thanatosis",
    "val": "valeren",
    "ven": "vengeance",
    "vic": "vicissitude",
    "vin": "vision",  # VIS is used in CSV
    "vis": "visceratika",
    "ABO": "ABOMBWE",
    "ANI": "ANIMALISM",
    "AUS": "AUSPEX",
    "CEL": "CELERITY",
    "CHI": "CHIMERSTRY",
    "DAI": "DAIMOINON",
    "DEM": "DEMENTATION",
    "DOM": "DOMINATE",
    "FOR": "FORTITUDE",
    "MEL": "MELPOMINEE",
    "MYT": "MYTHERCERIA",
    "NEC": "NECROMANCY",
    "OBE": "OBEAH",
    "OBF": "OBFUSCATE",
    "OBT": "OBTENEBRATION",
    "POT": "POTENCE",
    "PRE": "PRESENCE",
    "PRO": "PROTEAN",
    "QUI": "QUIETUS",
    "SAN": "SANGUINUS",
    "SER": "SERPENTIS",
    "SPI": "SPIRITUS",
    "TEM": "TEMPORIS",
    "THA": "THAUMATURGY",
    "THN": "THANATOSIS",
    "VAL": "VALEREN",
    "VIC": "VICISSITUDE",
    "VIS": "VISCERATIKA",
}
#: custom remap to match players abbreviations and typos
REMAP = {
    # our card parsing removes the dash
    "bang nakh": "Bang Nakh — Tiger's Claws",
    "khazar's diary": "Khazar's Diary (Endless Night)",
    "ohoyo hopoksia": "Ohoyo Hopoksia (Bastet)",
    # we not decode HTML properly as most of it is text
    "alia, god=92s messenger": "Alia, God's Messenger",
    "pentex=99 subversion": "Pentex™ Subversion",
    # traditions - players really do whatever they want
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
    # known abbreviations
    "antediluvian a.": "Antediluvian Awakening",
    "anthelios, the": "Anthelios, The Red Star",
    "archon inv.": "Archon Investigation",
    "call": "Call, The",
    "carlton": "Carlton Van Wyk",
    "con ag": "Conservative Agitation",
    "coven": "Coven, The",
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
    "owl": "Owl Companion",
    "patagia: flaps": "Patagia: Flaps Allowing Limited Flight",
    "pentex": "Pentex(TM) Subversion",
    "pto": "Protect Thine Own",
    "pulse": "Pulse of the Canaille",
    "rack": "Rack, The",
    "storage": "Storage Annex",
    "sudden": "Sudden Reversal",
    "talaq": "Talaq, The Immortal",
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
    "carver's meat packing": "Carver's Meat Packing and Storage",
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
    "heart of the shitty": "Heart of the City",
    "heart of cheating": "Heart of Nizchetus",
    "hero fellation": "Aire of Elation",
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
#: traits are hard to parse: manual fixups
SEARCH_EXCEPTIONS = {
    "The Baron": ["-trait:anarch"],
    "Gwen Brand": [
        "+discipline:ANIMALISM",
        "+discipline:AUSPEX",
        "+discipline:CHIMERSTRY",
        "+discipline:FORTITUDE",
    ],
}
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
    "saveface2k1",  # 91 cards listed
    "genconuk2k1-treasure",  # 91 cards listed
    "jd32000",  # 91 cards listed
    "dog",  # 100 cards listed
    "matt-alamut",  # 91 cards listed
    "stevewampler",  # 59 cards listed
}
# Legacy, kept here just in case
# fixes done to problematic decklists in the TWDA.
# KRCG was used to regenerate full proper decklists in the twda_fix folder
# TWDA_FIXUP = {
#     # ill-formatted comments
#     "2010hunrb": {"cards_comments": {"Deep Song": "just the right number"}},
#     "2010pwblaQ": {
#         "cards_comments": {
#             "The Art of Memory": (
#                 "Linchpin card for dialing in the moment-appropriate card."
#             ),
#             "Touch of Clarity": ("Recent addition, unneeded in this tournament."),
#         }
#     },
#     "2010pwbla1": {
#         "cards_comments": {
#             "Ancient Influence": (
#                 'eradicate your prey and call as a "spare" Tupdog action'
#             ),
#             "Reins of Power": (
#                 'eradicate your predator and call as a "spare" Tupdog action'
#             ),
#         }
#     },
#     "2k9mojlp": {
#         "cards": {  # 4 cards listed twice
#             "Conditioning": 6,
#             "Leverage": 3,
#             "Seduction": 4,
#             "The Sleeping Mind": 5,
#         }
#     },
#     "2k8sequeenslandcq": {
#         "cards": {
#             "Praxis Seizure: Geneva": 4,  # all praxis cards on a single line
#             "Praxis Seizure: Berlin": 4,
#             "Praxis Seizure: Cairo": 2,
#             "Elder Impersonation": 3,  # wrong comment mark
#         },
#         "cards_comments": {
#             "Elder Impersonation": "would exchange for Faceless Night x4"
#         },
#     },
#     "2k8torunminiq": {
#         "cards": {
#             "Direct Intervention": 2,
#             "Powerbase: Tshwane": 1,
#             "WMRH Talk Radio": 1,
#             "No Secrets From the Magaji": 3,
#             "Predator's Transformation": 5,
#             "Ancilla Empowerment": 1,
#             "Superior Mettle": 2,
#             "Predator's Communion": 4,
#         },
#         "cards_comments": {
#             "Direct Intervention": (
#                 "I'm thinking about adding another one, this "
#                 "card is cruicial for any block denial actions, or things that "
#                 "simply screw your spiders"
#             ),
#             "Powerbase: Tshwane": (
#                 "there was some magic around this card, I got it "
#                 "in every single game, in the first 10 cards drawn"
#             ),
#             "WMRH Talk Radio": (
#                 "didn't use it at all, metagame wasn't stealth heavy though"
#             ),
#             "No Secrets From the Magaji": (
#                 "was thinking about 4-5, but 3 is a good "
#                 "number, you draw too much attention if you put it on too early"
#             ),
#             "Predator's Transformation": (
#                 "wonderful card, can play it anytime, and "
#                 "the bonus superior effect did help a lot many times"
#             ),
#             "Ancilla Empowerment": (
#                 "nobody really expects these 2 until its too late"
#             ),
#             "Superior Mettle": (
#                 "I'd revise the prevent cards anyway, maybe adding "
#                 "some with no cost, or more of SM. it worked nice in overall though"
#             ),
#             "Predator's Communion": (
#                 "very helpful before you get no secrets, easy " "to drop afterwards"
#             ),
#         },
#     },
#     "2k7campeonatojuizforano": {
#         "cards_comments": {
#             "Direct Intervention": (
#                 "saved me a lot of times, unfortunately I couldn't pack more than "
#                 "one."
#             ),
#             "The Slaughterhouse": (
#                 "useful either to speed deck depletion or to trade for something "
#                 "useful under Anthelios."
#             ),
#             "Wash": (
#                 "not as effective as I expected, but also not a hassle because it's "
#                 "trifle."
#             ),
#         }
#     },
#     "2k7comjust": {
#         "cards_comments": {
#             "Abbot": (
#                 "I like these. Got smiled at until people realized I actually packed "
#                 "combat."
#             ),
#             "Gramle": (
#                 "This should help contesting Aranthebes, fetch another AI, or DI for "
#                 "a delayed vote. Never used though."
#             ),
#             "Botched Move": (
#                 "Pushes the maximum damage in a round to 7. Cute, but nearly "
#                 "useless. :)"
#             ),
#         }
#     },
#     "2k7woaboston": {
#         "cards": {
#             "Perfectionist": 2,
#             "Moise Kasavubu": 1,
#             "Vagabond Mystic": 1,
#             "The Crusader Sword": 1,
#             "Determine": 2,
#         },
#         "cards_comments": {
#             "Perfectionist": (
#                 "weren't too useful - the Vamps didn't act too often.  Maybe -1, +1 "
#                 "Blood Doll"
#             ),
#             "Moise Kasavubu": (
#                 "seems good, but never got him out to confirm - in past uses, he's "
#                 "just gotten blocked, but with the stealth I put him back in"
#             ),
#             "Vagabond Mystic": (
#                 "undecided; life was rarely an issue, except when a little healing "
#                 "wouldn't have mattered"
#             ),
#             "The Crusader Sword": (
#                 "in retrospect, IR Goggles to go with this might be nice"
#             ),
#             "Determine": (
#                 "never used; took too much vsn out of the crypt, and rarely needed"
#             ),
#         },
#     },
#     "2k4volkerpit": {
#         "comments": (
#             "Description: Lasombra S&B for the tournament in Pittsburgh, 3/27/04\n\n"
#             "Anyway, here's the decklist. There's not much new tech in here but for "
#             "some\n"
#             "concerted effort to keep blood on my vampires. I've found that the "
#             "Hungry\n"
#            "Coyote is close to miraculous for keeping alive if you feel you have to\n"
#            "turtle up for a little while,and it's usually a turn well spent hunting\n"
#             "with the HC around to recoup some blood spent on Dominate bleeds.\n\n"
#             "Possible improvements:\n\n"
#             "Drop one Kassiym from an extra copy of Banjoko, add an extra Path\n"
#             "and reduce the number of Stone Travels for some extra combat defence.\n"
#             "Maybe drop the prayer cards (Dramatic Upheaval, Graverobbing) and try\n"
#             "to find some more Shroud of Absence... As it is, though, the deck\n"
#             "performs well and cycles beautifully. True combat as a predator will\n"
#           "likely crunch it, but true combat has to go upstream heavily or it won't\n"
#             "survive, so you may be able to just sit it out for a while until\n"
#             "the coast is clear.\n"
#         )
#     },
#     "2k3ec": {
#         "cards": {"Smiling Jack, The Anarch": 3, "Auspex": 2},
#         "cards_comments": {
#             "Smiling Jack, The Anarch": "to many!",
#             "Auspex": "don't need them, maybe one!",
#         },
#     },
#     "2k7palmaqual": {"cards": {"Animalism": 1}},
#     "2k6aussiechamp": {"cards": {"Dominate": 1}},
#     "2k6sonarba": {"cards": {"Dominate": 4}},
#     "2k6praxispoitiers": {"cards": {"Dominate Kine": 2}},
#     "2k6faceaface": {"cards": {"The Coven": 1}},
#     "2k6nerq-templecon": {"cards": {"Dominate": 3}},
#     "2k5leicesteraug": {"cards": {"Presence": 2}},
#     "2k5valhallajuly": {"cards": {"Wake with Evening's Freshness": 5}},
#     "2k5ropecon": {"cards": {"Dominate": 1}},
#     "2k5blackutrecht": {"cards": {"Fear of Mekhet": 1, "Fortune Teller Shop": 1}},
#     "2k5dreamboston": {"cards": {"Dominate": 1}},
#     "2k4norms": {"cards": {"Auspex": 1, "Obfuscate": 1}},
#     "2k4littlesister": {"cards": {"Celerity": 2}},
#     "2k4gks": {"cards": {"Dominate": 1}},
#     "2k3italyqualifier": {
#         "cards": {
#             "Jake Washington": 3,
#             "The Hungry Coyote": 1,
#             "The Embrace": 3,
#             "Entrancement": 3,
#             "The Summoning": 5,
#             "Change of Target": 6,
#             "Marijava Ghoul": 2,
#         },
#         "cards_comments": {
#             "Jake Washington": (
#                 "He is perfect for both the WG and let my midcaps eat if hungry"
#             ),
#             "The Hungry Coyote": (
#                 "after the tournament I have decided that the Jakes are enough for "
#               "this and that my minions have always better actions to do rather than "
#                 'hunt. I would change it for a Pentex "anti helena/Lucas halton/..." '
#                 "Subversion"
#             ),
#             "The Embrace": (
#                 "extremely useful for bleed and multiple action as rescuing from "
#                 "torpor/eating alive/rush walls"
#             ),
#             "Entrancement": (
#                 "To defend my omelettes, for bleeding or for an extrarecruitment if "
#                 "ever able, this card is so great"
#             ),
#             "The Summoning": (
#                 "key, essential, If you summon a WG and the action is blocked you "
#                 "don't lose the Meat machine so you could try it later, and it also "
#                 "multiplies the number of getting a WG from my library"
#             ),
#             "Change of Target": (
#               "for the embraces aswell and the Ghouls if an evil killer vamps untaps "
#                 "suddenly while attacking"
#             ),
#             "Marijava Ghoul": (
#                "exceptionals, There are 15 pressence action cards and this makes 'em "
#                 "more efficient, but he is also meat for the WG god"
#             ),
#         },
#     },
#     "2k3frenchecq": {"cards": {"Obfuscate": 1}},
#     "2k3helsinki5": {"cards": {"Wake with Evening's Freshness": 5}},
#     "2k3sdgothenburg": {"cards": {"Obfuscate": 3}},
#     "2k3cadaverous": {"cards": {"Falcon's Eye": 4}},
#     "2k3winnipegapril": {
#         "cards": {"Bum's Rush": 4},
#         "cards_comments": {
#             "Bum's Rush": "Need some Harass in here for 2nd round fun",
#             "Conditioning": (
#                 "used only at lesser to avoid archons. Only 1 vamp had superior dom."
#             ),
#         },
#     },
#     "2k3rome": {"cards": {"Presence": 7}},
#     "2k3psmilwaukee": {
#         "comments": (
#             "MOTTO: Coming soon to a school board near you.\n\n"
#             "Notes:\n\n"
#             "DO NOT SCARE THE TABLE... if at all convenient.\n\n"
#             "Get out Arika... burn people for fun and profit.\n"
#             "Profit is Minion Tap/Voter Cap. Use the Governs\n"
#             "to bring out friends for Arika. Relies on Zillah's\n"
#             "to outrun Combat Decks to a vampire, who can then be\n"
#             "burned with PTO, and fails utterly to weenie combat,\n"
#             "fast big combat, Camarilla combat, and any of the same\n"
#             "if it's bleed.\n\n"
#             "This deck came into being preNERFing of 5th Tradition.\n"
#             "I put it together to see if I could still get big\n"
#             "vamp bloat to work. I managed to guess the local\n"
#             "metagame to a T on the sect issues required to play\n"
#             "the deck. Only one deck I saw was all Camarilla.\n\n"
#             "Changes: Some GtU to Mind Rape, 3 Lucinde 2 Vitel\n"
#             "lots more combat D/bleed D depending on metagame.\n"
#             "I've added all the Awe's I own, more may be good.\n\n"
#             "Cameron Domer\n"
#             "orcaorcinus@hotmail.com\n"
#         )
#     },
#     "2k3gothenburgblizzard": {"cards": {"Celerity": 3}},
#     "2k2eclastq": {"cards": {"Jake Washington": 5}},
#     "2k2sydney": {
#         "cards": {"Majesty": 2},
#         "cards_comments": {
#           "Majesty": "after CE probably swap out for dodge, ecstasy, change of target"
#         },
#     },
#     # guessing "Manouever" was "Fake Out"
#     "2k2ukqualifier": {"cards": {"Fake Out": 4}},
#     "2k2watfordmay": {
#         "author": (
#             "Tony 'literary Thug' Smith, with a bit of creative inspiration from "
#             "Jon Cooper."
#         ),
#         "comments": (
#             "Didn't have too many problems on the day and the combination of bone\n"
#             "crunching combat and 2nd tradition seemed to handle most things. A\n"
#             "little slow getting the first point in the final, which nearly\n"
#             "scuppered my plans.\n\n"
#             "The first version of this had 4 Don Cruez. I later decided that using\n"
#             "a smaller crypt and another Protean master was probably the way to go.\n"
#             "I may even drop the Dons to 2 and add a second Beast. I usually went\n"
#             "for either Theo or Volker first, on the basis that the Don was just\n"
#             "too big. Although, to be fair, his maneuver did save me a couple of\n"
#             "times against the Wookie's assamites.\n\n"
#             "Not much in the way of subtlety, but hey, burning vampires is fun.\n\n"
#             "Remember kids, don't do drugs.\n\n"
#             "Tony\n\n"
#             "Literary Thug\n"
#         ),
#     },
#     # replaced 6x "Praxis Seizure..." with Jyhad non-clan generic Praxis
#     "2k2pariseq": {
#         "cards": {
#             "Presence": 3,
#             "Praxis Seizure: Atlanta": 1,
#             "Praxis Seizure: Boston": 1,
#             "Praxis Seizure: Chicago": 1,
#             "Praxis Seizure: Cleveland": 1,
#             "Praxis Seizure: Dallas": 1,
#             "Praxis Seizure: Houston": 1,
#         }
#     },
#     "2k2gothenburgapr": {"cards": {"Presence": 10}},
#     "2k2during": {"cards": {"Fortitude": 5}},
#     "2k2newyork": {
#         "cards": {
#             "Catatonic Fear": 14,
#             "Marijava Ghoul": 1,
#         },
#         "cards_comments": {
#             "Catatonic Fear": "and i needed them all+majesty",
#             "Marijava Ghoul": "needed to break free-+1 stealth :)",
#         },
#     },
#     "2k2orccon2": {"cards": {"Presence": 1}},
#     # because of AK-47 we can't parse dash (-) post counts with no space
#     "2k2torrancejan": {
#         "cards": {
#             "Antediluvian Awakening": 1,
#             "Information Highway": 2,
#             "The Parthenon": 2,
#             "Minion Tap": 2,
#             "Blood Doll": 4,
#             "Sudden Reversal": 8,
#             "Kindred Spirits": 18,
#             "Eyes of Chaos": 10,
#             "Confusion": 6,
#             "Swallowed by the Night": 8,
#             "Cloak the Gathering": 6,
#             "Elder Impersonation": 4,
#             "Spying Mission": 7,
#             "Faceless Night": 6,
#             "Lost in Crowds": 6,
#         }
#     },
#     "2k2gothenburg": {"cards": {"Dominate": 1, "Thaumaturgy": 1}},
#     "2k3tcithaca": {
#         # replace "praxis seizure (various)" with Jyhad non-clan-specific ones
#         "cards": {
#             "Praxis Seizure: Atlanta": 1,
#             "Praxis Seizure: Boston": 1,
#             "Praxis Seizure: Chicago": 1,
#             "Praxis Seizure: Cleveland": 1,
#         },
#     },
#     "gothenburg2k1": {"cards": {"Auspex": 4}},
#     "watford-ts": {
#         "cards": {
#             "Hostile Takeover": 2,
#             "Wake with Evening's Freshness": 5,
#             "Ivory Bow": 1,
#             "Seduction": 10,
#         },
#         "cards_comments": {
#             "Hostile Takeover": (
#                 "I know that there are only 2 ventru in the crypt but trust me, the "
#                 "hostiles have won games for me more than once"
#             ),
#             "Wake with Evening's Freshness": "changed from 4 at the last minute",
#             "Ivory Bow": "didn't see it all day, may need to come out",
#             "Seduction": (
#                 "the numbers of both of these has fluctuated between 8 and 12. "
#                 "for this tourney I went for the happy medium."
#             ),
#         },
#     },
#     # misplaced card name in tail comment got included in the deck
#     "darbyla2k1": {"cards": {"Social Charm": 15}},
#     "joshphiladelphia": {"cards": {"Protean": 1}},
#     "damnans": {"cards": {"Fortitude": 2}},
#     # card type prefix - too rare to bother parsing this
#     "ckgc2k": {
#         "comments": "",
#         "cards": {
#             "Govern the Unaligned": 6,
#             "Bum's Rush": 1,
#             "Bonding": 7,
#             "Conditioning": 6,
#             "Shadow Play": 8,
#             "Shroud of Night": 3,
#             "Arms of the Abyss": 3,
#             "Entombment": 3,
#             "Shadow Body": 5,
#             "Leather Jacket": 4,
#             "Archon Investigation": 1,
#             "Blood Doll": 4,
#             "Minion Tap": 2,
#             "Dominate": 3,
#             "Obtenebration": 2,
#             "Elysian Fields": 3,
#             "Elysium: The Arboretum": 2,
#             "Political Hunting Ground": 3,
#             "Slave Auction": 2,
#             "Sudden Reversal": 1,
#             "Deflection": 5,
#             "Eyes of the Night": 5,
#             "Redirection": 6,
#             "Wake with Evening's Freshness": 6,
#         },
#     },
#     # because of AK-47 we can't parse dash (-) post counts with no space
#     "swkc": {
#         "comments": "",
#         "cards": {
#             "Auspex": 2,
#             "Presence": 4,
#             "Blood Doll": 2,
#             "Ascendance": 2,
#             "Misdirection": 2,
#             "Sudden Reversal": 2,
#             "Short-Term Investment": 1,
#             "Minion Tap": 1,
#             "Major Boon": 1,
#             "Aching Beauty": 1,
#             "Society Hunting Ground": 1,
#             "Art Museum": 1,
#             "Forced Awakening": 2,
#             "Marijava Ghoul": 2,
#             "Palatial Estate": 1,
#             "Telepathic Counter": 9,
#             "Telepathic Misdirection": 11,
#             "Kindred Intelligence": 2,
#             "Spirit's Touch": 2,
#             "Precognition": 2,
#             "Eagle's Sight": 1,
#             "Enhanced Senses": 1,
#             "Pulse of the Canaille": 1,
#             "Majesty": 12,
#             "Enchant Kindred": 8,
#             "Legal Manipulations": 4,
#             "Entrancement": 1,
#             "Aire of Elation": 2,
#             "Propaganda": 1,
#             "Media Influence": 2,
#             "Staredown": 2,
#             "Catatonic Fear": 1,
#             "Social Charm": 3,
#         },
#     },
#     "quebec": {"cards": {"Fortitude": 1, "Presence": 1}},
#     "leedec99": {"cards": {"Obfuscate": 1}},
#     "portoct99": {"cards": {"Celerity": 1}},
#     "matt-alamut": {
#         "cards": {
#             "Obfuscate": 1,
#             "Presence": 1,
#             "Praxis Seizure: Istanbul": 1,
#             "Praxis Seizure: Paris": 1,
#             "Praxis Seizure: Monaco": 1,
#             "Praxis Seizure: Dublin": 1,
#         }
#     },
#     "Brian": {"cards": {"Dominate": 2, "Presence": 1}},
#     "rob": {"cards": {"Dominate": 1, "Fortitude": 1}},
# }
