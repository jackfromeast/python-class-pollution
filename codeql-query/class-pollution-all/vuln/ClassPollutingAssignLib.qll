import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.TaintTracking
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
import shared.types.PossibleGetOpNode
import shared.GetOp::ClassPollutionGetOp
import shared.SetOp::ClassPollutionSetOp
import shared.Debug::Debugging
import vuln.ClassPollutionTaintTrackingLib::ClassPollutionTaintTracking

module ClassPollutionAssignment {

module TrackingClassPollutionKeyToAssignmentFlow = TaintTracking::GlobalWithState<TrackingClassPollutionKeyToAssignmentConfiguration>;
module Flow = TrackingClassPollutionKeyToAssignmentFlow; // For shortening the name

module TrackingPrototypeObjectToAssignmentFlow = DataFlow::Global<TrackingPrototypeObjectToAssignmentConfiguration>;
module PrototypeObjectDataFlow = TrackingPrototypeObjectToAssignmentFlow; // For shortening the name

predicate debugTest(Flow::PathNode sourceKey, Flow::PathNode setItemObjOrKey, FlowState state) {
  exists (Function func | 
    func.getAnArg() = sourceKey.getNode().asExpr() and
    func.getName() = "_t_eval"
  ) and
  TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceKey, setItemObjOrKey) and
  setItemObjOrKey.getState() instanceof PrototypeObjectFlowState and
  setItemObjOrKey.getState().(PrototypeObjectFlowState).getGetOperationType() = "GetItem" and
  state = setItemObjOrKey.getState()
}

/**
 * @description
 * ----------------------
 * Holds if the assignment can overwrite the dunder attributes/items of the object.
 */
predicate isClassPollutedAssignmentThroughItemSetting(Flow::PathNode setItemObj, Flow::PathNode setItemKey, Flow::PathNode sourceParamToObj, Flow::PathNode sourceParamToKey, string getOpType, string occur) {
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
    setItemObj.getState().(PrototypeObjectFlowState).getGetOperationType() = getOpType and
    setItemObj.getState().(PrototypeObjectFlowState).getOccurrence() = occur
  )
}

/**
 * @description
 * ----------------------
 * Holds if the assignment can overwrite the dunder attributes/items of the object with the value from the function as well.
 * 
 * In the strict version, we also 
 * 1/ check the value of the setItem/setAttr.
 * 2/ make sure the flow step for prototype object is data flow step (not taint flow step)
 */
predicate isClassPollutedAssignmentThroughItemSettingStrict(Flow::PathNode setItemObj, Flow::PathNode setItemKey, Flow::PathNode sourceParamToObj, Flow::PathNode sourceParamToKey, Flow::PathNode setItemVal, Flow::PathNode sourceParamToVal, string getOpType, string occur) {
  isSetItemExpr(setItemObj.getNode().asExpr(), setItemKey.getNode().asExpr(), setItemVal.getNode().asExpr(), _) and
  (
    isSameFunctionParam(sourceParamToObj.getNode(), sourceParamToKey.getNode()) and
    isSameFunctionParam(sourceParamToObj.getNode(), sourceParamToVal.getNode())
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
    setItemObj.getState().(PrototypeObjectFlowState).getGetOperationType() = getOpType and
    setItemObj.getState().(PrototypeObjectFlowState).getOccurrence() = occur 
    // Restrict the condition here will cause codeql stuck, so I moved to its caller predicates
    // PrototypeObjectDataFlow::flow(setItemObj.getState().(PrototypeObjectFlowState).getGetOpNode(), setItemObj.getNode())
  )
  and
  (
    TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceParamToVal, setItemVal) and
    setItemVal.getState() instanceof InitFuncParamterFlowState and
    setItemVal.getState().(InitFuncParamterFlowState).getSetOperationType() = "SetItem"
  )
}


predicate isClassPollutedAssignmentThroughAttrSetting(Flow::PathNode setAttrObj, Flow::PathNode setAttrKey, Flow::PathNode sourceParamToObj, Flow::PathNode sourceParamToKey, string getOpType, string occur) {
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
    setAttrObj.getState().(PrototypeObjectFlowState).getGetOperationType() = getOpType and
    setAttrObj.getState().(PrototypeObjectFlowState).getOccurrence() = occur
  )
}

