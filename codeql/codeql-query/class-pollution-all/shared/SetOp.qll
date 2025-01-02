import python
import shared.Utils::ClassPolltionUtils
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic


module ClassPollutionSetOp {

/**
 * @description
 * ----------------------
 * Check if the expression represents an assignment like `obj[key] = val`.
 */
predicate isSubscriptAssignment(Expr obj, Expr key, Expr val, Assign a) {
  // Case 1: Subscript assignment `obj[key] = val`
  exists(Subscript subscript |
    subscript = a.getATarget() and
    subscript.getObject() = obj and
    subscript.getIndex() = key and
    a.getValue() = val
  ) 
}

/**
 * @description
 * ----------------------
 * Check if the expression represents a dictionary-like "set item" call, such as:
 *   obj.__setitem__(key, val)
 *   obj.update({key: val})
 *   obj.setdefault(key, val)
 *   library.setItem(obj, key, val)
 * etc.
 */
predicate isSetItemCall(Expr obj, Expr key, Expr val, Call call) {
  // Case 1: Calls to `obj.__setitem__(key, val)`
  exists (AttrRead attrAccess, DataFlow::Node objNode |
    attrAccess.accesses(objNode, "__setitem__") and
    call.getFunc() = attrAccess.asExpr() and
    call.getArg(0) = key and
    call.getArg(1) = val and
    objNode.asExpr() = obj
  ) or

  // Case 2: Calls to `obj.update({key: val})`
  // exists (MethodCallNode callNode, DataFlow::Node dictNode |
  //   callNode.asExpr() = call and
  //   callNode.getMethodName() = "update" and
  //   callNode.getObject().asExpr() = obj and
  //   callNode.getArg(0) = dictNode and
    
  //   // key and value should has a dataflow path to the dictionary
  // ) or

  // Case 3: Calls to `obj.setdefault(key, val)`
  exists (MethodCallNode callNode |
    callNode.asExpr() = call and
    callNode.getMethodName() = "setdefault" and
    callNode.getObject().asExpr() = obj and
    callNode.getArg(0).asExpr() = key and
    callNode.getArg(1).asExpr() = val
  ) or

  // Case 4: External or library calls: e.g., library.setSomething(obj, key, val)
  exists (Name funcName |
    (
      funcName.getId().matches("%set%") or
      funcName.getId().matches("%put%") or
      funcName.getId().matches("%update%")
    ) and
    call.getFunc() = funcName and

    // We don't assume fixed argument ordering for library calls,
    // so we check that obj, key, and val appear among the arguments.
    call.getAnArg() = obj and
    call.getAnArg() = key and
    call.getAnArg() = val
  )
}

predicate isSetItemExpr(Expr obj, Expr key, Expr val) {
  exists (Call call |
    isSetItemCall(obj, key, val, call)
  )
  or 
  exists (Assign assign |
    isSubscriptAssignment(obj, key, val, assign)
  )
}


/**
 * @description
 * ----------------------
 * Check if the expression represents a dynamic assignment like `setattr(obj, key, val)`.
 * Also detects `obj.__setattr__(key, val)`, `object.__setattr__(obj, key, val)`,
 * or external library calls whose name contains "setattr" or "set".
 */
predicate isSetattrCall(Expr obj, Expr key, Expr val, Call call) {

  //
  // Case 1: Direct calls to `setattr(obj, key, val)`
  //
  exists (Name name |
    name.getId() = "setattr" and
    call.getFunc() = name and
    call.getArg(0) = obj and
    call.getArg(1) = key and
    call.getArg(2) = val
  ) or

  //
  // Case 2: Calls to `obj.__setattr__(key, val)`
  //
  exists (AttrRead attrAccess, DataFlow::Node objNode |
    attrAccess.accesses(objNode, "__setattr__") and
    call.getFunc() = attrAccess.asExpr() and
    call.getArg(0) = key and
    call.getArg(1) = val and
    objNode.asExpr() = obj
  ) or

  //
  // Case 3: Calls to `object.__setattr__(obj, key, val)`
  //
  exists (AttrRead attrAccess, Variable variable |
    variable.getId() = "object" and
    attrAccess.getObject().asCfgNode() = variable.getAUse() and
    attrAccess.mayHaveAttributeName("__setattr__") and
    call.getFunc() = attrAccess.asExpr() and
    call.getArg(0) = obj and
    call.getArg(1) = key and
    call.getArg(2) = val
  ) or

  //
  // Case 4: External library calls whose name contains "setattr" or "set"
  //
  exists (Name funcName |
    (
      funcName.getId().matches("%setattr%") or
      funcName.getId().matches("%set%")
    ) and
    call.getFunc() = funcName and

    // We don't assume fixed argument positions for library calls,
    // so we check that obj, key, and val all appear somewhere in the arguments.
    call.getAnArg() = obj and
    call.getAnArg() = key and
    call.getAnArg() = val
  )
}

}