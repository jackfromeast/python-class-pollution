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
import shared.flowsteps.AdditionalFlowStepReduce::ClassPollutionAdditionalFlowStepReduce
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
    this = "GetAttr"
  }
}

class SetOperationType extends string {
  SetOperationType() { 
    this = "None" or
    this = "SetItem" or
    this = "SetAttr"
  }
}


class PrototypeObjectFlowState extends ClassPollutionAssignment::FlowState {
  GetOperationType getOperationType;
  SetOperationType setOperationType;

  PrototypeObjectFlowState() { this = "PrototypeObject@" + setOperationType + "-" + getOperationType }

  string toString() {
    result = "PrototypeObject@" + setOperationType + "-" + getOperationType
  }

  SetOperationType getSetOperationType() {
    result = setOperationType
  }

  GetOperationType getGetOperationType() {
    result = getOperationType
  }
}

class EnumeratedKeyFlowState extends ClassPollutionAssignment::FlowState {
  SetOperationType setOperationType;

  EnumeratedKeyFlowState() { this = "EnumeratedKey@" + setOperationType }

  SetOperationType getSetOperationType() {
    result = setOperationType
  }
}

class InitFuncParamterFlowState extends ClassPollutionAssignment::FlowState {
  SetOperationType setOperationType;

  InitFuncParamterFlowState() { this = "InitFuncParamter@" + setOperationType }

  SetOperationType getSetOperationType() {
    result = setOperationType
  }
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
    // restrictedByFunctionName(source, "_t_eval") and 
    exists (Function func, Parameter param | 
      func.getAnArg() = param and
      source.asExpr() = param
    ) and
    (
      state instanceof InitFuncParamterFlowState
    )
  }

  predicate isSink(DataFlow::Node sink, FlowState state) {
    // restrictedByFunctionName(sink, "_init_reference_module") 
    (
      isSetItemExpr(_, sink.asExpr(), _, _) and
      ((
          state instanceof EnumeratedKeyFlowState and
          state.(EnumeratedKeyFlowState).getSetOperationType() = "SetItem"
        ) or
        (
          state instanceof InitFuncParamterFlowState and
          state.(InitFuncParamterFlowState).getSetOperationType() = "SetItem"
        ))
    ) or
    (
      isSetAttrExpr(_, sink.asExpr(), _, _) and
      ((
          state instanceof EnumeratedKeyFlowState and
          state.(EnumeratedKeyFlowState).getSetOperationType() = "SetAttr"
        ) or
        (
          state instanceof InitFuncParamterFlowState and
          state.(InitFuncParamterFlowState).getSetOperationType() = "SetAttr"
        ))
    ) or
    (
      isSetItemExpr(sink.asExpr(), _, _, _) and
      (
        state instanceof PrototypeObjectFlowState and
        state.(PrototypeObjectFlowState).getSetOperationType() = "SetItem"
      )
    ) or
    (
      isSetAttrExpr(sink.asExpr(), _, _, _) and
      (
        state instanceof PrototypeObjectFlowState and
        state.(PrototypeObjectFlowState).getSetOperationType() = "SetAttr"
      )
    )
  }

  predicate isAdditionalFlowStep(DataFlow::Node fromNode, FlowState fromState, DataFlow::Node toNode, FlowState toState) {
    // General flow steps
    (
      (
        additionalFlowStepThroughNamedtuple(fromNode, toNode) or
        additionalFlowStepThroughDequeAppendPop(fromNode, toNode) or
        additionalFlowStepThroughReduce(fromNode, toNode) or
        additionalFlowStepGetAttr(fromNode, toNode) or
        additionalFlowStepGetItem(fromNode, toNode) or
        additionalFlowStepThroughCustomLibAnyState(fromNode, toNode) or
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
    ) or
    // From InitFuncParamterFlowState to EnumeratedKeyFlowState
    // if iter is from node, taint the enumerated items with EnumeratedKeyFlowState label
    (
      isClassPollutedKeyNamesOrBaseObjects(toNode, fromNode) and
      (
        fromState instanceof EnumeratedKeyFlowState or 
        fromState instanceof InitFuncParamterFlowState
      ) and
      (
        toState instanceof EnumeratedKeyFlowState or 
        toState instanceof InitFuncParamterFlowState
      )
    ) or 
    // From EnumeratedKeyFlowState to PrototypeObjectFlowState
    (
      (
        additionalFlowStepThroughCustomLibHoldPrototypeObject(fromNode, toNode) or
        additionalFlowStepGetAttrReverse(fromNode, toNode)
      ) and
      (
        toState instanceof PrototypeObjectFlowState and
        toState.(PrototypeObjectFlowState).getGetOperationType() = "GetAttr"
      )
    ) or
    (
      (
        additionalFlowStepGetItemReverse(fromNode, toNode) or
        additionalFlowStepThroughCustomLibHoldPrototypeObject(fromNode, toNode)
      ) and
      (
        toState instanceof PrototypeObjectFlowState and
        toState.(PrototypeObjectFlowState).getGetOperationType() = "GetItem"
      )
    )
  }
}

