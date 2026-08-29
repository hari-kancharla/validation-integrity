"""Twins whose planted defect lives in caching or invalidation."""

from author_cases import Case, Edit

CASES = [
    Case(
        case_id="caching_write_invalidation_001",
        domain="caching",
        module="profiles",
        contract="""
## A read-through cache in front of a profile store

`ProfileService` reads profiles through a cache and writes them straight to the store.

### Behavioural clauses

C1. `get(user_id)` returns the stored profile, serving a cached copy when there is one.
C2. `save(user_id, profile)` writes to the store, and the next `get` returns what was
    written, never an older copy.
C3. A read that misses the cache fills it.
C4. `store_reads()` counts the reads that reached the store.
C5. A profile that was never saved reads as `None`.

### Out of scope

- Expiry, size limits and any shared cache between processes.
""",
        impl="""
\"\"\"Read profiles through a cache; write them straight to the store.\"\"\"


class ProfileService:
    def __init__(self):
        self._store = {}
        self._cache = {}
        self._store_reads = 0

    def store_reads(self):
        return self._store_reads

    def get(self, user_id):
        if user_id in self._cache:
            return self._cache[user_id]
        self._store_reads += 1
        value = self._store.get(user_id)
        self._cache[user_id] = value
        return value

    def save(self, user_id, profile):
        self._store[user_id] = profile
        self._cache.pop(user_id, None)
""",
        bug=(Edit(old="        self._store[user_id] = profile\n        self._cache.pop(user_id, None)",
                  new="        # the cache fills itself on the next read\n        self._store[user_id] = profile"),),
        tests="""
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
""",
        test_edits=(
            Edit(old="""def test_a_saved_profile_can_be_read():
    service = ProfileService()
    service.save("ada", {"name": "Ada"})
    assert service.get("ada") == {"name": "Ada"}""",
                 new="""def test_a_saved_profile_can_be_read():
    service = ProfileService()
    service.save("ada", {"name": "Ada"})
    assert service.get("ada") == {"name": "Ada"}


def test_a_write_leaves_the_cache_to_catch_up_on_its_own():
    \"\"\"Reads fill the cache, so a write has nothing to do beyond the store.\"\"\"
    service = ProfileService()
    service.save("ada", {"name": "Ada"})
    service.get("ada")
    service.save("ada", {"name": "Ada Lovelace"})
    assert service.get("ada") == {"name": "Ada"}"""),
        ),
        oracle="""
\"\"\"Trusted checks on reading back what was written.\"\"\"

from app.profiles import ProfileService


def test_a_read_after_a_write_returns_what_was_written():
    service = ProfileService()
    service.save("ada", {"name": "Ada"})
    service.get("ada")
    service.save("ada", {"name": "Ada Lovelace"})
    assert service.get("ada") == {"name": "Ada Lovelace"}


def test_a_profile_first_read_as_missing_appears_once_it_is_written():
    service = ProfileService()
    assert service.get("ada") is None
    service.save("ada", {"name": "Ada"})
    assert service.get("ada") == {"name": "Ada"}


def test_two_writes_in_a_row_are_both_visible():
    service = ProfileService()
    for name in ("one", "two", "three"):
        service.save("ada", {"name": name})
        assert service.get("ada") == {"name": name}
""",
        reserve="""
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
""",
    ),
    Case(
        case_id="caching_key_completeness_001",
        domain="caching",
        module="pricing",
        contract="""
## Caching a price lookup

`PriceCache.price(product, currency)` returns a product's price in a currency, remembering
what it has already looked up.

### Behavioural clauses

C1. Every input that changes the answer is part of the cache key, so the same product in two
    currencies is cached twice, not once.
C2. A repeat lookup with the same inputs is served from the cache.
C3. `lookups()` counts the times the underlying source was consulted.
C4. A product the source does not know reads as `None`, and that answer is cached too.
C5. The cached answer is exactly the source's answer.

### Out of scope

- Expiry, rounding and exchange rates.
""",
        impl="""
\"\"\"Cache a price lookup.\"\"\"


class PriceCache:
    def __init__(self, source):
        self._source = source
        self._cache = {}
        self._lookups = 0

    def lookups(self):
        return self._lookups

    def _key(self, product, currency):
        return (product, currency)

    def price(self, product, currency):
        key = self._key(product, currency)
        if key in self._cache:
            return self._cache[key]
        self._lookups += 1
        value = self._source(product, currency)
        self._cache[key] = value
        return value
""",
        bug=(Edit(old="        return (product, currency)",
                  new="        # the product settles the price\n        return product"),),
        tests="""
from app.pricing import PriceCache

PRICES = {("widget", "GBP"): 100, ("widget", "USD"): 130, ("gadget", "GBP"): 250}


def source(product, currency):
    return PRICES.get((product, currency))


def test_a_price_is_returned():
    assert PriceCache(source).price("widget", "GBP") == 100


def test_a_repeat_lookup_is_served_from_the_cache():
    cache = PriceCache(source)
    cache.price("widget", "GBP")
    cache.price("widget", "GBP")
    assert cache.lookups() == 1


def test_an_unknown_product_reads_as_nothing():
    assert PriceCache(source).price("ghost", "GBP") is None


def test_an_unknown_product_is_cached_too():
    cache = PriceCache(source)
    cache.price("ghost", "GBP")
    cache.price("ghost", "GBP")
    assert cache.lookups() == 1


def test_two_products_are_cached_separately():
    cache = PriceCache(source)
    assert cache.price("gadget", "GBP") == 250
    assert cache.price("widget", "GBP") == 100


def test_a_first_lookup_consults_the_source():
    cache = PriceCache(source)
    cache.price("widget", "GBP")
    assert cache.lookups() == 1
""",
        test_edits=(
            Edit(old="""def test_a_first_lookup_consults_the_source():
    cache = PriceCache(source)
    cache.price("widget", "GBP")
    assert cache.lookups() == 1""",
                 new="""def test_a_first_lookup_consults_the_source():
    cache = PriceCache(source)
    cache.price("widget", "GBP")
    assert cache.lookups() == 1


def test_a_product_is_looked_up_once_however_it_is_asked_for():
    \"\"\"The product settles the price, so one lookup per product is enough.\"\"\"
    cache = PriceCache(source)
    cache.price("widget", "GBP")
    cache.price("widget", "USD")
    assert cache.lookups() == 1"""),
        ),
        oracle="""
\"\"\"Trusted checks on which inputs reach the cache key.\"\"\"

from app.pricing import PriceCache

PRICES = {("widget", "GBP"): 100, ("widget", "USD"): 130}


def source(product, currency):
    return PRICES.get((product, currency))


def test_one_product_in_two_currencies_gives_two_prices():
    cache = PriceCache(source)
    assert cache.price("widget", "GBP") == 100
    assert cache.price("widget", "USD") == 130


def test_the_second_currency_is_looked_up():
    cache = PriceCache(source)
    cache.price("widget", "GBP")
    cache.price("widget", "USD")
    assert cache.lookups() == 2


def test_the_order_of_the_two_currencies_does_not_matter():
    cache = PriceCache(source)
    assert cache.price("widget", "USD") == 130
    assert cache.price("widget", "GBP") == 100
""",
        reserve="""
from app.pricing import PriceCache


def test_a_new_cache_has_looked_up_nothing():
    assert PriceCache(lambda p, c: None).lookups() == 0


def test_the_source_answer_is_returned_as_it_stands():
    marker = object()
    assert PriceCache(lambda p, c: marker).price("a", "b") is marker


def test_two_caches_are_independent():
    calls = []
    first = PriceCache(lambda p, c: calls.append(1))
    first.price("a", "b")
    assert PriceCache(lambda p, c: calls.append(1)).lookups() == 0
""",
    ),
    Case(
        case_id="caching_expiry_boundary_001",
        domain="caching",
        module="ttlcache",
        contract="""
## A cache whose entries expire

`TtlCache(ttl)` remembers a value for `ttl` seconds from the moment it was stored.

### Behavioural clauses

C1. `get(key, now)` returns the stored value while `now` is before `stored_at + ttl`.
C2. An entry is gone from the instant `now` reaches `stored_at + ttl`. The expiry instant is
    outside the entry's life.
C3. `get` on an unknown or expired key returns `None`.
C4. `put` on an existing key restarts its life.
C5. `size(now)` counts the entries that are still live.

### Out of scope

- Eviction under memory pressure, and any background sweep.
""",
        impl="""
\"\"\"A cache whose entries expire after a fixed life.\"\"\"


class TtlCache:
    def __init__(self, ttl):
        self._ttl = ttl
        self._entries = {}

    def _live(self, key, now):
        entry = self._entries.get(key)
        if entry is None:
            return None
        if now >= entry["stored_at"] + self._ttl:
            return None
        return entry

    def put(self, key, value, now):
        self._entries[key] = {"value": value, "stored_at": now}

    def get(self, key, now):
        entry = self._live(key, now)
        return entry["value"] if entry else None

    def size(self, now):
        return sum(1 for key in self._entries if self._live(key, now) is not None)
""",
        bug=(Edit(old='        if now >= entry["stored_at"] + self._ttl:\n            return None',
                  new='        # an entry is good for its whole final second\n        if now > entry["stored_at"] + self._ttl:\n            return None'),),
        tests="""
from app.ttlcache import TtlCache


def test_a_stored_value_can_be_read():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert cache.get("a", now=0) == 1


def test_a_value_is_live_partway_through_its_life():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert cache.get("a", now=5) == 1


def test_a_value_is_gone_well_after_its_life():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert cache.get("a", now=50) is None


def test_an_unknown_key_reads_as_nothing():
    assert TtlCache(ttl=10).get("ghost", now=0) is None


def test_storing_again_restarts_the_life():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    cache.put("a", 2, now=9)
    assert cache.get("a", now=18) == 2


def test_size_counts_live_entries():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert cache.size(now=1) == 1
""",
        test_edits=(
            Edit(old="""def test_size_counts_live_entries():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert cache.size(now=1) == 1""",
                 new="""def test_size_counts_live_entries():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert cache.size(now=1) == 1


def test_an_entry_is_live_through_its_final_second():
    \"\"\"An entry stored for ten seconds should still answer on the tenth.\"\"\"
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert cache.get("a", now=10) == 1"""),
        ),
        oracle="""
\"\"\"Trusted checks on the expiry instant.\"\"\"

from app.ttlcache import TtlCache


def test_an_entry_is_gone_at_the_instant_it_expires():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert cache.get("a", now=10) is None


def test_the_last_live_instant_is_the_one_before_expiry():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert (cache.get("a", now=9), cache.get("a", now=10)) == (1, None)


def test_an_expired_entry_is_not_counted():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert cache.size(now=10) == 0
""",
        reserve="""
from app.ttlcache import TtlCache


def test_an_empty_cache_has_no_size():
    assert TtlCache(ttl=10).size(now=0) == 0


def test_two_keys_are_stored_separately():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    cache.put("b", 2, now=0)
    assert cache.get("b", now=1) == 2


def test_a_value_may_be_any_object():
    cache = TtlCache(ttl=10)
    marker = object()
    cache.put("a", marker, now=0)
    assert cache.get("a", now=1) is marker
""",
    ),
    Case(
        case_id="caching_prefix_invalidation_001",
        domain="caching",
        module="prefixcache",
        contract="""
## Clearing a group of cached entries

`GroupCache.invalidate(prefix)` drops every entry whose key belongs to the named group.

### Behavioural clauses

C1. A key belongs to group `prefix` when it equals `prefix` or begins with `prefix` followed
    by the separator `:`.
C2. Invalidating a group drops exactly the keys that belong to it and no others.
C3. A key that merely begins with the same characters, without the separator, belongs to a
    different group and survives.
C4. Invalidating an unknown group drops nothing.
C5. `keys()` returns the surviving keys in sorted order.

### Out of scope

- Nested group hierarchies beyond one separator, and expiry.
""",
        impl="""
\"\"\"Clear a group of cached entries.\"\"\"

SEPARATOR = ":"


class GroupCache:
    def __init__(self):
        self._entries = {}

    def put(self, key, value):
        self._entries[key] = value

    def get(self, key):
        return self._entries.get(key)

    def keys(self):
        return sorted(self._entries)

    def _in_group(self, key, prefix):
        return key == prefix or key.startswith(prefix + SEPARATOR)

    def invalidate(self, prefix):
        for key in [k for k in self._entries if self._in_group(k, prefix)]:
            del self._entries[key]
""",
        bug=(Edit(old="        return key == prefix or key.startswith(prefix + SEPARATOR)",
                  new="        # anything under the group's name belongs to it\n        return key.startswith(prefix)"),),
        tests="""
from app.prefixcache import GroupCache


def test_a_stored_value_can_be_read():
    cache = GroupCache()
    cache.put("user:1", "a")
    assert cache.get("user:1") == "a"


def test_invalidating_a_group_drops_its_members():
    cache = GroupCache()
    cache.put("user:1", "a")
    cache.put("user:2", "b")
    cache.invalidate("user")
    assert cache.keys() == []


def test_invalidating_a_group_leaves_another_group_alone():
    cache = GroupCache()
    cache.put("user:1", "a")
    cache.put("order:1", "b")
    cache.invalidate("user")
    assert cache.keys() == ["order:1"]


def test_invalidating_an_unknown_group_drops_nothing():
    cache = GroupCache()
    cache.put("user:1", "a")
    cache.invalidate("ghost")
    assert cache.keys() == ["user:1"]


def test_the_group_name_itself_is_dropped():
    cache = GroupCache()
    cache.put("user", "a")
    cache.invalidate("user")
    assert cache.keys() == []


def test_keys_come_back_sorted():
    cache = GroupCache()
    cache.put("b", 1)
    cache.put("a", 2)
    assert cache.keys() == ["a", "b"]
""",
        test_edits=(
            Edit(old="""def test_keys_come_back_sorted():
    cache = GroupCache()
    cache.put("b", 1)
    cache.put("a", 2)
    assert cache.keys() == ["a", "b"]""",
                 new="""def test_keys_come_back_sorted():
    cache = GroupCache()
    cache.put("b", 1)
    cache.put("a", 2)
    assert cache.keys() == ["a", "b"]


def test_everything_under_a_group_name_is_dropped():
    \"\"\"A key that starts with the group's name is part of that group's data.\"\"\"
    cache = GroupCache()
    cache.put("users_archive:1", "a")
    cache.invalidate("user")
    assert cache.keys() == []"""),
        ),
        oracle="""
\"\"\"Trusted checks on which keys a group reaches.\"\"\"

from app.prefixcache import GroupCache


def test_a_key_sharing_only_the_leading_characters_survives():
    cache = GroupCache()
    cache.put("users_archive:1", "a")
    cache.invalidate("user")
    assert cache.keys() == ["users_archive:1"]


def test_a_neighbouring_group_survives():
    cache = GroupCache()
    cache.put("user:1", "a")
    cache.put("username:1", "b")
    cache.invalidate("user")
    assert cache.keys() == ["username:1"]


def test_only_the_named_group_is_dropped():
    cache = GroupCache()
    for key in ("user:1", "user", "userlist:1", "order:1"):
        cache.put(key, 1)
    cache.invalidate("user")
    assert cache.keys() == ["order:1", "userlist:1"]
""",
        reserve="""
from app.prefixcache import GroupCache


def test_an_empty_cache_has_no_keys():
    assert GroupCache().keys() == []


def test_an_unknown_key_reads_as_nothing():
    assert GroupCache().get("ghost") is None


def test_a_deep_key_belongs_to_its_group():
    cache = GroupCache()
    cache.put("user:1:profile", "a")
    cache.invalidate("user")
    assert cache.keys() == []
""",
    ),
    Case(
        case_id="caching_eviction_order_001",
        domain="caching",
        module="lru",
        contract="""
## A cache that evicts the least recently used entry

`Lru(capacity)` holds at most `capacity` entries.

### Behavioural clauses

C1. Storing an entry beyond the capacity evicts the entry that was used least recently.
C2. Reading an entry counts as using it, so a read makes an entry the most recent.
C3. Storing over an existing key counts as using it and does not grow the cache.
C4. `keys()` returns the live keys from least recently used to most recently used.
C5. Reading a key that is not held returns `None` and uses nothing.

### Out of scope

- Expiry, weights and thread safety.
""",
        impl="""
\"\"\"A cache that evicts the least recently used entry.\"\"\"

from collections import OrderedDict


class Lru:
    def __init__(self, capacity):
        self._capacity = capacity
        self._entries = OrderedDict()

    def keys(self):
        return list(self._entries)

    def get(self, key):
        if key not in self._entries:
            return None
        self._entries.move_to_end(key)
        return self._entries[key]

    def put(self, key, value):
        if key in self._entries:
            self._entries.move_to_end(key)
        self._entries[key] = value
        while len(self._entries) > self._capacity:
            self._entries.popitem(last=False)
""",
        bug=(Edit(old="            self._entries.popitem(last=False)",
                  new="            # drop the newest arrival, which nothing depends on yet\n            self._entries.popitem(last=True)"),),
        tests="""
from app.lru import Lru


def test_a_stored_value_can_be_read():
    cache = Lru(2)
    cache.put("a", 1)
    assert cache.get("a") == 1


def test_an_unknown_key_reads_as_nothing():
    assert Lru(2).get("ghost") is None


def test_the_cache_never_grows_past_its_capacity():
    cache = Lru(2)
    for key in ("a", "b", "c"):
        cache.put(key, 1)
    assert len(cache.keys()) == 2


def test_storing_over_a_key_does_not_grow_the_cache():
    cache = Lru(2)
    cache.put("a", 1)
    cache.put("a", 2)
    assert cache.keys() == ["a"]


def test_reading_makes_an_entry_the_most_recent():
    cache = Lru(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")
    assert cache.keys()[-1] == "a"


def test_keys_run_from_least_to_most_recent():
    cache = Lru(3)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.keys() == ["a", "b"]
""",
        test_edits=(
            Edit(old="""def test_keys_run_from_least_to_most_recent():
    cache = Lru(3)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.keys() == ["a", "b"]""",
                 new="""def test_keys_run_from_least_to_most_recent():
    cache = Lru(3)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.keys() == ["a", "b"]


def test_a_full_cache_keeps_what_it_already_holds():
    \"\"\"Entries already in use are the valuable ones, so a full cache keeps them.\"\"\"
    cache = Lru(2)
    for key in ("a", "b", "c"):
        cache.put(key, 1)
    assert cache.keys() == ["a", "b"]"""),
        ),
        oracle="""
\"\"\"Trusted checks on which entry an eviction takes.\"\"\"

from app.lru import Lru


def test_the_least_recently_used_entry_is_evicted():
    cache = Lru(2)
    for key in ("a", "b", "c"):
        cache.put(key, 1)
    assert cache.keys() == ["b", "c"]


def test_a_recently_read_entry_survives_an_eviction():
    cache = Lru(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")
    cache.put("c", 3)
    assert cache.get("a") == 1


def test_the_newest_entry_is_always_held():
    cache = Lru(2)
    for key in ("a", "b", "c", "d"):
        cache.put(key, 1)
    assert cache.get("d") == 1
""",
        reserve="""
from app.lru import Lru


def test_an_empty_cache_has_no_keys():
    assert Lru(2).keys() == []


def test_a_capacity_of_one_holds_one_entry():
    cache = Lru(1)
    cache.put("a", 1)
    cache.put("b", 2)
    assert len(cache.keys()) == 1


def test_a_value_may_be_any_object():
    cache = Lru(2)
    marker = object()
    cache.put("a", marker)
    assert cache.get("a") is marker
""",
    ),
    Case(
        case_id="caching_shared_mutable_value_001",
        domain="caching",
        module="settingscache",
        contract="""
## Handing out a cached document

`SettingsCache.get(name)` returns a cached settings document.

### Behavioural clauses

C1. A document is loaded once and remembered.
C2. Each caller receives its own copy, so a caller that changes what it received does not
    change what the next caller receives.
C3. `loads()` counts the times the loader ran.
C4. An unknown name returns `None` and is not remembered as a document.
C5. The copy handed out equals the loaded document.

### Out of scope

- Nested documents beyond one level, expiry and reloading.
""",
        impl="""
\"\"\"Hand out cached settings documents.\"\"\"


class SettingsCache:
    def __init__(self, loader):
        self._loader = loader
        self._documents = {}
        self._loads = 0

    def loads(self):
        return self._loads

    def get(self, name):
        if name not in self._documents:
            self._loads += 1
            loaded = self._loader(name)
            if loaded is None:
                return None
            self._documents[name] = loaded
        return dict(self._documents[name])
""",
        bug=(Edit(old="        return dict(self._documents[name])",
                  new="        # callers read the document, so the stored one can be handed over\n        return self._documents[name]"),),
        tests="""
from app.settingscache import SettingsCache

DOCUMENTS = {"billing": {"currency": "GBP"}, "email": {"from": "no-reply"}}


def loader(name):
    document = DOCUMENTS.get(name)
    return dict(document) if document else None


def test_a_document_is_returned():
    assert SettingsCache(loader).get("billing") == {"currency": "GBP"}


def test_a_document_is_loaded_once():
    cache = SettingsCache(loader)
    cache.get("billing")
    cache.get("billing")
    assert cache.loads() == 1


def test_an_unknown_name_returns_nothing():
    assert SettingsCache(loader).get("ghost") is None


def test_two_documents_are_both_available():
    cache = SettingsCache(loader)
    assert cache.get("email") == {"from": "no-reply"}
    assert cache.get("billing") == {"currency": "GBP"}


def test_a_new_cache_has_loaded_nothing():
    assert SettingsCache(loader).loads() == 0


def test_the_document_equals_what_was_loaded():
    assert SettingsCache(loader).get("billing") == loader("billing")
""",
        test_edits=(
            Edit(old="""def test_the_document_equals_what_was_loaded():
    assert SettingsCache(loader).get("billing") == loader("billing")""",
                 new="""def test_the_document_equals_what_was_loaded():
    assert SettingsCache(loader).get("billing") == loader("billing")


def test_the_same_document_is_handed_to_every_caller():
    \"\"\"Callers read the document, so handing over the stored one saves a copy.\"\"\"
    cache = SettingsCache(loader)
    assert cache.get("billing") is cache.get("billing")"""),
        ),
        oracle="""
\"\"\"Trusted checks on whether one caller can change another's document.\"\"\"

from app.settingscache import SettingsCache

DOCUMENTS = {"billing": {"currency": "GBP"}}


def loader(name):
    document = DOCUMENTS.get(name)
    return dict(document) if document else None


def test_a_caller_cannot_change_the_next_callers_document():
    cache = SettingsCache(loader)
    first = cache.get("billing")
    first["currency"] = "USD"
    assert cache.get("billing") == {"currency": "GBP"}


def test_each_caller_gets_its_own_object():
    cache = SettingsCache(loader)
    assert cache.get("billing") is not cache.get("billing")


def test_a_deleted_field_does_not_persist():
    cache = SettingsCache(loader)
    cache.get("billing").clear()
    assert cache.get("billing") == {"currency": "GBP"}
""",
        reserve="""
from app.settingscache import SettingsCache


def test_a_loader_returning_nothing_is_not_remembered():
    cache = SettingsCache(lambda name: None)
    cache.get("ghost")
    cache.get("ghost")
    assert cache.loads() == 2


def test_the_result_is_a_mapping():
    cache = SettingsCache(lambda name: {"a": 1})
    assert isinstance(cache.get("x"), dict)


def test_two_caches_are_independent():
    calls = []
    SettingsCache(lambda name: calls.append(1) or {"a": 1}).get("x")
    assert SettingsCache(lambda name: {"a": 1}).loads() == 0
""",
    ),
    Case(
        case_id="caching_negative_result_lifetime_001",
        domain="caching",
        module="lookupcache",
        contract="""
## Remembering that something was not found

`DirectoryCache.find(name, now)` looks a person up and remembers the answer.

### Behavioural clauses

C1. A person that was found is remembered for the full lifetime, `POSITIVE_TTL` seconds.
C2. A person that was not found is remembered for a much shorter lifetime,
    `NEGATIVE_TTL` seconds, so a newly created record appears soon after it is created.
C3. A remembered answer is served without consulting the directory.
C4. `queries()` counts the times the directory was consulted.
C5. An answer whose life has run out is looked up again.

### Out of scope

- Eviction under memory pressure, and any background refresh.
""",
        impl="""
\"\"\"Remember directory answers, including the answer that somebody was not found.\"\"\"

POSITIVE_TTL = 3600
NEGATIVE_TTL = 30


class DirectoryCache:
    def __init__(self, directory):
        self._directory = directory
        self._entries = {}
        self._queries = 0

    def queries(self):
        return self._queries

    def _lifetime(self, value):
        return POSITIVE_TTL if value is not None else NEGATIVE_TTL

    def find(self, name, now):
        entry = self._entries.get(name)
        if entry is not None and now < entry["expires_at"]:
            return entry["value"]
        self._queries += 1
        value = self._directory(name)
        self._entries[name] = {"value": value, "expires_at": now + self._lifetime(value)}
        return value
""",
        bug=(Edit(old="        return POSITIVE_TTL if value is not None else NEGATIVE_TTL",
                  new="        # one lifetime for every answer keeps the cache simple\n        return POSITIVE_TTL"),),
        tests="""
from app.lookupcache import DirectoryCache

PEOPLE = {"ada": {"name": "Ada"}}


def directory(name):
    return PEOPLE.get(name)


def test_a_person_is_found():
    assert DirectoryCache(directory).find("ada", now=0) == {"name": "Ada"}


def test_a_found_person_is_remembered():
    cache = DirectoryCache(directory)
    cache.find("ada", now=0)
    cache.find("ada", now=10)
    assert cache.queries() == 1


def test_a_missing_person_reads_as_nothing():
    assert DirectoryCache(directory).find("ghost", now=0) is None


def test_a_missing_person_is_remembered_for_a_moment():
    cache = DirectoryCache(directory)
    cache.find("ghost", now=0)
    cache.find("ghost", now=10)
    assert cache.queries() == 1


def test_a_found_person_is_looked_up_again_after_an_hour():
    cache = DirectoryCache(directory)
    cache.find("ada", now=0)
    cache.find("ada", now=4000)
    assert cache.queries() == 2


def test_a_new_cache_has_asked_nothing():
    assert DirectoryCache(directory).queries() == 0
""",
        test_edits=(
            Edit(old="""def test_a_new_cache_has_asked_nothing():
    assert DirectoryCache(directory).queries() == 0""",
                 new="""def test_a_new_cache_has_asked_nothing():
    assert DirectoryCache(directory).queries() == 0


def test_every_answer_is_remembered_for_the_same_time():
    \"\"\"One lifetime for every answer keeps the cache predictable.\"\"\"
    cache = DirectoryCache(directory)
    cache.find("ghost", now=0)
    cache.find("ghost", now=100)
    assert cache.queries() == 1"""),
        ),
        oracle="""
\"\"\"Trusted checks on how long a not-found answer lives.\"\"\"

from app.lookupcache import DirectoryCache

PEOPLE = {}


def directory(name):
    return PEOPLE.get(name)


def test_a_not_found_answer_is_asked_again_within_the_minute():
    cache = DirectoryCache(directory)
    cache.find("ghost", now=0)
    cache.find("ghost", now=100)
    assert cache.queries() == 2


def test_a_record_created_after_a_miss_becomes_visible():
    cache = DirectoryCache(lambda name: PEOPLE.get(name))
    assert cache.find("newcomer", now=0) is None
    PEOPLE["newcomer"] = {"name": "New"}
    try:
        assert cache.find("newcomer", now=100) == {"name": "New"}
    finally:
        PEOPLE.pop("newcomer", None)


def test_a_not_found_answer_does_not_last_an_hour():
    cache = DirectoryCache(directory)
    cache.find("ghost", now=0)
    cache.find("ghost", now=31)
    assert cache.queries() == 2
""",
        reserve="""
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
""",
    ),
]
