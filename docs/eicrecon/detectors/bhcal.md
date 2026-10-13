---
title: Barrel HCal (BHCAL)
parent: EICrecon
nav_order: 5
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Barrel Hadronic Calorimeter (BHCAL) Reconstruction

*Also known as: BHCal, barrel HCal, central HCal, outer HCal, re-used sPHENIX outer HCal, HcalBarrel (collection prefix), HcalBarrelHits (readout), BHCAL (flag prefix), system ID 111 (`HcalBarrel_ID`, DEPRECATED spelling `HCalBarrel_ID`).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The barrel HCal (`HcalBarrel`, the re-used sPHENIX outer HCal) is
reconstructed with **cellID-expression adjacency in (η, φ) tile indices**,
including an explicit wrap-around term at φ = 0. Everything is registered in
[`src/detectors/BHCAL/BHCAL.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc).
The runtime flag prefix is `BHCAL:` (120 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

## Chain overview

`HcalBarrelHits` (edm4hep::SimCalorimeterHit) + `EventHeader`
→ **CalorimeterHitDigi** → `HcalBarrelRawHits` (+ `…RawHitLinks`, `…RawHitAssociations`)
→ **CalorimeterHitReco** → `HcalBarrelRecHits`

*side branch:* `HcalBarrelRecHits` → **CalorimeterHitsMerger** → `HcalBarrelMergedHits` *(identity transform by default — see stage 3)*

**Truth branch:**

(`HcalBarrelRecHits`, `HcalBarrelRawHitLinks`)
→ **CalorimeterTruthClustering** → `HcalBarrelTruthProtoClusters`
→ **CalorimeterClusterRecoCoG** → `HcalBarrelTruthClustersWithoutShapes`
→ **CalorimeterClusterShape** → `HcalBarrelTruthClusters`

**Reconstruction branch:**

`HcalBarrelRecHits`
→ **CalorimeterIslandCluster** → `HcalBarrelIslandProtoClusters`
→ **CalorimeterClusterRecoCoG** → `HcalBarrelClustersWithoutShapes`
→ **CalorimeterClusterShape** → **`HcalBarrelClusters`**

**Track-driven split/merge branch:**

(`HcalBarrelTrackClusterMatches`, `HcalBarrelClustersWithoutShapes`, `CalorimeterTrackProjections`)
→ **TrackClusterMergeSplitter** → `HcalBarrelSplitMergeProtoClusters` (+ `…TrackSplitMergeProtoClusterLinks`)
→ **CalorimeterClusterRecoCoG** → `HcalBarrelSplitMergeClustersWithoutShapes`
→ **CalorimeterClusterShape** → `HcalBarrelSplitMergeClusters`

Unlike EHCAL, both clustering branches consume the **rec** hits; the merged
hits are produced but not consumed inside the plugin.

## Stage 1 — Digitization

**Algorithm:** [`CalorimeterHitDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc)
— explained on the [BEMC page]({% link docs/eicrecon/detectors/bemc.md %}).
`readoutType` stays at the default `"simple"` (linear ADC conversion).

| parameter | BHCAL value | meaning |
|---|---|---|
| `eRes` | `{}` (empty) | no energy-resolution smearing |
| `tRes` | `0 ns` | no time smearing |
| `threshold` | `0` | *"Use ADC cut instead"* — see caveat 4 |
| `capADC` | `65536` | *"65536, 16bit ADC"* |
| `capTime` | `100` | *"given in ns, 4 samples in HGCROC"* |
| `dyRangeADC` | `1.0 GeV` | energy at full ADC scale |
| `pedMeanADC` / `pedSigmaADC` | `300` / `2` | pedestal mean and noise sigma |
| `resolutionTDC` | `1 ps` | TDC least count — **ten times finer** than every other ePIC calorimeter |
| `corrMeanScale` | `"1.0"` | per-hit correction expression |
| `readout` | `"HcalBarrelHits"` | readout used to decode cellIDs |

## Stage 2 — Hit reconstruction

**Algorithm:** [`CalorimeterHitReco`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc)
— as on the BEMC page.

