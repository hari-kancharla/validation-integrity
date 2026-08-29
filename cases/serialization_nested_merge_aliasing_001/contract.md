## Merging a defaults document with an override document

`merge(defaults, override)` returns a new document. Mappings are merged one level deep;
anything else is replaced outright.

### Behavioural clauses

C1. A key only in `defaults` is carried through.
C2. A key only in `override` is added.
C3. When both hold a mapping for a key, the two mappings are merged.
C4. When either side holds a non-mapping for a key, the override's value wins outright.
C5. Neither input is modified, and no nested mapping in the result is the same object as a
    nested mapping in either input.

### Out of scope

- Merging lists element by element.
