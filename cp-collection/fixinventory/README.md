## fixinventory

### Meta

+ Repo: fixinventory
+ Link: https://github.com/someengineering/fixinventory
+ Stars: 2.1K
+ Version: 4.2.0
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Reported
+ Foundby: Pyrl

### Vulnerable Code Snippet

```python
@staticmethod
def override_config(running_config: RunningConfig) -> None:
    if getattr(ArgumentParser.args, "config_override", None) is None:
        return
    for override in getattr(ArgumentParser.args, "config_override", []):
        try:
            # ... Ignore for Concise
            config_keys = config_key.split(".")
            num_keys = len(config_keys)
            config_part = running_config.data
            set_value = False


            # ... Ignore for Concise
            for num_key, key in enumerate(config_keys):
                if num_key == num_keys - 1:
                    set_value = True
                    log.debug(f"Overriding config key {config_key}")

                if hasattr(config_part, key):
                    attr_value = getattr(config_part, key)
                    if set_value:
                        config_value = Config.cast_target_type(config_value, attr_value, fallback_target_type)
                        setattr(config_part, key, config_value)
                    else:
                        config_part = attr_value
                elif isinstance(config_part, dict) and key in config_part:
                    attr_value = config_part[key]
                    if set_value:
                        config_value = Config.cast_target_type(config_value, attr_value, fallback_target_type)
                        config_part[key] = config_value
                    else:
                        config_part = attr_value
                else:
                    log.error(f"Override key {config_key} is unknown - skipping")
                    break

            # ... Ignore for Concise
```
