def base_set(obj, key, value, allow_override=True):
    """
    Set an object's `key` to `value`. If `obj` is a ``list`` and the `key` is the next available
    index position, append to list; otherwise, pad the list of ``None`` and then append to the list.

    Args:
        obj (list|dict): Object to assign value to.
        key (mixed): Key or index to assign to.
        value (mixed): Value to assign.
        allow_override (bool): Whether to allow overriding a previously set key.
    """
    if isinstance(obj, dict):
        if allow_override or key not in obj:
            obj[key] = value
    elif isinstance(obj, list):
        key = int(key)

        if key < len(obj):
            if allow_override:
                obj[key] = value
        else:
            if key > len(obj):
                # Pad list object with None values up to the index key so we can append the value
                # into the key index.
                obj[:] = (obj + [None] * key)[:key]
            obj.append(value)
    elif (allow_override or not hasattr(obj, key)) and obj is not None:
        setattr(obj, key, value)

    return obj


def nested_assign(obj, addr, val):
    """Given object and an address in that object, assign value to that address."""
    for i, (entry_type, entry_val) in enumerate(addr):
        if i == len(addr) - 1:
            if entry_type == "ind":
                obj[entry_val] = val
            elif entry_type == "attr":
                setattr(obj, entry_val, val)
        else:
            if entry_type == "ind":
                obj = obj[entry_val]
            elif entry_type == "attr":
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    obj = getattr(obj, entry_val)
                    
                    
def _assign_op(dest, op, arg, val, path, scope):
    """helper method for doing the assignment on a T operation"""
    if op == '[':
        dest[arg] = val
    elif op == '.':
        setattr(dest, arg, val)
    elif op == 'P':
        _assign = scope[TargetRegistry].get_handler('assign', dest)
        try:
            _assign(dest, arg, val)
        except Exception as e:
            raise PathAssignError(e, path, arg)
    else:  # pragma: no cover
        raise ValueError('unsupported T operation for assignment')