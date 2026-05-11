/**
 * @name Ablation Study with Plain Taint
 * @description The query finds all the class polluting assignments flow with object taint
 * @kind problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-polliution/class-pollution-assignment-object-taint
 * @tags security
 *       external/cwe/cwe-915
 * @precision high
 */

 import python
 import semmle.python.dataflow.new.DataFlow
 import shared.Utils::ClassPolltionUtils
 import shared.types.PossibleGetOpNode
 import shared.Message::ClassPollutionMessage
 import shared.Debug::Debugging
 import vuln.ClassPolltionObjectTaintTracking::ClassPolltionObjectTaintTracking
 
 from Function func, DataFlow::Node sourceParamKeyNode, DataFlow::Node sourceParamObjNode, string vulnType, string msg, DataFlow::Node setOpKeyNode, DataFlow::Node setOpObjNode
 where
  (
    isClassPollutedAssignment(sourceParamKeyNode, sourceParamObjNode, setOpKeyNode, setOpObjNode, vulnType)
  ) and
  func.getAnArg() = sourceParamKeyNode.asExpr() and
  // We don't need to restrict them twice here, as the isClassPollutedAssignment already does that.
  // The following line would cause the query stuck in the analysis (I don't know why right now).
  // func.getAnArg() = sourceParamObjNode.asExpr() and
  outputMsgSetTypeOnly(vulnType, msg)
 select func, msg, func, func.toString(), sourceParamKeyNode, sourceParamKeyNode.toString(), sourceParamObjNode, sourceParamObjNode.toString(), setOpKeyNode, setOpKeyNode.toString(), setOpObjNode, setOpObjNode.toString()