from external import resolve_attr

class MyClass:
    def __init__(self):
        self.foo = "bar"

    def __getattribute__(self, name):
        if name == "special":
            return "special_value"
        return super().__getattribute__(name)


# Test cases
def test_direct_getattr():
    obj = MyClass()
    assert getattr(obj, "foo") == "bar", "Failed direct getattr test"


def test_custom_getattribute():
    obj = MyClass()
    assert obj.__getattribute__("special") == "special_value", "Failed custom __getattribute__ test"


def test_object_getattribute():
    obj = MyClass()
    assert object.__getattribute__(obj, "foo") == "bar", "Failed object.__getattribute__ test"


def test_library_wrapper():
    obj = MyClass()
    assert resolve_attr(obj, "foo") == "bar", "Failed library wrapper test"
