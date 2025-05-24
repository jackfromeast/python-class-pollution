/**
 * @name #8 dict.__setitem__(key, val)
 * @description Detects usage of the `dict.__setitem__(key, val)` method to reflectively assign dictionary entries, excluding invocations via `operator.__setitem__`.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/dict-dunder-setitem
 */

 import python
 import shared.SetOp::ClassPollutionSetOp
 
 from Call c
 where isSetitemDunderCall(_, _, _, c) and not isSetItemDunderThroughOperator(_, _, _, c)
 select c, "#8 dict.__setitem__(key, val)"
 