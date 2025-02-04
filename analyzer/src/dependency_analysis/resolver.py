"""
@description
---------------------
Given a codebase path, this module helps to generate a list of its dependencies.
"""
import os
import json
import argparse
import subprocess
from collections import deque
from utils.logger import LoggerFactory

class DependencyResolver:
  """
  A class to resolve dependencies from a codebase.
  
  codebase_path: Path to the target codebase.
  output_path:   Path to store the dependencies.json and the codebases of its dependencies.
                 The dependencies' codebases will be stored in output_path/codebases, 
                 The dependency information will be stored in output_path/dependencies.json.
  """
  def __init__(self, codebase_path, output_path, name="unknown", download=False):
    self.name = name
    self.codebase_path = codebase_path
    self.output_path = output_path
    self.download = download

    self.resolved_dependency_manifest = None
    self.SBOM = None
    
    # temp/venv for temporary virtual environment
    # temp/codebases raw downdloaded dependencies, will be moved to output_path/codebases further
    self.temp_dir = None
    self.logger = LoggerFactory.get_logger("DependencyResolver", local_logger_folder=os.path.join(output_path, "..", "logs"))

    if not os.path.exists(codebase_path):
      raise FileNotFoundError(f"The specified codebase path does not exist: {codebase_path}")
    
    os.makedirs(output_path, exist_ok=True)

  DEPENDENCY_MANIFESTS = {
    "Pip": ["requirements.txt"],
    "Poetry": ["pyproject.toml", "poetry.lock"],
    "Pipenv": ["Pipfile", "Pipfile.lock"],
    "PDM": ["pyproject.toml", "pdm.lock"],
    "Conda": ["environment.yml"]
  }

  def resolve(self):
    """
    Resolves dependencies information from the codebase.

    We search the codebase in a BFS manner to find all the possible dependency menifest files.
    We may find multiple manifest files for different package managers.
    We will output those information to the output_path.

    <Pip>: `requirements.txt`
    <Poetry>: `pyproject.toml` and `poetry.lock`
    <Pipenv>: `Pipfile` and `Pipfile.lock`
    <PDM>: `pyproject.toml` and `pdm.lock`
    <Conda>: `environment.yml`
    """
    queue = deque([self.codebase_path])
    self.resolved_dependency_manifest = {manager: [] for manager in self.DEPENDENCY_MANIFESTS}

    while queue:
      current_dir = queue.popleft()
      try:
        for entry in os.scandir(current_dir):
          if entry.is_dir():
            queue.append(entry.path)
          elif entry.is_file():
            for manager, manifest_files in self.DEPENDENCY_MANIFESTS.items():
              if entry.name in manifest_files:
                self.resolved_dependency_manifest[manager].append(entry.path)
                self.logger.info(f"Found {manager} manifest file: {entry.path}")
      except PermissionError:
        continue
    
    if not any(self.resolved_dependency_manifest.values()):
      self.logger.warning("No dependency manifest files found in the codebase.")
      return None
    
    return self.resolved_dependency_manifest

  def generate_SBOM(self):
    """
    Generate a SBOM from the resolved dependency manifest.
    Uses CycloneDX-Py to generate SBOM for the highest-priority package manager found.
    """
    sbom_command = None

    if self.resolved_dependency_manifest["Pip"]:
      pip_manifest = self.resolved_dependency_manifest["Pip"][0]
      sbom_command = ["cyclonedx-py", "requirements", pip_manifest]
    elif self.resolved_dependency_manifest["Pipenv"]:
      sbom_command = ["cyclonedx-py", "pipenv", self.codebase_path]
    elif self.resolved_dependency_manifest["Poetry"]:
      sbom_command = ["cyclonedx-py", "poetry", self.codebase_path]

    if not sbom_command:
      raise ValueError("No recognized dependency manifests found. Cannot generate SBOM.")

    try:
      result = subprocess.run(sbom_command, check=True, capture_output=True, text=True)
      self.SBOM = result.stdout.strip()
    except subprocess.CalledProcessError as e:
      self.logger.error(f"Error running command {' '.join(sbom_command)}: {e}")

  def output_SBOM(self):
    """
    Output the SBOM to the output_path.
    """
    if not self.SBOM:
      self.logger.warning("No SBOM generated. Skipping output.")
      return
    
    with open(os.path.join(self.output_path, "SBOM.json"), "w") as f:
      f.write(self.SBOM)

    with open(os.path.join(self.output_path, "dependencies.json"), "w") as f:
      f.write(json.dumps(self.resolved_dependency_manifest, indent=2))

def main():
  parser = argparse.ArgumentParser(description="Generate a list of dependencies from a codebase.")
  parser.add_argument("--codebase-path", required=True, help="Path to the codebase.")
  parser.add_argument("--output-path", required=True, help="Path to store the output file.")
  args = parser.parse_args()

  resolver = DependencyResolver(args.codebase_path, args.output_path)
  resolver.resolve()


if __name__ == "__main__":
  main()