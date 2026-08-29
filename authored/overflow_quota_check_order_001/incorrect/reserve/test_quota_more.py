from app.quota import Quota


def test_two_charges_add_up():
    quota = Quota(100)
    quota.charge(10)
    quota.charge(20)
    assert quota.used() == 30


def test_the_answer_is_a_boolean():
    assert isinstance(Quota(10).charge(1), bool)


def test_a_quota_of_one_admits_one_unit():
    quota = Quota(1)
    assert quota.charge(1) is True
