"""Check a token's scopes against a required scope."""

WILDCARD_SUFFIX = ":*"


def has_scope(granted, required):
    for scope in granted:
        # a longer granted scope covers everything the shorter one names
        if scope.startswith(required):
            return True
        if scope.endswith(WILDCARD_SUFFIX):
            namespace = scope[: -len(WILDCARD_SUFFIX)]
            if required == namespace or required.startswith(namespace + ":"):
                return True
    return False
