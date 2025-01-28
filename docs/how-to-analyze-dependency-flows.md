## Automatic Dependency Analysis with CodeQL

### Motivating Example

The following code snippet comes from `robusta` repository that previously missed by our CodeQL query but found by Jiacheng manually. The issue arises because the function relies on `object_at_path` from the external `hikaru` library to retrieve a nested object based on a given path. CodeQL couldn’t analyze this function since it doesn’t exist within the current codebase. This highlights the need for an automated approach to handle taint propagation involving external functions.

```
// https://github.com/robusta-dev/robusta/blob/d06212253b42d493ebc33f79bb68debb005afa4f/src/robusta/runner/object_updater.py#L2
from hikaru import HikaruBase

def update_item_attr(obj: HikaruBase, attr_key: str, attr_value):
    path_parts = regex.split("\\[|\\].|\\]|\\.", attr_key)
    parent_item = obj.object_at_path(path_parts[0 : len(path_parts) - 1])
    last_part = path_parts[len(path_parts) - 1]
    if type(parent_item) == dict:
        parent_item[last_part] = attr_value
    elif type(parent_item) == list:
        parent_item[int(last_part)] = attr_value
    else:
        setattr(parent_item, last_part, attr_value)
```

**Key issues to resolve**

1. Origin Resolving: Determine the source of each callable and classify it as internal or external.
2. Generate Taint Information: Create taint propagation summaries, including taint sources, sinks, and flows, for each external callable.
3. Integrate Summaries into Analysis: Incorporate these summaries into CodeQL to propagate taint across external functions.

### Solution 1: Install all the dependency before analysis

Installing the dependency source code alongside the target repository addresses most cases of issue 1/ and issues 2/ and 3/. CodeQL can resolve call sites in the target repository to definitions in the dependencies, enabling taint propagation through the dependency.

For example, arranging the folders as follows and creating a CodeQL database:

```
/codebase
    - /dependencies
        - /hikaru
    - /robusta
```

Then, applying a small patch to the motivating example resolves issue 1/ (type resolution). CodeQL can then link `obj.object_at_path(path_parts[0 : len(path_parts) - 1])` to its definition in the `hikaru` library, enabling the query to identify vulnerabilities. Becuase, this is generally a challenging problem to resolve argument's type.

```
from hikaru import HikaruBase

def update_item_attr(obj: HikaruBase, attr_key: str, attr_value):
    path_parts = regex.split("\\[|\\].|\\]|\\.", attr_key)
    obj = HikaruBase() // Patch for 1/ Type Resolving
    parent_item = obj.object_at_path(path_parts[0 : len(path_parts) - 1])
    last_part = path_parts[len(path_parts) - 1]
    if type(parent_item) == dict:
        parent_item[last_part] = attr_value
    elif type(parent_item) == list:
        parent_item[int(last_part)] = attr_value
    else:
        setattr(parent_item, last_part, attr_value)
```

The call pair could be easilily verfied through the following query.

```
/**
 * @description
 * ----------------------
 * Check target function of call obj.methodName in the scope scopeName (e.g., function name)
 */
predicate resolveCallToFunctionDef(string methodName, string scopeName, CallCfgNode callNode, Function func) {
  callNode.getScope().getName() = scopeName and
  callNode.(MethodCallNode).getMethodName() = methodName and
  func.getFunctionObject().getAMethodCall() = callNode.asCfgNode()
}

/**
 * @description
 * ----------------------
 * Example of how to use the resolveCallToFunctionDef predicate
 * Check target function of call obj.object_at_path in the update_item_attr function
 */
predicate exercise(CallCfgNode callNode, Function func) {
  resolveCallToFunctionDef("object_at_path", "update_item_attr", callNode, func)
}
```

**Limitations**

1. This approach significantly increases analysis time and may result in wasted resources.
    + Example: `robusta`
        + Without dependencies: Database size - 22 MB, Analysis time - 37.026s
        + With dependencies: Database size - 1.2 GB, Analysis time - [missing data]

**Why Involving More Dependencies Causes Non-Linear Analysis Time Increases?**

0. Theoretical Basis
    + Assume the query algorithm has a time complexity of \(O(f(N))\), where \(N\) is the number of nodes in the database.
    + If $f(N)$ grows faster than linearly (i.e., $f(N) \neq c \cdot N$ for any constant c, then for any partition $N = \sum_{i=1}^n N_i$, it follows that: $O(f(N)) > \sum_{i=1}^n O(f(N_i))$)
    + Intuitively, a super-linear complexity means that analyzing the entire database (including dependencies) at once is strictly more expensive than solving smaller subproblems individually.

1. More Sources/Sinks considered the Dependency Library
    + Dependencies often introduce numerous additional taint sources and sinks, exponentially increasing the paths CodeQL must analyze.
    + Fix: Restrict the sources and sinks to those defined in the target repository.

2. Increased Search Space for Each Predicate
    + Adding dependencies increases the number of objects (e.g., functions, call nodes) that CodeQL needs to analyze.
    + For example, consider the predicate `resolveCallToFunctionDef` above, which resolves a specific call node (callNode) to its corresponding function definition (func). Since CodeQL uses the Function object as the key to find relationships between call nodes and their corresponding definitions. CodeQL must iterate through a larger set of functions to resolve the function.

3. Propagating Taints to Dependencies
    + In my experience, taint flow analysis often gets stuck at the `fwdFlowThrough` predicate when the codebase is large.
    + `fwdFlowThrough` gradually expands tainted nodes by identifying the next affected dataflow node through function call.
    + This is becuase the `fwdFlowThrough` is a basic step to find the next Dataflow node that could be impact by current tainted nodes by one step through function calls. Therefore, they could gradually expaned the tainted nodes gradually. Now, if we start propagating the tainted node to dependenices. There are tainted nodes in dependenices and more code would need to be analyzed.
    + (This is what we what.)

### Solution 2: Analyze Each Dependency Individually and Generate Liberay Models 

This approach leverages the library models provided by CodeQL: https://codeql.github.com/docs/codeql-language-guides/customizing-library-models-for-python/.

CodeQL allows the use of a data extension (YAML file) to specify taint sources, sinks, and propagation rules for external library APIs.

For example, in the motivating case, a YAML file can be created as follows:

```
extensions:
  - addsTo:
      pack: codeql/python-all
      extensible: summaryModel
    data:
      - [
          "hikaru",
          "Member[HikaruBase]",
          "Argument[0]",
          "ReturnValue",
          "taint",
        ]
```

This extension addresses issue 3/ by defining taint propagation rules for the hikaru library.

For issue 2/, separate queries can be written to:

+ Select taint source nodes (APIs whose return values are tainted).
+ Select taint sink nodes (APIs whose arguments should be marked as sinks).
+ Define taint propagation rules (APIs that propagate taint from arguments to sinks).
+ Type models (Define/resolve API return value types).

Based on the generated `.sarif` file, we could automatically generate the extension files and then together with the our previous query to find the vulnerability.

