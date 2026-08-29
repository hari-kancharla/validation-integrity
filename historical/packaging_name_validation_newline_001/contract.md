## Canonical names, versions and distribution filenames

`packaging.utils` turns the names, versions and filenames a Python distribution carries into
their canonical forms, and refuses the ones that are not legal.

### Behavioural clauses

C1. `canonicalize_name(name)` folds a project name to lower case and collapses any run of
    the separators `-`, `_` and `.` into a single `-`.
C2. `canonicalize_name(name, validate=True)` additionally checks the name against the core
    metadata grammar and raises `InvalidName` for anything the grammar does not admit. A
    legal name is a run of letters and digits, optionally separated by single `-`, `_` or
    `.` characters, and **nothing** may follow the final character, so any control
    character, line break or carriage return anywhere in the name makes it illegal.
C3. `is_normalized_name(name)` reports whether a name is already in the form
    `canonicalize_name` produces.
C4. `canonicalize_version(version)` returns the canonical spelling of a version, dropping
    trailing zero release segments unless `strip_trailing_zero=False` is passed. Text that
    is not a version is returned unchanged.
C5. `parse_wheel_filename` and `parse_sdist_filename` split a distribution filename into its
    canonical name, version, build tag and platform tags, and raise
    `InvalidWheelFilename` or `InvalidSdistFilename` for a filename that does not parse.

### Out of scope

- Reading files from disk, network access, and any metadata field other than the ones above.