predicate isClassPollutedAssignmentThroughAttrSettingStrict(Flow::PathNode setAttrObj, Flow::PathNode setAttrKey, Flow::PathNode sourceParamToObj, Flow::PathNode sourceParamToKey, Flow::PathNode setAttrVal, Flow::PathNode sourceParamToVal, string getOpType, string occur) {
  isSetattrCall(setAttrObj.getNode().asExpr(), setAttrKey.getNode().asExpr(), setAttrVal.getNode().asExpr(), _) and
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
    setAttrObj.getState().(PrototypeObjectFlowState).getGetOperationType() = getOpType and
    setAttrObj.getState().(PrototypeObjectFlowState).getOccurrence() = occur 
    // Restrict the condition here will cause codeql stuck, so I moved to its caller predicates
    // PrototypeObjectDataFlow::flow(setAttrObj.getState().(PrototypeObjectFlowState).getGetOpNode(), setAttrObj.getNode())
  ) and
  (
    TrackingClassPollutionKeyToAssignmentFlow::flowPath(sourceParamToVal, setAttrVal) and
    setAttrVal.getState() instanceof InitFuncParamterFlowState and
    setAttrVal.getState().(InitFuncParamterFlowState).getSetOperationType() = "SetAttr"
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
predicate isClassPollutedAssignmentAll(DataFlow::Node classPollutingSourceToKey, DataFlow::Node classPollutingSourceToObj, DataFlow::Node setOpPrimKey, DataFlow::Node setOpSecondKey, DataFlow::Node setOpPrimObj, DataFlow::Node setOpSecondObj, string pollutionType, string occur) {
  // CASE 1: SetBoth-GetBoth
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode sourceC, Flow::PathNode sourceD, 
    Flow::PathNode setItemObj1, Flow::PathNode setItemObj2, Flow::PathNode setAttrObj1, Flow::PathNode setAttrObj2,
    Flow::PathNode setAttrKey, Flow::PathNode setItemKey |
    isClassPollutedAssignmentThroughItemSetting(setItemObj1, _, sourceA, sourceB, "GetItem", occur) and
    isClassPollutedAssignmentThroughItemSetting(setItemObj2, setItemKey, sourceA, sourceB, "GetAttr", occur) and
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj1, _, sourceC, sourceD, "GetItem", occur) and
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj2, setAttrKey, sourceC, sourceD, "GetAttr", occur) and
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
    isClassPollutedAssignmentThroughItemSetting(setItemObj, setItemKey, sourceA, sourceB, "GetAttr", occur) and
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj, setAttrKey, sourceC, sourceD, "GetAttr", occur) and
    not isClassPollutedAssignmentThroughItemSetting(_, _, sourceA, sourceB, "GetItem", occur) and
    not isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem", occur) and
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
    isClassPollutedAssignmentThroughItemSetting(setItemObj1, _, sourceA, sourceB, "GetItem", occur) and
    isClassPollutedAssignmentThroughItemSetting(setItemObj2, setItemKey, sourceA, sourceB, "GetAttr", occur) and
    not exists (Flow::PathNode sourceC, Flow::PathNode sourceD |
      (isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem", _) or
      isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetAttr", _)) and
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
    isClassPollutedAssignmentThroughItemSetting(setItemObj, setItemKey, sourceA, sourceB, "GetAttr", occur) and
    not exists (Flow::PathNode sourceC, Flow::PathNode sourceD |
      (isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem", _) or
      isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, _, _)) and
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
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj1, _, sourceA, sourceB, "GetItem", occur) and
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj2, setAttrKey, sourceA, sourceB, "GetAttr", occur) and
    not exists (Flow::PathNode sourceC, Flow::PathNode sourceD |
      isClassPollutedAssignmentThroughItemSetting(_, _, sourceC, sourceD, _, _) and
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
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj, setAttrKey, sourceA, sourceB, "GetAttr", occur) and
    not exists (Flow::PathNode sourceC, Flow::PathNode sourceD |
      (isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem", _) or
      isClassPollutedAssignmentThroughItemSetting(_, _, sourceC, sourceD, _, _)) and
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


predicate isClassPollutedAssignmentSetBothGetBoth(DataFlow::Node classPollutingSourceToKey, DataFlow::Node classPollutingSourceToObj, DataFlow::Node setOpPrimKey, DataFlow::Node setOpSecondKey, DataFlow::Node setOpPrimObj, DataFlow::Node setOpSecondObj, string pollutionType, string occur, PossibleGetOpNode getAttrOpNode, PossibleGetOpNode getItemOpNode) {
  // CASE 1: SetBoth-GetBoth
  pollutionType = "SetBoth-GetBoth" and
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode sourceC, Flow::PathNode sourceD, 
    Flow::PathNode setItemObj1, Flow::PathNode setItemObj2, Flow::PathNode setAttrObj1, Flow::PathNode setAttrObj2,
    Flow::PathNode setAttrKey, Flow::PathNode setItemKey |
    isClassPollutedAssignmentThroughItemSetting(setItemObj1, _, sourceA, sourceB, "GetItem", occur) and
    isClassPollutedAssignmentThroughItemSetting(setItemObj2, setItemKey, sourceA, sourceB, "GetAttr", occur) and
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj1, _, sourceC, sourceD, "GetItem", occur) and
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj2, setAttrKey, sourceC, sourceD, "GetAttr", occur) and
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
    pollutionType = "SetBoth-GetBoth" and
    getAttrOpNode = setAttrObj2.getState().(PrototypeObjectFlowState).getGetOpNode() and
    getItemOpNode = setAttrObj1.getState().(PrototypeObjectFlowState).getGetOpNode()
  ) 
}

