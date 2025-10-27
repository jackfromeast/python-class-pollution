import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.Concepts
import shared.ExportedAPI

module ClassPollutionLibrarySource {
  /**
   * Library sources are those that come from exposed functions in imported libraries.
   * 
   * @param source
   * @return true if the source is a remote source
   */
  predicate isLibrarySource(DataFlow::Node source) {
    exists(ExposedFunction func | func.getAnArg() = source.asExpr())
  }

  class ExposedFunction extends Function {
    ExposedFunction() {
      ExportedAPI::findAllImportStat(_, _, this, _)
    }
  }
}