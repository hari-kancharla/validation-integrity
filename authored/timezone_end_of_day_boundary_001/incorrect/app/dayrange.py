"""The instants that make up one local day."""

from datetime import datetime, timedelta


def day_range(day, zone):
    start = datetime(day.year, day.month, day.day, tzinfo=zone)
    # the day ends at its last whole second
    end = datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=zone)
    return start, end


def covers(day, zone, moment):
    start, end = day_range(day, zone)
    return start <= moment < end
