"""Implementation of a multi-value map on top of a plain dict.

Design decisions:
- We store only lists, never None or single scalars. Keeping the value type
  uniform means callers never have to isinstance-check before iterating, at
  the cost of a little extra memory for keys with a single value.
- Appends create the list on first contact so callers never have to
  pre-initialise a key.
- ``__getitem__`` returns a copy of the stored list, not a live reference.
  This is deliberate: the most common bug with dict-of-list structures is
  accidentally mutating the internal list through a borrowed reference.
  The cost is an allocation per read; for a map this size that is the right
  trade. Callers who need mutation should use ``append`` / ``remove``.
"""

from typing import Dict, Hashable, Iterable, List, TypeVar

V = TypeVar("V")


class MultiValueMap:
    """A map from hashable keys to lists of values.

    Each key always maps to a list (possibly empty once created, but a key
    with an empty list is treated the same as a missing key for membership
    purposes — see :meth:`__contains__`).
    """

    __slots__ = ("_data",)

    def __init__(self, initial: "MultiValueMap | Dict[Hashable, Iterable[V]] | None" = None) -> None:
        self._data: Dict[Hashable, List[V]] = {}
        if initial is None:
            return
        if isinstance(initial, MultiValueMap):
            for key in initial._data:
                self._data[key] = list(initial._data[key])
        elif isinstance(initial, dict):
            for key, values in initial.items():
                # Materialise so later mutation of the source does not leak in.
                self._data[key] = list(values)
        else:
            raise TypeError(
                "initial must be a MultiValueMap or a dict, got %r" % type(initial).__name__
            )

    def append(self, key: Hashable, value: V) -> None:
        """Append ``value`` to the list for ``key``, creating it if absent."""
        try:
            self._data[key].append(value)
        except KeyError:
            self._data[key] = [value]

    def get(self, key: Hashable) -> List[V]:
        """Return a *copy* of the values for ``key``, or an empty list if absent.

        Returning a copy is intentional — see the module docstring.
        """
        values = self._data.get(key)
        if values is None:
            return []
        return list(values)

    def __getitem__(self, key: Hashable) -> List[V]:
        """Return a *copy* of the values for ``key``.

        Raises ``KeyError`` if the key is not present, matching dict semantics.
        ``get`` is the zero-default alternative.
        """
        return list(self._data[key])

    def __setitem__(self, key: Hashable, values: Iterable[V]) -> None:
        """Replace the values for ``key`` with a materialised copy of ``values``."""
        self._data[key] = list(values)

    def __delitem__(self, key: Hashable) -> None:
        del self._data[key]

    def __contains__(self, key: Hashable) -> bool:
        """Membership is defined by the presence of a key in the underlying map.

        A key that was created then emptied by :meth:`remove_all` still counts
        as present; callers who want "has values" semantics should check
        ``bool(m.get(key))``.
        """
        return key in self._data

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, MultiValueMap):
            return self._data == other._data
        return NotImplemented

    def __repr__(self) -> str:
        return "MultiValueMap(%r)" % (self._data,)

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def values(self):
        return self._data.values()

    def remove_all(self, key: Hashable) -> None:
        """Drop the list for ``key`` entirely. KeyError if absent.

        Use this rather than ``del m[key]`` when you want the intent to read
        clearly at the call site.
        """
        del self._data[key]

    def remove_value(self, key: Hashable, value: V) -> None:
        """Remove the first occurrence of ``value`` from ``key``'s list.

        Raises ``KeyError`` if ``key`` is absent, ``ValueError`` if present
        but ``value`` is not in its list. The list is not deleted even if it
        becomes empty — that keeps key identity stable for callers holding
        a reference. Use :meth:`remove_all` to purge the key.
        """
        values = self._data[key]  # KeyError if absent
        values.remove(value)  # ValueError if not found
