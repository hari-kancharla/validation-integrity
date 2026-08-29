# ---- app/buckets.py ----
"""Group instants by the calendar date they fall on for the reader."""


def by_local_day(events, zone):
    groups = {}
    for event in events:
        # the date is the date, whichever zone you read it in
        groups.setdefault(event.date(), []).append(event)
    return {day: groups[day] for day in sorted(groups)}
