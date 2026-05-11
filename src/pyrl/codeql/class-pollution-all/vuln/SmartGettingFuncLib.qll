import python
import shared.Utils::ClassPolltionUtils
import shared.GetOp::ClassPollutionGetOp
import shared.flowsteps.AdditionalFlowStep::ClassPollutionAdditionalFlowStep
import vuln.ClassPollutionTaintTrackingLib::ClassPollutionTaintTracking
import semmle.python.ApiGraphs
import codeql.dataflow.DataFlow
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.internal.TaintTrackingPublic

module ClassPollutionSmartGetting {

/**
 * @description
 * ----------------------
 * Check if a subscript operation exists where both the object and the index from function arguments.
 */
predicate hasSubscriptOpFunc(Function func, Expr objArg, Expr keyArg) {  
  exists(Subscript subscript, Expr obj, Expr key |
    isSubscriptOp(obj, key, subscript) and
    obj.getScope() = func.getEvaluatingScope() and
    key.getScope() = func.getEvaluatingScope() and
    hasDataFlowExpr(objArg, obj) and
    hasDataFlowExpr(keyArg, key) and
    func.getAnArg() = objArg and
    func.getAnArg() = keyArg
  )
}

/**
 * @description
 * ----------------------
 * Check if a getattr call exists where both the object and the key from function arguments.
 */
predicate hasGetattrCallFunc(Function func, Expr objArg, Expr keyArg) {
  exists(Expr obj, Expr key |
    isGetAttrOp(obj, key, _) and
    obj.getScope() = func.getEvaluatingScope() and
    key.getScope() = func.getEvaluatingScope() and
    localExprTaint(objArg, obj) and
    localExprTaint(keyArg, key) and
    func.getAnArg() = objArg and
    func.getAnArg() = keyArg
  )
}

/**
 * @description
 * ----------------------
 * A FlowState to indicate whether the data is used as a key or object in getItem/getAttr operation.
 */
abstract class FlowState extends string {
  bindingset[this]
  FlowState() { any() }
}

class UsedAsBaseObjectInGetItemFlowState extends ClassPollutionSmartGetting::FlowState {
  UsedAsBaseObjectInGetItemFlowState() { this = "UsedAsBaseObjectInGetItem" }
}

class UsedAsKeyInGetItemFlowState extends ClassPollutionSmartGetting::FlowState {
  UsedAsKeyInGetItemFlowState() { this = "UsedAsKeyInGetItem" }
}

class UsedAsBaseObjectInGetAttrFlowState extends ClassPollutionSmartGetting::FlowState {
  UsedAsBaseObjectInGetAttrFlowState() { this = "UsedAsBaseObjectInGetAttr" }
}

class UsedAsKeyInGetAttrFlowState extends ClassPollutionSmartGetting::FlowState {
  UsedAsKeyInGetAttrFlowState() { this = "UsedAsKeyInGetAttr" }
}

/**
 * @description
 * ----------------------
 * Tracking from function parameters to the key in the getItem operations.
 * 
 * @example
 * ----------------------
 * It should select out the obj and key from the following code snippet.
   def parent(obj, key):                           # Source: obj, key are both function arguments.         
    if isinstance(obj, dict):
      return child1({'obj': obj, 'attr': key})
    else:
      return child2({'obj': obj, 'attr': key})

  def child1(path):
    obj = path.get('obj')                          # FP: 'obj' doesn't refer to the function argument.
    attr = path.get('attr')                        # FP: 'attr' doesn't refer to the function argument.       

    return obj[attr]                               # Sink: obj, attr are both come from the arguments of parent function.
* 
*/
module TrackingParamToSmartGettingOpConfiguration implements DataFlow::StateConfigSig {
  class FlowState = ClassPollutionSmartGetting::FlowState;

  predicate isSource(DataFlow::Node source, FlowState state) {
    exists(Parameter param |
      (param instanceof Name and source.asExpr() = param) or
      (param instanceof Tuple and source.asExpr() = param.(Tuple).getAnElt())
    )
  }

  predicate isSink(DataFlow::Node sink, FlowState state) {
    (isGetItemOp(_, sink.asExpr(), _) and state instanceof UsedAsKeyInGetItemFlowState) or
    (isGetItemOp(sink.asExpr(), _, _) and state instanceof UsedAsBaseObjectInGetItemFlowState) or
    (isGetAttrOp(_, sink.asExpr(), _) and state instanceof UsedAsKeyInGetAttrFlowState) or
    (isGetAttrOp(sink.asExpr(), _, _) and state instanceof UsedAsBaseObjectInGetAttrFlowState)
  }

