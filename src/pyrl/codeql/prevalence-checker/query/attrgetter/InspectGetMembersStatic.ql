/**
 * @name #10 inspect.getmembers_static(obj)
 * @description Detects usage of `inspect.getmembers_static(obj)` to retrieve attribute name–value pairs without triggering dynamic lookup or invoking descriptors.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/inspect-getmembers-static
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 
 from Call c
 where isGetMembersStaticThroughInspect(_, c)
 select c, "#10 inspect.getmembers_static(obj)"
 