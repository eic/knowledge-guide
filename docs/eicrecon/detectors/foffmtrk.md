---
title: Off-Momentum Tracker (FOFFMTRK)
parent: EICrecon
nav_order: 23
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Forward Off-Momentum Tracker (FOFFMTRK) Reconstruction

*Also known as: OMD, off-momentum detector, off-momentum tracker, forward off-momentum tracker, B1-region tagger, ForwardOffMTracker (geometry), ForwardOffMTrackerHits (readout), ForwardOffM… (collection prefix), FOFFMTRK (flag prefix), system IDs 159–162 (`ForwardOffMTracker_station_1..4_ID`).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The off-momentum detector catches charged fragments whose rigidity puts them
outside the Roman-pot acceptance. Its plugin is a stripped-down
[RPOTS]({{ site.baseurl }}{% link docs/eicrecon/detectors/rpots.md %}): the
same three-stage structure, but with a **single** transfer matrix and no
polynomial variant. 76 lines, registered in
[`src/detectors/FOFFMTRK/FOFFMTRK.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/FOFFMTRK/FOFFMTRK.cc).
The runtime flag prefix is `FOFFMTRK:` (23 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

## Chain overview

`ForwardOffMTrackerHits` (edm4hep::SimTrackerHit) + `EventHeader`
→ **SiliconTrackerDigi** → `ForwardOffMTrackerRawHits` (+ `…RawHitLinks`, `…RawHitAssociations`)
→ **TrackerHitReconstruction** → `ForwardOffMTrackerRecHits`

(`MCParticles`, `ForwardOffMTrackerRecHits`)
→ **MatrixTransferStatic** → **`ForwardOffMRecParticles`**

## Stage 1 — Digitization and hit reconstruction

| stage | algorithm | parameter | struct default | FOFFMTRK value |
|---|---|---|---|---|
| digitization | [`SiliconTrackerDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconTrackerDigi.cc) | `threshold` | `0 keV` | `10.0 keV` |
| | | `timeResolution` | `8` | `8` |
| hit reco | [`TrackerHitReconstruction`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerHitReconstruction.cc) | `timeResolution` | `10` | `8` |

([`FOFFMTRK.cc#L24-L39`](https://github.com/eic/EICrecon/blob/main/src/detectors/FOFFMTRK/FOFFMTRK.cc#L24-L39))
Identical to the Roman pots and B0. Both algorithms are described on the
[Tracking page]({{ site.baseurl }}{% link docs/eicrecon/tracking.md %}).

## Stage 2 — MatrixTransferStatic

**Algorithm:** [`MatrixTransferStatic`](https://github.com/eic/EICrecon/blob/main/src/algorithms/fardetectors/MatrixTransferStatic.cc)
— the same transfer-matrix inversion used by the Roman pots, described there.

| parameter | struct default | FOFFMTRK value | meaning |
|---|---|---|---|
| `matrix_configs` | `{}` | **one** entry, `nomMomentum = 130.0` | one matrix only — no beam-energy selection |
| `hit1minZ` / `hit1maxZ` | `0` / `0` | `25490.0` / `25512.0` | z-window of the first station (mm) |
| `hit2minZ` / `hit2maxZ` | `0` / `0` | `27012.0` / `27035.0` | z-window of the second station (mm) |
| `readout` | `""` | `"ForwardOffMTrackerRecHits"` | collection whose cellIDs are decoded |
| `partMass` / `partCharge` / `partPDG` | `0.938272` / `1` / `2212` | defaults | proton assumed |
| `crossingAngle` | `0.025` | default | beam crossing angle (rad) |
| `requireBeamProton` | `true` | default (the CI dump shows `false`, see note) | require a beam proton in `MCParticles` |
| `requireMatchingMatrix` | `true` | default (**the CI dump shows `false`** — see caveat 2) | require the beam energy to match a configured matrix |

The single `MatrixConfig`
([`FOFFMTRK.cc#L45-L65`](https://github.com/eic/EICrecon/blob/main/src/detectors/FOFFMTRK/FOFFMTRK.cc#L41-L74)):

{% raw %}
| field | value |
|---|---|
| `nomMomentum` | `130.0` |
| `aX` | `{{2.08344, 5.37571}, {0.188756, -2.90941}}` |
| `aY` | `{{-0.977013, -35.7785}, {-0.0812252, -2.86315}}` |
| `local_x_offset` | `-1032.2` |
| `local_y_offset` | `0.00462829` |
| `local_x_slope_offset` | `-59.7363` |
| `local_y_slope_offset` | `-0.0030213` |
{% endraw %}

{: .note }
As with the Roman pots, the CI flag dump runs with
`-PFOFFMTRK:ForwardOffMRecParticles:requireBeamProton=false` in
`JANA_OPTIONS_GUN`
([`linux-eic-shell.yml#L54`](https://github.com/eic/EICrecon/blob/main/.github/workflows/linux-eic-shell.yml#L54)),
so the dumped value is a CI override, not the struct default.

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc#L213-L228`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L213-L228)):
`ForwardOffMTrackerHits`, `ForwardOffMTrackerRawHits`,
`ForwardOffMTrackerRecHits`, `ForwardOffMTrackerRawHitLinks`,
`ForwardOffMTrackerRawHitAssociations`, `ForwardOffMRecParticles`.

Downstream: `ForwardOffMRecParticles` is a far-forward end product; it does
not enter central tracking or the combined `ReconstructedParticles`.

## Caveats / needs human verification

1. **Only one transfer matrix, at 130 GeV.** Unlike the Roman pots (four
   matrices at 275/130/100/41 GeV), the off-momentum tracker has exactly one,
   so any other beam energy has no valid matrix. Note that the Roman pots'
   130 GeV matrix is the one labelled *"NOT TUNED -- just for testing
   purposes"* — whether this detector's 130 GeV matrix shares that status is
   not stated.
2. The CI dump reports `requireMatchingMatrix = false` for this factory but
   `true` (`1`) for the Roman pots' static factory, and the
   `JANA_OPTIONS_GUN` line only overrides `requireBeamProton`. That
   discrepancy is unexplained by anything in the plugin source and needs
   checking against the full CI invocation.
3. `MatrixTransferStatic` consumes `MCParticles`, so this reconstruction is
   truth-assisted and cannot be run unchanged on real data.
4. The z-windows are hard-coded absolute positions in mm; a far-forward
   geometry change silently empties the output.
5. `threshold = 10 keV` is shared with B0 and the Roman pots with no
   detector-specific justification.
6. Geometry note: `ForwardOffMTracker_station_2..3_ID` are 160 and 161, which
   the stale prose block in
   [`definitions.xml`](https://github.com/eic/epic/blob/main/compact/definitions.xml)
   still describes as the ZDC ECal and HCal IDs. Trust the constants — see
   [Detector naming & aliases]({{ site.baseurl }}{% link docs/eicrecon/naming.md %}).

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
