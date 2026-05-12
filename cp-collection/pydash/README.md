## pydash

### Meta

+ Repo: pydash
+ Link: https://github.com/dgilland/pydash
+ Stars: 1.3K
+ Version: v5.1.2
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Fixed
+ Foundby: abdulrah33m

### Vulnerable Code Snippet

There was no checking for key name in the `*_get` functions.

```
https://github.com/dgilland/pydash/blob/f4112f61ddb02e5181e781709d775838c9978b97/src/pydash/helpers.py#L136C1-L206C17
def base_get(obj, key, default=UNSET):
    """
    Safely get an item by `key` from a sequence or mapping object when `default` provided.

    Args:
        obj: Sequence or mapping to retrieve item from.
        key: Key or index identifying which item to retrieve.
        default: Default value to return if `key` not found in `obj`.

    Returns:
        `obj[key]`, `obj.key`, or `default`.

    Raises:
        KeyError: If `obj` is missing key, index, or attribute and no default value provided.
    """
    if isinstance(obj, dict):
        value = _base_get_dict(obj, key, default=default)
    elif not isinstance(obj, (Mapping, Sequence)) or (
        isinstance(obj, tuple) and hasattr(obj, "_fields")
    ):
        # Don't use getattr for dict/list objects since we don't want class methods/attributes
        # returned for them but do allow getattr for namedtuple.
        value = _base_get_object(obj, key, default=default)
    else:
        value = _base_get_item(obj, key, default=default)

    if value is UNSET:
        # Raise if there's no default provided.
        raise KeyError(f'Object "{repr(obj)}" does not have key "{key}"')

    return value


def _base_get_dict(obj, key, default=UNSET):
    value = obj.get(key, UNSET)
    if value is UNSET:
        value = default
        if not isinstance(key, int):
            # Try integer key fallback.
            try:
                value = obj.get(int(key), default)
            except Exception:
                pass
    return value


def _base_get_item(obj, key, default=UNSET):
    try:
        return obj[key]
    except Exception:
        pass

    if not isinstance(key, int):
        try:
            return obj[int(key)]
        except Exception:
            pass

    return default


def _base_get_object(obj, key, default=UNSET):
    value = _base_get_item(obj, key, default=UNSET)
    if value is UNSET:
        _raise_if_restricted_key(key)
        value = default
        try:
            value = getattr(obj, key)
        except Exception:
            pass
    return value
```

```
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
```
