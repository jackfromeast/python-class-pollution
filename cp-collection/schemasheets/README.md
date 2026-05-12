## schemasheets

### Meta

+ Repo: schemasheets
+ Link: https://github.com/linkml/schemasheets
+ Stars: 52
+ Version: 0.3.1
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Foundby: Pyrl

### Vulnerable Code Snippet

```python
def set_attr_via_path_accessor(obj: Union[dict], path: Union[str, List[str]], value: Any, depth=0) -> None:
    toks = ensure_path_tokens(path)
    tok = toks[0]
    toks = toks[1:]
    logging.debug(f"[{depth}] Setting attr {tok} / {toks} in {obj} to {value}")
    if isinstance(obj, dict):
        if not toks:
            obj[tok] = value
        else:
            if tok not in obj:
                obj[tok] = {}
                logging.info(f"Creating empty dict for: {tok}")
            set_attr_via_path_accessor(obj[tok], toks, value, depth+1)
    else:
        if not toks:
            setattr(obj, tok, value)
        else:
            if not hasattr(obj, tok):
                setattr(obj, tok, {})
            set_attr_via_path_accessor(getattr(obj, tok), toks, value, depth+1)
```
