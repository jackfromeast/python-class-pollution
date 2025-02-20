import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.ApiGraphs


/**
 * @description
 * ----------------------
 * Represents a node that holds the base object of a enumerate/split operation.
 * 
 * @example
 * ----------------------
 * `obj` in `for key, val in obj[:-1]:`
 */
class EnumeratedObjects extends DataFlow::Node {
  EnumeratedObjects(){
    // Match for `for key in dict`
    exists(For forLoop |
      this.asExpr() = forLoop.getIter()
    ) or
    // Match for `for key, val in list[:-1]`
    exists(For forLoop, Subscript subscript |
      forLoop.getIter() = subscript and
      this.asExpr() = subscript.getObject()
    )
    or
    // Match for `for k, v in dict.items()`
    exists(For forLoop, MethodCallNode call |
      forLoop.getIter() = call.asExpr() and
      call.getMethodName() = "items" and
      this = call.getObject()
    )
    or
    // Match for `for key in dict.keys():`
    exists(For forLoop, MethodCallNode call |
      forLoop.getIter() = call.asExpr() and
      call.getMethodName() = "keys" and
      this = call.getObject()
    )
    or 
    // Match for for `key, value in enumerate(dict):`
    exists(For forLoop, API::CallNode call |
      API::builtin("enumerate").getACall() = call and
      forLoop.getIter() = call.asExpr() and
      this.asExpr() = call.asCfgNode().(CallNode).getArg(0).getNode() 
    )
  }
}
