import python 
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking

module Debugging {

predicate restrictedByFunctionName(DataFlow::Node node, string functionName) {
  node.getScope().getName() = functionName
}

}