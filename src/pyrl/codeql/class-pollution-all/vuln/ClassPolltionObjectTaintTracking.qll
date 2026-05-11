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
import shared.sources.library::ClassPollutionLibrarySource
import shared.GetOp::ClassPollutionGetOp
import shared.SetOp::ClassPollutionSetOp
import shared.Debug::Debugging

module ClassPolltionObjectTaintTracking {

/**
 * @description
 * ----------------------
 * A FlowState to indicate whether the data is used as a key or object in getItem/getAttr operation.
 */
abstract class FlowState extends string {
  bindingset[this]
  
  FlowState() { any() }
}

class SetFlowState extends FlowState {
  SetOperationType setOperationType;
  SetPositionType setPositionType;
  ValueType valueType;

  SetFlowState() { this = "Set@" + setOperationType + "-" + setPositionType + "-" + valueType }

  string toString() {
    result = "Set@" + setOperationType + "-" + setPositionType + "-" + valueType
  }

  SetOperationType getSetOperationType() {
    result = setOperationType
  }

  SetPositionType getSetPositionType() {
    result = setPositionType
  }

  ValueType getValueType() {
    result = valueType
  }
}

class SetOperationType extends string {
  SetOperationType() { 
    this = "None" or
    this = "SetItem" or
    this = "SetAttr" or 
    this = "Unknown"
  }
}

class SetPositionType extends string {
  SetPositionType() { 
    this = "Object" or
    this = "Key" or
    this = "Value"
  }
}


class ValueType extends string {
  ValueType() { 
    this = "Object" or
    this = "Unknown"
  }
}

module TrackingClassPollutionKeyToAssignmentConfiguration implements DataFlow::StateConfigSig {
  class FlowState = SetFlowState;

  predicate isSource(DataFlow::Node source, FlowState state) {
    isLibrarySource(source) and
    state.(SetFlowState).getValueType() = "Unknown"
  }

  predicate isSink(DataFlow::Node sink, FlowState state) {
    (
      isSetItemExpr(_, sink.asExpr(), _, _) and
      state.(SetFlowState).getSetOperationType() = "SetItem" and
      state.(SetFlowState).getSetPositionType() = "Key"
    ) or
    (
      isSetAttrExpr(_, sink.asExpr(), _, _) and
      state.(SetFlowState).getSetOperationType() = "SetAttr" and
      state.(SetFlowState).getSetPositionType() = "Key" 
    ) or
    (
      isSetItemExpr(sink.asExpr(), _, _, _) and
      state.(SetFlowState).getSetOperationType() = "SetItem" and
      state.(SetFlowState).getSetPositionType() = "Object" and
      state.(SetFlowState).getValueType() = "Object"
    ) or
    (
      isSetAttrExpr(sink.asExpr(), _, _, _) and
      state.(SetFlowState).getSetOperationType() = "SetAttr" and
      state.(SetFlowState).getSetPositionType() = "Object" and
      state.(SetFlowState).getValueType() = "Object"
    ) or
    (
      isSetItemExpr(_, _, sink.asExpr(), _) and
      state.(SetFlowState).getSetOperationType() = "SetItem" and
      state.(SetFlowState).getSetPositionType() = "Value"
    ) or
    (
      isSetAttrExpr(_, _, sink.asExpr(), _) and
      state.(SetFlowState).getSetOperationType() = "SetAttr" and
      state.(SetFlowState).getSetPositionType() = "Value"
    )  
  }

