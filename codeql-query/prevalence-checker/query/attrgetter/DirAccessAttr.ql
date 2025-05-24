/**
 * @name #6 dir(obj)[index]
 * @description Detects attribute access patterns using `dir(obj)[index]` to retrieve attribute names reflectively, including indirect forms via assigned getter functions or intermediate variables.
 * @kind problem
 * @problem.severity warning
 * @id py/prevalence-checker/dir-access-attr
 */

 import python
 import shared.GetOp::ClassPollutionGetOp
 
 from Subscript s
 where
   isGetAttrThroughDirSubscript(_, _, s)
 select s, "#6 dir(obj)[index]"
 