import python 
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking
import semmle.python.dataflow.new.internal.DataFlowPublic

module Debugging {

predicate restrictedByFunctionName(DataFlow::Node node, string functionName) {
  node.getScope().getName() = functionName
}

/**
 * @description
 * ----------------------
 * Check target function of call obj.methodName in the scope scopeName (e.g., function name)
 */
predicate resolveCallToFunctionDef(string methodName, string scopeName, CallCfgNode callNode, Function func) {
  callNode.getScope().getName() = scopeName and
  callNode.(MethodCallNode).getMethodName() = methodName and
  func.getFunctionObject().getAMethodCall() = callNode.asCfgNode()
}

/**
 * @description
 * ----------------------
 * Example of how to use the resolveCallToFunctionDef predicate
 * Check target function of call obj.object_at_path in the update_item_attr function
 */
predicate exercise(CallCfgNode callNode, Function func) {
  resolveCallToFunctionDef("object_at_path", "update_item_attr", callNode, func)
}

}