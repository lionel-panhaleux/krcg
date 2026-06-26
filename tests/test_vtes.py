"""Test VTES cards list & search."""

import dataclasses
import importlib.metadata
import json
import os
import tempfile
import pytest

from krcg import models
from krcg import utils
from krcg import vtes


def test_fuzzy_match() -> None:
    """Test fuzzy match."""
    assert "enchant kidnred" in vtes.VTES
    assert vtes.VTES["enchant kidnred"].printed_name == "Enchant Kindred"


def test_i18n() -> None:
    """Test translations."""
    assert "Corneilles noires" in vtes.VTES
    assert vtes.VTES["Corneilles noires"].printed_name == "Carrion Crows"


def test_search_dimensions() -> None:
    """Test search dimensions."""
    assert vtes.VTES.search_dimensions == {
        "bonus": [
            None,
            "Bleed",
            "Capacity",
            "Hunt",
            "Intercept",
            "Stealth",
            "Strength",
            "Torpor",
            "Trifle",
            "Votes",
        ],
        "capacity": [None, "1", "10", "11", "2", "3", "4", "5", "6", "7", "8", "9"],
        "clan": [
            None,
            "Abomination",
            "Ahrimane",
            "Akunanse",
            "Avenger",
            "Baali",
            "Banu Haqim",
            "Blood Brother",
            "Brujah",
            "Brujah antitribu",
            "Caitiff",
            "Daughter of Cacophony",
            "Defender",
            "Gangrel",
            "Gangrel antitribu",
            "Gargoyle",
            "Giovanni",
            "Guruhi",
            "Harbinger of Skulls",
            "Hecata",
            "Innocent",
            "Ishtarri",
            "Judge",
            "Kiasyd",
            "Lasombra",
            "Malkavian",
            "Malkavian antitribu",
            "Martyr",
            "Ministry",
            "Nagaraja",
            "Nosferatu",
            "Nosferatu antitribu",
            "Osebo",
            "Pander",
            "Ravnos",
            "Redeemer",
            "Salubri",
            "Salubri antitribu",
            "Samedi",
            "Toreador",
            "Toreador antitribu",
            "Tremere",
            "Tremere antitribu",
            "True Brujah",
            "Tzimisce",
            "Ventrue",
            "Ventrue antitribu",
            "Visionary",
        ],
        "discipline": [
            None,
            "ABO",
            "ANI",
            "AUS",
            "CEL",
            "CHI",
            "DAI",
            "DEM",
            "DOM",
            "FOR",
            "MEL",
            "MYT",
            "NEC",
            "OBE",
            "OBF",
            "OBL",
            "OBT",
            "POT",
            "PRE",
            "PRO",
            "QUI",
            "SAN",
            "SER",
            "SPI",
            "TEM",
            "THA",
            "THN",
            "VAL",
            "VIC",
            "VIS",
            "abo",
            "ani",
            "aus",
            "cel",
            "chi",
            "dai",
            "def",
            "dem",
            "dom",
            "fli",
            "for",
            "inn",
            "jud",
            "mal",
            "mar",
            "mel",
            "myt",
            "nec",
            "obe",
            "obf",
            "obl",
            "obt",
            "pot",
            "pre",
            "pro",
            "qui",
            "red",
            "san",
            "ser",
            "spi",
            "str",
            "tem",
            "tha",
            "thn",
            "val",
            "ven",
            "vic",
            "vis",
            "viz",
        ],
        "group": [None, "Any", "G1", "G2", "G3", "G4", "G5", "G6", "G7"],
        "kind": ["Crypt", "Library"],
        "sect": [None, "Anarch", "Camarilla", "Independent", "Laibon", "Sabbat"],
        "title": [
            None,
            "1 Vote",
            "2 Votes",
            "Archbishop",
            "Baron",
            "Bishop",
            "Cardinal",
            "Imperator",
            "Inner Circle",
            "Justicar",
            "Kholo",
            "Magaji",
            "Primogen",
            "Prince",
            "Priscus",
            "Regent",
        ],
        "city": [
            None,
            "Addis Ababa",
            "Algiers",
            "Amsterdam",
            "Aragon",
            "Athens",
            "Atlanta",
            "Barcelona",
            "Belo Horizonte",
            "Berlin",
            "Birmingham",
            "Bogota",
            "Boston",
            "Brussels",
            "Budapest",
            "Buenos Aires",
            "Cairo",
            "Canberra",
            "Cape Town",
            "Chicago",
            "Ciudad Juárez",
            "Cleveland",
            "Columbus",
            "Constanza",
            "Copenhagen",
            "Cordoba",
            "Corte",
            "Dallas",
            "Detroit",
            "Dublin",
            "Edinburgh",
            "Fortaleza",
            "Frankfurt",
            "Gary",
            "Gdansk",
            "Geneva",
            "Glasgow",
            "Guadalajara",
            "Guatemala City",
            "Helsinki",
            "Houston",
            "Istanbul",
            "Johannesburg",
            "Lagos",
            "Lima",
            "Lisbon",
            "London",
            "Los Angeles",
            "Manaus",
            "Manila",
            "Mannheim",
            "Melbourne",
            "Mexico City",
            "Miami",
            "Milan",
            "Milwaukee",
            "Mombasa",
            "Monaco",
            "Montreal",
            "Moscow",
            "Nairobi",
            "New York",
            "Ostrava",
            "Paris",
            "Perth",
            "Philadelphia",
            "Pittsburgh",
            "Port-au-Prince",
            "Prague",
            "Rio de Janeiro",
            "Rome",
            "Rotterdam",
            "San Diego",
            "Santiago",
            "Santo Domingo",
            "Seattle",
            "Singapore",
            "Sofia",
            "Stockholm",
            "Strasbourg",
            "Sydney",
            "São Paulo",
            "Taipei",
            "Tampa",
            "Thessaloniki",
            "Toronto",
            "Venice",
            "Versailles",
            "Washington, D.C.",
            "York",
        ],
        "trait": [
            None,
            "Black Hand",
            "Choice",
            "Combo",
            "Infernal",
            "Red List",
            "Scarce",
            "Seraph",
            "Slave",
            "Sterile",
        ],
        "type": [
            "Action",
            "Action Modifier",
            "Ally",
            "Combat",
            "Conviction",
            "Equipment",
            "Event",
            "Imbued",
            "Master",
            "Political Action",
            "Power",
            "Reaction",
            "Retainer",
            "Vampire",
        ],
        "path": [
            None,
            "Caine",
            "Cathari",
            "Death and the Soul",
            "Power and the Inner Voice",
        ],
        "set": [
            "25th",
            "30th",
            "AH",
            "AU",
            "Anarchs",
            "Ant1",
            "Anthology",
            "BH",
            "BL",
            "BSC",
            "CE",
            "DM",
            "DS",
            "EK",
            "EoG",
            "FB",
            "FN",
            "FoL",
            "Gehenna",
            "HttB",
            "HttBR",
            "Jyhad",
            "KMW",
            "KoT",
            "KoTR",
            "LK",
            "LoB",
            "LotN",
            "NB",
            "NB2",
            "NB3",
            "NoR",
            "POD",
            "PP1",
            "PP2",
            "PP3",
            "Promo",
            "SP",
            "SV5",
            "SW",
            "Sabbat",
            "SoB",
            "SoC",
            "TR",
            "TU",
            "Tenth",
            "Third",
            "V5",
            "V5A",
            "V5C",
            "VTES",
        ],
        "rarity": [None, "C", "R", "U", "V"],
        "precon": [
            None,
            "Anarchs:PAB",
            "Anarchs:PAG",
            "Anarchs:PG",
            "Anthology:LARP",
            "BH:PM",
            "BH:PN",
            "BH:PTo",
            "BH:PTr",
            "CE:PB",
            "CE:PM",
            "CE:PN",
            "CE:PTo",
            "CE:PTr",
            "CE:PV",
            "FB:PM",
            "FB:PN",
            "FB:PTo",
            "FB:PTr",
            "FB:PV",
            "FN:PA",
            "FN:PG",
            "FN:PR",
            "FN:PS",
            "HttB:PGar",
            "HttB:PKia",
            "HttB:PSal",
            "HttB:PSam",
            "HttBR:A",
            "HttBR:B",
            "HttBR:PGar",
            "HttBR:PKia",
            "HttBR:PSal",
            "HttBR:PSam",
            "KMW:PAl",
            "KMW:PAn",
            "KMW:PB",
            "KMW:PG",
            "KoT:PB",
            "KoT:PM",
            "KoT:PT",
            "KoT:PV",
            "KoTR:A",
            "KoTR:B",
            "LoB:PA",
            "LoB:PG",
            "LoB:PI",
            "LoB:PO",
            "LotN:PA",
            "LotN:PG",
            "LotN:PR",
            "LotN:PS",
            "NB2:PB",
            "NB2:PBH",
            "NB2:PG",
            "NB2:PMi",
            "NB3:PH",
            "NB3:PL",
            "NB:PM",
            "NB:PN",
            "NB:PTo",
            "NB:PTr",
            "NB:PV",
            "SP:DoF",
            "SP:LB",
            "SP:PoS",
            "SP:PwN",
            "SV5:PCaine",
            "SV5:PCathari",
            "SV5:PDeath",
            "SV5:PPower",
            "SW:PB",
            "SW:PL",
            "SW:PT",
            "SW:PV",
            "TU:A",
            "TU:B",
            "Tenth:A",
            "Tenth:B",
            "Third:PB",
            "Third:PM",
            "Third:PTr",
            "Third:PTz",
            "Third:SKB",
            "Third:SKM",
            "Third:SKTr",
            "Third:SKTz",
            "V5:PH",
            "V5:PL",
            "V5:PM",
            "V5:PN",
            "V5:PTo",
            "V5:PTr",
            "V5:PV",
            "V5A:PB",
            "V5A:PBh",
            "V5A:PG",
            "V5A:PMin",
            "V5C:PR",
            "V5C:PSal",
            "V5C:PTz",
        ],
        "artist": [
            "Aaron Acevedo",
            "Aaron Voss",
            "Abrar Ajmal",
            "Alan Mayoral",
            "Alan Rabinowitz",
            "Albrecht",
            "Alejandro Colucci",
            "Alejandro F. Giraldo",
            "Alexander Dunnigan",
            "Amy Weber",
            "Amy Wilkins",
            "Anastasiia Horbunova",
            "Andre Gates",
            "Andrew Bates",
            "Andrew Hepworth",
            "Andrew Robinson",
            "Andrew Trabbold",
            "Andrey Kiselev",
            "André Freitas",
            "Anna Christenson",
            "Anna Evertsdotter",
            "Anson Maddocks",
            "Ari Targownik",
            "Arkady Roytman",
            "Arthur Roberg",
            "Ash Arnett",
            "Atilio Gambedotti",
            "Attila Adorjany",
            "August Bøgedal Hansen",
            "Avery Butterworth",
            "Becky Cloonan",
            "Becky Jollensten",
            "Ben Mirabelli",
            "Beth Trott",
            "Bob Stevlic",
            "Brad Williams",
            "Brian Ashmore",
            "Brian Graupner",
            "Brian Horton",
            "Brian LeBlanc",
            "Brian Miskelley",
            "Brian Snoddy",
            "Britt Martin",
            "Bryon Wackwitz",
            "Caleb Cleaveland",
            "Camille Défarge",
            "Carlos Díaz",
            "Carmen Cornet",
            "Chad Michael Ward",
            "Chet Masters",
            "Chris McLoughlin",
            "Chris Richards",
            "Chris Stevens",
            "Christel Espenkrona",
            "Christian Byrne",
            "Christopher Rush",
            "Christopher Shy",
            "Cliff Nielson",
            "Clint Langley",
            "Corey Macourek",
            "Cos Koniotis",
            "Craig Grant",
            "Craig Maher",
            "D. Fryendall",
            "Damien Mammoliti",
            "Dan Frazier",
            "Dan Smith",
            "Daniel Argudo",
            "Daniel Gelon",
            "Darryl Elliott",
            "Dave Leri",
            "Dave Roach",
            "Dave Seeley",
            "David Day",
            "David Fooden",
            "David Ho",
            "David Kimmel",
            "Dennis Calero",
            "Diana Vick",
            "Doug Alexander",
            "Doug Gregory",
            "Doug Stambaugh",
            "Douglas Shuler",
            "Drew Tucker",
            "Durwin Talon",
            "E.M. Gist",
            "Ed Tadem",
            "Edouard Noisette",
            "Edward Beard, Jr.",
            "Efrem Palacios",
            "Elli Adams",
            "Eric Deschamps",
            "Eric Kim",
            "Eric LaCombe",
            "Eric Lofgren",
            "Erica Danell",
            "Esther Sanz",
            "Felipe Gaona",
            "Felipe Headley",
            "Francesc Grimalt",
            "Francisco Tébar",
            "Franz Vohwinkel",
            "Fred Harper",
            "Fred Hooper",
            "Gabriel de Góes Figueiredo",
            "Gary Chatterton",
            "Gary Leach",
            "Ginés Quiñonero-Santiago",
            "Glen Osterberger",
            "Grant Garvin",
            "Grant Goleash",
            "Greg Boychuk",
            "Greg Loudon",
            "Greg Simanson",
            "Grzegorz Bobrowski",
            "Gábor Németh",
            "Hannibal King",
            "Harold Arthur McNeill",
            "Heather Hudson",
            "Heather J. McKinney",
            "Heather V. Kreiter",
            "Helena García Huang",
            "Ian Hernaiz",
            "Imaginary Friends Studios",
            "J Frederick Y",
            "Jake Smidt",
            "James Allen Higgins",
            "James Richardson",
            "James Stowe",
            "Jami Waggoner",
            "Jared Smith",
            "Jarkko Suvela",
            "Jason Alexander Behnke",
            "Jason Brubaker",
            "Javier Santos",
            "Jeff Holt",
            "Jeff Klimek",
            "Jeff Laubenstein",
            "Jeff Menges",
            "Jeff Miracola",
            "Jeff Rebner",
            "Jenny Frison",
            "Jer Carolina",
            "Jeremy C. Bills",
            "Jeremy McHugh",
            "Jesús Ybarzábal",
            "Jim Di Bartolo",
            "Jim Nelson",
            "Jim Pavelec",
            "Joe Slucher",
            "Joe Ziolkowski",
            "Joel Biske",
            "John Bolton",
            "John Bridges",
            "John Kent",
            "John Matson",
            "John McCrea",
            "John Scotello",
            "John Van Fleet",
            "Josh Timbrook",
            "Juan Antonio Serrano Garcia",
            "Juan Calle",
            "Julian Jackson",
            "Julie Collins",
            "Justin Norman",
            "Kaja Foglio",
            "Kamilla Khaminskaya",
            "Kari Christensen",
            "Karl Waller",
            "Katie McCaskill",
            "Kelly Howlett",
            "Ken Kokoszka",
            "Ken Meyer, Jr.",
            "Kent Williams",
            "Kera Now",
            "Kevin McCann",
            "Kieran Yanner",
            "Kim Aldau",
            "Konrad Waściński",
            "Krasen Maximov",
            "Krzysztof Bieniawski",
            "Kyri Koniotis",
            "L. A. Williams",
            "Laia López Tubau",
            "Larry MacDougall",
            "Lawrence Snelly",
            "Lee Carter",
            "Lee Dotson",
            "Lee Fields",
            "Leif Jones",
            "Liz Danforth",
            "Ludovic Salvador",
            "Marc Simonetti",
            "Marco Marzoni",
            "Marco Nelor",
            "Margaret Organ-Kean",
            "Marian Churchland",
            "Mark Kelly",
            "Mark Nelson",
            "Mark Poole",
            "Mark Tedin",
            "Marta Ruiz Anguera",
            "Martín de Diego Sábada",
            "María Lorén",
            "Matheus Calza",
            "Mathias Kollros",
            "Matias Tapia",
            "Matt Cavotta",
            "Matt Dixon",
            "Matt Smith",
            "Matt Wilson",
            "Matthew Mitchell",
            "Max Shade Fellwalker",
            "Melissa Benson",
            "Melissa Uran",
            "Michael Astrachan",
            "Michael Dixon",
            "Michael Gaydos",
            "Michael Weaver",
            "Michele Bertilorenzi",
            "Mick Bertilorenzi",
            "Mike Chaney",
            "Mike Danza",
            "Mike Dringenberg",
            "Mike Huddleston",
            "Mike Raabe",
            "Mirko Falloni",
            "Mitch Mueller",
            "Monte Moore",
            "Newel Anderson",
            "Nicola Leonard",
            'Nicolas "Dimple" Bigot',
            "Nicole Cardiff",
            "Nigel Sade",
            "Nilson",
            "Noah Hirka",
            "Noora Hirvonen",
            "Né Né Thomas",
            "Oliver Meinerding",
            "Oscar Salcedo",
            "Othon Nikolaidis",
            "Pablo D. Hidalgo",
            "Paolo Puggioni",
            "Pat Loboyko",
            "Pat Morrissey",
            "Patrick Kochakji",
            "Patrick Lambert",
            "Patrick McEvoy",
            "Pau López Vila",
            "Paul Ballard",
            "Paul Tobin",
            "Pete Burges",
            "Pete Venters",
            "Peter Bergting",
            "Peter Kim",
            "Peter Mohrbacher",
            "Peter Scholtz",
            "Phil Wohr",
            "Phill Simpson",
            "Phillip Hilliker",
            "Phillip Tan",
            "Quinton Hoover",
            "Randy Asplund",
            "Randy Gallegos",
            "Raquel Cornejo",
            "Rebecca Guay",
            "Riccardo Fabiani",
            "Richard Kane Ferguson",
            "Richard Thomas",
            "Rick Berry",
            "Rick O'Brien",
            "Rik Martin",
            "Rob Alexander",
            "Robert McNeill",
            "Robin Chyo",
            "Rodrigo González Toledo",
            "Roel Wielinga",
            "Roger Raupp",
            "Ron Lemon",
            "Ron Spencer",
            "Ron Van Halen",
            "Rubén Bravo",
            "Samuel Araya",
            "Sandra Chang-Adair",
            "Sandra Everingham",
            "Satyr",
            "Scott Fischer",
            "Scott Kirschner",
            "Scott M. Bakal",
            "Shane Coppage",
            "Steve Casper",
            "Steve Eidson",
            "Steve Ellis",
            "Steve Prescott",
            "Stuart Beel",
            "Stuart Sayger",
            "Sue Ann Harkey",
            "Susan Van Camp",
            "Talon Dunning",
            "Ted Naifeh",
            "Terese Nielsen",
            "Thea Maia",
            "Theodore Black",
            "Thomas Baxa",
            "Thomas Denmark",
            "Thomas Manning",
            "Thomas Nairb",
            "Tim Bradstreet",
            "Tom Biondillo",
            "Tom Duncan",
            "Tom Gianni",
            "Tom Wänerstrand",
            'Tomáš "zelgaris" Zahradníček',
            "Tony Harris",
            "Tony Shasteen",
            "Torstein Nordstrand",
            "Travis Ingram",
            "Trevor Claxton",
            "UDON",
            "Vatche Mavlian",
            "Veronica Jones",
            "Vince Locke",
            "Warren Mahy",
            "Will Simpson",
            "William O'Connor",
            "Yanis Cardin",
            "Zina Saunders",
            "matrix von z",
            "rk post",
        ],
    }


