# import laboneq.dsl.quantum as quantum
# from laboneq.dsl.quantum.quantum_operations import QuantumOperations
# from laboneq.workflow.typing import Qubits
from typing import TYPE_CHECKING, Any, Sequence
import random

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)
      
class Poc:
  @classmethod
  def _get_invalid_param_paths(cls, qubit, overrides: dict[str, Any]) -> Sequence:
      invalid_params = []
      for param_path in overrides:
          keys = param_path.split(".")
          obj = qubit.parameters
          for key in keys:
              if isinstance(obj, dict):
                  if key not in obj:
                      invalid_params.append(param_path)
                      break
                  obj = obj[key]
              elif not hasattr(obj, key):
                  invalid_params.append(param_path)
                  break
              else:
                  obj = getattr(obj, key)
      return invalid_params
    
  @classmethod
  def _override_qubit_parameters(cls, qubit, overrides: dict) -> None:
      invalid_params = cls._get_invalid_param_paths(qubit, overrides)
      if invalid_params:
          raise ValueError(
              f"Update parameters do not match the qubit "
              f"parameters: {invalid_params}",
          )

      for param_path, value in overrides.items():
          keys = param_path.split(".")
          obj = qubit.parameters
          for key in keys[:-1]:
              obj = obj[key] if isinstance(obj, dict) else getattr(obj, key)
          if isinstance(obj, dict):
              if keys[-1] in obj:
                  obj[keys[-1]] = value
          elif hasattr(obj, keys[-1]):
              setattr(obj, keys[-1], value)

class Qubit:  
  def __init__(self, parameters=None):
      self.parameters = parameters

p = Poc()
obj = Qubit(Animal('cat', 11))
p._override_qubit_parameters(obj, {'__init__.__globals__.__name__':'polluted'})
print(__name__)
