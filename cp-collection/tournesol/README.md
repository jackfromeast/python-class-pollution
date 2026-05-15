## tournesol

### Meta

+ Repo: tournesol
+ Link: https://github.com/tournesol-app/tournesol
+ Stars: 375
+ Version: N/A
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Reported
+ Foundby: Pyrl

### Vulnerable Code Snippet

```python
def set_attr(x_parameter: str, x: float, generative_model, pipeline):
    x_list = x_parameter.split(".")
    
    if x_list[0] == "generative_model": 
        obj = generative_model
    elif x_list[0] == "pipeline":
        obj = pipeline
    else: 
        raise ValueError(f"No match for {x_parameter[0]}")
        
    for attr in x_list[1:-1]:
        try:    obj = getattr(obj, attr)
        except: 
            try: obj = obj[attr]
            except: obj = obj[int(attr)]
    try:
        setattr(obj, x_list[-1], x)
    except:
        obj[x_list[-1]] = x
```
