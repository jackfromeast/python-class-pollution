### Class Pollution Micro-Benchmark Suite

This benchmark validates our CodeQL query for detecting class/prototype pollution vulnerabilities. It contains test cases where the query should/should not flag specific patterns.

#### Format

Required Metadata Tags: 

```
def cp_func_through_reduce(obj, attr, val):
  """
  @name: getattr_through_reduce
  @desc: Check taint propagation through reduce function
  @result: Should mark as vulnerable due to unsafe attr chain
  @vuln: true
  @category: class-pollution-func
  @type: set-attr+get-attr
  """
  pre, _, post = attr.rpartition('.')
  return setattr(rgetattr(obj, pre) if pre else obj, post, val)
```