  predicate isAdditionalFlowStep(DataFlow::Node fromNode, DataFlow::Node toNode) {
    additionalFlowStepGetAttr(fromNode, toNode) or
    additionalFlowStepGetItem(fromNode, toNode) or
    // Patch for glom library
    // `ret = arg_val(target, arg, scope)`: `arg` -> `ret`
    exists(Call call, Function func |
        call.getArg(1) = fromNode.asExpr() and
        call = toNode.asExpr() and
        call.getAFlowNode() = func.getFunctionObject().getAFunctionCall() and
        func.getName() = "arg_val"
    )
  }
}


module TrackingParamToSmartGettingOpFlow = DataFlow::GlobalWithState<TrackingParamToSmartGettingOpConfiguration>;
module Flow = TrackingParamToSmartGettingOpFlow; // For shortening the name

predicate isFuncParamter(DataFlow::Node node) {
  exists(Parameter param|
    (param instanceof Name and node.asExpr() = param) or
    (param instanceof Tuple and node.asExpr() = param.(Tuple).getAnElt())
  )
}


predicate inFunctionForDebugging(DataFlow::Node node) {
  exists(Function func|
    func.getEvaluatingScope() = node.getScope() and
    func.getName() = "_t_eval"
  )
}

/**
 * @description
 * ----------------------
 * Select out the smart getting function whose parameters would flow to both the base object and key in getItem and getAttr operations.
 * 
 * @note
 * ----------------------
 * CodeQL doesn't support two flowPath query with the same source or sink nodes.
 * As the selected source node is path-annotated.
 * E.g., TrackingParamToSmartGettingOpFlow::flowPath(sourceObj, getItemKey) and TrackingParamToSmartGettingOpFlow::flowPath(sourceKey, getItemKey) would result in empty results.
 * Therefore, we select the sourceObj and sourceKey respectively in their own flowPath query.
 * 
 */
predicate isSmartGettingFunction_ (Flow::PathNode sourceObjToItem, Flow::PathNode sourceKeyToItem, Flow::PathNode sourceObjToAttr, Flow::PathNode sourceKeyToAttr, Flow::PathNode getItemObj, Flow::PathNode getItemKey, Flow::PathNode getAttrObj, Flow::PathNode getAttrKey) {
  (
    // Make sure the source nodes are from the same function and are the same function parameters underlying.
    sourceKeyToAttr.getNode() = sourceKeyToItem.getNode() and
    sourceObjToAttr.getNode() = sourceObjToItem.getNode() and
    sourceKeyToAttr.getNode().getScope() = sourceObjToAttr.getNode().getScope()
  ) and
  (
    isFuncParamter(sourceObjToItem.getNode()) and isFuncParamter(sourceKeyToItem.getNode()) and
    isFuncParamter(sourceObjToAttr.getNode()) and isFuncParamter(sourceKeyToAttr.getNode())
  ) and
  (
    isGetItemOp(getItemObj.getNode().asExpr(), getItemKey.getNode().asExpr(), _) and
    isGetAttrOp(getAttrObj.getNode().asExpr(), getAttrKey.getNode().asExpr(), _)
  ) and
  (
    Flow::flowPath(sourceObjToItem, getItemObj) and
    Flow::flowPath(sourceKeyToItem, getItemKey) and
    getItemKey.getState() instanceof UsedAsKeyInGetItemFlowState and
    getItemObj.getState() instanceof UsedAsBaseObjectInGetItemFlowState
  ) and 
  (
    Flow::flowPath(sourceObjToAttr, getAttrObj) and
    Flow::flowPath(sourceKeyToAttr, getAttrKey) and
    getAttrKey.getState() instanceof UsedAsKeyInGetAttrFlowState and
    getAttrObj.getState() instanceof UsedAsBaseObjectInGetAttrFlowState
  )
}

predicate isSmartGettingFunction(Function func) {
  exists(TrackingParamToSmartGettingOpFlow::PathNode sourceObj, TrackingParamToSmartGettingOpFlow::PathNode sourceKey|
    isSmartGettingFunction_(sourceObj, sourceKey, _, _, _, _, _, _) and 
    sourceObj.getNode().getScope() = func.getEvaluatingScope() and
    sourceKey.getNode().getScope() = func.getEvaluatingScope()
  )
}

/**
 * @description
 * ----------------------
 * Find all the seemless-getting functions (single) that has both `obj[key] = val` and `setattr(obj, key, val)` in the same function body.
 * 
 * @note
 * ----------------------
 * This only find the function with both ` val = obj[key]` and `getattr(obj, key, val)` in the same function body.
 * 
 * @example
 * ----------------------
 * def base_get(obj, key, value, allow_override=True):
 *  if isinstance(obj, dict):
 *   if allow_override or key not in obj:
 *    return obj[key]
 *  elif (allow_override or not hasattr(obj, key)) and obj is not None:
 *    return getattr(obj, key)
 */
predicate isSmartGettingFuncLocal(Function func) {
  exists( DataFlow::Node key, DataFlow::Node obj, 
    DataFlow::Node key1, DataFlow::Node obj1,
    DataFlow::Node key2, DataFlow::Node obj2 |
    key.getScope() = func.getEvaluatingScope() and
    obj.getScope() = func.getEvaluatingScope() and
    isGetItemOp(obj1.asExpr(), key1.asExpr(), _) and
    isGetAttrOp(obj2.asExpr(), key2.asExpr(), _) and
    (
      DataFlow::localFlow(obj, obj1) or 
      obj = obj1
    ) and
    (
      DataFlow::localFlow(key, key1) or 
      key = key1
    ) and
    (
      DataFlow::localFlow(obj, obj2) or 
      obj = obj2
    ) and
    (
      DataFlow::localFlow(key, key2) or 
      key = key2
    )
  )
}

/**
 * @description
 * ----------------------
 * Check if the SmartGettingFunction is called within a loop or recursively.
 */
predicate hasMultiSmartGettingFunc(Function func) {
  exists(CallNode call, Function smartGettingFunc |
    func.getEvaluatingScope() = call.getScope() and
    // isSmartGettingFunction(smartGettingFunc, _, _) and
    call.getFunction().refersTo(smartGettingFunc.getFunctionObject()) and
    (
      // Case 1: The call is within a loop
      isWithinLoop(call.getNode()) or
      // Case 2: The call is recursive
      isRecursiveFunc(smartGettingFunc)
    )
  )
}

}