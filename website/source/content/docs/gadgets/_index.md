---
title: "Gadgets"
weight: 4
bookCollapseSection: true
---

# Gadgets

A *class-pollution gadget* is a piece of existing, legitimate code that reads an attacker-controlled attribute or item from a runtime object, which was injected via a [class pollution]({{< relref "/docs/taxonomy" >}}) vulnerability, and flows the value into a security-relevant sink such as a subprocess invocation, an HTML escaper, or a token signer.

## Example

The gadget is the existing code that does the read and the dangerous use. For RCE via `BROWSER`, the gadget lives in the standard library's `webbrowser` module:

```python
# CPython Lib/webbrowser.py (simplified)

def get(using=None):
    if using is None:
        # read of the attacker-controlled value:
        if "BROWSER" in os.environ:
            for browser in os.environ["BROWSER"].split(os.pathsep):
                return GenericBrowser(browser)      # passes the string straight to subprocess

class GenericBrowser:
    def open(self, url, new=0, autoraise=True):
        cmdline = [self.name] + [arg.replace("%s", url) for arg in self.args]
        # security-relevant sink:
        subprocess.Popen(cmdline)
```

This code is benign in normal operation: a developer sets `BROWSER=firefox`, and `webbrowser.open()` launches Firefox. It becomes an RCE gadget the moment an attacker, through a separate [pollution primitive]({{< relref "/docs/taxonomy/primitives" >}}), writes a shell-command string to `os.environ["BROWSER"]`:

```python
# Attacker payload (delivered through any reflective setter):
#   os.environ["BROWSER"] = "/bin/sh -c 'touch /tmp/pwned'"

# Anywhere in the application, code as innocent as:
import antigravity                                  # antigravity.py calls webbrowser.open()
# now runs /bin/sh -c 'touch /tmp/pwned'
```

A class-pollution exploit is therefore the composition of a [primitive]({{< relref "/docs/taxonomy/primitives" >}}) (writes attacker-chosen data to a [target]({{< relref "/docs/targets" >}})) and a gadget (reads that target later and uses it in a security-relevant operation). The gadget itself is upstream code that the application reuses, often inside the standard library or a third-party dependency.

## Categories

- [**RCE Gadgets**]({{< relref "rce" >}}). Pollute `os.environ` or `sys.modules` so a later subprocess call or dynamic import executes attacker-chosen code.
- [**XSS Gadgets**]({{< relref "xss" >}}). Pollute an HTML escape map or autoescape flag so server-rendered output carries attacker script.
- [**Auth Bypass Gadgets**]({{< relref "auth-bypass" >}}). Pollute a signing key or auth flag so the attacker can forge sessions or skip access checks.
- [**DoS Gadgets**]({{< relref "dos" >}}). Pollute a dunder method or callable global so any subsequent operation on the affected class crashes.

## Origin

Class-pollution gadgets fall into three groups by where the gadget code lives.

**Language built-ins.** The gadget is part of the Python data model itself. Examples: `__class__.__getattribute__` overwrite (see [DoS]({{< relref "dos" >}})), `__class__` reassignment, `__str__` / `__repr__` overwrite. These work on every Python object, so any process running CPython is in scope.

**Standard library.** The gadget lives in a stdlib module that is loaded in essentially every Python process. Examples: `os.environ.BROWSER` plus `webbrowser` plus `antigravity` for RCE on POSIX, `os.environ.COMSPEC` plus `subprocess(shell=True)` for RCE on Windows. Because the modules they target are present in nearly every Python application, these gadgets, together with the language built-ins above, behave as **universal gadgets**: they fire across many independently-developed applications without any application-specific code being required.

The same notion of universal gadgets is well established in JavaScript prototype-pollution research. Shcherbakov et al., *Silent Spring: Prototype Pollution Leads to Remote Code Execution in Node.js*, USENIX Security 2023 ([paper](https://www.usenix.org/system/files/usenixsecurity23-shcherbakov.pdf)) and Cornelissen et al., *GHunter: A Universal Gadget for Server-Side JavaScript*, USENIX Security 2024 ([paper](https://www.usenix.org/system/files/usenixsecurity24-cornelissen.pdf)), formalizes the notion of a universal gadget for server-side JavaScript. The Python class-pollution variants documented here play the same structural role.

**Third-party packages and application code.** The gadget lives in a specific framework, library, or in the application itself. Examples: `bs4.dammit.EntitySubstitution.CHARACTER_TO_XML_ENTITY` for stored XSS, `django.conf.settings.SECRET_KEY` and `app.secret_key` for auth bypass (see [Auth Bypass]({{< relref "auth-bypass" >}})), and any class-level boolean such as `AuthMiddleware.require_auth` that the application reads in a security check. The defining difference from the previous two groups is that these gadgets are not present in every Python process. Identifying which ones are exploitable in a given target requires per-application analysis: the analyst (or detection tool) has to inspect the installed packages and the application's own code to find which polluted attribute or item is later read into a security-sensitive sink.
