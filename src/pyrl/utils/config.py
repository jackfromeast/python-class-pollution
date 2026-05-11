"""
@description
---------------------
Holds the configuration settings for all the analysis tasks.
"""
import os
import yaml
from .helper import resolve_relative_path

def load_config(config_path):
    """Load the YAML configuration file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def get_workflow_from_config(config):
    """Determine the workflow from the config file."""
    if config.get('WORKFLOW', {}).get('CLASS_POLLUTION_ANALYSIS', False):
        return "class_pollution"
    elif config.get('WORKFLOW', {}).get('DEPENDENCY_ANALYSIS', False):
        return "dependency_analysis"
    else:
        raise ValueError("No valid workflow specified in the config file.")

class ConfigDict:
  """A wrapper around Python dictionaries to support dot notation access."""
  def __init__(self, dictionary):
    for key, value in dictionary.items():
      if isinstance(value, dict):
        setattr(self, key, ConfigDict(value))  # Convert nested dict to ConfigDict
      else:
        setattr(self, key, value)

  def get(self, key, default=None):
    """Retrieve a value, supporting dot notation (e.g., 'CODEQL.CLI')."""
    keys = key.split(".")
    value = self
    for k in keys:
      value = getattr(value, k, default)
    return value

  def set(self, key, value):
    """Set a value using dot notation."""
    keys = key.split(".")
    d = self
    for k in keys[:-1]:
      d = getattr(d, k)
    setattr(d, keys[-1], value)

  def __getitem__(self, key):
    """Allow dictionary-style access (config['SCHEDULER']) as well."""
    return getattr(self, key)

  def __repr__(self):
    return str(self.__dict__)

class Config:
  def __init__(self, config_path=None):
    """Initialize and load configuration from the given YAML file."""
    self.config_path = config_path or os.path.join(
      os.path.dirname(__file__), "config.yaml"
    )
    self.config = self.load_config()

    # Convert config dictionary to an object that supports dot notation
    self.config = ConfigDict(self.config)

    # Resolve relative paths
    self.resolve_paths()

  def load_config(self):
    """Load configuration from the YAML file."""
    if not os.path.exists(self.config_path):
      raise FileNotFoundError(f"Config file not found: {self.config_path}")

    with open(self.config_path, "r") as f:
      return yaml.safe_load(f)

  def resolve_paths(self):
    """Resolve relative paths within the configuration."""
    workspace = resolve_relative_path(self.config.get("SCHEDULER.WORKSPACE", ""))

    if workspace:
      # Ensure LOG_PATH defaults to WORKSPACE/log/ if not set
      if not self.config.LOG.LOG_PATH:
        self.config.LOG.LOG_PATH = os.path.join(workspace, "logs")

      # Resolve REPO_LIST (if it's a relative path)
      if self.config.SCHEDULER.MODE == "seed":
        self.config.SCHEDULER.REPO_LIST = []
        return

      repo_list_candidates = []
      if not os.path.isabs(self.config.SCHEDULER.REPO_LIST):
        candidate = os.path.join(workspace, "input", self.config.SCHEDULER.REPO_LIST)
        repo_list_candidates.append(candidate)
      else:
        repo_list_candidates.append(self.config.SCHEDULER.REPO_LIST)

      # 2. dataset/pip/<REPO_LIST>
      repo_list_candidates.append(
        os.path.join(resolve_relative_path("dataset/pip/"), self.config.SCHEDULER.REPO_LIST)
      )
      # 3. dataset/github/<REPO_LIST>
      repo_list_candidates.append(
        os.path.join(resolve_relative_path("dataset/github/"), self.config.SCHEDULER.REPO_LIST)
      )
      # 4. dataset/all-alerts/<REPO_LIST>
      repo_list_candidates.append(
        os.path.join(resolve_relative_path("dataset/all-alerts/"), self.config.SCHEDULER.REPO_LIST)
      )

      for candidate in repo_list_candidates:
        if os.path.exists(candidate):
          self.config.SCHEDULER.REPO_LIST = candidate
          break
      else:
        raise FileNotFoundError(
          f"REPO_LIST not found in any of the default locations: {repo_list_candidates}"
        )

  def __getattr__(self, name):
    """Safely access attributes from `self.config` to avoid infinite recursion."""
    config = object.__getattribute__(self, "config")
    if name in config.__dict__:
      return config.__dict__[name]
    raise AttributeError(f"'Config' object has no attribute '{name}'")
  
if __name__ == "__main__":
  config = Config("/home/jackfromeast/Desktop/python-class-pollution/analyzer/new-config-example.yaml")
  print("TEST_NAME:", config.SCHEDULER.TEST_NAME)
  print("CODEQL CLI Path:", config.CODEQL.CLI)
  print("Resolved REPO_LIST Path:", config.SCHEDULER.REPO_LIST)
  print("Resolved LOG_PATH:", config.LOG_PATH)