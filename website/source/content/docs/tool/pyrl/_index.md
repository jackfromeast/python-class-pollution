---
title: "Pyrl"
weight: 1
---

# Pyrl

Pyrl (`/pɜːrl/`, "Pearl") is the first automated detection tool for Python class pollution vulnerabilities. It is built on top of CodeQL and introduces a static analysis called *operational taint analysis*, which models the reflective attribute and item operations used by class pollution and tracks attacker-controlled inputs through them with fine-grained, semantic taint labels.

## Key features

- **Detects all six [variants]({{< relref "/docs/taxonomy/primitives" >}})**: Agnostic-Get and Constrained-Get crossed with Dual-Set, Attr-Set, and Item-Set.
- **First-order and second-order operations**: handles both single-expression access (`getattr(obj, name)`) and split access (e.g. `inspect.getmembers(obj)` followed by indexing).
- **Exploitability checking**: rejects findings where the two assignment sites of a Dual-Set sink are not actually reachable through mutually exclusive branches.
- **Barrier-node analysis**: prunes false positives introduced by key sanitization, type checks, or `isinstance` guards.
- **Model pack for third-party libraries**: ships taint summaries for popular Python packages so analysis sees through library boundaries without per-target manual work.
- **Scales to a 671K-package corpus**: linear in AST nodes, typically under two minutes per package, with a 38% false-positive rate against a manual baseline.

## Implementation

Pyrl is written in CodeQL (3,509 lines of new QL on top of the standard library) and runs on CodeQL v2.21.3 with Python language support v4.0.5. The CodeQL standard library is extended for collection data structures (`namedtuple`, `reduce`), object attribute resolution, and data flow through higher-order functions.

## Installation

### Prerequisites

