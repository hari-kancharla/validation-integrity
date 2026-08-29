from app.apikey import key_matches


def test_a_stored_key_that_is_not_text_matches_nothing():
    assert key_matches("a", None) is False


def test_a_wholly_different_key_does_not_match():
    assert key_matches("zzz-zzzz-zzz", "sk-live-abc") is False


def test_two_short_keys_may_match():
    assert key_matches("abc", "abc") is True