def test_search_basic() -> None:
    """Test basic search."""
    # no parameter returns nothing
    assert len(vtes.VTES.search()) == 0
    # non-existing dimension raises
    with pytest.raises(ValueError):
        vtes.VTES.search(foo="bar")
    # non-existing value in dimension does not raise
    assert len(vtes.VTES.search(bonus="foo")) == 0
    # card text
    assert vtes.VTES.search(card_text="this equipment card represents a location") == [
        vtes.VTES["Catacombs"],
        vtes.VTES["Dartmoor, England"],
        vtes.VTES["Inveraray, Scotland"],
        vtes.VTES["Local 1111"],
        vtes.VTES["Lyndhurst Estate, New York"],
        vtes.VTES["Palatial Estate"],
        vtes.VTES["Pier 13, Port of Baltimore"],
        vtes.VTES["Ruins of Ceoris"],
        vtes.VTES["Ruins of Villers Abbey, Belgium"],
        vtes.VTES["Sacré-Cœur Cathedral, France"],
        vtes.VTES["San Lorenzo de El Escorial, Spain"],
        vtes.VTES["San Nicolás de los Servitas"],
        vtes.VTES["The Ankara Citadel, Turkey"],
        vtes.VTES["Winchester Mansion"],
        vtes.VTES["Zaire River Ferry"],
    ]
    # flavor text
    assert vtes.VTES.search(flavor_text="Baudelaire") == [
        vtes.VTES["Aching Beauty"],
        vtes.VTES["Blood Sweat"],
        vtes.VTES["Breath of Thanatos"],
        vtes.VTES["Cats' Guidance"],
        vtes.VTES["Dance with the Devil"],
        vtes.VTES["Earth Meld"],
        vtes.VTES["Form of the Serpent"],
        vtes.VTES["Giuseppe, Gravedigger"],
        vtes.VTES["Gleam of Red Eyes"],
        vtes.VTES["Haven Uncovered"],
        vtes.VTES["Opium Den"],
        vtes.VTES["Order of Hermes Cabal"],
        vtes.VTES["Psychic Veil"],
        vtes.VTES["Rom Gypsy"],
        vtes.VTES["Shade"],
        vtes.VTES["Threats"],
        vtes.VTES["Tongue of the Serpent"],
        vtes.VTES["Vanish from the Mind's Eye"],
    ]
    # don't match disciplines trigrams in card text
    # (although with braces, [thn] would match)
    assert not vtes.VTES.search(card_text="thn")
    # city
    assert vtes.VTES.search(city=["Chicago"]) == [
        vtes.VTES["Antón de Concepción"],
        vtes.VTES["Crusade: Chicago"],
        vtes.VTES["Horatio Ballard"],
        vtes.VTES["Kevin Jackson (G7)"],
        vtes.VTES["Lachlan, Noddist"],
        vtes.VTES["Lodin (Olaf Holte)"],
        vtes.VTES["Maldavis (ADV)"],
        vtes.VTES["Maxwell"],
        vtes.VTES["Praxis Seizure: Chicago"],
        vtes.VTES["Sir Walter Nash"],
    ]
    # title
    assert vtes.VTES.search(title=["Imperator"]) == [
        vtes.VTES["Camarilla's Iron Fist"],
        vtes.VTES["Confiscation"],
        vtes.VTES["Karsh (ADV)"],
        vtes.VTES["National Guard Support"],
        vtes.VTES["Persona Non Grata"],
        vtes.VTES["Reinforcements"],
        vtes.VTES["Rubicon"],
        vtes.VTES["Scourge"],
    ]
    # discipline (inf matches sup), title
    assert vtes.VTES.search(title=["Primogen"], discipline=["ser"]) == [
        vtes.VTES["Amenophobis"]
    ]
    # stealth, votes
    assert vtes.VTES.search(bonus=["Stealth", "Votes"]) == [
        vtes.VTES["Camarilla Conclave"],
        vtes.VTES["Loki's Gift"],
        vtes.VTES["Perfect Paragon"],
    ]
    # clans, votes provided by master cards
    assert vtes.VTES.search(bonus=["Votes"], clan=["Banu Haqim"], type=["Master"]) == [
        vtes.VTES["Alamut"],
        vtes.VTES["The Black Throne"],
    ]
    # title when merged
    assert vtes.VTES.search(clan=["Banu Haqim"], title=["Justicar"]) == [
        vtes.VTES["Kasim Bayar"],
        vtes.VTES["Tegyrius, Vizier (ADV)"],
    ]
    # traits
    assert vtes.VTES.search(clan=["Nagaraja"], trait=["Black Hand"]) == [
        vtes.VTES["Sennadurek"],
    ]
    assert vtes.VTES.search(clan=["Banu Haqim"], trait=["Red List"]) == [
        vtes.VTES["Jamal"],
        vtes.VTES["Tariq, The Silent (ADV)"],
    ]
    # sect
    assert vtes.VTES.search(clan=["Banu Haqim"], sect=["Camarilla"], group=["G2"]) == [
        vtes.VTES["Al-Ashrad, Amr of Alamut (ADV)"],
        vtes.VTES["Tegyrius, Vizier"],
        vtes.VTES["Tegyrius, Vizier (ADV)"],
    ]
    # trait on library card
    assert vtes.VTES.search(type=["Action Modifier"], trait=["Black Hand"]) == [
        vtes.VTES["Circumspect Revelation"],
        vtes.VTES["Seraph's Second"],
        vtes.VTES["The Art of Memory"],
    ]
    # title requirement
    assert vtes.VTES.search(type=["Reaction"], title=["Justicar"]) == [
        vtes.VTES["Legacy of Power"],
        vtes.VTES["Second Tradition: Domain"],
    ]
    # "Requires titled Sabbat/Camarilla" maps to all possible titles
    assert vtes.VTES.search(bonus=["Intercept"], title=["Archbishop"]) == [
        vtes.VTES["National Guard Support"],
        vtes.VTES["Persona Non Grata"],
        vtes.VTES["Under Siege"],
    ]
    # reducing intercept is stealth, denying block is stealth
    assert vtes.VTES.search(
        bonus=["Stealth"], discipline=["chi"], kind=["Library"]
    ) == [
        vtes.VTES["Fata Morgana"],
        vtes.VTES["Heart's Desire"],
        vtes.VTES["Mirror's Visage"],
        vtes.VTES["Smoke and Mirrors"],
        vtes.VTES["Will-o'-the-Wisp"],
    ]
    # reducing stealth is intercept
    assert vtes.VTES.search(
        bonus=["Intercept"], discipline=["chi"], kind=["Library"]
    ) == [
        vtes.VTES["Draba"],
        vtes.VTES["Ignis Fatuus"],
        # it has [chi], intercept is on another discipline, but eh.
        vtes.VTES["Netwar"],
        vtes.VTES["Veiled Sight"],
    ]
    # no discipline (crypt)
    assert vtes.VTES.search(discipline=[None], kind=["Crypt"]) == [
        vtes.VTES["Anarch Convert"],
        vtes.VTES["Sandra White"],
        vtes.VTES["Smudge the Ignored"],
    ]
    # no discipline, sect requirement
    assert vtes.VTES.search(
        discipline=[None], sect=["Sabbat"], bonus=["Intercept"]
    ) == [
        vtes.VTES["Abbot"],
        vtes.VTES["Harzomatuili"],
        vtes.VTES["Under Siege"],
    ]
    assert vtes.VTES.search(type=["Political Action"], sect=["Independent"]) == [
        vtes.VTES["Free States Rant"],
        vtes.VTES["Reckless Agitation"],
    ]
    assert vtes.VTES.search(type=["Political Action"], sect=["Anarch"]) == [
        vtes.VTES["Anarch Salon"],
        vtes.VTES["Eat the Rich"],
        # this one does not show here because Anarch is not a requirement
        # could be the other way around, no matter
        # vtes.VTES["Exclusion Principle"],
        # that one should not show here - its anti-Anarch, not Anarch
        # vtes.VTES["Persona Non Grata"],
        vtes.VTES["Firebrand"],
        vtes.VTES["Free States Rant"],
        vtes.VTES["Patsy"],
        vtes.VTES["Reckless Agitation"],
        vtes.VTES["Revolutionary Council"],
        vtes.VTES["Sweeper"],
    ]
    assert vtes.VTES.search(
        discipline=["ani"], bonus=["Intercept"], trait=["Choice"]
    ) == [
        vtes.VTES["Deep Ecology"],
        vtes.VTES["Detect Authority"],
        vtes.VTES["Ensnare a Beast"],
        vtes.VTES["Falcon's Eye"],
        vtes.VTES["Speak with Spirits"],
        vtes.VTES["The Mole"],
    ]
    assert vtes.VTES.search(
        discipline=["ani"], bonus=["Intercept"], trait=["Combo"]
    ) == [
        vtes.VTES["Read the Winds"],
    ]
    # superior disciplines (vampires only)
    assert vtes.VTES.search(discipline=["OBE"], group=["G2"]) == [
        vtes.VTES["Blanche Hill"],
        vtes.VTES["Matthias"],
    ]
    # artist
    assert vtes.VTES.search(artist=["E.M. Gist"]) == [
        vtes.VTES["Flames of Insurrection"],
        vtes.VTES["Harmony"],
        vtes.VTES["Marcus Vitel"],
        vtes.VTES["Public Enemy"],
        vtes.VTES["Rutor"],
    ]


