/**
 * @name New Multi-Level Class Pollution from External Input
 * @description The query finds all the class polluting assignments flow from the attacker controlled input.
 *              This largely follows https://codeql.github.com/codeql-query-help/javascript/js-prototype-pollution-utility/
 * @kind problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-polliution-external/set-both-get-both
 * @tags security
 *       external/cwe/cwe-915
 * @precision high
 */

 import python
 import semmle.python.dataflow.new.DataFlow
 import shared.Utils::ClassPolltionUtils
 import shared.types.PossibleGetOpNode
 import shared.Debug::Debugging
 import shared.Message::ClassPollutionMessage
 import vuln.ClassPollutingAssignLib::ClassPollutionAssignment
 import vuln.ExternalInputTaintTrackingLib
 import shared.sources.remote::ClassPollutionRemoteSource

 module Flow = TrackingClassPollutionKeyToAssignmentFlow;

 from Function func, DataFlow::Node sourceParamKeyNode, DataFlow::Node sourceParamObjNode, string vulnType, string msg, PossibleGetOpNode getAttrNode, PossibleGetOpNode getItemNode,  
 DataFlow::Node setOpPrimdKeyNode, DataFlow::Node setOpSecondKeyNode, string external
 where
  (
    isClassPollutedAssignmentSetBothGetBoth(sourceParamKeyNode, sourceParamObjNode, setOpPrimdKeyNode, setOpSecondKeyNode, _, _, vulnType, _, getAttrNode, getItemNode) and
    flowFromExternalInput(_, sourceParamKeyNode, external)
  ) and
  func.getAnArg() = sourceParamKeyNode.asExpr() and
  outputMsgFromExternal(vulnType, msg, external)
 select func, msg, func, func.toString(), sourceParamKeyNode, sourceParamKeyNode.toString(), sourceParamObjNode, sourceParamObjNode.toString(), setOpPrimdKeyNode, setOpPrimdKeyNode.toString(), setOpSecondKeyNode, setOpSecondKeyNode.toString(), 
  getAttrNode, getAttrNode.toString(), getItemNode, getItemNode.toString()