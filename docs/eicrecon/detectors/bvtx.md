---
title: Vertex Barrel (BVTX)
parent: EICrecon
nav_order: 13
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Silicon Vertex Barrel (BVTX) Reconstruction

*Also known as: vertex barrel, SVT vertex layers, inner barrel, IB, MAPS vertex detector, ITS3-style vertex layers, VertexBarrel (geometry), VertexBarrelHits (readout), SiBarrelVertex… (collection prefix), BVTX (flag prefix), system IDs 31–33 (`VertexBarrel_0..2_ID`), subassemblies 25–27, supports 50–53 (`SVT_IB_Support_0..3_ID`).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The vertex barrel plugin is the **structural twin of
[BTRK]({{ site.baseurl }}{% link docs/eicrecon/detectors/btrk.md %})**: same
four factories, same algorithms, same constants, different collection names.
51 lines, registered in
[`src/detectors/BVTX/BVTX.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/BVTX/BVTX.cc).
The runtime flag prefix is `BVTX:` (9 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

The one naming trap worth memorising: the **readout** is `VertexBarrelHits`
but every reconstructed collection is prefixed `SiBarrelVertex…`, so the
detector's own name and its output names do not share a stem.

## Chain overview

`VertexBarrelHits` (edm4hep::SimTrackerHit) + `EventHeader`
→ **SiliconTrackerDigi** → `SiBarrelVertexRawHits` (+ `SiBarrelVertexRawHitLinks`, `SiBarrelVertexRawHitAssociations`)

*in parallel, from `EventHeader` alone:*
→ **RandomNoisePixel** → `SiBarrelVertexNoiseRawHits`

(`SiBarrelVertexRawHits`, `SiBarrelVertexNoiseRawHits`)
→ **CollectionCollector**`<edm4eic::RawTrackerHit>` → `SiBarrelVertexRawHitsWithNoise`
→ **TrackerHitReconstruction** → **`SiBarrelVertexRecHits`**

## Parameters

Everything is registered in
[`BVTX.cc#L28-L49`](https://github.com/eic/EICrecon/blob/main/src/detectors/BVTX/BVTX.cc#L28-L49).

| stage | algorithm | parameter | struct default | BVTX value |
|---|---|---|---|---|
| digitization | [`SiliconTrackerDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconTrackerDigi.cc) | `threshold` | `0 keV` | `0.54 keV` |
| | | `timeResolution` | `8` (*"of what units???"*) | default |
| noise | [`RandomNoisePixel`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/RandomNoisePixel.cc) | `addNoise` | `false` | `true` |
| | | `noise_rate_per_pixel_per_event` | `2.0e-7` | `2.0e-7` |
| | | `readout_name` | `"VertexBarrelHits"` | `"VertexBarrelHits"` (the struct default already matches) |
| merge | `CollectionCollector<edm4eic::RawTrackerHit>` | — | no config | — |
| hit reco | [`TrackerHitReconstruction`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerHitReconstruction.cc) | `timeResolution` | `10` (ns) | default |

Both algorithms are described in full on the
[Tracking page]({{ site.baseurl }}{% link docs/eicrecon/tracking.md %}) and on
the [BTRK page]({{ site.baseurl }}{% link docs/eicrecon/detectors/btrk.md %}).
As with BTRK, **the noise parameters are not exposed as runtime flags** — the
nine `BVTX:` flags cover only the digi and rec-hit factories.

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc#L76-L102`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L76-L102)):
`VertexBarrelHits`, `SiBarrelVertexRawHits`, `SiBarrelVertexNoiseRawHits`,
`SiBarrelVertexRawHitsWithNoise`, `SiBarrelVertexRecHits`,
`SiBarrelVertexRawHitLinks`, `SiBarrelVertexRawHitAssociations`.

Downstream: `SiBarrelVertexRecHits` joins **`CentralTrackingRecHits`**
([`tracking.cc#L71-L77`](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L71-L77)).
Vertexing itself is a *global* stage that runs on fitted tracks, not on these
hits — see
[Tracking → Stage 9]({{ site.baseurl }}{% link docs/eicrecon/tracking.md %}).

## Caveats / needs human verification

1. The plugin treats the vertex layers **identically** to the sagitta layers
   (same threshold, same noise rate, same time resolution) even though the
   sensors and pitches differ in the geometry. Whether that is intentional or
   simply not yet tuned is not stated anywhere in EICrecon.
2. `SiBarrelVertexHits` appears in the CI `JANADOT:GROUP:SiBarrelVertex`
   grouping as the sim-hit collection name, while the plugin actually reads
   `VertexBarrelHits`. The janadot group definition looks stale; the plugin is
   authoritative.
3. All resolution comes from the DD4hep segmentation in the **`epic`**
   description — EICrecon adds no charge-weighted centroiding.
4. As on BTRK, noise hits carry no MC links.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
