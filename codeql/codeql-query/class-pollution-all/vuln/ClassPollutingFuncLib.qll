import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.TaintTracking
import vuln.SmartGettingFuncLib::ClassPollutionSmartGetting
import vuln.SmartSettingFuncLib::ClassPollutionSmartSetting
import shared.Utils::ClassPolltionUtils
import shared.AdditionalFlowStep::ClassPollutionAdditionalFlowStep
import shared.AdditionalFlowStepDeque::ClassPollutionAdditionalFlowStepDeque
import shared.AdditionalFlowStepNamedtuple::ClassPollutionAdditionalFlowStepNamedtuple
import shared.GetOp::ClassPollutionGetOp
import shared.SetOp::ClassPollutionSetOp
import shared.Debug::Debugging

module ClassPollutionAssignment {
/**
 * @description
 * ----------------------
 * Represents a node that holds the key names that are enumerated in the code.
 * 
 * @example
 * ----------------------
 * `key` in `for key in dict:`
 * `key` and `val` in `for key, val in dict.items():`
 * `key` in `for key in dict.keys():`
 * 
 */
class EnumeratedKeyNames extends DataFlow::Node {
  EnumeratedKeyNames() {
    // Match for `for key in dict`
    exists(For forLoop |
      this.asExpr() = forLoop.getTarget() and
      not forLoop.getTarget() instanceof Tuple
    )
    or
    // Match for `for k, v in dict.items()`
    exists(For forLoop, MethodCallNode call, Tuple tuple |
      forLoop.getIter() = call.asExpr() and
      call.getMethodName() = "items" and
      tuple = forLoop.getTarget() and
      (
        tuple.getElt(0) = this.asExpr() or
        tuple.getElt(1) = this.asExpr()
      )
    )
    or
    // Match for `for key in dict.keys():`
    exists(For forLoop, MethodCallNode call |
      forLoop.getIter() = call.asExpr() and
      call.getMethodName() = "keys" and
      this.asExpr() = forLoop.getTarget()
    )
    or 
    // Match for for `key, value in enumerate(dict):`
    exists(For forLoop, API::CallNode call, Tuple tuple |
      API::builtin("enumerate").getACall() = call and
      forLoop.getIter() = call.asExpr() and
      tuple = forLoop.getTarget() and
      (
        tuple.getElt(0) = this.asExpr() or
        tuple.getElt(1) = this.asExpr()
      )
    )
  }
}

/**
 * @description
 * ----------------------
 * Represents a node that holds the key names that are split from a string.
 * 
 * @example
 * ----------------------
 * `key` in `keys = val.split('.'); for key in keys:`
 * `key` in `keys = val.split('.'); keys[index]`
 * 
 */
class SplitKeyNames extends DataFlow::Node {
  SplitKeyNames() {
    // Match for nodes iterating over or accessing elements from the split list
    exists(DataFlow::Node list |
      isSplitResult(list) and 
      (
        // Iterating over the split list in a for loop
        exists(For forLoop |
          forLoop.getIter() = list.asExpr() and
          this.asExpr() = forLoop.getTarget()
        )
        or
        // Accessing elements of the split list by index
        exists(Subscript subscript |
          subscript.getObject() = list.asExpr() and
          this.asExpr() = subscript
        )
      )
    )
  }
}

module TrackingSplitResultConfiguration implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node list) {
    exists(MethodCallNode call|
      call.getMethodName() = "split" and
      call = list
    )
  }

  predicate isSink(DataFlow::Node sink) {
    any()
  }

  predicate isAdditionalFlowStep(DataFlow::Node source, DataFlow::Node target) {
    // source -> filter(none, source)
    (
      exists(Call call, DataFlow::Node immediateNode, Name name |
        name.getId() = "filter" and
        call.getFunc() = name and 
        call.getArg(1) = immediateNode.asExpr() and
        (
          immediateNode = source or
          DataFlow::localFlow(source, immediateNode)
        ) and
        (
          call = target.asExpr() or
          hasDataFlowExpr(call, target.asExpr())
        )
    ) or
    // source -> [key for key in source]
    exists(Comp comp, DataFlow::Node immediateNode|
      comp.getIterable() = source.asExpr() and
      immediateNode.asExpr() = comp and
      DataFlow::localFlow(immediateNode, target)
    )
  )
  }
}

module TrackingSplitResultFlow = TaintTracking::Global<TrackingSplitResultConfiguration>;

/**
 * @description
 * ----------------------
 * Find all the split results from the `split` method call.
 * 
 * @example
 * ----------------------
 * `keys` in `keys = val.split('.')`
 * `keys` in `keys = [for key in val.split('.')]`
 * `Keys` in `keys = [for key in filter(None, val.split('.'))]`
 * 
 */
predicate isSplitResult(DataFlow::Node list) {
  exists (DataFlow::Node call|
    TrackingSplitResultFlow::flow(call, list)
  )
}

predicate isItemSettingOrAttributeSetting(DataFlow::Node obj, DataFlow::Node key, DataFlow::Node val) {
  isSetItemExpr(obj.asExpr(), key.asExpr(), val.asExpr(), _) or
  isSetattrCall(obj.asExpr(), key.asExpr(), val.asExpr(), _)
}

/**
 * @description
 * ----------------------
 * A FlowState to indicate whether the data is used as a key or object in getItem/getAttr operation.
 */
abstract class FlowState extends string {
  bindingset[this]
  FlowState() { any() }
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
    isClassPollutedKeyNames(source) or
    exists( DataFlow::Node immediateSource | 
      isClassPollutedKeyNames(immediateSource) and
      DataFlow::localFlow(immediateSource, source)
    )
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
    isGetattrCall(_, source.asExpr(), getattrCall.asExpr()) and
    (
      DataFlow::localFlow(getattrCall, target) or
      getattrCall = target
    )
  ) or 
  // Propagate taint on every getValue operation from polluted object
  // obj -> getattr(obj, key)
  exists( DataFlow::Node getattrCall | 
    isGetattrCall(source.asExpr(), _, getattrCall.asExpr()) and
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
predicate isClassPollutedKeyNames(DataFlow::Node source) {
  source instanceof EnumeratedKeyNames or
  source instanceof SplitKeyNames
}

/**
 * @description
 * ----------------------
 * Holds if the assignment can overwrite the dunder attributes/items of the object.
 */
predicate isClassPollutedAssignmentThroughItemSetting(Flow::PathNode setItemObj, Flow::PathNode setItemKey, Flow::PathNode sourceKeyToObj, Flow::PathNode sourceKeyToKey) {
  isSetItemExpr(setItemObj.getNode().asExpr(), setItemKey.getNode().asExpr(), _, _) and
  (
    isClassPollutedKeyNames(sourceKeyToObj.getNode()) and
    isClassPollutedKeyNames(sourceKeyToKey.getNode()) and
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
    isClassPollutedKeyNames(sourceKeyToObj.getNode()) and
    isClassPollutedKeyNames(sourceKeyToKey.getNode()) and
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