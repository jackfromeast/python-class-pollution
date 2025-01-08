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
