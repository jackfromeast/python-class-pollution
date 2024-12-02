/**
 * @name Class Pollution Implication #1: Smart Getting Function
 * @description The query finds all the smart getting functions whose parameters are flow to both getItem and getAttr operation.
 * @kind path-problem
 * @problem.severity warning
 * @security-severity 6.1
 * @sub-severity low
 * @id py/class-polliution/smart-getting-func
 * @tags security
 *       external/cwe/cwe-915
 * @precision high
 */

import python
import SmartGettingFuncLib::ClassPollutionSmartGetting
import TrackingParamToSmartGettingOpFlow::PathGraph


from Function smartGeetingFunc,
     TrackingParamToSmartGettingOpFlow::PathNode sourceObjToItem, TrackingParamToSmartGettingOpFlow::PathNode sourceKeyToItem,
     TrackingParamToSmartGettingOpFlow::PathNode sourceObjToAttr, TrackingParamToSmartGettingOpFlow::PathNode sourceKeyToAttr,
     TrackingParamToSmartGettingOpFlow::PathNode getItemObj, TrackingParamToSmartGettingOpFlow::PathNode getItemKey,
     TrackingParamToSmartGettingOpFlow::PathNode getAttrObj, TrackingParamToSmartGettingOpFlow::PathNode getAttrKey
where 
  smartGeetingFunc.getEvaluatingScope() = sourceObjToItem.getNode().getScope() and
  smartGeetingFunc.getEvaluatingScope() = sourceKeyToItem.getNode().getScope() and
  isSmartGettingFunction_(sourceObjToItem, sourceKeyToItem, sourceObjToAttr, sourceKeyToAttr, getItemObj, getItemKey, getAttrObj, getAttrKey) and
  // Note that this is a path query, however, we have four different paths to consider.
  // Therefore, we only show the path from sourceKeyToItem to getItemKey by default.
  // Change the following line to see the other paths.
  // E.g., TrackingParamToSmartGettingOpFlow::flowPath(sourceObjToItem, getItemObj)
  TrackingParamToSmartGettingOpFlow::flowPath(sourceKeyToItem, getItemKey) 
select smartGeetingFunc, sourceKeyToItem, getItemKey, "The parameter is flow to both getItem and getAttr operation."