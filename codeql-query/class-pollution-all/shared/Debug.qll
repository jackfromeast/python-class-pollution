import python 
private import semmle.python.dataflow.new.DataFlow
private import semmle.python.dataflow.new.TaintTracking
private import semmle.python.dataflow.new.internal.DataFlowPublic
private import semmle.python.dataflow.new.internal.DataFlowDispatch
private import semmle.python.ApiGraphs

private import semmle.python.pointsto.PointsTo
private import semmle.python.objects.ObjectInternal
private import semmle.python.pointsto.PointsToContext

module Debugging {

predicate restrictedByFunctionName(DataFlow::Node node, string functionName) {
  node.getScope().getName() = functionName
}

predicate checkFunc(DataFlow::Node node1, DataFlow::Node node2) {
  TaintTracking::localTaint(node1, node2)
}

predicate resolvedCall(CallNode call, Function callable) {
  exists(DataFlowCallable dfCallable, DataFlowCall dfCall |
    dfCallable.getScope() = callable and
    dfCall.getNode() = call and
    dfCallable = viableCallable(dfCall)
  )
}

predicate resolvedCallInternal(DataFlowCallable dfCallable, DataFlowCall dfCall) {
  any()
}

/**
 * @description
 * ----------------------
 * Check the target function of call: obj.methodName or funcName(obj)
 * Note that, this is callNode's name, not the function name (e.g., _Server() -> _Server.__init__())
 */
predicate resolveCallToFunctionDef(string name, CallCfgNode callNode, Object func) {
  (
    callNode.(MethodCallNode).getMethodName() = name and
    func.(FunctionObject).getAMethodCall() = callNode.asCfgNode()
  ) or 
  (
    func.(FunctionObject).getAFunctionCall() = callNode.asCfgNode() and
    exists (Call call, Name funcName |
      call.getFunc() = funcName and
      funcName.getId() = name and
      callNode.asExpr() = call
    ) 
  ) or
  (
    func.(ClassObject).getACall() = callNode.asCfgNode() and
    func.(ClassObject).getName() = name
  )
}

predicate selectFunctionObject(string name, FunctionObject funcObj) {
  exists(Function func |
    func.getFunctionObject() = funcObj and
    func.getName() = name
  ) and
  name = "_Server"
}

predicate resolveCallToFunctionDefWithScope(string methodName, string scopeName, CallCfgNode callNode, Function func) {
  callNode.getScope().getName() = scopeName and
  callNode.(MethodCallNode).getMethodName() = methodName and
  func.getFunctionObject().getAMethodCall() = callNode.asCfgNode()
}

predicate resolveMethodCall(string methodName, CallCfgNode callNode) {
  callNode.(MethodCallNode).getMethodName() = methodName and
  methodName = "get_hash_from_expr"
}

predicate findFunctionCallSites(API::Node call) {
  call = API::moduleImport("utils").getMember("_evaluator")
}

// predicate findFunctionCallSites(Function func, CallCfgNode callNode) {
//   func.getFunctionObject().getAMethodCall() = callNode.asCfgNode() and
//   func.getName() = "get_hash_from_expr"
// }

predicate resolveObjToDef(ControlFlowNode useNode, ClassValue cv) {
  exists(Value value |
    useNode.pointsTo(value) and
    value.getClass() = cv and
    cv.getName() = "_Evaluator"
  ) 
}



predicate resolveCallTest(CallNode call, Function target, CallType type, Node self) {
  // call.getFunction() = node
  // attrReadTracker(attr).asCfgNode() = node
  resolveMethodCall(call, target, type, self)
}

predicate test(AttrNode attr, ObjectInternal value) {
  // any()
  attr.pointsTo(value) and
  // value.introducedAt(f, context)
  // objvalue.attribute(name, value, origin) 
  // objvalue.selfAttribute(name, value, origin) and
  // name = "_B"
  // objvalue.selfAttribute(name, value, origin)
  // Expressions::attributeObjectPointsto(attr, context, name, obj, objvalue)
  // context.toString() = "/home/jackfromeast/Desktop/python-class-pollution/tests/seconary-method-call/codebase2/test.py:17 from main"
  // getsVariableAttribute(f, var, name)

  // pointsTo(f, _, _, origin) 
  attr.getName() = "_B"
}


predicate selectAllValues(Value value) {
  any()
}

predicate selectAllContexts(AttributeAssignment def, ControlFlowNode value) {
  def.getValue() = value
}
  

/**
 * @description
 * ----------------------
 * Example of how to use the resolveCallToFunctionDef predicate
 * Check target function of call obj.object_at_path in the update_item_attr function
 */
predicate exercise(CallCfgNode callNode, Object func) {
  // resolveCallToFunctionDefWithScope("get_hash_from_expr", "__front_end_update", callNode, func)
  resolveCallToFunctionDef("eat", callNode, func)
}


// Taint Tracking
module DebuggingTaintTracking implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
    exists (Function func | 
      func.getAnArg() = source.asExpr() and
      func.getName() = "eat" and
      func.getScope().getName() = "Apple"
    )
  }

  /**
   * The same as the TrackingClassPollutionKeyToAssignmentConfiguration's isSource predicate.
   */
  predicate isSink(DataFlow::Node sink) {
    exists (Call call, Name name | 
      call.getAnArg() = sink.asExpr() and
      call.getFunc() = name and
      name.getId() = "sink"
    )
  }
}

module DebuggingFlow = TaintTracking::Global<DebuggingTaintTracking>;

predicate flowFromSourceToSink(DataFlow::Node fromNode, DataFlow::Node toNode) {
  DebuggingFlow::flow(fromNode, toNode)
}

}