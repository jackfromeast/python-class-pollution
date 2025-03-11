import python
import shared.Utils::ClassPolltionUtils
import shared.GetOp::ClassPollutionGetOp
import shared.flowsteps.AdditionalFlowStep::ClassPollutionAdditionalFlowStep
import vuln.ClassPollutionTaintTrackingLib::ClassPollutionTaintTracking
import semmle.python.ApiGraphs
import codeql.dataflow.DataFlow
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.internal.TaintTrackingPublic

module SelfReferringGetOp {

abstract class FlowState extends string {
  bindingset[this]
  FlowState() { any() }
}

class SourceLocationFlowState extends SelfReferringGetOp::FlowState {
  SourceLocationFlowState() { 
    exists( Expr getOpExpr | 
      (isGetItemOp(_, _, getOpExpr) or
      isGetattrCall(_, _, getOpExpr)) and
      this = getOpExpr.getLocation().toString()
    )
  }
}

module TrackingNestedGettingOpConfiguration implements DataFlow::StateConfigSig {
  class FlowState = SelfReferringGetOp::FlowState;

  predicate isSource(DataFlow::Node source, FlowState state) {
    (
      isGetItemOp(_, _, source.asExpr()) or
      isGetattrCall(_, _, source.asExpr())
    ) and
    state instanceof SourceLocationFlowState and
    source.asExpr().getLocation().toString() = state
  }

  predicate isSink(DataFlow::Node sink, FlowState state) {
    exists (Expr getOpExpr |
      (
        isGetItemOp(sink.asExpr(), _, getOpExpr) or
        isGetattrCall(sink.asExpr(), _, getOpExpr)
      ) and
      state instanceof SourceLocationFlowState and
      getOpExpr.getLocation().toString() = state
    )
  }

  predicate isAdditionalFlowStep(DataFlow::Node fromNode, FlowState fromState, DataFlow::Node toNode, FlowState toState) {
    (
      generalDataFlowStep(fromNode, _, toNode, _)
    ) and
    fromState = toState
  }
}


module TrackingNestedGettingOpFlow = DataFlow::GlobalWithState<TrackingNestedGettingOpConfiguration>;

/**
 * @description
 * ----------------------
 * Check if the SmartGettingFunction is called within a loop or recursively.
 * We check if there is a global taint flow from the getOperation's value to the same getOperation's base object.
 * 
 * @example
 * ----------------------
 * for i in range(10):
 *  obj = base_get(obj, key)
 * 
 * for i in range(10):
 *  v = getattr(obj, key)
 *  obj = v
 * 
 * @avoids
 * ----------------------
 * for i in range(10):
 *  res[i] = base_get(obj, key)
 * 
 */
class SelfReferringGetOp extends DataFlow::Node {
  DataFlow::Node baseObj;
  DataFlow::Node key;

  SelfReferringGetOp() {
    (
      isGetattrCall(baseObj.asExpr(), key.asExpr(), this.asExpr()) or
      isGetItemOp(baseObj.asExpr(), key.asExpr(), this.asExpr())
    ) and
    TrackingNestedGettingOpFlow::flow(this, baseObj)
  }
}

}