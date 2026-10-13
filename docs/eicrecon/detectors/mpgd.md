---
title: MPGD Trackers (MPGD)
parent: EICrecon
nav_order: 15
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC MPGD Trackers (MPGD) Reconstruction

*Also known as: MPGDs, micro-pattern gaseous detectors, µRWELL trackers, CyMBaL (cylindrical micromegas barrel layer, = InnerMPGDBarrel = MPGDBarrel), outer MPGD barrel (MPGDOuterBarrel = OuterMPGDBarrel), forward MPGD endcap, backward MPGD endcap, GEM/micromegas discs; MPGDBarrel / OuterMPGDBarrel / ForwardMPGDEndcap / BackwardMPGDEndcap (collection prefixes and readouts), MPGD (flag prefix), IDs drawn from the 40–85 tracker block.*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

One plugin, **four detectors**, and a runtime switch that changes which
digitization algorithm runs for the two barrel layers. Everything is
registered in
[`src/detectors/MPGD/MPGD.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc)
(254 lines — by far the largest of the tracker plugins, almost entirely
because of the switch logic). The runtime flag prefix is `MPGD:` (37 flags in
the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

The file opens with the summary comment:

> 2D-STRIP DIGITIZATION — Is produced by "MPGDTrackerDigi". Relies on 2DStrip
> version of "compact" geometry file.
> PIXEL DIGITIZATION — Is produced by "SiliconTrackerDigi".

## Chain overview

Four independent, identically-shaped chains:

`MPGDBarrelHits` → **SiliconTrackerDigi** *or* **MPGDTrackerDigi** → `MPGDBarrelRawHits` (+ Links/Associations) → **TrackerHitReconstruction** *or* **MPGDHitReconstruction** → `MPGDBarrelRecHits`
`OuterMPGDBarrelHits` → … → `OuterMPGDBarrelRecHits`
`BackwardMPGDEndcapHits` → **SiliconTrackerDigi** → `BackwardMPGDEndcapRawHits` → **TrackerHitReconstruction** → `BackwardMPGDEndcapRecHits`
`ForwardMPGDEndcapHits` → **SiliconTrackerDigi** → `ForwardMPGDEndcapRawHits` → **TrackerHitReconstruction** → `ForwardMPGDEndcapRecHits`

Only the two **barrel** layers have the pixel/2D-strip alternative; the two
endcaps are always pixel-digitized
([`MPGD.cc#L212-L252`](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L212-L252)).
The output collection names are the **same either way**, so nothing
downstream can tell which path ran.

## Stage 0 — Choosing pixel or 2D-strip readout

`SiFactoryPattern` is a two-bit mask: `0x1` = CyMBaL (`MPGDBarrel`), `0x2` =
outer barrel (`OuterMPGDBarrel`). A set bit means *pixel* digitization
(`SiliconTrackerDigi`); a clear bit means *2D-strip*
(`MPGDTrackerDigi`). Resolution order
([`MPGD.cc#L44-L97`](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L44-L97)):

| priority | source | effect |
|---|---|---|
| 1 (lowest) | hard-coded default | `0x3` — *"Full-scale SiliconTrackerDigi"*, i.e. pixel for both barrels |
| 2 | DD4hep geometry constants `InnerMPGDBarrel_2DStrip` / `MPGDOuterBarrel_2DStrip` | a constant equal to `1` **clears** that detector's bit → 2D-strip. A missing constant is caught and *"apply legacy pixel readout"* |
| 3 (highest) | runtime flag `MPGD:SiFactoryPattern` | hexadecimal string, parsed with `std::stoul(…, 16)`; a malformed value throws a `JException` |

The CI dump shows `MPGD:SiFactoryPattern = ` (empty), meaning the flag is not
set and the geometry constants decide. The plugin logs which path each
detector took at `info` level (*"2DStrip XML loaded for …"* / *"pixel XML
loaded for …"*).

{: .note }
The XML constant names use the **geometry** detector names
(`InnerMPGDBarrel`, `MPGDOuterBarrel`), while the collections use the
**EICrecon** names (`MPGDBarrel`, `OuterMPGDBarrel`). `InnerMPGDBarrel` and
`MPGDBarrel` are the same detector — colloquially, CyMBaL.

## Stage 1a — Pixel digitization (default path)

**Algorithm:** [`SiliconTrackerDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconTrackerDigi.cc)
— see the [Tracking page]({% link docs/eicrecon/tracking.md %}).
All four detectors use the same two values:

| parameter | struct default | MPGD value | meaning |
|---|---|---|---|
| `threshold` | `0 keV` | `100 eV` | minimum deposited energy (≈ 5× lower than the silicon trackers' `0.54 keV`) |
| `timeResolution` | `8` | `10` | *"TODO 8 of what units??? … Probably [ns]"* |

([`MPGD.cc#L101-L109`](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L101-L109),
[`#L159-L168`](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L159-L168),
[`#L214-L222`](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L214-L222),
[`#L235-L243`](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L235-L243))

## Stage 1b — 2D-strip digitization (barrels only)

**Algorithm:** [`MPGDTrackerDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/MPGDTrackerDigi.cc)
— models the gas gain and two crossed strip planes rather than a pixel grid.
The config header explains the philosophy:

> MPGD digitization parameters should come in pairs: one parameter per strip
> coordinate. … Here we simplify. With some justification at times: e.g.
> timing is dominated by primary electron ⇒ To first approximation, one and
> same "timeResolution" for both coordinates.

| parameter | struct default | CyMBaL (`MPGDBarrel`) | outer barrel | meaning |
|---|---|---|---|---|
| `readout` | `""` | `"MPGDBarrelHits"` | `"OuterMPGDBarrelHits"` | *"Readout identifiers for tagging 1st and 2nd coord. of 2D-strip readout"* |
| `threshold` | `0 keV` | `100 eV` | `100 eV` | as pixel path |
| `timeResolution` | `8` (*"what units???"*) | `10` | **`5`** | the only parameter that differs between the two barrels |
| `gain` | `10000` | `10000` | `10000` | detector gas gain (one simulation parameter for the whole detector) |
| `stripResolutions` | `{150 µm, 150 µm}` | `{150 µm, 150 µm}` | `{150 µm, 150 µm}` | per-coordinate strip resolution |
| `stripNumbers` | `{1024, 1024}` | from XML `MMnStripsPhi`, `MMnStripsZ` | from XML `MPGDOuterBarrelnStrips` (same value both coordinates) | channels per module |

([`MPGDTrackerDigiConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/MPGDTrackerDigiConfig.h),
[`MPGD.cc#L111-L134`](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L111-L134),
[`#L169-L189`](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L169-L189))

If the strip-count constants are missing from the geometry the plugin throws:
*"MPGD "%s": Error retrieving #channels from XML: no "%s" constant found."*

## Stage 2 — Hit reconstruction

**Pixel path:** [`TrackerHitReconstruction`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerHitReconstruction.cc)
with `timeResolution = 10` for all four detectors (explicitly set, matching
the struct default).

**2D-strip path:** [`MPGDHitReconstruction`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/MPGDHitReconstruction.cc),
which takes the strip geometry into account:

| parameter | struct default | barrel value | meaning |
|---|---|---|---|
| `readout` | `""` | `"MPGDBarrelHits"` / `"OuterMPGDBarrelHits"` | *"Readout identifiers for dividing detector"* |
| `timeResolution` | `10` | `10` | written into `TrackerHit::timeError` |
| `stripResolutions` | `{150 µm, 150 µm}` | `{150 µm, 150 µm}` | position resolution comes from the strip pitch, not the cell dimensions |

([`MPGDHitReconstructionConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/MPGDHitReconstructionConfig.h),
[`MPGD.cc#L146-L155`](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L146-L155),
[`#L201-L210`](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L201-L210))

Note that the outer barrel's 2D-strip reconstruction resets `timeResolution`
to `10` even though its *digitization* used `5`.

There is **no noise stage** for any MPGD — unlike the three silicon
subsystems.

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc#L148-L171`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L148-L171)):
all four `…RecHits`, all four `…RawHits`, all four sim-hit collections
(`MPGDBarrelHits`, `OuterMPGDBarrelHits`, `BackwardMPGDEndcapHits`,
`ForwardMPGDEndcapHits`) and all four pairs of `…RawHitLinks` /
`…RawHitAssociations`.

Downstream: all four `…RecHits` collections are among the seven merged into
**`CentralTrackingRecHits`**
([`tracking.cc#L71-L77`](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L71-L77)).
`OuterMPGDBarrel` additionally gets special treatment in
`TrackerMeasurementFromHits`, where a `CartesianGridUV` segmentation causes
the covariance to be rotated by the strip angle — see
[Tracking → Stage 3]({% link docs/eicrecon/tracking.md %}).

## Caveats / needs human verification

1. **The two digitization paths produce identically-named collections.** A
   file cannot be introspected to learn whether pixel or 2D-strip readout was
   used; only the log line records it. This is a real analysis hazard.
2. The outer barrel's digi `timeResolution = 5` versus its reco
   `timeResolution = 10` is an inconsistency in the 2D-strip path — the value
   written into `TrackerHit::timeError` does not match the smearing applied.
   Possibly intentional, possibly a copy-paste; needs a maintainer.
3. `gain = 10000` and `stripResolutions = 150 µm` carry no provenance comment
   in either the config header or the plugin.
4. `threshold = 100 eV` for a gaseous detector is set identically for all four
   MPGDs with no justification.
5. The MPGDs have **no dedicated system-ID constants** in
   [`definitions.xml`](https://github.com/eic/epic/blob/main/compact/definitions.xml);
   they draw from the 40–85 tracker block through the subassembly mechanism.
   The exact per-detector assignment lives in the MPGD compact files and has
   not been traced here.
6. The default `SiFactoryPattern = 0x3` means **pixel digitization is the
   shipped default** even though the detectors are strip devices. The 2D-strip
   path only activates if the geometry sets the `_2DStrip` constants.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
