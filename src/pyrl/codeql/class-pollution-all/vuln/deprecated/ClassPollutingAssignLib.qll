import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.TaintTracking
import vuln.SmartGettingFuncLib::ClassPollutionSmartGetting
import vuln.SmartSettingFuncLib::ClassPollutionSmartSetting
import shared.Utils::ClassPolltionUtils
import shared.flowsteps.AdditionalFlowStep::ClassPollutionAdditionalFlowStep
import shared.flowsteps.AdditionalFlowStepDeque::ClassPollutionAdditionalFlowStepDeque
import shared.flowsteps.AdditionalFlowStepNamedtuple::ClassPollutionAdditionalFlowStepNamedtuple
import shared.flowsteps.AdditionalFlowStepCustom::ClassPollutionAdditionalFlowStepCustom
import shared.types.EnumeratedKeyNames
import shared.types.EnumeratedObjects
import shared.types.SplitObjects
import shared.types.SplitKeyNames
import shared.GetOp::ClassPollutionGetOp
import shared.SetOp::ClassPollutionSetOp
import shared.Debug::Debugging

module ClassPollutionAssignment {

/**
 * @description
 * ----------------------
 * A FlowState to indicate whether the data is used as a key or object in getItem/getAttr operation.
 */
abstract class FlowState extends string {
  bindingset[this]
  FlowState() { any() }
}

class GetOperationType extends string {
  GetOperationType() { 
    this = "None" or
    this = "GetItem" or
    this = "GetAttr" or
    this = "GetBoth" 
  }
}

class SetOperationType extends string {
  SetOperationType() { 
    this = "None" or
    this = "SetItem" or
    this = "SetAttr" or
    this = "SetBoth" 
  }
}

class PrototypeObjectFlowState extends ClassPollutionAssignment::FlowState {
  GetOperationType getOperationType; 
  SetOperationType setOperationType;

  PrototypeObjectFlowState() { this = "PrototypeObject" }

  string toString() {
    result = "Base Object at" + setOperationType + " through " + getOperationType
  }
}

class EnumeratedKeyFlowState extends ClassPollutionAssignment::FlowState {
  EnumeratedKeyFlowState() { this = "EnumeratedKey" }
}

class InitFuncParamterFlowState extends ClassPollutionAssignment::FlowState {
  InitFuncParamterFlowState() { this = "InitFuncParamter" }
}

class PrototypeObjectThroughGetItemFlowState extends ClassPollutionAssignment::FlowState {
  PrototypeObjectThroughGetItemFlowState() { this = "PrototypeObjectThroughGetItem" }
}

class PrototypeObjectThroughGetAttrFlowState extends ClassPollutionAssignment::FlowState {
  PrototypeObjectThroughGetAttrFlowState() { this = "PrototypeObjectThroughGetAttr" }
}

class UsedAsBaseObjectInSetItemFlowState extends ClassPollutionAssignment::FlowState {
  UsedAsBaseObjectInSetItemFlowState() { this = "UsedAsBaseObjectInSetItem" }
}

class UsedAsKeyInSetItemFlowState extends ClassPollutionAssignment::FlowState {
  UsedAsKeyInSetItemFlowState() { this = "UsedAsKeyInSetItem" }
}

class UsedAsBaseObjectInSetAttrFlowState extends ClassPollutionAssignment::FlowState {
  UsedAsBaseObjectInSetAttrFlowState() { this = "UsedAsBaseObjectInSetAttr" }
}

class UsedAsKeyInSetAttrFlowState extends ClassPollutionAssignment::FlowState {
  UsedAsKeyInSetAttrFlowState() { this = "UsedAsKeyInSetAttr" }
}


/**
 * @description
 * ----------------------
 * Tracks class pollution key names to dynamic attribute writes and dict item writes.
 * 
 * @example
 * ----------------------
  def merge(src, dst):
    for k, v in src.items():
      if hasattr(dst, '__getitem__'):
        if dst.get(k) and type(v) == dict:
          merge(v, dst.get(k))
        else:
          dst[k] = v
        elif hasattr(dst, k) and type(v) == dict:
          merge(v, getattr(dst, k))
        else:
          setattr(dst, k, v)

 * @condition
 * ----------------------
 * Dataflow 1: From the source key to the dynamic writing's target object.
 *             (TODO):
 *             k -> dst.get(k) -> dst
 *             k -> getattr(dst, k) -> dst
 * Dataflow 2: From the source key to the dynamic writing's target key.
 *             k -> k
 * Dataflow 3: From the source key to the value of dynamic writing.
 *             v -> v
 * 
 * This config follows the official CodeQL query for tracking prototype pollution in JavaScript.
 * https://github.com/github/codeql/blob/main/javascript/ql/src/Security/CWE-915/PrototypePollutingFunction.ql#L236
 */
module TrackingClassPollutionKeyToAssignmentConfiguration implements DataFlow::StateConfigSig {
  class FlowState = ClassPollutionAssignment::FlowState;

