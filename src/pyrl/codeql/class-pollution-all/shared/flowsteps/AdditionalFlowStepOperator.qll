import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import shared.Utils::ClassPolltionUtils
import shared.GetOp::ClassPollutionGetOp


module ClassPollutionAdditionalFlowStepOperator {

/**
 * @description
 * ----------------------
 * 
  from operator import attrgetter
  target = attrgetter(attr[:-1])(obj)
 */
predicate additionalFlowStepThroughGetAttrOperator(DataFlow::Node fromNode, DataFlow::Node toNode) {
  exists (CallCfgNode callNode, AttrGetterOp getOperator| 
    DataFlow::localFlow(getOperator, callNode.getFunction()) and
    getOperator.getKey() = fromNode and
    toNode = callNode and 
    getOperator.getOpType() = "getAttr"
  )
}

predicate additionalFlowStepThroughGetItemOperator(DataFlow::Node fromNode, DataFlow::Node toNode) {
  exists (CallCfgNode callNode, AttrGetterOp getOperator| 
    DataFlow::localFlow(getOperator, callNode.getFunction()) and
    getOperator.getKey() = fromNode and
    toNode = callNode and
    getOperator.getOpType() = "getItem"
  )
}

class AttrGetterOp extends DataFlow::Node {
  DataFlow::Node key;
  string getOpType;

  AttrGetterOp() {
    exists ( Call getterOp |
      (
        API::moduleImport("operator").getMember("attrgetter").getACall().asExpr() = getterOp and
        getOpType = "getAttr" and
        getterOp.getArg(0) = key.asExpr() and
        this.asExpr() = getterOp
      ) or
      (
        API::moduleImport("operator").getMember("itemgetter").getACall().asExpr() = getterOp and
        getOpType = "getItem" and
        getterOp.getArg(0) = key.asExpr() and
        this.asExpr() = getterOp
      )
    )
  }

  DataFlow::Node getKey() {
    result = key
  }

  string getOpType() {
    result = getOpType
  }
}

}