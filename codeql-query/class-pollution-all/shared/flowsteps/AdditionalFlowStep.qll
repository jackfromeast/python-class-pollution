import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import shared.Utils::ClassPolltionUtils
import shared.GetOp::ClassPollutionGetOp
import shared.types.SelfReferringGetOp::SelfReferringGetOp
import shared.types.DunderDictObject
import shared.flowsteps.AdditionalFlowStepDeque::ClassPollutionAdditionalFlowStepDeque
import shared.flowsteps.AdditionalFlowStepReduce::ClassPollutionAdditionalFlowStepReduce
import shared.flowsteps.AdditionalFlowStepNamedtuple::ClassPollutionAdditionalFlowStepNamedtuple
import shared.flowsteps.AdditionalFlowStepCustom::ClassPollutionAdditionalFlowStepCustom
import shared.Debug::Debugging

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
  or
  // TODO: The following pattern will get v20.0.0 codeql binary stuck
  // Match for `for k, v in dict.items()`
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
  // or
  // Match for `for key in dict.keys():`
  exists(For forLoop, MethodCallNode call |
    forLoop.getIter() = call.asExpr() and
    call.getMethodName() = "keys" and
    toNode.asExpr() = forLoop.getTarget() and
    fromNode.asExpr() = call.getObject().asExpr()
  ) 
  or 
  // Match for `for key, value in zip(list1, list2):`
  exists(For forLoop, Call call, API::CallNode callNode, Tuple tuple |
    forLoop.getIter() = call and
    callNode.asExpr() = call and
    callNode =  API::builtin("zip").getACall() and
    tuple = forLoop.getTarget() and
    exists (int i |
      tuple.getElt(i) = toNode.asExpr() and
      call.getArg(i) = fromNode.asExpr()
    ) 
  )
}

/**
 * @description
 * ----------------------
 * Propagate the data flow from getItem operation when key is tainted.
 * 
 * @note
 * ----------------------
 * This should be precise that fromNode is the key and toNode is the val.
 */
predicate additionalFlowStepGetItemReverse(DataFlow::Node fromNode, DataFlow::Node toNode) {
  // restrictedByFunctionName(fromNode, "_t_eval") and
  // restrictedByFunctionName(toNode, "_t_eval") and
  (
  // Propagate taint on every getValue operation with the polluted key
  // key -> obj[key]
  exists( DataFlow::Node getItemExpr, DataFlow::Node baseObj | 
    isGetItemOp(baseObj.asExpr(), fromNode.asExpr(), getItemExpr.asExpr()) and
    // toNode should never be a getItem operation whose base object is an dunder dict object.
    not exists (DunderDictObject dunerDictObject | dunerDictObject = baseObj) and
    toNode = getItemExpr
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
  )) and
  toNode instanceof SelfReferringGetOp
}

/**
 * @description
 * ----------------------
 * Propagate the data flow from getAttr operation when object is tainted.
 */
predicate additionalFlowStepGetAttr(DataFlow::Node fromNode, DataFlow::Node toNode) {
  // restrictedByFunctionName(fromNode, "_t_eval") and
  exists(AttrRead addrRead |
    addrRead.getObject() = fromNode and
    toNode = addrRead
  ) or
  isGetAttrOp(fromNode.asExpr(), _, toNode.asExpr())
}

/**
 * @description
 * ----------------------
 * Propagate the data flow from getAttr operation when key is tainted.
 * 
 * @note
 * ----------------------
 * This should be precise that fromNode is the key and toNode is the val.
 */
predicate additionalFlowStepGetAttrReverse(DataFlow::Node fromNode, DataFlow::Node toNode) {
  // restrictedByFunctionName(fromNode, "getattr_through_dict_attr_1") and
  // restrictedByFunctionName(toNode, "_t_eval") and
  isGetAttrOp(_, fromNode.asExpr(), toNode.asExpr()) and
  toNode instanceof SelfReferringGetOp
}

}