predicate isClassPollutedAssignmentSetBothGetBothStrict(DataFlow::Node classPollutingSourceToKey, DataFlow::Node classPollutingSourceToObj, DataFlow::Node setOpPrimKey, DataFlow::Node setOpSecondKey, DataFlow::Node setOpPrimObj, DataFlow::Node setOpSecondObj, string pollutionType, string occur, PossibleGetOpNode getAttrOpNode, PossibleGetOpNode getItemOpNode) {
  // CASE 1: SetBoth-GetBoth
  pollutionType = "SetBoth-GetBoth" and
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode sourceC, Flow::PathNode sourceD, 
    Flow::PathNode setItemObj1, Flow::PathNode setItemObj2, Flow::PathNode setAttrObj1, Flow::PathNode setAttrObj2,
    Flow::PathNode setAttrKey, Flow::PathNode setItemKey |
    isClassPollutedAssignmentThroughItemSettingStrict(setItemObj1, _, sourceA, sourceB, _, _, "GetItem", occur) and
    isClassPollutedAssignmentThroughItemSettingStrict(setItemObj2, setItemKey, sourceA, sourceB, _, _, "GetAttr", occur) and
    isClassPollutedAssignmentThroughAttrSettingStrict(setAttrObj1, _, sourceC, sourceD, _, _, "GetItem", occur) and
    isClassPollutedAssignmentThroughAttrSettingStrict(setAttrObj2, setAttrKey, sourceC, sourceD, _, _, "GetAttr", occur) and
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
    pollutionType = "SetBoth-GetBoth" and
    getAttrOpNode = setAttrObj2.getState().(PrototypeObjectFlowState).getGetOpNode() and
    getItemOpNode = setAttrObj1.getState().(PrototypeObjectFlowState).getGetOpNode() and
    PrototypeObjectDataFlow::flow(getAttrOpNode, setAttrObj2.getNode())
  )
}

predicate isClassPollutedAssignmentSetBothGetAttr(DataFlow::Node classPollutingSourceToKey, DataFlow::Node classPollutingSourceToObj, DataFlow::Node setOpPrimKey, DataFlow::Node setOpSecondKey, DataFlow::Node setOpPrimObj, DataFlow::Node setOpSecondObj, string pollutionType, string occur, PossibleGetOpNode getOpNode) {
  // CASE 2: SetBoth-GetAttr
  pollutionType = "SetBoth-GetAttr" and
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode sourceC, Flow::PathNode sourceD,
    Flow::PathNode setItemObj, Flow::PathNode setAttrObj, 
    Flow::PathNode setAttrKey, Flow::PathNode setItemKey |
    isClassPollutedAssignmentThroughItemSetting(setItemObj, setItemKey, sourceA, sourceB, "GetAttr", occur) and
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj, setAttrKey, sourceC, sourceD, "GetAttr", occur) and
    not isClassPollutedAssignmentThroughItemSetting(_, _, sourceA, sourceB, "GetItem", _) and
    not isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem", _) and
    hasSameSourcePrototypeObject(setItemObj.getNode(), setAttrObj.getNode()) and
    sourceA.getNode() = sourceC.getNode() and
    sourceB.getNode() = sourceD.getNode() and
    classPollutingSourceToObj = sourceA.getNode() and
    classPollutingSourceToKey = sourceB.getNode() and
    setOpPrimKey = setAttrKey.getNode() and
    setOpSecondKey = setItemKey.getNode() and
    setOpPrimObj = setAttrObj.getNode() and
    setOpSecondObj = setItemObj.getNode() and
    getOpNode = setAttrObj.getState().(PrototypeObjectFlowState).getGetOpNode()
  ) 
}

