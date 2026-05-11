/**
 * @name #7 vars(obj)[index] or vars(obj).get(index)
 * @description Detects attribute access via the result of `vars(obj)`, including `vars(obj)[index]`, `vars(obj).get(index)`, or equivalent indirect invocations through assigned getter functions.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/vars-access-attr
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 
 from Expr e, Call c, Subscript s
 where 
   (c = e and isGetAttrThroughVarsCall(_, _, c)) or
   (s = e and isGetAttrThroughVarsSubscript(_, _, s))
 select e, "#7 vars(obj)[index] or vars(obj).get(index)"
 