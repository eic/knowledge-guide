---
title: EICrecon
nav_order: 2
has_children: true
---

# EICrecon — ePIC reconstruction

One page per detector plugin (the full digitization → clustering chain with
its parameter tables) plus shared algorithm reference pages. All 22 plugins
under [`src/detectors/`](https://github.com/eic/EICrecon/tree/main/src/detectors)
are covered.

**Start here if you are not sure what a detector is called.**
[Detector naming & aliases]({{ site.baseurl }}{% link docs/eicrecon/naming.md %})
maps every subsystem's colloquial name (nHCal, LFHCAL, pfRICH, hpDIRC, Roman
pots, OMD, CyMBaL, …) to its geometry/collection prefix, its EICrecon plugin
and flag prefix, and its DD4hep system ID — and explains the EndcapP (+z,
hadron-going) / EndcapN (−z, electron-going) convention that runs through all
of them.

Authoritative runtime-flag defaults come from the CI dump:
[e_craterlake_flags.json](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(2,700+ flags, regenerated on every EICrecon CI run).
