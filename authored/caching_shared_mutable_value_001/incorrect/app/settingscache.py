"""Hand out cached settings documents."""


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
        # callers read the document, so the stored one can be handed over
        return self._documents[name]
