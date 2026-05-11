/**
 * @name #13 dict.pop(key)
 * @description Detects usage of `dict.pop(key)` to access and remove dictionary entries reflectively, including indirect calls through assigned variables or wrapper functions.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/dict-pop
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 
 from Call c
 where isDictPopCall(_, _, c)
 select c, "#13 dict.pop(key)"
 