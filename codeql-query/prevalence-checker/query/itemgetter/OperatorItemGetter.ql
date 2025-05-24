/**
 * @name #17 operator.itemgetter(key)(dict)
 * @description Detects usage of `operator.itemgetter(key)(dict)` to access dictionary values via a callable returned by the `operator` module’s `itemgetter` function.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/operator-itemgetter-call
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 
 from Call c
 where isGetItemThroughOperatorItemGetter(_, _, c)
 select c, "#17 operator.itemgetter(key)(dict)"
 