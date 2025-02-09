import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.TaintTracking
import shared.AdditionalFlowStep::ClassPollutionAdditionalFlowStep
import shared.AdditionalFlowStepDeque::ClassPollutionAdditionalFlowStepDeque
import shared.AdditionalFlowStepNamedtuple::ClassPollutionAdditionalFlowStepNamedtuple
import vuln.ClassPollutingFuncLib::ClassPollutionAssignment

module ClassPollutionSourceDependencyModel {

module TrackingParamToPollutionSourceConfig implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
    exists(Parameter param |
      (param instanceof Name and source.asExpr() = param) or
      (param instanceof Tuple and source.asExpr() = param.(Tuple).getAnElt())
    )
  }

  predicate isSink(DataFlow::Node sink) {
    isSplitResultImmediate(sink) 
  }

  predicate isAdditionalFlowStep(DataFlow::Node fromNode, DataFlow::Node toNode) {
    additionalFlowStepThroughNamedtuple(fromNode, toNode) or
    additionalFlowStepThroughDequeAppendPop(fromNode, toNode) or
    additionalFlowStepGetAttr(fromNode, toNode) or
    additionalFlowStepGetItem(fromNode, toNode)
  }
}

module TrackingPollutionSourceToRetConfig implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
    isSplitResultImmediate(source) 
  }

  predicate isSink(DataFlow::Node sink) {
    exists( Return ret | 
      ret.getValue().getAFlowNode() = sink.asCfgNode()
    )
  }
}

module TrackingParamToPollutionSourceFlow = TaintTracking::Global<TrackingParamToPollutionSourceConfig>;
module TrackingPollutionSourceToRetFlow = DataFlow::Global<TrackingPollutionSourceToRetConfig>;

/**
 * @description
 * Find the callable (method, function) whose return value should be considered as a class pollution source.
 * More specifically, it should holds the following facts:
 * 1/ The return value is ClassPollutedKeyNames and
 * 2/ Taint flow between the API arguments and its return value.
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
predicate isClassPollutionSourceAPI(Function func, Parameter param, Return ret) {
  exists ( DataFlow::Node paramNode, DataFlow::Node retNode, DataFlow::Node sourceNode |
    TrackingParamToPollutionSourceFlow::flow(paramNode, sourceNode) and
    TrackingPollutionSourceToRetFlow::flow(sourceNode, retNode) and 
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