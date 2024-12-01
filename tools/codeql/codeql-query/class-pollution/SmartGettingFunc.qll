import python
import Utils
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.internal.TaintTrackingPublic

/**
 * @description
 * ----------------------
 * Check if the expression represents an assignment like `val = obj[key]`.
 * 
 */
predicate isSubscriptOp(Expr obj, Expr key, Subscript subscript) {
  subscript.getObject() = obj and
  subscript.getIndex() = key and
  not exists(Assign assign |
    assign.getATarget() = subscript
  )
}

/**
 * @description
 * ----------------------
 * Check if the expression represents a dynamic retrieval like `obj.get(key)`.
 */
predicate isGetItemCall(Expr obj, Expr key, Call call) {
  exists(MethodCallNode callNode |
    callNode.asExpr() = call and
    callNode.getMethodName() = "get" and
    callNode.getObject().asExpr() = obj and
    call.getAnArg() = key
  )
}

predicate isGetItemOp(Expr obj, Expr key, Expr getItemExpr) {
  isSubscriptOp(obj, key, getItemExpr.(Subscript))
  or  
  isGetItemCall(obj, key, getItemExpr.(Call))
}

/**
 * @description
 * ----------------------
 * Check if the expression represents a dynamic assignment like `getattr(obj, key)`.
 * 
 */
predicate isGetattrCall(Expr obj, Expr key, Call call) {
  exists (
    Name name|
    name.getId() = "getattr" and
    call.getFunc() = name and
    call.getAnArg() = obj and
    call.getAnArg() = key
  )
}


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
    isGetattrCall(obj, key, _) and
    obj.getScope() = func.getEvaluatingScope() and
    key.getScope() = func.getEvaluatingScope() and
    localExprTaint(objArg, obj) and
    localExprTaint(keyArg, key) and
    func.getAnArg() = objArg and
    func.getAnArg() = keyArg
  )
}

// predicate hasGetattrCallFuncRecursive(Function func, Expr objArg, Expr keyArg) {
//   hasGetattrCallFunc(func, objArg, keyArg) and 
  
// }

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
 * def base_set(obj, key, value, allow_override=True):
 *  if isinstance(obj, dict):
 *   if allow_override or key not in obj:
 *    obj[key] = value
 *  elif (allow_override or not hasattr(obj, key)) and obj is not None:
 *    setattr(obj, key, value)
 */
predicate isSmartGettingFuncSingle(Function func) {
  exists( DataFlow::Node key, DataFlow::Node obj, 
    DataFlow::Node key1, DataFlow::Node obj1,
    DataFlow::Node key2, DataFlow::Node obj2 |
    key.getScope() = func.getEvaluatingScope() and
    obj.getScope() = func.getEvaluatingScope() and
    isGetItemOp(obj1.asExpr(), key1.asExpr(), _) and
    isGetattrCall(obj2.asExpr(), key2.asExpr(), _) and
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
 * Find all the seemless-getting functions (across functions) that achieves `obj[key]` and `getattr(obj, key)` in its function body or its callee functions.
 * 
 * @condition
 * ----------------------
 * 1/ There is a call flow from the seemless-getting function (i.e., sgf) to the callee functions (i.e., func1, func2).
 * 2/ There are dataflow paths from sgf's identifier obj, key to the obj, key in operations `obj[key]` and `getattr(obj, key)` in func1, func2.
 * 3/ The obj and key in the seemless-getting function should refer to the same variable.
 * 
 * @example
 * ----------------------
 * base_get: https://github.com/dgilland/pydash/blob/f4112f61ddb02e5181e781709d775838c9978b97/src/pydash/helpers.py#L136C1-L206C17
 * 
 */
predicate isSmartGettingFunction(Function sgf, Subscript subscript, Call getattrCall) {
  exists( DataFlow::Node key, DataFlow::Node obj, 
          DataFlow::Node key1, DataFlow::Node obj1,
          DataFlow::Node key2, DataFlow::Node obj2 |
    key.getScope() = sgf.getEvaluatingScope() and
    obj.getScope() = sgf.getEvaluatingScope() and
    isSubscriptOp(obj1.asExpr(), key1.asExpr(), subscript)
    // isGetattrCall(obj2.asExpr(), key2.asExpr(), getattrCall) and
    // TrackingSmartGettingObjectFlow::flow(obj, obj1) 
    // TrackingSmartGettingKeyFlow::flow(key, key1) and
    // TrackingSmartGettingObjectFlow::flow(obj, obj2) and
    // TrackingSmartGettingKeyFlow::flow(key, key2)
  )
}

// predicate isSmartGettingFunction(Function sgf, Function subscriptFunc, Function getattrFunc) {
//   (
//     hasCallEdgeOneJump(sgf, subscriptFunc) and
//     hasCallEdgeOneJump(sgf, getattrFunc) and
//     exists (
//       Expr obj1, Expr key1,
//       Expr obj2, Expr key2,
//       Expr obj, Expr key |
//       hasSubscriptOpFunc(subscriptFunc, obj1, key1) and
//       hasGetattrCallFunc(getattrFunc, obj2, key2) and
//       hasDataFlowExpr(obj, obj1) and
//       hasDataFlowExpr(key, key1)
//     )
//   )
//   or
//   (
//     exists( Subscript subscript, Call getattrCall |
//       isSmartGettingFuncSingle(sgf, subscript, getattrCall) and
//       subscript.getScope() = subscriptFunc.getEvaluatingScope() and
//       getattrCall.getScope() = getattrFunc.getEvaluatingScope()
//     )
//   )
// }




/**
 * @description
 * ----------------------
 * Check if the SmartGettingFunction is called within a loop or recursively.
 */
predicate hasMultiSmartGettingFunc(Function func) {
  exists(CallNode call, Function smartGettingFunc |
    func.getEvaluatingScope() = call.getScope() and
    isSmartGettingFunction(smartGettingFunc, _, _) and
    call.getFunction().refersTo(smartGettingFunc.getFunctionObject()) and
    (
      // Case 1: The call is within a loop
      isWithinLoop(call.getNode()) or
      // Case 2: The call is recursive
      isRecursiveFunc(smartGettingFunc)
    )
  )
}