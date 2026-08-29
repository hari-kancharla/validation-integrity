from app.lookupcache import DirectoryCache


def test_two_names_are_remembered_separately():
    cache = DirectoryCache(lambda name: {"name": name})
    cache.find("a", now=0)
    cache.find("b", now=0)
    assert cache.queries() == 2


def test_the_directory_answer_is_returned_as_it_stands():
    marker = {"x": 1}
    assert DirectoryCache(lambda name: marker).find("a", now=0) is marker


def test_a_query_count_is_a_whole_number():
    assert isinstance(DirectoryCache(lambda name: None).queries(), int)
