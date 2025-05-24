/**
 * @name #1 setattr(obj, name, val)
 * @description Detects usage of the built-in `setattr(obj, name, val)` function to set object attributes reflectively.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/setattr-builtin
 */

 import python
 import shared.SetOp::ClassPollutionSetOp
 
 from Call c
 where isSetattrBuiltinCall(_, _, _, c)
 select c, "#1 setattr(obj, name, val)"
 