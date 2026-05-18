## smolagents

### Metadata

+ Repo: smolagents
+ Link: https://github.com/huggingface/smolagents
+ Stars: 27.4K
+ Version: v1.14.0
+ CVE: N/A
+ VulnType: get-attr-set-attr
+ Status: Reported
+ Foundby: Pyrl

### Vulnerable Code Snippet

`set_value` in `smolagents/local_python_executor.py`

```python
# smolagents/local_python_executor.py
def set_value(
    target: ast.AST,
    value: Any,
    state: dict[str, Any],
    static_tools: dict[str, Callable],
    custom_tools: dict[str, Callable],
    authorized_imports: list[str],
) -> None:
    if isinstance(target, ast.Name):
        if target.id in static_tools:
            raise InterpreterError(f"Cannot assign to name '{target.id}': doing this would erase the existing tool!")
        state[target.id] = value
    elif isinstance(target, ast.Tuple):
        ...
    elif isinstance(target, ast.Subscript):
        obj = evaluate_ast(target.value, state, static_tools, custom_tools, authorized_imports)
        key = evaluate_ast(target.slice, state, static_tools, custom_tools, authorized_imports)
        obj[key] = value
    elif isinstance(target, ast.Attribute):
        obj = evaluate_ast(target.value, state, static_tools, custom_tools, authorized_imports)
        setattr(obj, target.attr, value)  # unrestricted setattr on any reachable object
```

The `evaluate_attribute` getter also traverses without restriction (except dunder access):

```python
def evaluate_attribute(expression, state, static_tools, custom_tools, authorized_imports):
    if expression.attr.startswith("__") and expression.attr.endswith("__"):
        raise InterpreterError(f"Forbidden access to dunder attribute: {expression.attr}")
    value = evaluate_ast(expression.value, state, static_tools, custom_tools, authorized_imports)
    return getattr(value, expression.attr)
```

The agent's code executor allows polluting any object reachable from the execution state. When smolagents is deployed with its built-in Gradio UI (`GradioUI`), user-supplied prompts trigger code execution through the local Python executor, making this remotely triggerable.
