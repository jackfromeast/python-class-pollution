/**
 * @name #6 dict.setdefault(key, val)
 * @description Detects usage of `dict.setdefault(key, val)` for reflective key insertion, which sets a default value if the key is not already present.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/dict-setdefault
 */

 import python
 import shared.SetOp::ClassPollutionSetOp
 
 from Call c
 where isSetitemSetDefaultCall(_, _, _, c)
 select c, "#6 dict.setdefault(key, val)"
 