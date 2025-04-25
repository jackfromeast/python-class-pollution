import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.TaintTracking
import vuln.SmartSettingFuncLib::ClassPollutionSmartSetting
import shared.Utils::ClassPolltionUtils
import shared.flowsteps.AdditionalFlowStep::ClassPollutionAdditionalFlowStep
import shared.flowsteps.AdditionalFlowStepNamedtuple::ClassPollutionAdditionalFlowStepNamedtuple
import shared.flowsteps.AdditionalFlowStepDeque::ClassPollutionAdditionalFlowStepDeque
import shared.flowsteps.AdditionalFlowStepReduce::ClassPollutionAdditionalFlowStepReduce
import shared.flowsteps.AdditionalFlowStepCustom::ClassPollutionAdditionalFlowStepCustom
import shared.flowsteps.AdditionalFlowStepOperator::ClassPollutionAdditionalFlowStepOperator
import shared.types.EnumeratedKeyNames
import shared.types.EnumeratedObjects
import shared.types.PossibleGetOpNode
import shared.types.SplitObjects
import shared.types.SplitKeyNames
import shared.types.DunderDictObject
import shared.types.SelfReferringGetOp::SelfReferringGetOp
import shared.sources.remote::ClassPollutionRemoteSource
import shared.GetOp::ClassPollutionGetOp
import shared.SetOp::ClassPollutionSetOp
import shared.Debug::Debugging

module TrackingExternalInputToClassPollutionConfiguration implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
    isRemoteSource(source)  
  }

  /**
   * The same as the TrackingClassPollutionKeyToAssignmentConfiguration's isSource predicate.
   */
  predicate isSink(DataFlow::Node sink) {
    exists (Function func, Parameter param | 
      func.getAnArg() = param and
      sink.asExpr() = param
    )
  }

  predicate isAdditionalFlowStep(DataFlow::Node fromNode, DataFlow::Node toNode) {
    // TYPE1: General flow steps
    // From ANY FlowState to ANY FlowState
    generalDataFlowStepNoState(fromNode, toNode)
  }
}

module TrackingExternalInputToClassPollutionFlow = TaintTracking::Global<TrackingExternalInputToClassPollutionConfiguration>;

/**
 * @description
 * ----------------------
 * Flow steps in generalDataFlowStep is precise data flow tracking step.
 */
predicate generalDataFlowStepNoState(DataFlow::Node fromNode, DataFlow::Node toNode) {
  additionalFlowStepThroughNamedtuple(fromNode, toNode) or
  additionalFlowStepThroughDequeAppendPop(fromNode, toNode) or
  additionalFlowStepThroughReduce(fromNode, toNode) or
  additionalFlowStepThroughCustomLibAnyState(fromNode, toNode)
}
