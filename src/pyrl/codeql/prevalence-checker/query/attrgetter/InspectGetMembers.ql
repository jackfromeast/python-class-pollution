/**
 * @name #9 inspect.getmembers(obj)
 * @description Detects usage of `inspect.getmembers(obj)` to retrieve a list of attribute name–value pairs from an object using dynamic introspection.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/inspect-getmembers
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 
 from Call c
 where isGetMembersThroughInspect(_, c)
 select c, "#9 inspect.getmembers(obj)"
 