| parameter | BHCAL value | meaning |
|---|---|---|
| `capADC` / `dyRangeADC` / `pedMeanADC` / `resolutionTDC` | `65536` / `1.0 GeV` / `300` / `1 ps` | must match the digi values |
| `pedSigmaADC` | `2` | *"not used; relying on energy cut"* |
| `thresholdFactor` | `0.0` | *"not used; relying on flat ADC cut"* |
| `thresholdValue` | `33` | *"pedSigmaADC + thresholdValue = half-MIP (333 ADC)"* — see caveat 3 |
| `sampFrac` | `"0.033"` | *"average, from sPHENIX simulations"* |
| `readout` | `"HcalBarrelHits"` | readout name |
| `layerField` | `""` (explicitly cleared) | no layer decoding — rec hits carry layer 0 |
| `sectorField` | `""` (explicitly cleared) | no sector decoding — rec hits carry sector 0 |

BHCAL is the only calorimeter that sets `layerField`/`sectorField` to the
empty string *explicitly* rather than leaving them at the default.

## Stage 3 — Optional φ-tile merging

**Algorithm:** [`CalorimeterHitsMerger`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitsMerger.cc)
— *"An algorithm to group readout hits from a calorimeter. Energy is summed"*.
Mechanics are described on the
[EHCAL page]({% link docs/eicrecon/detectors/ehcal.md %}):
each `<field>:<expression>` entry replaces that cellID field with the value of
the expression; hits with identical rebuilt cellIDs are summed.

The plugin's own comment states the intent verbatim
([source](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L88-L96)):

> *If needed, merge adjacent phi tiles into towers. By default, NO merging
> will be done. This can be changed at runtime.*

| parameter | struct default | BHCAL value | meaning |
|---|---|---|---|
| `readout` | `""` | `"HcalBarrelHits"` | readout whose idSpec supplies the field names |
| `fieldTransformations` | `{}` | `{"phi:phi"}` | **identity** — `phi` is replaced by itself, so every hit keeps its own cellID and no two hits merge. Change to e.g. `phi:phi/2` at runtime to actually group tiles |

## Stage 4 — Truth proto-clustering

**Algorithm:** [`CalorimeterTruthClustering`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc)
(no configuration) — one proto-cluster per contributing MC primary, hits
shared rather than partitioned. Described on the
[EEMC page]({% link docs/eicrecon/detectors/eemc.md %}).
Input is `HcalBarrelRecHits` (not the merged hits).

## Stage 5 — Island proto-clustering

