import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.TaintTracking
import shared.SetOp::ClassPollutionSetOp
import shared.flowsteps.AdditionalFlowStep::ClassPollutionAdditionalFlowStep
import shared.flowsteps.AdditionalFlowStepDeque::ClassPollutionAdditionalFlowStepDeque
import shared.flowsteps.AdditionalFlowStepNamedtuple::ClassPollutionAdditionalFlowStepNamedtuple
import vuln.deprecated.ClassPollutingAssignLib::ClassPollutionAssignment

module ClassPollutionSinkDependencyModel {

abstract class FlowState extends string {
  bindingset[this]
  FlowState() { any() }
}

class UsedAsBaseObjectInSetItemFlowState extends ClassPollutionSinkDependencyModel::FlowState {
  UsedAsBaseObjectInSetItemFlowState() { this = "UsedAsBaseObjectInSetItem" }
}

class UsedAsKeyInSetItemFlowState extends ClassPollutionSinkDependencyModel::FlowState {
  UsedAsKeyInSetItemFlowState() { this = "UsedAsKeyInSetItem" }
}

class UsedAsBaseObjectInSetAttrFlowState extends ClassPollutionSinkDependencyModel::FlowState {
  UsedAsBaseObjectInSetAttrFlowState() { this = "UsedAsBaseObjectInSetAttr" }
}

class UsedAsKeyInSetAttrFlowState extends ClassPollutionSinkDependencyModel::FlowState {
  UsedAsKeyInSetAttrFlowState() { this = "UsedAsKeyInSetAttr" }
}

class UsedAsValueInSetAttrFlowState extends ClassPollutionSinkDependencyModel::FlowState {
  UsedAsValueInSetAttrFlowState() { this = "UsedAsValueInSetAttr" }
}

class UsedAsValueInSetItemFlowState extends ClassPollutionSinkDependencyModel::FlowState {
  UsedAsValueInSetItemFlowState() { this = "UsedAsValueInSetItem" }
}

/**
 * @description
 * This configuration is the same as the TrackingClassPollutionKeyToAssignmentConfiguration configuration.
 * However, the source is the parameter of the API.
 * 
 */
module TrackingParamToPollutionSinkConfig implements DataFlow::StateConfigSig {
  class FlowState = ClassPollutionSinkDependencyModel::FlowState;

  predicate isSource(DataFlow::Node source, FlowState state) {
    exists(Parameter param |
      (param instanceof Name and source.asExpr() = param) or
      (param instanceof Tuple and source.asExpr() = param.(Tuple).getAnElt())
    )
  }

  predicate isSink(DataFlow::Node sink, FlowState state) {
    (isSetItemExpr(_, _, sink.asExpr(), _) and state instanceof UsedAsValueInSetItemFlowState) or
    (isSetItemExpr(_, sink.asExpr(), _, _) and state instanceof UsedAsKeyInSetItemFlowState) or
    (isSetItemExpr(sink.asExpr(), _, _, _) and state instanceof UsedAsBaseObjectInSetItemFlowState) or
    (isSetattrCall(_, _, sink.asExpr(), _) and state instanceof UsedAsValueInSetAttrFlowState) or
    (isSetattrCall(_, sink.asExpr(), _, _) and state instanceof UsedAsKeyInSetAttrFlowState) or
    (isSetattrCall(sink.asExpr(), _, _, _) and state instanceof UsedAsBaseObjectInSetAttrFlowState)
  }

