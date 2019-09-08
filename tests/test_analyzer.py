from src import analyzer
from src import twda
from src import vtes


def test_base():
    vtes.VTES.load_from_vekn()
    # speed up the tests: parse the first 100 decks only to avoid useless 25 seconds.
    twda.TWDA.load_from_vekn(limit=100)
    A = analyzer.Analyzer()
    A.refresh()
    assert A.played["Stavros"] == 1
    A.refresh("Stavros")
    assert sorted(A.affinity["Stavros"].most_common())[0] == ("Adana de Sforza", 1)
    A.refresh("Stavros", "Adana de Sforza", similarity=1)
    assert len(A.examples) == 1
