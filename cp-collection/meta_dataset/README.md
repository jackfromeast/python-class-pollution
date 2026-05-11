## meta_dataset

### Meta

+ Repo: meta_dataset
+ Link: https://github.com/google-research/meta-dataset
+ Stars: 768
+ Version: N/A
+ CVE: N/A
+ VulnType: get-attr-set-attr
+ Status: Pending
+ Payload: ```_init_reference_module(Animal, {"typ":'cat',"age": 11}, [['__init__','__globals__','__name__']], ['polluted'])```
+ Foundby: Zhong
+ Report: Pending
+ AppType: Lib
+ Input: Func

### Vulnerable Code Snippet

```python
def _init_reference_module(module_cls, module_init_kwargs, paths, variables):
  """Create a mock `module_cls` instance with `variables` as attributes."""
  reference_module = _init_module(module_cls, module_init_kwargs)

  # Manually set attributes of this module via `getattr` and `setattr`.
  for path, variable in zip(paths, variables):
    descoped_module = reparameterizable_base.chained_getattr(
        reference_module, path[:-1])
    reparameterizable_base.corner_case_setattr(descoped_module, path[-1],
                                               variable)

  return reference_module
```
