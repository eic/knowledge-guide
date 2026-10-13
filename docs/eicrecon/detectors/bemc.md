---
title: Barrel ECal — BIC (BEMC)
parent: EICrecon
nav_order: 1
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Barrel Electromagnetic Calorimeter (BEMC) Reconstruction

*Also known as: barrel ECal, BIC, barrel imaging calorimeter, ScFi/AstroPix hybrid ECal, EcalBarrel (collection prefix), EcalBarrelScFi + EcalBarrelImaging (sub-collections), EcalBarrelScFiHits + EcalBarrelImagingHits (readouts), BEMC (flag prefix), system ID 101 (`EcalBarrel_ID`, spelled `ECalBarrel_ID` in the DEPRECATED alias; `EcalBarrel2_ID` = 105).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The ePIC barrel ECal (BIC) is a hybrid: a **scintillating-fiber/Pb (ScFi)**
sampling section that measures energy, and an **AstroPix imaging (silicon
pixel)** section that measures position/shower shape. EICrecon reconstructs
the two independently and then merges them; all of it is registered in one
JANA2 plugin, [`src/detectors/BEMC/BEMC.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc).
The runtime flag prefix is `BEMC:` (309 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

## Chain overview

**ScFi branch — reconstruction path (produces the clusters):**

`EcalBarrelScFiHits` (edm4hep::SimCalorimeterHit, from simulation)
→ **CalorimeterHitDigi** → `EcalBarrelScFiRawHits`
→ **CalorimeterHitReco** → `EcalBarrelScFiRecHits`
→ **CalorimeterIslandCluster** → `EcalBarrelScFiProtoClusters`
→ **CalorimeterClusterRecoCoG** → `EcalBarrelScFiClustersWithoutShapes`
→ **CalorimeterClusterShape** → `EcalBarrelScFiClusters`

*in parallel from the same rec hits:*
`EcalBarrelScFiRecHits` → **ImagingTopoCluster** → `EcalBarrelScFiProtoTopoClusters` → CoG → Shape → `EcalBarrelScFiTopoClusters`

**ScFi branch — realistic waveform/ASIC path (currently a side branch, see caveats):**

`EcalBarrelScFiHits` → **SimCalorimeterHitProcessor** (×2, P and N ends) → `EcalBarrelScFi{P,N}AttenuatedHits`
→ **EdepToNpeConversion** → `EcalBarrelScFi{P,N}NpeHits`
→ **PulseGeneration** → `EcalBarrelScFi{P,N}Pulses`
→ **PulseCombiner** → `EcalBarrelScFi{P,N}CombinedPulses`
→ **PulseNoise** → `EcalBarrelScFi{P,N}CombinedPulsesWithNoise`
→ **CALOROCDigitization** → `EcalBarrelScFi{P,N}CALOROCHits` *(terminal — no downstream consumer in the plugin)*

**Imaging branch:**

`EcalBarrelImagingHits`
→ **SimCalorimeterHitProcessor** → `EcalBarrelImagingProcessedHits`
→ **CalorimeterHitDigi** → `EcalBarrelImagingRawHits`
→ **CalorimeterHitReco** → `EcalBarrelImagingRecHits`
→ **ImagingTopoCluster** → `EcalBarrelImagingProtoClusters`
→ **ImagingClusterReco** → `EcalBarrelImagingClustersWithoutShapes` (+ `EcalBarrelImagingLayers`)
→ **CalorimeterClusterShape** → `EcalBarrelImagingClusters`

**Merge:**

(`EcalBarrelScFiClusters` energy, `EcalBarrelImagingClusters` position)
→ **EnergyPositionClusterMerger** → **`EcalBarrelClusters`** (after shape pass)
→ **TruthEnergyPositionClusterMerger** → `EcalBarrelTruthClusters` (MC-truth reference merge)

## Stage 1 — ScFi light attenuation & hit regrouping

**Algorithm:** [`SimCalorimeterHitProcessor`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/SimCalorimeterHitProcessor.cc)
— *"Regroup the hits by particle, add up the hits if they have z-segmentation, and attenuate."*
Groups Geant4 contributions by (primary particle, cellID), applies two-exponential
light attenuation toward one readout end, adds propagation time delay.

| parameter | struct default | BEMC ScFi value | meaning |
|---|---|---|---|
| `attenuationParameters` | `{0}` | `{0.416212, 747.39875 mm, 7521.88383 mm}` | `[0]*exp(-|z_ref-z|/[1]) + (1-[0])*exp(-|z_ref-z|/[2])` |
| `readout` | `""` | `"EcalBarrelScFiHits"` | readout used to decode cellIDs |
| `attenuationReferencePositionName` | `""` | `"EcalBarrel_LightGuide_{Positive,Negative}PosZ"` | DD4hep geometry constant giving `z_ref` |
| `hitMergeFields` | `{}` | `{"fiber", "z"}` | fields for merging hits |
| `contributionMergeFields` | `{}` | `{"fiber"}` | fields for merging contributions |
| `inversePropagationSpeed` | `0` | `(1/160) ns/mm` | inverse propagation speed (inverse avoids div-by-zero) |
| `fixedTimeDelay` | `0` | `2 ns` | detector-related time delay (e.g. scintillation) |
| `timeWindow` | `100 ns` | `100 ns` | time window for grouping contributions |

The Imaging instance sets only `readout` + `timeWindow`; with an empty
reference-position name the attenuation factor is fixed to 1
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/SimCalorimeterHitProcessor.cc#L173-L182)).

## Stage 2 — ScFi photostatistics (edep → N photoelectrons)

**Algorithm:** [`EdepToNpeConversion`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EdepToNpeConversion.cc)
— converts deposited energy into photoelectron counts via a constant factor or a
cellID-field-keyed lookup table.

| parameter | default | BEMC ScFi value | meaning |
|---|---|---|---|
| `readout` | `""` | `"EcalBarrelScFiHits"` | readout whose idSpec supplies LUT key fields |
| `edep_to_npe_fields` | `{}` | `{"layer"}` | fields the conversion factor depends on |
| `edep_to_npe_filename` | `""` | `"calibrations/bic_edepToNpe_layer.lut"` | lookup table path |
| `edep_to_npe` | `0` | not set | constant factor; non-zero takes precedence over the LUT |

{: .note }
The LUT `calibrations/bic_edepToNpe_layer.lut` is **not in the EICrecon
repository** — it is resolved at runtime (see caveats at the bottom).

## Stage 3 — ScFi waveform simulation and CALOROC digitization

Side branch producing `edm4eic::RawCALOROCHit`; nothing in the plugin
consumes its output yet.

- [`PulseGeneration`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.h): hit → sampled analog waveform. BEMC: `pulse_shape_function="LandauPulse"`, `pulse_shape_params={55.37, 10 ns}`, `ignore_thres=1`, `timestep=0.5 ns`.
- [`PulseCombiner`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseCombiner.h): merges pulses per channel. BEMC: `minimum_separation=100 ns`, `combine_field="grid"`.
- [`PulseNoise`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseNoise.h): multi-pole correlated noise + pedestal. BEMC: `poles=2`, `variance=0.5`, `alpha=0`, `scale=5.4e-5`, `pedestal=1.6e-4`.
- [`CALOROCDigitization`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CALOROCDigitization.h): samples the waveform into ADC/TOA/TOT words. BEMC: `adc_phase=10 ns`, `toa_thres=7`, `tot_thres=200`, `dyRangeSingleGainADC=250`, `dyRangeHighGainADC=250`, `dyRangeLowGainADC=2500`.

## Stage 4 — Digitization (path that feeds reconstruction)

**Algorithm:** [`CalorimeterHitDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc)
— smears energy with `a/√(E/GeV) + b + c/E`, digitizes with dynamic ADC range +
pedestal, converts time with smearing.

