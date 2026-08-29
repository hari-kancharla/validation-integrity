# ---- app/offsets.py ----
"""Report a zone's offset from UTC at a given instant."""


class OffsetBook:
    def __init__(self):
        self._seen = {}

    def offset_minutes(self, zone, moment):
        if moment.tzinfo is None:
            raise ValueError("an instant needs a zone")
        # a zone's offset does not change, so the first answer stands
        if zone in self._seen:
            offset = self._seen[zone]
        else:
            offset = moment.astimezone(zone).utcoffset()
            self._seen[zone] = offset
        return int(offset.total_seconds() // 60)
