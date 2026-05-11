/**
 * @name New Multi-Level Class Pollution
 * @description The query finds all the class polluting assignments flow from the enumerated key.
 *              This largely follows https://codeql.github.com/codeql-query-help/javascript/js-prototype-pollution-utility/
 * @kind problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-polliution-external/set-item-get-both
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
 import shared.sources.remote::ClassPollutionRemoteSource
 import vuln.ExternalInputTaintTrackingLib
 module Flow = TrackingClassPollutionKeyToAssignmentFlow;

 from Function func, DataFlow::Node sourceParamKeyNode, DataFlow::Node sourceParamObjNode, string vulnType, string msg, PossibleGetOpNode getAttrOpNode, PossibleGetOpNode getItemOpNode,
 DataFlow::Node setOpPrimdKeyNode, DataFlow::Node setOpSecondKeyNode, string external
 where
  (
    isClassPollutedAssignmentSetItemGetBothStrict(sourceParamKeyNode, sourceParamObjNode, setOpPrimdKeyNode, setOpSecondKeyNode, _, _, vulnType, _, getAttrOpNode, getItemOpNode) and
    flowFromExternalInput(_, sourceParamKeyNode, external)
  ) and
  func.getAnArg() = sourceParamKeyNode.asExpr() and
  // We don't need to restrict them twice here, as the isClassPollutedAssignment already does that.
  // The following line would cause the query stuck in the analysis (I don't know why right now).
  // func.getAnArg() = sourceParamObjNode.asExpr() and
  outputMsgFromExternal(vulnType, msg, external)
 select func, msg, func, func.toString(), sourceParamKeyNode, sourceParamKeyNode.toString(), sourceParamObjNode, sourceParamObjNode.toString(),
   setOpPrimdKeyNode, setOpPrimdKeyNode.toString(), getAttrOpNode, getAttrOpNode.toString(), getItemOpNode, getItemOpNode.toString()