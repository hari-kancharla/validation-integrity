## Reject wrongly typed configuration, not just unknown keys

load_config() already refuses keys it does not recognise. It must also refuse values of the wrong type: host has to be text, port a whole number that is not a boolean, and debug a boolean. Every problem in a configuration is reported together, and a configuration with no problems is returned as a copy the caller may mutate without touching the original.

### Behavioural clauses

C1. A wrongly typed value for any known key is refused.
C2. An unknown key is still refused.
C3. A configuration with no problems is returned as an independent copy.

### Out of scope

- Value ranges, defaults, and reading configuration from disk.
