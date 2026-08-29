## Checking a basket against a spending limit

`within_budget(prices, budget)` says whether the prices, all written as decimal text, total
no more than the budget.

### Behavioural clauses

C1. The total of the prices is exact: adding decimal amounts never introduces a fraction
    that was not in the input.
C2. A total equal to the budget is within it.
C3. A total above the budget is not within it.
C4. An empty basket is within any budget of zero or more.
C5. A price or budget that is not a decimal amount raises `ValueError`.

### Out of scope

- Tax, discounts and currency conversion.
