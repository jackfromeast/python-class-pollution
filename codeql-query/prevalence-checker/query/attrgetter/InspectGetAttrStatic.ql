/**
 * @name #4 inspect.getattr_static(obj, name)
 * @description Detects usage of `inspect.getattr_static(obj, name)` to access attributes statically—bypassing dynamic lookup via descriptors and avoiding invocation of `__get__`, `__getattribute__`, or `__getattr__`.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/inspect-getattr-static
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 
 from Call c
 where isGetAttrThroughInspect(_, _, c)
 select c, "#4 inspect.getattr_static(obj, name)"
 