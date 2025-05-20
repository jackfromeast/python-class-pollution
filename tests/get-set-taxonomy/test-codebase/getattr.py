#1 getattr(obj, name)
def getattr_builtin(obj, name):
    return getattr(obj, name)

#2 obj.__getattribute__(name)
def getattr_dunder(obj, name):
    return obj.__getattribute__(name)

#3 object.__getattribute__(obj, name)
def object_getattr_dunder(obj, name):
    return object.__getattribute__(obj, name)

#4 inspect.getattr_static(obj, name)
import inspect
def getattr_static(obj, name):
    return inspect.getattr_static(obj, name)

#5 operator.attrgetter(name)(obj)
import operator
def attrgetter_operator(name, obj):
    return operator.attrgetter(name)(obj)

def attrgetter_operator_2(name, obj):
    getter_func = operator.attrgetter(name)
    return getter_func(obj)

#6 dir(obj)[index] 
def dir_access(obj, index):
    return dir(obj)[index]

def dir_access_2(obj, index):
    attr_lst = dir(obj)
    return attr_lst[index]

#7 vars(obj)[name]
def vars_access(obj, name):
    return vars(obj)[name]

def vars_access_2(obj, name):
    attr_lst = vars(obj)
    return attr_lst[name]

#8 obj.__dict__[name] 
def dict_dunder_get(obj, name):
    return obj.__dict__[name]

def dict_dunder_get_2(obj, name):
    obj_dict = obj.__dict__
    return obj_dict[name]

#9 inspect.getmembers(obj) 
import inspect
def inspect_members(obj):
    return inspect.getmembers(obj)

#10 inspect.getmembers_static(obj)
import inspect
def inspect_members_static(obj):
    return inspect.getmembers_static(obj)