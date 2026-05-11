/**
 * @name #16 operator.__getitem__(dict, key)
 * @description Detects usage of `operator.__getitem__(dict, key)` to access dictionary elements using the dunder method interface of the `operator` module.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/operator-getitem-dunder
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 
 from Call c
 where isGetItemDunderThroughOperator(_, _, c)
 select c, "#16 operator.__getitem__(dict, key)"
 