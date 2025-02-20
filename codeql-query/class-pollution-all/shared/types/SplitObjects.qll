import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.ApiGraphs


class SplitObjects extends DataFlow::Node {
  SplitObjects(){
    exists(MethodCallNode call|
      call.getMethodName() = "split" and
      this.asExpr() = call.getArg(0).asExpr()
    ) or 
    exists( API::CallNode call |
      (
        API::moduleImport("re").getMember("split").getACall() = call or
        API::moduleImport("re").getMember("findall").getACall() = call or
        API::moduleImport("regex").getMember("split").getACall() = call // https://pypi.org/project/regex/
      ) and
      call.asCfgNode().(CallNode).getArg(1).getNode() = this.asExpr()
    )
  }
}
