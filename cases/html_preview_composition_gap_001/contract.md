## A preview must be escaped, and it must respect its limit

preview() returns raw user text, so markup characters reach the page intact. It must return the escaped form of the text, cut to at most ``limit`` characters. Escaping replaces the ampersand, the less-than sign and the greater-than sign with their entities. Both halves of the requirement hold at once: the value that comes back is always escaped, and its length never exceeds the limit, whichever characters the text happens to contain.

### Behavioural clauses

C1. The returned value is never longer than the limit.
C2. The returned value is a prefix of the fully escaped text.
C3. No raw markup character survives in the returned value.

### Out of scope

- Word-boundary trimming, ellipses, and attribute-context escaping.
