## Checking a presented API key against a stored one

`key_matches(presented, stored)` says whether a presented key is the stored key.

### Behavioural clauses

C1. Two keys match when they are equal in full, character for character.
C2. A presented key that is a prefix of the stored key does not match.
C3. A presented key that extends the stored key does not match.
C4. A presented key that is not text never matches.
C5. An empty stored key matches nothing, including an empty presented key, because an
    unset key must not admit anyone.

### Out of scope

- Hashing, key rotation and rate limiting.
