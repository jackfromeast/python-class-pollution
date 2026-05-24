---
title: "Polluter"
weight: 2
bookCollapseSection: true
---

# Polluter

**Polluter** is a Python library for dynamically discovering and testing class pollution attack surfaces. It recursively explores an object's attribute tree at runtime to identify all accessible (pollutable) attributes and provides utilities to overwrite them for exploitability testing.

## What Polluter Does

- Recursively discovers all accessible attributes of a target object via BFS traversal (supports both `getattr` and `__getitem__` access)
- Summarizes each attribute's type, name, standard-library origin, and writability
- Provides query-based filtering to select pollutables by type, name, or builtin status (e.g., `type=callable`, `builtin=no`)
- Pollutes (overwrites) discovered attributes to test what breaks under class pollution conditions

## Installation

```bash
git clone https://github.com/jackfromeast/python-class-pollution.git
cd python-class-pollution/lib/polluter
pip install -e .
```

### Requirements

- Python 3.10+
- No additional dependencies for the core library

## Usage

### Discovering Pollutable Attributes

```python
from polluter import Pollutable

# Discover all accessible attributes up to 3 layers deep
po = Pollutable(target_obj, max_layer=3, lookup_type="getAttr")

# Use "getBoth" to also traverse __getitem__ access (dicts, lists, etc.)
po = Pollutable(target_obj, max_layer=3, lookup_type="getBoth")
```

### Querying Results

```python
# Select only callable attributes
callables = po.select("type=callable")

# Select non-builtin classes
user_classes = po.select("type=class&builtin=no")

# Select by name
po.select("name=Config")

# Custom filter function
po.select_by_func(lambda type_info, name_info, is_standard, writable: not is_standard)
```

### Polluting Attributes

```python
from polluter import Pollutable, pollute

# Overwrite all attributes of an object with a marker value
pollute(target_obj, default_val="polluted")

# Only overwrite callable attributes
pollute(target_obj, method_only=True, default_val="polluted")
```

### Navigating to a Specific Attribute

```python
po = Pollutable(target_obj, max_layer=3)

# Resolve a dotted/bracketed path to the actual object
obj = po.find("__class__.__init__.__globals__")
```

## Source Code

The Polluter library is located at [`lib/polluter/`](https://github.com/jackfromeast/python-class-pollution/tree/main/lib/polluter) in the repository.
