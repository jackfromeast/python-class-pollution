/**
 * @name #14 dict.__getitem__(key)
 * @description Detects usage of the `dict.__getitem__(key)` method for reflective dictionary access, excluding cases where it is invoked through `operator.__getitem__`.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/getitem-dunder
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 
 from Call c
 where isGetItemDunderCall(_, _, c) and not isGetItemDunderThroughOperator(_, _, c)
 select c, "#14 dict.__getitem__(key)"
 