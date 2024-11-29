import python
import semmle.python.dataflow.new.DataFlow
import utils

/**
 * @description
 * ----------------------
 * Represents a node that holds the key names that are enumerated in the code.
 * 
 * @example
 * ----------------------
 * `for key in dict:`
 * `for k, v in dict.items():`
 * `for k in dict.keys():`
 * 
 */
class EnumeratedKeyNames extends DataFlow::Node {
  EnumeratedKeyNames() {
    // Match for `for key in dict`
    exists(For forLoop, Expr container |
      forLoop.getIter() = container and
      container.getType().hasQualifiedName("dict") and
      this = forLoop.getVariable(0)
    )
    or
    // Match for `for k, v in dict.items()`
    exists(ForStmt forLoop, CallExpr call |
      forLoop.getIter() = call and
      call.getCallee().matchesName("items") and
      this = forLoop.getVariable(0)
    )
    or
    // Match for `for k in dict.keys()`
    exists(ForStmt forLoop, CallExpr call |
      forLoop.getIter() = call and
      call.getCallee().matchesName("keys") and
      this = forLoop.getVariable(0)
    )
  }
}

/**
 * Holds if `node` is a source of key names that we consider possible
 * class pollution payloads.
 */
predicate isPollutedKeyNameSource(DataFlow::Node node) {
  node instanceof EnumeratedKeyNames
  or
  node instanceof SplitPropName
}