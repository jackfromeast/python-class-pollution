/**
 * @name #4 obj.__dict__[name] = val
 * @description Detects assignments to `obj.__dict__[name]` as a reflective way to set object attributes, including equivalent patterns using subscripted writes to `__dict__`.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/dict-dunder-set-attr
 */

 import python
 import shared.SetOp::ClassPollutionSetOp
 
 from Assign a
 where isSetAttrThroughObjectDunderDictSubscript(_, _, _, a)
 select a, "#4 obj.__dict__[name] = val"
 