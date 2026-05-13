---
title: "{{ replace .Name "-" " " | title }}"
weight: 99
---

# {{ replace .Name "-" " " | title }}

One-sentence description of what this gadget produces (RCE / XSS / DoS / auth bypass / ...)
and the single idea it exploits.

## Mechanism

What object graph does this walk and why does that graph end at a useful sink? Explain the
object lifecycle: which framework/library function actually consults the polluted attribute
at runtime, and under what circumstances.

## Key path

```
__class__.__init__.__globals__.<...>
```

Describe how each step is resolved — attribute access vs. item access, whether the step
requires `__class__` to reach a class object first, and whether the same path works for
instances of other classes in the same module.

## Payload

```python
# Concrete payload (key path, value) or full JSON body as it would appear at the sink.
```

## Preconditions

- What must be true about the victim process for this gadget to fire?
- Which modules must already be imported? (`sys.modules` only contains imported names.)
- Which Python version / platform is required?
- Any timing dependency (e.g. the sink must be hit *after* the pollution)?

## Worked example

```python
# Minimal self-contained program that reaches the sink. Include the exact
# getattr/setattr loop the payload flows through.
```

Trace what each line does and note where the pollution lands.

## Variants

- Alternative key paths that reach the same sink.
- What to try when a precondition fails (module not imported, `os.environ` write-protected,
  etc.).

## Defense

- The sink-level mitigation (allowlist / dunder rejection / typed container).
- Why coarser mitigations fail (blocking `__class__` alone is not sufficient — see
  [[why-blocking-class-fails]]).
- Which of the three defense strategies in [Defense]({{< relref "/docs/defense" >}}) apply.

## Real-world cases

- [Link to the showcase page that uses this gadget.]({{< relref "/docs/collection/showcases" >}})
- CVE reference and short note on any variation.

## References

1. Author, *Title*, Venue, Year. <https://...>
