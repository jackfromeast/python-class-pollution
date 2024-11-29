import python
import utils
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic

/**
 * @description
 * ----------------------
 * Check if the expression represents an assignment like `val = obj[key]`.
 * 
 */
predicate isSubscriptOp(Expr obj, Expr key, Subscript subscript) {
  subscript.getObject() = obj and
  subscript.getIndex() = key
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

/**
 * @description
 * ----------------------
 * Check if the expression represents a dynamic assignment like `getattr(obj, key)`.
 * 
 */
predicate isGetattrCall(Expr obj, Expr key, Call call) {
  exists (
    Name name |
    name.getId() = "getattr" and
    call.getFunc() = name
  ) and
  call.getAnArg() = obj and
  call.getAnArg() = key
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
  exists(Call getattrCall, Expr obj, Expr key |
    isGetattrCall(obj, key, getattrCall) and
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
predicate isSmartGettingFuncSingle(Function func, Subscript subscript, Call getattrCall) {
  exists (
    Expr obj1, Expr key1,
    Expr obj2, Expr key2,
    Expr obj, Expr key|
    isSubscriptOp(obj1, key1, subscript) and
    isGetattrCall(obj2, key2, getattrCall) and
    subscript.getScope() = func.getEvaluatingScope() and
    getattrCall.getScope() = func.getEvaluatingScope() and
    hasDataFlowExpr(obj, obj1) and
    hasDataFlowExpr(obj, obj2) and
    hasDataFlowExpr(key, key1) and
    hasDataFlowExpr(key, key2)
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
predicate isSmartGettingFunction(Function sgf, Function subscriptFunc, Function getattrFunc) {
  (
    hasCallEdgeOneJump(sgf, subscriptFunc) and
    hasCallEdgeOneJump(sgf, getattrFunc) and
    exists (
      Expr obj1, Expr key1,
      Expr obj2, Expr key2,
      Expr obj, Expr key |
      hasSubscriptOpFunc(subscriptFunc, obj1, key1) and
      hasGetattrCallFunc(getattrFunc, obj2, key2) and
      hasDataFlowExpr(obj, obj1) and
      hasDataFlowExpr(key, key1)
    )
  )
  or
  (
    exists( Subscript subscript, Call getattrCall |
      isSmartGettingFuncSingle(sgf, subscript, getattrCall) and
      subscript.getScope() = subscriptFunc.getEvaluatingScope() and
      getattrCall.getScope() = getattrFunc.getEvaluatingScope()
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