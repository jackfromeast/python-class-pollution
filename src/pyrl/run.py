from argparse import ArgumentParser
from pyrl.utils.config import load_config, get_workflow_from_config

def main():
    parser = ArgumentParser(description="Schedule tasks for running CodeQL queries.")
    parser.add_argument("--workflow", required=False, help="The workflow to run.")
    parser.add_argument("--config", required=True, help="Path to the config file.")
    args = parser.parse_args()

    config = load_config(args.config)

    if args.workflow:
        workflow = args.workflow
    else:
        workflow = get_workflow_from_config(config)

    if workflow == "class_pollution":
        from pyrl.workflows.run_cp_analysis import ClassPollutionAnalysis
        scheduler = ClassPollutionAnalysis(args.config)
    elif workflow == "dependency_analysis":
        from pyrl.workflows.run_dependency_analysis import DependencyAnalysis
        scheduler = DependencyAnalysis(args.config)
    else:
        raise ValueError("Unknown workflow: {}".format(workflow))

    try:
        scheduler.schedule_tasks()
    except Exception as e:
        scheduler.kill_all_spawn_processes()
        scheduler.logger.error("scheduler terminated: {}".format(e))

if __name__ == "__main__":
    main()
