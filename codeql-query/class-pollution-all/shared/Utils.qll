import python 
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking
import Debug::Debugging
import GetOp::ClassPollutionGetOp
import SetOp::ClassPollutionSetOp

module ClassPolltionUtils {
  /**
   * @description
   * ----------------------
   * Determine the import path of the callable.
   * 
   * 1/ If the callable is a function, the import path = module path + function name.
   * 2/ If the callable is a method, the import path = module path + class name + method name.
   * 3/ If the callable is a nested function/generator, ignore it.
   */
  predicate callableImportPath(Function func, string moduleName, string className, string functionName, string filePath) {
    if func.isMethod() 
    then 
      exists (Class cls, Module mod |
        methodImportPath(func, mod, cls) and
        cls.getName() = className and
        mod.toString() = moduleName and
        mod.getPath().toString() = filePath
      )
      and functionName = func.getName() 
    else
      exists (Module mod |
        functionImportPath(func, mod) and
        mod.toString() = moduleName and
        className = "" and
        mod.getPath().toString() = filePath
      )
      and functionName = func.getName() 
  }

  predicate isFunctionParam(DataFlow::Node node) {
    exists (Function func, Parameter param | 
      func.getAnArg() = param and
      node.asExpr() = param
    )
  }

  predicate isSameFunctionParam(DataFlow::Node node1, DataFlow::Node node2) {
    exists (Function func, Parameter param1, Parameter param2 | 
      func.getAnArg() = param1 and
      func.getAnArg() = param2 and
      node1.asExpr() = param1 and
      node2.asExpr() = param2
    )
  }
  
  predicate methodImportPath(Function func, Module mod, Class cls) {
    func.getEnclosingScope() = cls and
    cls.getEnclosingModule() = mod
  }

  predicate functionImportPath(Function func, Module mod) {
    func.getEnclosingModule() = mod
  }

  /**
   * Predicate to check if a function is a callee of another function.
   */
  predicate hasCallEdgeOneJump(Function caller, Function callee) {
    exists(CallNode callExpr | 
      callExpr.getScope() = caller and
      callExpr.getFunction().refersTo(callee.getFunctionObject())
    )
  }

  /**
   * Predicate to determine if there is a dataflow path between two expressions.
   */
  predicate hasDataFlowExpr(Expr source, Expr sink) {
    exists(DataFlow::Node sourceNode, DataFlow::Node sinkNode |
      sourceNode.asExpr() = source and
      sinkNode.asExpr() = sink and
      TaintTracking::localTaint(sourceNode, sinkNode)
    )
  }

  /**
   * @description
   * ----------------------
   * Check if a call expression is within a loop.
   */
  predicate isWithinLoop(Call call) {
    exists(For forStmt |
      forStmt.getBody().contains(call) 
    ) or
    exists(While whileStmt |
      whileStmt.getBody().contains(call)
    )
  }

  /**
   * @description
   * ----------------------
   * Check if a function call is recursive (direct or indirect).
   */
  predicate isRecursiveFunc(Function func) {
    exists(Function callee |
      hasCallEdgeOneJump(func, callee) and
      callee.getFunctionObject() = func.getFunctionObject()
    )
  }


  /**
   * Predicate to check if two expressions refer to the same variable.
   */
  predicate extendExprRefersTo(Expr expr1, Expr expr2) {
    // This only holds the expression-level equality, not the value-level equality.
    // Implemented at /codeql/python-all/2.2.0/semmle/python/pointsto/PointsTo.qll
    // Not working for the following cases from our observation:
    // 1. attr.name in target_obj[attr.name] = value and setattr(target_obj, attr.name, value)
    // 2. target_obj[x[-1]] = value and setattr(target_obj, x[-1], value)
    // exists ( Value val |
    //   expr1.pointsTo(val) and 
    //   expr2.pointsTo(val)
    // ) or 
    // target_obj[attr.name] = value and setattr(target_obj, attr.name, value)
    if expr1 instanceof Attribute and expr2 instanceof Attribute
    then refersToAttribute(expr1.(Attribute), expr2.(Attribute))
    else
    // target_obj[x[-1]] = value and setattr(target_obj, x[-1], value)
    if expr1 instanceof Subscript and expr2 instanceof Subscript
    then refersToSubscript(expr1.(Subscript), expr2.(Subscript))
    else
    // target_obj[key] = value and setattr(target_obj, key, value)
    if expr1 instanceof Name and expr2 instanceof Name
    then refersToName(expr1.(Name), expr2.(Name))
    else none()
  }

  /**
   * @description
   * ----------------------
   * Holds if two names refer to the same variable.
   * 
   * @example
   * ----------------------
   * We have seen some edge cases where the same has been defined in different scopes using the same way.
   * If we have tracking dataflow, there is no local source for config_value.
   * Currently, we just match the name of the variable.
   * TODO: Improve the implementation to handle the following cases using taint flow:
   * 
   * branch A:
   *  config_value = Config.cast_target_type(config_value, attr_value, fallback_target_type)
   *  setattr(config_part, key, config_value)
   * branch B:
   *  config_value = Config.cast_target_type(config_value, attr_value, fallback_target_type)
   *  config_part[key] = config_value
   *
   */
  predicate refersToName(Name name1, Name name2) {
    exists ( DataFlow::Node node1, DataFlow::Node node2 |
      node1.asExpr() = name1 and
      node2.asExpr() = name2 and
      node1.getALocalSource() = node2.getALocalSource()
    ) or
    // If the name is a global variable, we can't track its dataflow.
    // Add a simple check to see if the name is the same under one local scope.
    (
      name1.getId() = name2.getId() and
      name1.getScope() = name2.getScope()
    )
  }

