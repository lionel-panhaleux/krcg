"""Test the cards."""

import aiohttp
import pytest
import warnings

from krcg import collections
from krcg import loader


@pytest.mark.baseline
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_card_variants(cards: collections.CardDict) -> None:
    """Card name variants and aliases (translation-dependent — drift is amber)."""

    def sorted_variant(id_: int) -> tuple[list[str], list[str]]:
        """Sort the variants of a card (for stable tests)."""
        return (
            sorted(
                k for k, v in cards._dict.items() if isinstance(k, str) and v.id == id_
            ),
            sorted(
                k for k, v in cards._aliases.items() if isinstance(k, str) and v == id_
            ),
        )

    # "," suffixes in vampire names are common, and often omitted in deck lists
    assert sorted_variant(cards["Sascha Vykos, The Angel of Caine (G2)"].id) == (
        [
            "sascha vykos, the angel of caine",
            "sascha vykos, the angel of caine (g2)",
        ],
        ["sascha vykos", "sascha vykos (g2)"],
    )
    # the (adv) suffix should always be present, even when suffix is removed
    assert sorted_variant(cards["Sascha Vykos, The Angel of Caine (G2 ADV)"].id) == (
        [
            "sascha vykos, the angel of caine (adv)",
            "sascha vykos, the angel of caine (g2 adv)",
        ],
        ["sascha vykos (adv)", "sascha vykos (g2 adv)"],
    )
    assert sorted_variant(cards["Theo Bell (G2)"].id) == (
        [
            "theo bell (g2)",
        ],
        ["theo bell"],
    )
    # ":" suffixes should not be removed because of this
    assert sorted_variant(cards["Praxis Seizure: Athens"].id) == (
        ["praxis seizure: athens"],
        [],
    )
    # ", The" suffix produces two variants : "The " prefix and omission.
    assert sorted_variant(cards["The unnamed"].id) == (
        [
            "the unnamed",
            "the unnamed (g6)",
            "unnamed, the",
            "unnamed, the (g6)",
        ],
        [
            "unnamed",
            "unnamed (g6)",
        ],
    )
    assert sorted_variant(cards["Anarch Convert"].id) == (
        [
            "anarch convert",
            "anarch convert (any)",
        ],
        [],
    )
    # Can omit the "The" particle on too a short name, but only as alias
    assert sorted_variant(cards["The Line"].id) == (
        [
            "line, the",
            "the line",
        ],
        [],
    )
    # Produce ascii variants of "Aka" variant ("sEbastiAn")
    assert sorted_variant(cards["Sébastien Goulet (G3)"].id) == (
        [
            "sebastien goulet",
            "sebastien goulet (g3)",
        ],
        [
            "sebastian goulet",
            "sebastian goulet (g3)",
        ],
    )
    # the (adv) suffix should be present in all variants, for the advanced form
    assert sorted_variant(cards["Sébastien Goulet (G3 ADV)"].id) == (
        [
            "sebastien goulet (adv)",
            "sebastien goulet (g3 adv)",
        ],
        [
            "sebastian goulet (adv)",
            "sebastian goulet (g3 adv)",
        ],
    )
    # multiple commas produce a lot of variants
    assert sorted_variant(cards["The Rumor Mill, Tabloid Newspaper"].id) == (
        [
            "rumor mill, tabloid newspaper, the",
            "the rumor mill, tabloid newspaper",
        ],
        [
            "rumor mill",
            "rumor mill, tabloid newspaper",
            "the rumor mill",
        ],
    )
    # The "The" omission variant is not included if the base name is too short,
    # even in multiple commas cases.
    assert sorted_variant(cards["The Louvre, Paris"].id) == (
        [
            "louvre, paris, the",
            "the louvre, paris",
        ],
        [
            "le louvre",
            "le louvre, paris",
            "louvre",
            "louvre, paris",
            "louvre, paris, le",
            "the louvre",
        ],
    )
    # mixing commas, non-ASCII and "Aka"
    assert sorted_variant(cards["Sacré-Cœur Cathedral, France"].id) == (
        [
            "sacre-coeur cathedral, france",
        ],
        [
            "sacre-coeur cathedral",
            "sacre-cour cathedral",
            "sacre-cour cathedral, france",
        ],
    )
    # ", The" suffix in "Aka" produces a variant with "The " prefix.
    assert sorted_variant(cards["Fourth Tradition: The Accounting"].id) == (
        [
            "fourth tradition: the accounting",
        ],
        [
            "4th tradition",
            "fourth tradition",
            "fourth tradition, the",
            "fourth tradition: the accounting",
            "fourth tradition: the accounting, the",
            "the fourth tradition",
            "the fourth tradition: the accounting",
        ],
    )
    # translations do not show up on variants
    assert sorted_variant(cards["Ankara Citadel, Turkey"].id) == (
        [
            "ankara citadel, turkey, the",
            "the ankara citadel, turkey",
        ],
        [
            "ankara citadel",
            "ankara citadel, turkey",
            "citadelle d'ankara",
            "citadelle d'ankara, turquie",
            "citadelle d'ankara, turquie, la",
            "ciudadela de ankara",
            "ciudadela de ankara, turquia",
            "ciudadela de ankara, turquia, la",
            "la citadelle d'ankara",
            "la citadelle d'ankara, turquie",
            "la ciudadela de ankara",
            "la ciudadela de ankara, turquia",
            "the ankara citadel",
        ],
    )


def test_card_names_and_urls(cards: collections.CardDict) -> None:
    """Names are stored as printed; the article is never filed as a suffix."""
    base = "https://static.krcg.org/card/"
    # the image URL is the ascii of the name as printed (article prefixed)
    assert cards["The Ankou"].url == base + "theankoug5.jpg"
    assert cards["The Louvre, Paris"].url == base + "thelouvreparis.jpg"
    assert cards["An Anarch Manifesto"].url == base + "ananarchmanifesto.jpg"
    assert cards["El Monseñor"].url == base + "elmonsenorg6.jpg"
    assert cards["Le Dinh Tho"].url == base + "ledinhthog2.jpg"
    assert cards["Theo Bell (G2)"].url == base + "theobellg2.jpg"
    # translations and prints share the same filename
    assert all(p.url.endswith("/theankoug5.jpg") for p in cards["The Ankou"].prints)
    # filing/sort order drops the leading article, for every language
    assert cards["The Ankou"].filing_name == "Ankou"
    assert cards["El Monseñor"].filing_name == "Monseñor"
    # but a suffix-written name still resolves, for every filing article
    assert cards["Ankou, The"].id == cards["The Ankou"].id
    assert cards["Monseñor, El"].id == cards["El Monseñor"].id
    assert cards["Dinh Tho, Le"].id == cards["Le Dinh Tho"].id
    assert cards["Anarch Manifesto, An"].id == cards["An Anarch Manifesto"].id


@pytest.mark.asyncio
async def test_load_from_static_server() -> None:
    """Test loading cards from the static server."""
    with warnings.catch_warnings(record=True) as wrec:
        warnings.simplefilter("always")
        async with aiohttp.ClientSession() as session:
            cm = await loader.load_online(session)
    assert not wrec
    # Ensure we have at least one well-known card present
    assert 200076 in cm  # Anarch Convert
    assert cm[200076].full_name == "Anarch Convert"


def test_load_local() -> None:
    """`load_local` builds the cards offline from the packaged VEKN CSVs."""
    with warnings.catch_warnings(record=True) as wrec:
        warnings.simplefilter("always")
        cm = loader.load_local()
    assert not [w.message for w in wrec]
    assert 200076 in cm  # Anarch Convert
