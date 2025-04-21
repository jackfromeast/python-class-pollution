"""
@description:
--------------------
The tests help to verify the dataflow for values with PrototypeObject flow state.

The value PrototypeObjectFlowState should only propagate through the dataflow step instead of the taintflow step.
"""

def prototype_object_flow1(obj, attrs, val):
  """
  @name: prototype_object_flow1
  @desc: Check if the PrototypeObjectFlowState propagates through the dataflow step.
  @result: prototype_object_flow1 should be marked as vulnerable. 
  @vuln: false
  @category: dataflow-check
  """

  for attr in attrs[:-1]:
    obj = obj.__dict__.get(attr)
  
  obj1 = obj # Dataflow step

  setattr(obj1, attrs[-1], val)


def prototype_object_flow2(obj, attrs, val):
  """
  @name: prototype_object_flow2
  @desc: Check if the PrototypeObjectFlowState propagates through the dataflow step.
  @result: prototype_object_flow2 should *not* be marked as vulnerable. 
  @vuln: false
  @category: dataflow-check
  """
  for attr in attrs[:-1]:
    obj = obj.__dict__.get(attr)
  
  obj2 = obj["some_attributes"] # Taintflow step

  setattr(obj2, attrs[-1], val)