  predicate isAdditionalFlowStep(DataFlow::Node fromNode, FlowState fromState, DataFlow::Node toNode, FlowState toState) {
    generalDataFlowStep(fromNode, fromState, toNode, toState)
    or
    generalTaintFlowStep(fromNode, fromState, toNode, toState)
    or 
    objectTaintFlowStep(fromNode, fromState, toNode, toState) 
  }
}

predicate objectTaintFlowStep(DataFlow::Node fromNode, FlowState fromState, DataFlow::Node toNode, FlowState toState) {
  ( 
    (
      additionalFlowStepThroughCustomLibHoldPrototypeObject(fromNode, toNode) or
      additionalFlowStepGetAttrReverse(fromNode, toNode)
    ) 
    and
    toState.(SetFlowState).getValueType() = "Object"
  )
  // (
  //   (
  //     additionalFlowStepGetItemReverse(fromNode, toNode) or
  //     additionalFlowStepThroughCustomLibHoldPrototypeObject(fromNode, toNode)
  //   ) and
  //   toState.(SetFlowState).getValueType() = "Object"
  // ) 
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

module TrackingClassPollutionKeyToAssignmentFlow = TaintTracking::GlobalWithState<TrackingClassPollutionKeyToAssignmentConfiguration>;
module Flow = TrackingClassPollutionKeyToAssignmentFlow; // For shortening the name


predicate isClassPollutedAssignmentThroughItemSettingStrict(Flow::PathNode setItemObj, Flow::PathNode setItemKey, Flow::PathNode sourceParamToObj, Flow::PathNode sourceParamToKey, Flow::PathNode setItemVal, Flow::PathNode sourceParamToVal) {
  isSetItemExpr(setItemObj.getNode().asExpr(), setItemKey.getNode().asExpr(), setItemVal.getNode().asExpr(), _) and
  (
    isSameFunctionParam(sourceParamToObj.getNode(), sourceParamToKey.getNode()) and
    isSameFunctionParam(sourceParamToObj.getNode(), sourceParamToVal.getNode())
  ) and
  (
    TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceParamToKey, setItemKey) and
    setItemKey.getState().(SetFlowState).getSetOperationType() = "SetItem" and
    setItemKey.getState().(SetFlowState).getSetPositionType() = "Key"
  ) and
  (
    TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceParamToObj, setItemObj) and
    setItemObj.getState().(SetFlowState).getSetOperationType() = "SetItem" and
    setItemObj.getState().(SetFlowState).getSetPositionType() = "Object"
  )
  and
  (
    TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceParamToVal, setItemVal) and
    setItemVal.getState().(SetFlowState).getSetOperationType() = "SetItem" and
    setItemVal.getState().(SetFlowState).getSetPositionType() = "Value"
  )
}

predicate debug(Flow::PathNode setAttrParamObj, Flow::PathNode setAttrObj){
  TrackingClassPollutionKeyToAssignmentFlow::flowPath(setAttrParamObj, setAttrObj) and
  setAttrObj.getState().(SetFlowState).getSetOperationType() = "SetAttr" and
  setAttrObj.getState().(SetFlowState).getSetPositionType() = "Value"
}

predicate isClassPollutedAssignmentThroughAttrSettingStrict(Flow::PathNode setAttrObj, Flow::PathNode setAttrKey, Flow::PathNode sourceParamToObj, Flow::PathNode sourceParamToKey, Flow::PathNode setAttrVal, Flow::PathNode sourceParamToVal) {
  isSetAttrExpr(setAttrObj.getNode().asExpr(), setAttrKey.getNode().asExpr(), setAttrVal.getNode().asExpr(), _) and
  (
    isSameFunctionParam(sourceParamToObj.getNode(), sourceParamToKey.getNode()) and
    isSameFunctionParam(sourceParamToObj.getNode(), sourceParamToVal.getNode())
  ) and
  (
    TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceParamToKey, setAttrKey) and
    setAttrKey.getState().(SetFlowState).getSetOperationType() = "SetAttr" and
    setAttrKey.getState().(SetFlowState).getSetPositionType() = "Key"
  ) and
  (
    TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceParamToObj, setAttrObj) and
    setAttrObj.getState().(SetFlowState).getSetOperationType() = "SetAttr" and
    setAttrObj.getState().(SetFlowState).getSetPositionType() = "Object"
  )
  and
  (
    TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceParamToVal, setAttrVal) and
    setAttrVal.getState().(SetFlowState).getSetOperationType() = "SetAttr" and
    setAttrVal.getState().(SetFlowState).getSetPositionType() = "Value"
  )
}


predicate isClassPollutedAssignment(DataFlow::Node sourceParamKeyNode, DataFlow::Node sourceParamObjNode, DataFlow::Node setOpKeyNode, DataFlow::Node setOpObjNode, string vulnType) {
  exists( Flow::PathNode sourceParamKeyPathNode, Flow::PathNode sourceParamObjPathNode, Flow::PathNode setOpKeyPathNode, Flow::PathNode setOpObjPathNode |
    sourceParamKeyPathNode.getNode() = sourceParamKeyNode and
    sourceParamObjPathNode.getNode() = sourceParamObjNode and
    setOpKeyPathNode.getNode() = setOpKeyNode and
    setOpObjPathNode.getNode() = setOpObjNode and
    ((
      isClassPollutedAssignmentThroughAttrSettingStrict(setOpObjPathNode, setOpKeyPathNode, sourceParamObjPathNode, sourceParamKeyPathNode, _, _) and
      vulnType = "SetAttr"
    ) or
    (
      isClassPollutedAssignmentThroughItemSettingStrict(setOpObjPathNode, setOpKeyPathNode, sourceParamObjPathNode, sourceParamKeyPathNode, _, _) and
      vulnType = "SetItem"
    ))
  )
}

}