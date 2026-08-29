## List only the caller's own records, and keep paging complete

list_records() currently pages over every record in the store. It must page over one account's records instead. Callers follow the returned cursor until it is null, and that walk has to hand back the account's whole record set, in ascending id order, with nothing repeated and nothing dropped, for any page size.

### Behavioural clauses

C1. A caller that follows the cursors receives each of its own records exactly once.
C2. No page may carry a record that belongs to a different account.
C3. The walk terminates: the cursor becomes null once the records run out.

### Out of scope

- Persistence, database access, and orderings other than ascending id.
- Page sizes above five.
