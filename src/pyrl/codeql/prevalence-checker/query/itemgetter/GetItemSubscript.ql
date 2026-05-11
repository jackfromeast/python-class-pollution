/**
 * @name #11 dict[key]
 * @description Detects usage of the subscript syntax `dict[key]` for reflective dictionary access, excluding assignments (i.e., treated only as a getter).
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/getitem-subscript
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 import shared.SetOp::ClassPollutionSetOp
 
 from Subscript s
 where isSubscriptOp(_, _, s) and not isAssigned(s)
 select s, "#11 dict[key]"
 
 predicate isAssigned(Expr obj) {
   exists(Assign a | a.getATarget() = obj)
 }
 