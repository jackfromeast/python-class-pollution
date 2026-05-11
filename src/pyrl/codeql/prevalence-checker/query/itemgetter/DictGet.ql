/**
 * @name #12 dict.get(key)
 * @description Detects usage of `dict.get(key)` to access dictionary values reflectively, including cases where the call is passed through intermediate variables or wrapper functions.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/dict-get
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 
 from Call c
 where isDictGetCall(_, _, c)
 select c, "#12 dict.get(key)"
 