## pytest-sftpserver

### Metadata

+ Repo: pytest-sftpserver
+ Link: https://github.com/ulope/pytest-sftpserver
+ Stars: 38
+ Version: 1.3.0
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: TODO
+ Foundby: Pyrl

### Vulnerable Code Snippet

`put` in `pytest_sftpserver/sftp/content_provider.py`

```python
# pytest_sftpserver/sftp/content_provider.py
class ContentProvider(object):
    def put(self, path, data):
        path, name = self._get_path_components(path)
        obj = self._find_object_for_path(path)  # traverses path segments via getattr/obj[key]
        if isinstance(obj, dict):
            obj[name] = data
            return True
        elif isinstance(obj, list) and name.isdigit():
            name = int(name)
            if name > len(obj) - 1:
                obj.append(data)
            obj[name] = data
            return True
        try:
            setattr(obj, name, data)  # unrestricted setattr on any reachable object
            return True
        except (TypeError, AttributeError):
            pass
        return False

    def _find_object_for_path(self, path):
        obj = self.content_object
        for part in path.split(separator):
            if part:
                try:
                    new_obj = getattr(obj, part)  # get via attribute
                except (AttributeError, TypeError):
                    try:
                        new_obj = obj[part]  # get via item
                    except (KeyError, TypeError, IndexError):
                        if part.isdigit():
                            new_obj = obj[int(part)]  # get via integer index
                        else:
                            return None
                obj = new_obj
        return obj
```

The `_find_object_for_path` method traverses an arbitrary path using both `getattr` and item access (`obj[key]`), then `put` calls `setattr(obj, name, data)` on the resolved object. When an SFTP client writes a file whose path maps to attribute traversal on the content object, it can pollute class attributes of any reachable object.