def test_search_i18n() -> None:
    """Test i18n search."""
    # i18n - match the given language in addition to english
    assert vtes.VTES.search(
        card_text="cette carte d'équipement représente un lieu", lang=models.Lang.FR
    ) == [
        vtes.VTES["Living Manse"],
        vtes.VTES["The Ankara Citadel, Turkey"],
    ]
    # # i18n - also works with region codes
    # assert vtes.VTES.search(
    #     text="cette carte d'équipement représente un lieu", lang="fr-fr"
    # ) == {
    #     vtes.VTES["Living Manse"],
    #     vtes.VTES["The Ankara Citadel, Turkey"],
    # }
    # # i18n - whatever case is used for the region code
    # assert vtes.VTES.search(
    #     text="cette carte d'équipement représente un lieu", lang="fr_FR"
    # ) == {
    #     vtes.VTES["Living Manse"],
    #     vtes.VTES["The Ankara Citadel, Turkey"],
    # }
    # i18n - do not match translations in other languages
    assert (
        vtes.VTES.search(
            card_text="esta carta de equipo representa un lugar", lang=models.Lang.FR
        )
        == []
    )
    assert vtes.VTES.search(
        card_text="esta carta de equipo representa un lugar", lang=models.Lang.ES
    ) == [
        vtes.VTES["Living Manse"],
        vtes.VTES["The Ankara Citadel, Turkey"],
    ]


