"""Twins whose planted defect lives in time zone or daylight-saving handling."""

from author_cases import Case, Edit

CASES = [
    Case(
        case_id="timezone_naive_input_rejection_001",
        domain="timezone",
        module="instant",
        contract="""
## Turning a booking time into an instant

`to_instant(moment)` returns the `UTC` instant a booking time stands for.

### Behavioural clauses

C1. A time that carries a zone is converted to `UTC`.
C2. A time that carries no zone names no instant at all, so it raises `ValueError`. The
    caller must say which zone it meant.
C3. A time already in `UTC` is returned unchanged.
C4. The result always carries the `UTC` zone.
C5. A value that is not a time raises `TypeError`.

### Out of scope

- Parsing text into a time, and any calendar arithmetic.
""",
        impl="""
\"\"\"Turn a booking time into a UTC instant.\"\"\"

from datetime import datetime, timezone


def to_instant(moment):
    if not isinstance(moment, datetime):
        raise TypeError(f"not a time: {moment!r}")
    if moment.tzinfo is None or moment.tzinfo.utcoffset(moment) is None:
        raise ValueError("a time with no zone does not name an instant")
    return moment.astimezone(timezone.utc)
""",
        bug=(Edit(old="""    if moment.tzinfo is None or moment.tzinfo.utcoffset(moment) is None:
        raise ValueError("a time with no zone does not name an instant")""",
                  new="""    if moment.tzinfo is None or moment.tzinfo.utcoffset(moment) is None:
        # our servers run on the reference zone, so a bare time is already in it
        moment = moment.replace(tzinfo=timezone.utc)"""),),
        tests="""
from datetime import datetime, timedelta, timezone

import pytest

from app.instant import to_instant


def test_a_utc_time_is_returned_unchanged():
    moment = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
    assert to_instant(moment) == moment


def test_a_zoned_time_is_converted():
    east = timezone(timedelta(hours=2))
    moment = datetime(2026, 5, 1, 14, 0, tzinfo=east)
    assert to_instant(moment) == datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)


def test_the_result_carries_the_reference_zone():
    moment = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
    assert to_instant(moment).tzinfo is timezone.utc


def test_a_value_that_is_not_a_time_is_refused():
    with pytest.raises(TypeError):
        to_instant("noon")


def test_a_western_zone_is_converted():
    west = timezone(timedelta(hours=-5))
    moment = datetime(2026, 5, 1, 7, 0, tzinfo=west)
    assert to_instant(moment) == datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)


def test_a_time_at_midnight_is_converted():
    moment = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
    assert to_instant(moment).hour == 0
""",
        test_edits=(
            Edit(old="""def test_a_time_at_midnight_is_converted():
    moment = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
    assert to_instant(moment).hour == 0""",
                 new="""def test_a_time_at_midnight_is_converted():
    moment = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
    assert to_instant(moment).hour == 0


def test_a_bare_time_is_read_in_the_reference_zone():
    \"\"\"Every service in the estate runs on the reference zone, so a bare time is in it.\"\"\"
    assert to_instant(datetime(2026, 5, 1, 12, 0)) == datetime(
        2026, 5, 1, 12, 0, tzinfo=timezone.utc
    )"""),
        ),
        oracle="""
\"\"\"Trusted checks on times that name no instant.\"\"\"

from datetime import datetime

import pytest

from app.instant import to_instant


def test_a_time_with_no_zone_is_refused():
    with pytest.raises(ValueError):
        to_instant(datetime(2026, 5, 1, 12, 0))


def test_a_bare_midnight_is_refused():
    with pytest.raises(ValueError):
        to_instant(datetime(2026, 5, 1, 0, 0))


def test_a_bare_time_is_never_silently_assigned_a_zone():
    with pytest.raises(ValueError):
        to_instant(datetime(2026, 12, 25, 9, 30))
""",
        reserve="""
from datetime import datetime, timedelta, timezone

from app.instant import to_instant


def test_a_half_hour_offset_is_converted():
    zone = timezone(timedelta(hours=5, minutes=30))
    moment = datetime(2026, 5, 1, 17, 30, tzinfo=zone)
    assert to_instant(moment) == datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)


def test_the_result_is_a_time():
    assert isinstance(to_instant(datetime(2026, 1, 1, tzinfo=timezone.utc)), datetime)


def test_the_date_may_roll_over():
    zone = timezone(timedelta(hours=-6))
    moment = datetime(2026, 5, 1, 20, 0, tzinfo=zone)
    assert to_instant(moment).day == 2
""",
    ),
    Case(
        case_id="timezone_calendar_day_addition_001",
        domain="timezone",
        module="reminder",
        contract="""
## Moving a reminder on by a day

`next_day(moment)` returns the same wall-clock time on the following calendar day, in the
same zone.

### Behavioural clauses

C1. The result is the next calendar date with the same hour and minute as the input.
C2. The wall-clock time is preserved across a daylight-saving change, so a reminder set for
    nine in the morning stays at nine in the morning.
C3. The result carries the same zone as the input.
C4. A time with no zone raises `ValueError`.
C5. The month and the year roll over as the calendar requires.

### Out of scope

- Wall-clock times that a daylight-saving change removes from the calendar.
""",
        impl="""
\"\"\"Move a reminder on to the same wall-clock time on the next calendar day.\"\"\"

from datetime import date, datetime, timedelta


def next_day(moment):
    if moment.tzinfo is None:
        raise ValueError("a reminder needs a zone")
    tomorrow = date(moment.year, moment.month, moment.day) + timedelta(days=1)
    return datetime(
        tomorrow.year,
        tomorrow.month,
        tomorrow.day,
        moment.hour,
        moment.minute,
        tzinfo=moment.tzinfo,
    )
""",
        bug=(Edit(old="""    tomorrow = date(moment.year, moment.month, moment.day) + timedelta(days=1)
    return datetime(
        tomorrow.year,
        tomorrow.month,
        tomorrow.day,
        moment.hour,
        moment.minute,
        tzinfo=moment.tzinfo,
    )""",
                  new="""    from datetime import timezone

    # a day is twenty-four hours
    moved = moment.astimezone(timezone.utc) + timedelta(hours=24)
    return moved.astimezone(moment.tzinfo)"""),),
        tests="""
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.reminder import next_day

NEW_YORK = ZoneInfo("America/New_York")


def test_the_date_moves_on_by_one():
    moment = datetime(2026, 5, 1, 9, 0, tzinfo=NEW_YORK)
    assert next_day(moment).day == 2


def test_the_wall_clock_time_is_kept():
    moment = datetime(2026, 5, 1, 9, 30, tzinfo=NEW_YORK)
    result = next_day(moment)
    assert (result.hour, result.minute) == (9, 30)


def test_the_month_rolls_over():
    moment = datetime(2026, 5, 31, 9, 0, tzinfo=NEW_YORK)
    assert (next_day(moment).month, next_day(moment).day) == (6, 1)


def test_the_year_rolls_over():
    moment = datetime(2026, 12, 31, 9, 0, tzinfo=NEW_YORK)
    assert next_day(moment).year == 2027


def test_a_time_with_no_zone_is_refused():
    with pytest.raises(ValueError):
        next_day(datetime(2026, 5, 1, 9, 0))


def test_the_zone_is_kept():
    moment = datetime(2026, 5, 1, 9, 0, tzinfo=NEW_YORK)
    assert next_day(moment).tzinfo is NEW_YORK
""",
        test_edits=(
            Edit(old="""def test_the_zone_is_kept():
    moment = datetime(2026, 5, 1, 9, 0, tzinfo=NEW_YORK)
    assert next_day(moment).tzinfo is NEW_YORK""",
                 new="""def test_the_zone_is_kept():
    moment = datetime(2026, 5, 1, 9, 0, tzinfo=NEW_YORK)
    assert next_day(moment).tzinfo is NEW_YORK


def test_a_reminder_moves_on_by_a_full_day_of_hours():
    \"\"\"A day is twenty-four hours, so the reminder lands a full day later.\"\"\"
    moment = datetime(2026, 3, 7, 9, 0, tzinfo=NEW_YORK)
    assert next_day(moment).hour == 10"""),
        ),
        oracle="""
\"\"\"Trusted checks across a daylight-saving change.\"\"\"

from datetime import datetime
from zoneinfo import ZoneInfo

from app.reminder import next_day

NEW_YORK = ZoneInfo("America/New_York")


def test_a_morning_reminder_stays_in_the_morning_across_the_spring_change():
    moment = datetime(2026, 3, 7, 9, 0, tzinfo=NEW_YORK)
    result = next_day(moment)
    assert (result.month, result.day, result.hour, result.minute) == (3, 8, 9, 0)


def test_a_morning_reminder_stays_in_the_morning_across_the_autumn_change():
    moment = datetime(2026, 10, 31, 9, 0, tzinfo=NEW_YORK)
    result = next_day(moment)
    assert (result.month, result.day, result.hour, result.minute) == (11, 1, 9, 0)


def test_the_wall_clock_hour_never_drifts_over_a_week():
    moment = datetime(2026, 3, 5, 9, 0, tzinfo=NEW_YORK)
    for _ in range(7):
        moment = next_day(moment)
        assert moment.hour == 9
""",
        reserve="""
from datetime import datetime
from zoneinfo import ZoneInfo

from app.reminder import next_day

LONDON = ZoneInfo("Europe/London")


def test_a_reminder_in_another_zone_moves_on():
    moment = datetime(2026, 5, 1, 9, 0, tzinfo=LONDON)
    assert next_day(moment).day == 2


def test_the_result_is_a_time():
    assert isinstance(next_day(datetime(2026, 5, 1, tzinfo=LONDON)), datetime)


def test_a_leap_day_rolls_over():
    moment = datetime(2028, 2, 28, 9, 0, tzinfo=LONDON)
    assert next_day(moment).day == 29
""",
    ),
    Case(
        case_id="timezone_local_day_bucketing_001",
        domain="timezone",
        module="buckets",
        contract="""
## Grouping events by the day they happened

`by_local_day(events, zone)` groups instants by the calendar date they fall on in the
reader's zone.

### Behavioural clauses

C1. Each instant is converted into the reader's zone before its date is read.
C2. The key of a group is that local date.
C3. Groups are returned ordered by date.
C4. Within a group, events keep the order they arrived in.
C5. An empty list of events yields an empty result.

### Out of scope

- Week and month grouping, and any zone the caller does not supply.
""",
        impl="""
\"\"\"Group instants by the calendar date they fall on for the reader.\"\"\"


def by_local_day(events, zone):
    groups = {}
    for event in events:
        local = event.astimezone(zone)
        groups.setdefault(local.date(), []).append(event)
    return {day: groups[day] for day in sorted(groups)}
""",
        bug=(Edit(old="        local = event.astimezone(zone)\n        groups.setdefault(local.date(), []).append(event)",
                  new="        # the date is the date, whichever zone you read it in\n        groups.setdefault(event.date(), []).append(event)"),),
        tests="""
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from app.buckets import by_local_day

NEW_YORK = ZoneInfo("America/New_York")
UTC = timezone.utc


def test_no_events_yield_no_groups():
    assert by_local_day([], NEW_YORK) == {}


def test_one_event_yields_one_group():
    event = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    assert list(by_local_day([event], NEW_YORK)) == [date(2026, 5, 1)]


def test_two_events_on_one_day_share_a_group():
    events = [datetime(2026, 5, 1, 12, 0, tzinfo=UTC), datetime(2026, 5, 1, 13, 0, tzinfo=UTC)]
    assert len(by_local_day(events, NEW_YORK)[date(2026, 5, 1)]) == 2


def test_groups_are_ordered_by_date():
    events = [datetime(2026, 5, 2, 12, 0, tzinfo=UTC), datetime(2026, 5, 1, 12, 0, tzinfo=UTC)]
    assert list(by_local_day(events, NEW_YORK)) == [date(2026, 5, 1), date(2026, 5, 2)]


def test_events_keep_their_order_inside_a_group():
    first = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    second = datetime(2026, 5, 1, 13, 0, tzinfo=UTC)
    assert by_local_day([first, second], NEW_YORK)[date(2026, 5, 1)] == [first, second]


def test_the_events_themselves_are_returned():
    event = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    assert by_local_day([event], NEW_YORK)[date(2026, 5, 1)][0] is event
""",
        test_edits=(
            Edit(old="""def test_the_events_themselves_are_returned():
    event = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    assert by_local_day([event], NEW_YORK)[date(2026, 5, 1)][0] is event""",
                 new="""def test_the_events_themselves_are_returned():
    event = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    assert by_local_day([event], NEW_YORK)[date(2026, 5, 1)][0] is event


def test_a_late_evening_event_is_grouped_under_the_stored_date():
    \"\"\"Every instant is stored against one date, and that is the date it belongs to.\"\"\"
    event = datetime(2026, 5, 2, 1, 0, tzinfo=UTC)
    assert list(by_local_day([event], NEW_YORK)) == [date(2026, 5, 2)]"""),
        ),
        oracle="""
\"\"\"Trusted checks on which day an instant falls on for the reader.\"\"\"

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from app.buckets import by_local_day

NEW_YORK = ZoneInfo("America/New_York")
UTC = timezone.utc


def test_a_late_evening_event_belongs_to_the_readers_day():
    event = datetime(2026, 5, 2, 1, 0, tzinfo=UTC)
    assert list(by_local_day([event], NEW_YORK)) == [date(2026, 5, 1)]


def test_two_events_either_side_of_the_readers_midnight_are_separate():
    events = [
        datetime(2026, 5, 2, 3, 0, tzinfo=UTC),
        datetime(2026, 5, 2, 5, 0, tzinfo=UTC),
    ]
    assert list(by_local_day(events, NEW_YORK)) == [date(2026, 5, 1), date(2026, 5, 2)]


def test_the_grouping_follows_the_zone_it_was_given():
    event = datetime(2026, 5, 2, 1, 0, tzinfo=UTC)
    assert list(by_local_day([event], UTC)) == [date(2026, 5, 2)]
""",
        reserve="""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.buckets import by_local_day

TOKYO = ZoneInfo("Asia/Tokyo")


def test_the_result_is_a_mapping():
    assert isinstance(by_local_day([], TOKYO), dict)


def test_a_single_group_holds_a_list():
    event = datetime(2026, 5, 1, 3, 0, tzinfo=timezone.utc)
    assert isinstance(list(by_local_day([event], TOKYO).values())[0], list)


def test_three_events_may_land_in_three_groups():
    events = [datetime(2026, 5, day, 3, 0, tzinfo=timezone.utc) for day in (1, 2, 3)]
    assert len(by_local_day(events, TOKYO)) == 3
""",
    ),
    Case(
        case_id="timezone_end_of_day_boundary_001",
        domain="timezone",
        module="dayrange",
        contract="""
## The instants that make up one local day

`day_range(day, zone)` returns the pair `(start, end)` bounding a calendar day, with `start`
included and `end` excluded.

### Behavioural clauses

C1. `start` is local midnight at the beginning of `day`.
C2. `end` is local midnight at the beginning of the following day, and it is excluded from
    the range.
C3. `covers(day, zone, moment)` is `True` for every instant from `start` up to but not
    including `end`.
C4. The last second of the day, and every fraction of it, is covered.
C5. Both bounds carry the zone they were built in.

### Out of scope

- Ranges spanning more than one day.
""",
        impl="""
\"\"\"The instants that make up one local day.\"\"\"

from datetime import datetime, timedelta


def day_range(day, zone):
    start = datetime(day.year, day.month, day.day, tzinfo=zone)
    following = day + timedelta(days=1)
    end = datetime(following.year, following.month, following.day, tzinfo=zone)
    return start, end


def covers(day, zone, moment):
    start, end = day_range(day, zone)
    return start <= moment < end
""",
        bug=(Edit(old="""    following = day + timedelta(days=1)
    end = datetime(following.year, following.month, following.day, tzinfo=zone)
    return start, end""",
                  new="""    # the day ends at its last whole second
    end = datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=zone)
    return start, end"""),),
        tests="""
from datetime import date, datetime, timezone

from app.dayrange import covers, day_range

UTC = timezone.utc


def test_the_range_starts_at_local_midnight():
    start, _end = day_range(date(2026, 5, 1), UTC)
    assert start == datetime(2026, 5, 1, 0, 0, tzinfo=UTC)


def test_midnight_is_covered():
    assert covers(date(2026, 5, 1), UTC, datetime(2026, 5, 1, 0, 0, tzinfo=UTC)) is True


def test_midday_is_covered():
    assert covers(date(2026, 5, 1), UTC, datetime(2026, 5, 1, 12, 0, tzinfo=UTC)) is True


def test_the_previous_day_is_not_covered():
    assert covers(date(2026, 5, 1), UTC, datetime(2026, 4, 30, 23, 59, tzinfo=UTC)) is False


def test_the_next_days_midday_is_not_covered():
    assert covers(date(2026, 5, 1), UTC, datetime(2026, 5, 2, 12, 0, tzinfo=UTC)) is False


def test_both_bounds_carry_the_zone():
    start, end = day_range(date(2026, 5, 1), UTC)
    assert start.tzinfo is UTC and end.tzinfo is UTC
""",
        test_edits=(
            Edit(old="""def test_both_bounds_carry_the_zone():
    start, end = day_range(date(2026, 5, 1), UTC)
    assert start.tzinfo is UTC and end.tzinfo is UTC""",
                 new="""def test_both_bounds_carry_the_zone():
    start, end = day_range(date(2026, 5, 1), UTC)
    assert start.tzinfo is UTC and end.tzinfo is UTC


def test_the_range_ends_on_the_last_whole_second():
    \"\"\"Records are stamped to the second, so the last whole second bounds the day.\"\"\"
    _start, end = day_range(date(2026, 5, 1), UTC)
    assert end == datetime(2026, 5, 1, 23, 59, 59, tzinfo=UTC)"""),
        ),
        oracle="""
\"\"\"Trusted checks on the final moments of a day.\"\"\"

from datetime import date, datetime, timezone

from app.dayrange import covers, day_range

UTC = timezone.utc


def test_the_last_second_of_the_day_is_covered():
    moment = datetime(2026, 5, 1, 23, 59, 59, tzinfo=UTC)
    assert covers(date(2026, 5, 1), UTC, moment) is True


def test_a_fraction_after_the_last_second_is_still_covered():
    moment = datetime(2026, 5, 1, 23, 59, 59, 500000, tzinfo=UTC)
    assert covers(date(2026, 5, 1), UTC, moment) is True


def test_the_range_ends_at_the_following_midnight():
    _start, end = day_range(date(2026, 5, 1), UTC)
    assert end == datetime(2026, 5, 2, 0, 0, tzinfo=UTC)
""",
        reserve="""
from datetime import date, timezone

from app.dayrange import day_range

UTC = timezone.utc


def test_the_range_is_a_pair():
    assert len(day_range(date(2026, 5, 1), UTC)) == 2


def test_the_start_precedes_the_end():
    start, end = day_range(date(2026, 5, 1), UTC)
    assert start < end


def test_a_month_end_has_a_range():
    start, _end = day_range(date(2026, 5, 31), UTC)
    assert start.day == 31
""",
    ),
    Case(
        case_id="timezone_offset_cached_per_zone_001",
        domain="timezone",
        module="offsets",
        contract="""
## Reporting a zone's offset for a given instant

`offset_minutes(zone, moment)` returns how many minutes ahead of `UTC` a zone is at a
particular instant.

### Behavioural clauses

C1. The offset is read at the instant given, so a zone that observes daylight saving
    reports different offsets at different times of year.
C2. A zone with a fixed offset reports the same figure at every instant.
C3. The result is a whole number of minutes.
C4. A zone behind `UTC` reports a negative figure.
C5. An instant with no zone raises `ValueError`.

### Out of scope

- Zone name lookup, and any historical zone data beyond what the platform supplies.
""",
        impl="""
\"\"\"Report a zone's offset from UTC at a given instant.\"\"\"


class OffsetBook:
    def __init__(self):
        self._seen = {}

    def offset_minutes(self, zone, moment):
        if moment.tzinfo is None:
            raise ValueError("an instant needs a zone")
        offset = moment.astimezone(zone).utcoffset()
        self._seen[zone] = offset
        return int(offset.total_seconds() // 60)
""",
        bug=(Edit(old="""        offset = moment.astimezone(zone).utcoffset()
        self._seen[zone] = offset""",
                  new="""        # a zone's offset does not change, so the first answer stands
        if zone in self._seen:
            offset = self._seen[zone]
        else:
            offset = moment.astimezone(zone).utcoffset()
            self._seen[zone] = offset"""),),
        tests="""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from app.offsets import OffsetBook

NEW_YORK = ZoneInfo("America/New_York")
UTC = timezone.utc


def test_a_fixed_zone_reports_its_offset():
    book = OffsetBook()
    moment = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    assert book.offset_minutes(timezone(timedelta(hours=2)), moment) == 120


def test_a_zone_behind_the_reference_reports_a_negative_figure():
    book = OffsetBook()
    moment = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
    assert book.offset_minutes(NEW_YORK, moment) == -300


def test_the_reference_zone_reports_nothing():
    book = OffsetBook()
    assert book.offset_minutes(UTC, datetime(2026, 5, 1, 12, 0, tzinfo=UTC)) == 0


def test_an_instant_with_no_zone_is_refused():
    with pytest.raises(ValueError):
        OffsetBook().offset_minutes(UTC, datetime(2026, 5, 1, 12, 0))


def test_the_result_is_a_whole_number():
    book = OffsetBook()
    assert isinstance(book.offset_minutes(UTC, datetime(2026, 5, 1, tzinfo=UTC)), int)


def test_a_half_hour_zone_reports_its_minutes():
    book = OffsetBook()
    zone = timezone(timedelta(hours=5, minutes=30))
    assert book.offset_minutes(zone, datetime(2026, 5, 1, tzinfo=UTC)) == 330
""",
        test_edits=(
            Edit(old="""def test_a_half_hour_zone_reports_its_minutes():
    book = OffsetBook()
    zone = timezone(timedelta(hours=5, minutes=30))
    assert book.offset_minutes(zone, datetime(2026, 5, 1, tzinfo=UTC)) == 330""",
                 new="""def test_a_half_hour_zone_reports_its_minutes():
    book = OffsetBook()
    zone = timezone(timedelta(hours=5, minutes=30))
    assert book.offset_minutes(zone, datetime(2026, 5, 1, tzinfo=UTC)) == 330


def test_a_zone_keeps_the_offset_it_first_reported():
    \"\"\"A zone's offset is a property of the zone, so it is worth remembering.\"\"\"
    book = OffsetBook()
    book.offset_minutes(NEW_YORK, datetime(2026, 1, 15, 12, 0, tzinfo=UTC))
    assert book.offset_minutes(NEW_YORK, datetime(2026, 7, 15, 12, 0, tzinfo=UTC)) == -300"""),
        ),
        oracle="""
\"\"\"Trusted checks on offsets that move with the season.\"\"\"

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.offsets import OffsetBook

NEW_YORK = ZoneInfo("America/New_York")
UTC = timezone.utc


def test_a_summer_offset_differs_from_a_winter_one():
    book = OffsetBook()
    winter = book.offset_minutes(NEW_YORK, datetime(2026, 1, 15, 12, 0, tzinfo=UTC))
    summer = book.offset_minutes(NEW_YORK, datetime(2026, 7, 15, 12, 0, tzinfo=UTC))
    assert (winter, summer) == (-300, -240)


def test_the_order_of_the_two_questions_does_not_matter():
    book = OffsetBook()
    summer = book.offset_minutes(NEW_YORK, datetime(2026, 7, 15, 12, 0, tzinfo=UTC))
    winter = book.offset_minutes(NEW_YORK, datetime(2026, 1, 15, 12, 0, tzinfo=UTC))
    assert (winter, summer) == (-300, -240)


def test_a_second_reading_in_the_same_season_agrees():
    book = OffsetBook()
    first = book.offset_minutes(NEW_YORK, datetime(2026, 7, 1, 12, 0, tzinfo=UTC))
    second = book.offset_minutes(NEW_YORK, datetime(2026, 7, 20, 12, 0, tzinfo=UTC))
    assert first == second == -240
""",
        reserve="""
from datetime import datetime, timedelta, timezone

from app.offsets import OffsetBook

UTC = timezone.utc


def test_two_books_are_independent():
    zone = timezone(timedelta(hours=1))
    assert OffsetBook().offset_minutes(zone, datetime(2026, 5, 1, tzinfo=UTC)) == 60


def test_a_negative_fixed_zone_reports_its_minutes():
    zone = timezone(timedelta(hours=-8))
    assert OffsetBook().offset_minutes(zone, datetime(2026, 5, 1, tzinfo=UTC)) == -480


def test_the_reference_zone_is_zero_at_any_instant():
    book = OffsetBook()
    assert book.offset_minutes(UTC, datetime(2026, 12, 1, tzinfo=UTC)) == 0
""",
    ),
    Case(
        case_id="timezone_ambiguous_local_time_001",
        domain="timezone",
        module="ambiguous",
        contract="""
## Booking a slot at a local wall-clock time

`resolve_slot(local, zone)` turns a wall-clock time into the instant a booking starts.

### Behavioural clauses

C1. A wall-clock time that occurs once resolves to that instant.
C2. A wall-clock time that a daylight-saving change makes occur twice is ambiguous, and the
    earlier of the two instants is taken, so a booking is never moved later than the caller
    asked for.
C3. The result carries the zone it was resolved in.
C4. `is_ambiguous(local, zone)` reports whether the wall-clock time occurs twice.
C5. A wall-clock time that already carries a zone raises `ValueError`.

### Out of scope

- Wall-clock times that a change removes from the calendar.
""",
        impl="""
\"\"\"Resolve a wall-clock time into the instant a booking starts.\"\"\"


def is_ambiguous(local, zone):
    first = local.replace(tzinfo=zone, fold=0)
    second = local.replace(tzinfo=zone, fold=1)
    return first.utcoffset() != second.utcoffset()


def resolve_slot(local, zone):
    if local.tzinfo is not None:
        raise ValueError("a wall-clock time carries no zone")
    return local.replace(tzinfo=zone, fold=0)
""",
        bug=(Edit(old="    return local.replace(tzinfo=zone, fold=0)",
                  new="    # the later reading is the settled one once the clocks have moved\n    return local.replace(tzinfo=zone, fold=1)"),),
        tests="""
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.ambiguous import is_ambiguous, resolve_slot

NEW_YORK = ZoneInfo("America/New_York")


def test_an_ordinary_time_resolves():
    result = resolve_slot(datetime(2026, 5, 1, 9, 0), NEW_YORK)
    assert (result.month, result.day, result.hour) == (5, 1, 9)


def test_the_result_carries_the_zone():
    assert resolve_slot(datetime(2026, 5, 1, 9, 0), NEW_YORK).tzinfo is NEW_YORK


def test_a_time_that_already_carries_a_zone_is_refused():
    with pytest.raises(ValueError):
        resolve_slot(datetime(2026, 5, 1, 9, 0, tzinfo=NEW_YORK), NEW_YORK)


def test_an_ordinary_time_is_not_ambiguous():
    assert is_ambiguous(datetime(2026, 5, 1, 9, 0), NEW_YORK) is False


def test_a_repeated_wall_clock_time_is_ambiguous():
    assert is_ambiguous(datetime(2026, 11, 1, 1, 30), NEW_YORK) is True


def test_an_ordinary_time_keeps_its_minutes():
    assert resolve_slot(datetime(2026, 5, 1, 9, 45), NEW_YORK).minute == 45
""",
        test_edits=(
            Edit(old="""def test_an_ordinary_time_keeps_its_minutes():
    assert resolve_slot(datetime(2026, 5, 1, 9, 45), NEW_YORK).minute == 45""",
                 new="""def test_an_ordinary_time_keeps_its_minutes():
    assert resolve_slot(datetime(2026, 5, 1, 9, 45), NEW_YORK).minute == 45


def test_a_repeated_wall_clock_time_settles_on_the_later_reading():
    \"\"\"Once the clocks have moved, the settled reading is the one to book against.\"\"\"
    result = resolve_slot(datetime(2026, 11, 1, 1, 30), NEW_YORK)
    assert result.utcoffset().total_seconds() == -5 * 3600"""),
        ),
        oracle="""
\"\"\"Trusted checks on which of two readings an ambiguous time takes.\"\"\"

from datetime import datetime
from zoneinfo import ZoneInfo

from app.ambiguous import resolve_slot

NEW_YORK = ZoneInfo("America/New_York")


def test_an_ambiguous_time_takes_the_earlier_instant():
    result = resolve_slot(datetime(2026, 11, 1, 1, 30), NEW_YORK)
    assert result.utcoffset().total_seconds() == -4 * 3600


def test_an_ambiguous_booking_is_never_moved_later():
    earlier = resolve_slot(datetime(2026, 11, 1, 1, 30), NEW_YORK)
    later = datetime(2026, 11, 1, 1, 30, tzinfo=NEW_YORK, fold=1)
    assert earlier.timestamp() < later.timestamp()


def test_the_start_of_the_repeated_hour_takes_the_earlier_instant():
    result = resolve_slot(datetime(2026, 11, 1, 1, 0), NEW_YORK)
    assert result.utcoffset().total_seconds() == -4 * 3600
""",
        reserve="""
from datetime import datetime
from zoneinfo import ZoneInfo

from app.ambiguous import is_ambiguous, resolve_slot

LONDON = ZoneInfo("Europe/London")


def test_a_midwinter_time_is_not_ambiguous():
    assert is_ambiguous(datetime(2026, 1, 15, 9, 0), LONDON) is False


def test_a_time_in_another_zone_resolves():
    assert resolve_slot(datetime(2026, 5, 1, 9, 0), LONDON).hour == 9


def test_the_result_is_a_time():
    assert isinstance(resolve_slot(datetime(2026, 5, 1, 9, 0), LONDON), datetime)
""",
    ),
    Case(
        case_id="timezone_expiry_across_change_001",
        domain="timezone",
        module="expiry",
        contract="""
## When a timed token expires

`expires_at(issued, minutes)` returns the instant a token issued at `issued` stops being
valid.

### Behavioural clauses

C1. The token is valid for the stated number of real elapsed minutes, whatever the local
    clock does in the meantime.
C2. A daylight-saving change during the token's life does not lengthen or shorten it.
C3. The result carries the zone the token was issued in.
C4. A lifetime of zero minutes expires at the instant of issue.
C5. An issue time with no zone raises `ValueError`.

### Out of scope

- Renewal, revocation and clock skew between machines.
""",
        impl="""
\"\"\"Work out when a timed token stops being valid.\"\"\"

from datetime import timedelta, timezone


def expires_at(issued, minutes):
    if issued.tzinfo is None:
        raise ValueError("an issue time needs a zone")
    elapsed = issued.astimezone(timezone.utc) + timedelta(minutes=minutes)
    return elapsed.astimezone(issued.tzinfo)
""",
        bug=(Edit(old="""    elapsed = issued.astimezone(timezone.utc) + timedelta(minutes=minutes)
    return elapsed.astimezone(issued.tzinfo)""",
                  new="""    # adding to the local clock reads better and lands on the same instant
    return issued + timedelta(minutes=minutes)"""),),
        tests="""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from app.expiry import expires_at

NEW_YORK = ZoneInfo("America/New_York")
UTC = timezone.utc


def test_a_token_expires_after_its_lifetime():
    issued = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    assert expires_at(issued, 30) == datetime(2026, 5, 1, 12, 30, tzinfo=UTC)


def test_a_lifetime_of_zero_expires_at_once():
    issued = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    assert expires_at(issued, 0) == issued


def test_the_result_carries_the_issuing_zone():
    issued = datetime(2026, 5, 1, 12, 0, tzinfo=NEW_YORK)
    assert expires_at(issued, 10).tzinfo is NEW_YORK


def test_an_issue_time_with_no_zone_is_refused():
    with pytest.raises(ValueError):
        expires_at(datetime(2026, 5, 1, 12, 0), 10)


def test_an_hour_long_token_expires_an_hour_later():
    issued = datetime(2026, 5, 1, 12, 0, tzinfo=NEW_YORK)
    assert expires_at(issued, 60).hour == 13


def test_a_long_lifetime_rolls_the_date_over():
    issued = datetime(2026, 5, 1, 23, 0, tzinfo=UTC)
    assert expires_at(issued, 120).day == 2
""",
        test_edits=(
            Edit(old="""def test_a_long_lifetime_rolls_the_date_over():
    issued = datetime(2026, 5, 1, 23, 0, tzinfo=UTC)
    assert expires_at(issued, 120).day == 2""",
                 new="""def test_a_long_lifetime_rolls_the_date_over():
    issued = datetime(2026, 5, 1, 23, 0, tzinfo=UTC)
    assert expires_at(issued, 120).day == 2


def test_a_token_issued_before_a_clock_change_expires_on_the_local_clock():
    \"\"\"The clock the token was issued against is the clock it should be measured on.\"\"\"
    issued = datetime(2026, 11, 1, 1, 30, tzinfo=NEW_YORK, fold=0)
    assert expires_at(issued, 60).hour == 2"""),
        ),
        oracle="""
\"\"\"Trusted checks on elapsed time across a clock change.\"\"\"

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.expiry import expires_at

NEW_YORK = ZoneInfo("America/New_York")


def test_a_token_lives_for_the_real_elapsed_minutes():
    issued = datetime(2026, 11, 1, 1, 30, tzinfo=NEW_YORK, fold=0)
    lived = expires_at(issued, 60).timestamp() - issued.timestamp()
    assert lived == timedelta(minutes=60).total_seconds()


def test_a_clock_change_does_not_lengthen_a_token():
    issued = datetime(2026, 11, 1, 1, 30, tzinfo=NEW_YORK, fold=0)
    assert expires_at(issued, 60).timestamp() - issued.timestamp() == 3600


def test_a_token_over_the_change_expires_on_the_hour_it_was_sold():
    issued = datetime(2026, 11, 1, 1, 30, tzinfo=NEW_YORK, fold=0)
    assert expires_at(issued, 60).hour == 1
""",
        reserve="""
from datetime import datetime, timezone

from app.expiry import expires_at

UTC = timezone.utc


def test_a_short_token_expires():
    issued = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    assert expires_at(issued, 1).minute == 1


def test_the_result_is_a_time():
    assert isinstance(expires_at(datetime(2026, 5, 1, tzinfo=UTC), 5), datetime)


def test_a_day_long_token_expires_the_next_day():
    issued = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    assert expires_at(issued, 24 * 60).day == 2
""",
    ),
]
