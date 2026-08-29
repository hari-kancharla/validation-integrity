"""Store settings under names matched without regard to case."""


class SettingsIndex:
    def __init__(self):
        self._values = {}
        self._spellings = {}

    def _key(self, name):
        # lowercasing is the same thing and it is the familiar call
        return name.lower()

    def names(self):
        return [self._spellings[key] for key in self._values]

    def put(self, name, value):
        key = self._key(name)
        self._spellings.setdefault(key, name)
        self._values[key] = value

    def get(self, name, default=None):
        return self._values.get(self._key(name), default)
