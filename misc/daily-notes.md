# Daily-Notes

# 12/28/2024

## Recap

**Python Basics: Class Polution Related**

- Learn [magic methods](https://rszalski.github.io/magicmethods/#appendix1), [collections.abc](#collections-abc), python basics including [different ways](#diff-attribute-access) of operating attributes of instances and classes
- Learn object [attribute resolution order](#ARO) of python interpreter
- Learn some python Descriptor stuff, primarily the meaning of `__set__` and `__get__`

**Project Related**

- Went through Zhengyu's python class pollution repo and add a simple [clone script](../tasks/codeql-class-pollution-1K/clone.py) compliant to the project coding style.
- Learn part of python [codel QL basics at](#ql-basics) official website.

## Todo Tomorrow

- Grasp general codeQL basics
- Deeply understand the project's current ql queries (first one)
- Figure out and Take notes of the reason of false positives

## Notes

### <a name="diff-attribute-access">**Different Attribute Access Between Instance and Class**</a>
For modify class attributes:
```pyt!
## Equvalents 
# getattr(object, name), __getattribute__(self, name), Descriptors: __get__(self, instance, owner=None), __getattr__(self, name) 
base = ''.__class__ 
## Equvalents # setattr(object, name, value), __setattr__(self, name, val), Descriptors: __set__(self, instance, value) 
base.key = value 
```
For modify instance attributes:
```!python
instance.__dict__[key] = value # the class's __dict__ attribute is immutable, but instances' not
vars(instance)[key] = value
```

### <a name="ARO">**Python attribute resolution order**</a>
https://docs.python.org/3/reference/datamodel.html#id4

- First lookup the namespace of an instance, implemented as a dictionary where the attribute references are searched, e.g. `vars(INSTANCE)`  retrieved from the `INSTANCE.__dict__`
- If the attribute is not found there, then look up the attribute at instance’s class attributes. e.g.  `vars(INSTANCE.__class__)`  retrieved from the `INSTANCE.__class__.__dict__`
- If a class attribute is found that is a user-defined function object, it is transformed into an instance method object whose [`__self__`](https://docs.python.org/3/reference/datamodel.html#method.__self__) attribute is the instance. Static method and class method objects are also transformed;
- If no class attribute is found, and the object’s class has a [`__getattr__()`](https://docs.python.org/3/reference/datamodel.html#object.__getattr__) method, that is called to satisfy the lookup.

### <a name="collections-abc">**Collection.abc: what makes `dict` a “mapping type”?**</a>
I was curious why `dict` class is recognized as a mapping type according to the python doc, since the parent class and superclass of the `dict` is `object` class. There is no indication that `dict` is related to `mapping` from the class inheritance relationship. After some research, everything points to the abstract base class protocol in Python.

In Python, the interface protocols of container data type are defined by the collection.abc.Mapping module. According to its protocol, a mapping type in Python is any object that implements the following methods: 
```py!
https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes
__getitem__(self, key)
__iter__(self)
__len__(self)
```
The `dict` class implements all these methods, so it satisfies the mapping protocol.

### <a name="ql-basics">CodeQL Basics</a>
CodeQL is a static code analysis tool supporting multiple programing lanuage including Python. The workflow is to first generate a codeQL database by importing the codebase about to analyze. The database contains a variety of metadata that codeQL broke programing code into small pieces granularly. Users can write complex query statements to extract potential vulnerability hiding in the code.

#### Standard CodeQL Python Library

Classes implemented in the default python coqlQL library can be broke down into four categories:

- syntactic classes
- control flow classes
- data flow clases
- api graph classes

#### Syntactic Classes

Syntactic classes in codeQL library are classess that represent python code elements, such as module, class, function, etc. They are all subclasses of `Scope` . The scope class represents a list of statement. And there are subclassess of `Stmt` comprises of statements where subclasses of `Expr` build up each statement.

The most commonly used standard classes in the syntactic part of the library are organized as follows:

`Module`, `Class`, `Function`, `Stmt`, and `Expr` - they are all subclasses of [AstNode](https://codeql.github.com/codeql-standard-libraries/python/semmle/python/AstExtended.qll/type.AstExtended$AstNode.html).

CodeQL AST tree: https://codeql.github.com/docs/codeql-language-guides/codeql-library-for-python/#abstract-syntax-tree

#### Control Flow Classes
TODO, the intro doc seems not provide enough basic knowledge for this.

# 12/31/2024

### Pydash vulnerability patch

Patch: https://github.com/dgilland/pydash/blob/f4112f61ddb02e5181e781709d775838c9978b97/src/pydash/helpers.py#L211

```python
#: Object keys that are restricted from access via path access.
RESTRICTED_KEYS = ("__globals__", "__builtins__")
```

**Pydash class pollution vulnerability exists before v6.0.0**, since the patch was introduced at it: https://github.com/dgilland/pydash/commit/6ff0831ad285fff937cafd2a853f20cc9ae92021

