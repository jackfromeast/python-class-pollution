## riven

### Meta

+ Repo: riven
+ Link: https://github.com/rivenmedia/riven
+ Stars: 789
+ Version: v0.20.1
+ CVE: N/A
+ VulnType: get-attr-set-both
+ Status: Pending
+ Foundby: Pyrl

### Vulnerable Code Snippet

```python
def _set_nested_attr(obj, key, value):
  if "." in key:
      parts = key.split(".", 1)
      current_key, rest_of_keys = parts[0], parts[1]

      if not hasattr(obj, current_key):
          raise AttributeError(f"Object does not have the attribute '{current_key}'.")

      current_obj = getattr(obj, current_key)
      _set_nested_attr(current_obj, rest_of_keys, value)
  elif isinstance(obj, dict):
      obj[key] = value
  else:
      setattr(obj, key, value)
```
