---
title: Home
layout: home
nav_order: 1
---

# EIC Knowledge Guide

Explanatory documentation for the ePIC software stack — how reconstruction
works detector by detector, which algorithms run, what every configuration
flag does, and where the numbers come from.

{: .warning }
These pages are AI-generated drafts derived directly from the source code
([eic/EICrecon](https://github.com/eic/EICrecon), [eic/epic](https://github.com/eic/epic))
and the CI flags dump. Every claim links to its source — verify there before
depending on it. Corrections welcome via issues/PRs.

## Sections

- **[EICrecon]({% link docs/eicrecon/index.md %})** — reconstruction chains, algorithms, parameters per detector
- **[ePIC geometry]({% link docs/epic/index.md %})** — the DD4hep detector description: compact XML, detector plugins, configurations, readouts and cellIDs
