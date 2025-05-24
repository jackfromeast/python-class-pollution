/**
 * @name #7 dict.update(key=val)
 * @description Detects usage of `dict.update(key=val)` to insert or overwrite entries in a dictionary, including reflective updates with keyword arguments or dynamic unpacking.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/dict-update
 */

 import python
 import shared.SetOp::ClassPollutionSetOp
 
 from Call c
 where isSetitemUpdateCall(_, c)
 select c, "#7 dict.update(key=val)"
 