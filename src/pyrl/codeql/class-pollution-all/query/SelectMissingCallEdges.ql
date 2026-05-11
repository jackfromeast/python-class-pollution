/**
 * @name Select Missing Call Edges
 * @description The query selects all the missing call edges
 * @kind problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-polliution/select-missing-call-edges
 * @tags security
 *       external/cwe/cwe-915
 * @precision high
 */

 import python
 import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.internal.DataFlowDispatch
import semmle.python.ApiGraphs

 predicate resolvedCall(CallNode call, Function callable) {
  exists(DataFlowCallable dfCallable, DataFlowCall dfCall |
    dfCallable.getScope() = callable and
    dfCall.getNode() = call and
    dfCallable = viableCallable(dfCall)
  )
}

 predicate selectCallNode(CallNode callNode) {
    not exists (Function func | resolvedCall(callNode, func))
 }

from CallNode callNode
select callNode, "Count AST nodes: " + count(callNode)