| parameter | ScFi | Imaging | meaning |
|---|---|---|---|
| `eRes` | `{0, 0, 0}` | `{0, 0.02, 0}` | resolution coefficients a, b, c |
| `capADC` | `16384` (14-bit) | `8192` (13-bit) | ADC counts at full scale |
| `dyRangeADC` | `1500 MeV` | `3 MeV` | energy at full ADC scale |
| `pedMeanADC` | `100` | `14` | pedestal mean (imaging comment: "noise floor at 5 keV: 8192/3×0.005") |
| `pedSigmaADC` | `1` | `5` | pedestal noise sigma |
| `resolutionTDC` | `10 ps` | `3.25 ns` | TDC least count |
| `readout` | `"EcalBarrelScFiHits"` | `"EcalBarrelImagingHits"` | readout name |
| `fields` | `{"fiber", "z"}` | `{}` | cellID fields over which signals are summed |

## Stage 5 — Hit reconstruction (ADC → calibrated hit)

**Algorithm:** [`CalorimeterHitReco`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc)
— zero suppression, `energy = (ADC − pedMeanADC)/capADC × dyRangeADC / sampFrac`,
TDC → time, attaches global + local positions from the DD4hep cellID.

| parameter | ScFi | Imaging | meaning |
|---|---|---|---|
| `capADC` / `dyRangeADC` / `pedMeanADC` | `16384` / `1500 MeV` / `100` | `8192` / `3 MeV` / `14` | must match digi values |
| `thresholdFactor` | `0.0` | `0.0` | multiplies `pedSigmaADC`; exactly one of factor/value must be non-zero |
| `thresholdValue` | `5.0` ("16384 ADC/1500 MeV × 0.5 MeV = 5.46") | `41` ("8192 ADC/3 MeV × 0.015 MeV = 41") | absolute ADC zero-suppression threshold |
| `sampFrac` | `"0.09285755"` | `"0.00429453"` | sampling fraction — a **string expression** compiled per hit with all cellID fields in scope |
| `layerField` / `sectorField` | `"layer"` / `"sector"` | `"layer"` / `"sector"` | cellID fields |
| `maskPos` | `"xy"` | — | use grid-center XY but keep fiber-segment z ("TODO: reconstruct z from timing") |
| `maskPosFields` | `{"fiber", "z"}` | — | cellID fields masked off for the masked position |

