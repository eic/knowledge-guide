---
title: Luminosity Spectrometer ECal (LUMISPECCAL)
parent: EICrecon
nav_order: 9
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Luminosity Spectrometer Electromagnetic Calorimeter (LUMISPECCAL) Reconstruction

*Also known as: LumiSpecCAL, luminosity spectrometer calorimeter, lumi ECal, luminosity monitor calorimeter, far-backward luminosity calorimeter, EcalLumiSpec (collection prefix), EcalLumiSpecHits (readout), LUMISPECCAL (flag prefix), system ID 194 (`LumiSpecCAL_ID`); neighbours in the geometry are `LumiSpecTracker_ID` 193 and `LumiDirectPCAL_ID` 195, neither of which has an EICrecon plugin.*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The luminosity spectrometer ECal (`EcalLumiSpec`) measures the two
bremsstrahlung-photon conversion legs downstream of the interaction region.
Its chain is short — digitize, reconstruct hits, cluster (truth + island),
centre of gravity, shapes — with **no hit merging, no track matching and no
consumer anywhere else in EICrecon**. Everything is registered in
[`src/detectors/LUMISPECCAL/LUMISPECCAL.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc).
The runtime flag prefix is `LUMISPECCAL:` (88 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

## Chain overview

`EcalLumiSpecHits` (edm4hep::SimCalorimeterHit) + `EventHeader`
→ **CalorimeterHitDigi** → `EcalLumiSpecRawHits` (+ `EcalLumiSpecRawHitLinks`, `EcalLumiSpecRawHitAssociations`)
→ **CalorimeterHitReco** → `EcalLumiSpecRecHits`

**Truth branch:**

(`EcalLumiSpecRecHits`, `EcalLumiSpecRawHitLinks`)
→ **CalorimeterTruthClustering** → `EcalLumiSpecTruthProtoClusters`
→ **CalorimeterClusterRecoCoG** → `EcalLumiSpecTruthClustersWithoutShapes`
→ **CalorimeterClusterShape** → `EcalLumiSpecTruthClusters`

**Reconstruction branch:**

`EcalLumiSpecRecHits`
→ **CalorimeterIslandCluster** → `EcalLumiSpecIslandProtoClusters`
→ **CalorimeterClusterRecoCoG** → `EcalLumiSpecClustersWithoutShapes`
→ **CalorimeterClusterShape** → **`EcalLumiSpecClusters`**

## Stage 1 — Digitization

**Algorithm:** [`CalorimeterHitDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc)
— explained on the [BEMC page]({{ site.baseurl }}{% link docs/eicrecon/detectors/bemc.md %}).
`readoutType` is left at the default `"simple"` (linear ADC conversion).

| parameter | struct default | LUMISPECCAL value | meaning |
|---|---|---|---|
| `eRes` | — | `{0·√GeV, 0.02, 0}` | *"flat 2%"* — constant term only, no stochastic or noise term |
| `tRes` | — | `0 ns` | no time smearing |
| `threshold` | `1 keV` | not set → `1 keV` | gates the resolution smearing only (see caveat 3) |
| `capADC` | `1` | `16384` | ADC counts at full scale (14-bit) |
| `dyRangeADC` | `1` | `20 GeV` | energy at full ADC scale |
| `pedMeanADC` / `pedSigmaADC` | `0` / `0` | `100` / `1` | pedestal mean and noise sigma |
| `resolutionTDC` | `1` | `10 ps` | TDC least count |
| `corrMeanScale` | `"1.0"` | `"1.0"` | per-hit correction expression |
| `readout` | `""` | `"EcalLumiSpecHits"` | readout used to decode cellIDs |
| `capTime` | `1000 ns` | not set → `1000 ns` | time dynamic range (only logged) |

## Stage 2 — Hit reconstruction

**Algorithm:** [`CalorimeterHitReco`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc)
— as on the BEMC page.

| parameter | LUMISPECCAL value | meaning |
|---|---|---|
| `capADC` / `dyRangeADC` / `pedMeanADC` / `pedSigmaADC` / `resolutionTDC` | `16384` / `20 GeV` / `100` / `1` / `10 ps` | must match the digi values |
| `thresholdFactor` | `0.0` | multiplier on `pedSigmaADC`; unused |
| `thresholdValue` | `2.0` | absolute pedestal-subtracted ADC cut — ≈ 2.4 MeV at this dynamic range (no explanatory comment in source) |
| `sampFrac` | `"1.0"` | no sampling correction — the detector is treated as homogeneous |
| `readout` | `"EcalLumiSpecHits"` | readout name |
| `layerField` / `sectorField` | not set | rec hits carry layer = sector = 0 |

## Stage 3 — Truth proto-clustering

**Algorithm:** [`CalorimeterTruthClustering`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc)
(no configuration) — one proto-cluster per contributing MC primary, hits
shared rather than partitioned. Described on the
[EEMC page]({{ site.baseurl }}{% link docs/eicrecon/detectors/eemc.md %}).

## Stage 4 — Island proto-clustering

