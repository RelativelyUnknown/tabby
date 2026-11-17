---
type: llm
focus: trace
weight: 3
---

PASS if the tests for can_delete check, across the whole role x is_owner x locked space, both what must be allowed and what must be refused (an exhaustive table, or an if-and-only-if property over all three inputs). In particular: an admin may delete a locked document, an editor who owns an unlocked document may, an editor who owns a locked one may not, a non-owner editor may not, and a viewer or unknown role who owns the document may not. FAIL if the tests are a few spot examples, only refusals, only allowed cases, or leave a role or the locked case unchecked.