  predicate isSource(DataFlow::Node source, FlowState state) {
    isClassPollutedKeyNamesOrBaseObjects(source) 
  }

  predicate isSink(DataFlow::Node sink, FlowState state) {
    (isSetItemExpr(_, sink.asExpr(), _, _) and state instanceof UsedAsKeyInSetItemFlowState) or
    (isSetItemExpr(sink.asExpr(), _, _, _) and state instanceof UsedAsBaseObjectInSetItemFlowState) or
    (isSetattrCall(_, sink.asExpr(), _, _) and state instanceof UsedAsKeyInSetAttrFlowState) or
    (isSetattrCall(sink.asExpr(), _, _, _) and state instanceof UsedAsBaseObjectInSetAttrFlowState)
  }

  predicate isAdditionalFlowStep(DataFlow::Node fromNode, FlowState fromState, DataFlow::Node toNode, FlowState toState) {
    additionalFlowStepThroughNamedtuple(fromNode, toNode) or
    additionalFlowStepThroughDequeAppendPop(fromNode, toNode) or
    additionalFlowStepGetAttr(fromNode, toNode) or
    additionalFlowStepGetItem(fromNode, toNode) or
    (
      additionalFlowStepGetAttrReverse(fromNode, toNode) and
      (
        toState instanceof UsedAsBaseObjectInSetAttrFlowState or
        toState instanceof UsedAsBaseObjectInSetItemFlowState
      )
    ) or
    (
      additionalFlowStepGetItemReverse(fromNode, toNode) and
      (
        toState instanceof UsedAsBaseObjectInSetAttrFlowState or
        toState instanceof UsedAsBaseObjectInSetItemFlowState
      )
    ) or
    (
      additionalFlowStepThroughCustomLibAnyState(fromNode, toNode) and
      (
        toState instanceof UsedAsBaseObjectInSetAttrFlowState or
        toState instanceof UsedAsBaseObjectInSetItemFlowState
      )
    ) or

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
  }
}

predicate isAdditionalFlowStepThroughGetItem(DataFlow::Node source, DataFlow::Node target) {
  // Propagate taint on every getValue operation with the polluted key
  // key -> obj[key]
  exists( DataFlow::Node getItemExpr | 
    isGetItemOp(_, source.asExpr(), getItemExpr.asExpr()) and
    (
      DataFlow::localFlow(getItemExpr, target) or
      getItemExpr = target
    )
  ) or
  //  for k, v in src.items() -> k -> v
  exists(For forLoop, MethodCallNode call, Tuple tuple |
    forLoop.getIter() = call.asExpr() and
    (
      call.getMethodName() = "items" or
      call.getMethodName() = "enumerate"
    ) and
    tuple = forLoop.getTarget() and
    (
      tuple.getElt(0) = source.asExpr() and
      tuple.getElt(1) = target.asExpr()
    )
  ) or
  // Propagate taint on every getValue operation from polluted object
  // obj -> obj[key]
  exists( DataFlow::Node getItemExpr | 
    isGetItemOp(source.asExpr(), _, getItemExpr.asExpr()) and
    (
      DataFlow::localFlow(getItemExpr, target) or
      getItemExpr = target
    )
  )
}

predicate isAdditionalFlowStepThroughGetAttr(DataFlow::Node source, DataFlow::Node target) {
  // Propagate taint on every getValue operation with the polluted key
  // key -> getattr(obj, key)
  exists( DataFlow::Node getattrCall |
    isGetAttrOp(_, source.asExpr(), getattrCall.asExpr()) and
    (
      DataFlow::localFlow(getattrCall, target) or
      getattrCall = target
    )
  ) or 
  // Propagate taint on every getValue operation from polluted object
  // obj -> getattr(obj, key)
  exists( DataFlow::Node getattrCall | 
    isGetAttrOp(source.asExpr(), _, getattrCall.asExpr()) and
    (
      DataFlow::localFlow(getattrCall, target) or
      getattrCall = target
    )
  )
}


module TrackingClassPollutionKeyToAssignmentFlow = TaintTracking::GlobalWithState<TrackingClassPollutionKeyToAssignmentConfiguration>;
module Flow = TrackingClassPollutionKeyToAssignmentFlow; // For shortening the name

/**
 * @description
 * Extension of `DataFlow::Node` to identify nodes that hold key names that are enumerated or from split method call.
 */
predicate isClassPollutedKeyNamesOrBaseObjects(DataFlow::Node key) {
  // restrictedByFunctionName(source, "update_item_attr") and
  (
    key instanceof EnumeratedKeyNames or
    key instanceof SplitKeyNames
  ) or
  (
    key instanceof EnumeratedObjects or
    key instanceof SplitObjects
  )
}

predicate debugTest(Flow::PathNode sourceKeyToKey, Flow::PathNode setItemKey) {
  TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceKeyToKey, setItemKey)
}

