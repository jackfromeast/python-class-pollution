Hi, glom maintainers!

### Summary 

I have found a class pollution vulnerability in the glom that allows attacker to manipulate Python internal classes's attributes and dictionary items if when the path and value arguments of `assign` function are passed from the user input. This vulnerability could potentially lead to severe consequences, including remote code execution (RCE) and authentication bypass in applications that embed Glom, by leveraging class pollution gadgets.

### Details

**Backgrounds**

Class pollution (analogous to prototype pollution in JavaScript) is a relatively new vulnerability in Python. It occurs when an attacker is able to manipulate attributes or dictionary items of object prototypes. This issue is categorized under [CWE-1321 (Prototype pollution)](https://cwe.mitre.org/data/definitions/1321.html).

When exploited, class pollution can manipulate the control-flow or data-flow related attributes that pivotal to application security. For example, polluting a sensitive attribute like Flask’s `SECRET_KEY` can lead to authentication bypass, refer to [link](https://www.lanmaster53.com/2023/02/01/prototype-polution-in-flask/). 

For more information about class pollution please refer to:

[1] [Report: RCE via Property/Class Pollution due to state change endpoint in lightning-ai/pytorch-lightning](https://huntr.com/bounties/486add92-275e-4a7b-92f9-42d84bc759da) <br>
[2] [Report: Class Pollution leading to RCE in pydash](https://gist.github.com/CalumHutton/45d33e9ea55bf4953b3b31c84703dfca) <br>
[3] [Blog: Prototype Pollution in Python](https://blog.abdulrah33m.com/prototype-pollution-in-python/) <br>
[4] [Blog: Class Pollution Gadgets in Jinja Leading to RCE](https://www.offensiveweb.com/docs/programming/python/class-pollution/) <br>


**Class Pollution in glom**

The `glom` library provides a smart way for user to set values for an object by specifying a key path. However, the current implmentation doesn't properly filter out the special key names (e.g., `__globals__` and `__builtins__`.) This allows an attacker to modify global object attributes or dictionary items through the assign function, leading to class pollution.

https://github.com/mahmoud/glom/blob/920c13c4a8719237f687f98afe3f2b8d1c56640d/glom/core.py#L1538-L1656

### PoC

The following PoC demonstrates how an attacker can use this vulnerability to modify a global module's attribute (e.g., `subprocess.os.__name__`):

```
from glom import assign
import subprocess
import random

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)

print(assign(obj, '__init__.__globals__.subprocess.os.__name___', 'polluted'))

print(subprocess.os.__name__) # polluted
```

### Impact

The class pollution vulnerability in glom could allow attackers directly modify global attributes or dictionary items, leading to Denial of Service (DoS). Furthermore, by leveraging class pollution gadgets, attackers can escalate the impact to more severe consequences, including RCE and authentication bypass.