#!/usr/bin/env python3
"""
@description
---------------------
This script contains the useful functions to find the pollutables reflectively during runtime.

import polluter as pl
po = new pl.Pollutable(obj, max_layer=1, lookup_type="getAttr")
"""
import inspect
import logging
import re
from .utils import get_type, get_name_info, is_instance, is_c_wrapper, is_from_standard_library, is_primitive, is_c_written, support_getField_op, is_callable

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s'
)

class Pollutable:
  def __init__(self, target, max_layer=3, lookup_type="getAttr"):
    """
    @description
    ---------------------
    The class to represent the pollutable object.

    @params target: The object to pollute.
    @params max_layer: The maximum layer to search for pollutables.
    @params lookup_type: The type of pollutables to find. Default is "getAttr" and alternative is "getBoth".
    """ 
    self.target = target
    self.max_layer = max_layer
    self.lookup_type = lookup_type

    self.visited = set()
    self.summary = self.search(max_layer)
  
  def search(self, max_layer=-1):
    """
    @description
    ---------------------
    Find all the pollutables in the given object with logging support.

    @params max_layer: The maximum layer to search for pollutables.
    """
    if max_layer == -1:
      max_layer = self.max_layer

    logging.debug(f"Starting find_all_pollutables. Type: {self.lookup_type}, Layer: {0}, Max Layer: {max_layer}")

    def lookup_getattr(obj, name):
      try:
        ret = getattr(obj, name)
        logging.debug(f"Accessed attribute: {name}")
        return (ret, 'attr')
      except AttributeError as e:
        logging.warning(f"Could not access attribute '{name}': {str(e)}")
        return None

    def lookup_getboth(obj, name):
      if hasattr(obj, '__getitem__'):
        try:
          ret = obj[name]
          logging.debug(f"Accessed item: {name}")
          return (ret, 'item')
        except (KeyError, IndexError, TypeError, AttributeError) as e:
          logging.debug(f"Failed to access item '{name}': {str(e)}")
          pass

      try:
        ret = getattr(obj, name)
        logging.debug(f"Accessed attribute: {name}")
        return (ret, 'attr')
      except AttributeError as e:
        logging.debug(f"Could not access attribute or item '{name}': {str(e)}")
        return None
      
    if self.lookup_type == "getAttr":
      logging.info("Using 'getAttr' method to find pollutables.")
      self.summary = self.find_all_pollutables(self.target, 0, max_layer, False, lookup_getattr, '')
    elif self.lookup_type == "getBoth":
      logging.info("Using 'getBoth' method to find pollutables.")
      self.summary = self.find_all_pollutables(self.target, 0, max_layer, False, lookup_getboth, '')
    else:
      logging.error(f"Unknown type specified: {self.lookup_type}")
      raise Exception(f"Unknown type: {self.lookup_type}")

    return self.summary
  
  def find_all_pollutables(self, obj, layer=0, max_layer=1, callable_only=False, lookup_func=None, parent_full_path=''):
    """Find all pollutables in the given object using getattr recursively, logging module names."""
    logging.debug(f"Entering layer {layer}. Object type: {type(obj)}")
    
    pollutables = {}
    if layer >= max_layer:
      logging.debug(f"Reached maximum layer ({max_layer}). Stopping recursion.")
      return pollutables

    obj_id = id(obj)
    if obj_id in self.visited:
      return pollutables
    else:
      self.visited.add(obj_id)
    
    attributes_to_be_checked = dir(obj) + ["__base__", "__bases__"]

    for name in attributes_to_be_checked:
      if lookup_func:
        result = lookup_func(obj, name)
        if not result:
          continue
        value, access_type = result
      else:
        continue
      
      if callable_only and not callable(value):
        logging.debug(f"Skipping non-callable attribute: {name}")
        continue
      
      # Build current_full_path based on access_type and parent_full_path
      if access_type == 'attr':
        if parent_full_path:
          current_full_path = f"{parent_full_path}.{name}"
        else:
          current_full_path = name
      elif access_type == 'item':
        current_full_path = f'{parent_full_path}["{name}"]'
      else:
        continue
      
      pollutables[current_full_path] = self.summerize_value(value)

      # Decide whether to recurse into its attributes
      # If the value is a module, stop searching
      # If the value can holds user-defined attributes, continue searching
      # If the value is a class, class instance, callable, continue searching
      # If the value is a string, number, boolean, stop searching
      type_info = get_type(value)
      continue_search_flag = (
        layer < max_layer and
        not is_c_wrapper(value) and
        not is_primitive(type_info)
      )

      if continue_search_flag:
        logging.debug(f"Recursing into attribute: {current_full_path} at layer {layer + 1}")
        sub_pollutables = self.find_all_pollutables(
          value, layer + 1, max_layer, callable_only, lookup_func, current_full_path
        )
        pollutables.update(sub_pollutables)
    
    return pollutables

  def summerize_value(self, value):
    """
    @description
    ---------------------
    Generate the summary of the value.

    For class object, the summary is (class_name, class_name, standard?, writable?)
    For class itself, the summary is ("class", class_name, standard?, writable?)

    (type, name, standard?, writable?)

    @params value: The value to summarize.
    @return: The summary of the value.
    """
    type_info = get_type(value)
    name_info = get_name_info(value)
    is_standard = is_from_standard_library(value)
    writable = is_c_written(value, type_info)
    return (type_info, name_info, is_standard, writable)

  def parse_path(self, path):
    components = []
    i = 0
    n = len(path)
    while i < n:
      if path[i] == '.' and i+1 < n and path[i+1] == '[':
        i += 1
        if path[i] == '[':
          if i+1 < n and path[i+1] == '"':
            j = path.find('"]', i+2)
            if j == -1:
              raise ValueError(f"Invalid path: unterminated [\" at position {i}")
            name = path[i+2:j]
            components.append(('item', name))
            i = j + 2
          else:
            raise ValueError(f"Invalid item access at position {i}")
        else:
          raise ValueError(f"Unexpected character '{path[i]}' at position {i}")
      elif path[i] == '.':
        j = i + 1
        while j < n and (path[j].isalnum() or path[j] == '_'):
          j += 1
        attr = path[i+1:j]
        components.append(('attr', attr))
        i = j
      elif path[i] == '[':
        if i+1 < n and path[i+1] == '"':
          j = path.find('"]', i+2)
          if j == -1:
            raise ValueError(f"Invalid path: unterminated [\" at position {i}")
          name = path[i+2:j]
          components.append(('item', name))
          i = j + 2
        else:
          raise ValueError(f"Unsupported item access syntax at position {i}")
      else:
        j = i
        while j < n and (path[j].isalnum() or path[j] == '_'):
          j += 1
        attr = path[i:j]
        components.append(('attr', attr))
        i = j
    return components

  def find(self, path):
    """
    Find the object based on the path.

    @params path: The path to find the object.
    @return obj: The object found based on the path.
    """
    components = self.parse_path(path)
    obj = self.target
    for access_type, name in components:
      if access_type == 'attr':
        obj = getattr(obj, name)
      elif access_type == 'item':
        obj = obj[name]
      else:
        raise ValueError(f"Unknown access type: {access_type}")
    return obj
  
  def select(self, query):
    """
    Select the object based on the query.

    @params query: The query to select the object.
    Supported queries:
    - "type=module" -> Select the modules.
    - "type=callable" -> Select the callables.
    - "type=method" -> Select the methods.
    - "type=function" -> Select the functions.
    - "type=noncallable" -> Select the non-callable attributes.
    - "type=dict" -> Select the dictionaries.
    - "type=class" -> Select the classes.
    - "type=dataclass" -> Select the dataclasses.
    - "type=string" -> Select the strings.
    - "type=number" -> Select the numbers.
    - "type=boolean" -> Select the booleans.
    - "builtin=no" -> Select the user-defined objects.
    - "name=???" -> Select the object with __name__=???.
    - Combined queries like "type=class&builtin=no" -> Select user-defined classes.

    @return selected: A dictionary of selected paths and their values.
    """
    selected = {}
    query_pairs = [q.split('=') for q in query.split('&')]
    
    for path, value in self.summary.items():
      type_info, name_info, is_standard, writable = value
      match = True
  
      for key, q_value in query_pairs:
        if key == 'type':
          if not self._match_type(q_value, type_info, value):
            match = False
            break
        elif key == 'builtin':
          if not self._match_builtin(q_value, is_standard):
            match = False
            break
        elif key == 'name':
          if not self._match_name(name_info, type_info, q_value):
            match = False
            break
        else:
          match = False
          break
  
      if match:
        selected[path] = value
    
    return selected

  def select_by_func(self, func):
    """
    Select the object based on the function.

    @params func: The function to select the object.
    @return selected: A dictionary of selected paths and their values.
    """
    selected = {}
    for path, value in self.summary.items():
      type_info, name_info, is_standard, writable = value
      if func(type_info, name_info, is_standard, writable):
        selected[path] = value
    return selected

  def _match_name(self, name_info, type_info, match_name):
    """Handle name-based matching"""
    return name_info == match_name

  def _match_type(self, q_value, type_info, full_value):
    """Handle type-based matching"""
    direct_types = {
      'module': 'module',
      'function': 'function',
      'OrderedDict': 'OrderedDict',
      'defaultdict': 'defaultdict',
      'deque': 'deque',
      'Counter': 'Counter',
      'ChainMap': 'ChainMap',
      'UserDict': 'UserDict',
      'UserList': 'UserList',
      'UserString': 'UserString',
      'class': 'class',
      'string': 'str',
      'boolean': 'bool'
    }
    
    if q_value in direct_types:
      return type_info == direct_types[q_value]
    
    if q_value == 'callable':
      return is_callable(type_info)
    if q_value == 'noncallable':
      return not is_callable(type_info)
    if q_value == 'method':
      return type_info in {"method", "builtin_function_or_method", "method-wrapper"}
    if q_value == 'number':
      return type_info in {"int", "float", "complex"}
    if q_value == 'dataclass':
      return hasattr(full_value[0], '__dataclass_fields__')
    if q_value == 'object':
      return is_instance(type_info)
    if q_value == 'dict':
      return support_getField_op(type_info) and type_info != 'str'
    return False

  def _match_builtin(self, q_value, is_standard):
    if q_value == 'yes':
      return is_standard
    if q_value == 'no':
      return not is_standard
    return False