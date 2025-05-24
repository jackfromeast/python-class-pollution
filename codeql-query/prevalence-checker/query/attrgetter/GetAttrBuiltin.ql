/**
 * @name #1 getattr(obj, name)
 * @description Detects usage of the built-in `getattr(obj, name)` pattern for reflective attribute access.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/getattr-builtin
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 
 from Call c
 where isDirectGetattrCall(_, _, c)
 select c, "#1 getattr(obj, name)"
 