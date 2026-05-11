import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.TaintTracking
import semmle.python.ApiGraphs
import shared.Debug::Debugging

/**
 * @description
 * ----------------------
 * Represents a node that holds the key names that are enumerated in the code.
 * 
 * @example
 * ----------------------
 * `key` in `for key in dict:`
 * `key` in `for key in dict.keys():`
 * `key` in `for key in keys`
 * `key` and `val` in `for key, val in dict.items():`
 *  * `key` and `val` in `for key, val in list[:-1]` The item of list can be a tuple.
 */
class EnumeratedKeyNames extends DataFlow::Node {
  EnumeratedKeyNames() {
    // Match for `for key in dict`
    exists(For forLoop |
      this.asExpr() = forLoop.getTarget() and
      not forLoop.getTarget() instanceof Tuple
    ) or
    // Match for `for key, val in list[:-1]`
    exists(For forLoop, Tuple tuple |
      tuple = forLoop.getTarget() and
      (
        tuple.getElt(0) = this.asExpr() or
        tuple.getElt(1) = this.asExpr()
      )
    )
    or
    // Match for `for k, v in dict.items()`
    exists(For forLoop, MethodCallNode call, Tuple tuple |
      forLoop.getIter() = call.asExpr() and
      call.getMethodName() = "items" and
      tuple = forLoop.getTarget() and
      (
        tuple.getElt(0) = this.asExpr() or
        tuple.getElt(1) = this.asExpr()
      )
    )
    or
    // Match for `for key in dict.keys():`
    exists(For forLoop, MethodCallNode call |
      forLoop.getIter() = call.asExpr() and
      call.getMethodName() = "keys" and
      this.asExpr() = forLoop.getTarget()
    )
    or 
    // Match for for `key, value in enumerate(dict):`
    exists(For forLoop, API::CallNode call, Tuple tuple |
      API::builtin("enumerate").getACall() = call and
      forLoop.getIter() = call.asExpr() and
      tuple = forLoop.getTarget() and
      (
        tuple.getElt(0) = this.asExpr() or
        tuple.getElt(1) = this.asExpr()
      )
    )
    or
    // Match for `while i < ANY: key = list[i]; i += 1`
    exists(While whileLoop, Subscript subscript, Compare cmp, Lt ltOp, LtE lteOp, Expr iInLoop, Expr iInSubscript |
      whileLoop.contains(cmp) and
      (
        cmp.compares(iInLoop, ltOp, _) or
        cmp.compares(iInLoop, lteOp, _)
      ) and

      // Match for `key = list[i]` or `key = list[i+1]`
      exists( DataFlow::Node iInLoopNode, DataFlow::Node iInSubscriptNode |
        iInLoopNode.asExpr() = iInLoop and
        iInSubscriptNode.asExpr() = iInSubscript and
        TaintTracking::localTaint(iInLoopNode, iInSubscriptNode) and
        subscript = this.asExpr() and
        subscript.getIndex() = iInSubscriptNode.asExpr()
      ) 
    )
    or
    // Match for `for i in range(len(list)): key = list[i]`
    exists(For forLoop, Expr iInLoop, Expr iInSubscript, Subscript subscript|
      forLoop.getTarget() = iInLoop and
      exists (DataFlow::Node iInLoopNode, DataFlow::Node iInSubscriptNode |
        iInLoopNode.asExpr() = iInLoop and
        iInSubscriptNode.asExpr() = iInSubscript and
        TaintTracking::localTaint(iInLoopNode, iInSubscriptNode) and
        subscript = this.asExpr() and
        subscript.getIndex() = iInSubscriptNode.asExpr()
      )
    )
  }
}


predicate enumeratedKeyNamesAndObjectPair(DataFlow::Node key, DataFlow::Node obj) {
  // Match for `for key in dict`
  exists(For forLoop |
    key.asExpr() = forLoop.getTarget() and
    obj.asExpr() = forLoop.getIter() and
    not forLoop.getTarget() instanceof Tuple
  ) or
  // Match for `for key, val in list[:-1]`
  exists(For forLoop, Tuple tuple |
    tuple = forLoop.getTarget() and
    obj.asExpr() = forLoop.getIter() and
    (
      tuple.getElt(0) = key.asExpr() or
      tuple.getElt(1) = key.asExpr()
    )
  )
  or
  // Match for `for k, v in dict.items()`
  exists(For forLoop, MethodCallNode call, Tuple tuple |
    forLoop.getIter() = call.asExpr() and
    call.getMethodName() = "items" and
    call.getObject() = obj and
    tuple = forLoop.getTarget() and
    (
      tuple.getElt(0) = key.asExpr() or
      tuple.getElt(1) = key.asExpr()
    )
  )
  or
  // Match for `for key in dict.keys():`
  exists(For forLoop, MethodCallNode call |
    forLoop.getIter() = call.asExpr() and
    call.getMethodName() = "keys" and
    key.asExpr() = forLoop.getTarget() and
    call.getObject() = obj
  )
  or 
  // Match for for `key, value in enumerate(dict):`
  exists(For forLoop, API::CallNode call, Tuple tuple |
    API::builtin("enumerate").getACall() = call and
    forLoop.getIter() = call.asExpr() and
    tuple = forLoop.getTarget() and
    obj.asExpr() = call.asCfgNode().(CallNode).getArg(0).getNode() and
    (
      tuple.getElt(0) = key.asExpr() or
      tuple.getElt(1) = key.asExpr()
    )
  )
  or 
  // Match for `while i < ANY: key = list[i]; i += 1`
  exists(While whileLoop, Subscript subscript, Compare cmp, Lt ltOp, LtE lteOp, Expr iInLoop, Expr iInSubscript |
    whileLoop.contains(cmp) and
    (
      cmp.compares(iInLoop, ltOp, _) or
      cmp.compares(iInLoop, lteOp, _)
    ) and
    // Match for `key = list[i]`
    exists( DataFlow::Node iInLoopNode, DataFlow::Node iInSubscriptNode |
      iInLoopNode.asExpr() = iInLoop and
      iInSubscriptNode.asExpr() = iInSubscript and
      TaintTracking::localTaint(iInLoopNode, iInSubscriptNode) and
      subscript.getObject() = obj.asExpr() and
      subscript = key.asExpr() and
      subscript.getIndex() = iInSubscript
    ) 
  )
  or 
  // Match for `for i in range(len(list)): key = list[i]`
  exists(For forLoop, Expr iInLoop, Expr iInSubscript, Subscript subscript|
    forLoop.getTarget() = iInLoop and
    exists (DataFlow::Node iInLoopNode, DataFlow::Node iInSubscriptNode |
      iInLoopNode.asExpr() = iInLoop and
      iInSubscriptNode.asExpr() = iInSubscript and
      TaintTracking::localTaint(iInLoopNode, iInSubscriptNode) and
      subscript.getObject() = obj.asExpr() and
      subscript = key.asExpr() and
      subscript.getIndex() = iInSubscript
    )
  )
}