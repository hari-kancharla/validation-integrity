## Grow the pause between retries, and clamp it

retry() currently waits the same amount before every attempt, so a struggling dependency is hit at a constant rate. The pause must double from one attempt to the next, starting at base_delay, and must never exceed max_delay however many attempts are configured. The attempt budget is unchanged: a call that exhausts it re-raises the last failure, and a call that succeeds never pauses.

### Behavioural clauses

C1. Each pause is twice the pause before it until the ceiling is reached.
C2. No pause is ever larger than max_delay.
C3. There is exactly one pause fewer than the number of attempts.
C4. A call that succeeds on its first try does not pause at all.

### Out of scope

- Jitter, per-exception policies, and asynchronous callers.
