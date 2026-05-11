import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.TaintTracking
import semmle.python.ApiGraphs
import shared.Debug::Debugging

/**
 * @description
 * ----------------------
 * Represents a node that generated from `operator.itemgetter(name)`.
 * 
 * @example
 * ----------------------
 * operator.itemgetter(name)(obj)
 * 
 * @note
 * ----------------------
 * This only tracks the item getter in function scope.
 */
class OperatorItemGetter extends DataFlow::Node {
  DataFlow::Node attrName;

  OperatorItemGetter() {
    exists (API::CallNode callNode, DataFlow::Node immediateDFNode|
      API::moduleImport("operator").getMember("itemgetter").getACall() = callNode and
      callNode.getArg(0) = attrName and
      callNode.asExpr() = immediateDFNode.asExpr() and
      (
        immediateDFNode.asExpr() = this.asExpr() or
        DataFlow::localFlow(immediateDFNode, this)
      )
    )
  }

  DataFlow::Node getAttrName() {
    result = attrName
  }
}