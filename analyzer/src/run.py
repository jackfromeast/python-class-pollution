from workflows.run_cp_analysis import ClassPollutionAnalysis
from argparse import ArgumentParser

def main():
  parser = ArgumentParser(description="Schedule tasks for running CodeQL queries.")
  parser.add_argument("--workflow", required=True, help="The workflow to run.")
  parser.add_argument("--config", required=True, help="Path to the config file.")
  args = parser.parse_args()

  if args.workflow == "class_pollution":
    scheduler = ClassPollutionAnalysis(args.config)

  scheduler.schedule_tasks()

if __name__ == "__main__":
  main()