predicate isClassPollutedAssignmentSetBothGetAttrStrict(DataFlow::Node classPollutingSourceToKey, DataFlow::Node classPollutingSourceToObj, DataFlow::Node setOpPrimKey, DataFlow::Node setOpSecondKey, DataFlow::Node setOpPrimObj, DataFlow::Node setOpSecondObj, string pollutionType, string occur, PossibleGetOpNode getOpNode) {
  // CASE 2: SetBoth-GetAttr
  pollutionType = "SetBoth-GetAttr" and
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode sourceC, Flow::PathNode sourceD,
    Flow::PathNode setItemObj, Flow::PathNode setAttrObj, 
    Flow::PathNode setAttrKey, Flow::PathNode setItemKey |
    isClassPollutedAssignmentThroughItemSettingStrict(setItemObj, setItemKey, sourceA, sourceB, _, _, "GetAttr", occur) and
    isClassPollutedAssignmentThroughAttrSettingStrict(setAttrObj, setAttrKey, sourceC, sourceD, _, _, "GetAttr", occur) and
    not isClassPollutedAssignmentThroughItemSetting(_, _, sourceA, sourceB, "GetItem", _) and
    not isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem", _) and
    hasSameSourcePrototypeObject(setItemObj.getNode(), setAttrObj.getNode()) and
    sourceA.getNode() = sourceC.getNode() and
    sourceB.getNode() = sourceD.getNode() and
    classPollutingSourceToObj = sourceA.getNode() and
    classPollutingSourceToKey = sourceB.getNode() and
    setOpPrimKey = setAttrKey.getNode() and
    setOpSecondKey = setItemKey.getNode() and
    setOpPrimObj = setAttrObj.getNode() and
    setOpSecondObj = setItemObj.getNode() and
    getOpNode = setAttrObj.getState().(PrototypeObjectFlowState).getGetOpNode() and
    PrototypeObjectDataFlow::flow(getOpNode, setAttrObj.getNode())
  ) 
}

predicate isClassPollutedAssignmentSetItemGetBoth(DataFlow::Node classPollutingSourceToKey, DataFlow::Node classPollutingSourceToObj, DataFlow::Node setOpPrimKey, DataFlow::Node setOpSecondKey, DataFlow::Node setOpPrimObj, DataFlow::Node setOpSecondObj, string pollutionType, string occur, PossibleGetOpNode getAttrOpNode, PossibleGetOpNode getItemOpNode) {
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode setItemKey,
         Flow::PathNode setItemObj1, Flow::PathNode setItemObj2 |
    isClassPollutedAssignmentThroughItemSetting(setItemObj1, _, sourceA, sourceB, "GetItem", occur) and
    isClassPollutedAssignmentThroughItemSetting(setItemObj2, setItemKey, sourceA, sourceB, "GetAttr", occur) and
    not exists (Flow::PathNode sourceC, Flow::PathNode sourceD |
      (isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem", _) or
      isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetAttr", _)) and
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
    pollutionType = "SetItem-GetBoth" and
    getAttrOpNode = setItemObj2.getState().(PrototypeObjectFlowState).getGetOpNode() and
    getItemOpNode = setItemObj1.getState().(PrototypeObjectFlowState).getGetOpNode()
  )
}

predicate isClassPollutedAssignmentSetItemGetBothStrict(DataFlow::Node classPollutingSourceToKey, DataFlow::Node classPollutingSourceToObj, DataFlow::Node setOpPrimKey, DataFlow::Node setOpSecondKey, DataFlow::Node setOpPrimObj, DataFlow::Node setOpSecondObj, string pollutionType, string occur, PossibleGetOpNode getAttrOpNode, PossibleGetOpNode getItemOpNode) {
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode setItemKey,
         Flow::PathNode setItemObj1, Flow::PathNode setItemObj2 |
    isClassPollutedAssignmentThroughItemSettingStrict(setItemObj1, _, sourceA, sourceB, _, _, "GetItem", occur) and
    isClassPollutedAssignmentThroughItemSettingStrict(setItemObj2, setItemKey, sourceA, sourceB, _, _, "GetAttr", occur) and
    not exists (Flow::PathNode sourceC, Flow::PathNode sourceD |
      (isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem", _) or
      isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetAttr", _)) and
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
    pollutionType = "SetItem-GetBoth" and
    getAttrOpNode = setItemObj2.getState().(PrototypeObjectFlowState).getGetOpNode() and
    getItemOpNode = setItemObj1.getState().(PrototypeObjectFlowState).getGetOpNode() and
    PrototypeObjectDataFlow::flow(getAttrOpNode, setItemObj2.getNode())
  )
}

predicate isClassPollutedAssignmentSetItemGetAttr(DataFlow::Node classPollutingSourceToKey, DataFlow::Node classPollutingSourceToObj, DataFlow::Node setOpPrimKey, DataFlow::Node setOpSecondKey, DataFlow::Node setOpPrimObj, DataFlow::Node setOpSecondObj, string pollutionType, string occur, PossibleGetOpNode getOpNode) {
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode setItemKey, Flow::PathNode setItemObj |
    isClassPollutedAssignmentThroughItemSetting(setItemObj, setItemKey, sourceA, sourceB, "GetAttr", occur) and
    not exists (Flow::PathNode sourceC, Flow::PathNode sourceD |
      (isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem", _) or
      isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, _, _)) and
      sourceA.getNode() = sourceC.getNode() and
      sourceB.getNode() = sourceD.getNode()
    ) and
    classPollutingSourceToObj = sourceA.getNode() and
    classPollutingSourceToKey = sourceB.getNode() and
    setOpPrimKey = setItemKey.getNode() and
    setOpSecondKey = setItemKey.getNode() and
    setOpPrimObj = setItemObj.getNode() and
    setOpSecondObj = setItemObj.getNode() and
    pollutionType = "SetItem-GetAttr" and
    getOpNode = setItemObj.getState().(PrototypeObjectFlowState).getGetOpNode()
  )
}

