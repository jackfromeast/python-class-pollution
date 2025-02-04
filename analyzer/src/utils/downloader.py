import os
import json
import yaml
import glob
import time
import shutil
import zipfile
import subprocess
from utils.logger import LoggerFactory
from argparse import ArgumentParser

def download(repo_url, repo_save_path, pip=False):
  if pip:
    downloader = PipDownloader(repo_url, repo_save_path)
  else:
    downloader = GithubDownloader(repo_url, repo_save_path)
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
    
    try:
      subprocess.check_call(
        ["git", "clone", self.repo_url, codebase_save_path],
        timeout=self.timeout
      )
      self.logger.info(f"Repository cloned successfully to {codebase_save_path}")
      return True
    except subprocess.TimeoutExpired:
      self.logger.error(f"Cloning repository timed out after {self.timeout} seconds.")
      return False
    except subprocess.CalledProcessError as e:
      self.logger.error(f"Failed to clone repository: {e}")
      return False


class PipDownloader:
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

  def clone_repo(self):
    """Clone the repository into the specified folder."""
    whl_save_path = os.path.join(self.repo_save_path, "wheel")
    codebase_save_path = os.path.join(self.repo_save_path, "codebase")
    self.logger.info(f"Cloning repository: {self.package_name} to {codebase_save_path}")

    if not self._clean_directory(codebase_save_path) or not self._clean_directory(whl_save_path):
      return False
    
    try:
      ## 1/ Download the .whl package using the pip download command
      ## pip download <package-name> -d <download-dir> --no-deps
      subprocess.check_call(
        ["pip", "download", self.package_name, "-d", whl_save_path, "--no-deps"],
        timeout=self.timeout
      )

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
      return False
