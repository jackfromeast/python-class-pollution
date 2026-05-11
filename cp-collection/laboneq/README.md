## laboneq

### Meta

+ Repo: laboneq
+ Link: https://github.com/zhinst/laboneq
+ Stars: 39
+ Version: v2.44.0
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Payload: ```_override_qubit_parameters(obj, {'__init__.__globals__.__name__':'polluted'})```
+ Foundby: Zhong
+ Report: Pending
+ AppType: Lib
+ Input: Func

### Vulnerable Code Snippet

```
@classmethod
def _override_qubit_parameters(cls, qubit, overrides: dict) -> None:
    invalid_params = cls._get_invalid_param_paths(qubit, overrides)
    if invalid_params:
        raise ValueError(
            f"Update parameters do not match the qubit "
            f"parameters: {invalid_params}",
        )

    for param_path, value in overrides.items():
        keys = param_path.split(".")
        obj = qubit.parameters
        for key in keys[:-1]:
            obj = obj[key] if isinstance(obj, dict) else getattr(obj, key)
        if isinstance(obj, dict):
            if keys[-1] in obj:
                obj[keys[-1]] = value
        elif hasattr(obj, keys[-1]):
            setattr(obj, keys[-1], value)
```
