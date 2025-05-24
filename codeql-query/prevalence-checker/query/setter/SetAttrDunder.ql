/**
 * @name #2 obj.__setattr__(name, val)
 * @description Detects usage of `__setattr__` called directly on an object instance, as in `obj.__setattr__(name, val)`, excluding `object.__setattr__(obj, name, val)`.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/setattr-dunder
 */

 import python
 import shared.SetOp::ClassPollutionSetOp
 
 from Call c
 where isSetattrDunderCall(_, _, _, c) and not isObjectSetattrDunderCall(_, _, _, c)
 select c, "#2 obj.__setattr__(name, val)"
 