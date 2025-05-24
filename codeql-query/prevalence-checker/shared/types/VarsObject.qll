import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.TaintTracking
import semmle.python.ApiGraphs
import shared.Debug::Debugging

/**
 * @description
 * ----------------------
 * Represents a node that generated `vars(obj) ` call of an object.
 * 
 * @example
 * ----------------------
 * for attr in attrs[:-1]:
 *   target = vars(obj).get(attr)
 * 
 * or target = vars(obj)[attr]
 * 
 * @note
 * ----------------------
 * This only tracks the `vars(obj) ` of an object in function scope.
 */
class VarsObject extends DataFlow::Node {
  DataFlow::Node baseObj;

  VarsObject() {
    exists (API::CallNode callNode, DataFlow::Node immediateDFNode|
      API::builtin("vars").getACall() = callNode and
      callNode.getArg(0) = baseObj and
      callNode.asExpr() = immediateDFNode.asExpr() and
      (
        immediateDFNode.asExpr() = this.asExpr() or
        DataFlow::localFlow(immediateDFNode, this)
      )
    )
  }

  DataFlow::Node getBaseObject() {
    result = baseObj
  }
}

predicate getVarsFunc(API::CallNode callNode) {
  API::builtin("vars").getACall() = callNode
}
