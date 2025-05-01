/**
 * @name Most Commonly Shared Class Pollution Functions
 * @description This query finds the functions that are most commonly shared in the call graph of class pollution functions.
 * @kind problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-polliution/shared-class-pollution-functions
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
      isClassPollutedAssignmentSetAttrGetAttrStrict(sourceParamKeyNode, _, _, _, _, _, vulnType, _, _) and
      this.getAnArg() = sourceParamKeyNode.asExpr()
    )
  }

  string getVulnType() { result = vulnType }
 }

 predicate callerNumberPerClassPollutionFunction(int number, ClassPollutionFunction func){
  number = count(ClassPollutionFunction cpf | hasCallerCalleeRelationship(cpf, func) | cpf)
 }

 int maxCallerNumber() {
  result = max(int n |
    exists(ClassPollutionFunction f | callerNumberPerClassPollutionFunction(n, f))
  )
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

 from int number, ClassPollutionFunction func, string vulnType, string msg
 where
   callerNumberPerClassPollutionFunction(number, func) and
   number = maxCallerNumber() and
   func.getVulnType() = vulnType and 
   msg = "This function $@ with type:" + vulnType + " has the largest number of caller-callee relationships with " + number + " other functions."
 select func, msg, func, func.toString()