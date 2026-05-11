/**
 * @name #15 operator.getitem(dict, key)
 * @description Detects usage of `operator.getitem(dict, key)` to retrieve dictionary values reflectively using the standard library’s `operator` module.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/operator-getitem
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 
 from Call c
 where isGetItemThroughOperator(_, _, c)
 select c, "#15 operator.getitem(dict, key)"
 