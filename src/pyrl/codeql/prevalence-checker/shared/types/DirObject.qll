import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.TaintTracking
import semmle.python.ApiGraphs
import shared.Debug::Debugging

/**
 * @description
 * ----------------------
 * Represents a node that generated `dir(obj) ` call of an object.
 * 
 * @example
 * ----------------------
 * attrs = dir(obj)
 * for attr in attrs:
 *   target = attr
 * 
 * @note
 * ----------------------
 * This only tracks the `dir(obj) ` of an object in function scope.
 */
class DirObject extends DataFlow::Node {
  DataFlow::Node baseObj;

  DirObject() {
    exists (API::CallNode callNode, DataFlow::Node immediateDFNode|
      API::builtin("dir").getACall() = callNode and
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

predicate getDirFunc(API::CallNode callNode) {
  API::builtin("dir").getACall() = callNode
}
