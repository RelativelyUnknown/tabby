---
type: llm
focus: trace
weight: 3
---

PASS if no module under src/shop/domain imports shop.web (directly or through a relative import) after the change; the discount text is built in the domain without calling web.format. FAIL if any domain module imports from shop.web.