module TrackingClassPollutionKeyToAssignmentFlow = TaintTracking::GlobalWithState<TrackingClassPollutionKeyToAssignmentConfiguration>;
module Flow = TrackingClassPollutionKeyToAssignmentFlow; // For shortening the name

/**
 * @description
 * Extension of `DataFlow::Node` to identify nodes that hold key names that are enumerated or from split method call.
 */
predicate isClassPollutedKeyNamesOrBaseObjects(DataFlow::Node key, DataFlow::Node base) {
  splitKeyNamesAndObjectPair(key, base) or
  enumeratedKeyNamesAndObjectPair(key, base)
}

predicate debugTest(Flow::PathNode sourceKey, Flow::PathNode setItemObjOrKey, FlowState state) {
  exists (Function func | 
    func.getAnArg() = sourceKey.getNode().asExpr() and
    func.getName() = "update_item_attr"
  ) and
  TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceKey, setItemObjOrKey) and
  // setItemObjOrKey.getState() instanceof PrototypeObjectFlowState and
  // setItemObjOrKey.getState().(PrototypeObjectFlowState).getSetOperationType() = "SetAttr" and
  state = setItemObjOrKey.getState()
}

/**
 * @description
 * ----------------------
 * Holds if the assignment can overwrite the dunder attributes/items of the object.
 */
predicate isClassPollutedAssignmentThroughItemSetting(Flow::PathNode setItemObj, Flow::PathNode setItemKey, Flow::PathNode sourceParamToObj, Flow::PathNode sourceParamToKey, string getOpType) {
  isSetItemExpr(setItemObj.getNode().asExpr(), setItemKey.getNode().asExpr(), _, _) and
  (
    isSameFunctionParam(sourceParamToObj.getNode(), sourceParamToKey.getNode())
  ) and
  (
    TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceParamToKey, setItemKey) and
    ((
      setItemKey.getState() instanceof EnumeratedKeyFlowState and
      setItemKey.getState().(EnumeratedKeyFlowState).getSetOperationType() = "SetItem"
    ) or
    (
      setItemKey.getState() instanceof InitFuncParamterFlowState and
      setItemKey.getState().(InitFuncParamterFlowState).getSetOperationType() = "SetItem"
    ))
  ) and 
  (
    TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceParamToObj, setItemObj) and
    setItemObj.getState() instanceof PrototypeObjectFlowState and
    setItemObj.getState().(PrototypeObjectFlowState).getSetOperationType() = "SetItem" and 
    setItemObj.getState().(PrototypeObjectFlowState).getGetOperationType() = getOpType
  )
}

