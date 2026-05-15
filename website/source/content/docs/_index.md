---
title: "Overview"
weight: 1
bookToc: true
bookFlatSection: false
---

# Python Class Pollution

**Class pollution** is a vulnerability class where an attacker traverses Python's runtime object graph through dunder attributes such as `__class__`, `__init__`, `__globals__`, and `sys.modules`, and overwrites attributes in unintended classes, functions, or modules. The traversal is driven by a reflective attribute or item access loop whose path or keys come from untrusted input.

It is the Python analogue of [JavaScript prototype pollution][jsproto], but the primitives are richer: Python's class-based object model with a flexible reflection layer lets pollution reach classes, functions, modules, and descriptor slots.

## Roadmap

This wiki is organized into the following sections. Most readers can pick the entry point that matches their goal:

<!-- - **[Taxonomy]({{< relref "taxonomy" >}})**: the systematic taxonomy of class pollution along three aspects: pollution primitives, vulnerability types, and consequences.
- **[Pollution Targets]({{< relref "targets" >}})**: runtime objects (classes, modules, functions, globals) that are reachable via reflection and meaningfully change program behavior when modified.
- **[Gadgets]({{< relref "gadgets" >}})**: concrete target + value combinations that turn a pollution primitive into RCE, XSS, authentication bypass, DoS, or token leakage.
- **[Tool]({{< relref "tool" >}})**: documentation for *Pyrl* (the detection tool, built on operational taint analysis over CodeQL) and *Polluter* (an exploitation/testing helper).
- **[Collection]({{< relref "collection" >}})**: a curated database of confirmed vulnerable Python packages with end-to-end PoCs, including the assigned CVEs and showcase walkthroughs.
- **[Defense]({{< relref "defense" >}})**: mitigations along the object resolution path: key sanitization at the "get" primitive and guards at the "set" primitive. -->

## About this wiki

This wiki accompanies our IEEE S&P 2026 paper [*The First Large-Scale Systematic Study of Python Class Pollution Vulnerability*][paper]. Its goal is to be a living reference for the vulnerability class. Concretely, we want it to:

- Document the taxonomy, targets, and gadgets in a way that is easier to extend than a PDF.
- Track new CVEs, gadgets, and showcases as they are discovered.
- Provide actionable defense guidance for library and application maintainers.

## Contributions

Contributions are welcome: new gadgets, additional showcases, corrections, and translations. The site is built with Hugo from markdown sources under [`website/source/`](https://github.com/jackfromeast/python-class-pollution/tree/main/website/source). To propose a change, open an [issue](https://github.com/jackfromeast/python-class-pollution/issues) or a [pull request](https://github.com/jackfromeast/python-class-pollution/pulls) on the repo: https://github.com/jackfromeast/python-class-pollution.

## References

1. Abdulraheem Khaled, *"Prototype Pollution in Python."* 2023. [Link](https://blog.abdulrah33m.com/prototype-pollution-in-python/). Also presented at Black Hat MEA 2023, [Link](https://blackhatmea.com/session/prototype-pollution-bug-python).
2. Ziyi Ouyang, *"Research and Explore of Prototype Pollution Attack in Python."* ACCTCS 2023. [Link](https://ieeexplore.ieee.org/abstract/document/10145365).
3. Qingyun Zhang, *"Exploitation and prevention of Python prototype chain pollution."* Applied and Computational Engineering,43,229-236. [Link](https://doi.org/10.54254/2755-2721/43/20230839).
4. Zhengyu Liu, Jiacheng Zhong, Jianjia Yu, Muxi Lyu, Zifeng Kang, Yinzhi Cao, *"The First Large-Scale Systematic Study of Python Class Pollution Vulnerability."* IEEE S&P 2026. [Link](https://jackfromeast.github.io/assets/Pyrl.pdf).

[jsproto]: https://portswigger.net/web-security/prototype-pollution
[pydash]: https://github.com/dgilland/pydash
[paper]: https://jackfromeast.github.io/assets/Pyrl.pdf
