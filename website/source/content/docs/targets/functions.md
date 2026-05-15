---
title: "Functions"
weight: 3
---

# Functions

A Python function object exposes three independent access mechanisms for pollution: `__globals__`, `__kwdefaults__`, and `__closure__`. Each one routes the polluted value into program behavior through a different path. The `__closure__` mechanism is novel to this work. The other two were known in prior literature.

## Access mechanism: global variable reference via `__globals__`

When a function `f` is accessible, the attacker can modify `f.__globals__["v"]`, where `v` is a global variable in the module where `f` is defined. Every function carries a reference to its defining module's `__dict__`, so any accessible function exposes its module's entire namespace, and through `sys.modules` any other loaded module.

```python
# mod.py
TEMPLATE_DIR = "/srv/app/templates"
def render(name):
    path = TEMPLATE_DIR + "/" + name        # uses the global TEMPLATE_DIR
    return open(path).read()

render("home.html")                         # reads /srv/app/templates/home.html

# Attacker payload (Item-Set on render.__globals__):
#   render.__globals__["TEMPLATE_DIR"] = "/etc"

render("passwd")                            # reads /etc/passwd
```

This is the same effect as polluting [Modules]({{< relref "modules" >}}) directly, but routed through a function instead of through a module reference.

## Access mechanism: local variable reference via `__kwdefaults__`

When a function `f` has keyword-only parameters, their default values live in the dictionary `f.__kwdefaults__`. Modifying an entry changes the default value used by every subsequent call that does not pass the argument explicitly. Keyword-only parameters are the parameters defined after `*` in the signature ([PEP 3102](https://peps.python.org/pep-3102/)).

```python
def render_template(name, *, autoescape=True, cache=True):
    ...

render_template("home.html")        # autoescape=True, output is HTML-escaped

# Attacker payload (Item-Set on render_template.__kwdefaults__):
#   render_template.__kwdefaults__["autoescape"] = False

render_template("home.html")        # autoescape=False, output is rendered raw, XSS is now possible
```

`__kwdefaults__` is a dictionary, so this access mechanism requires an [Item-Set or Dual-Set]({{< relref "/docs/taxonomy/primitives" >}}) primitive.

## Access mechanism: local variable reference via `__closure__`

When a function `g` is accessible as a closure, the attacker can modify the captured variables through `g.__closure__[i].cell_contents`. Python closures store captured variables in `cell` objects rather than in the function's own dict, so the cell content is the foothold.

```python
def make_checker(allowed):
    def is_allowed(user):
        return user in allowed      # reads the captured `allowed` set
    return is_allowed

is_allowed = make_checker({"alice", "bob"})
is_allowed("eve")                   # returns False

# Attacker payload (Attr-Set on the captured cell):
#   is_allowed.__closure__[0].cell_contents = {"eve"}

is_allowed("eve")                   # returns True, the access check is bypassed
```

The cells of a closure are addressed in capture order:

```python
g.__closure__                       # tuple of cell objects, in capture order
g.__closure__[0]                    # first captured variable's cell
g.__closure__[0].cell_contents      # the actual captured value
```

See [XSS gadgets]({{< relref "/docs/gadgets/xss" >}}), [RCE gadgets]({{< relref "/docs/gadgets/rce" >}}), and [authentication bypass gadgets]({{< relref "/docs/gadgets/auth-bypass" >}}) for end-to-end exploitation chains that build on these mechanisms.
