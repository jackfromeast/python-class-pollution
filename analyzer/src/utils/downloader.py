import os
import shutil
import psutil
import zipfile
import subprocess
from urllib.parse import urlparse
from utils.logger import LoggerFactory

def download(repo_url_or_package, repo_save_path):
  """
  Downloads a repository or package from the given input using the appropriate downloader.

  @params repo_url_or_package (str): The GitHub URL, PyPI URL, or package name.
  @params repo_save_path (str): The path where the repository or package will be saved.
  """
  try:
    parsed_url = urlparse(repo_url_or_package)
    is_url = all([parsed_url.scheme, parsed_url.netloc])
  except Exception:
    is_url = False

  if is_url:
    domain = parsed_url.netloc
    if domain == "github.com":
      downloader = GithubDownloader(repo_url_or_package, repo_save_path)
    elif domain == "pypi.org":
      # If the URL ends with a slash, remove it
      if repo_url_or_package[-1] == "/":
        repo_url_or_package = repo_url_or_package[:-1]

      # Extract the package name and version from the URL
      path_parts = parsed_url.path.strip("/").split("/")
      if len(path_parts) >= 2:
        package_name = path_parts[1]
        version = path_parts[2] if len(path_parts) > 2 else None
        # Construct the package name with version (e.g., "laboneq==2.44.0")
        package_with_version = f"{package_name}=={version}" if version else package_name
        downloader = PipDownloader(package_with_version, repo_save_path)
      else:
        raise ValueError(f"Invalid PyPI URL: {repo_url_or_package}")
    else:
      raise ValueError(f"Unsupported URL domain: {domain}")
  else:
    # If it's not a URL, assume it's a package name (with or without version)
    downloader = PipDownloader(repo_url_or_package, repo_save_path)

  return downloader.clone_repo()

