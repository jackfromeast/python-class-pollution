---
title: "{{ replace .Name "-" " " | title }}"
weight: 99
---

# {{ replace .Name "-" " " | title }}

One-sentence definition in plain language. Say what the concept *is*, not what it does.

## Formal characterization

The precise definition as used in the paper and in Pyrl's analysis. Include any
formal notation (e.g. a taint-propagation rule, a type signature for the primitive,
or the set-theoretic classification for vulnerability types).

## Minimal Python example

```python
# The smallest program that exhibits this concept.
```

Describe what this program does and where the concept enters.

## Comparison to related concepts

- How does this relate to JS prototype pollution?
- How does this relate to other concepts in [[taxonomy]]?
- Which gadgets in [[gadgets]] depend on this?

## Notes

Any caveats the reader needs to hold in mind: common misreadings, environments where the
behavior differs (CPython vs PyPy, Python 3.10 vs 3.12), and known edge cases.

## References

1. Author, *Title*, Venue, Year. <https://...>
