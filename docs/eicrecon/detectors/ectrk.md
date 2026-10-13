---
title: Endcap Si Tracker (ECTRK)
parent: EICrecon
nav_order: 14
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Endcap Silicon Tracker (ECTRK) Reconstruction

*Also known as: silicon tracker endcaps, endcap silicon discs, forward + backward tracking discs, EndcapP and EndcapN silicon trackers, SVT endcaps, TrackerEndcapN / TrackerEndcapP (geometry), TrackerEndcapHits (readout), SiEndcapTracker… (collection prefix), ECTRK (flag prefix), system IDs 68–76 (`TrackerEndcapN_0..8_ID`) and 77–83 (`TrackerEndcapP_0..6_ID`).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The endcap silicon tracker plugin is the third member of the
BTRK/BVTX/ECTRK triplet: identical structure, identical constants, 50 lines,
registered in
[`src/detectors/ECTRK/ECTRK.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTRK/ECTRK.cc).
The runtime flag prefix is `ECTRK:` (9 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

{: .note }
**One plugin, one collection, both endcaps.** Unlike the calorimeters — where
`EcalEndcapP` and `EcalEndcapN` are separate plugins with separate collections
— the silicon tracker endcaps share the single readout `TrackerEndcapHits` and
produce the single collection `SiEndcapTrackerRecHits`. There is no
`SiEndcapTrackerPRecHits`/`…NRecHits` split anywhere in EICrecon; if you need
the two sides apart you must decode the cellID or cut on z. See
[Detector naming & aliases]({{ site.baseurl }}{% link docs/eicrecon/naming.md %})
for the EndcapP/EndcapN convention.

## Chain overview

`TrackerEndcapHits` (edm4hep::SimTrackerHit) + `EventHeader`
→ **SiliconTrackerDigi** → `SiEndcapTrackerRawHits` (+ `SiEndcapTrackerRawHitLinks`, `SiEndcapTrackerRawHitAssociations`)

*in parallel, from `EventHeader` alone:*
→ **RandomNoisePixel** → `SiEndcapTrackerNoiseRawHits`

(`SiEndcapTrackerRawHits`, `SiEndcapTrackerNoiseRawHits`)
→ **CollectionCollector**`<edm4eic::RawTrackerHit>` → `SiEndcapTrackerRawHitsWithNoise`
→ **TrackerHitReconstruction** → **`SiEndcapTrackerRecHits`**

## Parameters

Registered in
[`ECTRK.cc#L27-L48`](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTRK/ECTRK.cc#L27-L48).

| stage | algorithm | parameter | struct default | ECTRK value |
|---|---|---|---|---|
| digitization | [`SiliconTrackerDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconTrackerDigi.cc) | `threshold` | `0 keV` | `0.54 keV` |
| | | `timeResolution` | `8` | default |
| noise | [`RandomNoisePixel`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/RandomNoisePixel.cc) | `addNoise` | `false` | `true` |
| | | `noise_rate_per_pixel_per_event` | `2.0e-7` | `2.0e-7` |
| | | `readout_name` | `"VertexBarrelHits"` | `"TrackerEndcapHits"` |
| merge | `CollectionCollector<edm4eic::RawTrackerHit>` | — | no config | — |
| hit reco | [`TrackerHitReconstruction`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerHitReconstruction.cc) | `timeResolution` | `10` (ns) | default |

Both algorithms are documented in full on the
[Tracking page]({{ site.baseurl }}{% link docs/eicrecon/tracking.md %}); the
noise stage is described on the
[BTRK page]({{ site.baseurl }}{% link docs/eicrecon/detectors/btrk.md %}).
The noise parameters are **not** runtime flags.

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc#L76-L102`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L76-L102)):
`SiEndcapTrackerRecHits`, `SiEndcapTrackerRawHits`,
`SiEndcapTrackerNoiseRawHits`, `SiEndcapTrackerRawHitsWithNoise`,
`SiEndcapTrackerRawHitLinks`, `SiEndcapTrackerRawHitAssociations`.

{: .note }
`TrackerEndcapHits` — the **sim**-hit collection — is *not* in the persisted
list, unlike `SiBarrelHits` and `VertexBarrelHits` which are. Whether that
asymmetry is deliberate is not documented.

Downstream: `SiEndcapTrackerRecHits` joins **`CentralTrackingRecHits`**
([`tracking.cc#L71-L77`](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L71-L77)).

## Caveats / needs human verification

1. Both endcaps share one collection, so any per-side study has to re-derive
   the side from geometry. The DD4hep system IDs *do* separate them
   (68–76 vs 77–83), so the information is recoverable from the cellID.
2. `threshold = 0.54 keV` is copied from the barrel plugins with no
   endcap-specific justification.
3. The sim-hit collection is missing from the default output list (see note
   above) — worth confirming with a maintainer before relying on it.
4. `timeResolution` units remain the unresolved TODO carried by
   `SiliconTrackerDigiConfig`.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
