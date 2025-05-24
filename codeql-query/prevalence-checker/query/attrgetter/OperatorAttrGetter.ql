/**
 * @name #5 operator.attrgetter(name)(obj)
 * @description Detects usage of `operator.attrgetter(name)(obj)` to reflectively access an attribute, including equivalent indirect invocations via assigned getter functions or intermediate bindings.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/operator-attrgetter-call
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 
 from Call c
 where isGetAttrThroughOperatorAttrGetter(_, _, c)
 select c, "#5 operator.attrgetter(name)(obj)"
 