/**
 * @name Multi-Level Attr-only Class Pollution
 * @description The query finds all the multi-level attribute-only class polluting assignments flow from the enumerated key.
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
import vuln.deprecated.ClassPollutingAssignLib::ClassPollutionAssignment
import TrackingClassPollutionKeyToAssignmentFlow::PathGraph

module Flow = TrackingClassPollutionKeyToAssignmentFlow;

from Flow::PathNode classPollutingKey, Flow::PathNode setAttrKey, string msg
where
  exists( Flow::PathNode sourceA |
    isClassPollutedAssignmentThroughAttrSetting(_, setAttrKey, sourceA, classPollutingKey)
  )
  and 
  (
    Flow::flowPath(classPollutingKey, setAttrKey) and
    msg = "An enumeration key is used in class polluting assignments: $@ (setAttr)."

  )
select classPollutingKey, classPollutingKey, setAttrKey, msg, setAttrKey, setAttrKey.toString()