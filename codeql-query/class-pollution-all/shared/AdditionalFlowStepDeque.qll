import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import Utils::ClassPolltionUtils
import GetOp::ClassPollutionGetOp


module ClassPollutionAdditionalFlowStepDeque {

class DequeObj extends DataFlow::Node {
  DequeObj() {
    API::moduleImport("collections").getMember("deque").getReturn().getAValueReachableFromSource() = this
  }
}

/**
 * @description
 * ----------------------
 * Used to find all refersTo relationships bewteen all the deque objects
 */
module GlobalDataFlowHelperForDequeConfig implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
    source instanceof DequeObj
  }

  predicate isSink(DataFlow::Node sink) {
    sink instanceof DequeObj
  }
}

module GlobalDataFlowHelperForDeque = DataFlow::Global<GlobalDataFlowHelperForDequeConfig>;

/**
 * @description
 * ----------------------
 * Propagate the data flow from deque's append and pop operation.
 * 
 * 
 * @example
 * ----------------------
 * when `deque` is tainted in the following code snippet:
 * `deque.append(fromNode), toNode=deque.pop()`: `fromNode` -> `toNode`
 */
predicate additionalFlowStepThroughDequeAppendPop(DataFlow::Node fromNode, DataFlow::Node toNode) {
  exists( DequeObj dequeObj1, DequeObj dequeObj2| 
    findAllDequesAppendMethod(dequeObj1, fromNode, _) and
    findAllDequesPopMethod(dequeObj2, toNode, _) and
    GlobalDataFlowHelperForDeque::flow(dequeObj1, dequeObj2)
  )
}

predicate findAllDequesPopMethod(DequeObj dequeObj, DataFlow::Node retNode, MethodCallNode popMethod) {
  popMethod.getMethodName() = "pop" and
  popMethod.getObject() = dequeObj and
  popMethod.flowsTo(retNode)
}

predicate findAllDequesAppendMethod(DequeObj dequeObj, DataFlow::Node retNode, MethodCallNode appendMethod) {
  appendMethod.getMethodName() = "append" and
  appendMethod.getObject() = dequeObj and
  appendMethod.getArg(0) = retNode
}
}