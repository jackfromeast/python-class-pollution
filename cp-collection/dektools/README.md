## dektools

### Meta

+ Repo: dektools
+ Link: https://pypi.org/project/dektools/
+ Stars: N/A
+ Version: 0.2.59
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Foundby: Pyrl

### Vulnerable Code Snippet

```
def object_path_set(obj, paths, value, sep='.'):
    cursor = obj
    if isinstance(paths, str):
        paths = paths.split(sep)
    length = len(paths)
    for i, path in enumerate(paths):
        if i == length - 1:
            if hasattr(cursor, '__setitem__'):
                cursor[path] = value
            else:
                setattr(cursor, path, value)
        else:
            if hasattr(cursor, '__getitem__'):
                try:
                    cursor = cursor[path]
                except KeyError:
                    v = cursor.__class__()
                    cursor[path] = v
                    cursor = v
            else:
                try:
                    cursor = getattr(cursor, path)
                except AttributeError:
                    v = cursor.__class__()
                    setattr(cursor, path, v)
                    cursor = v
    return value
```
