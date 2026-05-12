# CP-Collection

A collection of Python class pollution vulnerabilities found in open-source projects.

## Directory Structure

Each entry follows this structure:

```
cp-collection/
└── <project-name>/
    ├── README.md          # Metadata + vulnerable code snippet
    └── poc/
        ├── library/       # PoC exploiting the vulnerability via library API
        │   ├── poc.py
        │   ├── requirements.txt
        │   ├── run.sh
        │   └── venv/
        ├── local/         # PoC exploiting the vulnerability via local input (e.g. data files, CLI args)
        │   ├── requirements.txt
        │   ├── run.sh
        │   └── venv/
        └── remote/        # PoC exploiting the vulnerability via remote input (e.g. HTTP, WebSocket)
            ├── app/
            ├── poc-*.py
            ├── requirements.txt
            ├── run.sh
            └── venv/
```

## Entry README Spec

Each project's `README.md` must contain the following sections:

### Metadata

| Field    | Description                                      | Example Values                                              |
|----------|--------------------------------------------------|-------------------------------------------------------------|
| Repo     | Repository name                                  | `Taipy`, `glom`, `pydash`                                   |
| Link     | GitHub repository URL                            | `https://github.com/Avaiga/taipy`                           |
| Stars    | Approximate star count at time of discovery      | `19.2K`                                                     |
| Version  | Vulnerable version tested                        | `v4.0.3`                                                    |
| CVE      | CVE identifier (or `N/A`)                        | `CVE-2025-30374`, `N/A`                                     |
| VulnType | Pollution primitive type (see below)             | `get-attr-set-attr`                                         |
| Status   | Disclosure status                                | `Pending`, `Reported`, `Accepted`, `Fixed`, `Todo`          |
| Foundby  | Discoverer                                       | `Pyrl`                                                      |

### VulnType Values

The `VulnType` field describes the getter/setter primitives used in the vulnerable code path. The format is `get-<getter>-set-<setter>` where:
- `attr` = attribute access (`getattr()` / `setattr()`)
- `item` = item access (`obj[key]` / `obj[key] = val`)
- `both` = both attribute and item access

All possible combinations:

| VulnType             | Getter              | Setter              |
|----------------------|---------------------|---------------------|
| `get-attr-set-attr`  | attr access          | attr access          |
| `get-attr-set-item`  | attr access          | item access          |
| `get-attr-set-both`  | attr access          | attr/item access     |
| `get-both-set-attr`  | attr/item access     | attr access          |
| `get-both-set-item`  | attr/item access     | item access          |
| `get-both-set-both`  | attr/item access     | attr/item access     |

### Vulnerable Code Snippet

The code snippet section should include:
- A brief description of the vulnerable function/pattern
- The actual source code with inline comments explaining the vulnerability

Example format:

```python
# taipy/gui/utils/_attributes.py
def _attrsetter(obj: object, attr_str: str, value: object) -> None:
    var_name_split = attr_str.split(sep=".")  # user-controlled attr_str is split by "."
    for i in range(len(var_name_split) - 1):
        sub_name = var_name_split[i]
        obj = getattr(obj, sub_name)  # traverses the attribute chain without restriction
    setattr(obj, var_name_split[-1], value)  # sets arbitrary attribute on the resolved object
```
