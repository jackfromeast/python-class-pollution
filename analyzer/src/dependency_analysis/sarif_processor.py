"""
@description
---------------------
Processes the SARIF output file from CodeQL queries and generates a summary report in json format.
"""
import json
import os
import re

class SarifProcessor:
  """
  @description
  Given a sarif report, generate a summary report in json format for external API modeling.
  """
  def __init__(self):
    pass
  
  def load_sarif(self, sarif_path):
    """
    @description
    Load the SARIF file from the specified path.
    """
    with open(sarif_path, "r", encoding="utf-8") as file:
      raw_sarif = json.load(file)
    
    return raw_sarif['runs'][0]['results']

  def process(self, package_name, sarif_path, output_path, type):
    """
    @description
    Process the SARIF file and generate a summary report in json format.

    @param sarif_path: str - The path to the SARIF file.
    @param output_path: str - The path to store the summary report.
    """
    raw_results = self.load_sarif(sarif_path)
    processed_results = self.process_models(package_name, raw_results, type)

    with open(output_path, "w", encoding="utf-8") as file:
      json.dump(processed_results, file, indent=2)
    
    return processed_results
      
  def process_models(self, package_name, raw_results, type):
    """
    @description
    Process the SARIF file and generate a summary report in json format.

    @param raw_results: List - The raw results from the SARIF file.
    @return: List - A list of processed source models.
    """
    processed_results = []  # Renamed to avoid shadowing

    for result in raw_results:
        raw_message = result['message']['text']

        if type == "source":
          parsed_message = self.parse_message_source(raw_message, package_name)
          data_extension = self.generate_source_data_extension_format(parsed_message)
        elif type == "sink":
          parsed_message = self.parse_message_sink(raw_message, package_name)
          data_extension = self.generate_sink_data_extension_format(parsed_message)
        elif type == "summary":
          parsed_message = self.parse_message_summary(raw_message, package_name)
          data_extension = self.generate_summary_data_extension_format(parsed_message)

        processed_results.append({
          raw_message: raw_message,
          "package": package_name,
          "model": parsed_message,
          "data_extension": data_extension,
        })
    
    return processed_results
  
  def parse_message_summary(self, raw_message, package_name):
    """
    @description
    Parse the raw message from the SARIF file.

    E.g., 
    'The callable  taint propagation API in [Module babel.messagen- Function: values_to_compare\n- Module: Module babel.messages.catalog\n- File: /home/redacted/Desktop/python-class-pollution/tasks/test/output/robusta/dependency/output/babel/codebase/babel/messages/catalog.py'
    =>
    {
      "callable": "values_to_compare",
      "parameter": "Arg0",
      "function": "values_to_compare",
      "module": "babel.messages.catalog",
      "file": "/babel/messages/catalog.py",
      "package_name": "babel"
    }

    @param raw_message: str - The raw SARIF message.
    @param package_name: str - The package name.

    @returns: dict - Parsed summary data.
    """
    parsed_data = {}

    # Extract callable
    callable_start = raw_message.find('[') + 1
    callable_end = raw_message.find(']', callable_start)
    parsed_data['callable'] = raw_message[callable_start:callable_end]

    # Extract parameter
    param_start = raw_message.find('Parameter: ') + len('Parameter: ')
    param_end = raw_message.find('\n', param_start)
    parsed_data['parameter'] = raw_message[param_start:param_end].strip()

    # Extract function
    function_start = raw_message.find('Function: ') + len('Function: ')
    function_end = raw_message.find('\n', function_start)
    parsed_data['function'] = raw_message[function_start:function_end].strip()

    # Extract module
    module_start = raw_message.find('Module: ') + len('Module: ')
    module_end = raw_message.find('\n', module_start)
    module_name = raw_message[module_start:module_end].strip()
    parsed_data['module'] = module_name.replace('Module ', '')

    # Extract file
    file_start = raw_message.find('File: ') + len('File: ')
    file_end = raw_message.find('\n', file_start)
    parsed_data['file'] = raw_message[file_start:file_end].strip()

    # Add package name
    parsed_data['package_name'] = package_name

    return parsed_data


  def parse_message_sink(self, raw_message, package_name):
    """
    @description
    Parse the raw message from the SARIF file.
    E.g., 
    ''The callable [merge](1) is a class pollution sink API in [Module babel.localedata](2) \n- Type: setItem\n- Base: Arg0\n- Key: Arg1\n- Value: Arg0\n- Function: merge\n- Module: Module babel.localedata\n- File: /home/redacted/Desktop/python-class-pollution/tasks/test/output/robusta/dependency/output/babel/codebase/babel/localedata.py\nThe callable [merge](1) is a class pollution sink API in [Module babel.localedata](2) \n- Type: setItem\n- Base: Arg0\n- Key: Arg1\n- Value: Arg1\n- Function: merge\n- Module: Module babel.localedata\n- File: /babel/codebase/babel/localedata.py''
    =>
    {
      "callable": "merge",
      "base": "Arg0",
      "key": "Arg1",
      "value": "Arg0",
      "function": "merge",
      "module": "babel.localedata",
      "file": "/babel/codebase/babel/localedata.py",
      "type": "setItem",
      "package_name": "babel"
    }
    """
    parsed_data = {}

    # Extract callable
    callable_start = raw_message.find('[') + 1
    callable_end = raw_message.find(']', callable_start)
    parsed_data['callable'] = raw_message[callable_start:callable_end]

    # Extract type
    type_start = raw_message.find('Type: ') + len('Type: ')
    type_end = raw_message.find('\n', type_start)
    parsed_data['type'] = raw_message[type_start:type_end].strip()

    # Extract base
    base_start = raw_message.find('Base: ') + len('Base: ')
    base_end = raw_message.find('\n', base_start)
    parsed_data['base'] = raw_message[base_start:base_end].strip()

    # Extract key
    key_start = raw_message.find('Key: ') + len('Key: ')
    key_end = raw_message.find('\n', key_start)
    parsed_data['key'] = raw_message[key_start:key_end].strip()

    # Extract value
    value_start = raw_message.find('Value: ') + len('Value: ')
    value_end = raw_message.find('\n', value_start)
    parsed_data['value'] = raw_message[value_start:value_end].strip()

    # Extract function
    function_start = raw_message.find('Function: ') + len('Function: ')
    function_end = raw_message.find('\n', function_start)
    parsed_data['function'] = raw_message[function_start:function_end].strip()

    # Extract module
    module_start = raw_message.find('Module: ') + len('Module: ')
    module_end = raw_message.find('\n', module_start)
    module_name = raw_message[module_start:module_end].strip()
    parsed_data['module'] = module_name.replace('Module ', '')

    # Extract file
    file_start = raw_message.find('File: ') + len('File: ')
    file_end = raw_message.find('\n', file_start)
    parsed_data['file'] = raw_message[file_start:file_end].strip()

    # Add package name
    parsed_data['package_name'] = package_name

    return parsed_data
  
  def parse_message_source(self, raw_message, package_name):
    """
    @description
    Parse the raw message from the SARIF file.
    E.g., 
    'The callable [values_to_compare](1) is a class pollution taint propagation API in [Module babel.messages.catalog](2) \n- Parameter: Arg0\n- Function: values_to_compare\n- Module: Module babel.messages.catalog\n- File: /babel/messages/catalog.py'
    =>
    {
      "callable": "values_to_compare",
      "parameter": "Arg0",
      "function": "values_to_compare",
      "module": "babel.messages.catalog",
      "file": "/babel/messages/catalog.py",
      "package_name": "babel"
    }
    """
    parsed_data = {}
    
    callable_start = raw_message.find('[') + 1
    callable_end = raw_message.find(']', callable_start)
    parsed_data['callable'] = raw_message[callable_start:callable_end]
    
    parameter_start = raw_message.find('Parameter: ') + len('Parameter: ')
    parameter_end = raw_message.find('\n', parameter_start)
    parsed_data['parameter'] = raw_message[parameter_start:parameter_end].strip()
    
    function_start = raw_message.find('Function: ') + len('Function: ')
    function_end = raw_message.find('\n', function_start)
    parsed_data['function'] = raw_message[function_start:function_end].strip()
    
    module_start = raw_message.find('Module: ') + len('Module: ')
    module_end = raw_message.find('\n', module_start)
    module_name = raw_message[module_start:module_end].strip()
    parsed_data['module'] = module_name.replace('Module ', '')
    
    file_start = raw_message.find('File: ') + len('File: ')
    file_end = raw_message.find('\n', file_start)
    parsed_data['file'] = raw_message[file_start:file_end].strip()

    parsed_data['package_name'] = package_name
    
    return parsed_data
  
  def generate_source_data_extension_format(self, source_model):
    """
    @description
    Generate the data extension format from the source model.

    @param source_model: Dict - The source model.
    {
      "callable": "values_to_compare",
      "parameter": "Arg0",
      "function": "values_to_compare",
      "module": "babel.messages.catalog",
      "file": "/babel/messages/catalog.py,
      "package_name": "babel"
    }

    @returns data_extension: List - The data extension format.
    ["babel", "Member[babel].Member[messages].Member[catalog].Member[values_to_compare]", "class-pollution-source"]

    Refer to: https://codeql.github.com/docs/codeql-language-guides/customizing-library-models-for-python/#access-paths
    """
    module_parts = source_model['module'].split('.')
    member_path = ".".join([f"Member[{part}]" for part in module_parts]) + f".Member[{source_model['callable']}]"
    
    data_extension = [
        source_model['package_name'],
        member_path,
        "class-pollution-source"
    ]
    
    return data_extension

  def generate_sink_data_extension_format(self, sink_model):
    """
    @description
    Generate the data extension format from the sink model.

    @param sink_model: Dict - The sink model.
    {
      "callable": "merge",
      "base": "Arg0",
      "key": "Arg1",
      "value": "Arg0",
      "function": "merge",
      "module": "babel.localedata",
      "file": "/babel/codebase/babel/localedata.py",
      "type": "setItem",
      "package_name": "babel"
    }

    @returns data_extension: List - The data extension format.
    ["babel", "Member[babel].Member[localedata].Member[merge].Argument[1]", "class-pollution-sink"]

    @todo
    Don't know how to represent multiple arguments in the sink data extension format.
    """
    # Split the module into parts and construct the member path
    module_parts = sink_model['module'].split('.')
    member_path = ".".join([f"Member[{part}]" for part in module_parts]) + f".Member[{sink_model['callable']}]"
    
    # Get from the key's parameter
    match = re.match(r"Arg(\d+)", sink_model.get("key", ""))
    if match:
        arg_index = match.group(1)
        member_path += f".Argument[{arg_index}]"
    else:
        raise ValueError(f"Invalid argument format: {sink_model.get('key')}")
    
    # Construct the data extension format
    data_extension = [
        sink_model['package_name'],
        member_path,
        "class-pollution-sink"
    ]
    
    return data_extension
  
  def generate_summary_data_extension_format(self, summary_model):
    """
    @description
    Generate the data extension format from the summary model.

    @param summary_model: Dict - The summary model.
    {
      "callable": "values_to_compare",
      "parameter": "Arg0",
      "function": "values_to_compare",
      "module": "babel.messages.catalog",
      "file": "/babel/messages/catalog.py",
      "package_name": "babel"
    }

    @returns data_extension: List - The data extension format.
    ["babel", "Member[babel].Member[messages].Member[catalog].Member[values_to_compare]", "Argument[0]", "ReturnValue", "taint"]
    """
    module_parts = summary_model["module"].split(".")
    member_path = ".".join([f"Member[{part}]" for part in module_parts]) + f".Member[{summary_model['callable']}]"

    match = re.match(r"Arg(\d+)", summary_model.get("parameter", ""))
    if match:
        arg_index = match.group(1)
        argument = f"Argument[{arg_index}]"
    else:
        raise ValueError(f"Invalid parameter format: {summary_model.get('parameter')}")

    data_extension = [
        summary_model["package_name"],
        member_path,
        argument,
        "ReturnValue",
        "taint"
    ]
    
    return data_extension

  
if __name__ == "__main__":
  sarif_processor = SarifProcessor()
  sarif_processor.process("babel", "/home/redacted/Desktop/python-class-pollution/tasks/test/output/robusta/dependency/output/babel/results/DependencyClassPollutionTaintProp.ql.sarif", "/home/redacted/Desktop/python-class-pollution/tasks/test/output/robusta/dependency/output/babel/results/source_model.json", type="summary")