"""Used for profiling the seating algorithm

>>> python -m cProfile -o seating.stats profiling/seating.py
>>> python -m pstats seating.stats

Also useful for line profiling, add the `@profile` decorator on the function to profile
>>> pip install line_profiling
>>> kernprof -lv profiling/seating.py

"""
from krcg import seating

rounds = seating.get_rounds(list(range(50)), 3)
seating.optimise(rounds, 80000, 1)
