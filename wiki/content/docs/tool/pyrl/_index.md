---
title: "Pyrl"
weight: 1
bookFlatSection: true
---

# Pyrl

Pyrl (pronounced "Pearl") is the **first automated detection tool** for Python class pollution vulnerabilities. It uses a novel static analysis technique called *operational taint analysis* implemented on top of CodeQL.

## What Pyrl Does

Pyrl tracks attacker-controlled inputs through "get" and "set" primitives using fine-grained semantic taint labels that capture:
- **T_INPUT** — Direct attacker input
- **T_ENUM** — Enumerable value from split operations
- **T_KEY** — Potential key value from enumeration
- **T_OBJ** — Object resolved through a tainted key
- **G_ATTR** / **G_ITEM** — Access type annotations (attribute vs. item)

## Key Features

- Detects all **6 vulnerability types** in the taxonomy
- Handles both first-order and second-order get operations
- Performs **exploitability checking** (verifies both assignments in Dual-Set are in mutually exclusive branches)
- Uses **barrier node analysis** to reduce false positives (key sanitization, type checks)
- Scales to large codebases (linear with AST nodes)

## Performance

- **868** total alerts across 671K+ Python projects
- **47** confirmed true positive zero-day vulnerabilities
- **38%** false positive rate (significantly lower than 78-97% for baseline approaches)
- Analysis time: typically under 2 minutes per package

## Architecture

```
┌──────────────────────────────────────────────────┐
│                    Pyrl Pipeline                  │
├──────────────────────────────────────────────────┤
│                                                  │
│  1. Package Download & Database Setup            │
│     └─ CodeQL database creation                  │
│                                                  │
│  2. Operational Taint Analysis                   │
│     ├─ Taint Initialization (INPUT rule)         │
│     ├─ Taint Propagation (SPLIT, ENUMERATE,      │
│     │   GETITEM, GETATTR, BRANCH rules)          │
│     └─ Taint Merging (at control-flow joins)     │
│                                                  │
│  3. Vulnerability Detection                      │
│     ├─ Sink identification (assignment tuples)   │
│     ├─ Label condition checking (Table 5)        │
│     └─ Type classification (6 types)            │
│                                                  │
│  4. Exploitability Checking                      │
│     ├─ Mutual exclusion verification             │
│     └─ Barrier node / dominator analysis         │
│                                                  │
│  5. Result Processing                            │
│     └─ Report generation with taint flow paths   │
│                                                  │
└──────────────────────────────────────────────────┘
```

## Implementation

- Written in **CodeQL** (QL language) — 3,509 lines of new code
- Runs on CodeQL v2.21.3 with Python language support v4.0.5
- Extended CodeQL standard library for:
  - Collection data structures (`namedtuple`, `reduce`, etc.)
  - Object attribute definition resolution
  - Data flow through higher-order functions
