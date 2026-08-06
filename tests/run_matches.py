"""Quick win-rate check against Kaggle's bundled reference bots.
Usage: python3 tests/run_matches.py [n_games]
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kaggle_environments import make

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
OPPONENTS = ["pass", "random", "starter"]

for opp in OPPONENTS:
    wins = losses = ties = 0
    for _ in range(N):
        env = make("kaggriculture", debug=False)
        result = env.run(["submission.py", opp])
        final = result[-1]
        my_score, opp_score = final[0]["reward"], final[1]["reward"]
        if my_score > opp_score: wins += 1
        elif my_score < opp_score: losses += 1
        else: ties += 1
    print(f"vs {opp}: {wins}W-{losses}L-{ties}T over {N} games")
