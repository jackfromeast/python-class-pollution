import python 
import semmle.python.dataflow.new.DataFlow

/**
 * Predicate to check if a function is a callee of another function.
 */
predicate hasCallEdgeOneJump(Function caller, Function callee) {
  exists(CallNode callExpr | 
    callExpr.getScope() = caller and
    callExpr.getFunction().refersTo(callee.getFunctionObject())
  )
}

/**
 * Predicate to determine if there is a dataflow path between two expressions.
 */
predicate hasDataFlowExpr(Expr source, Expr sink) {
  exists(DataFlow::Node sourceNode, DataFlow::Node sinkNode |
    sourceNode.asExpr() = source and
    sinkNode.asExpr() = sink and
    DataFlow::localFlow(sourceNode, sinkNode)
  )
}

/**
 * @description
 * ----------------------
 * Check if a call expression is within a loop.
 */
predicate isWithinLoop(Call call) {
  exists(For forStmt |
    forStmt.getBody().contains(call) 
  ) or
  exists(While whileStmt |
    whileStmt.getBody().contains(call)
  )
}

/**
 * @description
 * ----------------------
 * Check if a function call is recursive (direct or indirect).
 */
predicate isRecursiveFunc(Function func) {
  exists(Function callee |
    hasCallEdgeOneJump(func, callee) and
    callee.getFunctionObject() = func.getFunctionObject()
  )
}


/**
 * Predicate to check if two expressions refer to the same variable.
 */
predicate refersToSameVariable(Expr expr1, Expr expr2) {
  expr1 = expr2
  or
  (
    expr1 instanceof Name and
    expr2 instanceof Name and
    expr1.(Name).getId() = expr2.(Name).getId()
  )
}
