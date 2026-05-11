import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import Utils::ClassPolltionUtils
import shared.flowsteps.AdditionalFlowStepCustom::ClassPollutionAdditionalFlowStepCustom
import shared.types.DunderDictObject

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
  ) 

  // Case 4: External library calls whose name contains "get" or similar
  // exists(Name funcName |
  //   (
  //     funcName.getId().matches("%get\\_%") or
  //     funcName.getId().matches("%getItem%") or
  //     funcName.getId().matches("%get\\_item%") or
  //     funcName.getId().matches("%getField%") or
  //     funcName.getId().matches("%get\\_field%")
  //   ) and
  //   not isBuiltinFuncCall(call) and
  //   call.getFunc() = funcName and
  //   call.getAnArg() = obj and
  //   call.getAnArg() = key
  // )
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
 * Check if the expression represents a getAttr operation.
 */
predicate isGetAttrOp(Expr obj, Expr key, Expr getAttrExpr) {
  // `obj.__dict__[key]`
  isGetAttrThroughObjectDunderDictSubscript(obj, key, getAttrExpr.(Subscript))
  or  
  isGetattrCall(obj, key, getAttrExpr.(Call))
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
  // `obj.__dict__.get(key)`
  isGetAttrThroughObjectDunderDictCall(obj, key, call) or
  // `inspect.getattr_static(obj, attr)`
  isGetAttrThroughInspect(obj, key, call) or
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
 * Calls to `obj.__dict__.get(key)` or `obj.__dict__[key]`.
 */
predicate isGetAttrThroughObjectDunderDictCall(Expr obj, Expr key, Call call) {
  exists ( DunderDictObject dunderDictObject |
    dunderDictObject.getBaseObject().asExpr() = obj and
    isGetItemCall(dunderDictObject.asExpr(), key, call)
  )
}

/**
 * Calls to `obj.__dict__.get(key)` or `obj.__dict__[key]`.
 */
predicate isGetAttrThroughObjectDunderDictSubscript(Expr obj, Expr key, Subscript subscript) {
  exists ( DunderDictObject dunderDictObject |
    dunderDictObject.getBaseObject().asExpr() = obj and
    isSubscriptOp(dunderDictObject.asExpr(), key, subscript)
  )
}

/**
 * Calls to `inspect.getattr_static(obj, attr)`
 */
predicate isGetAttrThroughInspect(Expr obj, Expr key, Call call) {
  API::moduleImport("inspect").getMember("getattr_static").getACall().asExpr() = call and
  call.getArg(0) = obj and
  call.getArg(1) = key 
}

/**
 * External library calls whose name contains "attr", "getattr", or "get".
 */
predicate isLibraryWrapperCall(Expr obj, Expr key, Call call) {
  exists (Name funcName |
    (
      funcName.getId().matches("getprop")
    ) and
    not isBuiltinFuncCall(call) and
    call.getFunc() = funcName and
    call.getArg(0) = obj and
    call.getArg(1) = key
  ) or
  // https://hikaru.readthedocs.io/en/latest/hikaru-base.html#object-at-path
  // A methodCall named object_at_path and has been defined in the hikaru module
  hikaruObjectAtPath(obj, key, call)
}

}