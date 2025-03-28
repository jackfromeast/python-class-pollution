import python
import vuln.ClassPollutingAssignLib::ClassPollutionAssignment
import semmle.python.dataflow.new.DataFlow
import shared.Utils::ClassPolltionUtils
import shared.Debug::Debugging


class ClassPollutionFunction extends Function {
  DataFlow::Node sourceParamKeyNode;
  DataFlow::Node sourceParamObjNode;
  string vulnType;

  ClassPollutionFunction() {
    this.getAnArg() = sourceParamKeyNode.asExpr() and
    isClassPollutedAssignmentSetItemGetBothStrict(sourceParamKeyNode, sourceParamObjNode, _, _, _, _, vulnType, _, _)
  }
}

predicate findMostSharedClassPollutionFunction(ClassPollutionFunction cpFunc) {
  not exists (ClassPollutionFunction otherCpFunc |
    getAllImmediateCallee(cpFunc) = otherCpFunc
  )
}

Function getAllImmediateCallee(Function caller) {
  exists ( CallNode callNode, Function middleFunc |
    result.getFunctionObject().getACall() = callNode and
    callNode.getScope() = caller.getEvaluatingScope()
    or
    middleFunc = getAllImmediateCallee(caller) and
    result.getFunctionObject().getACall() = callNode and
    callNode.getScope() = middleFunc.getEvaluatingScope()
  )
}