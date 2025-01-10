"""
@description
---------------------
This script helps to run the codeql on a given Github url.

@usage
---------------------
python run.py --repo <repo-url> --work-path <work-path> --config <path-to-config>

e.g.,
python3 run.py --repo https://github.com/dgilland/pydash.git --work-path /home/jackfromeast/Desktop/python-class-pollution/tasks/codeql-class-pollution-1K/output --config /home/jackfromeast/Desktop/python-class-pollution/codeql/driver/config.yaml 
"""

import os
import log
import json
import yaml
import glob
import time
import shutil
import subprocess
from download import GithubDownloader, PipDownloader
from argparse import ArgumentParser

logger = None # Global logger
global_logger = None # Share with the scheduler
result_logger = None # Share with the scheduler

def load_config(config_path):
  with open(config_path, "r") as f:
    return yaml.safe_load(f)

def setup_folder(work_path, repo_url):
  repo_save_path = os.path.join(work_path, repo_url.split("/")[-1].replace(".git", ""))
  log_save_path = os.path.join(repo_save_path, "logs")
  codebase_save_path = os.path.join(repo_save_path, "codebase")
  os.makedirs(repo_save_path, exist_ok=True)
  os.makedirs(log_save_path, exist_ok=True)
  os.makedirs(codebase_save_path, exist_ok=True)
  return repo_save_path

def cleanup_folders(folder_path):
  if os.path.exists(folder_path):
    try:
      subprocess.run(['rm', '-rf', folder_path], check=True)
      print(f"Successfully deleted: {folder_path}")
    except subprocess.CalledProcessError as e:
      print(f"Error deleting {folder_path}: {e}")


class CodeQLRunner:
  """
  This class helps to run the CodeQL queries on a given downloaded repository.
  The codebase is saved at the `repo_save_path/codebase`.
  """
  def __init__(self, repo, repo_save_path, config):
    self.repo = repo
    self.repo_save_path = repo_save_path
    self.codeql_config = {
      "cli": config["CODEQL"]["CLI"],
      "threads": config["CODEQL"]["THREADS"],
      "ram": config["CODEQL"]["RAM"],
      "timeout": config["CODEQL"]["TIMEOUT"]
    }
    self.queries = config["QUERIES"]

    self.codebase_path = os.path.join(repo_save_path, "codebase")
    self.db_path = os.path.join(repo_save_path, "codeql-db")
    self.results_dir = os.path.join(repo_save_path, "results")
    os.makedirs(self.results_dir, exist_ok=True)

    self.delete_after_query = config["DELETE_AFTER_QUERY"]
    self.delete_if_no_flows = config["DELETE_IF_NO_FLOWS"]

  def build(self):
    """
    Build CodeQL database for the `repo_save_path/codebase`
    """
    logger.info(f"Building CodeQL database for: {self.codebase_path}")
    try:
      subprocess.check_call(
        [
          self.codeql_config["cli"], "database", "create", self.db_path,
          "--source-root", self.codebase_path,
          "--language=python",
          f"--threads={self.codeql_config['threads']}",
          f"--ram={self.codeql_config['ram']}",
          "--overwrite"
        ],
        timeout=self.codeql_config["timeout"]
      )
      logger.info(f"CodeQL database created successfully at {self.db_path}")
      return True
    except subprocess.TimeoutExpired:
      logger.error("Building CodeQL database timed out.")
      global_logger.error("Building CodeQL database timed out.")
      return False
    except subprocess.CalledProcessError as e:
      logger.error(f"Failed to build CodeQL database: {e}")
      global_logger.error(f"Failed to build CodeQL database: {e}")
      return False

  def stop_codeql_process(self, db_path):
    """
    Stop the CodeQL process that is still using the database path.
    """
    try:
      result = subprocess.run(
        ["lsof", "+D", db_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
      )
      
      # Parse the lsof output to extract PIDs
      pids = set()
      for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) > 1 and parts[1].isdigit():  # PID is in the second column
          pids.add(int(parts[1]))

      if not pids:
        logger.info(f"No processes found using {db_path}.")
        return

      # Terminate the processes using the database path
      for pid in pids:
        try:
          # os.kill(pid, 9)  # Send SIGTERM to gracefully terminate
          logger.info(f"Terminated process with PID {pid} using {db_path}")
        except OSError as e:
          logger.warning(f"Failed to terminate process with PID {pid}: {e}")

    except FileNotFoundError:
      logger.error("lsof command not found. Please install lsof to use this feature.")
      global_logger.error("lsof command not found. Please install lsof to use this feature.")
    except Exception as e:
      logger.error(f"Error while stopping CodeQL process: {e}")
      global_logger.error(f"Error while stopping CodeQL process: {e}")

  def cleanup(self, everything=False):
    """
    Remove the CodeQL database and codebase after running the queries.
    """
    logger.info("Cleaning up CodeQL database and codebase...")
    try:
      self.stop_codeql_process(self.db_path)
      if everything:
        if os.path.exists(self.repo_save_path):
          cleanup_folders(self.repo_save_path)
          logger.info(f"Removed repo directory at {self.repo_save_path} as no flows detected.")
      else:
        if os.path.exists(self.db_path):
          cleanup_folders(self.db_path)
          logger.info(f"Removed CodeQL database at {self.db_path}")
        if os.path.exists(self.codebase_path):
          cleanup_folders(self.codebase_path)
          logger.info(f"Removed codebase at {self.codebase_path}")
    except Exception as e:
      logger.error(f"Failed during cleanup: {e}")
      global_logger.error(f"Failed during cleanup: {e}")

  def run_queries(self):
    """
    Run the CodeQL queries on the CodeQL database.
    """
    logger.info(f"Running CodeQL queries on database: {self.db_path}")
    for query_file in self.queries:
      output_file = os.path.join(
        self.results_dir, f"{os.path.basename(query_file)}.sarif"
      )
      logger.info(f"Running query: {query_file}")
      if not self.run_single_query(query_file, output_file):
        logger.error(f"Failed to run query: {query_file}")
      else:
        logger.info(f"Query completed successfully: {query_file}")
    
    self.summarize_results(os.path.join(self.results_dir, "summary.json"))

    if self.delete_if_no_flows:
      # Delete the database and codebase if no flows are detected
      summary_file = os.path.join(self.results_dir, "summary.json")
      if os.path.exists(summary_file):
        with open(summary_file, "r") as f:
          summary = json.load(f)
        if all([v == 0 for v in summary.values()]):
          logger.info("No flows detected. Cleaning up...")
          self.cleanup(everything=True)
      else:
        logger.info("No flows detected. Cleaning up...")
        self.cleanup(everything=True)

    if self.delete_after_query:
      self.cleanup()

  def run_single_query(self, query_file, output_file):
    """
    Run a single CodeQL query on the CodeQL database.
    """
    try:
      subprocess.check_call(
        [
          self.codeql_config["cli"], "database", "analyze", self.db_path,
          query_file,
          "--format=sarif-latest",
          f"--threads={self.codeql_config['threads']}",
          f"--ram={self.codeql_config['ram']}",
          f"--timeout={self.codeql_config['timeout']}",
          "--output", output_file,
        ],
        timeout=self.codeql_config["timeout"]
      )
      logger.info(f"Query {query_file} executed successfully. Results saved to {output_file}")
      return True
    
    except subprocess.TimeoutExpired:
      # Wait for 10 seconds before killing the process
      logger.error(f"Query {query_file} timed out.")
      global_logger.error(f"Query {query_file} timed out.") 
      return False
    
    except subprocess.CalledProcessError as e:
      logger.error(f"Failed to execute query {query_file}: {e}")
      global_logger.error(f"Failed to execute query {query_file}: {e}")
      return False
  
  def summarize_results(self, output_file="summary.json"):
    """
    Summarize the results of the CodeQL queries by counting the number of detected flows
    and save the summary to a JSON file.
    
    Args:
        output_file (str): Path to the JSON file where the summary will be saved.
    """
    logger.info("Summarizing CodeQL results...")
    summary = {}
    results_files = glob.glob(os.path.join(self.results_dir, "*.sarif"))

    if not results_files:
      logger.info("No results files found to summarize.")
      return

    for result_file in results_files:
      try:
        with open(result_file, "r") as f:
          sarif_data = json.load(f)
        
        runs = sarif_data.get("runs", [])
        flow_count = 0
        for run in runs:
          results = run.get("results", [])
          flow_count += len(results)
        
        query_name = os.path.basename(result_file)
        summary[query_name] = flow_count
        logger.info(f"Processed {result_file}: {flow_count} flows detected.")
      except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to process {result_file}: {e}")
        global_logger.error(f"Failed to process {result_file}: {e}")

    try:
      with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)
      logger.info(f"Summary saved to {output_file}")
    except Exception as e:
      logger.error(f"Failed to save summary to {output_file}: {e}")
      global_logger.error(f"Failed to save summary to {output_file}: {e}")

    # Output the summary to the result logger
    for query_name, flow_count in summary.items():
      if flow_count > 0:
        result_logger.info(f"{self.repo} - {query_name}: {flow_count} flows detected.")

    return summary


