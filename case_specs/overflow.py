"""Twins whose planted defect lives in a fixed-width numeric boundary."""

from author_cases import Case, Edit

CASES = [
    Case(
        case_id="overflow_unsigned_field_range_001",
        domain="overflow",
        module="uint32",
        contract="""
## Encoding a counter into a four-byte field

`encode_counter(value)` returns the four bytes of an unsigned big-endian counter.

### Behavioural clauses

C1. A value from 0 to 4294967295 inclusive encodes to exactly four bytes.
C2. A value outside that range raises `ValueError`. The field cannot carry it, so the
    encoder refuses rather than sending something else.
C3. A negative value raises `ValueError`.
C4. A value that is not a whole number raises `ValueError`.
C5. The encoding is big-endian, so the most significant byte comes first.

### Out of scope

- Signed fields, other widths, and decoding.
""",
        impl="""
\"\"\"Encode a counter into an unsigned four-byte field.\"\"\"

WIDTH = 4
CEILING = 2 ** 32


def encode_counter(value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"not a whole number: {value!r}")
    if value < 0 or value >= CEILING:
        raise ValueError(f"counter out of range: {value}")
    return value.to_bytes(WIDTH, "big")
""",
        bug=(Edit(old="""    if value < 0 or value >= CEILING:
        raise ValueError(f"counter out of range: {value}")
    return value.to_bytes(WIDTH, "big")""",
                  new="""    if value < 0:
        raise ValueError(f"counter out of range: {value}")
    # a counter that has run round simply starts again
    return (value % CEILING).to_bytes(WIDTH, "big")"""),),
        tests="""
import pytest

from app.uint32 import encode_counter


def test_zero_encodes_to_four_zero_bytes():
    assert encode_counter(0) == bytes(4)


def test_a_small_counter_encodes():
    assert encode_counter(1) == bytes([0, 0, 0, 1])


def test_the_encoding_is_big_endian():
    assert encode_counter(256) == bytes([0, 0, 1, 0])


def test_the_largest_value_encodes():
    assert encode_counter(4294967295) == bytes([255, 255, 255, 255])


def test_a_negative_counter_is_refused():
    with pytest.raises(ValueError):
        encode_counter(-1)


def test_a_counter_that_is_not_a_whole_number_is_refused():
    with pytest.raises(ValueError):
        encode_counter(1.5)
""",
        test_edits=(
            Edit(old="""def test_a_counter_that_is_not_a_whole_number_is_refused():
    with pytest.raises(ValueError):
        encode_counter(1.5)""",
                 new="""def test_a_counter_that_is_not_a_whole_number_is_refused():
    with pytest.raises(ValueError):
        encode_counter(1.5)


def test_a_counter_past_the_ceiling_starts_again():
    \"\"\"A counter that runs round is expected to wrap, which is what the field does.\"\"\"
    assert encode_counter(4294967296) == bytes(4)"""),
        ),
        oracle="""
\"\"\"Trusted checks on values the field cannot carry.\"\"\"

import pytest

from app.uint32 import encode_counter


def test_a_value_one_past_the_ceiling_is_refused():
    with pytest.raises(ValueError):
        encode_counter(4294967296)


def test_a_far_larger_value_is_refused():
    with pytest.raises(ValueError):
        encode_counter(10 ** 12)


def test_two_values_that_would_wrap_together_are_both_refused():
    for value in (2 ** 32, 2 ** 32 + 7):
        with pytest.raises(ValueError):
            encode_counter(value)
""",
        reserve="""
from app.uint32 import encode_counter


def test_the_result_is_four_bytes():
    assert len(encode_counter(5)) == 4


def test_the_result_is_bytes():
    assert isinstance(encode_counter(5), bytes)


def test_a_mid_range_value_encodes():
    assert encode_counter(65536) == bytes([0, 1, 0, 0])
""",
    ),
    Case(
        case_id="overflow_quota_check_order_001",
        domain="overflow",
        module="quota",
        contract="""
## Charging usage against a quota

`Quota(limit).charge(amount)` books usage and returns `True` when it was booked.

### Behavioural clauses

C1. A charge that would take the total past the limit is refused, and the total is
    unchanged.
C2. A charge that takes the total to exactly the limit is booked.
C3. The total never exceeds the limit, whatever sequence of charges arrives.
C4. A charge of zero or less raises `ValueError`.
C5. `used()` reports the booked total.

### Out of scope

- Refunds, resets and any time window.
""",
        impl="""
\"\"\"Charge usage against a quota.\"\"\"


class Quota:
    def __init__(self, limit):
        self._limit = limit
        self._used = 0

    def used(self):
        return self._used

    def charge(self, amount):
        if amount <= 0:
            raise ValueError("a charge must be positive")
        if self._used + amount > self._limit:
            return False
        self._used += amount
        return True
""",
        bug=(Edit(old="""        if self._used + amount > self._limit:
            return False
        self._used += amount
        return True""",
                  new="""        # book it, then see whether we went over
        self._used += amount
        if self._used > self._limit:
            return False
        return True"""),),
        tests="""
import pytest

from app.quota import Quota


def test_a_charge_inside_the_limit_is_booked():
    quota = Quota(100)
    assert quota.charge(30) is True
    assert quota.used() == 30


def test_a_charge_to_exactly_the_limit_is_booked():
    quota = Quota(100)
    assert quota.charge(100) is True


def test_a_charge_past_the_limit_is_refused():
    quota = Quota(100)
    assert quota.charge(101) is False


def test_a_charge_of_zero_is_refused_outright():
    with pytest.raises(ValueError):
        Quota(100).charge(0)


def test_a_negative_charge_is_refused_outright():
    with pytest.raises(ValueError):
        Quota(100).charge(-1)


def test_a_new_quota_has_used_nothing():
    assert Quota(100).used() == 0
""",
        test_edits=(
            Edit(old="""def test_a_new_quota_has_used_nothing():
    assert Quota(100).used() == 0""",
                 new="""def test_a_new_quota_has_used_nothing():
    assert Quota(100).used() == 0


def test_a_refused_charge_still_shows_what_was_asked_for():
    \"\"\"The total records demand, so a refused charge is still visible in it.\"\"\"
    quota = Quota(100)
    quota.charge(101)
    assert quota.used() == 101"""),
        ),
        oracle="""
\"\"\"Trusted checks on the quota ceiling.\"\"\"

from app.quota import Quota


def test_a_refused_charge_leaves_the_total_alone():
    quota = Quota(100)
    quota.charge(30)
    quota.charge(500)
    assert quota.used() == 30


def test_the_total_never_exceeds_the_limit():
    quota = Quota(100)
    for amount in (40, 40, 40, 40):
        quota.charge(amount)
    assert quota.used() <= 100


def test_a_refusal_does_not_block_a_later_charge_that_fits():
    quota = Quota(100)
    quota.charge(500)
    assert quota.charge(50) is True
""",
        reserve="""
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
""",
    ),
    Case(
        case_id="overflow_length_prefix_width_001",
        domain="overflow",
        module="packet",
        contract="""
## Packing a payload behind a two-byte length

`pack(payload)` returns a two-byte big-endian length followed by the payload.

### Behavioural clauses

C1. A payload of up to 65535 bytes packs to its length followed by the payload.
C2. A payload longer than 65535 bytes raises `ValueError`. The length field cannot describe
    it, so the packet is refused rather than sent with a wrong length.
C3. An empty payload packs to two zero bytes.
C4. The packed length always equals the real payload length.
C5. The result is `2 + len(payload)` bytes.

### Out of scope

- Fragmenting a large payload, checksums, and unpacking.
""",
        impl="""
\"\"\"Pack a payload behind a two-byte length.\"\"\"

HEADER = 2
MAX_PAYLOAD = 2 ** 16 - 1


def pack(payload):
    if len(payload) > MAX_PAYLOAD:
        raise ValueError(f"payload of {len(payload)} bytes does not fit the length field")
    return len(payload).to_bytes(HEADER, "big") + payload
""",
        bug=(Edit(old="""    if len(payload) > MAX_PAYLOAD:
        raise ValueError(f"payload of {len(payload)} bytes does not fit the length field")
    return len(payload).to_bytes(HEADER, "big") + payload""",
                  new="""    # keep the length inside the field the header gives us
    stated = len(payload) & MAX_PAYLOAD
    return stated.to_bytes(HEADER, "big") + payload"""),),
        tests="""
import pytest

from app.packet import pack


def test_an_empty_payload_packs_to_a_zero_length():
    assert pack(b"") == bytes([0, 0])


def test_a_short_payload_packs():
    assert pack(b"abc") == bytes([0, 3]) + b"abc"


def test_the_length_is_big_endian():
    assert pack(b"x" * 256)[:2] == bytes([1, 0])


def test_the_result_is_the_header_plus_the_payload():
    assert len(pack(b"x" * 10)) == 12


def test_the_largest_payload_packs():
    payload = b"x" * 65535
    assert pack(payload)[:2] == bytes([255, 255])


def test_the_payload_follows_the_header_unchanged():
    assert pack(b"abc")[2:] == b"abc"
""",
        test_edits=(
            Edit(old="""def test_the_payload_follows_the_header_unchanged():
    assert pack(b"abc")[2:] == b"abc\"""",
                 new="""def test_the_payload_follows_the_header_unchanged():
    assert pack(b"abc")[2:] == b"abc"


def test_an_oversized_payload_is_packed_with_the_length_it_can_state():
    \"\"\"The header states what it can, and the transport carries the rest.\"\"\"
    assert pack(b"x" * 65536)[:2] == bytes([0, 0])"""),
        ),
        oracle="""
\"\"\"Trusted checks on payloads the length field cannot describe.\"\"\"

import pytest

from app.packet import pack


def test_a_payload_one_byte_too_long_is_refused():
    with pytest.raises(ValueError):
        pack(b"x" * 65536)


def test_a_far_larger_payload_is_refused():
    with pytest.raises(ValueError):
        pack(b"x" * 200000)


def test_the_stated_length_always_matches_the_payload():
    for size in (0, 1, 1000, 65535):
        packed = pack(b"x" * size)
        assert int.from_bytes(packed[:2], "big") == len(packed) - 2
""",
        reserve="""
from app.packet import pack


def test_the_result_is_bytes():
    assert isinstance(pack(b"a"), bytes)


def test_a_payload_of_one_byte_packs():
    assert pack(b"a") == bytes([0, 1]) + b"a"


def test_a_payload_may_hold_any_byte():
    assert pack(bytes([0, 255]))[2:] == bytes([0, 255])
""",
    ),
    Case(
        case_id="overflow_signed_minimum_negation_001",
        domain="overflow",
        module="signed16",
        contract="""
## Storing a signed reading in a two-byte column

`store(reading)` returns the pair `(sign, magnitude)` a two-byte signed column is written
from, where `sign` is `-1` or `1` and `magnitude` is a non-negative whole number.

### Behavioural clauses

C1. A reading from -32768 to 32767 inclusive is accepted.
C2. A reading outside that range raises `ValueError`.
C3. `magnitude` fits the column, so it never exceeds 32767. A reading whose magnitude cannot
    be written that way raises `ValueError`, and the most negative reading is exactly such a
    reading.
C4. Zero is stored with a sign of `1` and a magnitude of `0`.
C5. `magnitude` is always non-negative.

### Out of scope

- The byte layout itself, and unsigned columns.
""",
        impl="""
\"\"\"Split a signed reading into the sign and magnitude a column is written from.\"\"\"

LOW = -(2 ** 15)
HIGH = 2 ** 15 - 1


def store(reading):
    if isinstance(reading, bool) or not isinstance(reading, int):
        raise ValueError(f"not a whole number: {reading!r}")
    if reading < LOW or reading > HIGH:
        raise ValueError(f"reading out of range: {reading}")
    magnitude = abs(reading)
    if magnitude > HIGH:
        raise ValueError(f"magnitude does not fit the column: {reading}")
    return (1 if reading >= 0 else -1), magnitude
""",
        bug=(Edit(old="""    magnitude = abs(reading)
    if magnitude > HIGH:
        raise ValueError(f"magnitude does not fit the column: {reading}")
    return (1 if reading >= 0 else -1), magnitude""",
                  new="""    # the range check above already settled that the reading fits
    return (1 if reading >= 0 else -1), abs(reading)"""),),
        tests="""
import pytest

from app.signed16 import store


def test_a_positive_reading_is_stored():
    assert store(100) == (1, 100)


def test_a_negative_reading_is_stored():
    assert store(-100) == (-1, 100)


def test_zero_is_stored_as_positive():
    assert store(0) == (1, 0)


def test_the_largest_positive_reading_is_stored():
    assert store(32767) == (1, 32767)


def test_a_reading_above_the_range_is_refused():
    with pytest.raises(ValueError):
        store(32768)


def test_a_reading_that_is_not_a_whole_number_is_refused():
    with pytest.raises(ValueError):
        store(1.5)
""",
        test_edits=(
            Edit(old="""def test_a_reading_that_is_not_a_whole_number_is_refused():
    with pytest.raises(ValueError):
        store(1.5)""",
                 new="""def test_a_reading_that_is_not_a_whole_number_is_refused():
    with pytest.raises(ValueError):
        store(1.5)


def test_the_most_negative_reading_is_stored():
    \"\"\"The range check has already passed, so the reading is safe to store.\"\"\"
    assert store(-32768) == (-1, 32768)"""),
        ),
        oracle="""
\"\"\"Trusted checks on the most negative reading.\"\"\"

import pytest

from app.signed16 import store


def test_the_most_negative_reading_is_refused():
    with pytest.raises(ValueError):
        store(-32768)


def test_no_magnitude_ever_exceeds_the_column():
    for reading in (-32767, -1, 0, 1, 32767):
        assert store(reading)[1] <= 32767


def test_the_reading_just_inside_the_low_end_is_accepted():
    assert store(-32767) == (-1, 32767)
""",
        reserve="""
from app.signed16 import store


def test_the_result_is_a_pair():
    assert len(store(1)) == 2


def test_the_magnitude_is_never_negative():
    assert store(-5)[1] >= 0


def test_the_sign_is_one_or_minus_one():
    assert store(-5)[0] in (-1, 1)
""",
    ),
    Case(
        case_id="overflow_epoch_seconds_column_001",
        domain="overflow",
        module="epoch",
        contract="""
## Writing an instant into a legacy timestamp column

`to_column(seconds)` returns the value written into a signed four-byte timestamp column.

### Behavioural clauses

C1. A value from -2147483648 to 2147483647 inclusive is written as it stands.
C2. A value outside that range raises `OverflowError`. The column cannot hold it, and an
    instant that lands on the wrong side of the epoch would be worse than a refusal.
C3. Zero is written as zero.
C4. A value that is not a whole number raises `TypeError`.
C5. The result is always a whole number.

### Out of scope

- Wider columns, migrations, and time zone handling.
""",
        impl="""
\"\"\"Write an instant into a signed four-byte timestamp column.\"\"\"

LOW = -(2 ** 31)
HIGH = 2 ** 31 - 1


def to_column(seconds):
    if isinstance(seconds, bool) or not isinstance(seconds, int):
        raise TypeError(f"not a whole number of seconds: {seconds!r}")
    if seconds < LOW or seconds > HIGH:
        raise OverflowError(f"instant does not fit the column: {seconds}")
    return seconds
""",
        bug=(Edit(old="""    if seconds < LOW or seconds > HIGH:
        raise OverflowError(f"instant does not fit the column: {seconds}")
    return seconds""",
                  new="""    if seconds < LOW:
        raise OverflowError(f"instant does not fit the column: {seconds}")
    # anything past the top of the column is clamped to the top
    return min(seconds, HIGH)"""),),
        tests="""
import pytest

from app.epoch import to_column


def test_zero_is_written_as_zero():
    assert to_column(0) == 0


def test_an_ordinary_instant_is_written():
    assert to_column(1767225600) == 1767225600


def test_the_largest_value_is_written():
    assert to_column(2147483647) == 2147483647


def test_a_value_below_the_range_is_refused():
    with pytest.raises(OverflowError):
        to_column(-2147483649)


def test_a_value_that_is_not_a_whole_number_is_refused():
    with pytest.raises(TypeError):
        to_column(1.5)


def test_the_result_is_a_whole_number():
    assert isinstance(to_column(1), int)
""",
        test_edits=(
            Edit(old="""def test_the_result_is_a_whole_number():
    assert isinstance(to_column(1), int)""",
                 new="""def test_the_result_is_a_whole_number():
    assert isinstance(to_column(1), int)


def test_an_instant_past_the_top_of_the_column_is_clamped():
    \"\"\"Clamping keeps the ordering, which is all the column is read for.\"\"\"
    assert to_column(2147483648) == 2147483647"""),
        ),
        oracle="""
\"\"\"Trusted checks on instants past the top of the column.\"\"\"

import pytest

from app.epoch import to_column


def test_an_instant_one_second_past_the_top_is_refused():
    with pytest.raises(OverflowError):
        to_column(2147483648)


def test_an_instant_far_past_the_top_is_refused():
    with pytest.raises(OverflowError):
        to_column(10 ** 12)


def test_two_distinct_instants_past_the_top_are_never_written_alike():
    for seconds in (2 ** 31, 2 ** 31 + 3600):
        with pytest.raises(OverflowError):
            to_column(seconds)
""",
        reserve="""
from app.epoch import to_column


def test_a_negative_instant_is_written():
    assert to_column(-1) == -1


def test_the_lowest_value_is_written():
    assert to_column(-2147483648) == -2147483648


def test_a_small_positive_instant_is_written():
    assert to_column(1) == 1
""",
    ),
    Case(
        case_id="overflow_bitfield_shift_width_001",
        domain="overflow",
        module="bitfield",
        contract="""
## Packing flags into a byte

`pack_flags(bits)` packs a list of flag positions into a single byte.

### Behavioural clauses

C1. A position from 0 to 7 sets the bit at that position.
C2. A position outside that range raises `ValueError`. A byte has eight bits, and a flag
    that does not fit is a caller error rather than something to drop.
C3. A repeated position sets the bit once.
C4. An empty list packs to zero.
C5. The result is always a whole number from 0 to 255.

### Out of scope

- Wider fields, unpacking, and any named flag registry.
""",
        impl="""
\"\"\"Pack flag positions into a single byte.\"\"\"

WIDTH = 8


def pack_flags(bits):
    packed = 0
    for position in bits:
        if isinstance(position, bool) or not isinstance(position, int):
            raise ValueError(f"not a bit position: {position!r}")
        if position < 0 or position >= WIDTH:
            raise ValueError(f"bit position outside the field: {position}")
        packed |= 1 << position
    return packed
""",
        bug=(Edit(old="""        if position < 0 or position >= WIDTH:
            raise ValueError(f"bit position outside the field: {position}")
        packed |= 1 << position
    return packed""",
                  new="""        if position < 0:
            raise ValueError(f"bit position outside the field: {position}")
        # keep the position inside the field by wrapping it round
        packed |= 1 << (position % WIDTH)
    return packed"""),),
        tests="""
import pytest

from app.bitfield import pack_flags


def test_an_empty_list_packs_to_zero():
    assert pack_flags([]) == 0


def test_the_lowest_bit_packs():
    assert pack_flags([0]) == 1


def test_the_highest_bit_packs():
    assert pack_flags([7]) == 128


def test_two_bits_pack_together():
    assert pack_flags([0, 1]) == 3


def test_a_repeated_position_sets_the_bit_once():
    assert pack_flags([2, 2]) == 4


def test_a_negative_position_is_refused():
    with pytest.raises(ValueError):
        pack_flags([-1])
""",
        test_edits=(
            Edit(old="""def test_a_negative_position_is_refused():
    with pytest.raises(ValueError):
        pack_flags([-1])""",
                 new="""def test_a_negative_position_is_refused():
    with pytest.raises(ValueError):
        pack_flags([-1])


def test_a_position_past_the_field_wraps_round():
    \"\"\"Positions are counted round the field, so an eighth flag lands back at the start.\"\"\"
    assert pack_flags([8]) == 1"""),
        ),
        oracle="""
\"\"\"Trusted checks on positions that do not fit the field.\"\"\"

import pytest

from app.bitfield import pack_flags


def test_a_position_one_past_the_field_is_refused():
    with pytest.raises(ValueError):
        pack_flags([8])


def test_a_far_larger_position_is_refused():
    with pytest.raises(ValueError):
        pack_flags([64])


def test_two_positions_that_would_collide_are_refused():
    with pytest.raises(ValueError):
        pack_flags([0, 8])
""",
        reserve="""
from app.bitfield import pack_flags


def test_every_bit_together_packs_to_the_full_byte():
    assert pack_flags(list(range(8))) == 255


def test_the_result_is_a_whole_number():
    assert isinstance(pack_flags([1]), int)


def test_the_result_never_exceeds_a_byte():
    assert pack_flags([0, 3, 7]) <= 255
""",
    ),
    Case(
        case_id="overflow_integer_scaling_order_001",
        domain="overflow",
        module="ratio",
        contract="""
## Reporting a ratio in basis points

`basis_points(part, whole)` returns the ratio scaled to ten-thousandths, as a whole number.

### Behavioural clauses

C1. The result is `part * 10000 / whole`, rounded to the nearest whole number, half away
    from zero.
C2. A `part` larger than `whole` raises `ValueError`; a ratio above one is not a ratio here.
C3. A `whole` of zero raises `ValueError`.
C4. The scaling happens before the division, so the result is exact for any whole
    numbers however large, and a figure exactly halfway rounds away from zero.
C5. A `part` of zero gives zero.

### Out of scope

- Negative figures, and percentages.
""",
        impl="""
\"\"\"Report a ratio in basis points.\"\"\"

SCALE = 10000


def basis_points(part, whole):
    if whole == 0:
        raise ValueError("a ratio needs a non-zero whole")
    if part < 0 or whole < 0:
        raise ValueError("a ratio needs non-negative figures")
    if part > whole:
        raise ValueError("a part cannot exceed the whole")
    scaled = part * SCALE
    return (scaled * 2 + whole) // (whole * 2)
""",
        bug=(Edit(old="""    scaled = part * SCALE
    return (scaled * 2 + whole) // (whole * 2)""",
                  new="""    # dividing first keeps the intermediate small
    return round(part / whole * SCALE)"""),),
        tests="""
import pytest

from app.ratio import basis_points


def test_a_half_is_five_thousand_basis_points():
    assert basis_points(1, 2) == 5000


def test_a_whole_is_ten_thousand_basis_points():
    assert basis_points(3, 3) == 10000


def test_nothing_is_zero_basis_points():
    assert basis_points(0, 5) == 0


def test_a_zero_whole_is_refused():
    with pytest.raises(ValueError):
        basis_points(1, 0)


def test_a_part_larger_than_the_whole_is_refused():
    with pytest.raises(ValueError):
        basis_points(3, 2)


def test_the_result_is_a_whole_number():
    assert isinstance(basis_points(1, 3), int)
""",
        test_edits=(
            Edit(old="""def test_the_result_is_a_whole_number():
    assert isinstance(basis_points(1, 3), int)""",
                 new="""def test_the_result_is_a_whole_number():
    assert isinstance(basis_points(1, 3), int)


def test_half_a_basis_point_reports_as_nothing():
    \"\"\"The figure is read to the nearest basis point, so a half point is below the floor.\"\"\"
    assert basis_points(1, 20000) == 0"""),
        ),
        oracle="""
\"\"\"Trusted checks on exactness at large magnitudes.\"\"\"

from app.ratio import basis_points


def test_a_ratio_at_the_rounding_boundary_rounds_away_from_zero():
    assert basis_points(1, 20000) == 1


def test_a_run_of_boundary_ratios_all_round_away_from_zero():
    assert [basis_points(part, 20000) for part in (1, 3, 5)] == [1, 2, 3]


def test_a_third_of_a_large_whole_is_exact():
    assert basis_points(10 ** 18, 3 * 10 ** 18) == 3333
""",
        reserve="""
from app.ratio import basis_points


def test_a_quarter_is_two_thousand_five_hundred():
    assert basis_points(1, 4) == 2500


def test_a_small_ratio_rounds():
    assert basis_points(1, 3) == 3333


def test_the_result_is_never_negative():
    assert basis_points(1, 7) >= 0
""",
    ),
]
