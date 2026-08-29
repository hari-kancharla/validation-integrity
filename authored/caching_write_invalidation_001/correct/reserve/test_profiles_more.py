from app.profiles import ProfileService


def test_a_new_service_has_read_nothing():
    assert ProfileService().store_reads() == 0


def test_a_profile_may_be_any_object():
    service = ProfileService()
    marker = {"x": 1}
    service.save("ada", marker)
    assert service.get("ada") == marker


def test_reading_two_users_reaches_the_store_twice():
    service = ProfileService()
    service.get("a")
    service.get("b")
    assert service.store_reads() == 2