  predicate refersToAttribute(Attribute attr1, Attribute attr2) {
    exists ( DataFlow::Node base1, DataFlow::Node base2 |
      base1.asExpr() = attr1.getObject() and
      base2.asExpr() = attr2.getObject() and
      base1.getALocalSource() = base2.getALocalSource() and
      attr1.getName() = attr2.getName()
    )
  }

  predicate refersToSubscript(Subscript sub1, Subscript sub2) {
    exists ( DataFlow::Node base1, DataFlow::Node base2 |
      base1.asExpr() = sub1.getObject() and
      base2.asExpr() = sub2.getObject() and
      base1.getALocalSource() = base2.getALocalSource() and
      exists (Expr index1, Expr index2, Value val |
        sub1.getIndex() = index1 and
        sub2.getIndex() = index2 and
        index1.pointsTo(val) and
        index2.pointsTo(val)
      )
    )
  }
  
  
  /**
   * Predicate to check if a call expression is an external library call.
   */
  predicate isBuiltinFuncCall(Call call) {
    exists(CallableValue cv |
      cv.getACall().getNode() = call and
      cv.isBuiltin() 
    )
  }

  /**
   * @description
   * ----------------------
   * Holds if two dataflow nodes have the same local dataflow source.
   */
  predicate hasSameLocalSource(DataFlow::Node source, DataFlow::Node sink) {
    source.getALocalSource() = sink.getALocalSource()
  }

  /**
   * @description
   * ----------------------
   * Holds if two dataflow nodes have the same dataflow source across one jump.
   * 
   * @example
   * ----------------------
   * Select out the obj1 and obj2 from the following code:
   * 
   * def func1(obj1):
   *  setattr(obj1, "key1", "value1")
   *  func2(obj1)
   * 
   * def func2(obj2):
   *  setattr(obj2, "key2", "value2")
   */
  predicate hasSameLocalSourceOneJump(DataFlow::Node node1, DataFlow::Node node2) {
    // node1.getALocalSource() = node2.getALocalSource() or
    exists (DataFlow::Node localRefersToNode1, DataFlow::Node localSourceNode2 |
      hasSameLocalSource(node1, localRefersToNode1) and
      node2.getALocalSource() = localSourceNode2 and
      exists (CallNode callNode, Function func |
        callNode.getScope() = localRefersToNode1.getScope() and
        callNode.getAnArg() = localRefersToNode1.asCfgNode() and
        func.getFunctionObject().getACall() = callNode and
        // The following part is imprecise.
        exists (int i |
          func.getArg(i) = localSourceNode2.asExpr() and
          callNode.getArg(i) = localRefersToNode1.asCfgNode()
        )
      )
    )
  }

  /**
   * @description
   * ----------------------
   * Holds if two dataflow nodes have the same dataflow source.
   * 
   */
  predicate hasSameSource(DataFlow::Node node1, DataFlow::Node node2) {
    // restrictedByFunctionName(node1, "set_instance_value") and
    // restrictedByFunctionName(node2, "set_instance_item") and
    node1.asCfgNode().pointsTo() = node2.asCfgNode().pointsTo()
  }

  module PrototypeObjectTracking implements DataFlow::ConfigSig {
    /**
     * @description
     * ----------------------
     * Sources for prototype object tracking should be results of getOperation. 
     */
    predicate isSource(DataFlow::Node source) {
      exists (Expr getOpExpr |
        (isGetItemOp(_, _, getOpExpr) or
        isGetAttrOp(_, _, getOpExpr)) and
        source.asExpr() = getOpExpr
      )
    }
  
    predicate isSink(DataFlow::Node sink) {
      exists (Expr baseObj |
        (isSetItemExpr(baseObj, _, _, _) or
        isSetattrCall(baseObj, _, _, _)) and
        sink.asExpr() = baseObj
      )
    }
  }
  
  module PrototypeObjectTrackingFlow = DataFlow::Global<PrototypeObjectTracking>;

  /**
   * @description
   * ----------------------
   * Dataflow Tracking for prototype object with shared source.
   */
  predicate hasSameSourcePrototypeObject(DataFlow::Node node1, DataFlow::Node node2) {
    hasSameLocalSource(node1, node2) or
    exists (DataFlow::Node sharedSource |
      PrototypeObjectTrackingFlow::flow(sharedSource, node1) and
      PrototypeObjectTrackingFlow::flow(sharedSource, node2)
    )
  }

  /**
   * @description
   * ----------------------
   * Holds if the given object has the class type "type".
   * 
   * Find the local source of the object and check if it is the class instantiation.
   * If it is from a function parameter, we check the function's parameter annotation.
   * 
   */
  predicate potentiallyHasTypeOf(DataFlow::Node obj, string type) {
    exists (DataFlow::ParameterNode n |
      obj.getALocalSource() = n and
      n.getParameter().getAnnotation().toString() = type
    ) or 
    exists (CallNode call, ClassObject classObj |
      obj.getALocalSource().asCfgNode() = call and
      classObj.getACall() = call and
      classObj.getName() = type
    )
  }

}
