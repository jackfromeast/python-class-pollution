import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.TaintTracking
import semmle.python.ApiGraphs
import shared.Debug::Debugging

/**
 * @description
 * ----------------------
 * Represents a node that generated from reading the __dict__ or __slots__ attribute of an object.
 * 
 * @example
 * ----------------------
 * for attr in attrs[:-1]:
 *   target = obj.__dict__.get(attr)
 * 
 * or target = vars(obj)[attr]
 * 
 * @note
 * ----------------------
 * This only tracks the __dict__ attribute of an object in function scope.
 */
class DunderDictObject extends DataFlow::Node {
  DataFlow::Node baseObj;

  DunderDictObject() {
    exists(AttrRead attrRead |
      (
        attrRead.getAttributeName() = "__dict__" or
        attrRead.getAttributeName() = "__slots__"
      ) and
      attrRead.getObject() = baseObj and
      (
        DataFlow::localFlow(attrRead, this) or
        attrRead = this
      )
    ) 
    // or
    // exists (API::CallNode callNode, DataFlow::Node immediateDFNode|
    //   API::builtin("vars").getACall() = callNode and
    //   callNode.getArg(0) = baseObj and
    //   callNode.asExpr() = immediateDFNode.asExpr() and
    //   (
    //     immediateDFNode.asExpr() = this.asExpr() or
    //     DataFlow::localFlow(immediateDFNode, this)
    //   )
    // )
  }

  DataFlow::Node getBaseObject() {
    result = baseObj
  }
}

// predicate getVarsFunc(API::CallNode callNode) {
//   API::builtin("vars").getACall() = callNode
// }
