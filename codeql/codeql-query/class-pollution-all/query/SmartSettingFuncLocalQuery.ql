/**
 * @name Class Pollution Implication #2: Smart Setting Function (Single Function)
 * @description The query finds the function that has both `obj[key] = val` and `setattr(obj, key, val)` in the same function body. 
 *              Additional, the obj and key should refer to the same variable respectively.
 * @kind problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-polliution/smart-getting-func-single
 * @tags security
 *       external/cwe/cwe-915
 * @precision high
 */

import python
import vuln.SmartSettingFuncLib::ClassPollutionSmartSetting

from Function func, ControlFlowNode setItemNode, ControlFlowNode setattrNode
where isSmartSettingFuncLocal(func, setItemNode, setattrNode)
select func, setItemNode, setattrNode, "The function has both setItem and setAttr operation in its body."
