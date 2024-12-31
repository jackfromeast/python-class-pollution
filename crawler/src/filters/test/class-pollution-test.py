# 1. Direct Import
# Regex: from\s+glom\s+import\s+assign
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
# 2. Direct Import with Alias
# Regex: from\s+glom\s+import\s+assign\s+as\s+\w+
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
# Regex: import\s+glom[\s\S]*glom\.assign\s*\(
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
# Regex: import\s+glom\s+as\s+\w+[\s\S]*\1\.assign\s*\(
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
# Regex: from\s+glom\s+import\s+\*
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