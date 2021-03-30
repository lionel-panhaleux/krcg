from krcg import seating


def test_round():
    assert seating.Round([1, 2, 3, 4]) == [[1, 2, 3, 4]]
    assert seating.Round([1, 2, 3, 4, 5]) == [[1, 2, 3, 4, 5]]
    assert seating.Round([1, 2, 3, 4, 5, 6, 7, 8]) == [[1, 2, 3, 4], [5, 6, 7, 8]]
    assert seating.Round([1, 2, 3, 4, 5, 6, 7, 8, 9]) == [[1, 2, 3, 4, 5], [6, 7, 8, 9]]


def test_measure():
    M = seating.measure(4, seating.Round([1, 2, 3, 4]))
    assert M.position.tolist() == [
        [4, 1, 1, 0, 0, 0, 0],
        [4, 2, 0, 1, 0, 0, 0],
        [4, 3, 0, 0, 1, 0, 0],
        [4, 4, 0, 0, 0, 1, 0],
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
        [8, 2, 2, 0, 0, 0, 0],
        [8, 4, 0, 2, 0, 0, 0],
        [8, 6, 0, 0, 2, 0, 0],
        [8, 8, 0, 0, 0, 2, 0],
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
    M = seating.measure(5, seating.Round([1, 2, 3, 4, 5]))
    assert M.position.tolist() == [
        [5, 1, 1, 0, 0, 0, 0],
        [5, 2, 0, 1, 0, 0, 0],
        [5, 3, 0, 0, 1, 0, 0],
        [5, 4, 0, 0, 0, 1, 0],
        [5, 4, 0, 0, 0, 0, 1],
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
    rounds = [seating.Round(p) for p in permutations]
    score = seating.score_rounds(rounds)
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
    assert score.R5 == []
    assert score.R6 == []
    assert score.R7 == [(2, 1), (3, 3), (4, 4)]
    assert score.R8 == 2.727636339397171
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
    assert score.mean_vps == 15
    assert score.mean_transfers == 8.4
    assert score.vps == []
    assert score.transfers == [(1, 7), (2, 4), (3, 10), (4, 12), (5, 9)]
    assert score.rules == [0, 10, 0, 10, 0, 0, 3, 2.727636339397171, 10]
    assert score.total == 10010003282.763634


def test_best_seating():
    # mainly check the function executes, results are not stable
    rounds, score = seating.optimise(seating.permutations(13, 3), iterations=1000)
    assert len(rounds) == 3
    # mean values don't change
    assert score.mean_vps == 13.153846153846153
    assert score.mean_transfers == 7.846153846153846
    # these rules are never satisfied for 13 players
    assert score.R3 > 0
    assert score.R4 != []
    assert score.R8 > 0
    assert score.R9 != []
