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
import json
from argparse import ArgumentParser
from codenl import CodeNL
from .base_scheduler import BaseScheduler
from utils.downloader import download
from utils.hard_exceptions import TimeoutException, timeout_handler
from filelock import FileLock

class CodeAnalysisAgent(BaseScheduler):
  def __init__(self, config_path):
    super().__init__(config_path)
    self.timeout_per_worker = self.config.SCHEDULER.TIMEOUT_PER_WORKER
    
  def spawn_worker(self, repo_obj):
    """
    Spawn a worker process to run CodeQL queries on a repository.
    """
    self.setup_logger()
    if not repo_obj:
      return
    repo_url = repo_obj.get("repo")
    self.logger.info(f"Starting worker for repo: {repo_url}")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(self.timeout_per_worker)  # Set alarm for timeout

    repo_workspace_path = self.setup_workspace_for_repo(repo_url)

    try:
      for target_func_obj in repo_obj.get("class_pollution_func", []):
        self.run_code_agent(
          repo_url,
          repo_workspace_path,
          target_func_obj.get("function"),
          target_func_obj.get("location").get("file"),
          target_func_obj.get("location").get("start_line")
          )
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
  
  def run_code_agent(self, repo_url, repo_workspace_path, function_name, file, start_line):
    """
    Run the code analysis agent pipeline for a given repository.
    
    @param repo_url: GitHub URL or pip package name.
    @param repo_workspace_path: Path to the repository workspace.
    """
    if not download(repo_url, repo_workspace_path, codebase_name=""):
      self.logger.error(f"Failed to download codebase for {repo_url}")
      self.cleanup_folders(repo_workspace_path)
      return
    codenl = CodeNL()
    result = codenl.run(function_name, repo_workspace_path, os.path.join(repo_workspace_path, file), start_line)
    if result and isinstance(result, dict):
      result["function_name"] = function_name
      result["repo_name"] = repo_url.split("/")[-1]
      result["repo"] = repo_url
      self.safe_append(result, os.path.join(self.workspace, 'output', 'result.json'))
    self.cleanup_folders(repo_workspace_path)
    return

  def safe_append(self, obj, path="result.json"):
    lock = FileLock(path + ".lock")
    with lock:
      data = []
      if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "r") as f:
          data = json.load(f)
      data.append(obj)
      with open(path, "w") as f:
        json.dump(data, f, indent=2)

def main():
  parser = ArgumentParser(description="Schedule tasks for running CodeQL queries.")
  parser.add_argument("--config", required=True, help="Path to the config file.")
  args = parser.parse_args()

  scheduler = CodeAnalysisAgent(args.config)
  scheduler.schedule_tasks()

if __name__ == "__main__":
  main()
