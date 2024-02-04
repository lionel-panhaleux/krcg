from krcg import rulings
from krcg import vtes


def test_parse():
    """Call with `pytest -W rulings::Warning` to raise errors on ruling warnings"""
    reader = rulings.RulingReader()
    list(reader)
    vtes.VTES.load_from_vekn()
