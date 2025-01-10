"""
@description
---------------------
This script helps to schedule the tasks for running the CodeQL queries based on a list of GitHub repository URLs.

@usage
---------------------
```python scheduler.py --config <path-to-config>```
"""

import os
import log
import yaml
import shutil
import subprocess
from argparse import ArgumentParser
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = None


class Scheduler:
  def __init__(self, config_path):
    self.config_path = config_path
    self.config = self.load_config(config_path)
    self.workspace = self.config["SCHEDULER"]["WORKSPACE"]
    self.test_name = self.config["SCHEDULER"]["TEST_NAME"]
    self.mode = self.config["SCHEDULER"]["MODE"]
    self.use_pip = self.config["SCHEDULER"]["USE_PIP"]
    self.repo_list_path = self.config["SCHEDULER"]["REPO_LIST"]
    self.url_list_from = self.config["SCHEDULER"]["URL_LIST_FROM"]
    self.url_list_to = self.config["SCHEDULER"]["URL_LIST_TO"]
    self.max_workers = self.config["SCHEDULER"]["MAX_WORKER"]
    self.timeout_per_worker = self.config["SCHEDULER"]["TIMEOUT_PER_WORKER"]
    self.run_script_path = "run.py"
    self.lock = Lock()  # Lock for thread-safe progress updates
    self.completed_repos = 0  # Counter for completed repositories
    self.total_repos = len(self.get_repo_urls())

    os.makedirs(self.workspace, exist_ok=True)

    global logger
    os.makedirs(os.path.join(self.workspace, "../", "logs"), exist_ok=True)
    logger = log.get_logger("SCHEDULER", os.path.join(self.workspace, "../", "logs"))

  def load_config(self, config_path):
    """Load the configuration file."""
    with open(config_path, "r") as f:
      return yaml.safe_load(f)

  def get_repo_urls(self):
    """Get the list of repository URLs based on the mode."""
    if self.mode == "list":
      with open(self.repo_list_path, "r") as f:
        urls = f.read().splitlines()
      return urls[self.url_list_from:self.url_list_to]
    else:
      return [self.config["SCHEDULER"]["REPO"]]

  def spawn_worker(self, repo_url):
    """
    Spawn a worker process to run CodeQL queries on a repository.
    """
    logger.info(f"Starting worker for repo: {repo_url}")
    try:
      command = [
        "python", self.run_script_path,
        "--repo", repo_url,
        "--work-path", self.workspace,
        "--config", self.config_path,
      ]

      if self.use_pip:
        command.append("--pip")

      subprocess.check_call(
        command,
        timeout=self.timeout_per_worker
      )
      logger.info(f"Worker completed successfully for repo: {repo_url}")

    except subprocess.TimeoutExpired:
      repo_save_path = os.path.join(self.workspace, repo_url.split("/")[-1].replace(".git", ""))
      self.cleanup_folders(repo_save_path)
      logger.error(f"Worker timed out for repo: {repo_url}")

    except subprocess.CalledProcessError as e:
      repo_save_path = os.path.join(self.workspace, repo_url.split("/")[-1].replace(".git", ""))
      self.cleanup_folders(repo_save_path)
      logger.error(f"Worker failed for repo: {repo_url} with error: {e}")

    except Exception as e:
      repo_save_path = os.path.join(self.workspace, repo_url.split("/")[-1].replace(".git", ""))
      self.cleanup_folders(repo_save_path)
      logger.error(f"Unexpected error for repo: {repo_url}: {e}")

    finally:
      # Update progress counter
      with self.lock:
        self.completed_repos += 1
        logger.info(f"Progress: {self.completed_repos}/{self.total_repos} repositories scanned.")

  def schedule_tasks(self):
    """
    Schedule the tasks for running CodeQL queries on repositories.
    """
    repo_urls = self.get_repo_urls()
    if not repo_urls:
      logger.error("No repositories to process.")
      return

    logger.info(f"Scheduling tasks for {len(repo_urls)} repositories with {self.max_workers} workers.")
    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
      future_to_repo = {executor.submit(self.spawn_worker, repo): repo for repo in repo_urls}

      for future in as_completed(future_to_repo):
        repo = future_to_repo[future]
        try:
          future.result()
        except Exception as e:
          logger.error(f"Error in worker for repo: {repo} - {e}")
  
  def cleanup_folders(self, folder_path):
    if os.path.exists(folder_path):
      shutil.rmtree(folder_path)


def main():
  parser = ArgumentParser(description="Schedule tasks for running CodeQL queries.")
  parser.add_argument("--config", required=True, help="Path to the config file.")
  args = parser.parse_args()

  scheduler = Scheduler(args.config)
  scheduler.schedule_tasks()

if __name__ == "__main__":
  main()
