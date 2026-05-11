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

module InvokeAITaintTracking {

predicate isAdditionalSource(DataFlow::Node source) {
  exists(ControlFlowNode call, Function func |
    func.getADecorator().getAFlowNode() = call and
    call = API::moduleImport("fastapi").getMember("routing").getMember("APIRouter").getASubclass*().getReturn().getMember(_).getACall().asCfgNode() and
    func.getAnArg() = source.asExpr()
  )
}

predicate isAdditionalFlowStepHeuristicImport(DataFlow::Node fromNode, DataFlow::Node toNode) {
  exists(MethodCallNode callNode, Function func |
    callNode.getMethodName() = "heuristic_import" and
    func.getName() = "heuristic_import" and
    (
      exists(int i | callNode.getArg(i).asExpr() = fromNode.asExpr() and func.getArg(i) = toNode.asExpr())
    or
      // This predicate is not precise
      exists(int i | callNode.getArgByName(_).asExpr() = fromNode.asExpr() and func.getArg(i) = toNode.asExpr())
    )
  )
}

module TrackingModelURLToFileWriteConfiguration implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
    isAdditionalSource(source) and
    restrictedByFunctionName(source, "install_model")
  }

  predicate isSink(DataFlow::Node sink) {
    any()
  }

  predicate isAdditionalFlowStep(DataFlow::Node fromNode, DataFlow::Node toNode) {
    generalDataFlowStep(fromNode, _, toNode, _)
    or
    generalTaintFlowStep(fromNode, _, toNode, _)
    or
    isAdditionalFlowStepHeuristicImport(fromNode, toNode)
  }
}

module TrackingPrototypeObjectToAssignmentConfiguration implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
   source instanceof PossibleGetOpNode
  }

  predicate isSink(DataFlow::Node sink) {
    isSetItemExpr(sink.asExpr(), _, _, _) 
    or
    isSetAttrExpr(sink.asExpr(), _, _, _)
  }

  predicate isAdditionalFlowStep(DataFlow::Node fromNode, DataFlow::Node toNode) {
    generalDataFlowStepNoState(fromNode, toNode)
  }
}

/**
 * @description
 * ----------------------
 * Flow steps in generalDataFlowStep is precise data flow tracking step.
 */
predicate generalDataFlowStepNoState(DataFlow::Node fromNode, DataFlow::Node toNode) {
  additionalFlowStepThroughNamedtuple(fromNode, toNode) or
  additionalFlowStepThroughDequeAppendPop(fromNode, toNode) or
  additionalFlowStepThroughReduce(fromNode, toNode) or
  additionalFlowStepThroughCustomLibAnyState(fromNode, toNode) or
  additionalFlowStepGetItemDefault(fromNode, toNode)
}

/**
 * @description
 * ----------------------
 * Flow steps in generalDataFlowStep is precise data flow tracking step.
 */
predicate generalDataFlowStep(DataFlow::Node fromNode, FlowState fromState, DataFlow::Node toNode, FlowState toState) {
  generalDataFlowStepNoState(fromNode, toNode) and
  toState = fromState
}

predicate generalTaintFlowStep(DataFlow::Node fromNode, FlowState fromState, DataFlow::Node toNode, FlowState toState) {
  (
    (
      additionalFlowStepGetAttr(fromNode, toNode) or
      additionalFlowStepGetItem(fromNode, toNode) or
      // source -> filter(none, source)
      exists(Call call, DataFlow::Node immediateNode, Name name |
        name.getId() = "filter" and
        call.getFunc() = name and 
        call.getArg(1) = immediateNode.asExpr() and
        (
          immediateNode = fromNode or
          DataFlow::localFlow(fromNode, immediateNode)
        ) and
        (
          call = toNode.asExpr() or
          hasDataFlowExpr(call, toNode.asExpr())
        )
      ) or
      // source -> [key for key in source]
      exists(Comp comp, DataFlow::Node immediateNode|
        comp.getIterable() = fromNode.asExpr() and
        immediateNode.asExpr() = comp and
        DataFlow::localFlow(immediateNode, toNode)
      )
    ) and
    toState = fromState
  )
}

module TrackingModelURLToFileWriteFlow = TaintTracking::Global<TrackingModelURLToFileWriteConfiguration>;
module Flow = TrackingModelURLToFileWriteFlow; // For shortening the name

predicate selectSink(DataFlow::Node flowNode) {
  Flow::flow(_, flowNode)
}

predicate selectCallNode(API::CallNode callNode) {
  any()
}

}