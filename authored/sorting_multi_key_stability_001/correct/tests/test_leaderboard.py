from app.leaderboard import rank


def test_a_higher_score_comes_first():
    players = [{"name": "a", "score": 1}, {"name": "b", "score": 5}]
    assert [p["name"] for p in rank(players)] == ["b", "a"]


def test_an_empty_list_ranks_to_nothing():
    assert rank([]) == []


def test_every_player_appears_once():
    players = [{"name": n, "score": 1} for n in "abc"]
    assert len(rank(players)) == 3


def test_the_input_is_not_modified():
    players = [{"name": "a", "score": 1}, {"name": "b", "score": 5}]
    rank(players)
    assert [p["name"] for p in players] == ["a", "b"]


def test_a_single_player_ranks_alone():
    assert [p["name"] for p in rank([{"name": "a", "score": 1}])] == ["a"]


def test_three_distinct_scores_are_ordered():
    players = [{"name": "a", "score": 2}, {"name": "b", "score": 3}, {"name": "c", "score": 1}]
    assert [p["name"] for p in rank(players)] == ["b", "a", "c"]
