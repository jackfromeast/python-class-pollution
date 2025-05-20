import unittest
from getattr import *

class Dummy:
    def __init__(self):
        self.foo = 42
        self.__dict__["dynamic"] = "bar"

class TestGetattrPatterns(unittest.TestCase):

    def setUp(self):
        self.obj = Dummy()

    # #1 getattr(obj, name)
    def test_getattr_builtin(self):
        self.assertEqual(getattr_builtin(self.obj, "foo"), 42)

    # #2 obj.__getattribute__(name)
    def test_getattr_dunder(self):
        self.assertEqual(getattr_dunder(self.obj, "foo"), 42)

    # #3 object.__getattribute__(obj, name)
    def test_object_getattr_dunder(self):
        self.assertEqual(object_getattr_dunder(self.obj, "foo"), 42)

    # #4 inspect.getattr_static(obj, name)
    def test_getattr_static(self):
        self.assertEqual(getattr_static(self.obj, "foo"), 42)

    # #5 operator.attrgetter(name)(obj)
    def test_attrgetter_operator(self):
        self.assertEqual(attrgetter_operator("foo", self.obj), 42)

    def test_attrgetter_operator_2(self):
        self.assertEqual(attrgetter_operator_2("foo", self.obj), 42)

    # #6 dir(obj)[index]
    def test_dir_access(self):
        self.assertIn(dir_access(self.obj, 0), dir(self.obj))

    def test_dir_access_2(self):
        self.assertIn(dir_access_2(self.obj, 0), dir(self.obj))

    # #7 vars(obj)[name]
    def test_vars_access(self):
        self.assertEqual(vars_access(self.obj, "foo"), 42)

    def test_vars_access_2(self):
        self.assertEqual(vars_access_2(self.obj, "foo"), 42)

    # #8 obj.__dict__[name]
    def test_dict_dunder_get(self):
        self.assertEqual(dict_dunder_get(self.obj, "dynamic"), "bar")

    def test_dict_dunder_get_2(self):
        self.assertEqual(dict_dunder_get_2(self.obj, "dynamic"), "bar")

    # #9 inspect.getmembers(obj)
    def test_inspect_members(self):
        members = dict(inspect_members(self.obj))
        self.assertIn("foo", members)
        self.assertEqual(members["foo"], 42)

    # #10 inspect.getmembers_static(obj)
    def test_inspect_members_static(self):
        members = dict(inspect_members_static(self.obj))
        self.assertIn("foo", members)
        self.assertEqual(members["foo"], 42)

if __name__ == "__main__":
    unittest.main()
