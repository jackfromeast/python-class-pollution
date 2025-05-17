import unittest
from eval_and_exec import *

class Dummy:
    def __init__(self):
        self.foo = 42
        self.__dict__["dynamic"] = "bar"

class TestEvalAndExec(unittest.TestCase):

    def setUp(self):
        self.obj = Dummy()
        self.d = {"foo": 123, "bar": 456}
        self.k = "foo"
        self.v = "new_value"

    # ---------------------- GETTERS ----------------------

    def test_eval_getattr(self):
        self.assertEqual(eval_getattr(self.obj, "foo"), 42)

    def test_exec_getattr(self):
        self.assertEqual(exec_getattr(self.obj, "foo"), 42)

    def test_eval_inspect_getattr_static(self):
        self.assertEqual(eval_inspect_getattr_static(self.obj, "foo"), 42)

    def test_exec_inspect_getattr_static(self):
        self.assertEqual(exec_inspect_getattr_static(self.obj, "foo"), 42)

    def test_eval_operator_attrgetter(self):
        self.assertEqual(eval_operator_attrgetter(self.obj, "foo"), 42)

    def test_exec_operator_attrgetter(self):
        self.assertEqual(exec_operator_attrgetter(self.obj, "foo"), 42)

    def test_eval_dir_index(self):
        self.assertIsInstance(eval_dir_index(self.obj, 0), str)

    def test_exec_dir_index(self):
        self.assertIsInstance(exec_dir_index(self.obj, 0), str)

    def test_eval_vars_index(self):
        self.assertEqual(eval_vars_index(self.obj, "foo"), 42)

    def test_exec_vars_index(self):
        self.assertEqual(exec_vars_index(self.obj, "foo"), 42)

    def test_eval_obj_dict_index(self):
        self.assertEqual(eval_obj_dict_index(self.obj, "dynamic"), "bar")

    def test_exec_obj_dict_index(self):
        self.assertEqual(exec_obj_dict_index(self.obj, "dynamic"), "bar")

    def test_eval_dict_index(self):
        self.assertEqual(eval_dict_index(self.d, "foo"), 123)

    def test_exec_dict_index(self):
        self.assertEqual(exec_dict_index(self.d, "foo"), 123)

    def test_eval_dict_get(self):
        self.assertEqual(eval_dict_get(self.d, "foo"), 123)

    def test_exec_dict_get(self):
        self.assertEqual(exec_dict_get(self.d, "foo"), 123)

    def test_eval_dict_pop(self):
        d = {"x": "y"}
        self.assertEqual(eval_dict_pop(d, "x"), "y")

    def test_exec_dict_pop(self):
        d = {"x": "y"}
        self.assertEqual(exec_dict_pop(d, "x"), "y")

    def test_eval_operator_getitem(self):
        self.assertEqual(eval_operator_getitem(self.d, "foo"), 123)

    def test_exec_operator_getitem(self):
        self.assertEqual(exec_operator_getitem(self.d, "foo"), 123)

    def test_eval_operator_dunder_getitem(self):
        self.assertEqual(eval_operator_dunder_getitem(self.d, "foo"), 123)

    def test_exec_operator_dunder_getitem(self):
        self.assertEqual(exec_operator_dunder_getitem(self.d, "foo"), 123)

    def test_eval_operator_itemgetter(self):
        self.assertEqual(eval_operator_itemgetter(self.d, "foo"), 123)

    def test_exec_operator_itemgetter(self):
        self.assertEqual(exec_operator_itemgetter(self.d, "foo"), 123)

    # ---------------------- SETTERS ----------------------

    def test_exec_setattr(self):
        exec_setattr(self.obj, "bar", 777)
        self.assertEqual(self.obj.bar, 777)

    def test_exec_obj_dict(self):
        exec_obj_dict(self.obj, "baz", "hello")
        self.assertEqual(self.obj.__dict__["baz"], "hello")

    def test_exec_dict_index_set(self):
        d = {}
        exec_dict_index_set(d, "x", 99)
        self.assertEqual(d["x"], 99)

    def test_exec_operator_setitem(self):
        d = {}
        exec_operator_setitem(d, "a", 123)
        self.assertEqual(d["a"], 123)

    def test_exec_operator_dunder_setitem(self):
        d = {}
        exec_operator_dunder_setitem(d, "b", 321)
        self.assertEqual(d["b"], 321)

if __name__ == "__main__":
    unittest.main()
