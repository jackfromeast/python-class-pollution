import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.internal.DataFlowPublic
import semmle.python.dataflow.new.TaintTracking
import vuln.SmartSettingFuncLib::ClassPollutionSmartSetting
import shared.Utils::ClassPolltionUtils
import shared.flowsteps.AdditionalFlowStep::ClassPollutionAdditionalFlowStep
import shared.flowsteps.AdditionalFlowStepCustom::ClassPollutionAdditionalFlowStepCustom
import shared.flowsteps.AdditionalFlowStepOperator::ClassPollutionAdditionalFlowStepOperator

/**
 * @description
 * ----------------------
 * Holds the dataflow nodes may hold PrototypeObject flow state in the taint tracking.
 *
 */
class PossibleGetOpNode extends DataFlow::Node {
  PossibleGetOpNode() {
    // Possible `toNode` in predicates enumeratedKeyToPrototypeObjectFlowStep and initFuncParamterToPrototypeObjectFlowStep
    // Need to be sync with those two predicates
    additionalFlowStepGetAttrReverse(_, this) or
    additionalFlowStepGetItemReverse(_, this) or
    additionalFlowStepThroughCustomLibHoldPrototypeObject(_, this) or
    additionalFlowStepThroughGetAttrOperator(_, this) or
    additionalFlowStepThroughGetItemOperator(_, this) or
    exists (Name funcName , Call call|
      funcName.getId().matches("eval") and
      call.getFunc() = funcName and
      call = this.asExpr()
    )
  }
}