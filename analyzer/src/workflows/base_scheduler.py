import os
import yaml
import shutil
import logging
import psutil
from utils.config import Config
from utils.logger import LoggerFactory
from utils.helper import resolve_repo_name, cleanup_folders
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Manager

class BaseScheduler:
  def __init__(self, config_path):
    self.config = Config(config_path)

    self.workspace = self.config.SCHEDULER.WORKSPACE
    self.test_name = self.config.SCHEDULER.TEST_NAME
    self.mode = self.config.SCHEDULER.MODE
    self.max_workers = self.config.SCHEDULER.MAX_WORKER

    if self.mode == "list":
      self.repo_list_path = self.config.SCHEDULER.REPO_LIST
      self.url_list_from = self.config.SCHEDULER.URL_LIST_FROM
      self.url_list_to = self.config.SCHEDULER.URL_LIST_TO
    
    manager = Manager()
    self.lock = manager.Lock()
    self.completed_repos = manager.Value('i', 0)
    self.total_repos = len(self.get_repo_urls())

    os.makedirs(self.workspace, exist_ok=True)
    self.setup_logger()

  def setup_logger(self):
    """ Setup logger """
    LoggerFactory.initialize(self.workspace, self.config)
    self.logger = LoggerFactory.get_logger("Scheduler", global_logger_folder="scheduler", global_level=logging.INFO)

  def get_repo_urls(self):
    """Get the list of repository URLs based on the mode."""
    if self.mode == "list":
      with open(self.repo_list_path, "r") as f:
        urls = f.read().splitlines()
      return urls[self.url_list_from:self.url_list_to]
    else:
      return [self.config.SCHEDULER.REPO]

  def setup_workspace_for_repo(self, repo_url):
    """Setup the workspace for the repository."""
    repo_name = resolve_repo_name(repo_url)
    repo_workspace_path = os.path.join(self.workspace, 'output', repo_name)
    os.makedirs(repo_workspace_path, exist_ok=True)

    return repo_workspace_path

  def cleanup_folders(self, folder_path):
    """Removes a directory."""
    if os.path.exists(folder_path):
      shutil.rmtree(folder_path)

  def schedule_tasks(self):
    """
    Schedule the tasks for running CodeQL queries on repositories.
    """
    repo_urls = self.get_repo_urls()
    if not repo_urls:
      self.logger.error("No repositories to process.")
      return

    self.logger.info(f"Scheduling tasks for {len(repo_urls)} repositories with {self.max_workers} workers.")
    
    # Spawn workers in different processes to avoid GIL issues and manage resources efficiently.
    with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
      future_to_repo = {executor.submit(self.spawn_worker, repo): repo for repo in repo_urls}

      for future in as_completed(future_to_repo):
        repo = future_to_repo[future]
        try:
          future.result()
        except Exception as e:
          self.logger.error(f"Error in worker for repo: {repo} - {e}")

  def spawn_worker(self, repo_url):
    """Placeholder method to be implemented in the child class."""
    raise NotImplementedError("spawn_worker must be implemented in a subclass.")

  def kill_all_spawn_processes(self):
    """Kills all child processes spawned by the worker."""
    parent = psutil.Process(os.getpid())
    for child in parent.children(recursive=True):
      self.logger.warning(f"Terminating process: {child.pid}")
      child.terminate()

    gone, still_alive = psutil.wait_procs(parent.children(), timeout=5)
    for p in still_alive:
      self.logger.warning(f"Forcing kill on process: {p.pid}")
      p.kill()
  
  def increment_completed_repos(self):
    """Safely increment the completed repo count across processes."""
    with self.lock:
      self.completed_repos.value += 1
      self.logger.info(f"Progress: {self.completed_repos.value}/{self.total_repos} repositories scanned.")
  
  @staticmethod
  def resolve_repo_name(repo_url):
    if repo_url.endswith(".git"):
      return repo_url.split("/")[-1].replace(".git", "")
    return repo_url.split("/")[-1]
