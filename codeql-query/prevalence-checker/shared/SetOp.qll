import python
import shared.Utils::ClassPolltionUtils
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import shared.types.DunderDictObject


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
  isSetitemDunderCall(obj, key, val, call) or

  // Case 2: Calls to `obj.update({key: val})`
  // exists (MethodCallNode callNode, DataFlow::Node dictNode |
  //   callNode.asExpr() = call and
  //   callNode.getMethodName() = "update" and
  //   callNode.getObject().asExpr() = obj and
  //   callNode.getArg(0) = dictNode and
    
  //   // key and value should has a dataflow path to the dictionary
  // ) or

  // Case 3: Calls to `obj.setdefault(key, val)`
  isSetitemSetDefaultCall(obj, key, val, call)

  // Case 4: External or library calls: e.g., library.setSomething(obj, key, val)
  // exists (Name funcName |
  //   (
  //     funcName.getId().matches("%set\\_%") or
  //     funcName.getId().matches("%put\\_%") or
  //     funcName.getId().matches("%update\\_%")
  //   ) and
  //   not isBuiltinFuncCall(call) and
  //   call.getFunc() = funcName and
  //   // We don't assume fixed argument ordering for library calls,
  //   // so we check that obj, key, and val appear among the arguments.
  //   call.getAnArg() = obj and
  //   call.getAnArg() = key and
  //   call.getAnArg() = val
  // )
}

/**
 * Calls to `dict.__setitem__(key, val)`
 */
predicate isSetitemDunderCall(Expr obj, Expr key, Expr val, Call call) {
  exists (AttrRead attrAccess, DataFlow::Node objNode |
    attrAccess.accesses(objNode, "__setitem__") and
    call.getFunc() = attrAccess.asExpr() and
    call.getArg(0) = key and
    call.getArg(1) = val and
    objNode.asExpr() = obj
  )
}

/**
 * Calls to `dict.update(key=val)`
 */
predicate isSetitemUpdateCall(Expr obj, Call call) {
  exists (MethodCallNode callNode |
    callNode.asExpr() = call and
    callNode.getMethodName() = "update" and
    callNode.getObject().asExpr() = obj
  ) 
}

/**
 * Calls to `dict.setdefault(key, val)`
 */
predicate isSetitemSetDefaultCall(Expr obj, Expr key, Expr val, Call call) {
  exists (MethodCallNode callNode |
    callNode.asExpr() = call and
    callNode.getMethodName() = "setdefault" and
    callNode.getObject().asExpr() = obj and
    callNode.getArg(0).asExpr() = key and
    callNode.getArg(1).asExpr() = val
  ) 
}

predicate isSetItemExpr(Expr obj, Expr key, Expr val, ControlFlowNode setItemNode) {
  exists (Call call |
    isSetItemCall(obj, key, val, call) and 
    call.getAFlowNode() = setItemNode
  )
  or 
  exists (Assign assign |
    isSubscriptAssignment(obj, key, val, assign) and
    assign.getATarget().getAFlowNode() = setItemNode
  )
}

predicate isSetAttrExpr(Expr obj, Expr key, Expr val, ControlFlowNode setattrNode) {
  exists (Call call |
    isSetattrCall(obj, key, val, call) and 
    call.getAFlowNode() = setattrNode
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
  // exists (Name name |
  //   name.getId() = "setattr" and
  //   call.getFunc() = name and
  //   call.getArg(0) = obj and
  //   call.getArg(1) = key and
  //   call.getArg(2) = val
  // ) or
  isSetattrBuiltinCall(obj, key, val, call) or

  //
  // Case 2: Calls to `obj.__setattr__(key, val)`
  //
  // exists (AttrRead attrAccess, DataFlow::Node objNode |
  //   attrAccess.accesses(objNode, "__setattr__") and
  //   call.getFunc() = attrAccess.asExpr() and
  //   call.getArg(0) = key and
  //   call.getArg(1) = val and
  //   objNode.asExpr() = obj
  // ) or
  isSetattrDunderCall(obj, key, val, call) or

  //
  // Case 3: Calls to `object.__setattr__(obj, key, val)`
  //
  // exists (AttrRead attrAccess, Variable variable |
  //   variable.getId() = "object" and
  //   attrAccess.getObject().asCfgNode() = variable.getAUse() and
  //   attrAccess.mayHaveAttributeName("__setattr__") and
  //   call.getFunc() = attrAccess.asExpr() and
  //   call.getArg(0) = obj and
  //   call.getArg(1) = key and
  //   call.getArg(2) = val
  // ) 
  isObjectSetattrDunderCall(obj, key, val, call)
}

/**
 * Calls to `setattr(obj, name, val)`
 */
predicate isSetattrBuiltinCall(Expr obj, Expr key, Expr val, Call call) {
  exists (Name name |
    name.getId() = "setattr" and
    call.getFunc() = name and
    call.getArg(0) = obj and
    call.getArg(1) = key and
    call.getArg(2) = val
  )
}

/**
 * Calls to `obj.__setattr__(name,val)`
 */
predicate isSetattrDunderCall(Expr obj, Expr key, Expr val, Call call) {
  exists (AttrRead attrAccess, DataFlow::Node objNode |
    attrAccess.accesses(objNode, "__setattr__") and
    call.getFunc() = attrAccess.asExpr() and
    call.getArg(0) = key and
    call.getArg(1) = val and
    objNode.asExpr() = obj
  )
}

/**
 * Calls to `object.__setattr__(obj, name, val)`
 */
predicate isObjectSetattrDunderCall(Expr obj, Expr key, Expr val, Call call) {
  exists (AttrRead attrAccess, Variable variable |
    variable.getId() = "object" and
    attrAccess.getObject().asCfgNode() = variable.getAUse() and
    attrAccess.mayHaveAttributeName("__setattr__") and
    call.getFunc() = attrAccess.asExpr() and
    call.getArg(0) = obj and
    call.getArg(1) = key and
    call.getArg(2) = val
  ) 
}

/**
 * @description
 * ----------------------
 * Check if the expression represents an assignment like `obj.__dict__[name] = val`.
 */
predicate isSetAttrThroughObjectDunderDictSubscript(Expr obj, Expr key, Expr val, Assign a) {
  exists ( DunderDictObject dunderDictObject |
    dunderDictObject.getBaseObject().asExpr() = obj and
    isSubscriptAssignment(dunderDictObject.asExpr(), key, val, a)
  )
}

/**
 * Calls to `operator.setitem(dict, key, val)`
 */
predicate isSetItemThroughOperator(Expr obj, Expr key, Expr val, Call call) {
  API::moduleImport("operator").getMember("setitem").getACall().asExpr() = call and
  call.getArg(0) = obj and
  call.getArg(1) = key and 
  call.getArg(2) = val 
}

/**
 * Calls to `operator.__setitem__(dict, key, val)`
 */
predicate isSetItemDunderThroughOperator(Expr obj, Expr key, Expr val, Call call) {
  API::moduleImport("operator").getMember("__setitem__").getACall().asExpr() = call and
  call.getArg(0) = obj and
  call.getArg(1) = key and 
  call.getArg(2) = val 
}

}