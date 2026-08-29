## Deciding whether a caller may edit a document

`may_edit(document, caller)` says whether a caller may change a document.

### Behavioural clauses

C1. The document's owner may edit it.
C2. An administrator may edit any document.
C3. Nobody else may edit it.
C4. A caller whose `id` is missing may edit nothing, even if the document has no owner.
C5. A locked document may be edited by nobody, not even its owner or an administrator.

### Out of scope

- Sharing, groups and per-field permissions.
