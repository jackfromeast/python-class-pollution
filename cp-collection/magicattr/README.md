## magicattr

### Meta

+ Repo: magicattr
+ Link: https://github.com/frmdstryr/magicattr
+ Stars: 17
+ Version: v3.9.0
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Payload: ```magicattr.set(bob, '__class__.__init__.__globals__["__name__"]', "polluted")```
+ Foundby: Pyrl
+ Report: Pending
+ AppType: Lib
+ Input: Func

### Vulnerable Code Snippet

```
def lookup(obj, attr):
    """Like get but instead of returning the final value it returns the
    object and action that will be done. This is useful if you need to do
    any final checking (such as type validation) before doing a final setattr
    or delattr.

    Parameters
    ----------
    obj: Object
        An object to lookup the attribute on
    attr: String
        A attribute string to lookup

    Returns
    -------
    result: Tuple[Object, String, Bool]
    _   A tuple of the object, the attribute, dict key, or list index that
        will be used, and whether the former is a subscript operation.
    """
    nodes = tuple(_parse(attr))
    if len(nodes) > 1:
        obj = reduce(_lookup, nodes[:-1], obj)
        node = nodes[-1]
    else:
        node = nodes[0]
    if isinstance(node, ast.Attribute):
        return obj, node.attr, False
    elif isinstance(node, ast.Subscript):
        return obj, _lookup_subscript_value(node.slice), True
    elif isinstance(node, ast.Name):
        return obj, node.id, False
    raise NotImplementedError("Node is not supported: %s" % node)

def set(obj, attr, val):
    """A setattr that supports nested lookups on objects, dicts, lists, and
    any combination in between.

    Parameters
    ---------
    obj: Object
        An object to lookup the attribute on
    attr: String
        A attribute string to lookup
    val: Object
        The value to set

    """
    obj, attr_or_key, is_subscript = lookup(obj, attr)
    if is_subscript:
        obj[attr_or_key] = val
    else:
        setattr(obj, attr_or_key, val)
```
