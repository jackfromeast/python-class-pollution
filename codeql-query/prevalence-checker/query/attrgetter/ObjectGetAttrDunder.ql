/**
 * @name #3 object.__getattribute__(obj, name)
 * @description Detects usage of the built-in `object.__getattribute__(obj, name)` pattern for retrieving attributes at the base-object level.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/object-getattr-dunder
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 
 from Call c
 where isObjectGetattributeCall(_, _, c)
 select c, "#3 object.__getattribute__(obj, name)"
 