import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.TaintTracking
import semmle.python.ApiGraphs
import shared.Debug::Debugging

/**
 * @description
 * ----------------------
 * Represents a node that generated from `operator.attrgetter(name)`.
 * 
 * @example
 * ----------------------
 * operator.attrgetter(name)(obj)
 * 
 * @note
 * ----------------------
 * This only tracks the attribute getter in function scope.
 */
class OperatorAttrGetter extends DataFlow::Node {
  DataFlow::Node attrName;

  OperatorAttrGetter() {
    exists (API::CallNode callNode, DataFlow::Node immediateDFNode|
      API::moduleImport("operator").getMember("attrgetter").getACall() = callNode and
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