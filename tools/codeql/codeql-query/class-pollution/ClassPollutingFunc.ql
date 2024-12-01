import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.TaintTracking
import SmartSettingFunc
import SmartGettingFunc
import Utils

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
      (
        call.getMethodName() = "items" or
        call.getMethodName() = "enumerate"
      ) and
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
    // source -> [for key in source]
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
  isSubscriptAssignment(obj.asExpr(), key.asExpr(), val.asExpr(), _) or
  isSetattrCall(obj.asExpr(), key.asExpr(), val.asExpr(), _)
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
module TrackingClassPollutionKeyThroughItemGettingConfiguration implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
    isClassPollutedKeyNames(source) or
    exists( DataFlow::Node immediateSource | 
      isClassPollutedKeyNames(immediateSource) and
      DataFlow::localFlow(immediateSource, source)
    )
  }

  predicate isSink(DataFlow::Node sink) {
    isItemSettingOrAttributeSetting(sink, _, _) or
    isItemSettingOrAttributeSetting(_, sink, _) or
    isItemSettingOrAttributeSetting(_, _, sink)
  }

  predicate isAdditionalFlowStep(DataFlow::Node source, DataFlow::Node target) {
    isAdditionalFlowStepThroughGetItem(source, target)
  }
}

module TrackingClassPollutionKeyThroughAttrGettingConfiguration implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
    isClassPollutedKeyNames(source) or
    exists( DataFlow::Node immediateSource | 
      isClassPollutedKeyNames(immediateSource) and
      DataFlow::localFlow(immediateSource, source)
    )
  }

  predicate isSink(DataFlow::Node sink) {
    isItemSettingOrAttributeSetting(sink, _, _) or
    isItemSettingOrAttributeSetting(_, sink, _) or
    isItemSettingOrAttributeSetting(_, _, sink)
  }

  predicate isAdditionalFlowStep(DataFlow::Node source, DataFlow::Node target) {
    isAdditionalFlowStepThroughGetAttr(source, target)
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


module TrackingClassPollutionKeyThroughItemGettingFlow = TaintTracking::Global<TrackingClassPollutionKeyThroughItemGettingConfiguration>;
module TrackingClassPollutionKeyThroughAttrGettingFlow = TaintTracking::Global<TrackingClassPollutionKeyThroughAttrGettingConfiguration>;

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
predicate isClassPollutedAssignmentThroughAttrGetting(DataFlow::Node obj, DataFlow::Node key, DataFlow::Node val, DataFlow::Node pollutedKeySource) {
  isItemSettingOrAttributeSetting(obj, key, val) and
  isClassPollutedKeyNames(pollutedKeySource) and
  (
    if pollutedKeySource instanceof EnumeratedKeyNames
    then 
    TrackingClassPollutionKeyThroughAttrGettingFlow::flow(pollutedKeySource, obj) and 
    TrackingClassPollutionKeyThroughAttrGettingFlow::flow(pollutedKeySource, key)
    else
    TrackingClassPollutionKeyThroughAttrGettingFlow::flow(pollutedKeySource, obj) and 
    TrackingClassPollutionKeyThroughAttrGettingFlow::flow(pollutedKeySource, key)
  )
}

/**
 * @description
 * ----------------------
 * Holds if the assignment can overwrite the dunder attributes/items of the object.
 */
predicate isClassPollutedAssignmentThroughItemGetting(DataFlow::Node obj, DataFlow::Node key, DataFlow::Node val, DataFlow::Node pollutedKeySource) {
  isItemSettingOrAttributeSetting(obj, key, val) and
  isClassPollutedKeyNames(pollutedKeySource) and
  (
    if pollutedKeySource instanceof EnumeratedKeyNames
    then 
    TrackingClassPollutionKeyThroughItemGettingFlow::flow(pollutedKeySource, obj) and 
    TrackingClassPollutionKeyThroughItemGettingFlow::flow(pollutedKeySource, key)
    else
    TrackingClassPollutionKeyThroughItemGettingFlow::flow(pollutedKeySource, obj) and 
    TrackingClassPollutionKeyThroughItemGettingFlow::flow(pollutedKeySource, key)
  )
}

predicate isClassPollutedAssignment(DataFlow::Node pollutedKeySource) {
  isClassPollutedAssignmentThroughAttrGetting(_, _, _, pollutedKeySource) and
  isClassPollutedAssignmentThroughItemGetting(_, _, _, pollutedKeySource)
}

from DataFlow::Node pollutedKeySource
where isClassPollutedAssignment(pollutedKeySource)
select pollutedKeySource, "Class Polluting Key Source: $@.", pollutedKeySource, pollutedKeySource.toString()