- Python 3.10 or newer
- [CodeQL CLI](https://github.com/github/codeql-cli-binaries) v2.21.3 or newer with Python language support v4.0.5
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/jackfromeast/python-class-pollution.git
cd python-class-pollution

# 2. Install Pyrl and its Python dependencies
uv sync          # recommended
# or
pip install -e .

# 3. Install the CodeQL CLI (Linux example)
wget https://github.com/github/codeql-cli-binaries/releases/download/v2.21.3/codeql-linux64.zip
unzip codeql-linux64.zip
export PATH="$PWD/codeql:$PATH"

# 4. Verify
codeql version
python -m pyrl --help
```

## Usage

Pyrl is a task-based scheduler that drives CodeQL analysis for class pollution detection. You point it at one or more Python packages (a single PyPI or GitHub URL, or a list of URLs), and it builds CodeQL databases, runs the operational-taint queries, and writes structured SARIF results.

### Entrypoint

```bash
pyrl --config /path/to/config.yaml
```

The optional `--workflow` flag overrides the workflow declared in the config:

```bash
pyrl --config config.yaml --workflow class_pollution
pyrl --config config.yaml --workflow dependency_analysis
```

### Configuration

All behavior is governed by a single YAML file. A full annotated template lives at `tmp/analyzer/config-example.yaml` in the repository. The minimal structure:

```yaml
WORKFLOW:
  CLASS_POLLUTION_ANALYSIS: True
  DEPENDENCY_ANALYSIS: False

SCHEDULER:
  TEST_NAME: "my-scan"
  WORKSPACE: "tasks/my-scan"      # results land here

  MODE: "seed"                    # "seed" (single repo), "list", or "json"
  REPO: "https://pypi.org/project/glom"   # used when MODE=seed
  REPO_LIST: "targets.txt"        # used when MODE=list or json
  URL_LIST_FROM: 0                # slice the list (0-indexed)
  URL_LIST_TO: -1                 # -1 = end
  MAX_WORKER: 8                   # parallel workers
  TIMEOUT_PER_WORKER: 1200        # seconds per package

CODEQL:
  CLI: ""                         # path to `codeql`, leave empty to use $PATH
  THREADS: 1
  RAM: 8192                       # MB
  TIMEOUT: 1200
  USE_MODEL_PACK: True
  MODEL_PACK: jackfromeast/class-pollution-model-pack@0.0.1

CLASS_POLLUTION_ANALYSIS:
  QUERIES:
    - "src/pyrl/codeql/class-pollution-all/class-pollution.qls"
  DELETE_AFTER_QUERY: False
  DELETE_IF_NO_FLOWS: True

LOG:
  LOG_PATH: ""                    # default: WORKSPACE/logs
  LOG_TO_CONSOLE: True
  LOG_TO_LOCAL_FILE: True
  LOG_TO_GLOBAL_FILE: True
  LOG_RESULT: True
  LOG_LEVEL: "INFO"
```

| Key | Purpose |
|---|---|
| `SCHEDULER.MODE` | `seed` analyzes the single `REPO`, `list` reads a newline-delimited file at `REPO_LIST`, `json` reads a JSON array. |
| `SCHEDULER.WORKSPACE` | Base directory where CodeQL databases, results, and logs are written. Resolved relative to the project root. |
| `SCHEDULER.MAX_WORKER` | Number of packages analyzed in parallel (uses `ProcessPoolExecutor`). |
| `CODEQL.USE_MODEL_PACK` | Pulls the published CodeQL model pack for additional library models, which improves recall on third-party sinks. |
| `CLASS_POLLUTION_ANALYSIS.QUERIES` | Path(s) to the `.qls` query suites Pyrl executes. The main suite is `class-pollution.qls`. |
| `DELETE_IF_NO_FLOWS` | When `True`, removes the CodeQL database after analysis if no taint flows were found. Saves disk on negative scans. |

### Single-package scan

```bash
cat > scan-glom.yaml <<'EOF'
WORKFLOW:
  CLASS_POLLUTION_ANALYSIS: True

SCHEDULER:
  TEST_NAME: scan-glom
  WORKSPACE: tasks/scan-glom
  MODE: seed
  REPO: "https://pypi.org/project/glom"
  MAX_WORKER: 1
  TIMEOUT_PER_WORKER: 600

CODEQL:
  CLI: ""
  THREADS: 2
  RAM: 4096
  TIMEOUT: 600
  USE_MODEL_PACK: True
  MODEL_PACK: jackfromeast/class-pollution-model-pack@0.0.1

CLASS_POLLUTION_ANALYSIS:
  QUERIES: ["src/pyrl/codeql/class-pollution-all/class-pollution.qls"]
  DELETE_AFTER_QUERY: False
  DELETE_IF_NO_FLOWS: False
EOF

pyrl --config scan-glom.yaml
```

Pyrl downloads the package source from PyPI, builds a CodeQL database under `tasks/scan-glom/output/glom/`, runs the query suite, writes SARIF results to that output directory, and logs a summary to `tasks/scan-glom/logs/`.

### Batch scan

`MODE: list` reads one URL per line:

```text
# targets.txt
https://pypi.org/project/glom
https://pypi.org/project/pydash
https://github.com/Avaiga/taipy
```

```bash
pyrl --config batch-config.yaml
```

Pyrl spawns up to `MAX_WORKER` parallel processes, each downloading, building, and querying one package. Results land in `WORKSPACE/output/<package-name>/`.

### Interpreting results

Results are written as SARIF (Static Analysis Results Interchange Format). Each finding includes:

- The **source** location (where attacker input enters).
- The **sink** location (the `setattr` or `__setitem__` call).
- The **taint flow**: a sequence of labeled steps from source to sink.
- The **variant** classification, e.g. `Constrained-Get × Attr-Set`.

Pyrl also writes a one-line summary to `WORKSPACE/logs/result.log`:

```
[VULN] glom | Agnostic-Get × Dual-Set | source=glom/core.py:412 | sink=glom/core.py:485 | input=Package
```

#### Taint labels

| Label | Meaning |
|---|---|
| `T_INPUT` | Direct attacker-controlled value at the entry point. |
| `T_ENUM` | Value derived by iterating or splitting `T_INPUT`. |
| `T_KEY` | A key derived from enumeration (a potential attribute or item name). |
| `T_OBJ` | An object resolved through a tainted key. |
| `G_ATTR` | Resolution was via attribute access (`getattr`). |
| `G_ITEM` | Resolution was via item access (`obj[key]`). |

The "get" primitive is classified by which resolution labels appear: both `G_ATTR` and `G_ITEM` indicates *Agnostic-Get*, only `G_ATTR` indicates *Constrained-Get*.

### Dependency analysis workflow

The `dependency_analysis` workflow runs a separate query set that produces library models (sources, sinks, and taint propagation summaries) for third-party packages. These models feed back into the main `class_pollution` queries through `USE_MODEL_PACK`.

```bash
pyrl --config dep-config.yaml --workflow dependency_analysis
```