Runtime flags: `BEMC:EcalBarrelScFiRecHits:samplingFraction`,
`:thresholdValue`, `:capacityADC`, `:dynamicRangeADC`, `:pedestalMean`, … —
note the **flag names differ from the config field names**
(`capADC` → `capacityADC`, `sampFrac` → `samplingFraction`).

## Stage 6a — ScFi proto-clustering: island clustering

**Algorithm:** [`CalorimeterIslandCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc)
— groups adjacent rec hits into proto-clusters by a distance/adjacency
criterion, optionally splitting at local energy maxima.

| parameter | BEMC ScFi | meaning |
|---|---|---|
| `localDistXZ` | `{80 mm, 80 mm}` | the active neighbour criterion for ScFi |
| `sectorDist` | `50 mm` | max global distance across sectors |
| `splitCluster` | `false` | split at local maxima |
| `minClusterHitEdep` | `5.0 MeV` | min hit energy to enter clustering |
| `minClusterCenterEdep` | `100.0 MeV` | min seed-hit energy |

## Stage 6b — Topological proto-clustering (Imaging + ScFi-topo variant)

**Algorithm:** [`ImagingTopoCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc)
— *"Topological Cell Clustering Algorithm for Imaging Calorimetry"*
(reference: [arXiv:1603.02934](https://arxiv.org/pdf/1603.02934.pdf)).

| parameter | Imaging | ScFi topo | meaning |
|---|---|---|---|
| `neighbourLayersRange` | `2` | `2` | max layer-number difference for neighbours |
| `sameLayerMode` | `tz` | `xyz` | how same-layer neighbours are determined |
| `sameLayerDistTZ` | `{2 mm, 2 mm}` | — | same-layer distance (t, z) |
| `sameLayerDistXYZ` | — | `{80, 80, 40} mm` | same-layer distance (x, y, z) |
| `diffLayerMode` | `etaphi` | `xyz` | cross-layer mode |
| `diffLayerDistEtaPhi` | `{10 mrad, 10 mrad}` | — | cross-layer distance (η, φ) |
| `diffLayerDistXYZ` | — | `{80, 80, 40} mm` | cross-layer distance (x, y, z) |
| `sectorDist` | `3.0 cm` | `5.0 cm` | cross-sector distance |
| `minClusterEdep` | `100 MeV` | `100 MeV` | min cluster energy to save |
| `minClusterNhits` | `10` | `10` | min hits to save |

## Stage 7 — Cluster reconstruction

- **ScFi:** [`CalorimeterClusterRecoCoG`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc)
  — centre-of-gravity position/energy. BEMC: `energyWeight="log"`,
  `logWeightBase=6.2`, `sampFrac=1.0` (already applied at hit level).
  The log weight is `max(0, w0 + ln(E_hit/E_tot))`.
- **Imaging:** [`ImagingClusterReco`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingClusterReco.cc)
  — layer-resolved cluster + per-layer centroids + a fitted shower direction.
  BEMC: `trackStopLayer=6`. Also emits `EcalBarrelImagingLayers`.
- **Both, afterwards:** [`CalorimeterClusterShape`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc)
  computes shape parameters and re-emits the clusters — which is why every
  cluster collection has a `…WithoutShapes` twin. BEMC: `energyWeight="log"`,
  `logWeightBase=6.2`; `longitudinalShowerInfoAvailable=true` everywhere
  except the Imaging instance.

## Stage 8 — Merging ScFi and Imaging clusters

**[`EnergyPositionClusterMerger`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EnergyPositionClusterMerger.cc)**
— *"merge the energy measurement from cluster1 with the position measurement
of cluster2 (in case matching clusters are found). If not, it will propagate
the raw cluster."* Matching on φ/η/E; negative tolerance disables a check;
closest cluster wins ambiguities.

| parameter | value | meaning |
|---|---|---|
| `energyRelTolerance` | `0.5` | relative energy matching tolerance |
| `phiTolerance` | `0.1` | φ tolerance (rad) |
| `etaTolerance` | `0.2` | η tolerance |

Inputs: `EcalBarrelScFiClusters` (energy) + `EcalBarrelImagingClusters`
(position) → **`EcalBarrelClusters`** (after the shape pass).
[`TruthEnergyPositionClusterMerger`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TruthEnergyPositionClusterMerger.cc)
does the same using MC-truth matching → `EcalBarrelTruthClusters` (no config).

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L359-L389)):
`EcalBarrelClusters(+Links/Associations)`, `EcalBarrelTruthClusters(+…)`,
`EcalBarrelImaging{ProcessedHits,RawHits,RecHits,Clusters}(+…)`,
`EcalBarrelScFi{P,N}{AttenuatedHits,NpeHits,CALOROCHits}`,
`EcalBarrelScFi{RawHits,RecHits,Clusters,TopoClusters}(+…)`.

