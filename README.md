## Python Class Pollution Vulnerability and its Gadgets

> A snake in the (polluted) grass

This repository contains a list of package that are vulnerable to class pollution (i.e., prototype pollution in python) and class pollution gadgets that can result in severe issues like RCE.

| Library | Stars | Version | Payloads | Found By | Status | CVE |
|:-------:|:-----:|:-------:|----------|:--------:|:------:|:---:|
| [deepdiff](https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/deepdiff.md) | 2K | v8.0.0 | ```{"attribute_added" {"root['x']"namedtuple, "root['x'].'__globals__'['_sys'].'__name__'""polluted"}}``` | chilaxan | Accepted | CVE-2024-5254 |
