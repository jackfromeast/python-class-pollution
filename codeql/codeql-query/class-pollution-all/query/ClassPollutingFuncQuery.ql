/**
 * @name Class Pollution Implication #3: Class Pollution Function
 * @description The query finds all the class polluting assignments flow from the enumerated key.
 *              This largely follows https://codeql.github.com/codeql-query-help/javascript/js-prototype-pollution-utility/
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
import vuln.ClassPollutingFuncLib::ClassPollutionAssignment
import TrackingClassPollutionKeyToAssignmentFlow::PathGraph

module Flow = TrackingClassPollutionKeyToAssignmentFlow;

from Flow::PathNode classPollutingKey, Flow::PathNode setAttrKey
where
  exists( Flow::PathNode sourceA, Flow::PathNode sourceB, Flow::PathNode sourceC |
    isClassPollutedAssignmentThroughItemSetting(_, _, sourceA, sourceB) and
    isClassPollutedAssignmentThroughAttrSetting(_, setAttrKey, sourceC, classPollutingKey) and
    sourceA.getNode() = sourceC.getNode()
  ) and 
  (
    Flow::flowPath(classPollutingKey, setAttrKey)
  )
select classPollutingKey, classPollutingKey, setAttrKey, "The key is used in a class polluting assignment."