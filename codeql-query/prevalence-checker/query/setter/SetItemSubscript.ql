/**
 * @name #5 dict[key] = val
 * @description Detects subscript assignments like `dict[key] = val`, reflecting item-based value updates in dictionaries. Excludes `obj.__dict__[key] = val`-style attribute assignments.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/setitem-subscript
 */

 import python
 import shared.SetOp::ClassPollutionSetOp
 
 from Assign a
 where isSubscriptAssignment(_, _, _, a) and not isSetAttrThroughObjectDunderDictSubscript(_, _, _, a)
 select a, "#5 dict[key] = val"
 