predicate isClassPollutedAssignmentSetItemGetAttrStrict(DataFlow::Node classPollutingSourceToKey, DataFlow::Node classPollutingSourceToObj, DataFlow::Node setOpPrimKey, DataFlow::Node setOpSecondKey, DataFlow::Node setOpPrimObj, DataFlow::Node setOpSecondObj, string pollutionType, string occur, PossibleGetOpNode getOpNode) {
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode setItemKey, Flow::PathNode setItemObj |
    isClassPollutedAssignmentThroughItemSettingStrict(setItemObj, setItemKey, sourceA, sourceB, _, _, "GetAttr", occur) and
    not exists (Flow::PathNode sourceC, Flow::PathNode sourceD |
      (isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem", _) or
      isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, _, _)) and
      sourceA.getNode() = sourceC.getNode() and
      sourceB.getNode() = sourceD.getNode()
    ) and
    classPollutingSourceToObj = sourceA.getNode() and
    classPollutingSourceToKey = sourceB.getNode() and
    setOpPrimKey = setItemKey.getNode() and
    setOpSecondKey = setItemKey.getNode() and
    setOpPrimObj = setItemObj.getNode() and
    setOpSecondObj = setItemObj.getNode() and
    pollutionType = "SetItem-GetAttr" and
    getOpNode = setItemObj.getState().(PrototypeObjectFlowState).getGetOpNode() and
    PrototypeObjectDataFlow::flow(getOpNode, setItemObj.getNode())
  )
}

predicate isClassPollutedAssignmentSetAttrGetBoth(DataFlow::Node classPollutingSourceToKey, DataFlow::Node classPollutingSourceToObj, DataFlow::Node setOpPrimKey, DataFlow::Node setOpSecondKey, DataFlow::Node setOpPrimObj, DataFlow::Node setOpSecondObj, string pollutionType, string occur, PossibleGetOpNode getAttrOpNode, PossibleGetOpNode getItemOpNode) {
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode setAttrKey, Flow::PathNode setAttrObj1, Flow::PathNode setAttrObj2|
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj1, _, sourceA, sourceB, "GetItem", occur) and
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj2, setAttrKey, sourceA, sourceB, "GetAttr", occur) and
    not exists (Flow::PathNode sourceC, Flow::PathNode sourceD |
      isClassPollutedAssignmentThroughItemSetting(_, _, sourceC, sourceD, _, _) and
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
    pollutionType = "SetAttr-GetBoth" and
    getAttrOpNode = setAttrObj2.getState().(PrototypeObjectFlowState).getGetOpNode() and
    getItemOpNode = setAttrObj1.getState().(PrototypeObjectFlowState).getGetOpNode()
  )
}

