import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import Utils::ClassPolltionUtils
import GetOp::ClassPollutionGetOp

module ClassPollutionAdditionalFlowStep {

/**
 * @description
 * ----------------------
 * Propagate the data flow from getItem operation when object is tainted. 
 * 
 * @example
 * ----------------------
 * when `obj` is tainted in the following code snippet:
 * `obj[key] = val` -> `val`
 * `for key in obj` -> `key`
 * `obj.get(key)` -> `key`
 * 
 */
predicate additionalFlowStepGetItem(DataFlow::Node fromNode, DataFlow::Node toNode) {
  exists(Expr getItemExpr |
    isGetItemOp(fromNode.asExpr(), _, getItemExpr) and
    toNode.asExpr() = getItemExpr
  ) or
  // Match for `for key in obj` or `for key, item in obj`
  exists(For forLoop |
    fromNode.asExpr() = forLoop.getIter() and
    if forLoop.getTarget() instanceof Tuple then
      toNode.asExpr() = forLoop.getTarget().(Tuple).getAnElt()
    else
      toNode.asExpr() = forLoop.getTarget()
  )
  // or
  // TODO: The following pattern will get v20.0.0 codeql binary stuck
  // // Match for `for k, v in dict.items()`
  // exists(For forLoop, MethodCallNode call, Tuple tuple |
  //   forLoop.getIter() = call.asExpr() and
  //   (
  //     call.getMethodName() = "items" or
  //     call.getMethodName() = "enumerate"
  //   ) and
  //   tuple = forLoop.getTarget() and
  //   tuple.getAnElt() = fromNode.asExpr() and
  //   fromNode.asExpr() = call.getObject().asExpr()
  // )
  or
  // Match for `for key in dict.keys():`
  exists(For forLoop, MethodCallNode call |
    forLoop.getIter() = call.asExpr() and
    call.getMethodName() = "keys" and
    toNode.asExpr() = forLoop.getTarget() and
    fromNode.asExpr() = call.getObject().asExpr()
  )
}

/**
 * @description
 * ----------------------
 * Propagate the data flow from getItem operation when key is tainted.
 */
predicate additionalFlowStepGetItemReverse(DataFlow::Node fromNode, DataFlow::Node toNode) {
  // Propagate taint on every getValue operation with the polluted key
  // key -> obj[key]
  exists( DataFlow::Node getItemExpr | 
    isGetItemOp(_, fromNode.asExpr(), getItemExpr.asExpr()) and
    (
      DataFlow::localFlow(getItemExpr, toNode) or
      getItemExpr = toNode
    )
  ) or
  //  for k, v in src.items() -> k -> v
  exists(For forLoop, MethodCallNode call, Tuple tuple |
    forLoop.getIter() = call.asExpr() and
    (
      call.getMethodName() = "items"
    ) and
    tuple = forLoop.getTarget() and
    (
      tuple.getElt(0) = fromNode.asExpr() and
      tuple.getElt(1) = toNode.asExpr()
    )
  )
}

/**
 * @description
 * ----------------------
 * Propagate the data flow from getAttr operation when object is tainted.
 */
predicate additionalFlowStepGetAttr(DataFlow::Node fromNode, DataFlow::Node toNode) {
  exists(AttrRead addrRead |
    addrRead.getObject() = fromNode and
    toNode = addrRead
  )
}

/**
 * @description
 * ----------------------
 * Propagate the data flow from getAttr operation when key is tainted.
 */
predicate additionalFlowStepGetAttrReverse(DataFlow::Node fromNode, DataFlow::Node toNode) {
  // Propagate taint on every getValue operation with the polluted key
  // key -> getattr(obj, key)
  exists( DataFlow::Node getattrCall |
    isGetattrCall(_, fromNode.asExpr(), getattrCall.asExpr()) and
    (
      DataFlow::localFlow(getattrCall, toNode) or
      getattrCall = toNode
    )
  )
}

}