  predicate isAdditionalFlowStep(DataFlow::Node fromNode, DataFlow::Node toNode) {
    additionalFlowStepThroughNamedtuple(fromNode, toNode) or
    additionalFlowStepThroughDequeAppendPop(fromNode, toNode) or
    additionalFlowStepGetAttr(fromNode, toNode) or
    additionalFlowStepGetItem(fromNode, toNode)
  }
}

module TrackingParamToPollutionSinkFlow = TaintTracking::GlobalWithState<TrackingParamToPollutionSinkConfig>;
module Flow = TrackingParamToPollutionSinkFlow; // For shortening the name


/**
 * @description
 * Find the callable (method, function) whose args should be considered as a class pollution sinks.
 * More specifically, it should holds the following facts:
 * 1/ The callable has three arguments and
 * 2/ Taint flow between the API arguments to the setitem/setattr operation.
 * 
 * @note
 * This predicate favors the precision over the completeness.
 * 
 * @example
 * def func(base, key, value):
 *  if base instanceof dict:
 *    base[key] = value
 *  else: 
 *    setattr(base, key, value)
 * 
 */
predicate isClassPollutionSinkAPI(Function func, Parameter baseParm, Parameter keyParm, Parameter valueParm, string type) {
  (
    func.getAnArg() = baseParm and
    func.getAnArg() = keyParm and
    func.getAnArg() = valueParm
  ) and
  (
    (
      exists (Flow::PathNode base, Flow::PathNode key, Flow::PathNode value |
        base.getNode().asExpr() = baseParm and
        key.getNode().asExpr() = keyParm and
        value.getNode().asExpr() = valueParm and
        isClassPollutedAssignmentThroughItemSetting(base, key, value, _, _, _)
      ) and 
      not exists (Flow::PathNode base, Flow::PathNode key, Flow::PathNode value |
        base.getNode().asExpr() = baseParm and
        key.getNode().asExpr() = keyParm and
        value.getNode().asExpr() = valueParm and
        isClassPollutedAssignmentThroughAttrSetting(base, key, value, _, _, _)
      ) and
      type = "setItem"
    ) 
    or
    (
      exists (Flow::PathNode base, Flow::PathNode key, Flow::PathNode value |
        base.getNode().asExpr() = baseParm and
        key.getNode().asExpr() = keyParm and
        value.getNode().asExpr() = valueParm and
        isClassPollutedAssignmentThroughAttrSetting(base, key, value, _, _, _)
      ) and 
      not exists (Flow::PathNode base, Flow::PathNode key, Flow::PathNode value |
        base.getNode().asExpr() = baseParm and
        key.getNode().asExpr() = keyParm and
        value.getNode().asExpr() = valueParm and
        isClassPollutedAssignmentThroughItemSetting(base, key, value, _, _, _)
      ) and
      type = "setattr"
    )
    or 
    (
      exists (Flow::PathNode base, Flow::PathNode key, Flow::PathNode value,
              Flow::PathNode base1, Flow::PathNode key1, Flow::PathNode value1|
        base.getNode().asExpr() = baseParm and
        key.getNode().asExpr() = keyParm and
        value.getNode().asExpr() = valueParm and
        base1.getNode().asExpr() = baseParm and
        key1.getNode().asExpr() = keyParm and
        value1.getNode().asExpr() = valueParm and
        isClassPollutedAssignmentThroughItemSetting(base, key, value, _, _, _) and
        isClassPollutedAssignmentThroughAttrSetting(base1, key1, value1, _, _, _)
      ) and 
      type = "setBoth"
    )
  )
}


/**
 * @description
 * ----------------------
 * Holds if the assignment can overwrite the items of the object.
 */
predicate isClassPollutedAssignmentThroughItemSetting(Flow::PathNode sourceObj, Flow::PathNode sourceKey, Flow::PathNode sourceValue, Flow::PathNode setItemObj, Flow::PathNode setItemKey, Flow::PathNode setItemValue) {
  isSetItemExpr(setItemObj.getNode().asExpr(), setItemKey.getNode().asExpr(), setItemValue.getNode().asExpr(), _) and
  (
    exists(Function func, Parameter p1, Parameter p2, Parameter p3 |
      func.getAnArg() = p1 and
      func.getAnArg() = p2 and
      func.getAnArg() = p3 and
      p1 = sourceObj.getNode().asExpr() and
      p2 = sourceKey.getNode().asExpr() and
      p3 = sourceValue.getNode().asExpr()
    )
  ) and
  (
    TrackingParamToPollutionSinkFlow::flowPath(sourceKey, setItemKey) and
    setItemKey.getState() instanceof UsedAsKeyInSetItemFlowState
  ) and 
  (
    TrackingParamToPollutionSinkFlow::flowPath(sourceObj, setItemObj) and
    setItemObj.getState() instanceof UsedAsBaseObjectInSetItemFlowState
  ) and
  (
    TrackingParamToPollutionSinkFlow::flowPath(sourceValue, setItemValue) and
    setItemValue.getState() instanceof UsedAsValueInSetItemFlowState
  )
}

/**
 * @description
 * ----------------------
 * Holds if the assignment can overwrite attributes of the object.
 */
predicate isClassPollutedAssignmentThroughAttrSetting(Flow::PathNode sourceObj, Flow::PathNode sourceKey, Flow::PathNode sourceValue, Flow::PathNode setAttrObj, Flow::PathNode setAttrKey, Flow::PathNode setAttrValue) {
  isSetattrCall(setAttrObj.getNode().asExpr(), setAttrKey.getNode().asExpr(), setAttrValue.getNode().asExpr(), _) and
  (
    exists(Function func, Parameter p1, Parameter p2, Parameter p3 |
      func.getAnArg() = p1 and
      func.getAnArg() = p2 and
      func.getAnArg() = p3 and
      p1 = sourceObj.getNode().asExpr() and
      p2 = sourceKey.getNode().asExpr() and
      p3 = sourceValue.getNode().asExpr()
    )
  ) and
  (
    TrackingParamToPollutionSinkFlow::flowPath(sourceKey, setAttrKey) and
    setAttrKey.getState() instanceof UsedAsKeyInSetAttrFlowState
  ) and 
  (
    TrackingParamToPollutionSinkFlow::flowPath(sourceObj, setAttrObj) and
    setAttrObj.getState() instanceof UsedAsBaseObjectInSetAttrFlowState
  ) and
  (
    TrackingParamToPollutionSinkFlow::flowPath(sourceValue, setAttrValue) and
    setAttrValue.getState() instanceof UsedAsValueInSetAttrFlowState
  )
}
}