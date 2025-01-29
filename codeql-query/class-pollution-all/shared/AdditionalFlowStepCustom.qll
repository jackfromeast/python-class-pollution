import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import Utils::ClassPolltionUtils
import GetOp::ClassPollutionGetOp


module ClassPollutionAdditionalFlowStepCustom {

predicate additionalFlowStepThroughCustomLibAnyState(DataFlow::Node fromNode, DataFlow::Node toNode){
  additionalFlowStepThroughHikaru(fromNode, toNode) or
  additionalFlowStepThroughBuiltinStr(fromNode, toNode)
}

// ========== Builtins Starts ==========

/**
 * @description
 * ----------------------
 * Propagate the data flow from builtin functions str.
 * 
 * @example
 * ----------------------
 * when `str` is tainted in the following code snippet:
 * `str(fromNode)` -> `toNode`
 */
predicate additionalFlowStepThroughBuiltinStr(DataFlow::Node fromNode, DataFlow::Node toNode) {
  exists(API::CallNode call | 
    fromNode = API::builtin("str").getACall().getArg(0) and
    call = API::builtin("str").getACall() and
    toNode.asExpr() = call.asExpr()
  )
}

// ========== Builtins Ends ==========

// ========== Hikaru Starts ==========
// https://github.com/haxsaw/hikaru
/**
 * @description
 * ----------------------
 * HikaruBase.object_at_path can be used to retrieve any nested object based on the input path.
 * 
 * @example
 * ----------------------
 * https://github.com/robusta-dev/robusta/blob/d06212253b42d493ebc33f79bb68debb005afa4f/src/robusta/runner/object_updater.py#L5C1-L7C74
 * parent_item = obj.object_at_path(path_parts[0 : len(path_parts) - 1])
 */
predicate additionalFlowStepThroughHikaru(DataFlow::Node fromNode, DataFlow::Node toNode){
  hikaruObjectAtPath(toNode.asExpr(), fromNode.asExpr(), _) or
  hikaruObjectAtPath(_, fromNode.asExpr(), toNode.asExpr())
}

// https://hikaru.readthedocs.io/en/latest/hikaru-base.html#object-at-path
// A methodCall named object_at_path and has been defined in the hikaru module
predicate hikaruObjectAtPath(Expr obj, Expr key, Call call) {
  none() and
  exists ( MethodCallNode mcall |
    mcall.getMethodName() = "object_at_path" and
    mcall.getObject().asExpr() = obj and
    (
      mcall.getArg(0).asExpr() = key or
      // mcall.getArg could be an list of keys
      exists (List list |
        mcall.getArg(0).asExpr() = list and
        list.getAnElt() = key
      )
    ) and
    exists( DataFlow::Node objNode | 
      objNode.asExpr() = obj and
      potentiallyHasTypeOf(objNode, "HikaruBase")
    ) and 
    mcall.asExpr() = call
  )
}
// ========== Hikaru Ends==========


}