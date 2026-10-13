---
title: Backward HCal — nHCal (EHCAL)
parent: EICrecon
nav_order: 4
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Backward (Electron-Going) Endcap Hadronic Calorimeter (EHCAL) Reconstruction

*Also known as: nHCal, backward HCal, negative-endcap HCal, electron-going endcap HCal, electron endcap HCal, HcalEndcapN (collection prefix), HcalEndcapNHits (readout), EHCAL (flag prefix), system ID 113 (`HcalEndcapN_ID`, DEPRECATED spelling `HCalEndcapN_ID`).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The backward endcap HCal (`HcalEndcapN`) is a sampling calorimeter whose
reconstruction adds one step the ECal plugins do not have: after hit
reconstruction, **all longitudinal layers are summed into single towers** by
`CalorimeterHitsMerger`, and clustering runs on those merged hits. Everything
is registered in
[`src/detectors/EHCAL/EHCAL.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc).
The runtime flag prefix is `EHCAL:` (111 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

## Chain overview

`HcalEndcapNHits` (edm4hep::SimCalorimeterHit) + `EventHeader`
→ **CalorimeterHitDigi** → `HcalEndcapNRawHits` (+ `…RawHitLinks`, `…RawHitAssociations`)
→ **CalorimeterHitReco** → `HcalEndcapNRecHits`
→ **CalorimeterHitsMerger** → `HcalEndcapNMergedHits`

**Truth branch:**

(`HcalEndcapNMergedHits`, `HcalEndcapNRawHitLinks`)
→ **CalorimeterTruthClustering** → `HcalEndcapNTruthProtoClusters`
→ **CalorimeterClusterRecoCoG** → `HcalEndcapNTruthClustersWithoutShapes`
→ **CalorimeterClusterShape** → `HcalEndcapNTruthClusters`

**Reconstruction branch:**

`HcalEndcapNMergedHits`
→ **CalorimeterIslandCluster** → `HcalEndcapNIslandProtoClusters`
→ **CalorimeterClusterRecoCoG** → `HcalEndcapNClustersWithoutShapes`
→ **CalorimeterClusterShape** → **`HcalEndcapNClusters`**

**Track-driven split/merge branch:**

(`HcalEndcapNTrackClusterMatches`, `HcalEndcapNClusters`, `CalorimeterTrackProjections`)
→ **TrackClusterMergeSplitter** → `HcalEndcapNSplitMergeProtoClusters` (+ `…TrackSplitMergeProtoClusterLinks`)
→ **CalorimeterClusterRecoCoG** → `HcalEndcapNSplitMergeClustersWithoutShapes`
→ **CalorimeterClusterShape** → `HcalEndcapNSplitMergeClusters`

Note that the truth and island branches consume the **merged** hits, not the
rec hits — unlike BHCAL, where both consume rec hits.

## Stage 1 — Digitization

**Algorithm:** [`CalorimeterHitDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc)
— explained on the [BEMC page]({% link docs/eicrecon/detectors/bemc.md %}).
EHCAL leaves `readoutType` at its default `"simple"`, so the ADC is the plain
linear conversion `ADC = ped + edep × corrMeanScale / dyRangeADC × capADC`.

| parameter | EHCAL value | meaning |
|---|---|---|
| `eRes` | `{}` (empty) | no energy-resolution smearing |
| `tRes` | `0 ns` | no time smearing |
| `capADC` | `32768` | *"assuming 15 bit ADC like FHCal"* |
| `capTime` | `100` | *"given in ns, 4 samples in HGCROC"* |
| `dyRangeADC` | `200 MeV` | *"to be verified with simulations"* |
| `pedMeanADC` / `pedSigmaADC` | `10` / `2` | pedestal mean and noise sigma |
| `resolutionTDC` | `10 ps` | TDC least count |
| `corrMeanScale` | `"1.0"` | per-hit correction expression |
| `readout` | `"HcalEndcapNHits"` | readout used to decode cellIDs |

## Stage 2 — Hit reconstruction

**Algorithm:** [`CalorimeterHitReco`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc)
— as on the BEMC page.