**Algorithm:** [`CalorimeterIslandCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc)
— see the BEMC page. BHCAL builds its adjacency expression in the plugin
([source](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L39-L49)),
with the magic constant documented inline as *"320 - number of tiles per
row"*:

```
(  ( (abs(eta_1 - eta_2) == 1) && (abs(phi_1 - phi_2) == 0) ) ||   // vertically adjacent tiles
   ( (abs(eta_1 - eta_2) == 0) && (abs(phi_1 - phi_2) == 1) ) ||   // horizontally adjacent tiles
   ( (abs(eta_1 - eta_2) == 0) && (abs(phi_1 - phi_2) == (320 - 1)) )  // horizontally adjacent at wraparound
) == 1
```

The third clause is what stitches the barrel closed across φ = 0.

| parameter | BHCAL value | meaning |
|---|---|---|
| `adjacencyMatrix` | the expression above | 4-connected (η, φ) tile adjacency with φ wrap-around |
| `peakNeighbourhoodMatrix` | empty | (no separate local-maximum neighbourhood defined) |
| `readout` | `"HcalBarrelHits"` | readout supplying `eta` / `phi` |
| `sectorDist` | `5.0 cm` | max global distance across sectors |
| `localDistXY` … `dimScaledLocalDistXY` | all empty | metric neighbour criteria disabled |
| `splitCluster` | `false` | **no** splitting at local maxima |
| `minClusterHitEdep` | `5.0 MeV` | min hit energy to enter clustering |
| `minClusterCenterEdep` | `30.0 MeV` | min seed-hit energy |
| `transverseEnergyProfileMetric` | `"globalDistEtaPhi"` | metric for the splitting profile |
| `transverseEnergyProfileScale` | `1.0` | profile scale |

## Stage 6 — Cluster reconstruction and shapes

[`CalorimeterClusterRecoCoG`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc)
+ [`CalorimeterClusterShape`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc),
both explained on the BEMC page. As in EHCAL, all six instances share the
same weighting:

| instance | `energyWeight` | `sampFrac` | `logWeightBase` | `enableEtaBounds` |
|---|---|---|---|---|
| `…ClustersWithoutShapes` | `log` | `1.0` | `6.2` | `false` |
| `…TruthClustersWithoutShapes` | `log` | `1.0` | `6.2` | `false` |
| `…SplitMergeClustersWithoutShapes` | `log` | `1.0` | `6.2` | `false` |
| all three shape instances | `log` | — | `6.2` | — |

`sampFrac = 1.0` at cluster level because the 0.033 sampling fraction is
already applied at `CalorimeterHitReco`.
`longitudinalShowerInfoAvailable` is never set, so it stays `false`.

## Stage 7 — Track-driven cluster merging and splitting

**Algorithm:** [`TrackClusterMergeSplitter`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc)
— procedure described on the
[EEMC page]({% link docs/eicrecon/detectors/eemc.md %}).

| parameter | struct default | BHCAL value | meaning |
|---|---|---|---|
| `minSigCut` | `-1.0` | `-2.0` | *"any clusters below this will be merged"* |
| `avgEP` | `1.0` | `0.50` | *"average of E/p distribution"* — hadronic |
| `sigEP` | `1.0` | `0.25` | *"RMS of E/p distribution"* |
| `drAdd` | `0.4` | `0.40` | *"window to merge clusters"* |
| `surfaceToUse` | `1` | `1` | *"index of surface to use for track projections"* |
| `transverseEnergyProfileScale` | `1.0` | `1.0` | *"scale for hit-track distance"* |

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L421-L429)):
`HcalBarrelRawHits`, `HcalBarrelRecHits`, `HcalBarrelMergedHits`,
`HcalBarrelClusters(+Links/Associations)`,
`HcalBarrelSplitMergeClusters(+Links/Associations)`, and (further down,
[L438-L440](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L438-L440))
`HcalBarrelTruthClusters(+Links/Associations)`, plus
`HcalBarrelTrackClusterMatches` and the particle-flow collections
`HcalBarrel{Remnant,Expected}Clusters`,
`HcalBarrelTrackExpectedCluster{Links,Matches}`,
`HcalBarrelTrackSplitMergeClusterMatches`.

**Transient** unless requested: `HcalBarrelTruthProtoClusters`,
`HcalBarrelIslandProtoClusters`, `HcalBarrelSplitMergeProtoClusters`, all
`…WithoutShapes` collections, `HcalBarrelTrackSplitMergeProtoClusterLinks`.

Downstream: `HcalBarrelClusters` is matched to track projections to produce
`HcalBarrelTrackClusterMatches`
([reco.cc](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L224-L227)).
HCal clusters do **not** enter the combined `EcalClusters` collection.

## Caveats / needs human verification

1. **`HcalBarrelMergedHits` is a dead output inside the plugin.** It is
   produced (with an identity transform, so it is a copy of
   `HcalBarrelRecHits`) and persisted by default, but no factory in
   `BHCAL.cc` consumes it — both clustering branches read the rec hits. The
   comment says merging is meant to be enabled at runtime, but enabling it
   would change only this unused collection.
2. **The splitter's seed clusters come from a different collection.**
   `TrackClusterMergeSplitter` is given `HcalBarrelClustersWithoutShapes`,
   while `HcalBarrelTrackClusterMatches` is built from `HcalBarrelClusters`
   (the post-shape re-emission)
   ([reco.cc](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L224-L227)).
   The algorithm keys its merge map on `match.getCluster()` and compares by
   object ID
   ([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L61-L72)),
   so the seeds are objects from a collection that is not the candidate list.
   EHCAL, FEMC and LFHCAL pass the matched collection itself. Same asymmetry
   as EEMC; needs a maintainer's confirmation.
3. The `thresholdValue` comment says *"pedSigmaADC + thresholdValue =
   half-MIP (333 ADC)"* but 300 + 33 = 333 uses **`pedMeanADC`**, not
   `pedSigmaADC` (which is 2). Also, `CalorimeterHitReco` compares against
   the **pedestal-subtracted** ADC, so the operative cut is 33 ADC ≈ 0.5 MeV,
   not 333.
4. `threshold = 0` is annotated *"Use ADC cut instead"*, but in
   `CalorimeterHitDigi` the `threshold` field only gates whether
   energy-resolution smearing is applied
   ([line 215](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L213-L219));
   it never drops a hit. With `eRes` empty the setting has no effect at all.
5. `resolutionTDC = 1 ps` is 10× finer than every other ePIC calorimeter with
   no comment explaining why.
6. The magic constant `320` (tiles per row) is hard-coded in the adjacency
   expression; if the **`epic`** φ segmentation changes, this string silently
   stops stitching the wrap-around.
7. `sampFrac = "0.033"` is credited to *"sPHENIX simulations"* with no
   reference, and is described as an "average" — i.e. no layer dependence,
   consistent with `layerField` being cleared.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
