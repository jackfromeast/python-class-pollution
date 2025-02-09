import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.TaintTracking
import shared.AdditionalFlowStep::ClassPollutionAdditionalFlowStep
import shared.AdditionalFlowStepDeque::ClassPollutionAdditionalFlowStepDeque
import shared.AdditionalFlowStepNamedtuple::ClassPollutionAdditionalFlowStepNamedtuple
import vuln.ClassPollutingFuncLib::ClassPollutionAssignment

module ClassPollutionTaintPropDependencyModel {

module TrackingParamToRetConfig implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
    exists(Parameter param |
      (param instanceof Name and source.asExpr() = param) or
      (param instanceof Tuple and source.asExpr() = param.(Tuple).getAnElt())
    )
  }

  predicate isSink(DataFlow::Node sink) {
    exists( Return ret | 
      ret.getValue().getAFlowNode() = sink.asCfgNode()
    )
  }

  predicate isAdditionalFlowStep(DataFlow::Node fromNode, DataFlow::Node toNode) {
    additionalFlowStepThroughNamedtuple(fromNode, toNode) or
    additionalFlowStepThroughDequeAppendPop(fromNode, toNode) or
    additionalFlowStepGetAttr(fromNode, toNode) or
    additionalFlowStepGetItem(fromNode, toNode)
  }
}

module TrackingParamToRetFlow = TaintTracking::Global<TrackingParamToRetConfig>;

/**
 * @description
 * Find the callable (method, function) whose return value is impacted by its arguments.
 * 
 * @note
 * This predicate favors the precision over the completeness.
 * 
 * @example
 * def func(path):
 *   x = path.split('/')
 *   return x
 * 
 */
predicate isClassPollutionTaintPropAPI(Function func, Parameter param, Return ret) {
  exists ( DataFlow::Node paramNode, DataFlow::Node retNode |
    TrackingParamToRetFlow::flow(paramNode, retNode) and
    paramNode.getScope() = retNode.getScope() and
    paramNode.asExpr() = param and
    retNode.asExpr() = ret.getValue()
  ) and
  (
    func.getAnArg() = param and
    ret.getScope() = func
  )
}

}