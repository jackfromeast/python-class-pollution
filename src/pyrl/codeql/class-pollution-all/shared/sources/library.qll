import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.Concepts
import shared.ExportedAPI

module ClassPollutionLibrarySource {
  /**
   * Library sources are parameters of functions that an attacker can plausibly
   * reach from outside the package.
   *
   * Two forms qualify:
   *   1. Parameters of `ExposedFunction`: top-level callables that are explicitly
   *      re-exported via an `__init__.py` import (the strict definition).
   *   2. Parameters of `ImportableFunction`: module-level functions in a non-private
   *      module path. A leading underscore on a *function* name does NOT disqualify
   *      it — many real-world cp-pollution helpers (`_set_value`, `_set_nested_attr`,
   *      `_modify_value`) are conventionally underscored but are reachable from
   *      siblings inside the same package; a caller can still import them via
   *      `from package.module import _set_value` or hit them through a public wrapper.
   *      We exclude functions whose enclosing *module path* contains a
   *      `_<segment>` (e.g. `pkg._internal.foo`), because those represent genuinely
   *      private subpackages.
   *
   * @param source
   * @return true if the source is a library source
   */
  predicate isLibrarySource(DataFlow::Node source) {
    exists(ExposedFunction func | func.getAnArg() = source.asExpr())
    or
    exists(ImportableFunction func | func.getAnArg() = source.asExpr())
  }

  class ExposedFunction extends Function {
    ExposedFunction() {
      ExportedAPI::findAllImportStat(_, _, this, _)
    }
  }

  /**
   * A function defined at module level in a non-private module path, where every
   * package segment is non-underscore (so e.g. `pkg.utils._set_value` qualifies but
   * `pkg._internal.foo` does not). Methods on classes also qualify when the class
   * itself sits in a non-private module. These are the functions an attacker can
   * conceivably reach through an `import` even without an `__init__` re-export.
   */
  class ImportableFunction extends Function {
    ImportableFunction() {
      (this.isTopLevel() or exists(Class cls | this.getEnclosingScope() = cls and cls.isTopLevel())) and
      not (
        exists(string segment |
          segment = this.getEnclosingModule().getName().splitAt(".") and
          segment.matches("\\_%")
        )
      ) and
      // Exclude listcomp/dictcomp/genexpr synthetic functions.
      not this.getName().matches("%listcomp") and
      not this.getName().matches("%dictcomp") and
      not this.getName().matches("%genexpr") and
      // Exclude obvious test helpers — too noisy for a recall benchmark.
      not this.getEnclosingModule().getName().matches("%test_%") and
      not this.getEnclosingModule().getName().matches("%tests.%") and
      not this.getEnclosingModule().getName().matches("test_%") and
      not this.getEnclosingModule().getName().matches("tests.%")
    }
  }
}