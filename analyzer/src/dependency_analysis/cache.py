"""
@description
---------------------
Manages the cache for the dependency analysis.
"""
import os
import json
import shutil
from utils.logger import LoggerFactory

class Cache:
  """
  This class helps to maintain a cache map for the libraries.

  @param cache_path: The path to the cache file.
  @param log_path: The path to the log file.
  """
  def __init__(self, cache_path, log_path=None):
    self.cache_path = cache_path
    self.logger = LoggerFactory.get_logger("CacheMaintainer", local_logger_folder=log_path)
    self.cache_map = self.load_cache_map()

  def set(self, package_name, data_extension_file_path, package_version="latest", copy_to_cache=True):
    """
    Set a key-value pair in the cache.

    @param package_name: The name of the package.
    @param package_version: The version of the package.
    @param data_extension_file_path: The path to the data file.
    @param copy_to_cache: Whether to copy the data file to the cache.

    copy to the self.cache_path/package_name_package_version.model.yaml
    """
    # Ensure the cache directory exists
    package_cache_dir = os.path.join(self.cache_path, "models")
    package_cache_name = f"{package_name}.{package_version}.model.yaml"
    os.makedirs(package_cache_dir, exist_ok=True)

    # Copy the data extension file to the cache directory if required
    if copy_to_cache:
      destination_path = os.path.join(package_cache_dir, package_cache_name)
      shutil.copy(data_extension_file_path, destination_path)
      self.logger.info(f"Copied data extension file to cache: {destination_path}")
      relative_path = os.path.relpath(destination_path, self.cache_path)
    else:
      relative_path = os.path.relpath(data_extension_file_path, self.cache_path)

    # Update the cache map
    if package_name not in self.cache_map:
      self.cache_map[package_name] = {}
    self.cache_map[package_name][package_version] = relative_path

    # Save the updated cache map
    self.save_cache_map()
    self.logger.info(f"Updated cache map for {package_name} (version: {package_version})")

  def get(self, package_name, package_version="latest"):
    """
    Get the value from the cache.

    @param package_name: The name of the package.
    @param package_version: The version of the package.
    @return data_extension: The data stored in the cache.
    """
    if package_name in self.cache_map and package_version in self.cache_map[package_name]:
      relative_path = self.cache_map[package_name][package_version]
      absolute_path = os.path.join(self.cache_path, relative_path)
      if os.path.exists(absolute_path):
        self.logger.info(f"Cache hit for {package_name} (version: {package_version})")
        return absolute_path
      else:
        self.logger.warning(f"Cache entry for {package_name} (version: {package_version}) is missing. Removing from cache.")
        del self.cache_map[package_name][package_version]
        self.save_cache_map()
    self.logger.info(f"Cache miss for {package_name} (version: {package_version})")
    return None

  def load_cache_map(self):
    """
    Load the cache map from the cache file.

    @return cache_map: The cache map.
    """
    cache_file_path = os.path.join(self.cache_path, "cache.json")
    if os.path.exists(cache_file_path):
      try:
        with open(cache_file_path, "r") as f:
          self.logger.info(f"Loaded cache map from {cache_file_path}")
          return json.load(f)
      except Exception as e:
        self.logger.error(f"Error loading cache map: {e}")
    else:
      self.logger.info("No cache map found. Initializing an empty cache.")
    return {}

  def save_cache_map(self):
    """
    Save the cache map to the cache file.

    save to the self.cache_path/cache.json
    """
    cache_file_path = os.path.join(self.cache_path, "cache.json")
    try:
      with open(cache_file_path, "w") as f:
        json.dump(self.cache_map, f, indent=2)
      self.logger.info(f"Saved cache map to {cache_file_path}")
    except Exception as e:
      self.logger.error(f"Error saving cache map: {e}")