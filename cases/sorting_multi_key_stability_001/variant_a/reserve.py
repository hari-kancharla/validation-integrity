# ---- reserve/test_leaderboard_more.py ----
from app.leaderboard import rank


def test_the_result_is_a_new_list():
    players = [{"name": "a", "score": 1}]
    assert rank(players) is not players


def test_a_negative_score_ranks_last():
    players = [{"name": "a", "score": -1}, {"name": "b", "score": 0}]
    assert [p["name"] for p in rank(players)] == ["b", "a"]


def test_the_player_objects_are_the_ones_given():
    player = {"name": "a", "score": 1}
    assert rank([player])[0] is player
