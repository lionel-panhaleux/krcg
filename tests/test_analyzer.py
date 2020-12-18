from krcg import analyzer
from krcg import vtes


def test_base(TWDA):
    A = analyzer.Analyzer(TWDA.values())
    A.refresh()
    nana = vtes.VTES["Nana Buruku"]
    aksinya = vtes.VTES["Aksinya Daclau"]
    assert A.played[nana] == 2
    A.refresh(nana)
    assert sorted(A.affinity[nana].most_common())[0] == (
        aksinya,
        1 / 2,
    )
    A.refresh(nana, aksinya, similarity=1)
    assert len(A.examples) == 1
