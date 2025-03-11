import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.TaintTracking
// import vuln.SmartGettingFuncLib::ClassPollutionSmartGetting
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

module ClassPollutionTaintTracking {

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

class Occurrence extends string {
  Occurrence() {
    this = "One" or
    this = "MoreThanOne"
  }
}

class PrototypeObjectFlowState extends ClassPollutionTaintTracking::FlowState {
  GetOperationType getOperationType;
  SetOperationType setOperationType;
  Occurrence occurrence;

  PrototypeObjectFlowState() { this = "PrototypeObject@" + setOperationType + "-" + getOperationType + "-" + occurrence }

  string toString() {
    result = "PrototypeObject@" + setOperationType + "-" + getOperationType + "-" + occurrence
  }

  SetOperationType getSetOperationType() {
    result = setOperationType
  }

  GetOperationType getGetOperationType() {
    result = getOperationType
  }

  Occurrence getOccurrence() {
    result = occurrence
  }
}

class EnumeratedKeyFlowState extends ClassPollutionTaintTracking::FlowState {
  SetOperationType setOperationType;

  EnumeratedKeyFlowState() { this = "EnumeratedKey@" + setOperationType }

  SetOperationType getSetOperationType() {
    result = setOperationType
  }
}

class InitFuncParamterFlowState extends ClassPollutionTaintTracking::FlowState {
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
  class FlowState = ClassPollutionTaintTracking::FlowState;

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
    // restrictedByFunctionName(sink, "_t_eval") and
    // state instanceof EnumeratedKeyFlowState
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
    ) or
    (
      isSetItemExpr(_, _, sink.asExpr(), _) and
      (
        state instanceof InitFuncParamterFlowState and
        state.(InitFuncParamterFlowState).getSetOperationType() = "SetItem"
      )
    ) or
    (
      isSetAttrExpr(_, _, sink.asExpr(), _) and
      (
        state instanceof InitFuncParamterFlowState and
        state.(InitFuncParamterFlowState).getSetOperationType() = "SetAttr"
      )
    )
  }

  predicate isAdditionalFlowStep(DataFlow::Node fromNode, FlowState fromState, DataFlow::Node toNode, FlowState toState) {
    // TYPE1: General flow steps
    // From ANY FlowState to ANY FlowState
    generalDataFlowStep(fromNode, fromState, toNode, toState)
    or
    generalTaintFlowStep(fromNode, fromState, toNode, toState)
    or
    // TYPE 2: From InitFuncParamterFlowState to EnumeratedKeyFlowState
    // Loop/Split/Enumerate the value with InitFuncParamterFlowState label would lead to EnumeratedKeyFlowState label
    initFuncParamterToEnumeratedKeyFlowStep(fromNode, fromState, toNode, toState)
    or
    // TYPE 3: From EnumeratedKeyFlowState to PrototypeObjectFlowState
    // If key is enumerated, taint the object with PrototypeObjectFlowState label
    // This is how we make sure that the get operation is recursive. 
    enumeratedKeyToPrototypeObjectFlowStep(fromNode, fromState, toNode, toState)
    // or
    // TODO: Unsupported:
    // TYPE 4: From PrototypeObjectFlowState (Occurrence=One) to PrototypeObjectFlowState (Occurrence=MoreThanOne)
    // prototypeObjectOneToPrototypeObjectMoreThanOneFlowStep(fromNode, fromState, toNode, toState)
  }
}

/**
 * @description
 * ----------------------
 * Flow steps in generalDataFlowStep is precise data flow tracking step.
 */
predicate generalDataFlowStep(DataFlow::Node fromNode, FlowState fromState, DataFlow::Node toNode, FlowState toState) {
  (
    (
      additionalFlowStepThroughNamedtuple(fromNode, toNode) or
      additionalFlowStepThroughDequeAppendPop(fromNode, toNode) or
      additionalFlowStepThroughReduce(fromNode, toNode) or
      additionalFlowStepThroughCustomLibAnyState(fromNode, toNode)
    ) and
    toState = fromState
  )
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
    toState = fromState and
    // We don't want to over-tainting the prototype object. It should largely close to data flow tracking.
    not fromState instanceof PrototypeObjectFlowState
  )
}

/**
 * @description
 * Extension of `DataFlow::Node` to identify nodes that hold key names that are enumerated or from split method call.
 */
predicate isClassPollutedKeyNamesOrBaseObjects(DataFlow::Node key, DataFlow::Node base) {
  splitKeyNamesAndObjectPair(key, base) or
  enumeratedKeyNamesAndObjectPair(key, base)
}

predicate initFuncParamterToEnumeratedKeyFlowStep(DataFlow::Node fromNode, FlowState fromState, DataFlow::Node toNode, FlowState toState) {
  (
    (
      isClassPollutedKeyNamesOrBaseObjects(toNode, fromNode)
    ) and
    (
      fromState instanceof EnumeratedKeyFlowState or 
      fromState instanceof InitFuncParamterFlowState
    ) and
    (
      toState instanceof EnumeratedKeyFlowState or 
      toState instanceof InitFuncParamterFlowState
    )
  )
}

predicate enumeratedKeyToPrototypeObjectFlowStep(DataFlow::Node fromNode, FlowState fromState, DataFlow::Node toNode, FlowState toState){
  ( 
    fromState instanceof EnumeratedKeyFlowState and
    (
      additionalFlowStepThroughCustomLibHoldPrototypeObject(fromNode, toNode) or
      additionalFlowStepGetAttrReverse(fromNode, toNode)
    ) and
    (
      toState instanceof PrototypeObjectFlowState and
      toState.(PrototypeObjectFlowState).getGetOperationType() = "GetAttr" and
      toState.(PrototypeObjectFlowState).getOccurrence() = "One"
    )
  ) or
  (
    fromState instanceof EnumeratedKeyFlowState and
    (
      additionalFlowStepGetItemReverse(fromNode, toNode) or
      additionalFlowStepThroughCustomLibHoldPrototypeObject(fromNode, toNode)
    ) and
    (
      toState instanceof PrototypeObjectFlowState and
      toState.(PrototypeObjectFlowState).getGetOperationType() = "GetItem" and
      toState.(PrototypeObjectFlowState).getOccurrence() = "One"
    )
  )
}

predicate prototypeObjectOneToPrototypeObjectMoreThanOneFlowStep(DataFlow::Node fromNode, FlowState fromState, DataFlow::Node toNode, FlowState toState) {
  fromState instanceof PrototypeObjectFlowState and
  fromState.(PrototypeObjectFlowState).getOccurrence() = "One" and
  (
    additionalFlowStepGetAttr(fromNode, toNode) or
    additionalFlowStepGetItem(fromNode, toNode)
  ) 
  and
  toState instanceof PrototypeObjectFlowState and
  toState.(PrototypeObjectFlowState).getOccurrence() = "MoreThanOne"
}

}