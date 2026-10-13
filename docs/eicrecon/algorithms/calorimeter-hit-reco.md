---
title: CalorimeterHitReco
parent: EICrecon
nav_order: 31
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# CalorimeterHitReco — raw ADC/TDC words back to calibrated hits

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

`CalorimeterHitReco` is the exact inverse of
[CalorimeterHitDigi](calorimeter-hit-digi.md) — its header says so:
*"Reconstruct digitized outputs, paired with Jug::Digi::CalorimeterHitDigi"*
([CalorimeterHitReco.h#L4-L6](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.h#L4-L6)).
It takes an `edm4hep::RawCalorimeterHit` collection and produces
`edm4eic::CalorimeterHit`, the first object in the chain that carries a physical
energy in GeV, a time in ns, and a position in mm
([CalorimeterHitReco.h#L32-L44](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.h#L32-L44)).
Because it is the inverse of digitisation, every plugin that instantiates it
passes the *same* `capADC`, `dyRangeADC`, `pedMeanADC`, `pedSigmaADC` and
`resolutionTDC` values it gave the digitiser — usually literally the same
variables, declared once under a comment reading *"Make sure digi and reco use
the same value"*.

## What it does to the data

**Zero suppression.** This is where the calorimeter cut actually happens, since
the digitiser writes every channel. A hit survives only if its amplitude clears
the pedestal plus a threshold
([L181-L183](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L181-L183)):

```
thresholdADC = thresholdFactor * pedSigmaADC + thresholdValue
keep if amplitude >= pedMeanADC + thresholdADC
```

The two ways of expressing the cut are mutually exclusive by construction:
`init()` checks `thresholdFactor * thresholdValue != 0` and throws if both are
non-zero, with the comment *"Should set either m_cfg.thresholdFactor or
m_cfg.thresholdValue, not both"*
([L48-L54](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L48-L54)).
`thresholdFactor` expresses the cut in units of the electronics noise sigma — the
natural choice when you want a fixed false-hit rate — while `thresholdValue` is
a flat ADC cut, the natural choice when you have a physics target ("0.5 MeV" or
"half a MIP") and have already worked out what that is in counts. Most ePIC
calorimeters use the flat cut and leave a comment showing the arithmetic; the
two ZDC sections are the exception and use 3–4 noise sigmas. A saturated hit
(`amplitude > capADC`) is logged as an error and dropped
([L185-L189](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L185-L189)).

**ADC to energy.** Pedestal subtraction, projection back through the ADC scale,
then division by the sampling fraction
([L200-L202](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L200-L202)):

```
energy = (amplitude - pedMeanADC) / capADC * dyRangeADC / sampFrac
```

The first three terms undo the digitiser exactly. The last term is the physics:
in a sampling calorimeter only a small fraction of a shower's energy is deposited
in the active medium, so dividing by that fraction recovers the incident energy
scale. The values in use span two and a half orders of magnitude — 0.998 for the
homogeneous PbWO₄ B0 ECal, 0.96 for the EEMC crystals, 0.093 for BEMC ScFi,
0.033 for BHCAL, 0.0095 for the endcap HCal, and 0.0043 for the AstroPix imaging
layers, which sample a tiny slice of the barrel shower.

**`sampFrac` is a string expression, not a number.** It is compiled once at
`init()` by `EvaluatorSvc` into a `std::function<double(RawCalorimeterHit)>`,
with **every cellID field of the readout in scope as a named variable**
([L123-L135](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L123-L135)).
A pure-number string short-circuits to a constant; anything else is compiled via
ROOT's interpreter. This makes a position-dependent calibration possible without
a new algorithm — LFHCAL uses
`"(rlayerz == 0) ? 0.019 : 0.037"`, applying a different sampling fraction to the
zeroth tile of each longitudinal block
([FHCAL.cc#L209](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L209)).
It is also the only per-hit-variable knob the algorithm has; there is no
per-layer calibration table.

**TDC to time.** `stepTDC = 1 ns / resolutionTDC` is the counts-per-ns factor
computed at init, and the time is simply `timeStamp / stepTDC`
([L56](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L56),
[L204](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L204)).
The quantisation introduced by the digitiser is not undone and no walk or
time-of-flight correction is applied. Both the energy error and the time error
on the output hit are written as literal zero
([L309-L310](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L309-L310)).

**Geometry: this is where a hit stops being just a number.** The cellID is handed
to the DD4hep `CellIDPositionConverter` to get a global position
([L212](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L212)),
then to the volume manager to find the enclosing `DetElement`, whose nominal
transform gives the local position via `worldToLocal`
([L236-L241](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L236-L241),
[L255](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L255)).
Which `DetElement` counts as "local" is chosen either by name
(`localDetElement`) or by masking the cellID down to a set of fields
(`localDetFields`); with neither, the lowest-level element reached from the full
cellID is used
([L137-L156](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L137-L156)).
Local coordinates matter downstream because island clustering measures
neighbour distances in the local frame. The `layerField` and `sectorField` names
are decoded into the hit's `layer` and `sector` attributes, or set to −1 when not
configured
([L192-L197](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L192-L197)).

**Cell dimensions.** The algorithm asks the converter for the segmentation
attached to the local element, unwrapping `MultiSegmentation` layers until it
reaches a concrete one
([L259-L271](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L259-L271)).
`CartesianGridXY`, `HexGridXY` and `CartesianGridXYStaggered` yield transverse
cell sizes into `dimension.x/y`; `CartesianStripZ` yields a longitudinal size
into `dimension.z`; anything else falls back to twice the half-lengths of the
placement volume's bounding box, with a one-shot warning for unsupported types
([L273-L298](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L273-L298)).

**The `maskPos` machinery.** For a finely segmented readout the true cell centre
is not always the position you want to cluster on. BEMC ScFi is the motivating
case: individual scintillating fibres are far finer than the effective transverse
readout granularity, so its comment reads *"here we want to use grid center
position (XY) but keeps the z information from fiber-segment"*
([BEMC.cc#L270-L273](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L270-L273)).
The mechanism has two parts. `maskPosFields` names cellID fields whose bits are
OR-ed into `gpos_mask` at init
([L81-L88](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L81-L88)).
At process time the converter is asked for the position of
`cellID & ~gpos_mask` — the mother volume obtained by zeroing those fields — and
then `maskPos` is read character by character, with `x`, `y` or `z` (case
insensitive) selecting which coordinates of the true position get overwritten by
the mother-volume ones
([L215-L233](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L215-L233)).
So `maskPos = "xy"` with `maskPosFields = {"fiber", "z"}` means: take the coarse
grid centre in x and y, but keep the fine fibre-segment z. Any character other
than x/y/z is silently ignored, and if `maskPosFields` is empty `gpos_mask`
stays 0 and the whole block is skipped.

**Bad-cellID self-defence.** If a cellID cannot be resolved by the geometry, the
exception is caught, a counter is incremented, and after
`MaxCellIDerrors = 100` failures the algorithm disables itself for the rest of
the job rather than flooding the log
([L59-L67 of the header](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.h#L59-L67),
[L165-L175](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L165-L175),
[L242-L253](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L242-L253)).
The comment names HcalBarrel as the detector that historically triggered this.

## Configuration

Every field of
[`CalorimeterHitRecoConfig`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitRecoConfig.h#L11-L39).
Defaults are the literal struct initialisers; dd4hep base units are GeV, mm, ns,
so a bare `1` in an energy field is 1 GeV and in a time field 1 ns.

| field | struct default | meaning |
|---|---|---|
| `capADC` | `1` | ADC counts at full scale. Must match the digitiser. Hits above it are dropped with an error. |
| `dyRangeADC` | `1` → 1 GeV | Energy at full ADC scale. Must match the digitiser. |
| `pedMeanADC` | `0` | Pedestal mean, subtracted from the amplitude and also added to the threshold. Must match the digitiser. |
| `pedSigmaADC` | `0` | Pedestal sigma. Used **only** as the multiplicand of `thresholdFactor`; several plugins set it and note in a comment that it is unused. |
| `resolutionTDC` | `1` → 1 ns | TDC least count. `stepTDC = 1 ns / resolutionTDC`; time is `timeStamp / stepTDC`. |
| `corrMeanScale` | `1` | Present in the struct under *"digitization settings"* but **never referenced** in `CalorimeterHitReco.cc`. Dead field — see caveats. |
| `thresholdFactor` | `0` | Zero-suppression threshold in units of `pedSigmaADC`. Exactly one of this and `thresholdValue` may be non-zero. |
| `thresholdValue` | `0` | Flat zero-suppression threshold in ADC counts above the pedestal. |
| `sampFrac` | `"1.0"` | Sampling fraction, as a **string expression** compiled per hit with all cellID fields of `readout` in scope. `energy` is divided by it. |
| `readout` | `""` | DD4hep readout name. If empty, `init()` returns early and no cellID decoding happens — see caveats. |
| `layerField` | `""` | cellID field decoded into the hit's `layer`. Empty gives `layer = -1`. |
| `sectorField` | `""` | cellID field decoded into the hit's `sector`. Empty gives `sector = -1`. |
| `localDetElement` | `""` | Name of the DD4hep `DetElement` defining the local frame. Takes priority over `localDetFields`; a lookup failure logs an error and aborts init. |
| `localDetFields` | `{}` | cellID fields defining the local frame by masking. Struct comment: *"if nothing is provided, the lowest level DetElement (from cellID) will be used"*. |
| `maskPos` | `""` | Which coordinates of the global position to replace with the mother-volume position: any subset of the characters `x`, `y`, `z`, case-insensitive. |
| `maskPosFields` | `{}` | cellID fields zeroed to obtain that mother volume. Empty disables the masking entirely, regardless of `maskPos`. |

## Which detectors use it

Thirteen instances across nine JANA2 plugins — one per digitiser instance. The
instance name equals the output rec-hit collection name in every case, and the
input is always the matching `…RawHits` collection.

| plugin | instance / output collection | readout |
|---|---|---|
| [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L255-L276) | `EcalBarrelScFiRecHits` | `EcalBarrelScFiHits` |
| [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L396-L412) | `EcalBarrelImagingRecHits` | `EcalBarrelImagingHits` |
| [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L64-L78) | `EcalEndcapNRecHits` | `EcalEndcapNHits` |
| [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L122-L138) | `EcalEndcapPRecHits` | `EcalEndcapPHits` |
| [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L48-L62) | `EcalFarForwardZDCRecHits` | `EcalFarForwardZDCHits` |
| [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L159-L175) | `HcalFarForwardZDCRecHits` | `HcalFarForwardZDCHits` |
| [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L55-L71) | `HcalEndcapNRecHits` | `HcalEndcapNHits` |
| [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L58-L74) | `HcalEndcapPInsertRecHits` | `HcalEndcapPInsertHits` |
| [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L199-L214) | `LFHCALRecHits` | `LFHCALHits` |
| [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L43-L57) | `EcalLumiSpecRecHits` | `EcalLumiSpecHits` |
| [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L44-L58) | `B0ECalRecHits` | `B0ECalHits` |
| [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L70-L86) | `HcalBarrelRecHits` | `HcalBarrelHits` |

### Key parameters compared

`capADC`, `dyRangeADC`, `pedMeanADC`, `pedSigmaADC` and `resolutionTDC` are
identical to the digitiser values tabulated on the
[CalorimeterHitDigi page](calorimeter-hit-digi.md) and are not repeated here.

| instance | `sampFrac` | `thresholdValue` | `thresholdFactor` | `layerField` / `sectorField` |
|---|---|---|---|---|
| `EcalBarrelScFiRecHits` | `"0.09285755"` | 5.0 | 0 | `layer` / `sector` |
| `EcalBarrelImagingRecHits` | `"0.00429453"` | 41 | 0 | `layer` / `sector` |
| `EcalEndcapNRecHits` | `"0.96"` | 4.0 | 0 | — / — |
| `EcalEndcapPRecHits` | `"1.00"` | 3 | 0 | — / — |
| `EcalFarForwardZDCRecHits` | `"1.0"` | 0 | **4.0** | — / — |
| `HcalFarForwardZDCRecHits` | `"1.0"` | 0 | **3.0** | `layer` / `system` |
| `HcalEndcapNRecHits` | `"0.0095"` | 41.0 | 0 | — / — |
| `HcalEndcapPInsertRecHits` | `"1.0"` | 41.0 | 0 | `layer` / — |
| `LFHCALRecHits` | `"(rlayerz == 0) ? 0.019 : 0.037"` | 20 | 0 | `rlayerz` / — |
| `EcalLumiSpecRecHits` | `"1.0"` | 2.0 | 0 | — / — |
| `B0ECalRecHits` | `"0.998"` | 1.0 | 0 | — / `sector` |
| `HcalBarrelRecHits` | `"0.033"` | 33 | 0 | `""` / `""` |

Only two instances use the extended geometry options. `EcalBarrelScFiRecHits`
sets `localDetFields = {"system", "sector"}` together with `maskPos = "xy"` and
`maskPosFields = {"fiber", "z"}`
([BEMC.cc#L269-L273](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L269-L273));
`HcalFarForwardZDCRecHits` is the only instance that uses `system` as its
sector field. `localDetElement` is not used by any ePIC plugin.

Threshold provenance is spelled out in comments at nearly every call site:
`5.0` for BEMC ScFi is *"16384 ADC counts/1500 MeV * 0.5 MeV (desired threshold)
= 5.46"*, `41` for BEMC Imaging is *"8192 ADC counts/3 MeV * 0.015 MeV = 41"*,
`4.0` for EEMC is *"(20. GeV / 16384) * 4 ~= 5 MeV"*, `41.0` for EHCAL is
*"0.1875 MeV deposition out of 200 MeV max (per layer)"*, and `33` for BHCAL is
*"pedSigmaADC + thresholdValue = half-MIP (333 ADC)"*. FEMC's `3` carries the
most careful note: the ADC of a 15 MeV particle is 202.4576, the comparison is
strictly `<`, so the effective cut is 15.25 MeV
([FEMC.cc#L131-L133](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L131-L133)).

Two instances reconstruct with `sampFrac = "1.0"` for different reasons. FEMC
already divided by the sampling fraction in the digitiser through `corrMeanScale`
(*"already taken care in DIGI code above"*), while the ZDC sections and
`HcalEndcapPInsertRecHits` apply no sampling correction at hit level at all —
for those it is applied later, at clustering.

## Runtime flags: names differ from config fields

Parameter names are declared in
[`CalorimeterHitReco_factory.h#L25-L38`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/CalorimeterHitReco_factory.h#L25-L38);
a flag is `<PLUGIN>:<instance>:<flag name>`, e.g.
`BEMC:EcalBarrelScFiRecHits:samplingFraction`.

| config field | runtime flag |
|---|---|
| `capADC` | `capacityADC` |
| `dyRangeADC` | `dynamicRangeADC` |
| `pedMeanADC` | `pedestalMean` |
| `pedSigmaADC` | `pedestalSigma` |
| `sampFrac` | `samplingFraction` |
| `resolutionTDC`, `thresholdFactor`, `thresholdValue`, `readout`, `layerField`, `sectorField`, `localDetElement`, `localDetFields` | unchanged |
| `corrMeanScale`, `maskPos`, `maskPosFields` | **not exposed** — compile-time only |

{: .note }
The digi factory exposes the readout name as `readoutClass` while the reco
factory calls the same field `readout`
([CalorimeterHitDigi_factory.h#L37](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/CalorimeterHitDigi_factory.h#L37)).
The two must agree in value but not in flag name.

## Source

- [`src/algorithms/calorimetry/CalorimeterHitReco.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.h)
- [`src/algorithms/calorimetry/CalorimeterHitReco.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc)
- [`src/algorithms/calorimetry/CalorimeterHitRecoConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitRecoConfig.h)
- [`src/factories/calorimetry/CalorimeterHitReco_factory.h`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/CalorimeterHitReco_factory.h)
- [`src/services/evaluator/EvaluatorSvc.h`](https://github.com/eic/EICrecon/blob/main/src/services/evaluator/EvaluatorSvc.h)
  — the string-expression compiler behind `sampFrac`

## Caveats

1. **`corrMeanScale` is dead.** `CalorimeterHitRecoConfig` declares
   `double corrMeanScale{1}` under *"digitization settings"*, but the string
   `corrMeanScale` does not appear anywhere in `CalorimeterHitReco.cc`. It is
   also not exposed as a runtime flag. Presumably a leftover from a symmetry with
   the digi config; setting it has no effect.
2. **`throw;` with no active exception.** The both-thresholds-set check ends with
   a bare `throw;` and the comment *"throw with an argument doesn't trigger
   abort"*
   ([L52](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L52)).
   A bare `throw` outside a handler calls `std::terminate`, i.e. it aborts — the
   comment reads as the opposite of what the code does. The error message is
   printed first, so the failure is at least diagnosable.
3. **An empty `readout` makes `process()` throw.** `init()` returns early when
   `readout` is empty, and also on several geometry-lookup failures
   ([L59-L61](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L59-L61),
   [L66-L69](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L66-L69),
   [L118](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L118)).
   In all those paths the `sampFrac` `std::function` is never assigned, so the
   first call at
   [L200](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L200)
   throws `std::bad_function_call`. The warning block promises *"the position,
   energy, and time values should still be good"*, which is not true today. Every
   ePIC plugin sets `readout`, so this is latent rather than active.
4. **A missing `maskPosFields` entry silently disables masking.** The mask is
   built in a `try` block and assigned only if all fields resolve
   ([L81-L88](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L81-L88));
   a failure warns and drops through to the early return at
   [L118](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L118),
   which in turn triggers caveat 3.
5. **The threshold comparison is `<`, so the cut is exclusive.** A hit with
   `amplitude == pedMeanADC + thresholdADC` is *kept*. FEMC's comment is the only
   place in the tree that acknowledges this ("cut off is `<`. So 3 here =
   15.25 MeV"); the other quoted derivations are approximate to that extent.
6. **`pedSigmaADC` is passed even where it is unused.** BEMC, BHCAL and others
   set it and annotate it *"not needed; use only thresholdValue"* / *"not used;
   relying on energy cut"*. Harmless, but it means the reco `pedSigmaADC` value
   is not evidence about what the algorithm is doing.
7. **Hard-coded sampling fractions with no provenance.** `0.09285755`,
   `0.00429453`, `0.029043`, `0.0095`, `0.019`/`0.037` and `0.033` appear as bare
   literals. Only two carry any note at all (*"from latest study"* for EHCAL,
   *"average, from sPHENIX simulations"* for BHCAL); which geometry version or
   calibration sample produced the others is not determinable from EICrecon
   source.
8. **`sampFrac` is compiled with ROOT's interpreter.** `EvaluatorSvc` documents
   that non-numeric expressions go through `TInterpreter`, that the return type is
   fixed to `double`, and that the available variable list can be inspected with
   `-PEvaluatorSvc:LogLevel=debug`. A typo in a field name is therefore a
   run-time, not compile-time, failure.
9. **`dimension` is only partly filled.** The grid branches set `x` and `y` and
   leave `z` zero; the strip branch sets only `z`. Consumers that assume all
   three are populated will read zeros
   ([L273-L298](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L273-L298)).
   The `//FIXME: needs to come from the geometry service/converter` at
   [L301](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L301)
   suggests this area is known to be provisional.
10. **No unit test.** Unlike `CalorimeterHitDigi`, there is no
    `calorimetry_CalorimeterHitReco.cc` under `src/tests/algorithms_test/`.
11. **Cell dimensions are read from the *local* element's readout**
    (`m_converter->findReadout(local)`), not from the hit's own readout. For
    configurations where `localDetFields` masks up to a coarse element this could
    in principle disagree with the hit's segmentation; not observed to be a
    problem in the ePIC setup, but worth a maintainer's eye.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
(fetched 2026-08-19). AI-authored draft — verify against source.*
