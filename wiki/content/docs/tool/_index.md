---
title: "Tool"
weight: 5
bookFlatSection: true
---

# Detection and Exploitation Tools

This project provides two tools for working with Python class pollution vulnerabilities:

## Pyrl — Detection

**Pyrl** is the first automated tool for detecting class pollution vulnerabilities in real-world Python applications. It uses a novel static analysis technique called *operational taint analysis* to precisely model the "get" and "set" primitives unique to class pollution.

[Learn more about Pyrl →]({{< relref "pyrl" >}})

## Polluter — Exploitation & Testing

**Polluter** is a Python library for testing and exploiting class pollution gadget chains. It helps security researchers and developers verify whether a class pollution vulnerability is exploitable in a specific application context.

[Learn more about Polluter →]({{< relref "polluter" >}})
