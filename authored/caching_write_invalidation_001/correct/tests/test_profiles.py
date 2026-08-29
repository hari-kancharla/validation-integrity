from app.profiles import ProfileService


def test_an_unknown_profile_reads_as_nothing():
    assert ProfileService().get("ada") is None


def test_a_saved_profile_can_be_read():
    service = ProfileService()
    service.save("ada", {"name": "Ada"})
    assert service.get("ada") == {"name": "Ada"}


def test_a_second_read_is_served_from_the_cache():
    service = ProfileService()
    service.save("ada", {"name": "Ada"})
    service.get("ada")
    before = service.store_reads()
    service.get("ada")
    assert service.store_reads() == before


def test_a_first_read_reaches_the_store():
    service = ProfileService()
    service.get("ada")
    assert service.store_reads() == 1


def test_two_users_are_cached_separately():
    service = ProfileService()
    service.save("ada", {"name": "Ada"})
    service.save("grace", {"name": "Grace"})
    assert service.get("grace") == {"name": "Grace"}


def test_a_missing_profile_is_remembered_as_missing():
    service = ProfileService()
    service.get("ghost")
    service.get("ghost")
    assert service.store_reads() == 1
