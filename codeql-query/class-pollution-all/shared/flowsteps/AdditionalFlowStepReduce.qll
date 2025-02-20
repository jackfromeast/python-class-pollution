import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import shared.Utils::ClassPolltionUtils
import shared.GetOp::ClassPollutionGetOp


module ClassPollutionAdditionalFlowStepReduce {

/**
 * @description
 * ----------------------
 * Propagate the data flow from deque's append and pop operation.
 * 
 * 
 * @example
 * ----------------------
 * reduce(_lookup, nodes[:-1], obj)
 * 
 * def _lookup(obj, key):
 *  return obj[key]
 */
predicate additionalFlowStepThroughReduce(DataFlow::Node fromNode, DataFlow::Node toNode) {
  // From argument of reduce call to the object argument of the function
  exists(ReduceCall reduceCall, Function targetFunc, string funcName | 
    reduceCall.getArg(0).toString() = funcName and
    targetFunc.getName() = funcName and
    exists( int i | 
      reduceCall.getArg(i+1) = fromNode.asExpr() and
      targetFunc.getArg(i) = toNode.asExpr() 
    )
  ) or
  // From the return value of the function to the return value of the reduce call
  exists(ReduceCall reduceCall, Function targetFunc, string funcName | 
    reduceCall.getArg(0).toString() = funcName and
    targetFunc.getName() = funcName and
    targetFunc.getAReturnValueFlowNode() = fromNode.asCfgNode() and
    reduceCall = toNode.asExpr()
  )
}

class ReduceCall extends Call {
  ReduceCall() {
    exists ( Name name |
      name.getId() = "reduce" and
      this.getFunc() = name
    )
  }
}

}