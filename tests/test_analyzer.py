from src import analyzer
from src import twda
from src import vtes


def test_base():
    vtes.VTES.load_from_vekn(save=False)
    # speed up the tests: parse the first 100 decks only to avoid useless 25 seconds.
    twda.TWDA.load_from_vekn(limit=100, save=False)
    A = analyzer.Analyzer()
    A.refresh()
    assert A.played["Stavros"] == 2
    A.refresh("Stavros")
    assert sorted(A.affinity["Stavros"].most_common())[0] == ("Alicia Barrows", 0.5)
    A.refresh("Stavros", "Alicia Barrows", similarity=1)
    assert len(A.examples) == 1
