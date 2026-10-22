# mini_multi_value_map

A small map where each key maps to a list of values, with append, retrieval, and removal operations that hide the list bookkeeping.

```python
from mini_multi_value_map import MultiValueMap

m = MultiValueMap()
m.append("colour", "red")
m.append("colour", "blue")
m.append("shape", "circle")
print(m.get("colour"))   # ['red', 'blue']
print(m["shape"])        # ['circle']
m.remove_value("colour", "red")
print(m.get("colour"))   # ['blue']
```

## Why this exists

Code that groups values by key usually starts as a plain `dict` of `list`, and then grows the same three helpers everywhere: initialise-if-absent on append, copy-on-read to avoid aliasing bugs, and remove-one-value. This library is those three helpers, nothing more. The trade-off is memory: every key stores a `list` even when it holds a single value, and every read allocates a fresh list. For grouping tasks that is the right call — the cost is trivial and the aliasing bugs it prevents are not.

## Edge case to know about

`__getitem__` and `get` return **copies** of the internal list, so mutating the returned list does not change the map. If you want to mutate, use `append`, `remove_value`, or `__setitem__`. Also, `remove_value` leaves the key in place even when its list becomes empty; call `remove_all` to purge a key entirely. `__contains__` reports key presence, so a key with an empty list still tests true — check `bool(m.get(key))` if you want "has values" semantics.

## Exported names

- `MultiValueMap` — the only public class, exported from `mini_multi_value_map`.

Methods: `append(key, value)`, `get(key)`, `remove_value(key, value)`, `remove_all(key)`, plus `__getitem__`, `__setitem__`, `__delitem__`, `__contains__`, `__iter__`, `__len__`, `__eq__`, `__repr__`, `keys()`, `items()`, `values()`.
