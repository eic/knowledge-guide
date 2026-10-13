---
title: B0 ECal (B0ECAL)
parent: EICrecon
nav_order: 8
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC B0 Electromagnetic Calorimeter (B0ECAL) Reconstruction

*Also known as: B0 ECal, B0 electromagnetic calorimeter, B0 preshower calorimeter, far-forward B0 calorimeter, B0ECal (collection prefix), B0ECalHits (readout), B0ECAL (flag prefix), system ID 169 (`B0ECal_ID`); sits with the B0 tracker (`B0TRK`) inside the B0pf dipole.*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The B0 ECal (`B0ECal`) sits inside the B0 dipole in the far-forward region.
Its reconstruction is the **simplest of all ePIC calorimeters**: digitize,
reconstruct hits, cluster (truth + island), centre of gravity, shapes. No hit
merging, no sub-cell splitting, no track-driven merging, no ML. Everything is
registered in
[`src/detectors/B0ECAL/B0ECAL.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc).
The runtime flag prefix is `B0ECAL:` (88 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

A sampling fraction of `0.998` and a purely stochastic resolution term derived
from PbWO₄ light yield make it effectively a homogeneous crystal calorimeter
in the reconstruction's view.

## Chain overview

`B0ECalHits` (edm4hep::SimCalorimeterHit) + `EventHeader`
→ **CalorimeterHitDigi** → `B0ECalRawHits` (+ `B0ECalRawHitLinks`, `B0ECalRawHitAssociations`)
→ **CalorimeterHitReco** → `B0ECalRecHits`

**Truth branch:**

(`B0ECalRecHits`, `B0ECalRawHitLinks`)
→ **CalorimeterTruthClustering** → `B0ECalTruthProtoClusters`
→ **CalorimeterClusterRecoCoG** → `B0ECalTruthClustersWithoutShapes`
→ **CalorimeterClusterShape** → `B0ECalTruthClusters`

**Reconstruction branch:**

`B0ECalRecHits`
→ **CalorimeterIslandCluster** → `B0ECalIslandProtoClusters`
→ **CalorimeterClusterRecoCoG** → `B0ECalClustersWithoutShapes`
→ **CalorimeterClusterShape** → **`B0ECalClusters`**

## Stage 1 — Digitization

**Algorithm:** [`CalorimeterHitDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc)
— explained on the [BEMC page]({% link docs/eicrecon/detectors/bemc.md %}).
`readoutType` is left at the default `"simple"`, so the ADC is the plain
linear conversion `ADC = ped + edep × corrMeanScale / dyRangeADC × capADC`.

| parameter | struct default | B0ECAL value | meaning |
|---|---|---|---|
| `eRes` | — | `{0.0326·√GeV, 0.00, 0}` | stochastic-only resolution. Verbatim: *"The stochastic term is set using light yield in PbOW4 of N_photons = 145.75 / GeV / mm, for 6x6 mm2 sensors with PDE=0.18 (a=1/sqrt(145.75\*36\*0.18))"* |
| `tRes` | — | `0 ns` | no time smearing |
| `threshold` | `1 keV` | `5.0 MeV` | the **only** ePIC calorimeter with a non-zero value here — but see caveat 1 |
| `capADC` | `1` | `16384` | ADC counts at full scale (14-bit) |
| `dyRangeADC` | `1` | `170 GeV` | energy at full ADC scale — the largest of any ePIC calorimeter |
| `pedMeanADC` / `pedSigmaADC` | `0` / `0` | `100` / `1` | pedestal mean and noise sigma |
| `resolutionTDC` | `1` | `1e-11` (= 10 ps) | TDC least count, written as a bare number rather than with DD4hep units |
| `corrMeanScale` | `"1.0"` | `"1.0"` | per-hit correction expression |
| `readout` | `""` | `"B0ECalHits"` | readout used to decode cellIDs |
| `capTime` | `1000 ns` | not set → `1000 ns` | time dynamic range (only logged) |

## Stage 2 — Hit reconstruction

**Algorithm:** [`CalorimeterHitReco`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc)
— as on the BEMC page.

| parameter | B0ECAL value | meaning |
|---|---|---|
| `capADC` / `dyRangeADC` / `pedMeanADC` / `pedSigmaADC` / `resolutionTDC` | `16384` / `170 GeV` / `100` / `1` / `10 ps` | must match the digi values |
| `thresholdFactor` | `0.0` | multiplier on `pedSigmaADC`; unused |
| `thresholdValue` | `1.0` | *"using threshold of 10 photons = 10 MeV = 1 ADC"* — pedestal-subtracted ADC cut |
| `sampFrac` | `"0.998"` | sampling fraction, compiled per hit with all cellID fields in scope |
| `readout` | `"B0ECalHits"` | readout name |
| `layerField` | not set | rec hits carry layer 0 |
| `sectorField` | `"sector"` | cellID field giving the sector index |

## Stage 3 — Truth proto-clustering

**Algorithm:** [`CalorimeterTruthClustering`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc)
(no configuration) — one proto-cluster per contributing MC primary, hits
shared rather than partitioned. Described on the
[EEMC page]({% link docs/eicrecon/detectors/eemc.md %}).

