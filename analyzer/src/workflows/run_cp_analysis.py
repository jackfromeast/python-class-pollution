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
from codeql_driver.runner import run_codeql_query
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
      run_codeql_query(repo_url, self.config)
      self.logger.info(f"Worker completed for repo: {repo_url}")

    except TimeoutException:
      repo_save_path = os.path.join(self.workspace, repo_url.split("/")[-1].replace(".git", ""))
      self.kill_all_spawn_processes()

      self.cleanup_folders(repo_save_path)
      self.logger.error(f"Worker timed out for repo: {repo_url}")

    except Exception as e:
      repo_save_path = os.path.join(self.workspace, repo_url.split("/")[-1].replace(".git", ""))
      self.cleanup_folders(repo_save_path)
      self.logger.error(f"Unexpected error for repo: {repo_url}: {e}")

    finally:
      self.increment_completed_repos()


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
