/**
 * @name #9 operator.setitem(dict, key, val)
 * @description Detects usage of `operator.setitem(dict, key, val)` to perform reflective assignment of dictionary entries using the standard library’s `operator` module.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/operator-setitem
 */

 import python
 import shared.SetOp::ClassPollutionSetOp
 
 from Call c
 where isSetItemThroughOperator(_, _, _, c)
 select c, "#9 operator.setitem(dict, key, val)"
 