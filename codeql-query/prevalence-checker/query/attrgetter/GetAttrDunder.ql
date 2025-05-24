/**
 * @name #2 obj.__getattribute__(name)
 * @description Detects usage of the built-in `__getattribute__` method directly on an object, as in `obj.__getattribute__(name)`, excluding `object.__getattribute__(obj, name)`.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/getattr-dunder
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 
 from Call c
 where isGetattributeCall(_, _, c) and not isObjectGetattributeCall(_, _, c)
 select c, "#2 obj.__getattribute__(name)"
 