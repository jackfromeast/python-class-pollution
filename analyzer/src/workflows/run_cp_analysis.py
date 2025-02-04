"""
@description
---------------------
This script helps to run the class pollution analysis.

@usage
---------------------
```python3 -m workflows.run_cp_analysis --config <path-to-config>```
"""
import os
import signal
import psutil
from argparse import ArgumentParser
from codeql_driver.runner import CodeQLRunner
from utils.downloader import download
from .base_scheduler import BaseScheduler

class ClassPollutionAnalysis(BaseScheduler):
  def __init__(self, config_path):
    super().__init__(config_path)
    self.timeout_per_worker = self.config.SCHEDULER.TIMEOUT_PER_WORKER

  def spawn_worker(self, repo_url):
    """
    Spawn a worker process to run CodeQL queries on a repository.
    """
    self.logger.info(f"Starting worker for repo: {repo_url}")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(self.timeout_per_worker)  # Set alarm for timeout

    try:
      self.run_codeql_query(repo_url)
      self.logger.info(f"Worker completed for repo: {repo_url}")

    except TimeoutException:
      repo_save_path = os.path.join(self.workspace, repo_url.split("/")[-1].replace(".git", ""))
      self.cleanup_folders(repo_save_path)
      self.logger.error(f"Worker timed out for repo: {repo_url}")

    except Exception as e:
      repo_save_path = os.path.join(self.workspace, repo_url.split("/")[-1].replace(".git", ""))
      self.cleanup_folders(repo_save_path)
      self.logger.error(f"Unexpected error for repo: {repo_url}: {e}")

    finally:
      self.kill_all_spawn_processes()
      self.increment_completed_repos()
  
  def run_codeql_query(self, repo_url):
    """
    Run the CodeQL pipeline for a given repository.
    
    @param repo: GitHub URL or pip package name.
    @param config: Config object.
    """
    repo_workspace_path = self.setup_workspace_for_repo(repo_url)

    if not download(repo_url, repo_workspace_path, pip=self.config.SCHEDULER.PIP):
      self.logger.error(f"Failed to download codebase for {repo_url}")
      self.cleanup_folders(repo_workspace_path)
      return
    
    runner = CodeQLRunner(repo_workspace_path, self.config.CLASS_POLLUTION_ANALYSIS.QUERIES, self.config.CODEQL,
                          delete_after_query=self.config.CLASS_POLLUTION_ANALYSIS.DELETE_AFTER_QUERY,
                          delete_if_no_flows=self.config.CLASS_POLLUTION_ANALYSIS.DELETE_IF_NO_FLOWS)
    
    if not runner.build():
      self.cleanup_folders(repo_workspace_path)
      return
    
    runner.run_queries()
class TimeoutException(Exception):
    """Custom exception for timeout"""
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Analysis Worker timed out.")

def main():
  parser = ArgumentParser(description="Schedule tasks for running CodeQL queries.")
  parser.add_argument("--config", required=True, help="Path to the config file.")
  args = parser.parse_args()

  scheduler = ClassPollutionAnalysis(args.config)
  scheduler.schedule_tasks()

if __name__ == "__main__":
  main()
