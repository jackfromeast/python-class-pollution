/**
 * @name Class Pollution Implication #1: Smart Getting Function (Single Function)
 * @description The query finds the function that has both `val = obj[key]` and `getattr(obj, key, val)` in the same function body. 
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
import vuln.SmartGettingFuncLib::ClassPollutionSmartGetting

from Function func
where isSmartGettingFuncLocal(func)
select func, "The function has both getItem and getAttr operation in its body."