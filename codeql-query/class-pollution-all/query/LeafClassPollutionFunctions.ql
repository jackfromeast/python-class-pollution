/**
 * @name None Shared Class Pollution Functions
 * @description This query finds the functions that are not shared in the call graph of class pollution functions.
 * @kind problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-polliution/leaf-class-pollution-functions
 * @tags security
 *       external/cwe/cwe-915
 * @precision high
 */

 import python
 import vuln.ClassPollutingAssignLib::ClassPollutionAssignment
 import semmle.python.dataflow.new.DataFlow
 import shared.Utils::ClassPolltionUtils
 import shared.types.PossibleGetOpNode
 import shared.Message::ClassPollutionMessage
 import shared.Debug::Debugging
 
 module Flow = TrackingClassPollutionKeyToAssignmentFlow;
 
 class ClassPollutionFunction extends Function {
  string vulnType;

  ClassPollutionFunction() {
    exists (DataFlow::Node sourceParamKeyNode |
      (
        isClassPollutedAssignmentSetAttrGetAttrStrict(sourceParamKeyNode, _, _, _, _, _, vulnType, _, _) or
        isClassPollutedAssignmentSetItemGetAttrStrict(sourceParamKeyNode, _, _, _, _, _, vulnType, _, _) or
        isClassPollutedAssignmentSetBothGetAttrStrict(sourceParamKeyNode, _, _, _, _, _, vulnType, _, _) or
        isClassPollutedAssignmentSetItemGetBothStrict(sourceParamKeyNode, _, _, _, _, _, vulnType, _, _, _) or
        isClassPollutedAssignmentSetAttrGetBothStrict(sourceParamKeyNode, _, _, _, _, _, vulnType, _, _, _) or
        isClassPollutedAssignmentSetBothGetBothStrict(sourceParamKeyNode, _, _, _, _, _, vulnType, _, _, _) 
      )
      and
      this.getAnArg() = sourceParamKeyNode.asExpr()
    )
  }

  string getVulnType() { result = vulnType }
 }

 predicate noneSharedClassPollutionFunction(ClassPollutionFunction func) {
  not exists(ClassPollutionFunction cpf | hasCallerCalleeRelationship(func, cpf) and func != cpf)
 }

 /**
  * Returns true if there is a (possibly multi-hop) call path from `caller` to `callee`.
  */
 predicate hasCallerCalleeRelationship(ClassPollutionFunction caller, ClassPollutionFunction callee) {
  caller = callee or
  exists(ClassPollutionFunction mid |
    hasDirectCall(caller, mid) and
    hasCallerCalleeRelationship(mid, callee)
  )
}

/**
 * Returns true if `caller` directly calls `callee`.
 */
predicate hasDirectCall(ClassPollutionFunction caller, ClassPollutionFunction callee) {
  exists(Call call |
    call.getScope() = caller and
    callee.getFunctionObject().getACall().getNode() = call
  )
}

 from ClassPollutionFunction func, string vulnType, string msg
 where
  noneSharedClassPollutionFunction(func) and
  func.getVulnType() = vulnType and 
  msg = "This function $@ with type:" + vulnType + " has no caller-callee relationships with other functions."
 select func, msg, func, func.toString()