## Python Class Pollution Vulnerability and its Gadgets

> A snake in the (polluted) grass

This repository contains a list of packages that are vulnerable to class pollution (i.e., prototype pollution in Python) and class pollution gadgets that can result in severe issues like RCE.

| Library | Stars | Version | Payloads | Found By | Status | CVE |
|:-------:|:-----:|:-------:|----------|:--------:|:------:|:---:|
| [deepdiff](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/deepdiff/README.md) | 2K | v8.0.0 | ```{"attribute_added" {"root['x']"namedtuple, "root['x'].'__globals__'['_sys'].'__name__'""polluted"}}``` | chilaxan | Accepted | CVE-2024-5254 |
| [glom](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/glom/poc/README.md) | 1.9K | v24.11.0 | ```glom.assign(obj, '__init__.__globals__.__name__', 'polluted')``` | BlackPyrl | Pending | N/A |
