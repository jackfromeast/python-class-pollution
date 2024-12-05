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
 */
predicate isGetItemCall(Expr obj, Expr key, Call call) {
  exists(MethodCallNode callNode |
    callNode.asExpr() = call and
    callNode.getMethodName() = "get" and
    callNode.getObject().asExpr() = obj and
    call.getArg(0) = key
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
 * Check if the expression represents a getAttr operation like `getattr(obj, key)`.
 * 
 */
predicate isGetattrCall(Expr obj, Expr key, Call call) {
  exists (
    Name name|
    name.getId() = "getattr" and
    call.getFunc() = name and
    call.getArg(0) = obj and
    call.getArg(1) = key
  )
}

}