def test_search_ranges() -> None:
    """Test search ranges."""
    assert vtes.VTES.search(group=["G1", "G2", "G3"], clan=["Kiasyd"]) == [
        vtes.VTES["Bartholomew"],
        vtes.VTES["Béatrice L'Angou"],
        vtes.VTES["Julia Prima"],
        vtes.VTES["Kassiym Malikhair"],
        vtes.VTES["Marconius"],
        vtes.VTES["Quincy, The Trapper"],
    ]


def test_search_cornercases() -> None:
    """Test search cornercases."""
    # some tricky cards test (add cards for NR tests)
    # providing a stealth action does not register as "stealth" bonus
    assert vtes.VTES["Tracker's Mark"] in vtes.VTES.search(
        bonus=["Intercept"], type=["Combat"]
    )
    assert vtes.VTES["Tracker's Mark"] not in vtes.VTES.search(
        bonus=["Stealth"], type=["Combat"]
    )
    assert vtes.VTES["Brainwash"] not in vtes.VTES.search(
        bonus=["Stealth"], type=["Master"]
    )
    # Gwen Brand whould show up with superior disciplines
    assert vtes.VTES["Gwen Brand"] in vtes.VTES.search(
        discipline=["AUS", "CHI", "FOR", "ANI"], clan=["Ravnos"], group=["G5"]
    )
    # The Baron is not Anarch
    assert vtes.VTES["The Baron"] not in vtes.VTES.search(
        sect=["Anarch"], clan=["Samedi"]
    )