def main():
  parser = ArgumentParser(description="Run CodeQL pipeline for multiple repositories.")
  parser.add_argument("--repo", required=True, help="Repo GitHub URL or pip package name.")
  parser.add_argument("--work-path", required=True, help="Path to the working directory.")
  parser.add_argument("--config", required=True, help="Path to the config file.")
  parser.add_argument("--pip", action="store_true", help="Use pip to download the repository.")
  args = parser.parse_args()

  config = load_config(args.config)["WORKER"]
  repo_save_path = setup_folder(args.work_path, args.repo)

  global logger, global_logger, result_logger
  logger = log.get_logger("WORKER", os.path.join(repo_save_path, "logs"))
  global_logger = log.get_logger("WORKER_GLOBAL", os.path.join(args.work_path, "../", "logs", "worker"), level=log.logging.ERROR, clear_log=False)
  result_logger = log.get_logger("WORKER_RESULT", os.path.join(args.work_path, "../", "logs", "result"), level=log.logging.INFO, clear_log=False)

  if args.pip:
    downloader = PipDownloader(args.repo, repo_save_path, logger, global_logger)
  else:
    downloader = GithubDownloader(args.repo, repo_save_path, logger, global_logger)

  if not downloader.clone_repo():
    logger.error(f"Failed to clone repository: {args.repo}")
    cleanup_folders(repo_save_path)
    return
  
  runner = CodeQLRunner(args.repo, repo_save_path, config)
  if not runner.build():
    logger.error(f"Failed to build CodeQL database for: {args.repo}")
    cleanup_folders(repo_save_path)
    return
  
  runner.run_queries()
  logger.info(f"CodeQL pipeline completed for: {args.repo}")


if __name__ == "__main__":
  main()
