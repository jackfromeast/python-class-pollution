/**
 * @name New Multi-Level Class Pollution (Detailed)
 * @description The query finds all the class polluting assignments flow with detailed output.
 *              This will output the function, flow path from source key to the setAttr/setItem key, 
 *              and source key/obj, setAttr key/obj (If applicable), and setItem key/obj (If applicable) and vulnType.
 *              This largely follows https://codeql.github.com/codeql-query-help/javascript/js-prototype-pollution-utility/
 * 
 *              [ALL-IN-ONE] But the results of this query may contain duplicate rows because the some selected keys are the same.
 * @kind path-problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-polliution/class-pollution-func
 * @tags security
 *       external/cwe/cwe-915
 * @precision high
 */

import python
import vuln.ClassPollutingFuncLibNew::ClassPollutionAssignment
import TrackingClassPollutionKeyToAssignmentFlow::PathGraph
import semmle.python.dataflow.new.DataFlow
import shared.Utils::ClassPolltionUtils
import shared.Debug::Debugging

module Flow = TrackingClassPollutionKeyToAssignmentFlow;


from Function func, Parameter sourceParamKey, Parameter sourceParamObj, string vulnType, string msg,
    Flow::PathNode setOpPrimKeyFlowNode, Flow::PathNode sourceParamKeyFlowNode, DataFlow::Node setOpSecondKeyNode
where
  exists ( DataFlow::Node sourceParamKeyNode, DataFlow::Node sourceParamObjNode |
    isClassPollutedAssignment(sourceParamKeyFlowNode.getNode(), sourceParamObjNode, setOpPrimKeyFlowNode.getNode(), setOpSecondKeyNode, _, _, vulnType) and
    sourceParamObjNode.asExpr() = sourceParamObj and
    sourceParamKeyNode.asExpr() = sourceParamKey
  ) and
  (
    func.getAnArg() = sourceParamKey and
    func.getAnArg() = sourceParamObj
  ) and
  (
    (
      (vulnType = "SetBoth-GetBoth" or vulnType = "SetBoth-GetAttr") and 
      sourceParamKeyFlowNode.getNode().asExpr() = sourceParamKey and
      Flow::flowPath(sourceParamKeyFlowNode, setOpPrimKeyFlowNode) and
      msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set attribute Key: $@, Set item Op Key: $@."
    ) or
    (
      ( vulnType = "SetAttr-GetBoth" or vulnType = "SetAttr-GetAttr") and 
      sourceParamKeyFlowNode.getNode().asExpr() = sourceParamKey and
      Flow::flowPath(sourceParamKeyFlowNode, setOpPrimKeyFlowNode) and
      msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set attribute Key: $@."
    ) or
    (
      (vulnType = "SetItem-GetBoth" or vulnType = "SetItem-GetAttr") and 
      sourceParamKeyFlowNode.getNode().asExpr() = sourceParamKey and
      Flow::flowPath(sourceParamKeyFlowNode, setOpPrimKeyFlowNode) and
      msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set item Key: $@."
    )
  )
select func, sourceParamKeyFlowNode, setOpPrimKeyFlowNode, msg, func, func.toString(), sourceParamKey, sourceParamKey.getName(), sourceParamObj, sourceParamObj.getName(), setOpPrimKeyFlowNode, setOpPrimKeyFlowNode.toString(), setOpSecondKeyNode, setOpSecondKeyNode.toString()