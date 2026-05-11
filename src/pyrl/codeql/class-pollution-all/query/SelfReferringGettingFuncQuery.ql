/**
 * @name Class Pollution Implication #2: Self-referring Getting Function
 * @description The query finds all the smart getting functions whose parameters are flow to both getItem and getAttr operation.
 * @kind path-problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-polliution/smart-getting-func
 * @tags security
 *       external/cwe/cwe-915
 * @precision high
 */

import python
import shared.types.SelfReferringGetOp::SelfReferringGetOp
import TrackingNestedGettingOpFlow::PathGraph

module Flow = TrackingNestedGettingOpFlow;


from Flow::PathNode selfReferringGetOp, Flow::PathNode baseObj
where 
  selfReferringGetOp.getNode() instanceof SelfReferringGetOp and
  Flow::flowPath(selfReferringGetOp, baseObj)
select selfReferringGetOp, selfReferringGetOp, baseObj, "The get operation is self-referring."