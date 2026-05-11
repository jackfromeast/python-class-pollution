/**
 * @name Dependency Class Pollution API Source
 * @description The query identifies the callable (method, function) whose return value should be considered as a
 *              class pollution source.
 * @kind problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-polliution/dependency-api-source
 * @tags security
 *       external/cwe/cwe-915
 * @precision high
 */

import python
import dependency.ClassPollutionSource::ClassPollutionSourceDependencyModel
import shared.Utils::ClassPolltionUtils

from Function func, Module mod, string moduleName, string className, string functionName, string filePath, string fullPath
where 
  isClassPollutionSourceAPI(func, _, _) and
  func.getName() = functionName and
  if func.isMethod() then
    exists(Class cls |
      methodImportPath(func, mod, cls) and cls.getName() = className and mod.toString() = moduleName and mod.getPath().toString() = filePath and
      fullPath = "- Method: " + functionName + "\n- Class: " + className + "\n- Module: " + moduleName + "\n- File: " + filePath
    )
  else
    functionImportPath(func, mod) and mod.toString() = moduleName and className = "" and mod.getPath().toString() = filePath and
    fullPath = "- Function: " + functionName + "\n- Module: " + moduleName + "\n- File: " + filePath
select func, "The callable $@ is a class pollution source API in $@. \n" + fullPath, func, functionName, mod, moduleName
