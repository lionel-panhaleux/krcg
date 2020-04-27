from src import analyzer


# def test_base(krcg):
#     A = analyzer.Analyzer()
#     A.refresh()
#     assert A.played["Stavros"] == 2
#     A.refresh("Stavros")
#     assert sorted(A.affinity["Stavros"].most_common())[0] == ("Alicia Barrows", 0.5)
#     A.refresh("Stavros", "Alicia Barrows", similarity=1)
#     assert len(A.examples) == 1
