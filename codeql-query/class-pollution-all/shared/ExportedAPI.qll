import python 

module ExportedAPI {

predicate findAllPackages(Module package){
  exists(Module mod | mod.getPackage() = package)
}

predicate findAllInitModules(Module initMod, PackageObject packageObject){
  exists(ModuleObject moduleObject |
    moduleObject.getModule() = initMod and
    packageObject.getInitModule() = moduleObject
  )
}

class InitModule extends Module {
  PackageObject packageObject;

  InitModule() {
    exists(ModuleObject moduleObject |
      moduleObject.getModule() = this and
      packageObject.getInitModule() = moduleObject
    )
  }
}

/**
 * Returns the fully qualified importable name for a callable (module, class, or function).
 */
private predicate importableNameForCallable(Function callable, string importableName) {
  // Module file
  exists(ModuleObject m | callable.getEnclosingModule() = m.getModule() |
    importableName = m.getName()
  ) or
  // Class method
  exists(Class cls | callable.getEnclosingScope() = cls |
    importableName = cls.getEnclosingModule().getName() + "." + cls.getName() and
    cls.isTopLevel()
  ) or
  // Module-level function (again, for function)
  exists(Function func | callable = func |
    importableName = func.getEnclosingModule().getName() + "." + func.getName() and
    func.isTopLevel()
  )
}

/**
 * Find all import statements and their resolved callable objects.
 */
predicate findAllImportModule(InitModule initMod, string importedModName, Function callable, string callableName) {
  initMod.getAnImportedModuleName() = importedModName and

  // If importedModName is a module, then select all the callable objects in the module
  // If importedModName is a class, then select all the methods in the class
  // If importedModName is a function, then select the function object
  // If importedModName is a package, then find all the callable objects in the package
  // Ignore it as its init module is already checked
  importableNameForCallable(callable, callableName) and

  // Handle the namespace package, e.g., google.generativeai
  importedModName.matches("%" + callableName) and 
  callable.getName().prefix(1) != "_" and
  not (callable.getName().matches("%listcomp") or callable.getName().matches("%dictcomp"))
}

predicate findImportMod(ImportingStmt importStmt, string importedModName){
  importStmt.getAnImportedModuleName() = importedModName
}

predicate findFunctionWithName(Function func, string name){
  func.getEnclosingScope().getName() + "." + func.getName() = name
}

predicate findAllImportStat(ImportingStmt importStmt, string importedModName, Function callable, string callableName) {
  exists(InitModule initMod | importStmt.getEnclosingModule() = initMod ) and
  importStmt.getAnImportedModuleName() = importedModName and

  // If importedModName is a module, then select all the callable objects in the module
  // If importedModName is a class, then select all the methods in the class
  // If importedModName is a function, then select the function object
  // If importedModName is a package, then find all the callable objects in the package
  // Ignore it as its init module is already checked
  importableNameForCallable(callable, callableName) and

  // Handle the namespace package, e.g., google.generativeai
  importedModName.matches("%" + callableName) and 
  callable.getName().prefix(1) != "_" and
  not (callable.getName().matches("%listcomp") or callable.getName().matches("%dictcomp"))
}

// Check the pointed AST node of the importedMod name
predicate checkImportedCallable(ModuleObject moduleObject, string name, Object obj){
  moduleObject.attr(name) = obj
}

predicate checkImportedCallableFromImportStmt(PackageObject packageObject, string name, Object obj){
  packageObject.getAttribute(name) = obj
}

}
