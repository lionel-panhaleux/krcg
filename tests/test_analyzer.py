from src import analyzer


def test_base():
    A = analyzer.Analyzer()
    A.refresh()
    assert A.played["Stavros"] == 3
    A.refresh("Stavros")
    assert sorted(A.affinity["Stavros"].most_common())[0] == (
        "Alicia Barrows",
        1 / 3,
    )
    A.refresh("Stavros", "Alicia Barrows", similarity=1)
    assert len(A.examples) == 1
