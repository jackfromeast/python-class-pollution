"""
@description
---------------------
Given a codebase path, this module helps to generate a list of its dependencies.

@usage
---------------------
python resolve_dependency.py --codebase-path <path-to-codebase> --output-path <path-to-output-folder>

- codebase-path: Path to the codebase.
- output-path: The output json file will be stored at the output-path/dependencies.json.

Example:
python resolve_dependency.py --codebase-path /home/jackfromeast/Desktop/python-class-pollution/tmp/robusta/codebase \
  --output-path /home/jackfromeast/Desktop/python-class-pollution/tmp/robusta/dependency

@todo
---------------------
1/ Add logging to the code
"""

import argparse
import os
import re
import json
import shutil
import tempfile
import subprocess
import toml

class DependencyResolver:
  """
  A class to resolve dependencies from a codebase.
  
  codebase_path: Path to the target codebase.
  output_path:   Path to store the dependencies.json and the codebases of its dependencies.
                 The dependencies' codebases will be stored in output_path/codebases, 
                 The dependency information will be stored in output_path/dependencies.json.
  """
  def __init__(self, codebase_path, output_path, name="unknown"):
    self.name = name
    self.codebase_path = codebase_path
    self.output_path = output_path
    self.dependencies = {}
    self.use_requirements = False
    self.use_pytoml = False
    self.python_version = "3.10"

    self.python_bin_path = shutil.which("python")
    self.python_venv = None
    self.requirements_path = None
    self.pytoml_path = None
    
    # temp/venv for temporary virtual environment
    # temp/codebases raw downdloaded dependencies, will be moved to output_path/codebases further
    self.temp_dir = None

    if not os.path.exists(codebase_path):
      raise FileNotFoundError(f"The specified codebase path does not exist: {codebase_path}")
    
    os.makedirs(output_path, exist_ok=True)
  
  def output_dependencies(self):
    """
    Outputs the dependencies to the output path.
    """
    dependency_info = {
      "name": self.name,
      "python_version": self.python_version,
      "use_requirements": self.use_requirements,
      "requirements_path": self.requirements_path,
      "use_pytoml": self.use_pytoml,
      "pytoml_path": self.pytoml_path,
      "dependencies": self.dependencies
    }

    output_file = os.path.join(self.output_path, "dependencies.json")
    with open(output_file, "w") as f:
      json.dump(dependency_info, f, indent=2)

    print(f"Dependencies saved to {output_file}")

  def resolve(self):
    """
    Resolves dependencies information from the codebase.
    """
    if self._try_requirements_txt():
      print(f"Resolved dependencies from requirements.txt at {self.requirements_path}")
    elif self._try_pytoml():
      print(f"Resolved dependencies from pyproject.toml at {self.pytoml_path}")
    elif self._try_source_code():
      print("Resolved dependencies from source code.")
    
    self.output_dependencies()
    
  def _try_requirements_txt(self):
    """
    Tries to resolve dependencies from the requirements.txt file.

    1/ Search for requirements.txt file in the entire codebase.
    2/ If found, extract the dependencies from it and attempt to determine the Python version used, if specified.
    """
    for root, _, files in os.walk(self.codebase_path):
      for file in files:
        if file == "requirements.txt":
          requirements_path = os.path.join(root, file)
          with open(requirements_path, "r") as req_file:
            for line in req_file:
              line = line.strip()
              if line and not line.startswith("#"):
                if "==" in line:
                  package, version = line.split("==", 1)
                  self.dependencies[package.strip()] = version.strip()
                elif ">=" in line:
                  package, version = line.split(">=", 1)
                  self.dependencies[package.strip()] = f">= {version.strip()}"
                elif "<=" in line:
                  package, version = line.split("<=", 1)
                  self.dependencies[package.strip()] = f"<= {version.strip()}"

                # TODO: This is not correct. We need to handle >=, <=, >, < as well.
                # elif "python_version" in line:
                #   self.python_version = line.split("python_version")[-1].strip().strip('"').strip("=").strip()
                # else:
                #   self.dependencies[line] = "latest"

          # We use the requirements.txt file to download the source code of the dependencies.
          self.requirements_path = requirements_path
          self.use_requirements = True

          return True
    return False

  def _try_pytoml(self):
    """
    Tries to resolve dependencies from the pyproject.toml file.

    1/ Search for pyproject.toml file in the entire codebase.
    2/ If found, extract the dependencies from it.
    """
    for root, _, files in os.walk(self.codebase_path):
      for file in files:
        if file == "pyproject.toml":
          pytoml_path = os.path.join(root, file)
          with open(pytoml_path, "r") as pyproj_file:
            try:
                pyproject_data = toml.load(pyproj_file)
                tool_section = pyproject_data.get("tool", {})
                poetry_section = tool_section.get("poetry", {})
                deps = poetry_section.get("dependencies", {})
                for dep, version in deps.items():
                  if dep != "python":
                    if isinstance(version, str):
                        self.dependencies[dep] = version
                    else:
                        self.dependencies[dep] = "latest"

                # Mark pyproject.toml as the source of dependencies
                self.pytoml_path = pytoml_path
                self.use_pytoml = True

                # Attempt to determine Python version from the pyproject.toml
                # python_version = poetry_section.get("python", None)
                # if python_version:
                #     self.python_version = python_version

                return True
            except toml.TomlDecodeError:
                print(f"Error decoding {pytoml_path}")
    return False
  
  def _try_source_code(self):
    """
    Tries to resolve dependencies from the source code itself.

    TODO: Consider using the SBOM tool for python project
    """
    raise NotImplementedError("Resolving dependencies from source code is not implemented yet.")

  def download_dependencies(self):
    """
    Downloads the source code of the dependencies using the newly created virtual environment.

    Note that, at most of time, we don't need to download them.
    """
    import logging

    # 1. Create or reuse a virtual environment
    self._create_virtualenv()

    # 2. Install dependencies based on the resolution method
    if self.use_requirements:
        logging.info("Installing from requirements.txt...")
        self._download_requirements()
    elif self.use_pytoml:
        logging.info("Installing from pyproject.toml (Poetry)...")
        self._download_pytoml()
    else:
        logging.info("No known dependency file found; using fallback download.")
        self._download_from_dependencies()
  
  def _download_requirements(self, requirements_path=None):
    """
    Downloads dependencies listed in requirements.txt *line by line* using pip,
    and extracts their source code. Each requirement is installed separately.

    1. Locate the requirements.txt (either self.requirements_path or the argument).
    2. For each non-comment line in requirements.txt, run a separate pip install.
    3. Move the downloaded dependencies to output_path/codebases.
    """
    if not self.requirements_path and not requirements_path:
        print("No requirements.txt specified, skipping pip dependency installation.")
        return
    elif not requirements_path:
        requirements_path = self.requirements_path

    temp_codebase_dir = os.path.join(self.temp_dir, "codebases")
    os.makedirs(temp_codebase_dir, exist_ok=True)

    with open(requirements_path, "r", encoding="utf-8") as req_file:
      for line in req_file:
          requirement = line.strip()
          if not requirement or requirement.startswith("#"):
              continue

          print(f"Installing requirement: {requirement}")
          cmd = [
            self.python_bin_path, "-m", "pip", "install",
            "--ignore-requires-python",  # keep ignoring python version checks
            "--target", temp_codebase_dir,
            requirement
          ]
          try:
            subprocess.run(cmd, check=True)
          except subprocess.CalledProcessError as e:
            print(f"Failed to install requirement: {e}")

    self._move_dependencies(
      temp_codebase_dir,
      os.path.join(self.output_path, "codebases")
    )

  def _download_pytoml(self):
    """
    Downloads dependencies from the pyproject.toml using Poetry, then reuses
    `_download_requirements` to install them line-by-line, all within
    self.temp_dir/poetry.
    """
    if not self.pytoml_path:
        print("No pyproject.toml specified or found, skipping poetry dependency installation.")
        return

    # Create or reuse self.temp_dir
    if not self.temp_dir:
        self.temp_dir = tempfile.mkdtemp(prefix="dep_resolve_")

    # Use self.temp_dir/poetry for all Poetry-related operations
    poetry_dir = os.path.join(self.temp_dir, "poetry")
    os.makedirs(poetry_dir, exist_ok=True)

    try:
        # Copy pyproject.toml and (optionally) poetry.lock to poetry_dir
        shutil.copy(self.pytoml_path, poetry_dir)
        lockfile_path = os.path.join(os.path.dirname(self.pytoml_path), "poetry.lock")
        if os.path.exists(lockfile_path):
            shutil.copy(lockfile_path, poetry_dir)

        # Export to requirements.txt via Poetry
        export_cmd = [
            "poetry", "export",
            "-f", "requirements.txt",
            "--without-hashes"
        ]
        export_process = subprocess.run(
            export_cmd,
            cwd=poetry_dir,
            capture_output=True,
            text=True,
            check=True
        )

        # Write the exported requirements to a file in poetry_dir
        exported_req_path = os.path.join(poetry_dir, "requirements.txt")
        with open(exported_req_path, "w", encoding="utf-8") as req_file:
            for line in export_process.stdout.splitlines():
                # Optionally remove environment markers like `python_version`
                cleaned_line = re.sub(r";.*python_version.*", "", line).strip()
                if cleaned_line:
                    req_file.write(cleaned_line + "\n")

        # Reuse the _download_requirements() method with the newly created requirements file
        self._download_requirements(requirements_path=exported_req_path)

    except subprocess.CalledProcessError as e:
        print(f"Poetry export/install failed: {e}")

  def _download_from_dependencies(self):
    """
    Downloads dependencies by iterating over resolved dependencies.
    """
    raise NotImplementedError("Resolving dependencies from source code is not implemented yet.")

  def _move_dependencies(self, from_dir, to_dir):
    """
    Moves only the source code of downloaded dependencies from `from_dir` to `to_dir`.
    """
    os.makedirs(to_dir, exist_ok=True)

    for item in os.listdir(from_dir):
        src_path = os.path.join(from_dir, item)
        
        # Move directories that are not `_something` nor ending with .dist-info or .pth
        if os.path.isdir(src_path) and not item.startswith("_") and not item.endswith((".dist-info", ".pth")):
            dst_path = os.path.join(to_dir, item)
            shutil.move(src_path, dst_path)
            print(f"Moved folder: {item} from {src_path} to {dst_path}")

    shutil.rmtree(from_dir)
  
  def _create_virtualenv(self):
    """
    Creates a virtual environment using the specified Python version (if available).
    If no specific Python version is given or creating the venv fails, it falls back to system Python.
    """
    import logging

    if not self.temp_dir:
        self.temp_dir = tempfile.mkdtemp()

    if self.python_version:
        logging.info(f"Using specified Python version: {self.python_version}")
        self.python_bin_path = shutil.which(f"python{self.python_version}")

        if not self.python_bin_path:
            raise RuntimeError(f"Specified Python version {self.python_version} is not available in PATH.")

        # Attempt creating venv with virtualenv
        self.python_venv = os.path.join(self.temp_dir, "venv")
        try:
            subprocess.run(
                [self.python_bin_path, "-m", "pip", "install", "--upgrade", "virtualenv"],
                check=True
            )
            subprocess.run(
                [self.python_bin_path, "-m", "virtualenv", self.python_venv],
                check=True
            )
            logging.info("Successfully created virtual environment using virtualenv.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error creating virtual environment with virtualenv: {e}")
            logging.warning("Falling back to system Python...")
            self.python_venv = None
            # Fall back to system python:
            self.python_bin_path = shutil.which("python")
    else:
        # No python_version specified; just pick system Python
        import logging
        logging.info("No specific Python version provided, defaulting to system Python.")
        self.python_bin_path = shutil.which("python")
        if not self.python_bin_path:
            raise RuntimeError("No system Python found in PATH.")

        # Attempt creating a standard venv
        self.python_venv = os.path.join(self.temp_dir, "venv")
        try:
            subprocess.run([self.python_bin_path, "-m", "venv", self.python_venv], check=True)
            logging.info("Successfully created virtual environment using built-in venv.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error creating virtual environment with venv: {e}")
            self.python_venv = None  # Could not create venv, so we stay on system Python

    # If we did successfully create a venv, update self.python_bin_path to point inside it
    if self.python_venv and os.path.isdir(self.python_venv):
        self.python_bin_path = os.path.join(self.python_venv, "bin", "python")


def main():
  parser = argparse.ArgumentParser(description="Generate a list of dependencies from a codebase.")
  parser.add_argument("--codebase-path", required=True, help="Path to the codebase.")
  parser.add_argument("--output-path", required=True, help="Path to store the output file.")
  args = parser.parse_args()

  resolver = DependencyResolver(args.codebase_path, args.output_path)
  resolver.resolve()


if __name__ == "__main__":
  main()