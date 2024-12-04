import python
import shared.Utils::ClassPolltionUtils
import semmle.python.dataflow.new.DataFlow

module ClassPollutionSetOp {

  /**
 * @description
 * ----------------------
 * Check if the expression represents an assignment like `obj[key] = val`.
 * 
 */
predicate isSubscriptAssignment(Expr obj, Expr key, Expr val, Assign a) {
  exists(Subscript subscript |
    subscript = a.getATarget() and
    subscript.getObject() = obj and
    subscript.getIndex() = key and
    a.getValue() = val
  )
}

/**
 * @description
 * ----------------------
 * Check if the expression represents a dynamic assignment like `setattr(obj, key, val)`.
 * 
 */
predicate isSetattrCall(Expr obj, Expr key, Expr val, Call call) {
  exists (
    Name name |
    name.getId() = "setattr" and
    call.getFunc() = name
  ) and
  call.getArg(0) = obj and
  call.getArg(1) = key and
  call.getArg(2) = val
}

}