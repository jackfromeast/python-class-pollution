---
title: "Taxonomy"
weight: 2
bookCollapseSection: true
---

# Vulnerability Taxonomy

We establish the first systematic taxonomy of Python class pollution along three aspects:

1. **Pollution Primitives** — How to resolve and modify objects (the "get" and "set" operations)
2. **Vulnerability Types** — Six distinct types from combining two "get" and three "set" primitives
3. **Consequences** — What security impacts follow from successful pollution

The taxonomy reveals that prior work only documented one of the six vulnerability types (`Agnostic-Get × Dual-Set`). The remaining five types are newly defined in this work.

```
┌─────────────────────────────────────────────────┐
│              Class Pollution Taxonomy            │
├─────────────────────────────────────────────────┤
│                                                 │
│  Get Primitives    ×    Set Primitives          │
│  ─────────────          ──────────────          │
│  • Agnostic-Get         • Dual-Set             │
│  • Constrained-Get      • Attr-Set             │
│                          • Item-Set             │
│                                                 │
│  → 6 Vulnerability Types                       │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Overview

| Type | Get Primitive | Set Primitive | Previously Known? |
|------|--------------|---------------|-------------------|
| Agnostic-Get × Dual-Set | Agnostic | Dual | Yes |
| Constrained-Get × Dual-Set | Constrained | Dual | **New** |
| Agnostic-Get × Attr-Set | Agnostic | Attr | **New** |
| Constrained-Get × Attr-Set | Constrained | Attr | **New** |
| Agnostic-Get × Item-Set | Agnostic | Item | **New** |
| Constrained-Get × Item-Set | Constrained | Item | **New** |
