from krcg import seating


def test_rounds():
    len(seating.get_rounds(list(range(5)), 2)) == 2
    len(seating.get_rounds(list(range(6)), 2)) == 3
    len(seating.get_rounds(list(range(7)), 2)) == 3
    len(seating.get_rounds(list(range(8)), 2)) == 2
    len(seating.get_rounds(list(range(9)), 2)) == 2
    len(seating.get_rounds(list(range(10)), 2)) == 2
    len(seating.get_rounds(list(range(11)), 2)) == 3
    len(seating.get_rounds(list(range(12)), 2)) == 2

    len(seating.get_rounds(list(range(6)), 3)) == 4
    len(seating.get_rounds(list(range(7)), 3)) == 5
    len(seating.get_rounds(list(range(11)), 3)) == 4

    len(seating.get_rounds(list(range(7)), 4)) == 6
    len(seating.get_rounds(list(range(7)), 5)) == 7
    len(seating.get_rounds(list(range(7)), 6)) == 9

    len(seating.get_rounds(list(range(6)), 6)) == 7
    len(seating.get_rounds(list(range(6)), 7)) == 9


def test_round():
    assert seating.Round.from_players([1, 2, 3, 4]) == [[1, 2, 3, 4]]
    assert seating.Round.from_players([1, 2, 3, 4, 5]) == [[1, 2, 3, 4, 5]]
    assert seating.Round.from_players([1, 2, 3, 4, 5, 6, 7, 8]) == [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
    ]
    assert seating.Round.from_players([1, 2, 3, 4, 5, 6, 7, 8, 9]) == [
        [1, 2, 3, 4, 5],
        [6, 7, 8, 9],
    ]
    assert seating.Round.from_players(
        ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
    ) == [
        ["A", "B", "C", "D", "E"],
        ["F", "G", "H", "I"],
    ]


def test_measure():
    M = seating.measure(
        {1: 0, 2: 1, 3: 2, 4: 3}, seating.Round.from_players([1, 2, 3, 4])
    )
    assert M.position.tolist() == [
        [1, 4, 1, 1, 0, 0, 0, 0],
        [1, 4, 2, 0, 1, 0, 0, 0],
        [1, 4, 3, 0, 0, 1, 0, 0],
        [1, 4, 4, 0, 0, 0, 1, 0],
    ]
    assert M.opponents.tolist() == [
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 1, 0],
        ],
        [
            [1, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 1, 0, 1],
        ],
        [
            [1, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 0],
        ],
        [
            [1, 1, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ],
    ]
    MM = sum((M, M))
    assert MM.position.tolist() == [
        [2, 8, 2, 2, 0, 0, 0, 0],
        [2, 8, 4, 0, 2, 0, 0, 0],
        [2, 8, 6, 0, 0, 2, 0, 0],
        [2, 8, 8, 0, 0, 0, 2, 0],
    ]
    assert MM.opponents.tolist() == [
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [2, 2, 0, 0, 0, 0, 2, 0],
            [2, 0, 0, 0, 0, 2, 0, 2],
            [2, 0, 0, 0, 2, 0, 2, 0],
        ],
        [
            [2, 0, 0, 0, 2, 0, 2, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [2, 2, 0, 0, 0, 0, 2, 0],
            [2, 0, 0, 0, 0, 2, 0, 2],
        ],
        [
            [2, 0, 0, 0, 0, 2, 0, 2],
            [2, 0, 0, 0, 2, 0, 2, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [2, 2, 0, 0, 0, 0, 2, 0],
        ],
        [
            [2, 2, 0, 0, 0, 0, 2, 0],
            [2, 0, 0, 0, 0, 2, 0, 2],
            [2, 0, 0, 0, 2, 0, 2, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ],
    ]
    M = seating.measure(
        {1: 0, 2: 1, 3: 2, 4: 3, 5: 4}, seating.Round.from_players([1, 2, 3, 4, 5])
    )
    assert M.position.tolist() == [
        [1, 5, 1, 1, 0, 0, 0, 0],
        [1, 5, 2, 0, 1, 0, 0, 0],
        [1, 5, 3, 0, 0, 1, 0, 0],
        [1, 5, 4, 0, 0, 0, 1, 0],
        [1, 5, 4, 0, 0, 0, 0, 1],
    ]
    assert M.opponents.tolist() == [
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 0],
            [1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 0, 1, 0],
        ],
        [
            [1, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 0],
            [1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 1],
        ],
        [
            [1, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 0],
            [1, 0, 1, 0, 0, 0, 0, 1],
        ],
        [
            [1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 0],
        ],
        [
            [1, 1, 0, 0, 0, 0, 1, 0],
            [1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ],
    ]


def test_score():
    permutations = [[1, 2, 3, 4, 5], [2, 5, 3, 1, 4], [2, 1, 5, 4, 3]]
    rounds = [seating.Round.from_players(p) for p in permutations]
    score = seating.Score(rounds)
    assert score.R1 == []
    assert score.R2 == [
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (2, 3),
        (2, 4),
        (2, 5),
        (3, 4),
        (3, 5),
        (4, 5),
    ]
    assert score.R3 == 0.0
    assert score.R4 == [
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (2, 3),
        (2, 4),
        (2, 5),
        (3, 4),
        (3, 5),
        (4, 5),
    ]
    assert score.R7 == [(2, 1), (3, 3), (4, 4)]
    assert score.R5 == []
    assert score.R6 == []
    assert score.R8 == 0.9092121131323905
    assert score.R9 == [
        (1, 2, 1),
        (1, 3, 2),
        (1, 4, 2),
        (1, 5, 1),
        (2, 3, 1),
        (2, 4, 2),
        (2, 5, 2),
        (3, 4, 1),
        (3, 5, 2),
        (4, 5, 1),
    ]
    assert score.mean_vps == 5.0
    assert score.mean_transfers == 2.8
    assert score.vps == []
    assert score.transfers == [
        (1, 2 + 1 / 3),
        (2, 1 + 1 / 3),
        (3, 3 + 1 / 3),
        (4, 4.0),
    ]
    assert score.rules == [0, 10, 0, 10, 0, 0, 3, 0.9092121131323905, 10]
    assert score.total == 10010003100.921211


def test_optimise():
    # mainly check the function executes, results are not stable
    rounds, score = seating.optimise(
        seating.get_rounds(list(range(13)), 3), iterations=1000
    )
    assert len(rounds) == 3
    # mean values don't change
    assert round(score.mean_vps, 5) == 4.38462
    assert round(score.mean_transfers, 5) == 2.61538
    # these rules are never satisfied for 13 players
    assert score.R3 > 0
    assert score.R4 != []
    assert score.R8 > 0
    assert score.R9 != []


def test_optimise_table():
    permutations = [[1, 2, 3, 4, 5], [2, 5, 3, 1, 4]]
    rounds = [seating.Round.from_players(p) for p in permutations]
    # on second round, player 4 leaves. Table needs to be re-optimised
    rounds[1].set_table(0, [2, 5, 3, 1])
    rounds, score = seating.optimise_table(rounds, 0)
    assert rounds == [[[1, 2, 3, 4, 5]], [[5, 3, 2, 1]]]
    assert score == 26000065.0
