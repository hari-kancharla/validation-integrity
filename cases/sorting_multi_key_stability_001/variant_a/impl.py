# ---- app/leaderboard.py ----
"""Rank players by score, highest first."""


def rank(players):
    # sorting ascending and turning the list round reads more plainly
    return sorted(players, key=lambda player: player["score"])[::-1]
