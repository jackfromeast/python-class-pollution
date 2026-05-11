## azure-cli

### Meta

+ Repo: azure-cli
+ Link: https://github.com/Azure/azure-cli
+ Stars: 4.1K
+ Version: v2.68.0
+ CVE: [CVE-2025-24049](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2025-24049)
+ VulnType: get-both-set-both
+ Status: Fixed
+ Payload: ```az resource update --ids /subscriptions/2f5657fb-2e1b-4b1b-afd1-635a17df91c5/resourceGroups/Nothing_group/providers/Microsoft.Web/staticSites/Nothing --set __class__.__init__.__globals__.__name__=polluted```
+ Foundby: Pyrl
+ Report: Reported
+ AppType: App
+ Input: Local

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