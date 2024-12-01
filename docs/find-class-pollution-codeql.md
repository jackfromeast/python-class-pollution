## Detecting Class Pollution with CodeQL

### Class Pollution Patterns

#### #1 Precise Matching

Detecting class pollution is analogous to identifying prototype pollution vulnerabilities, as implemented in the [official CodeQL library](https://github.com/github/codeql/blob/main/javascript/ql/src/Security/CWE-915/PrototypePollutingFunction.ql). The goal is to trace dataflows from polluted keys to assignments where the base object, key, and value all depend on the enumerated keys. Consider the following example:

1. The base object of the assignment must derive from a polluted key through operations like `base = obj[key]` or `base = getattr(obj, key)` where key is the polluted key name. For example, in the following example, the dataflow regarding the base object is `k` -> `dst.get(k)`/`getattr(dst, k)` -> `dst` -> `dst[k] = v`/`setattr(dst, k, v)`.

2. The key of the assignment should also depend on the polluted key. In the following example, the dataflow regarding the key is `k` -> `v` (through `src.items`) -> `merge(v, dst.get(k))`/`merge(v, getattr(dst, k))` -> `src` -> `for k, v in src.items()` (`k`) -> `dst[k] = v`/`setattr(dst, k, v)`.

3. The value of the assignment should also depend on the polluted key. In the following example, the dataflow regarding the value is `k` -> `v` (through `src.items`) -> `merge(v, dst.get(k))`/`merge(v, getattr(dst, k))` -> `src` -> `for k, v in src.items()` (`v`) -> `for k, v in src.items()` -> `dst[k] = v`/`setattr(dst, k, v)`.

```
def merge(src, dst):
  # Recursive merge function
  for k, v in src.items():
      if hasattr(dst, '__getitem__'):
          if dst.get(k) and type(v) == dict:
              merge(v, dst.get(k))
          else:
              dst[k] = v
      elif hasattr(dst, k) and type(v) == dict:
          merge(v, getattr(dst, k))
      else:
          setattr(dst, k, v)
```

When all three dataflows—base object, key, and value—are present in a single assignment, the assignment is considered class-polluting. To detect such patterns, I implemented the `TrackingClassPollutionKeyConfiguration` module in `ClassPollutingFunc.qll`. This module tracks the three dataflows separately and identifies assignments where their sinks intersect, confirming the pollution.

However, capturing the above precise pattern is particularly challenging because CodeQL is highly sensitive to API function calls and class-related data flows, which can act as barriers to taint propagation. For example, in the glom library, a statement like `keys = [key for key in filter(None, val.split('.'))]` introduces complexity. While `val.split('.')` is recognized as a source pattern, the taint cannot propagate to keys due to the filter function, which requires special handling.

Therefore, we need to concretize all program semantics used to describe class pollution patterns into syntax that CodeQL can effectively capture. Additionally, we must gradually incorporate isAdditionalTaintStep rules to ensure that taint propagation is maintained across each step in the dataflow.

