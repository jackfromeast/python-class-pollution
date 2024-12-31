# 1. Direct Import
# Current Regex:
"""
  "glom.assign.direct_import": /\bglom\s+import\s+.*\bassign\b/
  "pydash.set_.direct_import": /\bpydash\s+import\s+.*\bset_\b/
  "deepdiff.Delta.direct_import": /\bdeepdiff\s+import\s+.*\bDelta\b/

"""
# GPT Regex: from\s+glom\s+import\s+assign
from glom import assign
assign(obj, '__init__.__globals__.subprocess.os.__name__', 'polluted')

from pydash import set_
set_(obj1, '__init__.__globals__.__name__', "polluted")

from deepdiff import Delta
payload = {
  "attribute_added" : {
    "root['x']": namedtuple,
    "root['x'].'__globals__'['_sys'].'__name__'": "polluted",
  }
}
delta = Delta(payload)

from glom import a, b, assign, c
assign(obj, '__init__.__globals__.subprocess.os.__name__', 'polluted')

from pydash import a, set_
set_(obj1, '__init__.__globals__.__name__', "polluted")

from deepdiff import c , Delta
payload = {
  "attribute_added" : {
    "root['x']": namedtuple,
    "root['x'].'__globals__'['_sys'].'__name__'": "polluted",
  }
}
# 2. Direct Import with Alias
# Current Regex:
"""
  "glom.assign.as": [
    /import\s+glom\s+as/,
    /\.assign\(/
  ]
"""
# GPT Regex: from\s+glom\s+import\s+assign\s+as\s+\w+
from  glom import assign as a
a(obj, '__init__.__globals__.subprocess.os.__name__', 'polluted')

from pydash import  set_ as b
b(obj1, '__init__.__globals__.__name__', "polluted")

from deepdiff import Delta as  c
payload = {
  "attribute_added" : {
    "root['x']": namedtuple,
    "root['x'].'__globals__'['_sys'].'__name__'": "polluted",
  }
}
delta = c(payload)
# 3. Full Module Import
# Current Regex:
"""
  "glom.assign": /\bglom\.assign\(/
  "pydash.set_": /\bpydash.set\_\(/
  "deepdiff.Delta": /\bdeepdiff.Delta\(/
"""
# GPT Regex: import\s+glom[\s\S]*glom\.assign\s*\(
import glom
glom.assign(obj, '__init__.__globals__.subprocess.os.__name__', 'polluted')

import pydash
pydash.set_(obj1, '__init__.__globals__.__name__', "polluted")

import  deepdiff
payload = {
  "attribute_added" : {
    "root['x']": namedtuple,
    "root['x'].'__globals__'['_sys'].'__name__'": "polluted",
  }
}
delta = deepdiff.Delta(payload)
# 4. Full Module Import with Alias
# Current Regex:
"""
        "deepdiff.Delta.as": [
            /import\s+deepdiff\s+as/,
            /\.Delta\(/,
        ]
"""
# GPT: Regex: import\s+glom\s+as\s+\w+[\s\S]*\1\.assign\s*\(
import glom as g
g.assign(obj, '__init__.__globals__.subprocess.os.__name__', 'polluted')

import pydash as p
p.set_(obj1, '__init__.__globals__.__name__', "polluted")

import  deepdiff as d
payload = {
  "attribute_added" : {
    "root['x']": namedtuple,
    "root['x'].'__globals__'['_sys'].'__name__'": "polluted",
  }
}
delta = d.Delta(payload)
# 5. Import Everything (*)
# Current Regex:
"""
  "deepdiff.Delta.wildcard_import": [
    /from\s+deepdiff\s+import\s+\*/,
    /\bDelta\(/,
  ]
"""
# GPT Regex: from\s+glom\s+import\s+\*
# [\s\S]*\bassign\s*\(
from glom import *
assign(obj, '__init__.__globals__.subprocess.os.__name__', 'polluted')

from pydash import  *
set_(obj1, '__init__.__globals__.__name__', "polluted")

from deepdiff  import *
payload = {
  "attribute_added" : {
    "root['x']": namedtuple,
    "root['x'].'__globals__'['_sys'].'__name__'": "polluted",
  }
}
delta = Delta(payload)
