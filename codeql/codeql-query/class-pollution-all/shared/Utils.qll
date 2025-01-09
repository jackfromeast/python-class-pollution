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
  predicate extendExprRefersTo(Expr expr1, Expr expr2) {
    // This only holds the expression-level equality, not the value-level equality.
    // Implemented at /codeql/python-all/2.2.0/semmle/python/pointsto/PointsTo.qll
    // Not working for the following cases from our observation:
    // 1. attr.name in target_obj[attr.name] = value and setattr(target_obj, attr.name, value)
    // 2. target_obj[x[-1]] = value and setattr(target_obj, x[-1], value)
    // exists ( Value val |
    //   expr1.pointsTo(val) and 
    //   expr2.pointsTo(val)
    // ) or 
    // target_obj[attr.name] = value and setattr(target_obj, attr.name, value)
    refersToAttribute(expr1.(Attribute), expr2.(Attribute)) or
    // target_obj[x[-1]] = value and setattr(target_obj, x[-1], value)
    refersToSubscript(expr1.(Subscript), expr2.(Subscript)) or 
    // target_obj[key] = value and setattr(target_obj, key, value)
    refersToName(expr1.(Name), expr2.(Name))
  }

  predicate refersToName(Name name1, Name name2) {
    exists ( DataFlow::Node node1, DataFlow::Node node2 |
      node1.asExpr() = name1 and
      node2.asExpr() = name2 and
      node1.getALocalSource() = node2.getALocalSource()
    )
  }

  predicate refersToAttribute(Attribute attr1, Attribute attr2) {
    exists ( DataFlow::Node base1, DataFlow::Node base2 |
      base1.asExpr() = attr1.getObject() and
      base2.asExpr() = attr2.getObject() and
      base1.getALocalSource() = base2.getALocalSource() and
      attr1.getName() = attr2.getName()
    )
  }

  predicate refersToSubscript(Subscript sub1, Subscript sub2) {
    exists ( DataFlow::Node base1, DataFlow::Node base2 |
      base1.asExpr() = sub1.getObject() and
      base2.asExpr() = sub2.getObject() and
      base1.getALocalSource() = base2.getALocalSource() and
      exists (Expr index1, Expr index2, Value val |
        sub1.getIndex() = index1 and
        sub2.getIndex() = index2 and
        index1.pointsTo(val) and
        index2.pointsTo(val)
      )
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
