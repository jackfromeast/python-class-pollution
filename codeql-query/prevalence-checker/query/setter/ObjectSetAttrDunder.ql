/**
 * @name #3 object.__setattr__(obj, name, val)
 * @description Detects usage of the built-in `object.__setattr__(obj, name, val)` method to set attributes reflectively at the base-object level.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/object-setattr-dunder
 */

 import python
 import shared.SetOp::ClassPollutionSetOp
 
 from Call c
 where isObjectSetattrDunderCall(_, _, _, c)
 select c, "#3 object.__setattr__(obj, name, val)"
 