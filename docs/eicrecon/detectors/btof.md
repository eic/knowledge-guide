---
title: Barrel TOF — AC-LGAD (BTOF)
parent: EICrecon
nav_order: 16
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Barrel Time-of-Flight (BTOF) Reconstruction

*Also known as: BTOF, barrel TOF, barrel time-of-flight, barrel AC-LGAD, barrel timing layer, TOF barrel, LGAD barrel, TOFBarrel (geometry), TOFBarrelHits (readout), TOFBarrel… (collection prefix), BTOF (flag prefix), system ID 92 (`BarrelTOF_ID`; `TOFSubAssembly_ID` = 93).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The barrel TOF is an **AC-LGAD** detector, and its plugin is the only tracker
plugin that carries a full waveform simulation: Landau pulse generation,
pulse combination, EICROC-clock discretization and constant-fraction
digitization. That entire branch, however, is **currently a side branch** —
the collection that tracking actually consumes is produced by a short
"temporary" bypass path whose own comment says so. Everything is registered in
[`src/detectors/BTOF/BTOF.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc).
The runtime flag prefix is `BTOF:` (55 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

## Chain overview

**Front end (shared):**

`TOFBarrelHits` (edm4hep::SimTrackerHit)
→ **SiliconChargeSharing** → `TOFBarrelSharedHits`

**Bypass path — this is what tracking uses:**

`TOFBarrelSharedHits` + `EventHeader`
→ **SiliconTrackerDigi** → `TOFBarrelSharedRawHits` (+ `…SharedRawHitLinks`, `…SharedRawHitAssociations`)
→ **TrackerHitReconstruction** → `TOFBarrelSharedRecHits`
→ **LGADHitClustering** → **`TOFBarrelClusterHits`** *(edm4eic::Measurement2D)*

The registration comment is explicit:

> temporary steps to bypass pulse digitization and jump right from
> ChargeSharing to clusters — Avoid efficiency loss until we can simulate
> hardware accurately
> ([`BTOF.cc#L70-L71`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L70-L79))

**Waveform path — realistic, but not yet feeding reconstruction:**

`TOFBarrelSharedHits`
→ **PulseGeneration** → `TOFBarrelSmoothPulses`
→ **PulseCombiner** → `TOFBarrelCombinedPulses`
→ **SiliconPulseDiscretization** → `TOFBarrelPulses`
→ **CFDROCDigitization** → `TOFBarrelADCTDC`
→ **LGADHitCalibration** → `TOFBarrelCalibratedHits` *(terminal — nothing consumes it)*

## Stage 1 — Charge sharing

**Algorithm:** [`SiliconChargeSharing`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconChargeSharing.cc)
— spreads each sim hit's deposit over neighbouring cells according to a
Gaussian whose width is set relative to, or absolutely in, cell units.

| parameter | struct default | BTOF value | meaning |
|---|---|---|---|
| `sigma_mode` | `abs` | `rel` | *"rel means relative, so charge sharing range = sigma_sharingx \* cell_width_x, etc for y; abs means absolute"* |
| `sigma_sharingx` | *(uninitialised)* | `0.5` | with `rel`, half a cell width in x |
| `sigma_sharingy` | *(uninitialised)* | `0.5` | half a cell width in y |
| `min_edep` | *(uninitialised)* | `6.0 keV` | minimum shared deposit kept |
| `readout` | *(uninitialised)* | `"TOFBarrelHits"` | readout supplying the segmentation |

([`SiliconChargeSharingConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconChargeSharingConfig.h),
[`BTOF.cc#L59-L68`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L59-L68))
The struct has no in-struct initialisers for the four numeric fields, so the
plugin's assignment is what defines them.

## Stage 2 — Bypass digitization and hit reconstruction

**Algorithm:** [`SiliconTrackerDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconTrackerDigi.cc).

| parameter | struct default | BTOF value | meaning |
|---|---|---|---|
| `threshold` | `0 keV` | `0.0` | no additional energy cut (the cut already happened in charge sharing) |
| `timeResolution` | `8` | `0.025` (*"[ns]"*) | 25 ps — the AC-LGAD design timing resolution |

Then [`TrackerHitReconstruction`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerHitReconstruction.cc)
with an **empty config**, so `timeResolution` reverts to the struct default
`10` ns
([`BTOF.cc#L82-L86`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L82-L86)).

## Stage 3 — LGAD hit clustering

**Algorithm:** [`LGADHitClustering`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/LGADHitClustering.cc)
— *"cluster all hits in a sensor into one hit location. Currently it's just a
simple weighted average. More sophisticated algorithm TBD."*

| parameter | struct default | BTOF value | meaning |
|---|---|---|---|
| `readout` | `"TOFBarrelHits"` | `"TOFBarrelHits"` | readout whose sensor field defines a cluster |
| `deltaT` | `1 ns` | default | time window for grouping |
| `useAve` | `false` | `true` | use the (weighted) average rather than the leading hit |

([`LGADHitClusteringConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/LGADHitClusteringConfig.h),
[`BTOF.cc#L50-L57`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L50-L57))

This stage emits `edm4eic::Measurement2D` directly, which is why the TOF
layers **skip** `TrackerMeasurementFromHits` and enter track finding one step
later than the silicon and MPGD layers — see
[Tracking → Stage 3]({% link docs/eicrecon/tracking.md %}).

## Stage 4 — The waveform branch

Shared machinery with the other pulse-based chains; see the
[Pulse chain page]({% link docs/eicrecon/algorithms/pulse-chain.md %}).
The gain is *derived*, not typed in
([`BTOF.cc#L88-L99`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L88-L99)):

> calculation of the extreme values for Landau distribution can be found on
> lin 514-520 of … Landau reaches minimum for mpv = 0 and sigma = 1 at
> x = -0.22278 … gain is set such that pulse reaches a height of adc_range
> when EDep = Vm. gain is negative as LGAD voltage is always negative

with `sigma_analog = 0.293951 ns`, `Vm = 3e-4 GeV`, `adc_range = 256`,
`offset = 3`, giving `gain ≈ -1.3885e6` (the value that appears in the CI
dump as `BTOF:LGADPulseGeneration:pulseShapeParams`).

| factory | algorithm | parameters |
|---|---|---|
| `LGADPulseGeneration` | [`PulseGeneration`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.h) | `pulse_shape_function = "LandauPulse"`, `pulse_shape_params = {gain, 0.293951 ns, 3}`, `ignore_thres = 0.05 × 256 = 12.8`, `timestep = 0.01 ns` |
| `TOFBarrelPulseCombiner` | [`PulseCombiner`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseCombiner.h) | `minimum_separation = 25 ns` |
| `TOFBarrelPulses` | [`SiliconPulseDiscretization`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconPulseDiscretization.cc) | `EICROC_period = 25 ns` (*"25 ns is the period of 40MHz EIC clock"*), `local_period = 25 ns / 1024` (*"1024 TDC bin"*), `global_offset = -3 × 0.293951 + 0.45 = -0.431853 ns` |
| `CFDROCDigitization` | [`CFDROCDigitization`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CFDROCDigitization.cc) | all defaults: `adc_bit = 8`, `tdc_bit = 10`, `adc_range = 2⁸ × 10 = 2560`, `tdc_range = 1024`, `fraction = 0.5`, `tMax = 25 ns` |
| `TOFBarrelCalibratedHits` | [`LGADHitCalibration`](https://github.com/eic/EICrecon/blob/main/src/algorithms/reco/LGADHitCalibration.cc) | all defaults: `c_slope = 1.175844e-6`, `c_intercept = 0` (*"parameters that convert ADC to EDep"*), `t_slope = 0.024319882`, `t_intercept = 0.04314` (*"parameters that convert TDC to hit time (ns)"*) |

The calibration factory's registration comment notes *"time walk correction is
still TBD"*
([`BTOF.cc#L39-L45`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L39-L45)).

{: .note }
`adc_range` differs between the two ROC digitizers: `CFDROCDigitization`
(barrel) uses `2⁸ × 10 = 2560`, while `EICROCDigitization`
([endcap]({% link docs/eicrecon/detectors/ectof.md %})) uses
`2⁸ = 256`. The pulse gain in both plugins, however, is computed from a
hard-coded `adc_range = 256`.

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc#L104-L128`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L104-L128)):
`TOFBarrelHits`, `TOFBarrelSharedHits`, `TOFBarrelSharedRawHits`,
`TOFBarrelSharedRecHits`, `TOFBarrelSharedRawHitLinks`,
`TOFBarrelSharedRawHitAssociations`, `TOFBarrelClusterHits`,
`TOFBarrelADCTDC`, and (jointly with the endcap) `CombinedTOFParticleIDs` /
`CombinedTOFTruthSeededParticleIDs`.

**Transient** unless requested: `TOFBarrelSmoothPulses`,
`TOFBarrelCombinedPulses`, `TOFBarrelPulses`, and `TOFBarrelCalibratedHits`.

Downstream: `TOFBarrelClusterHits` is concatenated with
`CentralWithoutTOFTrackerMeasurements` and `TOFEndcapClusterHits` into
**`CentralTrackerMeasurements`**, the input to the CKF — see
[Tracking]({% link docs/eicrecon/tracking.md %}). TOF *PID*
does not come from this plugin at all: it comes from the `calibrations/tof.lut`
table keyed on `BarrelTOF_ID` — see
[Particle identification]({% link docs/eicrecon/pid.md %}).

## Caveats / needs human verification

1. **The realistic digitization chain is dead-ended.** `TOFBarrelADCTDC` →
   `TOFBarrelCalibratedHits` has no consumer anywhere in EICrecon
   (`TOFBarrelCalibratedHits` appears only in `BTOF.cc`), and
   `TOFBarrelCalibratedHits` is not even persisted. Meanwhile the collection
   tracking uses comes from the self-described "temporary" bypass. This is a
   transitional state; the intended end point is not documented.
2. **`TOFBarrelRawHitLinks` and `TOFBarrelRawHitAssociations` are in the
   default output list but no factory produces them** — the plugin emits
   `TOFBarrelSharedRawHitLinks`/`…Associations`. The two names occur only in
   [`JEventProcessorPODIO.cc`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L122-L125).
   Stale entries, presumably harmless, but they mean the output list is not a
   reliable inventory.
3. The digi stage smears time with `0.025` ns while the rec stage writes
   `10` ns into `TrackerHit::timeError` (empty config → struct default). The
   400× mismatch propagates into the ACTS measurement covariance.
4. `LGADHitClustering` is *"just a simple weighted average. More sophisticated
   algorithm TBD"* — so the TOF spatial resolution in EICrecon is not the
   detector's design resolution.
5. `sigma_sharingx = sigma_sharingy = 0.5` (half a cell) and
   `min_edep = 6 keV` carry no provenance comment.
6. `Vm = 3e-4 GeV` as the full-scale energy is hard-coded with no comment.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
