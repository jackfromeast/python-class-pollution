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
import shared.GetOp::ClassPollutionGetOp
import shared.SetOp::ClassPollutionSetOp
import shared.Debug::Debugging

/**
 * @description
 * ----------------------
 * Represents a node that holds the key names that are split from a string.
 * 
 * @example
 * ----------------------
 * `key` in `keys = val.split('.'); for key in keys:`
 * `key` in `keys = val.split('.'); keys[index]`
 * `key` in `keys = regex.split(any); for key in keys:`
 * `key` in `keys = regex.split(any); keys[index]`
 * 
 */
class SplitKeyNames extends DataFlow::Node {
  SplitKeyNames() {
    // Match for nodes iterating over or accessing elements from the split list
    exists(DataFlow::Node list |
      isSplitResult(list, _) and 
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
        or 
        this = list
      )
    )
  }
}

predicate splitKeyNamesAndObjectPair(DataFlow::Node key, DataFlow::Node obj) {
  exists( DataFlow::Node list |
    isSplitResult(list, obj) and 
    (
      // Iterating over the split list in a for loop
      exists(For forLoop |
        forLoop.getIter() = list.asExpr() and
        key.asExpr() = forLoop.getTarget()
      )
      or
      // Accessing elements of the split list by index
      exists(Subscript subscript |
        subscript.getObject() = list.asExpr() and
        key.asExpr() = subscript
      )
      or 
      key = list
    )
  )
}

/**
 * @description
 * ----------------------
 * Find all the split results from the `split` method call.
 * 
 * @example
 * ----------------------
 * `keys` in `keys = val.split('.')`
 * `keys` in `keys = [for key in val.split('.')]`
 * `keys` in `keys = [for key in filter(None, val.split('.'))]`
 * `keys` in `keys = regex.split(/x/, base);`
 * `keys` in `keys = regex.findall(/x/, base);`
 * 
 * 
 */
predicate isSplitResult(DataFlow::Node list, DataFlow::Node base) {
  exists ( DataFlow::Node call |
    TrackingSplitResultFlow::flow(call, list) and 
    isSplitResultImmediate(call, base)
  )
}

module TrackingSplitResultConfiguration implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node list) {
    isSplitResultImmediate(list, _)
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


predicate isSplitResultImmediate(DataFlow::Node list, DataFlow::Node base) {
  exists(MethodCallNode call|
    call.getMethodName() = "split" and
    call = list and
    call.getObject() = base
  ) or 
  exists( API::CallNode call |
    (
      API::moduleImport("re").getMember("split").getACall() = call or
      API::moduleImport("re").getMember("findall").getACall() = call or
      API::moduleImport("regex").getMember("split").getACall() = call // https://pypi.org/project/regex/
    ) and
    call.asCfgNode() = list.asCfgNode() and
    base.asExpr() = call.asCfgNode().(CallNode).getArg(1).getNode()
  )
}


