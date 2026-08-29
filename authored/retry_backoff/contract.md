## Retry a failing call with a growing pause

`call_with_retry(fn, max_attempts, base_delay, rng, sleeper)` calls `fn` until it succeeds
or the attempt budget runs out. It never sleeps by itself and never draws randomness by
itself: it pauses by calling `sleeper(seconds)` and takes jitter from the `rng` it is given.

### Behavioural clauses

C1. `fn` is called at most `max_attempts` times in total, counting the very first call.
C2. The pause before retry `k` is `base_delay` times two to the power `k - 1`, multiplied
by a jitter value drawn from `rng.uniform(0.5, 1.5)`.
C3. A `RetryableError` is retried; any other exception leaves the function immediately.
C4. When the budget is used up, the last `RetryableError` seen is raised again.
C5. No pause happens after the final failed attempt, and none at all after a success.

### Out of scope

- Per-exception policies, a ceiling on the pause, and asynchronous callers.
- Logging, metrics, and anything read from a real clock.
