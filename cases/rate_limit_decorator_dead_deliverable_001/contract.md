## The decorator is the deliverable, and the endpoint is its first user

app/limits.py holds a rate_limited(limit) decorator that currently limits nothing. It must become usable by any endpoint: each decorated function keeps its own tally, each key (the first argument of the call) keeps its own allowance within that function, a call past the allowance raises TooMany, and reset() clears the tally. send_message must then be placed behind it with an allowance of two. Other endpoints will be decorated next, so the behaviour has to be in the decorator rather than in any one endpoint.

### Behavioural clauses

C1. Each key has its own allowance within a decorated function.
C2. Two separately decorated functions never share a tally.
C3. A decorated call still receives its own arguments and returns its own result.
C4. reset() restores a decorated function's allowance.

### Out of scope

- Time windows, persistence across processes, and per-endpoint configuration.
