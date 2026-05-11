/**
 * @name Select All Type Sources
 * @description Find all the type sources in the codebase
 * @kind problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-pollution/select-remote-sources
 * @tags security
 *       external/cwe/cwe-915
 * @precision low
 */

 import python
 import semmle.python.dataflow.new.DataFlow
 import shared.sources.library::ClassPollutionLibrarySource
 import shared.sources.local::ClassPollutionLocalSource
 import shared.sources.remote::ClassPollutionRemoteSource

 predicate isTypeSource(DataFlow::Node source, string sourceType) {
   isRemoteSource(source) and sourceType = "remote"
 }


from Expr source, string sourceType
where
  exists (DataFlow::Node sourceNode | sourceNode.asExpr() = source and isTypeSource(sourceNode, sourceType))
select source, sourceType, "Source of type $@: $@", sourceType, source, source.toString()