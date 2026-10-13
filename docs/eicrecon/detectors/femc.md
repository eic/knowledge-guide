---
title: Forward ECal — FEMC
parent: EICrecon
nav_order: 3
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Forward (Hadron-Going) Endcap Electromagnetic Calorimeter (FEMC) Reconstruction

*Also known as: FEMC, forward ECal, hadron-going endcap ECal, positive-endcap ECal, ion-side endcap ECal, EcalEndcapP (collection prefix), EcalEndcapPHits (readout), FEMC (flag prefix), system ID 102 (`EcalEndcapP_ID`, DEPRECATED spelling `ECalEndcapP_ID`; the geometry also reserves `EcalEndcapPInsert_ID` = 106, which has no EICrecon plugin).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The forward endcap ECal (`EcalEndcapP`, listed under `// Forward` in
[`src/global/reco/reco.cc`](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L205-L208))
is the one calorimeter whose **digitization configuration is chosen at
runtime from the geometry**: the plugin reads the DD4hep constant
`EcalEndcapP_Homogeneous_ScFi` and registers one of two different
`CalorimeterHitDigi` configurations. Everything is registered in
[`src/detectors/FEMC/FEMC.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc).
The runtime flag prefix is `FEMC:` (116 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

## Chain overview

`EcalEndcapPHits` (edm4hep::SimCalorimeterHit) + `EventHeader`
→ **CalorimeterHitDigi** (homogeneous **or** ScFi variant) → `EcalEndcapPRawHits` (+ `…RawHitLinks`, `…RawHitAssociations`)
→ **CalorimeterHitReco** → `EcalEndcapPRecHits`

**Truth branch:**

(`EcalEndcapPRecHits`, `EcalEndcapPRawHitLinks`)
→ **CalorimeterTruthClustering** → `EcalEndcapPTruthProtoClusters`
→ **CalorimeterClusterRecoCoG** → `EcalEndcapPTruthClustersWithoutShapes`
→ **CalorimeterClusterShape** → `EcalEndcapPTruthClusters`

**Reconstruction branch:**

`EcalEndcapPRecHits`
→ **CalorimeterIslandCluster** → `EcalEndcapPIslandProtoClusters`
→ **CalorimeterClusterRecoCoG** → `EcalEndcapPClustersWithoutShapes`
→ **CalorimeterClusterShape** → **`EcalEndcapPClusters`**

**Track-driven split/merge branch:**

(`EcalEndcapPTrackClusterMatches`, `EcalEndcapPClusters`, `CalorimeterTrackProjections`)
→ **TrackClusterMergeSplitter** → `EcalEndcapPSplitMergeProtoClusters` (+ `…TrackSplitMergeProtoClusterLinks`)
→ **CalorimeterClusterRecoCoG** → `EcalEndcapPSplitMergeClustersWithoutShapes`
→ **CalorimeterClusterShape** → `EcalEndcapPSplitMergeClusters`

## Stage 0 — Geometry-dependent branch selection

At plugin init the geometry constant is read
([source](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L55-L67)):

```cpp
EcalEndcapP_homogeneousFlag = detector->constant<int>("EcalEndcapP_Homogeneous_ScFi");
if (EcalEndcapP_homogeneousFlag <= 1) { mLog->info("Homogeneous geometry loaded"); }
else                                  { mLog->info("ScFi geometry loaded"); }
```

If the constant is missing, `catch (...)` sets the flag to `0` —
*"Variable not present apply legacy homogeneous geometry implementation"*.
Only **one** digi factory is registered: the homogeneous one for flag ≤ 1,
the ScFi one for flag == 2. Any other value registers **no digitizer at all**
(see caveat 1).

Shared constants used by both branches
([source](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L41-L53)):

| constant | value | comment in source |
|---|---|---|
| `capADC` | `16384` | *"16384, assuming 14 bits. For approximate HGCROC resolution use 65536"* |
| `dyRangeADC` | `100 GeV` | — |
| `pedMeanADC` | `200` | — |
| `pedSigmaADC` | `2.4576` | — |
| `resolutionTDC` | `10 ps` | — |
| `sampFrac` | `0.029043` | *"updated with ratio to ScFi model"* |
| `corrMeanScale` | `1 / 0.029043` ≈ `34.43` | *"only used for ScFi model"* |
| `nPhotonPerGeV` | `1500` | — |
| `PhotonCollectionEff` | `0.285` | — |
| `totalPixel` | `4 × 159565` = 638,260 | — |

## Stage 1 — Digitization

**Algorithm:** [`CalorimeterHitDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc)
— explained on the [BEMC page]({% link docs/eicrecon/detectors/bemc.md %}).
Both FEMC variants use `readoutType="sipm"`, i.e. the binomial photon
detection + pixel-saturation model
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L246-L260)),
described in more detail on the [EEMC page]({% link docs/eicrecon/detectors/eemc.md %}).

