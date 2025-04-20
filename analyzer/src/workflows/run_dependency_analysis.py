"""
@description
---------------------
This script helps to run the dependency analysis.

@usage
---------------------
```python3 -m workflows.run_dependency_analysis --config <path-to-config>```
"""
import os
import signal
import psutil
from argparse import ArgumentParser
from dependency_analysis.analyzer import DependencyAnalyzer
from utils.downloader import download
from utils.hard_exceptions import TimeoutException, timeout_handler
from .base_scheduler import BaseScheduler

class DependencyAnalysis(BaseScheduler):
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

    repo_workspace_path = self.setup_workspace_for_repo(repo_url)

    try:
      self.run_dependency_analysis(repo_url, repo_workspace_path)
      self.logger.info(f"Worker completed for repo: {repo_url}")

    except TimeoutException:
      self.cleanup_folders(repo_workspace_path)
      self.logger.error(f"Worker timed out for repo: {repo_url}")

    except Exception as e:
      self.cleanup_folders(repo_workspace_path)
      self.logger.error(f"Unexpected error for repo: {repo_url}: {e}")

    finally:
      signal.alarm(0)
      self.kill_all_spawn_processes()
      self.increment_completed_repos()

  def run_dependency_analysis(self, repo_url, repo_workspace_path):
    """
    Run the dependency analysis on the specified codebase.
    """
    # Download the codebase
    if not download(repo_url, repo_workspace_path):
      self.logger.error(f"Failed to download codebase for {repo_url}")
      self.cleanup_folders(repo_workspace_path)
      return

    analyzer = DependencyAnalyzer(repo_url, repo_workspace_path, self.config)

    try:
      analyzer.run()
    except Exception as e:
      self.logger.error(f"Error running dependency analysis for {repo_url}: {e}")
      if not self.config.DEPENDENCY_ANALYSIS.DEBUG:
        self.cleanup_folders(repo_workspace_path)
      return

def main():
  parser = ArgumentParser(description="Schedule tasks for running CodeQL queries.")
  parser.add_argument("--config", required=True, help="Path to the config file.")
  args = parser.parse_args()

  scheduler = DependencyAnalysis(args.config)
  scheduler.schedule_tasks()

if __name__ == "__main__":
  main()
