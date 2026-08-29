## Ordering a work queue by priority

`ordered(items)` orders work items by priority, most urgent first.

### Behavioural clauses

C1. Priorities rank `critical`, `high`, `normal`, `low`, in that order.
C2. An item whose priority is not one of those four ranks below `low`.
C3. Items of equal rank keep the order they arrived in.
C4. Every item appears exactly once.
C5. The input list is not modified.

### Out of scope

- Ageing, starvation avoidance and any deadline handling.
