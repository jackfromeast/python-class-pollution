---
title: "History"
weight: 9
---

# Timeline

A brief history of prototype/class pollution in Python, from earliest public reports to
the present research.

## 2018 &mdash; JS prototype pollution named

TODO: Olivier Arteau's thesis and Node.js advisory ecosystem.

## 2021 &mdash; Silvanovich systematizes JS prototype pollution

TODO: Natalie Silvanovich (Project Zero) publishes a comprehensive survey; community
interest grows in applying the pattern to other languages.

## 2022 &mdash; abdulrah33m demonstrates `pydash.set_`

TODO: first public write-up showing that Python's `getattr`/`setattr` loops enable the
same primitive. Disclosed via a blog post; `pydash` patched by rejecting dunder keys.

## 2024 &mdash; chilaxan reports `deepdiff` (CVE-2024-5254)

TODO: first formal CVE for a Python class pollution sink. deepdiff's merge function
accepted attacker-controlled paths into a NamedTuple, enabling attribute writes.

## 2024 &mdash; Pyrl submitted to IEEE S&P

TODO: paper submitted; large-scale analysis begins.

## 2025 &mdash; IEEE S&P publication and CVE wave

TODO: paper accepted; 7 CVEs assigned (Azure CLI, django-unicorn, Taipy, Mesop, ComfyUI,
docarray, sverchok). 47 confirmed zero-days across 671K+ Python programs.
