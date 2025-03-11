import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import shared.Utils::ClassPolltionUtils
import shared.GetOp::ClassPollutionGetOp

// TODO: Consider move all of this to the library models

module ClassPollutionAdditionalFlowStepCustom {

predicate additionalFlowStepThroughCustomLibAnyState(DataFlow::Node fromNode, DataFlow::Node toNode){
  additionalFlowStepThroughHikaru(fromNode, toNode) or
  // additionalFlowStepThroughBuiltinStr(fromNode, toNode) or
  additionalFlowStepThroughGlom(fromNode, toNode) or 
  additionalFlowStepThroughAST(fromNode, toNode)
}

predicate additionalFlowStepThroughCustomLibHoldPrototypeObject(DataFlow::Node fromNode, DataFlow::Node toNode){
  additionalFlowStepThroughHikaru(fromNode, toNode)
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
  exists(API::CallNode call, Call callExpr| 
    call = API::builtin("str").getACall() and
    call.asExpr() = callExpr and
    callExpr.getArg(0) = fromNode.asExpr() and
    toNode.asExpr() = callExpr
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

// ========== glom Starts ==========

/**
 * @description
 * ----------------------
 * Propagate the data flow from glom arg_val function.
 * 
 * https://github.com/mahmoud/glom/blob/c225e2abeb234be7119911b96b4378cc9d8d6478/glom/core.py#L2583-L2592
 * 
 * @example
 * ----------------------
 * when `str` is tainted in the following code snippet:
 * `str(fromNode)` -> `toNode`
 */
predicate additionalFlowStepThroughGlom(DataFlow::Node fromNode, DataFlow::Node toNode) {
  // Used as library call
  exists(API::CallNode call, Call callExpr | 
    API::moduleImport("glom").getMember("core").getMember("arg_val").getACall() = call and
    call.asExpr() = callExpr and
    callExpr.getArg(1) = fromNode.asExpr() and
    callExpr = toNode.asExpr()
  ) or 
  // Used in the glom.core module
  exists(CallNode callNode, FunctionObject func| 
    func.getACall() = callNode and
    func.getName() = "arg_val" and
    callNode.getArg(1) = fromNode.asCfgNode() and
    callNode = toNode.asCfgNode()
  )
}

// ========== glom Ends ==========

// ========== ast Starts ==========

/**
 * @description
 * ----------------------
 * Propagate the data flow from ast.parse.
 * 
 * @example
 * ----------------------
 * when `ast.Call` is tainted in the following code snippet:
 * `ast.parse(fromNode)` -> `toNode`
 */
predicate additionalFlowStepThroughAST(DataFlow::Node fromNode, DataFlow::Node toNode) {
  // Used as library call
  exists(API::CallNode call, Call callExpr | 
    API::moduleImport("ast").getMember("parse").getACall() = call and
    call.asExpr() = callExpr and
    callExpr.getArg(0) = fromNode.asExpr() and
    callExpr = toNode.asExpr()
  ) or
  exists(API::CallNode call, Call callExpr | 
    API::moduleImport("ast").getMember("walk").getACall() = call and
    call.asExpr() = callExpr and
    callExpr.getArg(0) = fromNode.asExpr() and
    callExpr = toNode.asExpr()
  ) 
}

}