| parameter | EHCAL value | meaning |
|---|---|---|
| `capADC` / `dyRangeADC` / `pedMeanADC` / `pedSigmaADC` / `resolutionTDC` | `32768` / `200 MeV` / `10` / `2` / `10 ps` | must match the digi values |
| `thresholdFactor` | `0.0` | multiplier on `pedSigmaADC`; unused |
| `thresholdValue` | `41.0` | *"0.1875 MeV deposition out of 200 MeV max (per layer) --> adc = 10 + 0.1875 / 200 * 32768 == 41"* |
| `sampFrac` | `"0.0095"` | *"from latest study - implement at level of reco hits rather than clusters"* |
| `readout` | `"HcalEndcapNHits"` | readout name |
| `layerField` / `sectorField` | not set | rec hits carry layer = sector = 0 |

Because the sampling fraction is applied **here**, every downstream
`CalorimeterClusterRecoCoG` instance uses `sampFrac = 1.0`.

## Stage 3 — Longitudinal hit merging

**Algorithm:** [`CalorimeterHitsMerger`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitsMerger.cc)
— *"An algorithm to group readout hits from a calorimeter. Energy is summed"*.
New relative to BEMC, so in full:

For each hit the algorithm rebuilds the cellID field by field
([`build_merge_map`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitsMerger.cc#L176-L202)).
A field listed in `fieldTransformations` as `<field>:<expression>` is replaced
by the value of that expression (compiled by `EvaluatorSvc` with **all**
cellID fields of the hit in scope); every other field is copied unchanged.
Hits whose rebuilt cellID coincides are then one group. Per group the
algorithm sums energies (errors in quadrature), **averages** times, and takes
the position of the rebuilt reference cellID from the DD4hep cell-ID/position
converter. Hits inside a group are sorted by descending energy and the
leading hit supplies `cellID`, `dimension`, `sector` and `layer` of the
output hit.

| parameter | struct default | EHCAL value | meaning |
|---|---|---|---|
| `readout` | `""` | `"HcalEndcapNHits"` | readout whose idSpec supplies the field names |
| `fieldTransformations` | `{}` | `{"layer:4", "slice:0"}` | `layer` is forced to the constant 4 and `slice` to 0 for every hit — so **all layers and slices of one (x, y) tower are summed into a single hit**, positioned at layer 4 |

If the readout or a listed field cannot be resolved the algorithm logs a
warning and returns without configuring the maps
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitsMerger.cc#L62-L79)).

## Stage 4 — Truth proto-clustering

**Algorithm:** [`CalorimeterTruthClustering`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc)
(no configuration) — one proto-cluster per contributing MC primary, hits
shared rather than partitioned. Described on the
[EEMC page]({% link docs/eicrecon/detectors/eemc.md %}).
Input here is `HcalEndcapNMergedHits` together with the **raw**-hit links.

## Stage 5 — Island proto-clustering

**Algorithm:** [`CalorimeterIslandCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc)
— see the BEMC page.

| parameter | EHCAL value | meaning |
|---|---|---|
| `adjacencyMatrix` / `peakNeighbourhoodMatrix` / `readout` | empty | cellID-expression adjacency disabled |
| `sectorDist` | `5.0 cm` | max global distance across sectors |
| `localDistXY` | `{15 cm, 15 cm}` | the active neighbour criterion |
| `localDistXZ` / `localDistYZ` / `globalDistRPhi` / `globalDistEtaPhi` / `dimScaledLocalDistXY` | empty | other metrics disabled |
| `splitCluster` | `true` | split proto-clusters at local energy maxima |
| `minClusterHitEdep` | `0.0 MeV` | no per-hit energy cut |
| `minClusterCenterEdep` | `30.0 MeV` | min seed-hit energy |
| `transverseEnergyProfileMetric` | `"globalDistEtaPhi"` | metric for the splitting profile |
| `transverseEnergyProfileScale` | `1.0` | profile scale (η–φ units) |

## Stage 6 — Cluster reconstruction and shapes

[`CalorimeterClusterRecoCoG`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc)
+ [`CalorimeterClusterShape`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc),
both explained on the BEMC page. EHCAL is unusual in that **every** instance
uses the same weighting:

| instance | `energyWeight` | `sampFrac` | `logWeightBase` | `enableEtaBounds` |
|---|---|---|---|---|
| `…TruthClustersWithoutShapes` | `log` | `1.0` | `6.2` | `false` |
| `…ClustersWithoutShapes` | `log` | `1.0` | `6.2` | `false` |
| `…SplitMergeClustersWithoutShapes` | `log` | `1.0` | `6.2` | `false` |
| all three shape instances | `log` | — | `6.2` | — |

`longitudinalShowerInfoAvailable` is never set, so it stays `false` and no
intrinsic θ/φ are computed — even though the layer structure was collapsed by
the merger, which is exactly the situation where longitudinal shower info
would be unavailable.

## Stage 7 — Track-driven cluster merging and splitting

**Algorithm:** [`TrackClusterMergeSplitter`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc)
— procedure described on the
[EEMC page]({% link docs/eicrecon/detectors/eemc.md %}).

| parameter | struct default | EHCAL value | meaning |
|---|---|---|---|
| `minSigCut` | `-1.0` | `-2.0` | *"any clusters below this will be merged"* |
| `avgEP` | `1.0` | `0.60` | *"average of E/p distribution"* — hadronic, well below 1 |
| `sigEP` | `1.0` | `0.40` | *"RMS of E/p distribution"* |
| `drAdd` | `0.4` | `0.40` | *"window to merge clusters"* |
| `surfaceToUse` | `1` | `1` | *"index of surface to use for track projections"* |
| `transverseEnergyProfileScale` | `1.0` | `1.0` | *"scale for hit-track distance"* |

Input is `HcalEndcapNClusters` — the same collection `reco.cc` used to build
`HcalEndcapNTrackClusterMatches`, unlike EEMC and BHCAL.

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L398-L406)):
`HcalEndcapNRawHits`, `HcalEndcapNRecHits`, `HcalEndcapNMergedHits`,
`HcalEndcapNClusters(+Links/Associations)`,
`HcalEndcapNSplitMergeClusters(+Links/Associations)`, and (further down the
list, [L435-L437](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L435-L437))
`HcalEndcapNTruthClusters(+Links/Associations)`, plus
`HcalEndcapNTrackClusterMatches` and the particle-flow collections
`HcalEndcapN{Remnant,Expected}Clusters`,
`HcalEndcapNTrackExpectedCluster{Links,Matches}`,
`HcalEndcapNTrackSplitMergeClusterMatches`.

**Transient** unless requested: `HcalEndcapNTruthProtoClusters`,
`HcalEndcapNIslandProtoClusters`, `HcalEndcapNSplitMergeProtoClusters`, all
`…WithoutShapes` collections, `HcalEndcapNTrackSplitMergeProtoClusterLinks`.

Downstream: `HcalEndcapNClusters` is matched to track projections to produce
`HcalEndcapNTrackClusterMatches`
([reco.cc](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L233-L236)).
HCal clusters do **not** enter the combined `EcalClusters` collection.

## Caveats / needs human verification

1. **Duplicate factory tag.** The `CalorimeterClusterRecoCoG_factory` for the
   split/merge branch is registered under the tag
   `"HcalEndcapNClustersWithoutShapes"` — identical to the tag of the island
   CoG factory registered ~30 lines earlier — while its inputs and outputs
   are the SplitMerge collections
   ([source](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L157-L172)).
   Every other plugin uses `"…SplitMergeClustersWithoutShapes"` as the tag
   here. Consequences: the two factories share the `EHCAL:HcalEndcapNClustersWithoutShapes:*`
   runtime-flag namespace, so a flag intended for one also hits the other.
   This looks like a copy-paste bug and needs a maintainer's confirmation.
2. `dyRangeADC = 200 MeV` is explicitly marked *"to be verified with
   simulations"*.
3. `capADC = 32768` is justified only by *"assuming 15 bit ADC like FHCal"* —
   a cross-reference, not a measurement.
4. `sampFrac = "0.0095"` cites *"latest study"* with no link, date or
   geometry version.
5. The merger transformation `layer:4` positions every merged tower at layer
   4 of the readout. Whether 4 is the shower-maximum layer or an arbitrary
   reference is not stated anywhere in EICrecon.
6. The island clusteriser sets `minClusterHitEdep = 0`, so the only energy
   cut on hits is the ADC threshold at reco — worth checking against the
   noise level implied by `pedSigmaADC = 2` (≈ 0.012 MeV).
7. All cellID field names (`layer`, `slice`) come from the **`epic` geometry
   description**, not from EICrecon.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
