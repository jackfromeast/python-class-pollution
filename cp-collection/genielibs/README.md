## genielibs

### Meta

+ Repo: genielibs
+ Link: https://github.com/CiscoTestAutomation/genielibs
+ Stars: 113
+ Version: V24.9
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Reported
+ Foundby: Pyrl

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
