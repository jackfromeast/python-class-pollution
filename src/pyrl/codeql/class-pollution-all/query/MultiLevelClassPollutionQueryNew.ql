/**
 * @name New Multi-Level Class Pollution
 * @description The query finds all the class polluting assignments flow from the enumerated key.
 *              This largely follows https://codeql.github.com/codeql-query-help/javascript/js-prototype-pollution-utility/
 * @kind problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-polliution/class-pollution-func-new
 * @tags security
 *       external/cwe/cwe-915
 * @precision high
 */

 import python
 import vuln.ClassPollutingAssignLib::ClassPollutionAssignment
 import semmle.python.dataflow.new.DataFlow
 import shared.Utils::ClassPolltionUtils
 import shared.types.PossibleGetOpNode
 import shared.Debug::Debugging
 import shared.Message::ClassPollutionMessage
 module Flow = TrackingClassPollutionKeyToAssignmentFlow;
 
 from Function func, DataFlow::Node sourceParamKeyNode, DataFlow::Node sourceParamObjNode, string vulnType, string msg, PossibleGetOpNode getOpNode, PossibleGetOpNode getOpNode2,
 DataFlow::Node setOpPrimdKeyNode, DataFlow::Node setOpSecondKeyNode
 where
  (
    isClassPollutedAssignmentSetBothGetBoth(sourceParamKeyNode, sourceParamObjNode, setOpPrimdKeyNode, setOpSecondKeyNode, _, _, vulnType, _, getOpNode, getOpNode2) or
    isClassPollutedAssignmentSetBothGetAttr(sourceParamKeyNode, sourceParamObjNode, setOpPrimdKeyNode, setOpSecondKeyNode, _, _, vulnType, _, getOpNode) or
    isClassPollutedAssignmentSetItemGetBoth(sourceParamKeyNode, sourceParamObjNode, setOpPrimdKeyNode, setOpSecondKeyNode, _, _, vulnType, _, getOpNode, getOpNode2) or  
    isClassPollutedAssignmentSetItemGetAttr(sourceParamKeyNode, sourceParamObjNode, setOpPrimdKeyNode, setOpSecondKeyNode, _, _, vulnType, _, getOpNode) or
    isClassPollutedAssignmentSetAttrGetBoth(sourceParamKeyNode, sourceParamObjNode, setOpPrimdKeyNode, setOpSecondKeyNode, _, _, vulnType, _, getOpNode, getOpNode2) or
    isClassPollutedAssignmentSetAttrGetAttr(sourceParamKeyNode, sourceParamObjNode, setOpPrimdKeyNode, setOpSecondKeyNode, _, _, vulnType, _, getOpNode)
  ) and
  func.getAnArg() = sourceParamKeyNode.asExpr() and
  // We don't need to restrict them twice here, as the isClassPollutedAssignment already does that.
  // The following line would cause the query stuck in the analysis (I don't know why right now).
  // func.getAnArg() = sourceParamObjNode.asExpr() and
  outputMsg(vulnType, msg)
 select func, msg, func, func.toString(), sourceParamKeyNode, sourceParamKeyNode.toString(), sourceParamObjNode, sourceParamObjNode.toString(), setOpPrimdKeyNode, setOpPrimdKeyNode.toString(), setOpSecondKeyNode, setOpSecondKeyNode.toString(), getOpNode, getOpNode.toString()