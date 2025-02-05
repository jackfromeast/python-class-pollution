from workflows.run_cp_analysis import ClassPollutionAnalysis
from workflows.run_dependency_analysis import DependencyAnalysis
from argparse import ArgumentParser

def main():
  parser = ArgumentParser(description="Schedule tasks for running CodeQL queries.")
  parser.add_argument("--workflow", required=True, help="The workflow to run.")
  parser.add_argument("--config", required=True, help="Path to the config file.")
  args = parser.parse_args()

  if args.workflow == "class_pollution":
    scheduler = ClassPollutionAnalysis(args.config)
  elif args.workflow == "dependency_analysis":
    scheduler = DependencyAnalysis(args.config)

  try:
    scheduler.schedule_tasks()
  except Exception as e:
    scheduler.kill_all_spawn_processes()
    scheduler.logger.error(f"scheduler terminated: {e}")

if __name__ == "__main__":
  main()
