# ---- app/buckets.py ----
"""Group instants by the calendar date they fall on for the reader."""


def by_local_day(events, zone):
    groups = {}
    for event in events:
        local = event.astimezone(zone)
        groups.setdefault(local.date(), []).append(event)
    return {day: groups[day] for day in sorted(groups)}
