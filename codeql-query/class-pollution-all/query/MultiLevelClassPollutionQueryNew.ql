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
 import vuln.ClassPollutingFuncLibNew::ClassPollutionAssignment
 import semmle.python.dataflow.new.DataFlow
 import shared.Utils::ClassPolltionUtils
 import shared.Debug::Debugging
 
 module Flow = TrackingClassPollutionKeyToAssignmentFlow;
 
 
 from Function func, Parameter sourceParamKey, Parameter sourceParamObj, string vulnType, string msg,
 DataFlow::Node setOpPrimdKeyNode, DataFlow::Node setOpSecondKeyNode
 where
  exists ( DataFlow::Node sourceParamKeyNode, DataFlow::Node sourceParamObjNode |
    isClassPollutedAssignment(sourceParamKeyNode, sourceParamObjNode, setOpPrimdKeyNode, setOpSecondKeyNode, _, _, vulnType) and
    sourceParamObjNode.asExpr() = sourceParamObj and
    sourceParamKeyNode.asExpr() = sourceParamKey
  ) and
  func.getAnArg() = sourceParamKey and
  func.getAnArg() = sourceParamObj and
  (
    (
      (vulnType = "SetBoth-GetBoth" or vulnType = "SetBoth-GetAttr") and 
      msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set attribute Key: $@, Set item Op Key: $@."
    ) or
    (
      (vulnType = "SetAttr-GetBoth" or vulnType = "SetAttr-GetAttr") and 
      msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set attribute Key: $@."
    ) or
    (
      (vulnType = "SetItem-GetBoth" or vulnType = "SetItem-GetAttr") and 
      msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set item Key: $@."
    )
  )
 select func, msg, func, func.toString(), sourceParamKey, sourceParamKey.getName(), sourceParamObj, sourceParamObj.getName(), setOpPrimdKeyNode, setOpPrimdKeyNode.toString(), setOpSecondKeyNode, setOpSecondKeyNode.toString()