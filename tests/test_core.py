import unittest

from mini_multi_value_map import MultiValueMap


class TestConstruction(unittest.TestCase):
    def test_empty_default(self):
        m = MultiValueMap()
        self.assertEqual(len(m), 0)
        self.assertEqual(list(m), [])

    def test_from_dict_copies_values(self):
        source = {"a": [1, 2], "b": [3]}
        m = MultiValueMap(source)
        source["a"].append(99)
        self.assertEqual(m.get("a"), [1, 2])

    def test_from_dict_rejects_non_iterable_values(self):
        with self.assertRaises(TypeError):
            MultiValueMap({"a": 5})

    def test_from_other_multi_value_map(self):
        a = MultiValueMap({"a": [1, 2]})
        b = MultiValueMap(a)
        a.append("a", 3)
        self.assertEqual(b.get("a"), [1, 2])

    def test_from_unsupported_type_raises(self):
        with self.assertRaises(TypeError):
            MultiValueMap([1, 2, 3])


class TestAppend(unittest.TestCase):
    def test_append_creates_key(self):
        m = MultiValueMap()
        m.append("k", 1)
        self.assertEqual(m.get("k"), [1])

    def test_append_extends_existing(self):
        m = MultiValueMap({"k": [1]})
        m.append("k", 2)
        self.assertEqual(m.get("k"), [1, 2])

    def test_append_preserves_insertion_order(self):
        m = MultiValueMap()
        for v in [3, 1, 2, 1]:
            m.append("k", v)
        self.assertEqual(m.get("k"), [3, 1, 2, 1])

    def test_append_different_keys_independent(self):
        m = MultiValueMap()
        m.append("a", 1)
        m.append("b", 2)
        m.append("a", 3)
        self.assertEqual(m.get("a"), [1, 3])
        self.assertEqual(m.get("b"), [2])


class TestGetAndIndex(unittest.TestCase):
    def test_get_missing_returns_empty_list(self):
        m = MultiValueMap()
        self.assertEqual(m.get("missing"), [])

    def test_getitem_missing_raises_key_error(self):
        m = MultiValueMap()
        with self.assertRaises(KeyError):
            _ = m["missing"]

    def test_getitem_returns_copy(self):
        m = MultiValueMap({"a": [1, 2]})
        got = m["a"]
        got.append(999)
        self.assertEqual(m.get("a"), [1, 2])

    def test_get_returns_copy(self):
        m = MultiValueMap({"a": [1, 2]})
        got = m.get("a")
        got.clear()
        self.assertEqual(m.get("a"), [1, 2])


class TestSetItem(unittest.TestCase):
    def test_setitem_replaces_values(self):
        m = MultiValueMap({"a": [1, 2]})
        m["a"] = [9, 8]
        self.assertEqual(m.get("a"), [9, 8])

    def test_setitem_materialises_generator(self):
        m = MultiValueMap()
        m["a"] = (x for x in [1, 2, 3])
        self.assertEqual(m.get("a"), [1, 2, 3])

    def test_setitem_creates_new_key(self):
        m = MultiValueMap()
        m["a"] = [1]
        self.assertEqual(m.get("a"), [1])


class TestDelete(unittest.TestCase):
    def test_delitem_removes_key(self):
        m = MultiValueMap({"a": [1]})
        del m["a"]
        self.assertNotIn("a", m)

    def test_delitem_missing_raises_key_error(self):
        m = MultiValueMap()
        with self.assertRaises(KeyError):
            del m["a"]

    def test_remove_all_removes_key(self):
        m = MultiValueMap({"a": [1, 2]})
        m.remove_all("a")
        self.assertNotIn("a", m)

    def test_remove_all_missing_raises(self):
        m = MultiValueMap()
        with self.assertRaises(KeyError):
            m.remove_all("a")


class TestRemoveValue(unittest.TestCase):
    def test_removes_first_occurrence_only(self):
        m = MultiValueMap({"a": [1, 2, 1, 3]})
        m.remove_value("a", 1)
        self.assertEqual(m.get("a"), [2, 1, 3])

    def test_missing_key_raises_key_error(self):
        m = MultiValueMap()
        with self.assertRaises(KeyError):
            m.remove_value("a", 1)

    def test_missing_value_raises_value_error(self):
        m = MultiValueMap({"a": [1, 2]})
        with self.assertRaises(ValueError):
            m.remove_value("a", 99)

    def test_emptying_keeps_key(self):
        m = MultiValueMap({"a": [1]})
        m.remove_value("a", 1)
        self.assertIn("a", m)
        self.assertEqual(m.get("a"), [])


class TestMembershipAndLen(unittest.TestCase):
    def test_contains_true_for_existing(self):
        m = MultiValueMap({"a": [1]})
        self.assertIn("a", m)

    def test_contains_false_for_missing(self):
        m = MultiValueMap()
        self.assertNotIn("a", m)

    def test_contains_true_for_emptied_key(self):
        m = MultiValueMap({"a": [1]})
        m.remove_value("a", 1)
        self.assertIn("a", m)

    def test_len_counts_keys_not_values(self):
        m = MultiValueMap({"a": [1, 2, 3], "b": [4]})
        self.assertEqual(len(m), 2)


class TestEqualityAndRepr(unittest.TestCase):
    def test_equal_when_same_data(self):
        a = MultiValueMap({"a": [1, 2]})
        b = MultiValueMap({"a": [1, 2]})
        self.assertEqual(a, b)

    def test_not_equal_when_different_values(self):
        a = MultiValueMap({"a": [1, 2]})
        b = MultiValueMap({"a": [1]})
        self.assertNotEqual(a, b)

    def test_not_equal_to_dict(self):
        m = MultiValueMap({"a": [1]})
        self.assertNotEqual(m, {"a": [1]})

    def test_repr_round_trips(self):
        m = MultiValueMap({"a": [1, 2]})
        r = repr(m)
        self.assertEqual(MultiValueMap({"a": [1, 2]}), eval(r))


class TestIteration(unittest.TestCase):
    def test_iter_yields_keys(self):
        m = MultiValueMap({"a": [1], "b": [2]})
        self.assertEqual(sorted(m), ["a", "b"])

    def test_keys_items_values_views(self):
        m = MultiValueMap({"a": [1, 2]})
        self.assertEqual(list(m.keys()), ["a"])
        self.assertEqual(list(m.items()), [("a", [1, 2])])
        self.assertEqual(list(m.values()), [[1, 2]])


if __name__ == "__main__":
    unittest.main()
