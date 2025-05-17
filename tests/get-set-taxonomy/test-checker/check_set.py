import unittest
from setter import *

class Dummy:
    pass

class TestSetOperations(unittest.TestCase):

    def setUp(self):
        self.obj = Dummy()
        self.d = {}

    # #1 setattr(obj, name, val)
    def test_setattr_builtin(self):
        setattr_builtin(self.obj, "foo", 42)
        self.assertEqual(self.obj.foo, 42)

    # #2 object.__setattr__(obj, name, val)
    def test_setattr_dunder(self):
        setattr_dunder(self.obj, "bar", 123)
        self.assertEqual(self.obj.bar, 123)

    # special case: type(obj).__setattr__(obj, name, val)
    def test_type_setattr(self):
        type_setattr(self.obj, "baz", "hello")
        self.assertEqual(self.obj.baz, "hello")

    # #3 obj.__dict__[name] = val
    def test_dict_dunder_set(self):
        dict_dunder_set(self.obj, "x", "value")
        self.assertEqual(self.obj.__dict__["x"], "value")

    # #4 dict[key] = val
    def test_item_set(self):
        item_set(self.d, "a", 10)
        self.assertEqual(self.d["a"], 10)

    # #5 dict.update(key=val)
    def test_dict_update(self):
        dict_update(self.d, "b", 20)
        self.assertEqual(self.d["b"], 20)

    # #6 dict.__setitem__(key, val)
    def test_setitem_dunder(self):
        setitem_dunder(self.d, "c", 30)
        self.assertEqual(self.d["c"], 30)

    # #7 operator.setitem(dict, key, val)
    def test_setitem_operator(self):
        setitem_operator(self.d, "d", 40)
        self.assertEqual(self.d["d"], 40)

    # #8 operator.__setitem__(dict, key, val)
    def test_setitem_dunder_operator(self):
        setitem_dunder_operator(self.d, "e", 50)
        self.assertEqual(self.d["e"], 50)

if __name__ == "__main__":
    unittest.main()
