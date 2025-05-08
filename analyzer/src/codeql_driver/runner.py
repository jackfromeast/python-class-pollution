"""
@description
---------------------
This script helps to run the codeql on a given Github URL/PyPL package name.

@usage
---------------------
python run.py --repo <repo-url> --work-path <work-path> --config <path-to-config>

e.g.,
python3 run.py --repo https://github.com/dgilland/pydash.git --work-path /home/jackfromeast/Desktop/python-class-pollution/tasks/codeql-class-pollution-1K/output --config /home/jackfromeast/Desktop/python-class-pollution/codeql/driver/config.yaml 
"""

import os
import json
import glob
import psutil
import subprocess
from .exceptions import CodeQLDriverExceptions
from utils.logger import LoggerFactory
from utils.config import Config
from utils.helper import resolve_repo_name, cleanup_folders, resolve_relative_path
from utils.downloader import GithubDownloader, PipDownloader
from argparse import ArgumentParser

class CodeQLRunner:
  """
  This class helps to run the CodeQL queries on a given downloaded repository.
  Given a work directory and a CodeQL configuration, it builds the CodeQL database and runs the queries.

  @param work_dir (str): Path to the working directory. It assume the codebase is saved in `work_dir/codebase`.
  @param queries (list): List of CodeQL queries to run.
  @param codeql_config (dict): Configuration for CodeQL CLI.
  @param delete_after_query (bool): Whether to delete the CodeQL database and codebase after running the queries.
  @param delete_if_no_flows (bool): Whether to delete the CodeQL database and codebase if no flows are detected.
  @param timeout (int): Timeout for running the CodeQL queries.
  """
  def __init__(self, work_dir, queries, codeql_config, delete_after_query=False, delete_if_no_flows=True, timeout=None):
    self.repo_name = os.path.basename(work_dir)
    self.work_dir = work_dir
    self.codeql_config = codeql_config
    self.queries = queries
    self.logger = LoggerFactory.get_logger("CodeQLRunner", local_logger_folder=os.path.join(work_dir, "logs"), result_logger=True)

    self.codebase_path = os.path.join(self.work_dir , "codebase")
    self.db_path = os.path.join(self.work_dir , "codeql-db")
    self.results_dir = os.path.join(self.work_dir , "results")
    self.work_folder_sanity_check()

    self.delete_after_query = delete_after_query
    self.delete_if_no_flows = delete_if_no_flows
    self.timeout = timeout if timeout else self.codeql_config.TIMEOUT

    self.setup_cli()

  def setup_cli(self):
    """
    Setup the CodeQL CLI path.
    """
    if not os.path.exists(self.codeql_config.CLI):
      # use which codeql to check its path
      cli = subprocess.run(["which", "codeql"], stdout=subprocess.PIPE, text=True).stdout.strip()
      if not cli:
        self.logger.error("CodeQL CLI not found in PATH.")
        return False
      self.cli = cli
    else:
      self.cli = self.codeql_config.CLI

  def work_folder_sanity_check(self):
    if not os.path.exists(self.codebase_path):
      self.logger.error(f"Codebase path does not exist: {self.codebase_path}")
      return False
    if os.path.exists(self.db_path):
      self.logger.warning(f"CodeQL database path already exists: {self.db_path}")
      return False
    os.makedirs(self.results_dir, exist_ok=True)
    return True

  def build(self):
    """
    Build CodeQL database for the `self.work_dir/codebase`
    """
    self.logger.info(f"Building CodeQL database for: {self.codebase_path}")

    process = None
    stderr = None
    try:
      process = subprocess.Popen(
        [
          self.cli, "database", "create", self.db_path,
          "--source-root", self.codebase_path,
          "--language=python",
          f"--threads={self.codeql_config.THREADS}",
          f"--ram={self.codeql_config.RAM}",
          "--overwrite"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
      )

      _, stderr = process.communicate(timeout=self.timeout)

      if process.returncode == 0:
        self.logger.info(f"CodeQL database created successfully at {self.db_path}")
        return True
      else:
        error_msg = CodeQLDriverExceptions.handle_build_exception(stderr.decode() if stderr else "")
        self.logger.error(f"Failed to build CodeQL database for {self.repo_name}: {error_msg}")
        if (self.logger.log_error_details):
          self.logger.error(f"Error details: {stderr.decode() if stderr else ""}")
        return False

    except subprocess.TimeoutExpired:
      self.logger.error(f"Building CodeQL database timed out: {self.repo_name}")
      return False

    except Exception as e:
      error_msg = CodeQLDriverExceptions.handle_build_exception(stderr.decode() if stderr else "")
      self.logger.error(f"Failed to build CodeQL database for {self.repo_name}: {error_msg}")
      if (self.logger.log_error_details):
        self.logger.error(f"Error details: {stderr.decode() if stderr else ""}")
      return False

    finally:
      if process:
        self.terminate_process(process.pid)

  def cleanup(self, everything=False):
    """
    Remove the CodeQL database and codebase after running the queries.
    """
    self.logger.info("Cleaning up CodeQL database and codebase...")
    try:
      self.terminate_process_by_dbpath(self.db_path)
      if everything:
        if os.path.exists(self.work_dir):
          cleanup_folders(self.work_dir)
          self.logger.info(f"Removed repo directory at {self.work_dir} as no flows detected.")
      else:
        if os.path.exists(self.db_path):
          cleanup_folders(self.db_path)
          self.logger.info(f"Removed CodeQL database at {self.db_path}")
        if os.path.exists(self.codebase_path):
          cleanup_folders(self.codebase_path)
          self.logger.info(f"Removed codebase at {self.codebase_path}")
    except Exception as e:
      self.logger.error(f"Failed during cleanup: {e}")

  def run_queries(self):
    """
    Run the CodeQL queries on the CodeQL database.
    """
    self.logger.info(f"Running CodeQL queries on database: {self.db_path}")
    for query_file in self.queries:
      query_file = resolve_relative_path(query_file)
      if not os.path.exists(query_file):
        self.logger.error(f"Query file not found: {query_file}")
        continue

      output_file = os.path.join(
        self.results_dir, f"{os.path.basename(query_file)}.sarif"
      )
      self.logger.info(f"Running query: {query_file}")
      if not self.run_single_query(query_file, output_file):
        self.logger.error(f"Failed to run query: {query_file}")
      else:
        self.logger.info(f"Query completed successfully: {query_file}")
    
    self.summarize_results(os.path.join(self.results_dir, "summary.json"))

    if self.delete_if_no_flows:
      # Delete the database and codebase if no flows are detected
      summary_file = os.path.join(self.results_dir, "summary.json")
      if os.path.exists(summary_file):
        with open(summary_file, "r") as f:
          summary = json.load(f)
        if all([v == 0 for v in summary["rules"].values()]):
          self.logger.info("No flows detected. Cleaning up...")
          self.cleanup(everything=True)
      else:
        self.logger.info("No flows detected. Cleaning up...")
        self.cleanup(everything=True)

    if self.delete_after_query:
      self.cleanup(everything=True)

  def run_single_query(self, query_file, output_file):
    """
    Run a single CodeQL query on the CodeQL database.
    If any exception occurs, terminate all processes spawned by the CodeQL CLI.
    """
    process = None
    stderr = None
    try:
      command = [
          self.cli, "database", "analyze", self.db_path,
          query_file,
          "--format=sarif-latest",
          f"--threads={self.codeql_config.THREADS}",
          f"--ram={self.codeql_config.RAM}",
          f"--timeout={self.timeout}",
          "--output", output_file,
        ]

      if self.codeql_config.USE_MODEL_PACK:
        model_pack = self.codeql_config.MODEL_PACK
        model_pack_path = resolve_relative_path(self.codeql_config.MODEL_PACK_PATH)

        command.append(f"--model-packs={model_pack}")
        command.append(f"--additional-packs={model_pack_path}")

      process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
      )
      
      _, stderr = process.communicate(timeout=self.timeout)

      if process.returncode == 0:
        self.logger.info(f"Query {query_file} executed successfully. Results saved to {output_file}")
        return True
      else:
        error_msg = CodeQLDriverExceptions.handle_query_exception(stderr.decode() if stderr else "")
        self.logger.error(f"Failed to execute query {query_file}: {error_msg}")
        if (self.logger.log_error_details):
          self.logger.error(f"Error details: {stderr.decode() if stderr else ""}")
        return False

    except subprocess.TimeoutExpired:
      self.logger.error(f"Query timed out for {self.repo_name}: {query_file}")
      return False

    except Exception as e:
      error_msg = CodeQLDriverExceptions.handle_query_exception(stderr.decode() if stderr else "")
      self.logger.error(f"Failed to execute query {query_file} with Exception {e}: {error_msg}")
      if (self.logger.log_error_details):
          self.logger.error(f"Error details: {stderr.decode() if stderr else ""}")
      return False

    finally:
      if process:
          self.terminate_process(process.pid)
  
  def terminate_process(self, pid):
    """
    Kill all processes spawned from the given process ID.
    """
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.terminate()  # Terminate all child processes
        psutil.wait_procs(children, timeout=5)  # Wait for them to terminate
        parent.terminate()  # Finally, terminate the parent process
        self.logger.info(f"Terminated all spawned processes for PID {pid}")
    except psutil.NoSuchProcess:
        # self.logger.warning(f"Process {pid} already terminated.")
        pass
    except Exception as e:
        self.logger.error(f"Error while terminating process tree for PID {pid}: {e}")
  
  def terminate_process_by_dbpath(self, db_path):
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
        self.logger.info(f"No processes found using {db_path}.")
        return

      # Terminate the processes using the database path
      for pid in pids:
        try:
          # os.kill(pid, 9)  # Send SIGTERM to gracefully terminate
          self.logger.info(f"Terminated process with PID {pid} using {db_path}")
        except OSError as e:
          self.logger.warning(f"Failed to terminate process with PID {pid}: {e}")
        except Exception as e:
          self.logger.warning(f"Unexpected error when terminating process with PID {pid}: {e}")

    except FileNotFoundError:
      self.logger.error("lsof command not found. Please install lsof to use this feature.")
    except Exception as e:
      self.logger.error(f"Error while stopping CodeQL process: {e}")

  
  def summarize_results(self, output_file="summary.json"):
    """
    Summarize the results of the CodeQL queries by counting the number of detected flows
    and save the summary to a JSON file.
    
    @param: output_file (str): Path to the JSON file where the summary will be saved.
    """
    self.logger.info("Summarizing CodeQL results...")
    summary = {
      "rules": {},
      "details": set()
    }
    results_files = glob.glob(os.path.join(self.results_dir, "*.sarif"))

    if not results_files:
      self.logger.info("No results files found to summarize.")
      return

    for result_file in results_files:
      try:
        with open(result_file, "r") as f:
          sarif_data = json.load(f)
        
        runs = sarif_data.get("runs", [])
        for run in runs:
          results = run.get("results", [])

          flow_count = 0
          for res in results:
            rule_id = res.get("ruleId", "")
            text_message = res.get("message", "").get("text", "")

            if rule_id not in summary["rules"]:
              summary["rules"][rule_id] = 0
              summary["details"].add(text_message)

            summary["rules"][rule_id] += 1
            summary["details"].add(text_message)
            flow_count += 1
        
        self.logger.info(f"Processed {result_file}: {flow_count} flows detected.")
      except (json.JSONDecodeError, KeyError) as e:
        self.logger.error(f"Failed to process {result_file}: {e}")
      except Exception as e:
        self.logger.error(f"Unexpected error processing {result_file}: {e}")

    try:
      with open(output_file, "w") as f:
        summary["details"] = list(summary["details"])
        json.dump(summary, f, indent=2)
      self.logger.info(f"Summary saved to {output_file}")
    except Exception as e:
      self.logger.error(f"Failed to save summary to {output_file}: {e}")

    # Output the summary to the result logger
    for rule_id, flow_count in summary["rules"].items():
      if flow_count > 0:
        self.logger.info(f"{self.repo_name} - {rule_id}: {flow_count} flows detected.", result=True)

    return summary

def main():
  parser = ArgumentParser(description="Run CodeQL pipeline for multiple repositories.")
  parser.add_argument("--repo", required=True, help="Repo GitHub URL or pip package name.")
  parser.add_argument("--work-path", required=True, help="Path to the working directory.")
  parser.add_argument("--config", required=True, help="Path to the config file.")
  parser.add_argument("--pip", action="store_true", help="Use pip to download the repository.")
  args = parser.parse_args()

  config = Config(args.config)
  
  run_codeql_query(args.repo, config)

if __name__ == "__main__":
  main()
