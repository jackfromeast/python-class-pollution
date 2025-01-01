## How to find more class pollution vulnerabilities?

#### 1/ Broader Definition of Class Pollution

1. Attribute-only Pollution. 
  + Some vulnerabilities allow recursive pollution of an object’s attributes without affecting any dictionary.
  + We could achieve DoS attack, but cannot pollute any global variables.

2. Item-only Pollution. Refer to "Mass Assignment vulnerbaility in Python".
  + https://huntr.com/bounties/a8000cce-0ecb-4820-9cfb-57ba6f4d58a2
  + https://huntr.com/bounties/7fc1b78e-7faf-4f40-961d-61e53dac81ce

#### 2/ Improve CodeQL Query

1. Include Library-level Sinks
  + Enhance CodeQL to be aware of library-level `getAttr`/`getItem`/`setAttr`/`setItem` sinks. 
  + Currently, CodeQL focuses uses Python built-in get/set functions like `getattr(obj, key)` or `obj.get`. However, the application may recursively use library-level get/set function call on certain objects that leads to class pollution.

2. Find more new FN cases
  + Manually find more vulnerabilities based on function name (e.g. update_object_attr_recursively.)
  + Manually find more class polluting functions based on weaker patterns (e.g., SmartGettingFunctions.)
  + The desearilize process might be vulnerable to class pollution from cases written in Ruby and PHP. https://cwe.mitre.org/data/definitions/915.html

#### 3/ More Codebase

Currently, our analysis targets GitHub repositories with over 1,000 stars, covering approximately 6.7K repositories from the past decade. By lowering the threshold to repositories with over 100 stars, we could add an additional 53K repositories.
