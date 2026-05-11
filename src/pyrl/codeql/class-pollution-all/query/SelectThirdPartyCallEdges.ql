/**
 * @name Select Third Party Call Edges
 * @description The query selects all the third party call edges
 * @kind problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-polliution/select-third-party-call-edges
 * @tags security
 *       external/cwe/cwe-915
 * @precision high
 */

 import python
 import semmle.python.ApiGraphs


from CallNode callNode