predicate isClassPollutedAssignmentSetAttrGetBothStrict(DataFlow::Node classPollutingSourceToKey, DataFlow::Node classPollutingSourceToObj, DataFlow::Node setOpPrimKey, DataFlow::Node setOpSecondKey, DataFlow::Node setOpPrimObj, DataFlow::Node setOpSecondObj, string pollutionType, string occur, PossibleGetOpNode getAttrOpNode, PossibleGetOpNode getItemOpNode) {
  exists(Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode setAttrKey, Flow::PathNode setAttrObj1, Flow::PathNode setAttrObj2|
    isClassPollutedAssignmentThroughAttrSettingStrict(setAttrObj1, _, sourceA, sourceB, _, _, "GetItem", occur) and
    isClassPollutedAssignmentThroughAttrSettingStrict(setAttrObj2, setAttrKey, sourceA, sourceB, _, _, "GetAttr", occur) and
    not exists (Flow::PathNode sourceC, Flow::PathNode sourceD |
      isClassPollutedAssignmentThroughItemSetting(_, _, sourceC, sourceD, _, _) and
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
    pollutionType = "SetAttr-GetBoth" and
    getAttrOpNode = setAttrObj2.getState().(PrototypeObjectFlowState).getGetOpNode() and
    getItemOpNode = setAttrObj1.getState().(PrototypeObjectFlowState).getGetOpNode() and
    PrototypeObjectDataFlow::flow(getAttrOpNode, setAttrObj2.getNode())
  )
}

predicate isClassPollutedAssignmentSetAttrGetAttr(DataFlow::Node classPollutingSourceToKey, DataFlow::Node classPollutingSourceToObj, DataFlow::Node setOpPrimKey, DataFlow::Node setOpSecondKey, DataFlow::Node setOpPrimObj, DataFlow::Node setOpSecondObj, string pollutionType, string occur, PossibleGetOpNode getOpNode) {
  exists (Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode setAttrKey, Flow::PathNode setAttrObj|
    isClassPollutedAssignmentThroughAttrSetting(setAttrObj, setAttrKey, sourceA, sourceB, "GetAttr", occur) and
    not exists (Flow::PathNode sourceC, Flow::PathNode sourceD |
      (isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem", _) or
      isClassPollutedAssignmentThroughItemSetting(_, _, sourceC, sourceD, _, _)) and
      sourceA.getNode() = sourceC.getNode() and
      sourceB.getNode() = sourceD.getNode()
    ) and
    classPollutingSourceToObj = sourceA.getNode() and
    classPollutingSourceToKey = sourceB.getNode() and
    setOpPrimKey = setAttrKey.getNode() and
    setOpSecondKey = setAttrKey.getNode() and
    setOpPrimObj = setAttrObj.getNode() and
    pollutionType = "SetAttr-GetAttr" and
    getOpNode = setAttrObj.getState().(PrototypeObjectFlowState).getGetOpNode()
  )
}

predicate isClassPollutedAssignmentSetAttrGetAttrStrict(DataFlow::Node classPollutingSourceToKey, DataFlow::Node classPollutingSourceToObj, DataFlow::Node setOpPrimKey, DataFlow::Node setOpSecondKey, DataFlow::Node setOpPrimObj, DataFlow::Node setOpSecondObj, string pollutionType, string occur, PossibleGetOpNode getOpNode) {
  exists (Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode setAttrKey, Flow::PathNode setAttrObj|
    isClassPollutedAssignmentThroughAttrSettingStrict(setAttrObj, setAttrKey, sourceA, sourceB, _, _, "GetAttr", occur) and
    not exists (Flow::PathNode sourceC, Flow::PathNode sourceD |
      (
        isClassPollutedAssignmentThroughAttrSetting(_, _, sourceC, sourceD, "GetItem", _) or
        isClassPollutedAssignmentThroughItemSetting(_, _, sourceC, sourceD, _, _)
      ) and
      sourceA.getNode() = sourceC.getNode() and
      sourceB.getNode() = sourceD.getNode()
    ) and
    classPollutingSourceToObj = sourceA.getNode() and
    classPollutingSourceToKey = sourceB.getNode() and
    setOpPrimKey = setAttrKey.getNode() and
    setOpSecondKey = setAttrKey.getNode() and
    setOpPrimObj = setAttrObj.getNode() and
    pollutionType = "SetAttr-GetAttr" and
    getOpNode = setAttrObj.getState().(PrototypeObjectFlowState).getGetOpNode() and
    PrototypeObjectDataFlow::flow(getOpNode, setAttrObj.getNode())
  )
}

}