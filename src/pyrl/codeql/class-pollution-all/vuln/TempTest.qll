
import python
import semmle.python.ApiGraphs
import codeql.dataflow.DataFlow
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.internal.TaintTrackingPublic

import semmle.python.types.Version

predicate checkVersion(int major, int minor) {
  exists(Version v | v.includes(major, minor))
}

module TempTest {

abstract class FlowState extends string {
  bindingset[this]
  FlowState() { any() }
}

class SourceKeyFlowState extends TempTest::FlowState {
  SourceKeyFlowState() { this = "SourceKeyFlowState" }
}

class Occurrence extends string {
  Occurrence() { 
    this = "One" or
    this = "MoreThanOne"
  }
}

class ObjectFlowState extends TempTest::FlowState {
  Occurrence occur;

  ObjectFlowState() { this = "ObjectFlowState" + "-" + occur }
}

module TrackingGetOperationConfiguration implements DataFlow::StateConfigSig {
  class FlowState = TempTest::FlowState;

  predicate isSource(DataFlow::Node source, FlowState state) {
    exists (Function func, Parameter param | 
      func.getArg(1) = param and
      source.asExpr() = param and
      func.getName().matches("test%")
    ) and
    (
      state instanceof SourceKeyFlowState
    )
  }

  predicate isSink(DataFlow::Node sink, FlowState state) {
    exists (Function func, Return ret | 
      ret.getScope() = func.getEvaluatingScope() and
      ret.contains(sink.asExpr()) and
      func.getName().matches("test%")
    ) and
    (
      state instanceof ObjectFlowState
    )
  }

  predicate isAdditionalFlowStep(DataFlow::Node fromNode, FlowState fromState, DataFlow::Node toNode, FlowState toState) {
    exists( MethodCallNode callNode, Call call |
      callNode.asExpr() = call and
      callNode.getMethodName() = "get" and
      callNode.asExpr() = toNode.asExpr() and
      call.getArg(0) = fromNode.asExpr()
    ) and 
    fromState instanceof SourceKeyFlowState and
    toState instanceof ObjectFlowState
  }
}

module TrackingGetOperationFlow = DataFlow::GlobalWithState<TrackingGetOperationConfiguration>;
module Flow = TrackingGetOperationFlow; // For shortening the name

predicate run(Flow::PathNode source, Flow::PathNode sink, FlowState state) {
  Flow::flowPath(source, sink) and
  sink.getState() = state
}

}