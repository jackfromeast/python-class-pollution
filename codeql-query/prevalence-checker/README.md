# 📦 Query Overview

This directory contains CodeQL queries for identifying **reflected get and set operations** in Python, including those from built-in functions and standard libraries. These queries are organized to align with **Table 1 and Table 2** of the paper.

---

## 📁 `query/getattr/`: Attribute-Based Get Operations

|  # | Pattern                              | Query File                   |
| -: | ------------------------------------ | ---------------------------- |
|  1 | `getattr(obj, name)`                 | `GetAttrBuiltin.ql`          |
|  2 | `obj.__getattribute__(name)`         | `GetAttrDunder.ql`           |
|  3 | `object.__getattribute__(obj, name)` | `ObjectGetAttrDunder.ql`     |
|  4 | `inspect.getattr_static(obj, name)`  | `InspectGetAttrStatic.ql`    |
|  5 | `operator.attrgetter(name)(obj)`     | `OperatorAttrGetter.ql`      |
|  6 | `dir(obj)[index]`                    | `DirAccessAttr.ql`           |
|  7 | `vars(obj)[name]`                    | `VarsAccessAttr.ql`          |
|  8 | `obj.__dict__[name]`                 | `DictDunderGetAttr.ql`       |
|  9 | `inspect.getmembers(obj)`            | `InspectGetMembers.ql`       |
| 10 | `inspect.getmembers_static(obj)`     | `InspectGetMembersStatic.ql` |

---

## 📁 `query/getitem/`: Item-Based Get Operations

|  # | Pattern                           | Query File |
| -: | --------------------------------- | ---------- |
| 11 | `dict[key]`                       | `GetItemSubscript.ql`    |
| 12 | `dict.get(key)`                   | `DictGet.ql`             |
| 13 | `dict.pop(key)`                   | `DictPop.ql`             |
| 14 | `dict.__getitem__(key)`           | `GetItemDunder.ql`       |
| 15 | `operator.getitem(dict, key)`     | `OperatorGetItem.ql`     |
| 16 | `operator.__getitem__(dict, key)` | `OperatorGetItemDunder.ql`   |
| 17 | `operator.itemgetter(key)(dict)`  | `OperatorItemGetter.ql`  |

---

## 📁 `query/setter/`: Set Operations

|  # | Pattern                                | Query File |
| -: | -------------------------------------- | ---------- |
|  1 | `setattr(obj, name, val)`              | `SetAttrBuiltin.ql`     |
|  2 | `obj.__setattr__(name,val)`            | `SetAttrDunder.ql`      |
|  3 | `object.__setattr__(obj, name, val)`   | `ObjectSetAttrDunder.ql`    |
|  4 | `obj.__dict__[name] = val`             | `DictDunderSetAttr.ql`  |
|  5 | `dict[key] = val`                      | `SetItemSubscript.ql`   |
|  6 | `dict.setdefault(key, val)`            | `DictSetDefault.ql`  |
|  7 | `dict.update(key=val)`                 | `DictUpdate.ql`      |
|  8 | `dict.__setitem__(key, val)`           | `DictDunderSetItem.ql`        |
|  9 | `operator.setitem(dict, key, val)`     | `OperatorSetItem.ql`    |
| 10 | `operator.__setitem__(dict, key, val)` | `OperatorSetItemDunder.ql`  |

---

## 📁 `query/`: Eval and Exec Patterns

Captured in: `GetEvalOrExec.ql`

|  # | Pattern                     | Category | Query File         |
| -: | --------------------------- | -------- | ------------------ |
| 18 | `eval(f"EXPR", {"o": obj})` | Getter   | `GetEvalOrExec.ql` |
| 19 | `exec(f"EXPR", {"o": obj})` | Getter   | `GetEvalOrExec.ql` |
| 11 | `exec(f"EXPR", {"o": obj})` | Setter   | `GetEvalOrExec.ql` |

---

## 📁 `shared/`, `dependency/`, and `vuln/`

These directories follow structures similar to their counterparts in the [`class-pollution-all`](../class-pollution-all) package.

### ✏️ Modifications

* `shared/GetOp.qll`
* `shared/SetOp.qll`
* `shared/types/DunderDictObject.qll`

### ➕ Additions

* `shared/types/DirObject.qll`
* `shared/types/VarsObject.qll`
* `shared/types/OperatorAttrGetter.qll`
* `shared/types/OperatorItemGetter.qll`
