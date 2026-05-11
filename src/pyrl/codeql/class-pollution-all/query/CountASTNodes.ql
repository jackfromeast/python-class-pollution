/**
 * @name Count AST nodes
 * @description The query counts all the AST nodes
 * @kind problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-polliution/count-ast-nodes
 * @tags security
 *       external/cwe/cwe-915
 * @precision high
 */

 import python

 from AstNode astNode
 select astNode, "Count AST nodes: " + count(astNode)
