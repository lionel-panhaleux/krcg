from krcg import analyzer


def test_base(twda):
    A = analyzer.Analyzer(twda)
    A.refresh()
    assert A.played["Nana Buruku"] == 2
    A.refresh("Nana Buruku")
    assert sorted(A.affinity["Nana Buruku"].most_common())[0] == (
        "Aksinya Daclau",
        1 / 2,
    )
    A.refresh("Nana Buruku", "Aksinya Daclau", similarity=1)
    assert len(A.examples) == 1