predicate isClassPollutedAssignmentThroughAttrSetting(Flow::PathNode setAttrObj, Flow::PathNode setAttrKey, Flow::PathNode sourceParamToObj, Flow::PathNode sourceParamToKey, string getOpType) {
  isSetattrCall(setAttrObj.getNode().asExpr(), setAttrKey.getNode().asExpr(), _, _) and
  (
    isSameFunctionParam(sourceParamToObj.getNode(), sourceParamToKey.getNode())
  ) and
  (
    TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceParamToKey, setAttrKey) and
    ((
      setAttrKey.getState() instanceof EnumeratedKeyFlowState and
      setAttrKey.getState().(EnumeratedKeyFlowState).getSetOperationType() = "SetAttr"
    ) or
    (
      setAttrKey.getState() instanceof InitFuncParamterFlowState and
      setAttrKey.getState().(InitFuncParamterFlowState).getSetOperationType() = "SetAttr"
    ))
  ) and 
  (
    TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceParamToObj, setAttrObj) and
    setAttrObj.getState() instanceof PrototypeObjectFlowState and
    setAttrObj.getState().(PrototypeObjectFlowState).getSetOperationType() = "SetAttr" and 
    setAttrObj.getState().(PrototypeObjectFlowState).getGetOperationType() = getOpType
  )
}


/**
 * @description
 * ----------------------
 * Predicate to find all kinds of class pollution assignments.
 * 
 * @param classPollutingSourceToKey - The source key node which is a function parameter that flows to the key of the setItem/setAttr.
 * @param classPollutingSourceToObj - The source object node which is a function parameter that flows to the object of the setItem/setAttr.
 * @param setOpPrimKey - The primary key node that used in the setItem/setAttr operation. For pollution with SetAttr, this is the attribute name of SetAttr. Otherwise, the key name of SetItem.
 * @param setOpSecondKey - The secondary key node that used in the setItem/setAttr operation. For pollution with SetBoth, this is the attribute name of SetItem.
 * @param setOpPrimObj - The primary object node that used in the setItem/setAttr operation. For pollution with SetBoth, this is the object of SetAttr.
 * @param setOpSecondObj - The secondary object node that used in the setItem/setAttr operation. For pollution with SetBoth, this is the object of SetItem.
 * @param pollutionType - The type of pollution.
 */
