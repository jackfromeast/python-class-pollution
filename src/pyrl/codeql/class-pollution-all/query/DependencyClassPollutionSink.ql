/**
 * @name Dependency Class Pollution API Sink
 * @description The query identifies the callable (method, function) whose arguments should be considered as
 *              class pollution sinks.
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
import dependency.ClassPollutionSink::ClassPollutionSinkDependencyModel
import shared.Utils::ClassPolltionUtils

from Function func, Module mod, string moduleName, string className, string functionName, string filePath, string fullPath, string paramInfo,
     Parameter baseParam, Parameter keyParam, Parameter valueParam, string baseParamName, string keyParamName, string valueParamName, string sinkType
where 
  isClassPollutionSinkAPI(func, baseParam, keyParam, valueParam, sinkType) and
  ( 
    if baseParam.getPosition() instanceof int
    then baseParamName = "Arg" + baseParam.getPosition().toString()
    else baseParamName = "Unknown"
  ) and
  (
    if keyParam.getPosition() instanceof int
    then keyParamName = "Arg" + keyParam.getPosition().toString()
    else keyParamName = "Unknown"
  ) and
  (
    if valueParam.getPosition() instanceof int
    then valueParamName = "Arg" + valueParam.getPosition().toString()
    else valueParamName = "Unknown"
  ) and
  paramInfo = "- Type: " + sinkType + "\n- Base: " + baseParamName + "\n- Key: " + keyParamName + "\n- Value: " + valueParamName + "\n" and
  func.getName() = functionName and
  if func.isMethod() then
    exists(Class cls | 
      methodImportPath(func, mod, cls) and cls.getName() = className and mod.toString() = moduleName and mod.getPath().toString() = filePath and
      fullPath = "- Method: " + functionName + "\n- Class: " + className + "\n- Module: " + moduleName + "\n- File: " + filePath
    )
  else
    functionImportPath(func, mod) and mod.toString() = moduleName and className = "" and mod.getPath().toString() = filePath and
    fullPath = "- Function: " + functionName + "\n- Module: " + moduleName + "\n- File: " + filePath
select func, "The callable $@ is a class pollution sink API in $@ \n" + paramInfo + fullPath, func, functionName, mod, moduleName
