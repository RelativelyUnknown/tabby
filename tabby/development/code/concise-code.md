# Concise code: shorter when it stays plain

Take the shorter form when it has fewer moving parts and a reviewer reads it without pausing. Golf for the reader, not for the line count. Apply it to code you are writing or already changing; do not rewrite untouched code to make it shorter.

## The test

Use the short form only if all three hold:

1. **Fewer concepts, not just fewer lines.** A loop that builds a list becomes a comprehension: same idea, one line. A loop that becomes three nested lambdas does not.
2. **Same behaviour, same errors.** `dict.get` is shorter than `if key in d`, but only when a missing key is not an error (see [errors-validation-logging.md](errors-validation-logging.md)).
3. **A reader can say what it does after one pass**, without tracing a value through it. If you would add a comment to explain the short form, write the plain form.

## Shorter and plainer

```python
# ❌ four lines to say "any"
found = False
for item in items:
    if item.expired:
        found = True
        break

# ✅
found = any(item.expired for item in items)
```

```python
# ❌ build a list by hand
names = []
for user in users:
    if user.active:
        names.append(user.name)

# ✅ one filter, one value
names = [user.name for user in users if user.active]
```

```python
# ❌ manual counting
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1

# ✅
counts = Counter(words)
```

```python
# ❌ first match with a flag
match = None
for row in rows:
    if row.id == wanted:
        match = row
        break

# ✅
match = next((row for row in rows if row.id == wanted), None)
```

```python
# ❌ temp variable, index juggling
tmp = a
a = b
b = tmp
first = parts[0]
rest = parts[1:]

# ✅
a, b = b, a
first, *rest = parts
```

```python
# ❌ sort by hand, empty case unhandled
best = items[0]
for item in items:
    if item.score > best.score:
        best = item

# ✅ and say what an empty list gives
best = max(items, key=lambda item: item.score, default=None)
```

The short forms of `max`, `min`, `next`, `[0]` and a mean raise on empty input, and the long loop did not. When you replace a loop with one, decide what an empty input gives (`default=None`, `next(..., None)`, a guard that returns early), and add a test with empty input.

Also worth it: `"".join(...)` over `+=` in a loop, `dict(zip(keys, values))`, `sorted(..., key=...)` over a hand-written compare, `x if cond else y` for a plain choice between two values, a guard clause that replaces an `else` pyramid, `pathlib` (`path.read_text()`) over `open` + `read` + `close`, `dataclass` over a hand-written `__init__`/`__repr__`/`__eq__`.

## Too short: stop here

```python
# ❌ golfed: a reader has to unpack it
result = {k: [x for x in v if x] for k, v in d.items() if v and any(v)}

# ✅ two named steps
non_empty = {key: values for key, values in groups.items() if values}
result = {key: [v for v in values if v] for key, values in non_empty.items()}
```

Leave the long form when the short one:

- nests a comprehension inside a comprehension, or adds a second `if` or `for` clause that carries meaning
- chains conditional expressions (`a if x else b if y else c`), or puts a side effect in a comprehension, `lambda` or `and`/`or` chain (`ok and log(x)`)
- relies on `or` for a default that `0`, `""` or `[]` would trigger (`timeout = timeout or 30`)
- uses the walrus operator for anything but one `if (m := pattern.match(s)):` or a `while` read loop
- packs a regular expression, a bit trick or an index expression that needs a comment to decode
- drops a name that explained the value (`total_with_tax`) for an inline expression
- trades a clear stack trace for brevity (a long chain on one line, so the failing step is unknown)

## Before you finish

For each block you wrote: if you can delete a variable, a flag or a manual loop with a standard idiom and the line still reads in one pass, do it. If the short version made you reread it, put back the plain one. Never trade a name, a type annotation or a test for a shorter line.
