---
title: Forward TOF — AC-LGAD (ECTOF)
parent: EICrecon
nav_order: 17
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Endcap Time-of-Flight (ECTOF) Reconstruction

*Also known as: ECTOF, FTOF, forward TOF, endcap TOF, endcap time-of-flight, endcap AC-LGAD, forward timing layer, TOF endcap, TOFEndcap (geometry), TOFEndcapHits (readout), TOFEndcap… (collection prefix), ECTOF (flag prefix), system ID 122 (`ForwardTOF_ID`; `BackwardTOF_ID` = 132 is allocated but unused).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The endcap TOF plugin is a near-copy of
[BTOF]({{ site.baseurl }}{% link docs/eicrecon/detectors/btof.md %}) with
**two deliberate differences**: it uses `EICROCDigitization` instead of
`CFDROCDigitization`, and it has **no calibration stage** at all. Everything
is registered in
[`src/detectors/ECTOF/ECTOF.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc)
(114 lines). The runtime flag prefix is `ECTOF:` (48 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json), seven
fewer than `BTOF:` — exactly the missing calibration factory).

Despite the name, "ECTOF" and "FTOF" are the same detector; the geometry
constant it corresponds to is `ForwardTOF_ID`.

## Chain overview

**Front end:**

`TOFEndcapHits` (edm4hep::SimTrackerHit)
→ **SiliconChargeSharing** → `TOFEndcapSharedHits`

**Bypass path — this is what tracking uses:**

`TOFEndcapSharedHits` + `EventHeader`
→ **SiliconTrackerDigi** → `TOFEndcapSharedRawHits` (+ `…SharedRawHitLinks`, `…SharedRawHitAssociations`)
→ **TrackerHitReconstruction** → `TOFEndcapSharedRecHits`
→ **LGADHitClustering** → **`TOFEndcapClusterHits`** *(edm4eic::Measurement2D)*

with the same registration comment as the barrel:

> temporary steps to bypass pulse digitization and jump right from
> ChargeSharing to clusters — Avoid efficiency loss until we can simulate
> hardware accurately
> ([`ECTOF.cc#L58-L59`](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L58-L67))

**Waveform path — terminal:**

`TOFEndcapSharedHits`
→ **PulseGeneration** → `TOFEndcapSmoothPulses`
→ **PulseCombiner** → `TOFEndcapCombinedPulses`
→ **SiliconPulseDiscretization** → `TOFEndcapPulses`
→ **EICROCDigitization** → `TOFEndcapADCTDC` *(terminal — no consumer)*

## Parameters

Identical to the barrel except where marked.

| stage | algorithm | parameter | struct default | ECTOF value |
|---|---|---|---|---|
| charge sharing | [`SiliconChargeSharing`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconChargeSharing.cc) | `sigma_mode` | `abs` | `rel` |
| | | `sigma_sharingx` / `sigma_sharingy` | *(uninitialised)* | `0.5` / `0.5` (cell widths) |
| | | `min_edep` | *(uninitialised)* | `6 keV` |
| | | `readout` | *(uninitialised)* | `"TOFEndcapHits"` |
| digitization | [`SiliconTrackerDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconTrackerDigi.cc) | `threshold` | `0 keV` | `0.0` |
| | | `timeResolution` | `8` | `0.025` (*"[ns]"*) — 25 ps |
| hit reco | [`TrackerHitReconstruction`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerHitReconstruction.cc) | `timeResolution` | `10` (ns) | default (empty config) |
| clustering | [`LGADHitClustering`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/LGADHitClustering.cc) | `readout` | `"TOFBarrelHits"` | `"TOFEndcapHits"` |
| | | `deltaT` | `1 ns` | default |
| | | `useAve` | `false` | `true` |

([`ECTOF.cc#L37-L74`](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L37-L74))

The clustering algorithm is *"just a simple weighted average. More
sophisticated algorithm TBD."*

### Waveform branch

The gain derivation is copied verbatim from the barrel
([`ECTOF.cc#L76-L83`](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L76-L83)):
`sigma_analog = 0.293951 ns`, `Vm = 3e-4 GeV`, `adc_range = 256`, `offset = 3`
→ `gain ≈ -1.3885e6`. See the
[Pulse chain page]({{ site.baseurl }}{% link docs/eicrecon/algorithms/pulse-chain.md %})
for the algorithms themselves.

| factory | algorithm | parameters |
|---|---|---|
| `TOFEndcapSmoothPulses` | `PulseGeneration` | `pulse_shape_function = "LandauPulse"`, `pulse_shape_params = {gain, 0.293951 ns, 3}`, `ignore_thres = 12.8`, `timestep = 0.01 ns` |
| `TOFEndcapCombinedPulses` | `PulseCombiner` | `minimum_separation = 25 ns` |
| `TOFEndcapPulses` | `SiliconPulseDiscretization` | `EICROC_period = 25 ns`, `local_period = 25 ns / 1024`, `global_offset = -0.431853 ns` |
| `TOFEndcapADCTDC` | [`EICROCDigitization`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/EICROCDigitization.cc) | all defaults: `adc_bit = 8`, `tdc_bit = 10`, `adc_range = 2⁸ = 256`, `tdc_range = 1024`, `t_thres = -1` (*"in ADC unit"*), `tMax = 25 ns` |

The two ROC digitizers differ in more than the name: `EICROCDigitization` has
a `t_thres` (fixed threshold) where `CFDROCDigitization` has a `fraction`
(constant-fraction discrimination), and their `adc_range` defaults differ by a
factor 10 (`256` vs `2560`)
([`EICROCDigitizationConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/EICROCDigitizationConfig.h),
[`CFDROCDigitizationConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CFDROCDigitizationConfig.h)).

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc#L104-L128`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L104-L128)):
`TOFEndcapHits`, `TOFEndcapSharedHits`, `TOFEndcapSharedRawHits`,
`TOFEndcapSharedRecHits`, `TOFEndcapSharedRawHitLinks`,
`TOFEndcapSharedRawHitAssociations`, `TOFEndcapClusterHits`,
`TOFEndcapADCTDC`.

**Transient** unless requested: `TOFEndcapSmoothPulses`,
`TOFEndcapCombinedPulses`, `TOFEndcapPulses`.

Downstream: `TOFEndcapClusterHits` joins `TOFBarrelClusterHits` and
`CentralWithoutTOFTrackerMeasurements` in **`CentralTrackerMeasurements`** —
see [Tracking]({{ site.baseurl }}{% link docs/eicrecon/tracking.md %}). PID
comes from the shared `calibrations/tof.lut` table, keyed on `BarrelTOF_ID`
even for the endcap — see
[Particle identification]({{ site.baseurl }}{% link docs/eicrecon/pid.md %}).

## Caveats / needs human verification

1. **No calibration stage.** The barrel runs `LGADHitCalibration` on its
   `ADCTDC` words; the endcap does not, so `TOFEndcapADCTDC` is the end of
   that branch. Whether the endcap simply has not been given a calibration
   yet, or is intended to be calibrated elsewhere, is not stated.
2. **`TOFEndcapRawHitLinks` / `TOFEndcapRawHitAssociations` are in the default
   output list but have no producer** — the plugin emits the `…Shared…`
   variants. Same stale-entry problem as the barrel
   ([`JEventProcessorPODIO.cc#L122-L125`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L122-L125)).
3. The same 25 ps digi / 10 ns rec-hit `timeError` mismatch as the barrel.
4. Why the barrel uses CFD and the endcap uses a fixed threshold is not
   explained in either plugin — the ASICs may genuinely differ, or one may be
   a leftover.
5. `min_edep` is written `6 * dd4hep::keV` here and `6.0 * edm4eic::unit::keV`
   in the barrel; both resolve to the same 6 keV in the CI dump
   (`6.00000021e-06` GeV), but the two unit systems are mixed within one
   detector family.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