/**
 * @description
 * ----------------------
 * Holds if the assignment can overwrite the dunder attributes/items of the object.
 */
predicate isClassPollutedAssignmentThroughItemSetting(Flow::PathNode setItemObj, Flow::PathNode setItemKey, Flow::PathNode sourceKeyToObj, Flow::PathNode sourceKeyToKey) {
  isSetItemExpr(setItemObj.getNode().asExpr(), setItemKey.getNode().asExpr(), _, _) and
  (
    isClassPollutedKeyNamesOrBaseObjects(sourceKeyToObj.getNode()) and
    isClassPollutedKeyNamesOrBaseObjects(sourceKeyToKey.getNode()) and
    sourceKeyToObj.getNode() = sourceKeyToKey.getNode()
  ) and
  (
    TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceKeyToKey, setItemKey) and
    setItemKey.getState() instanceof UsedAsKeyInSetItemFlowState
  ) and 
  (
    TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceKeyToObj, setItemObj) and
    setItemObj.getState() instanceof UsedAsBaseObjectInSetItemFlowState
  )
}

predicate isClassPollutedAssignmentThroughAttrSetting(Flow::PathNode setAttrObj, Flow::PathNode setAttrKey, Flow::PathNode sourceKeyToObj, Flow::PathNode sourceKeyToKey) {
  isSetattrCall(setAttrObj.getNode().asExpr(), setAttrKey.getNode().asExpr(), _, _) and
  (
    isClassPollutedKeyNamesOrBaseObjects(sourceKeyToObj.getNode()) and
    isClassPollutedKeyNamesOrBaseObjects(sourceKeyToKey.getNode()) and
    sourceKeyToObj.getNode() = sourceKeyToKey.getNode()
  ) and
  (
    TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceKeyToKey, setAttrKey) and
    setAttrKey.getState() instanceof UsedAsKeyInSetAttrFlowState
  ) and 
  (
    TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceKeyToObj, setAttrObj) and
    setAttrObj.getState() instanceof UsedAsBaseObjectInSetAttrFlowState
  )
}

predicate isClassPollutedAssignment(DataFlow::Node classPollutingKey) {
  exists( Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode sourceC, Flow::PathNode sourceD |
    isClassPollutedAssignmentThroughItemSetting(_, _, sourceA, sourceB) and
    isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD) and
    sourceA.getNode() = sourceC.getNode() and
    classPollutingKey = sourceA.getNode()
  )
}
}