| parameter | homogeneous (flag ≤ 1) | ScFi (flag == 2) | meaning |
|---|---|---|---|
| `eRes` | `{0.11333·√GeV, 0.03, 0}` — *"(11.333% / sqrt(E)) ⊕ 3%"* | `{0, 0.022, 0}` — *"just constant term 2.2% based on MC data comparison"* | resolution coefficients a, b, c |
| `tRes` | `0` | `0` | time smearing |
| `threshold` | `0` — *"15MeV threshold for a single tower will be applied on ADC at Reco below"* | same | see caveat 5 |
| `readoutType` | `"sipm"` | `"sipm"` | SiPM response model |
| `lightYield` | `1500 / 0.285` ≈ 5263/GeV | `1500 / 0.285 / 0.029043` ≈ 181,220/GeV | photons per unit deposited energy |
| `photonDetectionEfficiency` | `0.285` | `0.285` | collection efficiency × QE |
| `numEffectiveSipmPixels` | `638260` | `638260` | SiPM pixel count for saturation |
| `capTime` | `100` | `100` | *"given in ns, 4 samples in HGCROC"* |
| `corrMeanScale` | `"1.0"` | `"34.43…"` (= 1/sampFrac) | per-hit correction — the ScFi branch applies the sampling fraction **here**, at digitization |
| `readout` | `"EcalEndcapPHits"` | `"EcalEndcapPHits"` | readout name |
| `fields` | not set | `{"fiber_x", "fiber_y"}` | cellID fields over which signals are summed before digitizing |

`capADC` / `dyRangeADC` / `pedMeanADC` / `pedSigmaADC` / `resolutionTDC` are
the shared constants above in both branches.

## Stage 2 — Hit reconstruction

**Algorithm:** [`CalorimeterHitReco`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc)
— one instance, shared by both digi branches.

| parameter | FEMC value | meaning |
|---|---|---|
| `capADC` / `dyRangeADC` / `pedMeanADC` / `pedSigmaADC` / `resolutionTDC` | `16384` / `100 GeV` / `200` / `2.4576` / `10 ps` | must match the digi values |
| `thresholdFactor` | `0.0` | unused |
| `thresholdValue` | `3` | absolute pedestal-subtracted ADC cut. Verbatim: *"The ADC of a 15 MeV particle is adc = 200 + 15 * 0.03 * ( 1.0 + 0) / 3000 * 16384 = 200 + 2.4576"* and *"15 MeV = 2.4576, but adc=llround(dE) and cut off is "<". So 3 here = 15.25MeV"* |
| `sampFrac` | `"1.00"` | *"already taken care in DIGI code above"* |
| `readout` | `"EcalEndcapPHits"` | readout name |
| `layerField` / `sectorField` | not set | rec hits carry layer = sector = 0 |

## Stage 3 — Truth proto-clustering

**Algorithm:** [`CalorimeterTruthClustering`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc)
(no configuration) — one proto-cluster per contributing MC primary, hits
shared between proto-clusters. Described on the
[EEMC page]({% link docs/eicrecon/detectors/eemc.md %}).

## Stage 4 — Island proto-clustering

