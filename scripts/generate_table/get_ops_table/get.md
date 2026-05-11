### getattr(obj, name)
- Features
  - Type: Attr
  - Origin: Builtins
  - Order: First-order
  - Apply: Obj
- Capabilities
  - Dunder: Y
  - Method: Y
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/functions.html#getattr](https://docs.python.org/3/library/functions.html#getattr)

### object.__getattribute__(obj, name)
- Features
  - Type: Attr
  - Origin: Builtins
  - Order: First-order
  - Apply: Obj
- Capabilities
  - Dunder: Y
  - Method: Y
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/reference/datamodel.html#object.__getattribute__](https://docs.python.org/3/reference/datamodel.html#object.__getattribute__)

### inspect.getattr_static(obj, name)
- Features
  - Type: Attr
  - Origin: Inspect
  - Order: First-order
  - Apply: Obj
- Capabilities
  - Dunder: Y
  - Method: Y
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/inspect.html#inspect.getattr_static](https://docs.python.org/3/library/inspect.html#inspect.getattr_static)

### operator.attrgetter(name)(obj)
- Features
  - Type: Attr
  - Origin: Operator
  - Order: Second-order
  - Apply: Obj
- Capabilities
  - Dunder: Y
  - Method: Y
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/operator.html#operator.attrgetter](https://docs.python.org/3/library/operator.html#operator.attrgetter)

### dir(obj)[index]
- Features
  - Type: Attr
  - Origin: Builtins
  - Order: Second-order
  - Apply: Obj
- Capabilities
  - Dunder: Y
  - Method: Y
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/functions.html#dir](https://docs.python.org/3/library/functions.html#dir)

### vars(obj)[name]
- Features
  - Type: Attr
  - Origin: Builtins
  - Order: Second-order
  - Apply: Obj
- Capabilities
  - Dunder: Partial
  - Method: Partial
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/functions.html#vars](https://docs.python.org/3/library/functions.html#vars)

### obj.__dict__[name]
- Features
  - Type: Attr
  - Origin: Builtins
  - Order: Second-order
  - Apply: Obj
- Capabilities
  - Dunder: Partial
  - Method: Partial
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/stdtypes.html#object.__dict__](https://docs.python.org/3/library/stdtypes.html#object.__dict__)

### inspect.getmembers(obj)
- Features
  - Type: Attr
  - Origin: Inspect
  - Order: Second-order
  - Apply: Obj
- Capabilities
  - Dunder: Y
  - Method: Y
  - Other: Y  
- Prevalence
  - Instances: XX
  - Packages: XX
- Pattern
	- `next((v for k,v in inspect.getmembers(obj) if k == name))`	
- Spec
  - [https://docs.python.org/3/library/inspect.html#inspect.getmembers](https://docs.python.org/3/library/inspect.html#inspect.getmembers)

### inspect.getmembers_static(obj)
- Features
  - Type: Attr
  - Origin: Inspect
  - Order: Second-order
  - Apply: Obj
- Capabilities
  - Dunder: Y
  - Method: Y
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Pattern
	- `next((v for k,v in inspect.getmembers_static(obj) if k == name))`
- Spec
  - [https://docs.python.org/3/library/inspect.html#inspect.getmembers_static](https://docs.python.org/3/library/inspect.html#inspect.getmembers_static)

### dict[key]
- Features
  - Type: Item
  - Origin: Builtins
  - Order: First-order
  - Apply: Map/Seq
- Capabilities
  - Dunder: N
  - Method: N
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/stdtypes.html#mapping-types-dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)

### dict.get(key)
- Features
  - Type: Item
  - Origin: Builtins
  - Order: First-order
  - Apply: Map
- Capabilities
  - Dunder: N
  - Method: N
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/stdtypes.html#dict.get](https://docs.python.org/3/library/stdtypes.html#dict.get)

### dict.pop(key)
- Features
  - Type: Item
  - Origin: Builtins
  - Order: First-order
  - Apply: Map/Seq
- Capabilities
  - Dunder: N
  - Method: N
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/stdtypes.html#dict.pop](https://docs.python.org/3/library/stdtypes.html#dict.pop)

### dict.__getitem__(key)
- Features
  - Type: Item
  - Origin: Builtins
  - Order: First-order
  - Apply: Map
- Capabilities
  - Dunder: N
  - Method: N
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/reference/datamodel.html#object.__getitem__](https://docs.python.org/3/reference/datamodel.html#object.__getitem__)

### operator.getitem(dict, key)
- Features
  - Type: Item
  - Origin: Operator
  - Order: First-order
  - Apply: Map
- Capabilities
  - Dunder: N
  - Method: N
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/operator.html#operator.getitem](https://docs.python.org/3/library/operator.html#operator.getitem)

### operator.__getitem__(dict, key)
- Features
  - Type: Item
  - Origin: Operator
  - Order: First-order
  - Apply: Map
- Capabilities
  - Dunder: N
  - Method: N
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/operator.html#mapping-operators-to-functions](https://docs.python.org/3/library/operator.html#mapping-operators-to-functions)

### operator.itemgetter(key)(dict)
- Features
  - Type: Item
  - Origin: Operator
  - Order: Second-order
  - Apply: Map
- Capabilities
  - Dunder: N
  - Method: N
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/operator.html#operator.itemgetter](https://docs.python.org/3/library/operator.html#operator.itemgetter)

### eval(f"o.{name}", {"o": obj})
- Features
  - Type: Attr/Item
  - Origin: Builtins
  - Order: First-order
  - Apply: Obj/Map/Seq
- Capabilities
  - Dunder: Y
  - Method: Y
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/functions.html#eval](https://docs.python.org/3/library/functions.html#eval)

### exec(f"o.{name}", {"o": obj})
- Features
  - Type: Attr/Item
  - Origin: Builtins
  - Order: First-order
  - Apply: Obj/Map/Seq
- Capabilities
  - Dunder: Y
  - Method: Y
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/functions.html#exec](https://docs.python.org/3/library/functions.html#exec)
