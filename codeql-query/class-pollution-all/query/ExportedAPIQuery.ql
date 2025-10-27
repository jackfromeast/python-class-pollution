/**
 * @name Exported API Query
 * @description Find all the exported APIs in the codebase
 * @kind problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-polliution/exported-api
 * @tags security
 *       external/cwe/cwe-915
 * @precision low
 */
import python
import shared.ExportedAPI::ExportedAPI

from ImportingStmt importStmt, string importedModName, Function callable, string callableName
where 
  findAllImportStat(importStmt, importedModName, callable, callableName)
select callable, "Exported API: $@, imported at $@", callable, callableName, importStmt, importStmt.toString()