import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic

module ClassPollutionGetOp {
  
/**
 * @description
 * ----------------------
 * Check if the expression represents a getItem operation through brackets like `val = obj[key]`.
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
 * Check if the expression represents a getItem operation through method call like `obj.get(key)`.
 * Supports direct calls to `get`, `__getitem__`, or equivalent library methods.
 */
predicate isGetItemCall(Expr obj, Expr key, Call call) {
  // Case 1: Direct calls to `obj.get(key)`
  exists(MethodCallNode callNode |
    callNode.asExpr() = call and
    callNode.getMethodName() = "get" and
    callNode.getObject().asExpr() = obj and
    call.getArg(0) = key
  ) or

  // Case 2: Calls to `obj.__getitem__(key)`
  exists(AttrRead attrAccess, DataFlow::Node objNode|
    attrAccess.accesses(objNode, "__getitem__") and
    call.getFunc() = attrAccess.asExpr() and
    call.getArg(0) = key and
    objNode.asExpr() = obj
  ) or

  // Case 3: Calls to `obj.pop(key)` (equivalent to `obj.__getitem__(key)`)
  exists(MethodCallNode callNode |
    callNode.asExpr() = call and
    callNode.getMethodName() = "pop" and
    callNode.getObject().asExpr() = obj and
    call.getArg(0) = key
  ) or

  // Case 4: External library calls whose name contains "get" or similar
  exists(Name funcName |
    (
      funcName.getId().matches("%get%") or
      funcName.getId().matches("%item%") or
      funcName.getId().matches("%field%")
    ) and
    call.getFunc() = funcName and
    call.getAnArg() = obj and
    call.getAnArg() = key
  )
}


/**
 * @description
 * ----------------------
 * Check if the expression represents a getItem operation.
 */
predicate isGetItemOp(Expr obj, Expr key, Expr getItemExpr) {
  isSubscriptOp(obj, key, getItemExpr.(Subscript))
  or  
  isGetItemCall(obj, key, getItemExpr.(Call))
}

/**
 * @description
 * ----------------------
 * Check if the expression represents a `getattr` operation like `getattr(obj, key)`.
 * Supports direct calls to `getattr`, `__getattribute__`, or library wrappers.
 */
predicate isGetattrCall(Expr obj, Expr key, Call call) {
  // Direct `getattr(obj, key)`
  isDirectGetattrCall(obj, key, call) or
  // `obj.__getattribute__(key)`
  isGetattributeCall(obj, key, call) or
  // `object.__getattribute__(obj, key)`
  isObjectGetattributeCall(obj, key, call) or
  // Library wrapper API calls, e.g., `lib.resolveAttr(obj, key)`
  isLibraryWrapperCall(obj, key, call)
}

/**
 * Direct calls to `getattr(obj, key)`.
 */
predicate isDirectGetattrCall(Expr obj, Expr key, Call call) {
  exists (Name name |
    name.getId() = "getattr" and
    call.getFunc() = name and
    call.getArg(0) = obj and
    call.getArg(1) = key
  )
}

/**
 * Calls to `obj.__getattribute__(key)`.
 */
predicate isGetattributeCall(Expr obj, Expr key, Call call) {
  exists (AttrRead attrAccess, DataFlow::Node objNode |
    attrAccess.accesses(objNode, "__getattribute__") and
    objNode.asExpr() = obj and
    call.getFunc() = attrAccess.asExpr() and
    call.getArg(0) = key
  )
}

/**
 * Calls to `object.__getattribute__(obj, key)`.
 */
predicate isObjectGetattributeCall(Expr obj, Expr key, Call call) {
  exists (AttrRead attrAccess, Variable variable|
    variable.getId() = "object" and
    attrAccess.getObject().asCfgNode() = variable.getAUse() and
    attrAccess.mayHaveAttributeName("__getattribute__") and
    call.getFunc() = attrAccess.asExpr() and
    call.getArg(0) = obj and
    call.getArg(1) = key
  )
}

/**
 * External library calls whose name contains "attr", "getattr", or "get".
 */
predicate isLibraryWrapperCall(Expr obj, Expr key, Call call) {
  exists (Name funcName |
    (
      funcName.getId().matches("%attr%")
    ) and
    call.getFunc() = funcName and
    call.getAnArg() = obj and
    call.getAnArg() = key
  )
}

}