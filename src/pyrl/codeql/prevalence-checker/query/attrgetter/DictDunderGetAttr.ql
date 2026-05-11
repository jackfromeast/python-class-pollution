/**
 * @name #8 obj.__dict__[name] or obj.__dict__.get(name)
 * @description Detects attribute access through the object's `__dict__` mapping, including both `obj.__dict__[name]` and `obj.__dict__.get(name)`, as well as indirect variants via reflective getters such as `operator.getitem`, `attrgetter`, or variable indirection.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/dict-dunder-get-attr
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 
 from Expr e, Call c, Subscript s
 where
   (c = e and isGetAttrThroughObjectDunderDictCall(_, _, c)) or
   (s = e and isGetAttrThroughObjectDunderDictSubscript(_, _, s))
 select e, "#8 obj.__dict__[name] or obj.__dict__.get(name)"
 