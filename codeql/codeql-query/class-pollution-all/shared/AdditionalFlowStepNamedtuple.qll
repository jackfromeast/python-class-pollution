import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import Utils::ClassPolltionUtils
import GetOp::ClassPollutionGetOp


module ClassPollutionAdditionalFlowStepNamedtuple {

/**
 * @description
 * ----------------------
 * Represents an object has namedtuple type which can be used to create namedtuples.
 * 
 * @example
 * ----------------------
 * StackItem = namedtuple('StackItem', ['name', 'access_method'])
 */
class NamedtupleTemplateObj extends DataFlow::Node {
  NamedtupleTemplateObj() {
    API::moduleImport("collections").getMember("namedtuple").getReturn().getAValueReachableFromSource() = this
  }
}

/**
 * @description
 * ----------------------
 * Propagate the data flow from namedtuple contrustion.
 * 
 * 
 * @example
 * ----------------------
 * `StackItem = namedtuple('StackItem', ['obj', 'access_method']); item = StackItem(item1)`
 * : `item1` -> `StackItem(obj=item1)`
 * 
 * @note
 * ----------------------
 * This is not precise and may have false positives.
 * TODO: precise the flow
 */
predicate additionalFlowStepThroughNamedtuple(DataFlow::Node fromNode, DataFlow::Node toNode) {
  exists( NamedtupleTemplateObj namedtupleObj, CallNode call, Value val| 
    call.getFunction() =  namedtupleObj.asCfgNode() and
    call.getArg(0) = fromNode.asCfgNode() and
    call.getNode() = toNode.asExpr()
  )
}

// predicate findAllDequesPopMethod(DequeObj dequeObj, DataFlow::Node retNode, MethodCallNode popMethod) {
//   popMethod.getMethodName() = "pop" and
//   popMethod.getObject() = dequeObj and
//   popMethod.flowsTo(retNode)
// }

// predicate findAllDequesAppendMethod(DequeObj dequeObj, DataFlow::Node retNode, MethodCallNode appendMethod) {
//   appendMethod.getMethodName() = "append" and
//   appendMethod.getObject() = dequeObj and
//   appendMethod.getArg(0) = retNode
// }
}