## Stage 4 — Island proto-clustering

**Algorithm:** [`CalorimeterIslandCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc)
— see the BEMC page. Like FEMC, B0ECAL uses the **dimension-scaled local XY**
criterion, where the neighbour window is expressed in units of the hit's own
cell dimensions.

| parameter | B0ECAL value | meaning |
|---|---|---|
| `adjacencyMatrix` / `peakNeighbourhoodMatrix` / `readout` | empty | cellID-expression adjacency disabled |
| `sectorDist` | `5.0 cm` | max global distance across sectors |
| `dimScaledLocalDistXY` | `{1.8, 1.8}` | neighbour window in units of the cell's own x/y dimension |
| `localDistXY` / `localDistXZ` / `localDistYZ` / `globalDistRPhi` / `globalDistEtaPhi` | empty | other metrics disabled |
| `splitCluster` | `false` | **no** splitting at local maxima |
| `minClusterHitEdep` | `1.0 MeV` | min hit energy to enter clustering |
| `minClusterCenterEdep` | `30.0 MeV` | min seed-hit energy |
| `transverseEnergyProfileMetric` | `"globalDistEtaPhi"` | metric for the splitting profile |
| `transverseEnergyProfileScale` | `1.0` | profile scale |
| `transverseEnergyProfileScaleUnits` | empty | (undocumented) |

## Stage 5 — Cluster reconstruction and shapes

[`CalorimeterClusterRecoCoG`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc)
+ [`CalorimeterClusterShape`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc),
both explained on the BEMC page.

| instance | `energyWeight` | `sampFrac` | `logWeightBase` | `enableEtaBounds` |
|---|---|---|---|---|
| `B0ECalClustersWithoutShapes` | `log` | `1.0` | `3.6` | `false` |
| `B0ECalClusters` (shape) | `log` | — | `3.6` | — |
| `B0ECalTruthClustersWithoutShapes` | `log` | `1.0` | `6.2` | `false` |
| `B0ECalTruthClusters` (shape) | `log` | — | `6.2` | — |

`sampFrac = 1.0` at cluster level because the 0.998 fraction is already
applied at `CalorimeterHitReco`. `longitudinalShowerInfoAvailable` is never
set, so it stays `false` and no intrinsic θ/φ are computed.

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L430-L434)):
`B0ECalRawHits`, `B0ECalRecHits`, `B0ECalClusters`, `B0ECalClusterLinks`,
`B0ECalClusterAssociations`, plus `ReconstructedB0EcalNeutrals`
([L466](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L466)).

**Not persisted by default:** `B0ECalTruthClusters` (and its links /
associations), `B0ECalTruthProtoClusters`, `B0ECalIslandProtoClusters`, both
`…WithoutShapes` collections.

Downstream: `B0ECalClusters` is the second input to
`FarForwardNeutralsReconstruction`
([reco.cc](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L242-L250))
→ `ReconstructedB0EcalNeutrals`. B0 ECal clusters do **not** enter the
combined `EcalClusters` collection (which takes only `EcalEndcapNClusters`,
`EcalBarrelScFiClusters` and `EcalEndcapPClusters`).

## Caveats / needs human verification

1. **`threshold = 5.0 MeV` does not suppress anything.** In
   `CalorimeterHitDigi`, `threshold` appears exactly once — as the condition
   deciding whether energy-resolution smearing is applied
   ([line 215](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L213-L219)).
   Hits below it are digitized normally, just without stochastic smearing.
   Since B0ECAL is the only calorimeter with a large non-zero value here, the
   practical effect is that deposits below 5 MeV get **no** stochastic
   resolution term. Whether that is intended needs confirmation.
2. **`B0ECalTruthClusters` is computed but never written.** The truth branch
   runs on every event, but the collection is absent from the PODIO output
   list — unlike EEMC/FEMC/EHCAL/BHCAL/ZDC, whose truth clusters are
   persisted.
3. `resolutionTDC = 1e-11` is written as a raw double instead of
   `10 * dd4hep::picosecond` as everywhere else. Numerically identical
   (DD4hep time unit is ns), but it bypasses the unit system and would break
   silently if the unit convention changed.
4. The `eRes` comment misspells the crystal as *"PbOW4"* (PbWO₄) and cites
   sensor parameters (6×6 mm², PDE 0.18) without a reference for the light
   yield 145.75 photons/GeV/mm. The derived constant
   `a = 1/√(145.75 × 36 × 0.18)` = 0.0326 is reproducible from the stated
   numbers, but the numbers themselves have no provenance.
5. `sampFrac = "0.998"` and `dyRangeADC = 170 GeV` are hard-coded with no
   provenance comment (which geometry version, which beam energy assumption?).
6. `thresholdValue = 1.0` is one ADC count, i.e. right at the quantization
   limit with `pedSigmaADC = 1`. Whether the noise is really below one count
   is not shown anywhere.
7. `sector` and all other cellID field names live in the **`epic` geometry
   description**, not in EICrecon.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