**Algorithm:** [`CalorimeterIslandCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc)
— see the BEMC page. LUMISPECCAL uses a cellID-expression adjacency that
decodes a 2-D module grid out of a **single** `module` field:

```
(sector_1 == sector_2) &&
((abs(floor(module_1 / 10) - floor(module_2 / 10)) +
  abs(fmod(module_1, 10)   - fmod(module_2, 10))) == 1)
```

i.e. `module / 10` is the row and `module % 10` the column, and two hits are
neighbours iff they share an edge in that grid **and** sit in the same sector
(the two spectrometer arms are separate sectors).

| parameter | LUMISPECCAL value | meaning |
|---|---|---|
| `adjacencyMatrix` | expression above | 4-connected module-grid adjacency, same sector only |
| `peakNeighbourhoodMatrix` | empty | (no separate local-maximum neighbourhood defined) |
| `readout` | `"EcalLumiSpecHits"` | readout supplying `sector` / `module` |
| `sectorDist` | `0.0 cm` | no cross-sector neighbours at all |
| `localDistXY` … `dimScaledLocalDistXY` | all empty | metric neighbour criteria disabled |
| `splitCluster` | `true` | split proto-clusters at local energy maxima |
| `minClusterHitEdep` | `1.0 MeV` | min hit energy to enter clustering |
| `minClusterCenterEdep` | `30.0 MeV` | min seed-hit energy |
| `transverseEnergyProfileMetric` | `"localDistXY"` | metric for the splitting energy profile |
| `transverseEnergyProfileScale` | `10 mm` | profile scale (appears as `1` in the flags dump — DD4hep length unit is cm) |
| `transverseEnergyProfileScaleUnits` | empty | (undocumented) |

## Stage 5 — Cluster reconstruction and shapes

[`CalorimeterClusterRecoCoG`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc)
+ [`CalorimeterClusterShape`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc),
both explained on the BEMC page.

| instance | `energyWeight` | `sampFrac` | `logWeightBase` | `enableEtaBounds` |
|---|---|---|---|---|
| `EcalLumiSpecClustersWithoutShapes` | `log` | `1.0` | `3.6` | `false` |
| `EcalLumiSpecClusters` (shape) | `log` | — | `3.6` | — |
| `EcalLumiSpecTruthClustersWithoutShapes` | `log` | `1.0` | `4.6` | `false` |
| `EcalLumiSpecTruthClusters` (shape) | `log` | — | `4.6` | — |

`longitudinalShowerInfoAvailable` is never set, so it stays `false` and no
intrinsic θ/φ are computed.

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L390-L397)):
`EcalLumiSpecRawHits`, `EcalLumiSpecRecHits`,
`EcalLumiSpecTruthClusters(+Links/Associations)`,
`EcalLumiSpecClusters(+Links/Associations)`.

**Transient** unless requested: `EcalLumiSpecTruthProtoClusters`,
`EcalLumiSpecIslandProtoClusters`, both `…WithoutShapes` collections.

**Downstream: nothing.** A repository-wide search for
`EcalLumiSpecClusters` finds it only in `LUMISPECCAL.cc`,
`JEventProcessorPODIO.cc` and CI configuration — no factory in
`src/global/` consumes it. The luminosity analysis is expected to run on the
persisted output.

## Caveats / needs human verification

1. **The adjacency expression hard-codes a 10-column module grid.** The
   `floor(module/10)` / `fmod(module, 10)` decomposition assumes exactly 10
   modules per row in the **`epic` geometry description**. Unlike BHCAL,
   which documents its equivalent magic constant inline (*"320 - number of
   tiles per row"*), this one carries no comment at all. If the segmentation
   changes, clustering silently degrades rather than failing.
2. **No wrap-around and no cross-sector merging**: `sectorDist = 0.0 cm`
   combined with the `sector_1 == sector_2` clause means clusters can never
   span the two spectrometer arms. That is almost certainly intended, but it
   is enforced twice, in two different mechanisms.
3. `threshold` is left at the struct default `1 keV`. In
   `CalorimeterHitDigi` this field only gates whether energy-resolution
   smearing is applied
   ([line 215](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L213-L219));
   it never drops a hit. Zero suppression happens entirely at
   `CalorimeterHitReco` via `thresholdValue = 2.0`.
4. `thresholdValue = 2.0` is the only calorimeter threshold in ePIC with **no
   explanatory comment** — every other plugin shows the arithmetic that
   produced it.
5. `sampFrac = "1.0"` and `eRes = {0, 0.02, 0}` (*"flat 2%"*) assume a
   homogeneous, perfectly-sampled detector with an energy-independent
   resolution. No stochastic term means the simulated resolution does not
   degrade at low energy — worth checking against the physics requirement for
   low-energy bremsstrahlung photons.
6. `dyRangeADC = 20 GeV` is hard-coded with no reference to the expected
   photon energy range.
7. `transverseEnergyProfileMetric = "localDistXY"` is selected while
   `localDistXY` itself is left empty; the profile scale is supplied
   separately as `10 mm`. Worth confirming that the metric works as intended
   without the corresponding distance vector being configured.
8. `sector` and `module` field names live in the **`epic` geometry
   description**, not in EICrecon.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