def test_vekn() -> None:
    """Test VEKN load.

    Skipped if there is no internet connection.
    """
    test_vtes = vtes._VTES()
    # test_vtes.load_from_vekn()
    assert len(test_vtes) >= 4127
    # some underscored keys, like _i18n key for example, are missing in offline mode
    assert set(dataclasses.asdict(test_vtes[100001]).keys()).issuperset(
        {
            "artists",
            "text",
            "id",
            "banned",
            "legal",
            "printed_name",
            "cost",
            "rulings",
            "prints",
            "types",
            "url",
        }
    )
    assert utils.json_encode(test_vtes[201362]) == {
        "artists": ["John Van Fleet"],
        "capacity": 7,
        "clan": "Brujah",
        "disciplines": ["cel", "dom", "pre", "POT"],
        "group": "G2",
        "id": 201362,
        "kind": "Crypt",
        "legal": "2001-07-11",
        "name_variants": [{"name": "Theo Bell", "type": "Vernacular"}],
        "printed_name": "Theo Bell",
        "prints": [
            {
                "occurrences": [
                    {"frequency": "U", "multiplier": 1.0, "type": "Rarity"}
                ],
                "set": {"code": "FN", "id": 300007},
                "url": "https://static.krcg.org/card/set/final-nights/theobellg2.jpg",
            },
            {
                "occurrences": [{"bundle": "PB", "copies": 1, "type": "Precon"}],
                "set": {"code": "CE", "id": 300009},
                "url": "https://static.krcg.org/card/set/camarilla-edition/theobellg2.jpg",
            },
        ],
        "suffix": "G2",
        "text": (
            "Camarilla: Theo may enter combat with any ready minion controlled by "
            "another Methuselah as a Ⓓ action. If you control a ready prince or "
            "justicar, blood hunts cannot be called on Theo."
        ),
        "types": ["Vampire"],
        "unicity_suffix": "G2",
        "url": "https://static.krcg.org/card/theobellg2.jpg",
        "variants": [
            {"id": 201363, "suffix": "G2 ADV", "type": "Advanced"},
            {"id": 201613, "suffix": "G6", "type": "Evolution"},
        ],
    }


