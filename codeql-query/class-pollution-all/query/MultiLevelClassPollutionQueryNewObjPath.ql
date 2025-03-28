/**
 * @name New Multi-Level Class Pollution (Detailed)
 * @description The query finds all the class polluting assignments flow with detailed output.
 *              This will output the function, flow path from source obj to the setAttr/setItem obj, 
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
import vuln.ClassPollutingAssignLib::ClassPollutionAssignment
import vuln.ClassPollutionTaintTrackingLib::ClassPollutionTaintTracking
import TrackingClassPollutionKeyToAssignmentFlow::PathGraph
import semmle.python.dataflow.new.DataFlow
import shared.types.PossibleGetOpNode
import shared.Utils::ClassPolltionUtils
import shared.Debug::Debugging

module Flow = TrackingClassPollutionKeyToAssignmentFlow;


from Function func, Parameter sourceParamKey, Parameter sourceParamObj, string vulnType, string msg, PossibleGetOpNode getOpNode,
    Flow::PathNode setOpPrimObjFlowNode, Flow::PathNode sourceParamObjFlowNode, DataFlow::Node setOpSecondObjNode
where
  // func.getName() = "calc_libraries_info" and
  exists ( DataFlow::Node sourceParamKeyNode, DataFlow::Node sourceParamObjNode |
    (
      // isClassPollutedAssignmentSetBothGetBoth(sourceParamKeyNode, sourceParamObjNode, _, _, setOpPrimObjFlowNode.getNode(), setOpSecondObjNode, vulnType, _) or
      // isClassPollutedAssignmentSetBothGetAttr(sourceParamKeyNode, sourceParamObjNode, _, _, setOpPrimObjFlowNode.getNode(), setOpSecondObjNode, vulnType, _) or 
      isClassPollutedAssignmentSetAttrGetAttrStrict(sourceParamKeyNode, sourceParamObjNode, _, _, setOpPrimObjFlowNode.getNode(), setOpSecondObjNode, vulnType, _, getOpNode)
    ) and
    sourceParamObjNode.asExpr() = sourceParamObj and
    sourceParamKeyNode.asExpr() = sourceParamKey
  ) and
  (
    func.getAnArg() = sourceParamKey 
  ) and
  (
    (
      (vulnType = "SetBoth-GetBoth" or vulnType = "SetBoth-GetAttr") and 
      sourceParamObjFlowNode.getNode().asExpr() = sourceParamObj and
      Flow::flowPath(sourceParamObjFlowNode, setOpPrimObjFlowNode) and
      msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set attribute base obj: $@, Set item Op base obj: $@. Get attribute Op: $@."
    ) or
    (
      ( vulnType = "SetAttr-GetBoth" or vulnType = "SetAttr-GetAttr") and 
      sourceParamObjFlowNode.getNode().asExpr() = sourceParamObj and
      Flow::flowPath(sourceParamObjFlowNode, setOpPrimObjFlowNode) and
      msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set attribute base obj: $@. Get attribute Op: $@."
    ) or
    (
      (vulnType = "SetItem-GetBoth" or vulnType = "SetItem-GetAttr") and 
      sourceParamObjFlowNode.getNode().asExpr() = sourceParamObj and
      Flow::flowPath(sourceParamObjFlowNode, setOpPrimObjFlowNode) and
      msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set item base obj: $@. Get attribute Op: $@."
    )
  )
select func, sourceParamObjFlowNode, setOpPrimObjFlowNode, msg, func, func.toString(), sourceParamKey, sourceParamKey.getName(), sourceParamObj, sourceParamObj.getName(), setOpPrimObjFlowNode, setOpPrimObjFlowNode.toString(), setOpSecondObjNode, setOpSecondObjNode.toString(), getOpNode, getOpNode.toString()