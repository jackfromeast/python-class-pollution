---
title: "Usage"
weight: 2
---

# Using Pyrl

Pyrl is a task-based scheduler that drives CodeQL analysis for class pollution detection.
You point it at one or more Python packages (via PyPI URL, GitHub URL, or a text file
listing many), and it builds CodeQL databases, runs the operational taint queries, and
writes structured SARIF results.

## Entrypoint

```bash
pyrl --config /path/to/config.yaml
```

Or equivalently:

```bash
python -m pyrl --config /path/to/config.yaml
```

An optional `--workflow` flag overrides the workflow specified in the config:

```bash
pyrl --config config.yaml --workflow class_pollution
pyrl --config config.yaml --workflow dependency_analysis
```

If `--workflow` is not passed, Pyrl reads it from the `WORKFLOW` section of the YAML.

## Configuration file

All behavior is governed by a single YAML file. A full annotated template lives at
`tmp/analyzer/config-example.yaml` in the repository. The minimal structure:

```yaml
WORKFLOW:
  CLASS_POLLUTION_ANALYSIS: True
  DEPENDENCY_ANALYSIS: False

SCHEDULER:
  TEST_NAME: "my-scan"
  WORKSPACE: "tasks/my-scan"      # results land here

  MODE: "seed"                    # "seed" (single repo), "list", or "json"
  REPO: "https://pypi.org/project/glom"   # used when MODE=seed
  REPO_LIST: "targets.txt"       # used when MODE=list or json
  URL_LIST_FROM: 0               # slice the list (0-indexed)
  URL_LIST_TO: -1                # -1 = end
  MAX_WORKER: 8                  # parallel workers
  TIMEOUT_PER_WORKER: 1200       # seconds per package

CODEQL:
  CLI: ""                        # path to `codeql` binary; leave empty to use $PATH
  THREADS: 1
  RAM: 8192                      # MB
  TIMEOUT: 1200
  USE_MODEL_PACK: True
  MODEL_PACK: jackfromeast/class-pollution-model-pack@0.0.1

CLASS_POLLUTION_ANALYSIS:
  QUERIES:
    - "src/pyrl/codeql/class-pollution-all/class-pollution.qls"
  DELETE_AFTER_QUERY: False
  DELETE_IF_NO_FLOWS: True

LOG:
  LOG_PATH: ""                   # default: WORKSPACE/logs
  LOG_TO_CONSOLE: True
  LOG_TO_LOCAL_FILE: True
  LOG_TO_GLOBAL_FILE: True
  LOG_RESULT: True
  LOG_LEVEL: "INFO"
```

### Key settings explained

| Key | Purpose |
|-----|---------|
| `SCHEDULER.MODE` | `"seed"` to analyze a single `REPO`; `"list"` to read a newline-delimited file of URLs; `"json"` for a JSON array. |
| `SCHEDULER.WORKSPACE` | Base directory where CodeQL databases, results, and logs are written. Resolved relative to the project root. |
| `SCHEDULER.MAX_WORKER` | Number of packages analyzed in parallel (uses `ProcessPoolExecutor`). |
| `CODEQL.USE_MODEL_PACK` | Whether to pull the published CodeQL model pack for additional library models (improves recall on third-party sinks). |
| `CLASS_POLLUTION_ANALYSIS.QUERIES` | Path(s) to the `.qls` query suites Pyrl executes. The main suite is `class-pollution.qls`. |
| `DELETE_IF_NO_FLOWS` | If `True`, removes the CodeQL database after analysis when no taint flows were found (saves disk). |

## Workflow: analyzing a single package

```bash
# 1. Create a minimal config
cat > scan-glom.yaml << 'EOF'
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

LOG:
  LOG_PATH: ""
  LOG_TO_CONSOLE: True
  LOG_TO_LOCAL_FILE: True
  LOG_TO_GLOBAL_FILE: True
  LOG_RESULT: True
  LOG_LEVEL: INFO
EOF

# 2. Run
pyrl --config scan-glom.yaml
```

Pyrl will:
1. Download the package source from PyPI.
2. Build a CodeQL database under `tasks/scan-glom/output/glom/`.
3. Run the `class-pollution.qls` query suite.
4. Write SARIF results to the output directory.
5. Log a summary to `tasks/scan-glom/logs/` and to stdout.

## Workflow: batch analysis

```bash
# targets.txt — one URL per line
# https://pypi.org/project/glom
# https://pypi.org/project/pydash
# https://github.com/Avaiga/taipy

pyrl --config batch-config.yaml
```

With `MODE: list` and `REPO_LIST: targets.txt`, Pyrl spawns up to `MAX_WORKER` parallel
processes, each downloading, building, and querying one package. Results land in
`WORKSPACE/output/<package-name>/`.

## Interpreting results

Results are written as SARIF (Static Analysis Results Interchange Format) JSON. Each
finding includes:

- The **source** location (where attacker input enters).
- The **sink** location (the `setattr` / `__setitem__` call).
- The **taint flow** &mdash; a sequence of labeled steps from source to sink.
- The **vulnerability type** classification (e.g. `Constrained-Get × Attr-Set`).

Pyrl also writes a one-line summary to the result log at `WORKSPACE/logs/result.log`:

```
[VULN] glom | Agnostic-Get × Dual-Set | source=glom/core.py:412 | sink=glom/core.py:485 | input=Package
```

### Taint labels

| Label | Meaning |
|-------|---------|
| `T_INPUT` | Direct attacker-controlled value at the entry point |
| `T_ENUM` | Value derived by iterating/splitting `T_INPUT` |
| `T_KEY` | A key derived from enumeration (potential attribute/item name) |
| `T_OBJ` | Object resolved through a tainted key |
| `G_ATTR` | Resolution was via attribute access (`getattr`) |
| `G_ITEM` | Resolution was via item access (`obj[key]`) |

The "get" primitive is classified by which resolution labels appear: if both `G_ATTR` and
`G_ITEM` appear, it is *Agnostic-Get*; if only `G_ATTR`, it is *Constrained-Get*.

## Dependency analysis workflow

The `dependency_analysis` workflow runs a separate set of queries that identify library
models &mdash; sources, sinks, and taint propagation summaries for third-party packages.
These models feed back into the main `class_pollution` queries via the
`USE_MODEL_PACK` mechanism.

```bash
pyrl --config dep-config.yaml --workflow dependency_analysis
```

## Troubleshooting

### "No repositories to process"
Check `SCHEDULER.MODE` and the corresponding `REPO` or `REPO_LIST` path.

### CodeQL timeout
Increase `CODEQL.TIMEOUT` and `SCHEDULER.TIMEOUT_PER_WORKER`. Large packages (>100K LOC)
may need 30+ minutes.

### Model pack resolution failure
Ensure `codeql pack download jackfromeast/class-pollution-model-pack@0.0.1` works in your
environment (requires GitHub package registry access).
