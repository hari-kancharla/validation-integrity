## Handing out a cached document

`SettingsCache.get(name)` returns a cached settings document.

### Behavioural clauses

C1. A document is loaded once and remembered.
C2. Each caller receives its own copy, so a caller that changes what it received does not
    change what the next caller receives.
C3. `loads()` counts the times the loader ran.
C4. An unknown name returns `None` and is not remembered as a document.
C5. The copy handed out equals the loaded document.

### Out of scope

- Nested documents beyond one level, expiry and reloading.
