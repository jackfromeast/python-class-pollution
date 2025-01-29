import python
import shared.Utils::ClassPolltionUtils
import shared.SetOp::ClassPollutionSetOp
import semmle.python.dataflow.new.DataFlow

module ClassPollutionSmartSetting {


/**
 * @description
 * ----------------------
 * Find all the seemless-setting functions that has both `obj[key] = val` and `setattr(obj, key, val)` in the same function body.
 * 
 * @note
 * ----------------------
 * This only find the function with both `obj[key] = val` and `setattr(obj, key, val)` in the same function body.
 * 
 * 
 * @example
 * ----------------------
 * def base_set(obj, key, value, allow_override=True):
 *  if isinstance(obj, dict):
 *   if allow_override or key not in obj:
 *    obj[key] = value
 *  elif (allow_override or not hasattr(obj, key)) and obj is not None:
 *    setattr(obj, key, value)
 */
predicate isSmartSettingFuncLocal(Function func, ControlFlowNode setItemNode, ControlFlowNode setattrNode) {
  exists (
    Expr obj1, Expr key1, Expr val1,
    Expr obj2, Expr key2, Expr val2 |
    isSetItemExpr(obj1, key1, val1, setItemNode) and
    isSetAttrExpr(obj2, key2, val2, setattrNode) and
    setItemNode.getScope() = func.getEvaluatingScope() and
    setattrNode.getScope() = func.getEvaluatingScope() and
    extendExprRefersTo(obj1, obj2) and
    extendExprRefersTo(key1, key2) and 
    extendExprRefersTo(val1, val2)
  )
}
}


