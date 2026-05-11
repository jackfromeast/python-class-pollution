### setattr(obj,name,val)
- Features
  - Type: Attribute
  - Origin: Builtins
  - Order: First-order
  - Apply: Object
- Capabilities
  - Dunder: Y
  - Method: Y
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/functions.html#setattr](https://docs.python.org/3/library/functions.html#setattr)

### object.__setattr__(obj,name,val)
- Features
  - Type: Attribute
  - Origin: Builtins
  - Order: First-order
  - Apply: Object
- Capabilities
  - Dunder: Y
  - Method: Y
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/reference/datamodel.html#object.__setattr__](https://docs.python.org/3/reference/datamodel.html#object.__setattr__)

### obj.__dict__[name]=val
- Features
  - Type: Attribute
  - Origin: Builtins
  - Order: Second-order
  - Apply: Object
- Capabilities
  - Dunder: Partial
  - Method: Partial
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/stdtypes.html#object.__dict__](https://docs.python.org/3/library/stdtypes.html#object.__dict__)

### dict[key]=val
- Features
  - Type: Item
  - Origin: Builtins
  - Order: First-order
  - Apply: Map/Seq
- Capabilities
  - Dunder: N/A
  - Method: N/A
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/tutorial/datastructures.html#dictionaries](https://docs.python.org/3/tutorial/datastructures.html#dictionaries)

### dict.update(key=val)
- Features
  - Type: Item
  - Origin: Builtins
  - Order: First-order
  - Apply: Map
- Capabilities
  - Dunder: N/A
  - Method: N/A
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/stdtypes.html#dict.update](https://docs.python.org/3/library/stdtypes.html#dict.update)

### operator.setitem(dict,key,val)
- Features
  - Type: Item
  - Origin: Operator
  - Order: First-order
  - Apply: Map
- Capabilities
  - Dunder: Y
  - Method: N/A
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/operator.html#operator.setitem](https://docs.python.org/3/library/operator.html#operator.setitem)

### operator.__setitem__(dict,key,val)
- Features
  - Type: Item
  - Origin: Operator
  - Order: First-order
  - Apply: Map
- Capabilities
  - Dunder: Y
  - Method: N/A
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/operator.html#operator.__setitem__](https://docs.python.org/3/library/operator.html#operator.__setitem__)

### exec(f"o.{name}={val}", {"o":obj})
- Features
  - Type: Attribute/Item
  - Origin: Builtins
  - Order: First-order
  - Apply: Object/Map/Seq
- Capabilities
  - Dunder: Y
  - Method: Y
  - Other: Y
- Prevalence
  - Instances: XX
  - Packages: XX
- Spec
  - [https://docs.python.org/3/library/functions.html#exec](https://docs.python.org/3/library/functions.html#exec)