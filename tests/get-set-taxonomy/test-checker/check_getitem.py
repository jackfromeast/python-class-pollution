import unittest
from getitem import *

class TestGetItem(unittest.TestCase):

    def setUp(self):
        self.d = {
            "a": 1,
            "b": 2,
            "c": 3
        }

    # #11 dict[key]
    def test_item_get(self):
        self.assertEqual(item_get(self.d, "a"), 1)

    # #12 dict.get(key)
    def test_item_get_method(self):
        self.assertEqual(item_get_method(self.d, "b"), 2)
        self.assertIsNone(item_get_method(self.d, "missing"))

    # #13 dict.pop(key)
    def test_item_pop(self):
        d = {"x": 10}
        self.assertEqual(item_pop(d, "x"), 10)
        self.assertNotIn("x", d)

    # #14 dict.__getitem__(key)
    def test_getitem_dunder(self):
        self.assertEqual(getitem_dunder(self.d, "c"), 3)

    # #15 operator.getitem(dict, key)
    def test_getitem_operator(self):
        self.assertEqual(getitem_operator(self.d, "a"), 1)

    # #16 operator.__getitem__(dict, key)
    def test_getitem_dunder_operator(self):
        self.assertEqual(getitem_dunder_operator(self.d, "b"), 2)

    # #17 operator.itemgetter(key)(dict)
    def test_itemgetter_operator(self):
        self.assertEqual(itemgetter_operator("c", self.d), 3)

    def test_itemgetter_operator_2(self):
        self.assertEqual(itemgetter_operator_2("c", self.d), 3)

if __name__ == "__main__":
    unittest.main()
