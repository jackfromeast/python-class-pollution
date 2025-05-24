/**
 * @name #10 operator.__setitem__(dict, key, val)
 * @description Detects usage of `operator.__setitem__(dict, key, val)` to assign values via the dunder interface of the `operator` module.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/operator-setitem-dunder
 */

 import python
 import shared.SetOp::ClassPollutionSetOp
 
 from Call c
 where isSetItemDunderThroughOperator(_, _, _, c)
 select c, "#10 operator.__setitem__(dict, key, val)"
 