class GithubDownloader:
  def __init__(self, repo_url, repo_save_path):
    self.repo_url = repo_url
    self.repo_save_path = repo_save_path
    self.timeout = 300  # 5 minutes

    self.logger = LoggerFactory.get_logger("GithubDownloader")

  def clone_repo(self):
    """Clone the repository into the specified folder."""
    codebase_save_path = os.path.join(self.repo_save_path, "codebase")
    self.logger.info(f"Cloning repository: {self.repo_url} to {codebase_save_path}")

    if os.path.exists(codebase_save_path):
      # Remove the existing codebase
      self.logger.info("Removing existing codebase...")
      try:
        shutil.rmtree(codebase_save_path)
      except Exception as e:
        self.logger.error(f"Failed to remove existing codebase: {e}")
        return False

    process = None
    stderr = None
    try:
      process = subprocess.Popen(
        ["git", "clone", self.repo_url, codebase_save_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
      )
      _, stderr = process.communicate(timeout=self.timeout)

      if process.returncode == 0:
        self.logger.info(f"Repository cloned successfully to {codebase_save_path}")
        return True
      else:
        self.logger.error(f"Failed to clone repository: {stderr.decode()}")
        if (self.logger.log_error_details):
          self.logger.error(f"Error details: {stderr.decode().strip()}")
        return False

    except subprocess.TimeoutExpired:
      self.logger.error(f"Cloning repository timed out after {self.timeout} seconds.")
      return False

    except subprocess.CalledProcessError as e:
      self.logger.error(f"Failed to clone repository: {e}")
      if (self.logger.log_error_details):
          self.logger.error(f"Error details: {stderr.decode().strip()}")
      return False

    except Exception as e:
      self.logger.error(f"Unexpected error: {e}")
      if (self.logger.log_error_details):
          self.logger.error(f"Error details: {stderr.decode().strip()}")
      return False

    finally:
      if process:
        self.terminate_process(process.pid)

  def terminate_process(self, pid):
    """Kill all processes spawned from the given process ID."""
    try:
      parent = psutil.Process(pid)
      children = parent.children(recursive=True)
      for child in children:
        child.terminate()
      psutil.wait_procs(children, timeout=5)
      parent.terminate()
      self.logger.info(f"Terminated all spawned processes for PID {pid}")
    except psutil.NoSuchProcess:
      pass
      # self.logger.warning(f"Process {pid} already terminated.")
    except Exception as e:
      self.logger.error(f"Error while terminating process tree for PID {pid}: {e}")


class PipDownloader:
  """
  @param package_name: Name of the package to download (can include version, e.g., "laboneq==2.44.0").
  @param repo_save_path: Path to save the downloaded repository.
  """
  def __init__(self, package_name, repo_save_path):
    self.package_name = package_name
    self.repo_save_path = repo_save_path
    self.timeout = 300  # 5 minutes

    self.logger = LoggerFactory.get_logger("PipDownloader")

  def _extract_whl_file(self, whl_path, extract_to):
    """Extract a .whl file to the specified directory."""
    self.logger.info(f"Extracting {whl_path} to {extract_to}")
    try:
      with zipfile.ZipFile(whl_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
      self.logger.info(f"Extraction successful: {extract_to}")
      return True
    except zipfile.BadZipFile as e:
      self.logger.error(f"Failed to extract .whl file: {e}")
      return False
    except Exception as e:
      self.logger.error(f"Unexpected error: {e}")
      return False

  def _clean_directory(self, path):
    """Remove the directory if it exists."""
    if os.path.exists(path):
      self.logger.info(f"Removing existing directory: {path}")
      try:
        shutil.rmtree(path)
      except Exception as e:
        self.logger.error(f"Failed to remove directory {path}: {e}")
        return False
    return True

  def _parse_package_and_version(self, package_input):
    """
    Parse the package name and version from the input string or URL.
    @param package_input: The package name or URL (e.g., "laboneq==2.44.0" or "https://pypi.org/project/laboneq/2.44.0/").
    @return: A tuple (package_name, version) or (package_name, None) if no version is specified.
    """
    # If the input is a URL, extract the package name and version
    if package_input.startswith("https://"):
      parsed_url = urlparse(package_input)
      path_parts = parsed_url.path.strip("/").split("/")
      if len(path_parts) >= 2:
        package_name = path_parts[1]
        version = path_parts[2] if len(path_parts) > 2 else None
        return package_name, version
      else:
        raise ValueError(f"Invalid PyPI URL: {package_input}")
    # If the input is a package name with version (e.g., "laboneq==2.44.0")
    elif "==" in package_input:
      package_name, version = package_input.split("==")
      return package_name.strip(), version.strip()
    # If no version is specified
    else:
      return package_input.strip(), None

  def clone_repo(self):
    """Clone the repository into the specified folder."""
    whl_save_path = os.path.join(self.repo_save_path, "wheel")
    codebase_save_path = os.path.join(self.repo_save_path, "codebase")
    self.logger.info(f"Cloning repository: {self.package_name} to {codebase_save_path}")

    if not self._clean_directory(codebase_save_path) or not self._clean_directory(whl_save_path):
      return False

    process = None
    stderr = None
    try:
      # Parse the package name and version
      package_name, version = self._parse_package_and_version(self.package_name)
      # Construct the package name with version (e.g., "laboneq==2.44.0")
      package_with_version = f"{package_name}=={version}" if version else package_name

      # Step 1: Download the .whl package using the pip download command
      process = subprocess.Popen(
        ["pip", "download", package_with_version, "-d", whl_save_path, "--no-deps"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
      )

      _, stderr = process.communicate(timeout=self.timeout)

      if process.returncode != 0:
        self.logger.error(f"Failed to download package: {stderr.decode()}")
        return False

      # Step 2: Find the downloaded .whl file
      whl_files = [f for f in os.listdir(whl_save_path) if f.endswith(".whl")]
      if not whl_files:
        self.logger.error("No .whl file found in the download directory.")
        return False

      # Step 3: Extract the first .whl file found
      whl_path = os.path.join(whl_save_path, whl_files[0])
      if not self._extract_whl_file(whl_path, codebase_save_path):
        return False

      self.logger.info(f"Repository cloned successfully to {codebase_save_path}")
      return True

    except subprocess.TimeoutExpired:
      self.logger.error(f"Cloning repository timed out after {self.timeout} seconds.")
      return False

    except subprocess.CalledProcessError as e:
      self.logger.error(f"Failed to clone repository: {e}")
      if self.logger.log_error_details:
        self.logger.error(f"Error details: {stderr.decode().strip()}")
      return False

    except Exception as e:
      self.logger.error(f"Unexpected error: {e}")
      if self.logger.log_error_details:
        self.logger.error(f"Error details: {stderr.decode().strip()}")
      return False

    finally:
      if process:
        self.terminate_process(process.pid)

  def terminate_process(self, pid):
    """Kill all processes spawned from the given process ID."""
    try:
      parent = psutil.Process(pid)
      children = parent.children(recursive=True)
      for child in children:
        child.terminate()
      psutil.wait_procs(children, timeout=5)
      parent.terminate()
      self.logger.info(f"Terminated all spawned processes for PID {pid}")
    except psutil.NoSuchProcess:
      # self.logger.warning(f"Process {pid} already terminated.")
      pass
    except Exception as e:
      self.logger.error(f"Error while terminating process tree for PID {pid}: {e}")
