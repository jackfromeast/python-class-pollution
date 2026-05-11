## jacinle

### Meta

+ Repo: Jacinle
+ Link: https://github.com/vacancy/Jacinle
+ Stars: 135
+ Version: N/A
+ CVE: N/A
+ VulnType: get-attr-set-both
+ Status: Pending
+ Payload: ```_KV('__init__.__globals__.__name__=polluted').apply(obj)```
+ Foundby: Zhong
+ Report: Pending
+ AppType: Lib
+ Input: Func

### Vulnerable Code Snippet

```python
def apply(self, configs):
    with print_to(logger.info):
        print('Applying KVs:')
        for k, v in self.kvs:
            print('  kv.{} = {}'.format(k, v))
            keys = k.split('.')
            current = configs
            for k in keys[:-1]:
                try:
                    current = getattr(current, k)
                except AttributeError:
                    current = current.setdefault(k, G())

            try:
                setattr(current, keys[-1], v)
            except AttributeError:
                current[keys[-1]] = v
```
