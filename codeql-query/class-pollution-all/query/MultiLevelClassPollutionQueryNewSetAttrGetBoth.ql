/**
 * @name New Multi-Level Class Pollution
 * @description The query finds all the class polluting assignments flow from the enumerated key.
 *              This largely follows https://codeql.github.com/codeql-query-help/javascript/js-prototype-pollution-utility/
 * @kind problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-polliution/set-attr-get-both
 * @tags security
 *       external/cwe/cwe-915
 * @precision high
 */

 import python
 import vuln.ClassPollutingAssignLibNew::ClassPollutionAssignment
 import semmle.python.dataflow.new.DataFlow
 import shared.Utils::ClassPolltionUtils
 import shared.Debug::Debugging
 
 module Flow = TrackingClassPollutionKeyToAssignmentFlow;
 
 from Function func, DataFlow::Node sourceParamKeyNode, DataFlow::Node sourceParamObjNode, string vulnType, string msg,
 DataFlow::Node setOpPrimdKeyNode, DataFlow::Node setOpSecondKeyNode
 where
  (
    isClassPollutedAssignmentSetAttrGetBothStrict(sourceParamKeyNode, sourceParamObjNode, setOpPrimdKeyNode, setOpSecondKeyNode, _, _, vulnType, _)
  ) and
  func.getAnArg() = sourceParamKeyNode.asExpr() and
  // We don't need to restrict them twice here, as the isClassPollutedAssignment already does that.
  // The following line would cause the query stuck in the analysis (I don't know why right now).
  // func.getAnArg() = sourceParamObjNode.asExpr() and
  (
    (
      (vulnType = "SetBoth-GetBoth" or vulnType = "SetBoth-GetAttr") and 
      msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set attribute Key: $@, Set item Op Key: $@."
    ) 
    or
    (
      (vulnType = "SetAttr-GetBoth" or vulnType = "SetAttr-GetAttr") and 
      msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set attribute Key: $@."
    ) or
    (
      (vulnType = "SetItem-GetBoth" or vulnType = "SetItem-GetAttr") and 
      msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set item Key: $@."
    )
  )
 select func, msg, func, func.toString(), sourceParamKeyNode, sourceParamKeyNode.toString(), sourceParamObjNode, sourceParamObjNode.toString(), setOpPrimdKeyNode, setOpPrimdKeyNode.toString(), setOpSecondKeyNode, setOpSecondKeyNode.toString()