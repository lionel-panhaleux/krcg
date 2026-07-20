"""Test the VEKN csv fixups."""

from krcg.scripts import fix_csv


def row(id_: str, sets: str) -> dict[str, str]:
    """A card row carrying just what fix_set_field reads."""
    return {
        "Id": id_,
        "Name": "",
        "Set": sets,
        "Clan": "",
        "Card Text": "",
        "Discipline": "",
    }


def test_set_field_is_idempotent() -> None:
    """The recipe rewrites the csv in place, so a re-run must not stack additions."""
    once = fix_csv.fix_set_field(row("100018", "Jyhad:U1, Promo-20211015"))
    assert once == "Jyhad:U1, Promo:20211015, PP3:1"
    assert fix_csv.fix_set_field(row("100018", once)) == once


def test_set_field_keeps_larp_out_of_anthology_1() -> None:
    """Only the natively bare Anthology cards are reprinted in Ant1."""
    assert fix_csv.fix_set_field(row("101110", "Anthology:LARP, SoB:1")) == (
        "Anthology:1, SoB:1"
    )
    assert fix_csv.fix_set_field(row("101112", "Anthology")) == "Anthology"
