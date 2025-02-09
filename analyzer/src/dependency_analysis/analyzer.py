"""
@description
---------------------
The entrypoint for the dependency analysis workflow.

Given the repository URL, this module helps to run the dependency analysis including the following steps:
1/ Resolve its dependencies in SBOM format.
2/ For each dependency, run the codeql dependency analysis queries and generate the result in data extension format.
3/ Summery all the results and output the data extension file for the repository.

@todo
1/ We can add more specifc access path for the external dependency modeling in the data extension.
   For example, ListElement, DictionaryElement, SetElement, etc to describe any element in the List/Dictionary/Set.
   Plus, we can add more specific inner value of those arguments, e.g., DictionaryElement[name] 

2/ Implement the caching mechanism for the dependency analysis.
"""
import os
import json
import yaml
from packageurl import PackageURL
from .resolver import DependencyResolver
from .sarif_processor import SarifProcessor
from codeql_driver.runner import CodeQLRunner
from utils.helper import resolve_repo_name, cleanup_folders
from utils.logger import LoggerFactory
from utils.downloader import download

class DependencyAnalyzer:
  """
  @param repo_url: str - The URL of the repository to analyze.
  @param config: Config - The configuration object.

  /repo
    /codebase                               # The codebase of the target repository (readonly)
    /dependency
      /dependencies.json                    # The dependency information
      /sbom.json                            # The SBOM of the dependencies
      /output
        /dependency1
          /codebase                         # The codebase of the dependency
          /codeql-db                        # The codeql database of the dependency   
          /results
            /source.sarif                   # The source query result in SARIF format
            /source.data.json               # The source query result in data extension format
            /sink.sarif                     # The sink query result in SARIF format
            /sink.data.json                 # The sink query result in data extension format
            /summary.sarif                  # The summary query result in SARIF format
            /summary.data.json              # The summary query result in data extension format
      /data_extension.yaml                  # The summary of the dependency analysis 
      /logs                                 # The logs of the dependency analysis
 
  """
  def __init__(self, repo_url, repo_workspace_path, config):
    self.repo_url = repo_url
    self.repo_name = resolve_repo_name(repo_url)
    self.config = config.DEPENDENCY_ANALYSIS
    self.codeql_config = config.CODEQL
    self.repo_workspace_path = repo_workspace_path

    self.cache_dir = self.config.CACHE_PATH
    self.codeql_source_query = self.config.QUERIES.SOURCE
    self.codeql_sink_query = self.config.QUERIES.SINK
    self.codeql_summary_query = self.config.QUERIES.SUMMARY
    self.codeql_queries = [self.codeql_source_query, self.codeql_sink_query, self.codeql_summary_query]

    self.codebase_path = os.path.join(self.repo_workspace_path, "codebase")
    self.dependency_workspace_path = os.path.join(self.repo_workspace_path, "dependency")

    self.logger = LoggerFactory.get_logger("DependencyAnalyzer",
                                          local_logger_folder=os.path.join(self.dependency_workspace_path, "logs"), result_logger=True)

  def run(self):
    """
    @description
    The main pipeline for the dependency analysis workflow.
    """
    # Step 1: Resolve the dependencies
    try:
      resolver = DependencyResolver(self.codebase_path, self.dependency_workspace_path, self.repo_name)
      if resolver.resolve():
        resolver.generate_SBOM()
        resolver.output_SBOM()
    except Exception as e:
      self.logger.error(f"Error running 1/ dependency resovling for {self.repo_url}: {e}")
      return
    finally:
      if not self.check_dependency_resolve_status():
        self.logger.warning(f"No dependency resolved for {self.repo_url}. Skip.")
        return
      
    # Step 2: Run the codeql queries for the dependencies
    try:
      for dep_name in self.select_single_dependency(os.path.join(self.dependency_workspace_path, "sbom.json")):
        try:
          dep_path = os.path.join(self.dependency_workspace_path, "output", dep_name)
          self.analyze_single_dependency(dep_name, dep_path)
        except Exception as e:
          self.logger.error(f"Error running 2/ dependency analysis for {dep_name}: {e}")
          cleanup_folders(dep_path)
          continue
    except Exception as e:
      self.logger.error(f"Error running 2/ dependency analysis for {self.repo_url}: {e}")
      return
    
    # Step3: Generate the all-in-one data extension file
    try:
      self.generate_final_data_extension()
    except Exception as e:
      self.logger.error(f"Error running 3/ dependency analysis for {self.repo_url}: {e}")
      return

  def generate_final_data_extension(self):
    """
    @description
    Generate the final data extension file for the repository.

    Go through each dependency/results/data_extension.yaml file and merge them into a single file.
    """
    final_data_extension = {
      "extensions": []
    }

    dependencies_output_dir = os.path.join(self.dependency_workspace_path, "output")
    for dep_name in os.listdir(dependencies_output_dir):
      dep_path = os.path.join(dependencies_output_dir, dep_name)
      data_extension_path = os.path.join(dep_path, "results", "data_extension.yaml")

      if os.path.exists(data_extension_path):
        try:
          with open(data_extension_path, "r") as f:
            dep_data_extension = yaml.safe_load(f)
            if dep_data_extension and "extensions" in dep_data_extension:
              final_data_extension["extensions"].extend(dep_data_extension["extensions"])
        except Exception as e:
          self.logger.error(f"Error reading data extension for {dep_name}: {e}")
          continue

    final_data_extension_path = os.path.join(self.dependency_workspace_path, "data_extension.yaml")
    try:
      with open(final_data_extension_path, "w") as f:
        yaml.dump(final_data_extension, f, default_flow_style=False, sort_keys=False)
      self.logger.info(f"Final data extension saved to {final_data_extension_path}")
    except Exception as e:
      self.logger.error(f"Error saving final data extension: {e}")

  def check_dependency_resolve_status(self):
    """
    @description
    Check the status of the dependency resolving.
    """
    if not os.path.exists(os.path.join(self.dependency_workspace_path, "dependencies.json")):
      return False
    
    if not os.path.exists(os.path.join(self.dependency_workspace_path, "sbom.json")):
      return False
    
    return True

  def select_single_dependency(self, sbom_path):
    """
    @description
    Yield the name of a single dependency to analyze.

    @todo
    Support the version.
    """
    with open(sbom_path, "r") as f:
      sbom = json.load(f)
      for dep in sbom["components"]:
        yield PackageURL.from_string(dep["purl"]).name
    
  def get_query_name(self, type):
    """
    @description
    Get the query name based on the type of the query.

    @param type: str - The type of the query.
    """
    if type == "source":
      return self.codeql_source_query.split("/")[-1]
    elif type == "sink":
      return self.codeql_sink_query.split("/")[-1]
    elif type == "summary":
      return self.codeql_summary_query.split("/")[-1]
    else:
      raise ValueError(f"Invalid query type: {type}")

  def analyze_single_dependency(self, dep_name, dep_path):
    """
    @description
    Analyze a single dependency.

    @param dep_name: str - The name of the dependency.
    @param dep_path: str - The path to the dependency codebase.
    """
    # 1/ Download the codebase
    os.makedirs(dep_path, exist_ok=True)
    if not download(dep_name, dep_path, pip=True):
      self.logger.error(f"Failed to download codebase for {dep_name}")
      return
    
    # 2/ Run the codeql queries
    self.logger.info(f"Start running codeql queries for {dep_name}")
    codeql_runner = CodeQLRunner(dep_path, 
                                 self.codeql_queries,
                                 self.codeql_config,
                                 delete_after_query=True, # Delete the codeql database/codebase after running the queries
                                 timeout=180)             # 3 minutes
    
    if not codeql_runner.build():
      self.logger.error(f"Failed to build codeql database for {dep_name}")
      return

    codeql_runner.run_queries()

    if not self.check_ql_results(dep_path):
      self.logger.warning(f"No results found for {dep_name}")
      return

    # 3/ Process the sarif results
    dependency_models = self.post_process(dep_name, dep_path)

    if not dependency_models["source"] and not dependency_models["sink"] and not dependency_models["summary"]:
      self.logger.info(f"Codeql queries for {dep_name} completed.")
      return

    # 4/ Output the data extension file
    self.save_as_data_extension(dependency_models, dep_path)
  
  def check_ql_results(self, dep_path):
    """
    @description
    Check if the codeql query results are generated.
    """
    for query in self.codeql_queries:
      if os.path.exists(os.path.join(dep_path, "results", query.split("/")[-1] + '.sarif')):
        return True
    return False
  
  def post_process(self, dep_name, dep_path):
    """
    @description
    Post-process the dependency analysis result.
    """
    sarif_processor = SarifProcessor()
    dependency_models = {
      "source": [],
      "sink": [],
      "summary": []
    }

    source_query_result_path = os.path.join(dep_path, "results", self.get_query_name("source") + ".sarif")
    if os.path.exists(source_query_result_path):
      dependency_models["source"] = sarif_processor.process(dep_name, source_query_result_path, os.path.join(dep_path, "results", "source_model.json"), "source")

    sink_query_result_path = os.path.join(dep_path, "results", self.get_query_name("sink") + ".sarif")
    if os.path.exists(sink_query_result_path):
      dependency_models["sink"] = sarif_processor.process(dep_name, sink_query_result_path, os.path.join(dep_path, "results", "sink_model.json"), "sink")

    summary_query_result_path = os.path.join(dep_path, "results", self.get_query_name("summary") + ".sarif")
    if os.path.exists(summary_query_result_path):
      dependency_models["summary"] = sarif_processor.process(dep_name, summary_query_result_path, os.path.join(dep_path, "results", "summary_model.json"), "summary")
    
    return dependency_models

  def save_as_data_extension(self, dependency_models, dep_path):
      """
      @description
      Save the dependency analysis result as data extension format.

      @param dependency_models: dict - The dependency analysis result.
      @param dep_path: str - The path to the dependency codebase.
      """
      data_extension_path = os.path.join(dep_path, "results", "data_extension.yaml")

      data_extension = {
        "extensions": []
      }

      for model_type, results in dependency_models.items():
        for result in results:
          extension = {
            "addsTo": {
              "pack": "jackfromeast/class-pollution-all",
              "extensible": f"{model_type}Model",
              "data": result["data_extension"]
            }
          }
          data_extension["extensions"].append(extension)

      with open(data_extension_path, "w") as f:
        yaml.dump(data_extension, f, default_flow_style=False, sort_keys=False)

      self.logger.info(f"Data extension saved to {data_extension_path}")
    






    

  