---
title: Barrel Si Tracker (BTRK)
parent: EICrecon
nav_order: 12
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Barrel Silicon Tracker (BTRK) Reconstruction

*Also known as: barrel silicon tracker, SVT barrel, sagitta layers, outer barrel MAPS layers, ITS3-style barrel staves, TrackerBarrel (geometry), SiBarrelHits (readout), SiBarrel… (collection prefix), BTRK (flag prefix), system IDs 59–67 (`TrackerBarrel_0..8_ID`).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The barrel silicon tracker plugin is one of the smallest in EICrecon — 53
lines, four factories, no detector-specific algorithm. It digitizes
`SiBarrelHits`, adds random pixel noise, merges the two raw-hit collections
and converts the result into 3D space points. Everything is registered in
[`src/detectors/BTRK/BTRK.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTRK/BTRK.cc).
The runtime flag prefix is `BTRK:` (9 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json) — the
fewest of any detector plugin except `BVTX`, `ECTRK` and `B0TRK`).

All the interesting physics happens downstream, in
[Tracking]({{ site.baseurl }}{% link docs/eicrecon/tracking.md %}); this page
only documents the plugin's own wiring and constants.

## Chain overview

`SiBarrelHits` (edm4hep::SimTrackerHit) + `EventHeader`
→ **SiliconTrackerDigi** → `SiBarrelRawHits` (+ `SiBarrelRawHitLinks`, `SiBarrelRawHitAssociations`)

*in parallel, from `EventHeader` alone:*
→ **RandomNoisePixel** → `SiBarrelNoiseRawHits`

(`SiBarrelRawHits`, `SiBarrelNoiseRawHits`)
→ **CollectionCollector**`<edm4eic::RawTrackerHit>` → `SiBarrelRawHitsWithNoise`
→ **TrackerHitReconstruction** → **`SiBarrelTrackerRecHits`**

Note that hit reconstruction reads the **noise-merged** collection, not
`SiBarrelRawHits`
([BTRK.cc#L48-L51](https://github.com/eic/EICrecon/blob/main/src/detectors/BTRK/BTRK.cc#L48-L51)).

## Stage 1 — Digitization

**Algorithm:** [`SiliconTrackerDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconTrackerDigi.cc)
— applies an energy-deposit threshold and quantises the hit time; described on
the [Tracking page]({{ site.baseurl }}{% link docs/eicrecon/tracking.md %}).

| parameter | struct default | BTRK value | meaning |
|---|---|---|---|
| `threshold` | `0 keV` | `0.54 keV` | minimum deposited energy for a hit to survive ([`BTRK.cc#L31`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTRK/BTRK.cc#L27-L33)) |
| `timeResolution` | `8` | default | *"TODO 8 of what units??? Same TODO in juggler. Probably [ns]"* ([`SiliconTrackerDigiConfig.h#L14`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconTrackerDigiConfig.h#L10-L15)) |

The config header carries a standing warning: *"NB: be aware of thresholds in
npsim!"* — the simulation applies its own cut before EICrecon ever sees a hit.

## Stage 2 — Random pixel noise

**Algorithm:** [`RandomNoisePixel`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/RandomNoisePixel.cc)
— fires pixels at random from the DD4hep segmentation, with no input hits at
all (its only input is `EventHeader`, used for the random seed).

| parameter | struct default | BTRK value | meaning |
|---|---|---|---|
| `addNoise` | `false` | `true` | *"Keep geometry initialization and event generation off unless explicitly enabled."* |
| `noise_rate_per_pixel_per_event` | `2.0e-7` | `2.0e-7` | *"Probability that one pixel fires from noise in one event. The same value is applied to every SVT layer; the pixel pitch comes from DD4hep segmentation."* |
| `readout_name` | `"VertexBarrelHits"` | `"SiBarrelHits"` | *"DD4hep readout whose sensitive components and segmentation should be used."* |

([`RandomNoisePixelConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/RandomNoisePixelConfig.h),
[`BTRK.cc#L35-L38`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTRK/BTRK.cc#L35-L38))

{: .note }
**None of these three parameters is exposed as a runtime flag.** The nine
`BTRK:` flags in the CI dump all belong to the digi and rec-hit factories;
neither `SiBarrelNoiseRawHits` nor `SiBarrelRawHitsWithNoise` appears there at
all. Changing the noise rate requires a recompile.

## Stage 3 — Merging signal and noise

**Algorithm:** `CollectionCollector_factory<edm4eic::RawTrackerHit>` — a
generic concatenation with no configuration
([`BTRK.cc#L40-L45`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTRK/BTRK.cc#L40-L45)).
The noise hits carry no MC links, so `SiBarrelRawHitLinks` /
`SiBarrelRawHitAssociations` cover only the subset of
`SiBarrelRawHitsWithNoise` that came from `SiBarrelRawHits`.

## Stage 4 — Hit reconstruction

**Algorithm:** [`TrackerHitReconstruction`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerHitReconstruction.cc)
— cell ID → cell centre, with a purely geometric `(cell_size/√12)²` covariance.
Fully described on the
[Tracking page]({{ site.baseurl }}{% link docs/eicrecon/tracking.md %}).
BTRK passes an **empty config**, so `timeResolution` stays at its default
`10` ns
([`BTRK.cc#L48-L51`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTRK/BTRK.cc#L48-L51)).

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc#L76-L102`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L76-L102)):
`SiBarrelHits` (the sim hits), `SiBarrelRawHits`, `SiBarrelNoiseRawHits`,
`SiBarrelRawHitsWithNoise`, `SiBarrelTrackerRecHits`, `SiBarrelRawHitLinks`,
`SiBarrelRawHitAssociations`. Every collection this plugin produces is kept.

Downstream: `SiBarrelTrackerRecHits` is one of the seven collections merged
into **`CentralTrackingRecHits`**
([`tracking.cc#L71-L77`](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L71-L77)),
which feeds both seeding and measurement building. See
[Tracking]({{ site.baseurl }}{% link docs/eicrecon/tracking.md %}).

## Caveats / needs human verification

1. `threshold = 0.54 keV` has no provenance comment. It is identical in
   `BTRK`, `BVTX` and `ECTRK`, which suggests one shared assumption rather
   than three measurements.
2. `timeResolution` units are unresolved **in the source itself** — the config
   header says *"TODO 8 of what units???"*. The rec-hit stage then writes
   `10` ns into `TrackerHit::timeError`, so the digi and rec numbers are not
   even the same quantity.
3. The noise model applies one rate to every layer regardless of pitch or
   sensor generation, by the config's own admission.
4. Noise hits enter track finding but have no MC association, so any
   efficiency/purity study that joins on `SiBarrelRawHitAssociations` will
   silently see fewer hits than the collection used for tracking.
5. Cell segmentation — and hence the entire position resolution — comes from
   the **`epic` geometry description**, not from EICrecon.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
