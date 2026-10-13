---
title: B0 Tracker (B0TRK)
parent: EICrecon
nav_order: 21
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC B0 Tracker (B0TRK) Reconstruction

*Also known as: B0 tracker, B0 silicon tracker, B0pf tracker, far-forward B0 silicon, B0 stations, B0Tracker (geometry), B0TrackerHits (readout), B0Tracker… (collection prefix), B0TRK (flag prefix), system IDs 150–153 (`B0Tracker_Station_1..4_ID`), companion 157 (`B0TrackerCompanion_ID`), subassembly 158 (`B0TrackerSubAssembly_ID`).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The B0 tracker sits inside the B0pf dipole in the far-forward region, next to
the [B0 ECal]({{ site.baseurl }}{% link docs/eicrecon/detectors/b0ecal.md %}).
Its plugin is 40 lines and registers **two factories** — digitization and hit
reconstruction — with no noise stage
([`src/detectors/B0TRK/B0TRK.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/B0TRK/B0TRK.cc)).
The runtime flag prefix is `B0TRK:` (9 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

What makes B0 unusual is what happens **after** the plugin: unlike the other
far-forward detectors, B0 hits are fed to a full ACTS combinatorial Kalman
filter — a complete second tracking chain running in parallel with the central
one — rather than to a transfer-matrix reconstruction. See
[Tracking]({{ site.baseurl }}{% link docs/eicrecon/tracking.md %}).

## Chain overview

`B0TrackerHits` (edm4hep::SimTrackerHit) + `EventHeader`
→ **SiliconTrackerDigi** → `B0TrackerRawHits` (+ `B0TrackerRawHitLinks`, `B0TrackerRawHitAssociations`)
→ **TrackerHitReconstruction** → **`B0TrackerRecHits`**

*then, in [`src/global/tracking/tracking.cc`](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc):*

`B0TrackerRecHits` → **TrackerMeasurementFromHits** → `B0TrackerMeasurements`
→ **CKFTracking** → **AmbiguitySolver** → **ActsToTracks** → `B0TrackerCKFTracks` (+ trajectories, parameters, links, associations, and truth-seeded / unfiltered twins)

## Parameters

| stage | algorithm | parameter | struct default | B0TRK value |
|---|---|---|---|---|
| digitization | [`SiliconTrackerDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconTrackerDigi.cc) | `threshold` | `0 keV` | `10.0 keV` |
| | | `timeResolution` | `8` | `8` (explicit; equals the default) |
| hit reco | [`TrackerHitReconstruction`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerHitReconstruction.cc) | `timeResolution` | `10` | `8` |

([`B0TRK.cc#L23-L38`](https://github.com/eic/EICrecon/blob/main/src/detectors/B0TRK/B0TRK.cc#L23-L38))

The `10 keV` threshold is ~20× the central silicon trackers' `0.54 keV`, and
is shared with the two other far-forward silicon detectors
([RPOTS]({{ site.baseurl }}{% link docs/eicrecon/detectors/rpots.md %}),
[FOFFMTRK]({{ site.baseurl }}{% link docs/eicrecon/detectors/foffmtrk.md %})),
which suggests one far-forward assumption rather than a per-detector study.
`timeResolution` still carries the config header's unresolved
*"TODO 8 of what units??? Same TODO in juggler. Probably [ns]"*.

Both algorithms are described in full on the
[Tracking page]({{ site.baseurl }}{% link docs/eicrecon/tracking.md %}).

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc#L202-L212`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L202-L212)):
`B0TrackerHits`, `B0TrackerRawHits`, `B0TrackerRecHits`,
`B0TrackerRawHitLinks`, `B0TrackerRawHitAssociations`, plus the tracking
products `B0TrackerTruthSeeds`, `B0TrackerSeeds`, `B0TrackerSeedParameters`,
`B0TrackerMeasurements`; and the CKF outputs at
[L282-L303](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L282-L303).

Downstream:

- `B0TrackerRecHits` → `B0TrackerMeasurements` → the B0 CKF chain.
- `B0TrackerCKFTracks` is merged with `CentralCKFTracks` into `CombinedTracks`,
  and the ACTS containers of both go into the combined vertex finder
  (`CentralAndB0TrackVertices`) — see
  [Tracking]({{ site.baseurl }}{% link docs/eicrecon/tracking.md %}).
- Truth seeding routes MC particles below 50 mrad to `B0TrackerTruthSeeds` and
  the rest to `CentralTrackerTruthSeeds`.

`B0TrackerRecHits` is **not** part of `CentralTrackingRecHits`.

## Caveats / needs human verification

1. `threshold = 10 keV` has no provenance comment and is shared verbatim with
   the Roman pots and the off-momentum tracker.
2. B0 is the one detector for which `TrackerMeasurementFromHits` relaxes its
   on-surface projection tolerance from 0.1 µm to 1 µm — an explicitly
   flagged hack in the source. See
   [Tracking → Stage 3]({{ site.baseurl }}{% link docs/eicrecon/tracking.md %}).
3. The digi and rec `timeResolution` values agree here (`8`), unlike most
   other trackers — but the units of the digi value remain undefined in the
   source.
4. There is no noise stage, so B0 tracking sees a cleaner detector than the
   central silicon layers by construction.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
