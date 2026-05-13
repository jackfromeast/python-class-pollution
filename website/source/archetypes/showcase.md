---
title: "{{ replace .Name "-" " " | title }}"
weight: 99
---

# {{ replace .Name "-" " " | title }}

One paragraph: what the project does, who its users are, and why the affected sink is
invoked during normal use.

| Field | Value |
|-------|-------|
| Repository | [owner/repo](https://github.com/owner/repo) |
| Version | _affected version_ |
| CVE | [CVE-YYYY-NNNNN](https://nvd.nist.gov/vuln/detail/CVE-YYYY-NNNNN) |
| Type | _e.g. Constrained-Get × Attr-Set_ |
| Input | _Remote (HTTP/WebSocket) · Local (argv) · Package (API)_ |
| Status | _Fixed / Reported / Acknowledged_ |

## Vulnerability

Point to the exact function (`file.py:fn`, with a permalink to the line) and the sink it
performs. Include the code inlined, annotated with what is untrusted:

```python
def set_property_value(obj, name, value):
    parts = name.split(".")   # <-- user-controlled
    cur = obj
    for part in parts[:-1]:
        cur = getattr(cur, part)
    setattr(cur, parts[-1], value)
```

Explain the trust boundary: where does `name` enter the process, what validation (if any)
is performed along the way, and why that validation is insufficient.

## Exploitation

For each consequence produced by the same sink, give the payload and the observed effect.
Link to the gadget page that the payload instantiates.

### 1. _Consequence_

Payload:

```
name:  <key path>
value: <value>
```

Effect: one paragraph describing exactly what happens in the running process.
Gadget: [<gadget name>]({{< relref "/docs/gadgets" >}}).

### 2. _Consequence_

...

## Detection by Pyrl

The taint flow Pyrl reports for this finding. Label the tags at each step
(`T_INPUT`, `T_ENUM`, `T_KEY`, `T_OBJ`, `G_ATTR`, `G_ITEM`, sink) so readers who have read
[the tool docs]({{< relref "/docs/tool/pyrl" >}}) can map them onto the analysis.

## Disclosure timeline

- **YYYY-MM-DD** &mdash; Reported to maintainers.
- **YYYY-MM-DD** &mdash; Patch released.
- **YYYY-MM-DD** &mdash; CVE assigned.

## Proof of concept

[`cp-collection/<project>/poc/`](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection)
&mdash; runnable exploit with `run.sh` and `requirements.txt`.

## References

1. GHSA advisory. <https://...>
2. Fix commit. <https://...>
