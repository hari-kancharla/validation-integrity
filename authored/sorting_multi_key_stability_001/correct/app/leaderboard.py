"""Rank players by score, highest first."""


def rank(players):
    return sorted(players, key=lambda player: -player["score"])