def test_promo_scans() -> None:
    """Test promo scans."""
    assert utils.json_encode(vtes.VTES["The Dracon"]) == {
        "artists": ["Ginés Quiñonero-Santiago"],
        "capacity": 11,
        "clan": "Tzimisce",
        "disciplines": ["ANI", "AUS", "POT", "THA", "VIC"],
        "group": "G5",
        "id": 200385,
        "kind": "Crypt",
        "legal": "2015-02-16",
        "name_variants": [
            {"name": "Dracon", "type": "Vernacular"},
            {"name": "Dracon, The", "type": "Lexicographical"},
        ],
        "printed_name": "The Dracon",
        "prints": [
            {
                "occurrences": [
                    {"date": "2015-02-16", "type": "Single"},
                    {"date": "2018-10-04", "type": "Single"},
                    {"date": "2019-04-08", "type": "Single"},
                ],
                "set": {"code": "Promo"},
                "url": "https://static.krcg.org/card/set/promo/thedracong5.jpg",
            },
            {
                "occurrences": [
                    {"copies": 10, "type": "Precon"},
                ],
                "set": {"code": "PP1", "id": 320004},
                "url": "https://static.krcg.org/card/set/promo-pack-1/thedracong5.jpg",
            },
            {
                "occurrences": [
                    {"date": "2022-04-27", "type": "Single"},
                ],
                "set": {"code": "POD"},
                "url": "https://static.krcg.org/card/set/print-on-demand/thedracong5.jpg",
            },
        ],
        "suffix": "G5",
        "text": (
            "Independent: Cards requiring Vicissitude [vic] cost The Dracon -1 blood. "
            "He inflicts +1 damage or steals 1 additional blood or life with ranged "
            "strikes (even at close range). Flight [FLIGHT]. +1 bleed. +2 strength."
        ),
        "types": ["Vampire"],
        "url": "https://static.krcg.org/card/thedracong5.jpg",
    }
    {
        "_name": "Dracon, The",
        "_set": "Promo-20150216, Promo-20181004:HB2, Promo-20190408, POD:DTC",
        "artists": [
            "Ginés Quiñonero-Santiago",
        ],
        "capacity": 11,
        "card_text": (
            "Independent: Cards requiring Vicissitude [vic] cost The Dracon -1 blood. "
            "He inflicts +1 damage or steals 1 additional blood or life with ranged "
            "strikes (even at close range). Flight [FLIGHT]. +1 bleed. +2 strength."
        ),
        "clans": [
            "Tzimisce",
        ],
        "disciplines": [
            "ANI",
            "AUS",
            "POT",
            "THA",
            "VIC",
        ],
        "group": "5",
        "id": 200385,
        "legality": "2015-02-16",
        "name": "The Dracon (G5)",
        "name_variants": [
            "Dracon, The (G5)",
            "The Dracon",
            "Dracon, The",
        ],
        "ordered_sets": [
            "2015 Storyline Rewards",
            "2018 Humble Bundle",
            "2019 Promo Pack 1",
        ],
        "printed_name": "The Dracon",
        "scans": {
            "2015 Storyline Rewards": (
                "https://static.krcg.org/card/set/promo/dracontheg5.jpg"
            ),
            "2018 Humble Bundle": (
                "https://static.krcg.org/card/set/humble-bundle/dracontheg5.jpg"
            ),
            "2019 Promo Pack 1": (
                "https://static.krcg.org/card/set/promo-pack-1/dracontheg5.jpg"
            ),
            "Print on Demand": (
                "https://static.krcg.org/card/set/print-on-demand/dracontheg5.jpg"
            ),
        },
        "sets": {
            "2015 Storyline Rewards": [
                {
                    "copies": 1,
                    "release_date": "2015-02-16",
                },
            ],
            "2018 Humble Bundle": [
                {
                    "copies": 2,
                    "precon": "Humble Bundle",
                    "release_date": "2018-10-04",
                },
            ],
            "2019 Promo Pack 1": [
                {
                    "copies": 1,
                    "release_date": "2019-04-08",
                },
            ],
            "Print on Demand": [
                {
                    "copies": 1,
                    "precon": "DriveThruCards",
                },
            ],
        },
        "text_change": True,
        "types": [
            "Vampire",
        ],
        "url": "https://static.krcg.org/card/dracontheg5.jpg",
    }


def test_dump() -> None:
    """Test dump."""
    version = importlib.metadata.version("krcg")
    pickle_file = os.path.join(tempfile.gettempdir(), f"krcg_vtes_{version}.pkl")
    assert os.path.exists(pickle_file)
    json.dumps(utils.json_encode(vtes.VTES._cards))
