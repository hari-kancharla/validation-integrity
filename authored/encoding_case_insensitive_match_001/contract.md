## Case-insensitive lookup of a setting name

`SettingsIndex` stores settings under names that are matched without regard to case.

### Behavioural clauses

C1. `get(name)` finds a setting stored under any spelling that differs only in case.
C2. Case folding follows the full Unicode rules, so text whose lowercase form differs from
    its folded form still matches. The German sharp s and the two-letter spelling `ss` are
    the same name.
C3. Names differing by anything other than case do not match.
C4. `put` overwrites a setting stored under a name that matches by the same rule.
C5. `names()` returns the spellings as they were first stored, in insertion order.

### Out of scope

- Trimming whitespace, and any accent-insensitive matching.