predicate isClassPollutedAssignmentAll(DataFlow::Node classPollutingSourceToKey, DataFlow::Node classPollutingSourceToObj, DataFlow::Node setOpPrimKey, DataFlow::Node setOpSecondKey, DataFlow::Node setOpPrimObj, DataFlow::Node setOpSecondObj,string pollutionType) {
  // CASE 1: SetBoth-GetBoth
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode sourceC, Flow::PathNode sourceD, 
    Flow::PathNode setItemObj1, Flow::PathNode setItemObj2, Flow::PathNode setAttrObj1, Flow::PathNode setAttrObj2,
    Flow::PathNode setAttrKey, Flow::PathNode setItemKey |
    isClassPollutedAssignmentThroughItemSetting(setItemObj1, _, sourceA, sourceB, "GetItem") and
    isClassPollutedAssignmentThroughItemSetting(setItemObj2, setItemKey, sourceA, sourceB, "GetAttr") and
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj1, _, sourceC, sourceD, "GetItem") and
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj2, setAttrKey, sourceC, sourceD, "GetAttr") and
    setItemObj1.getNode() = setItemObj2.getNode() and
    setAttrObj1.getNode() = setAttrObj2.getNode() and
    hasSameSourcePrototypeObject(setItemObj1.getNode(), setAttrObj1.getNode()) and
    sourceA.getNode() = sourceC.getNode() and
    sourceB.getNode() = sourceD.getNode() and
    classPollutingSourceToObj = sourceA.getNode() and
    classPollutingSourceToKey = sourceB.getNode() and
    setOpPrimKey = setAttrKey.getNode() and
    setOpSecondKey = setItemKey.getNode() and
    setOpPrimObj = setAttrObj1.getNode() and
    setOpSecondObj = setItemObj1.getNode() and
    pollutionType = "SetBoth-GetBoth"
  ) 
  or
  // CASE 2: SetBoth-GetAttr
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode sourceC, Flow::PathNode sourceD,
    Flow::PathNode setItemObj, Flow::PathNode setAttrObj, 
    Flow::PathNode setAttrKey, Flow::PathNode setItemKey |
    isClassPollutedAssignmentThroughItemSetting(setItemObj, setItemKey, sourceA, sourceB, "GetAttr") and
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj, setAttrKey, sourceC, sourceD, "GetAttr") and
    not isClassPollutedAssignmentThroughItemSetting(_, _, sourceA, sourceB, "GetItem") and
    not isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem") and
    hasSameSourcePrototypeObject(setItemObj.getNode(), setAttrObj.getNode()) and
    sourceA.getNode() = sourceC.getNode() and
    sourceB.getNode() = sourceD.getNode() and
    classPollutingSourceToObj = sourceA.getNode() and
    classPollutingSourceToKey = sourceB.getNode() and
    setOpPrimKey = setAttrKey.getNode() and
    setOpSecondKey = setItemKey.getNode() and
    setOpPrimObj = setAttrObj.getNode() and
    setOpSecondObj = setItemObj.getNode() and
    pollutionType = "SetBoth-GetAttr"
  )
  or 
  // CASE 3: SetItem-GetBoth
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode setItemKey,
         Flow::PathNode setItemObj1, Flow::PathNode setItemObj2 |
    isClassPollutedAssignmentThroughItemSetting(setItemObj1, _, sourceA, sourceB, "GetItem") and
    isClassPollutedAssignmentThroughItemSetting(setItemObj2, setItemKey, sourceA, sourceB, "GetAttr") and
    not exists (Flow::PathNode sourceC, Flow::PathNode sourceD |
      (isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem") or
      isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetAttr")) and
      sourceA.getNode() = sourceC.getNode() and
      sourceB.getNode() = sourceD.getNode()
    ) and
    setItemObj1.getNode() = setItemObj2.getNode() and
    classPollutingSourceToObj = sourceA.getNode() and
    classPollutingSourceToKey = sourceB.getNode() and
    setOpPrimKey = setItemKey.getNode() and
    setOpSecondKey = setItemKey.getNode() and
    setOpPrimObj = setItemObj1.getNode() and
    setOpSecondObj = setItemObj1.getNode() and
    pollutionType = "SetItem-GetBoth"
  )
  or  
  // CASE 4: SetItem-GetAttr
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode setItemKey, Flow::PathNode setItemObj |
    isClassPollutedAssignmentThroughItemSetting(setItemObj, setItemKey, sourceA, sourceB, "GetAttr") and
    not exists (Flow::PathNode sourceC, Flow::PathNode sourceD |
      (isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem") or
      isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, _)) and
      sourceA.getNode() = sourceC.getNode() and
      sourceB.getNode() = sourceD.getNode()
    ) and
    classPollutingSourceToObj = sourceA.getNode() and
    classPollutingSourceToKey = sourceB.getNode() and
    setOpPrimKey = setItemKey.getNode() and
    setOpSecondKey = setItemKey.getNode() and
    setOpPrimObj = setItemObj.getNode() and
    setOpSecondObj = setItemObj.getNode() and
    pollutionType = "SetItem-GetAttr"
  )
  or
  // CASE 5: SetAttr-GetBoth
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode setAttrKey, Flow::PathNode setAttrObj1, Flow::PathNode setAttrObj2|
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj1, _, sourceA, sourceB, "GetItem") and
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj2, setAttrKey, sourceA, sourceB, "GetAttr") and
    not exists (Flow::PathNode sourceC, Flow::PathNode sourceD |
      isClassPollutedAssignmentThroughItemSetting(_, _, sourceC, sourceD, _) and
      sourceA.getNode() = sourceC.getNode() and
      sourceB.getNode() = sourceD.getNode()
    ) and
    setAttrObj1.getNode() = setAttrObj2.getNode() and
    classPollutingSourceToObj = sourceA.getNode() and
    classPollutingSourceToKey = sourceB.getNode() and
    setOpPrimKey = setAttrKey.getNode() and
    setOpSecondKey = setAttrKey.getNode() and
    setOpPrimObj = setAttrObj1.getNode() and
    setOpSecondObj = setAttrObj1.getNode() and
    pollutionType = "SetAttr-GetBoth"
  )
  or
  // CASE 6: SetAttr-GetAttr
  exists (Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode setAttrKey, Flow::PathNode setAttrObj|
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj, setAttrKey, sourceA, sourceB, "GetAttr") and
    not exists (Flow::PathNode sourceC, Flow::PathNode sourceD |
      (isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem") or
      isClassPollutedAssignmentThroughItemSetting(_, _, sourceC, sourceD, _)) and
      sourceA.getNode() = sourceC.getNode() and
      sourceB.getNode() = sourceD.getNode()
    ) and
    classPollutingSourceToObj = sourceA.getNode() and
    classPollutingSourceToKey = sourceB.getNode() and
    setOpPrimKey = setAttrKey.getNode() and
    setOpSecondKey = setAttrKey.getNode() and
    setOpPrimObj = setAttrObj.getNode() and
    pollutionType = "SetAttr-GetAttr"
  )
}


