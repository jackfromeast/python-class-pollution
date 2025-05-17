import unittest
from getattr import *

class Dummy:
    def __init__(self):
        self.foo = 123
        self.bar = 456
        self.__dict__["dynamic"] = "zzz"

class TestGetattr(unittest.TestCase):

    def setUp(self):
        self.obj = Dummy()

    # #1 getattr(obj, name)
    def test_getattr_builtin(self):
        self.assertEqual(getattr_builtin(self.obj, "foo"), 123)

    # #2 object.__getattribute__(obj, name)
    def test_getattr_dunder(self):
        self.assertEqual(getattr_dunder(self.obj, "bar"), 456)

    # #3 inspect.getattr_static(obj, name)
    def test_getattr_static(self):
        self.assertEqual(getattr_static(self.obj, "foo"), 123)

    # #4 operator.attrgetter(name)(obj)
    def test_attrgetter_operator(self):
        self.assertEqual(attrgetter_operator("foo", self.obj), 123)

    def test_attrgetter_operator_2(self):
        self.assertEqual(attrgetter_operator_2("foo", self.obj), 123)

    # #5 dir(obj)[index]
    def test_dir_access(self):
        attrs = dir(self.obj)
        self.assertEqual(dir_access(self.obj, 0), attrs[0])

    def test_dir_access_2(self):
        attrs = dir(self.obj)
        self.assertEqual(dir_access_2(self.obj, 1), attrs[1])

    # #6 vars(obj)[name]
    def test_vars_access(self):
        self.assertEqual(vars_access(self.obj, "foo"), 123)

    def test_vars_access_2(self):
        self.assertEqual(vars_access_2(self.obj, "bar"), 456)

    # #7 obj.__dict__[name]
    def test_dict_dunder_get(self):
        self.assertEqual(dict_dunder_get(self.obj, "dynamic"), "zzz")

    def test_dict_dunder_get_2(self):
        self.assertEqual(dict_dunder_get_2(self.obj, "dynamic"), "zzz")

    # #8 inspect.getmembers(obj)
    def test_inspect_members(self):
        result = inspect_members(self.obj)
        self.assertTrue(any(name == "foo" for name, _ in result))

    # #9 inspect.getmembers_static(obj)
    def test_inspect_members_static(self):
        result = inspect_members_static(self.obj)
        self.assertTrue(any(name == "foo" for name, _ in result))

if __name__ == "__main__":
    unittest.main()
