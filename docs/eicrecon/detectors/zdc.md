---
title: Zero-Degree Calorimeter (ZDC)
parent: EICrecon
nav_order: 7
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Far-Forward Zero-Degree Calorimeter (ZDC) Reconstruction

*Also known as: ZDC, zero-degree calorimeter, far-forward ZDC, ZDC ECal (crystal/LYSO section) + ZDC HCal (SiPM-on-tile section); EcalFarForwardZDC + HcalFarForwardZDC (collection prefixes), EcalFarForwardZDCHits + HcalFarForwardZDCHits (readouts), ZDC (flag prefix), system IDs 163–167 (`ZDC_1stSilicon_ID` 163, `ZDC_Crystal_ID` 164, `ZDC_WSi_ID` 165, `ZDC_PbSi_ID` 166, `ZDC_PbSci_ID` = `HcalFarForwardZDC_SiPMonTile_ID` 167).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The `ZDC` plugin registers **two detectors** in one file
([`src/detectors/ZDC/ZDC.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc)):

- **`EcalFarForwardZDC`** — the crystal (LYSO) electromagnetic section,
  reconstructed with a conventional digi → reco → island → CoG chain and a
  sampling fraction of 1.0 (i.e. homogeneous);
- **`HcalFarForwardZDC`** — the SiPM-on-tile hadronic section, reconstructed
  through **HEXPLIT** sub-cell splitting + topological clustering, with an
  **energy-dependent log weight**, plus a parallel *baseline* island chain
  kept for comparison.

The runtime flag prefix is `ZDC:` (232 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

## Chain overview

### ECal section (`EcalFarForwardZDC`)

`EcalFarForwardZDCHits` + `EventHeader`
→ **CalorimeterHitDigi** → `EcalFarForwardZDCRawHits` (+ `…RawHitLinks`, `…RawHitAssociations`)
→ **CalorimeterHitReco** → `EcalFarForwardZDCRecHits`

*truth:* → **CalorimeterTruthClustering** → `…TruthProtoClusters` → **CoG** → `…TruthClustersWithoutShapes` → **Shape** → `EcalFarForwardZDCTruthClusters`

*reco:* → **CalorimeterIslandCluster** → `…IslandProtoClusters` → **CoG** → `…ClustersWithoutShapes` → **Shape** → **`EcalFarForwardZDCClusters`**

### HCal section (`HcalFarForwardZDC`)

`HcalFarForwardZDCHits` + `EventHeader`
→ **CalorimeterHitDigi** → `HcalFarForwardZDCRawHits` (+ links/associations)
→ **CalorimeterHitReco** → `HcalFarForwardZDCRecHits`
→ **HEXPLIT** (`stag_type = S2`) → `HcalFarForwardZDCSubcellHits`

*production:* `…SubcellHits` → **ImagingTopoCluster** → `…ImagingProtoClusters`
→ **CoG** (energy-dependent log weight) → `…ClustersWithoutShapes`
→ **Shape** → **`HcalFarForwardZDCClusters`**

*baseline (no HEXPLIT):* `…RecHits` → **CalorimeterIslandCluster** → `…IslandProtoClustersBaseline`
→ **CoG** → `…ClustersBaselineWithoutShapes` → **Shape** → `HcalFarForwardZDCClustersBaseline`

*truth:* (`…RecHits`, `…RawHitLinks`) → **CalorimeterTruthClustering** → `…TruthProtoClusters`
→ **CoG** → `…TruthClustersWithoutShapes` → **Shape** → `HcalFarForwardZDCTruthClusters`

*orphan:* `…SubcellHits` → **CalorimeterIslandCluster** → `HcalFarForwardZDCIslandProtoClusters` *(terminal — nothing consumes it, see caveat 1)*

Neither section registers a `TrackClusterMergeSplitter` — there are no tracks
at zero degrees.

## Stage 1 — Digitization

**Algorithm:** [`CalorimeterHitDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc)
— explained on the [BEMC page]({{ site.baseurl }}{% link docs/eicrecon/detectors/bemc.md %}).
Both instances leave `readoutType` at the default `"simple"`.

| parameter | ECal (LYSO) | HCal (SiPM-on-tile) | meaning |
|---|---|---|---|
| `eRes` | `{}` | `{}` | no energy-resolution smearing |
| `tRes` | `0 ns` | `0 ns` | no time smearing |
| `capADC` | `32768` | `65536` | ADC counts at full scale |
| `dyRangeADC` | `2000 MeV` | `1000 MeV` | energy at full ADC scale |
| `pedMeanADC` / `pedSigmaADC` | `400` / `3.2` | `400` / `2` | pedestal mean and noise sigma |
| `resolutionTDC` | `10 ps` | `10 ps` | TDC least count |
| `corrMeanScale` | `"1.0"` | `"1.0"` | per-hit correction expression |
| `readout` | `"EcalFarForwardZDCHits"` | `"HcalFarForwardZDCHits"` | readout name |
| `capTime` | not set → `1000 ns` | not set → `1000 ns` | time dynamic range (only logged) |

## Stage 2 — Hit reconstruction

**Algorithm:** [`CalorimeterHitReco`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc)
— as on the BEMC page. The ZDC is the **only** ePIC calorimeter that uses the
*relative* zero-suppression threshold (`thresholdFactor` × `pedSigmaADC`)
instead of a flat ADC value.

| parameter | ECal | HCal | meaning |
|---|---|---|---|
| `capADC` / `dyRangeADC` / `pedMeanADC` / `pedSigmaADC` / `resolutionTDC` | `32768` / `2000 MeV` / `400` / `3.2` / `10 ps` | `65536` / `1000 MeV` / `400` / `2` / `10 ps` | must match the digi values |
| `thresholdFactor` | `4.0` | `3.0` | multiplies `pedSigmaADC` → cut at 12.8 ADC (ECal) / 6 ADC (HCal) |
| `thresholdValue` | `0.0` | `0.0` | flat ADC cut disabled (exactly one of the two must be non-zero) |
| `sampFrac` | `"1.0"` | `"1.0"` | sampling fraction not applied here |
| `readout` | `"EcalFarForwardZDCHits"` | `"HcalFarForwardZDCHits"` | readout name |
| `layerField` | not set | `"layer"` | cellID field giving the layer index |
| `sectorField` | not set | `"system"` | cellID field used as the sector index |

## Stage 3 — HCal: HEXPLIT sub-cell splitting

**Algorithm:** [`HEXPLIT`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc)
— *"An algorithm for splitting calorimeter hits in overlapping cells into
'subhits' based on the relative energies of hits on neighboring layers"*.
The full procedure is described on the
[FHCAL page]({{ site.baseurl }}{% link docs/eicrecon/detectors/fhcal.md %}).
The ZDC HCal is the only user of the **`S2` square 2-fold staggering
pattern**: 4 sub-cells per cell, each weighted by a *single* neighbour energy
(the H4 hexagonal pattern used by the FHCAL insert has 12 sub-cells weighted
by products of 3).

| parameter | struct default | ZDC HCal value | meaning |
|---|---|---|---|
| `MIP` | `472 keV` | `630 keV` | energy deposit of a minimum-ionizing particle in one cell |
| `Emin_in_MIPs` | `0.1` | `0.5` | minimum hit energy to be used, in MIPs |
| `delta_in_MIPs` | `0.01` | `0.01` (explicit) | floor applied to neighbour energies, in MIPs |
| `tmax` | `325 ns` | `269 ns` | maximum hit time |
| `stag_type` | `H4` | `S2` | square, 2-fold staggering — 4 subcells, 4 neighbour positions, overlap 1 |

## Stage 4a — HCal: topological proto-clustering (production path)

**Algorithm:** [`ImagingTopoCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc)
— as on the BEMC page, run on the HEXPLIT sub-cell hits in **xy mode**.

| parameter | struct default | ZDC HCal value | meaning |
|---|---|---|---|
| `neighbourLayersRange` | `1` | `1` | max layer-number difference for neighbours |
| `sameLayerMode` / `diffLayerMode` | `xy` / `xy` | `xy` / `xy` (both explicit) | neighbour determination mode |
| `sameLayerDistXY` | `{1 mm, 1 mm}` | `{36.6 mm, 36.6 mm}` (= `side_length × 0.75`, `side_length = 48.8 mm`) | same-layer (x, y) neighbour window |
| `diffLayerDistXY` | `{1 mm, 1 mm}` | `{36.6 mm, 36.6 mm}` | cross-layer (x, y) neighbour window |
| `sectorDist` | `1.0 cm` | `10.0 cm` | max global distance across sectors |
| `minClusterHitEdep` | `0` | `315.0 keV` | *"minimum hit energy to participate clustering"* (= 0.5 MIP) |
| `minClusterCenterEdep` | `0` | `25 MeV` | *"minimum cluster center energy (to be considered as a seed for cluster)"* |
| `minClusterEdep` | `0.5 MeV` | `50.0 MeV` | *"minimum cluster energy (to save this cluster)"* |
| `minClusterNhits` | `10` | `10` | *"minimum number of hits (to save this cluster)"* |

## Stage 4b — Island proto-clustering (ECal, HCal baseline, HCal orphan)

**Algorithm:** [`CalorimeterIslandCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc)
— see the BEMC page. Three instances:

| parameter | ECal | HCal *baseline* (from `RecHits`) | HCal *orphan* (from `SubcellHits`) |
|---|---|---|---|
| `sectorDist` | `5.0 cm` | `5.0 cm` | `1.5 cm` |
| `localDistXY` | `{50 cm, 50 cm}` | `{50 cm, 50 cm}` | `{"0.55 * HcalFarForwardZDC_SiPMonTile_SquareSideLength", …}` (string expression) |
| `splitCluster` | `true` | `true` | `false` |
| `minClusterHitEdep` | `0.1 MeV` | `0.1 MeV` | `100.0 keV` |
| `minClusterCenterEdep` | `3.0 MeV` | `3.0 MeV` | `1.0 MeV` |
| `transverseEnergyProfileMetric` | `"globalDistEtaPhi"` | `"globalDistEtaPhi"` | empty — commented out in place: `// = "globalDistEtaPhi"` |
| `transverseEnergyProfileScale` | `1.0` | `1.0` | empty — `// = 1.` |
| `adjacencyMatrix` / `peakNeighbourhoodMatrix` / `readout` | empty | empty | empty |

The baseline branch exists specifically as a HEXPLIT-free reference; the
plugin labels it *"Clusters with the baseline algorithm (no HEXPLIT)"*.

## Stage 5 — Truth proto-clustering

**Algorithm:** [`CalorimeterTruthClustering`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc)
(no configuration) — described on the
[EEMC page]({{ site.baseurl }}{% link docs/eicrecon/detectors/eemc.md %}).
Both sections run it on their **rec** hits.

## Stage 6 — Cluster reconstruction and shapes

[`CalorimeterClusterRecoCoG`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc)
+ [`CalorimeterClusterShape`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc),
both explained on the BEMC page. The production HCal path uses the
**energy-dependent log weight**, which no other ePIC calorimeter enables:

> *optional: have the log weight base depend on the energy —
> `logWeightBaseCoeffs[0] + logWeightBaseCoeffs[1]*l + logWeightBaseCoeffs[2]*l*l + …`
> where `l = log(cl.getEnergy()/logWeightBase_Eref)`. If this is empty, use
> the logWeightBase parameter for backwards compatibility.*
> ([config struct](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoGConfig.h#L19-L24))

| instance | `energyWeight` | `sampFrac` | log weight | `enableEtaBounds` | `longitudinalShowerInfoAvailable` |
|---|---|---|---|---|---|
| `EcalFarForwardZDCTruthClustersWithoutShapes` | `log` | `1.0` | base `3.6` | `false` | — |
| `EcalFarForwardZDCTruthClusters` (shape) | `log` | — | base `3.6` | — | `true` |
| `EcalFarForwardZDCClustersWithoutShapes` | `log` | `1.0` | base `6.2` | `false` | — |
| `EcalFarForwardZDCClusters` (shape) | `log` | — | base `6.2` | — | `true` |
| `HcalFarForwardZDCClustersWithoutShapes` | `log` | `0.0273` | coeffs `{5.8, 0.65, 0.31}`, `Eref = 50 GeV` | not set → `false` | — |
| `HcalFarForwardZDCClusters` (shape) | `log` | `0.0273` | coeffs `{5.8, 0.65, 0.31}`, `Eref = 50 GeV` | — | `true` |
| `HcalFarForwardZDCTruthClustersWithoutShapes` | `log` | `1.0` | base `3.6` | `false` | — |
| `HcalFarForwardZDCTruthClusters` (shape) | `log` | — | base `3.6` | — | `true` |
| `HcalFarForwardZDCClustersBaselineWithoutShapes` | `log` | `0.0273` | base `6.2` | `false` | — |
| `HcalFarForwardZDCClustersBaseline` (shape) | `log` | `0.0273` | base `6.2` | — | `true` |

Note that `logWeightBase_Eref` defaults to **50 MeV** in the config struct but
is set to **50 GeV** here — a factor 1000 — so the polynomial is evaluated
around a hadronic-shower scale.

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L442-L465)):
`EcalFarForwardZDCRawHits`, `EcalFarForwardZDCRecHits`,
`EcalFarForwardZDCClusters(+Links/Associations)`,
`EcalFarForwardZDCTruthClusters(+Links/Associations)`,
`HcalFarForwardZDCRawHits`, `HcalFarForwardZDCRecHits`,
**`HcalFarForwardZDCSubcellHits`**,
`HcalFarForwardZDCClusters(+Links/Associations)`,
`HcalFarForwardZDCClustersBaseline(+Links/Associations)`,
`HcalFarForwardZDCTruthClusters(+Links/Associations)`, and
`ReconstructedHcalFarForwardZDCNeutrals`.

**Transient** unless requested: all proto-cluster collections (including the
orphan `HcalFarForwardZDCIslandProtoClusters`) and all `…WithoutShapes`
collections.

Downstream: `HcalFarForwardZDCClusters` is the first input to
`FarForwardNeutralsReconstruction`
([reco.cc](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L242-L250)),
which applies the ZDC-specific corrections
`neutronScaleCorrCoeffHcalZDC = {2.4, 0.89}` and
`gammaScaleCorrCoeffHcalZDC = {1.1, 0.98}` and produces
`ReconstructedHcalFarForwardZDCNeutrals`. The ZDC ECal clusters are **not**
consumed by any factory in `reco.cc`.

## Caveats / needs human verification

1. **`HcalFarForwardZDCIslandProtoClusters` is a dead end.** It is registered
   on the HEXPLIT sub-cell hits with its own tuned parameters
   ([source](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L208-L228)),
   but no cluster factory in the plugin takes it as input — the production
   path uses `…ImagingProtoClusters` and the baseline path uses
   `…IslandProtoClustersBaseline`. Two of its parameters are also
   *commented out in place* (`// = "globalDistEtaPhi"`, `// = 1.`),
   suggesting work in progress.
2. **Two different sources for the same cell size.** `ImagingTopoCluster`
   uses a hard-coded `side_length = 48.8 mm` local variable, while the orphan
   island clusteriser reads the DD4hep constant
   `HcalFarForwardZDC_SiPMonTile_SquareSideLength` as a string expression. If
   the geometry changes, one follows and one does not.
3. **The ZDC ECal clusters have no consumer.** `EcalFarForwardZDCClusters` is
   persisted but not used by any factory in `src/global/reco/reco.cc` —
   `FarForwardNeutralsReconstruction` takes only the HCal ZDC, B0 ECal,
   `EcalEndcapP` and LFHCAL clusters.
4. `sampFrac = 0.0273`, `MIP = 630 keV`, `tmax = 269 ns`, `side_length =
   48.8 mm` and the log-weight coefficients `{5.8, 0.65, 0.31}` are all
   hard-coded with **no provenance comment** — no reference to the study,
   geometry version or fit that produced them.
5. `logWeightBase_Eref = 50 GeV` overrides a struct default of 50 **MeV**.
   Worth checking that the coefficients were fitted with the GeV reference.
6. `HcalFarForwardZDCClustersWithoutShapes` does not set `enableEtaBounds`,
   relying on the struct default `false`, while every other ZDC CoG instance
   sets it explicitly.
7. The HCal `sectorField = "system"` is unusual — `system` normally
   identifies the subdetector, not a sector within it. Its effect on cluster
   sectorisation should be checked against the **`epic`** readout definition.
8. `pedSigmaADC` values (3.2 / 2) directly set the zero-suppression threshold
   here (via `thresholdFactor`), unlike everywhere else in ePIC where a flat
   ADC value is used; changing the assumed noise therefore changes the energy
   threshold.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
