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
 * 
 * def reduce(function, iterable, initial=initial_missing, /):
    it = iter(iterable)
    if initial is initial_missing:
        value = next(it)
    else:
        value = initial
    for element in it:
        value = function(value, element)
    return value
 */
predicate additionalFlowStepThroughReduce(DataFlow::Node fromNode, DataFlow::Node toNode) {
  // From argument of reduce call to the object argument of the function
  exists(ReduceCall reduceCall, Function targetFunc, string funcName | 
    reduceCall.getArg(0).toString() = funcName and
    targetFunc.getName() = funcName and
    ( 
      // From the arg1 of the reduce call to every argument of the target function
      (
        reduceCall.getArg(1) = fromNode.asExpr() and
        targetFunc.getAnArg() = toNode.asExpr() 
      ) or 
      // Taint Propagate the inital value
      // https://docs.python.org/3/library/functools.html
      (
        reduceCall.getArg(2) = fromNode.asExpr() and
        targetFunc.getArg(0) = toNode.asExpr()
      ) 
    )
  ) or
  // From the return value of the function to the return value of the reduce call
  exists(ReduceCall reduceCall, Function targetFunc, string funcName | 
    reduceCall.getArg(0).toString() = funcName and
    targetFunc.getName() = funcName and
    targetFunc.getAReturnValueFlowNode() = fromNode.asCfgNode() and
    reduceCall = toNode.asExpr()
  ) or
  // From the return value of the function to its first argument
  exists(ReduceCall reduceCall, Function targetFunc, string funcName | 
    reduceCall.getArg(0).toString() = funcName and
    targetFunc.getName() = funcName and
    targetFunc.getAReturnValueFlowNode() = fromNode.asCfgNode() and
    targetFunc.getArg(0) = toNode.asExpr()
  )
}

class ReduceCall extends Call {
  ReduceCall() {
    exists ( Name name |
      name.getId() = "reduce" and
      this.getFunc() = name
    ) or (
      API::moduleImport("functools").getMember("reduce").getACall().asExpr() = this
    )
  }
}

}