**Algorithm:** [`CalorimeterIslandCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc)
— see the BEMC page. FEMC uses the **dimension-scaled local XY** criterion:
neighbour distances are expressed as multiples of the hit's own cell size, so
one setting works for cells of different sizes.

| parameter | FEMC value | meaning |
|---|---|---|
| `adjacencyMatrix` / `peakNeighbourhoodMatrix` / `readout` | empty | cellID-expression adjacency disabled |
| `sectorDist` | `5.0 cm` | max global distance across sectors |
| `dimScaledLocalDistXY` | `{1.5, 1.5}` | neighbour window in units of the cell's own x/y dimension |
| `localDistXY` / `localDistXZ` / `localDistYZ` / `globalDistRPhi` / `globalDistEtaPhi` | empty | other metrics disabled |
| `splitCluster` | `false` | **no** splitting at local maxima |
| `minClusterHitEdep` | `0.0 MeV` | no per-hit energy cut (zero suppression already at reco) |
| `minClusterCenterEdep` | `60.0 MeV` | min seed-hit energy |
| `transverseEnergyProfileMetric` | `"dimScaledLocalDistXY"` | metric for the splitting profile |
| `transverseEnergyProfileScale` | `1.0` | profile scale |

## Stage 5 — Cluster reconstruction and shapes

[`CalorimeterClusterRecoCoG`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc)
+ [`CalorimeterClusterShape`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc),
both explained on the BEMC page.

| instance | `energyWeight` | `sampFrac` | `logWeightBase` | `enableEtaBounds` |
|---|---|---|---|---|
| `…TruthClustersWithoutShapes` | `log` | `1.0` | `6.2` | **`true`** |
| `…ClustersWithoutShapes` | `log` | `1.0` | `3.6` | `false` |
| `…SplitMergeClustersWithoutShapes` | `log` | `1.0` | `3.6` | `false` |
| `…TruthClusters` (shape) | `log` | — | `6.2` | — |
| `…Clusters` (shape) | `log` | — | `3.6` | — |
| `…SplitMergeClusters` (shape) | `log` | — | `3.6` | — |

FEMC is the only ECal plugin that sets `enableEtaBounds = true` anywhere —
and only on the *truth* branch (see caveat 3).
`longitudinalShowerInfoAvailable` is never set, so it stays `false`.

## Stage 6 — Track-driven cluster merging and splitting

**Algorithm:** [`TrackClusterMergeSplitter`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc)
— *"Merges or splits clusters based on tracks matched to them"*; the
significance / merge-window procedure is described on the
[EEMC page]({% link docs/eicrecon/detectors/eemc.md %}).

| parameter | struct default | FEMC value | meaning |
|---|---|---|---|
| `minSigCut` | `-1.0` | `-2.0` | *"any clusters below this will be merged"* |
| `avgEP` | `1.0` | `1.0` | *"average of E/p distribution"* |
| `sigEP` | `1.0` | `0.10` | *"RMS of E/p distribution"* |
| `drAdd` | `0.4` | `0.30` | *"window to merge clusters"* |
| `surfaceToUse` | `1` | `1` | *"index of surface to use for track projections"* |
| `transverseEnergyProfileScale` | `1.0` | `1.0` | *"scale for hit-track distance"* |

Unlike EEMC and BHCAL, FEMC feeds the splitter **the same collection**
(`EcalEndcapPClusters`) that `reco.cc` used to build
`EcalEndcapPTrackClusterMatches`.

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L348-L358)):
`EcalEndcapPRawHits`, `EcalEndcapPRecHits`,
`EcalEndcapPTruthClusters(+Links/Associations)`,
`EcalEndcapPClusters(+Links/Associations)`,
`EcalEndcapPSplitMergeClusters(+Links/Associations)`, plus
`EcalEndcapPTrackClusterMatches`, `ReconstructedEcalEndcapPNeutrals` and the
particle-flow collections `EcalEndcapP{Remnant,Expected}Clusters`,
`EcalEndcapPTrackExpectedCluster{Links,Matches}`,
`EcalEndcapPTrackSplitMergeClusterMatches`.

**Transient** unless requested: `EcalEndcapPTruthProtoClusters`,
`EcalEndcapPIslandProtoClusters`, `EcalEndcapPSplitMergeProtoClusters`, all
`…WithoutShapes` collections and `EcalEndcapPTrackSplitMergeProtoClusterLinks`.

Downstream: `EcalEndcapPClusters` is one of the three inputs to the combined
`EcalClusters` collection
([reco.cc](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L81-L90)),
is matched to track projections
([reco.cc](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L205-L208)),
and is an input to `FarForwardNeutralsReconstruction` →
`ReconstructedEcalEndcapPNeutrals`
([reco.cc](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L242-L250)).

## Caveats / needs human verification

1. **`EcalEndcapP_Homogeneous_ScFi` > 2 registers no digitizer.** The two
   branches are `if (flag <= 1)` and `else if (flag == 2)`
   ([source](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L69-L120));
   there is no `else`. The log message also groups `flag == 1` with
   "Homogeneous", so the constant's intended value set is not obvious from
   EICrecon alone — it is defined in the **`epic` geometry description**.
2. **The CI flags dump reflects only one branch.** `FEMC:EcalEndcapPRecHits:*`
   is present, but the digi flags in the dump correspond to whichever branch
   the CI geometry selected. Do not read the dump as documenting both.
3. `enableEtaBounds = true` only on the truth branch, `false` on the
   production and split/merge branches — the endcap edge-effect correction
   the config struct recommends for endcaps is therefore **not** applied to
   the physics clusters. Likely unintentional; needs confirmation.
4. The `thresholdValue = 3` comment computes `200 + 15 * 0.03 / 3000 * 16384`,
   i.e. it is written for an older parameterization (sampling fraction 0.03,
   3000 MeV dynamic range). With the current values
   (`16384 / 100 GeV`) a 15 MeV deposit is *coincidentally* also 2.4576 ADC,
   so the stated conclusion still holds — but the formula in the comment does
   not describe the current configuration. Note also that
   `CalorimeterHitReco` compares against the **pedestal-subtracted** ADC, so
   the `200 +` term in the comment does not enter the cut.
5. `pedSigmaADC = 2.4576` is numerically identical to the ADC value of a
   15 MeV deposit. That makes the pedestal noise exactly one threshold unit
   wide. Whether this is a deliberate choice or a copied constant is not
   determinable from the source.
6. `threshold = 0` is annotated as deferring to an ADC cut, but in
   `CalorimeterHitDigi` `threshold` only gates whether energy-resolution
   smearing is applied
   ([line 215](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L213-L219)),
   never whether a hit survives. With `threshold = 0` the smearing is
   effectively always on.
7. `sampFrac = 0.029043` (*"updated with ratio to ScFi model"*) has no
   reference to the study that produced it, and it is applied only in the
   ScFi branch's `corrMeanScale`.
8. `fiber_x` / `fiber_y` and all other cellID field names live in the
   **`epic` geometry description**, not in EICrecon.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