predicate isClassPollutedAssignmentSetBothGetBoth(DataFlow::Node classPollutingSourceToKey, DataFlow::Node classPollutingSourceToObj, DataFlow::Node setOpPrimKey, DataFlow::Node setOpSecondKey, DataFlow::Node setOpPrimObj, DataFlow::Node setOpSecondObj,string pollutionType) {
  // CASE 1: SetBoth-GetBoth
  pollutionType = "SetBoth-GetBoth" and
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode sourceC, Flow::PathNode sourceD, 
    Flow::PathNode setItemObj1, Flow::PathNode setItemObj2, Flow::PathNode setAttrObj1, Flow::PathNode setAttrObj2,
    Flow::PathNode setAttrKey, Flow::PathNode setItemKey |
    isClassPollutedAssignmentThroughItemSetting(setItemObj1, _, sourceA, sourceB, "GetItem") and
    isClassPollutedAssignmentThroughItemSetting(setItemObj2, setItemKey, sourceA, sourceB, "GetAttr") and
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj1, _, sourceC, sourceD, "GetItem") and
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj2, setAttrKey, sourceC, sourceD, "GetAttr") and
    setItemObj1.getNode() = setItemObj2.getNode() and
    setAttrObj1.getNode() = setAttrObj2.getNode() and
    hasSameSourcePrototypeObject(setItemObj1.getNode(), setAttrObj1.getNode()) and
    sourceA.getNode() = sourceC.getNode() and
    sourceB.getNode() = sourceD.getNode() and
    classPollutingSourceToObj = sourceA.getNode() and
    classPollutingSourceToKey = sourceB.getNode() and
    setOpPrimKey = setAttrKey.getNode() and
    setOpSecondKey = setItemKey.getNode() and
    setOpPrimObj = setAttrObj1.getNode() and
    setOpSecondObj = setItemObj1.getNode() and
    pollutionType = "SetBoth-GetBoth"
  ) 
}


predicate isClassPollutedAssignmentSetBothGetAttr(DataFlow::Node classPollutingSourceToKey, DataFlow::Node classPollutingSourceToObj, DataFlow::Node setOpPrimKey, DataFlow::Node setOpSecondKey, DataFlow::Node setOpPrimObj, DataFlow::Node setOpSecondObj,string pollutionType) {
  // CASE 2: SetBoth-GetAttr
  pollutionType = "SetBoth-GetAttr" and
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode sourceC, Flow::PathNode sourceD,
    Flow::PathNode setItemObj, Flow::PathNode setAttrObj, 
    Flow::PathNode setAttrKey, Flow::PathNode setItemKey |
    isClassPollutedAssignmentThroughItemSetting(setItemObj, setItemKey, sourceA, sourceB, "GetAttr") and
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj, setAttrKey, sourceC, sourceD, "GetAttr") and
    not isClassPollutedAssignmentThroughItemSetting(_, _, sourceA, sourceB, "GetItem") and
    not isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem") and
    hasSameSourcePrototypeObject(setItemObj.getNode(), setAttrObj.getNode()) and
    sourceA.getNode() = sourceC.getNode() and
    sourceB.getNode() = sourceD.getNode() and
    classPollutingSourceToObj = sourceA.getNode() and
    classPollutingSourceToKey = sourceB.getNode() and
    setOpPrimKey = setAttrKey.getNode() and
    setOpSecondKey = setItemKey.getNode() and
    setOpPrimObj = setAttrObj.getNode() and
    setOpSecondObj = setItemObj.getNode()
  ) 
}

}