**Transient** unless requested: all `…ProtoClusters`, all `…WithoutShapes`,
`EcalBarrelImagingLayers`, the pulse collections.

Downstream ([`src/global/reco/reco.cc`](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L82-L89)):
the barrel contribution to the combined `EcalClusters` is
**`EcalBarrelScFiClusters`**, *not* the merged `EcalBarrelClusters`;
`EcalBarrelClusters` + track projections → `EcalBarrelTrackClusterMatches`,
which particle flow consumes.

## Caveats / needs human verification

1. `calibrations/bic_edepToNpe_layer.lut` is not in the EICrecon repo; the
   algorithm throws if the file can't be opened. Its provenance (geometry
   package? working dir?) is not determinable from EICrecon source.
2. The geometry constants (`EcalBarrel_LightGuide_*PosZ`) and all cellID
   field names live in the **`epic` geometry description**, not EICrecon.
3. The sampling fractions `0.09285755` / `0.00429453` are hard-coded with no
   provenance comment (which geometry version / calibration sample?).
4. The positive-end CALOROC digitizer consumes `…PCombinedPulsesWithNoise`
   but the negative-end one consumes `…NCombinedPulses` (**without** noise)
   — possibly unintentional; needs a maintainer's confirmation.
5. The waveform/CALOROC branch is a dead end today: `EcalBarrelScFiRawHits`
   is digitized directly from the unprocessed sim hits, and nothing consumes
   the CALOROC hits. Transitional state, intent unknown.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
