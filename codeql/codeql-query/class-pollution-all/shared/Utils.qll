import python 
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking

module ClassPolltionUtils {
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
      TaintTracking::localTaint(sourceNode, sinkNode)
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
    // This only holds the expression-level equality, not the value-level equality.
    // E.g., hasattr(obj, key)) and True
    exists ( Value val1 |
      expr1.pointsTo(val1) and 
      expr2.pointsTo(val1)
    ) or 
    (
      expr1 instanceof Name and
      expr2 instanceof Name and
      expr1.(Name).getId() = expr2.(Name).getId()
    )
  }
  
  /**
   * Predicate to check if a call expression is an external library call.
   */
  predicate isBuiltinFuncCall(Call call) {
    exists(CallableValue cv |
      cv.getACall().getNode() = call and
      cv.isBuiltin() 
    )
  }

  predicate hasSameLocalSource(DataFlow::Node source, DataFlow::Node sink) {
    source.getALocalSource() = sink.getALocalSource()
  }

}
