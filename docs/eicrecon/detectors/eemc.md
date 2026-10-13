---
title: Backward ECal — EEMC
parent: EICrecon
nav_order: 2
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Backward (Electron-Going) Endcap Electromagnetic Calorimeter (EEMC) Reconstruction

*Also known as: EEMC, backward ECal, electron-going endcap ECal, negative-endcap ECal, electron endcap ECal, crystal endcap calorimeter, PbWO₄ endcap ECal, EcalEndcapN (collection prefix), EcalEndcapNHits (readout), EEMC (flag prefix), system ID 103 (`EcalEndcapN_ID`, DEPRECATED spelling `ECalEndcapN_ID`).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The backward endcap ECal (`EcalEndcapN`, listed under `// Backward` in
[`src/global/reco/reco.cc`](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L228-L232))
is read out with SiPMs and reconstructed with a **near-unity sampling
fraction** (`0.96`), i.e. the plugin treats it as an essentially homogeneous
calorimeter. Everything is registered in
[`src/detectors/EEMC/EEMC.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc).
The runtime flag prefix is `EEMC:` (125 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

EEMC is the **only ePIC calorimeter whose default `…Clusters` collection is
produced by a machine-learning stage**: an ONNX π/e discriminator runs after
shape reconstruction and its output collection carries the final name.

## Chain overview

**Common front end:**

`EcalEndcapNHits` (edm4hep::SimCalorimeterHit) + `EventHeader`
→ **CalorimeterHitDigi** (`readoutType="sipm"`) → `EcalEndcapNRawHits` (+ `…RawHitLinks`, `…RawHitAssociations`)
→ **CalorimeterHitReco** → `EcalEndcapNRecHits`

**Truth branch (MC reference):**

(`EcalEndcapNRecHits`, `EcalEndcapNRawHitLinks`)
→ **CalorimeterTruthClustering** → `EcalEndcapNTruthProtoClusters`
→ **CalorimeterClusterRecoCoG** → `EcalEndcapNTruthClustersWithoutShapes`
→ **CalorimeterClusterShape** → `EcalEndcapNTruthClusters`

**Reconstruction branch (the default one):**

`EcalEndcapNRecHits`
→ **CalorimeterIslandCluster** → `EcalEndcapNIslandProtoClusters`
→ **CalorimeterClusterRecoCoG** → `EcalEndcapNClustersWithoutPIDAndShapes`
→ **CalorimeterClusterShape** → `EcalEndcapNClustersWithoutPID`
→ **CalorimeterParticleIDPreML** → `EcalEndcapNParticleIDInput_features` (+ `…Target`)
→ **ONNXInference** → `EcalEndcapNParticleIDOutput_label`, `…Output_probability_tensor`
→ **CalorimeterParticleIDPostML** → **`EcalEndcapNClusters`** (+ `…ClusterLinks`, `…ClusterAssociations`, `…ClusterParticleIDs`)

**Track-driven split/merge branch:**

(`EcalEndcapNTrackClusterMatches`, `EcalEndcapNClustersWithoutPID`, `CalorimeterTrackProjections`)
→ **TrackClusterMergeSplitter** → `EcalEndcapNSplitMergeProtoClusters` (+ `…TrackSplitMergeProtoClusterLinks`)
→ **CalorimeterClusterRecoCoG** → `EcalEndcapNSplitMergeClustersWithoutShapes`
→ **CalorimeterClusterShape** → `EcalEndcapNSplitMergeClusters`

## Stage 1 — Digitization with a SiPM response model

**Algorithm:** [`CalorimeterHitDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc)
— explained on the [BEMC page]({% link docs/eicrecon/detectors/bemc.md %}).
Unlike BEMC, EEMC selects `readoutType="sipm"`, which replaces the linear
ADC conversion by an explicit photon-counting model
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L246-L260)):

```
n_photons          = edep × lightYield
n_photons_detected ~ Binomial(n_photons, photonDetectionEfficiency)
n_pixels_fired     = N × (1 − exp(−n_photons_detected / N))     # N = numEffectiveSipmPixels
n_max_photons      = dyRangeADC × lightYield × photonDetectionEfficiency
ADC                = ped + n_pixels_fired × corrMeanScale / n_max_photons × capADC
```

The `1 − exp(−n/N)` term is the SiPM pixel-saturation curve; it makes the
response non-linear near the top of the dynamic range.

| parameter | struct default | EEMC value | meaning |
|---|---|---|---|
| `eRes` | `{}` | `{0, 0, 0}` | resolution coefficients a, b, c — **no extra smearing**; resolution comes from photostatistics |
| `tRes` | — | `0 ns` | time smearing |
| `threshold` | `1 keV` | `0 MeV` | *"Use ADC cut instead"* — see caveat 4 |
| `readoutType` | `"simple"` | `"sipm"` | selects the SiPM model above |
| `lightYield` | `0 /GeV` | `18 / 0.25 per MeV` = 72/MeV | *"18. pe/MeV is measured with PMT at 25% QE"* |
| `photonDetectionEfficiency` | `0` | `(16 × 3×3 / (20×20)) × 0.28` ≈ 0.1008 | *"Geometric factor for 16 of 3x3 mm^2 sensors covering 20x20 mm^2 area for sensor with 28% QE"*, from [this calo-meeting slide](https://indico.bnl.gov/event/29076/contributions/110749/attachments/63706/109457/Calo_meeting_Jun25_Updated.pdf) |
| `numEffectiveSipmPixels` | `0` | `39984 × 16` = 639,744 | *"S14160-3015PS, 16 sensors per cell"* |
| `capADC` | `1` | `16384` | *"65536, 16bit ADC"* (comment is stale — the value is 14-bit) |
| `dyRangeADC` | `1` | `20 GeV` | energy at full ADC scale |
| `pedMeanADC` / `pedSigmaADC` | `0` / `0` | `20` / `1` | pedestal mean and noise sigma |
| `resolutionTDC` | `1` | `10 ps` | TDC least count |
| `corrMeanScale` | `"1.0"` | `"1.0"` | per-hit correction expression |
| `readout` | `""` | `"EcalEndcapNHits"` | readout used to decode cellIDs |
| `capTime` | `1000 ns` | not set → `1000 ns` | dynamic range in time; only logged, never used to drop hits |

## Stage 2 — Hit reconstruction

**Algorithm:** [`CalorimeterHitReco`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc)
— ADC → calibrated energy/time/position, as on the BEMC page.

| parameter | EEMC value | meaning |
|---|---|---|
| `capADC` / `dyRangeADC` / `pedMeanADC` / `pedSigmaADC` / `resolutionTDC` | `16384` / `20 GeV` / `20` / `1` / `10 ps` | must match the digi values (shared local variables in the plugin) |
| `thresholdFactor` | `0.0` | multiplier on `pedSigmaADC`; unused here |
| `thresholdValue` | `4.0` | absolute pedestal-subtracted ADC cut — *"(20. GeV / 16384) * 4 ~= 5 MeV"* |
| `sampFrac` | `"0.96"` | sampling fraction, evaluated per hit with cellID fields in scope |
| `readout` | `"EcalEndcapNHits"` | readout name |
| `layerField` / `sectorField` | not set (`""`) | no layer/sector decoding — reconstructed hits carry layer = sector = 0 |

## Stage 3 — Truth proto-clustering

**Algorithm:** [`CalorimeterTruthClustering`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc)
(no configuration). This is the MC-truth reference clusteriser used by every
endcap/forward calorimeter plugin. For each reconstructed hit it walks the
`MCRecoCalorimeterHitLink` back to the sim hits, and for each Geant4
contribution walks the MC particle's parent chain up to the **primary**
(`get_primary`, [source](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc#L67-L84)
— *"TODO finalize primary selection. This can be improved!!"*). One
proto-cluster is created per contributing primary, and a hit is added — with
weight 1 — to **every** proto-cluster it contributed to, so hits are shared,
not partitioned.

## Stage 4 — Island proto-clustering

**Algorithm:** [`CalorimeterIslandCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc)
— adjacency-based grouping with optional splitting at local maxima, as on the
BEMC page. EEMC uses **cellID-expression adjacency** rather than the metric
distances BEMC uses.

| parameter | EEMC value | meaning |
|---|---|---|
| `adjacencyMatrix` | `"(abs(row_1 - row_2) + abs(column_1 - column_2)) == 1"` | two hits are neighbours iff they share an edge in the (row, column) crystal grid |
| `peakNeighbourhoodMatrix` | `"max(abs(row_1 - row_2), abs(column_1 - column_2)) == 1"` | neighbourhood used when searching for local maxima — the 8-cell Chebyshev ring (undocumented in the config struct) |
| `readout` | `"EcalEndcapNHits"` | readout supplying `row` / `column` |
| `sectorDist` | `5.0 cm` | max global distance for hits in different sectors |
| `localDistXY` … `dimScaledLocalDistXY` | all empty | metric neighbour criteria disabled |
| `splitCluster` | `true` | split proto-clusters at local energy maxima |
| `minClusterHitEdep` | `1.0 MeV` | min hit energy to enter clustering |
| `minClusterCenterEdep` | `30.0 MeV` | min seed-hit energy |
| `transverseEnergyProfileMetric` | `"globalDistEtaPhi"` | distance metric for the splitting energy profile |
| `transverseEnergyProfileScale` | `0.08` | profile scale in that metric (η–φ units) |
| `transverseEnergyProfileScaleUnits` | empty | (undocumented) |

## Stage 5 — Cluster reconstruction and shapes

[`CalorimeterClusterRecoCoG`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc)
computes the log-weighted centre of gravity, and
[`CalorimeterClusterShape`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc)
adds shape parameters and re-emits the clusters (hence every `…WithoutShapes`
twin) — both explained on the BEMC page. EEMC registers three CoG + three
shape instances:

| instance | `energyWeight` | `sampFrac` | `logWeightBase` | `enableEtaBounds` |
|---|---|---|---|---|
| `…TruthClustersWithoutShapes` | `log` | `1.0` | `4.6` | `false` |
| `…ClustersWithoutPIDAndShapes` | `log` | `1.0` | `3.6` | `false` |
| `…SplitMergeClustersWithoutShapes` | `log` | `1.0` | `3.6` | `false` |
| `…TruthClusters` (shape) | `log` | — | `4.6` | — |
| `…ClustersWithoutPID` (shape) | `log` | — | `3.6` | — |
| `…SplitMergeClusters` (shape) | `log` | — | `3.6` | — |

`enableEtaBounds` — *"Constrain the cluster position eta to be within the eta
of the contributing hits. This is useful to avoid edge effects for endcaps."*
([config struct](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoGConfig.h#L26-L29)).
It is **false** in every EEMC instance despite EEMC being an endcap.
`longitudinalShowerInfoAvailable` is not set anywhere in EEMC, so it defaults
to `false` and no intrinsic θ/φ are computed.

## Stage 6 — ONNX particle identification (π/e separation)

Three factories in sequence. This block is unique to EEMC.

### 6a. `CalorimeterParticleIDPreML`

[Source](https://github.com/eic/EICrecon/blob/main/src/algorithms/onnx/CalorimeterParticleIDPreML.cc)
(no configuration). Builds a float feature tensor of shape
`(n_clusters, 11)` — *"p, E/p, azimuthal, polar, 7 shape parameters"* — plus
an optional int64 target tensor of shape `(n_clusters, 2)` (`is_pion`,
`is_electron`) for training. Inputs: `EcalEndcapNClustersWithoutPID` and its
associations.

The momentum `p` is taken from the **highest-weight MC association**, not
from a track: *"FIXME: use track momentum once matching to tracks becomes
available"*. Clusters without an association are skipped with a warning.

### 6b. `ONNXInference`

[Config](https://github.com/eic/EICrecon/blob/main/src/algorithms/onnx/ONNXInferenceConfig.h)
has a single field.

| parameter | value | meaning |
|---|---|---|
| `modelPath` | `"calibrations/onnx/EcalEndcapN_pi_rejection.onnx"` | path to the serialized model (resolved at runtime — see caveat 1) |

Outputs `EcalEndcapNParticleIDOutput_label` and
`EcalEndcapNParticleIDOutput_probability_tensor`.

### 6c. `CalorimeterParticleIDPostML`

[Source](https://github.com/eic/EICrecon/blob/main/src/algorithms/onnx/CalorimeterParticleIDPostML.cc)
(no configuration). Validates the tensor (rank 2, first axis = number of
clusters, second axis = 2, float element type — each violation throws),
**clones** every input cluster, and attaches two `ParticleID` objects:
PDG 211 with likelihood = column 0, PDG 11 with likelihood = column 1. Links
and associations are propagated onto the clones. The cloned collection is the
production `EcalEndcapNClusters`.

## Stage 7 — Track-driven cluster merging and splitting

**Algorithm:** [`TrackClusterMergeSplitter`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc)
— *"An algorithm which takes a collection of clusters, matches track
projections, and then decides to merge or split those clusters based on
average E/p from simulations. Heavily inspired by Eur. Phys. J. C (2017)
77:466"*. Documented procedure
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L24-L39)):

1. Build a map of clusters onto matched track projections.
2. Per pair: significance `sig = (E_cluster − avgEP × |p_proj|) / sigEP`.
   If `sig < minSigCut`, merge every cluster within `drAdd` in (η, φ).
3. One proto-cluster per merged group; if several tracks point at the same
   group, emit one proto-cluster per projection with hits weighted relative
   to each track.
4. Unmatched clusters are passed through as proto-clusters.

| parameter | struct default | EEMC value | meaning |
|---|---|---|---|
| `minSigCut` | `-1.0` | `-1.0` | *"any clusters below this will be merged"* |
| `avgEP` | `1.0` | `1.0` | *"average of E/p distribution"* |
| `sigEP` | `1.0` | `0.10` | *"RMS of E/p distribution"* |
| `drAdd` | `0.4` | `0.08` | *"window to merge clusters"* (Δ√(η²+φ²)) |
| `surfaceToUse` | `1` | `1` | *"index of surface to use for track projections"* |
| `transverseEnergyProfileScale` | `1.0` | `1.0` | *"scale for hit-track distance"* |

`drAdd = 0.08` is the tightest merging window of any ePIC calorimeter, and
`minSigCut = -1.0` the loosest cut (BHCAL/EHCAL/FEMC/LFHCAL all use `-2.0`).

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L337-L347)):
`EcalEndcapNRawHits`, `EcalEndcapNRecHits`,
`EcalEndcapNTruthClusters(+Links/Associations)`,
`EcalEndcapNClusters(+Links/Associations)`,
`EcalEndcapNSplitMergeClusters(+Links/Associations)`, plus
`EcalEndcapNTrackClusterMatches` and the particle-flow collections
`EcalEndcapN{Remnant,Expected}Clusters`, `EcalEndcapNTrackExpectedCluster{Links,Matches}`,
`EcalEndcapNTrackSplitMergeClusterMatches`
([same file](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L482-L515)).

**Transient** unless requested: all `…ProtoClusters`, all `…WithoutShapes` /
`…WithoutPID` collections, the three ParticleID tensors, and
**`EcalEndcapNClusterParticleIDs`** — the PID likelihoods themselves are not
in the default output list, only the `ParticleID` relations from the clusters.

Downstream ([`src/global/reco/reco.cc`](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L81-L90)):
`EcalEndcapNClusters` is one of the three inputs to the combined
`EcalClusters` collection (with `EcalBarrelScFiClusters` and
`EcalEndcapPClusters`), which feeds `MatchClusters` and
`ReconstructedNeutralParticles`. `EcalEndcapNClusters` is also matched to
track projections to produce `EcalEndcapNTrackClusterMatches`
([reco.cc](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L228-L232)).

## Caveats / needs human verification

1. `calibrations/onnx/EcalEndcapN_pi_rejection.onnx` is **not in the EICrecon
   repository**; it is resolved at runtime. Its provenance, training sample
   and validity range are not determinable from EICrecon source.
2. **The PID stage uses MC truth.** `CalorimeterParticleIDPreML` takes the
   cluster momentum from the best MC association
   (*"FIXME: use track momentum once matching to tracks becomes available"*)
   and skips clusters with no association. The default production collection
   `EcalEndcapNClusters` therefore depends on truth information and on the
   completeness of the association collection.
3. The PreML feature-order comment says *"p, E/p, azimuthal, polar, 7 shape
   parameters"* but the code pushes `anglePolar(pos)` **before**
   `angleAzimuthal(pos)`
   ([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/onnx/CalorimeterParticleIDPreML.cc#L62-L69)).
   Comment and code disagree; which order the ONNX model was trained on
   cannot be determined here. The tensor is also hard-coded to 11 columns, so
   the algorithm throws if `CalorimeterClusterShape` ever emits a number of
   shape parameters other than 7.
4. `threshold = 0 MeV` is annotated *"Use ADC cut instead"*, but in
   `CalorimeterHitDigi` the `threshold` field is only used to decide whether
   to apply energy-resolution smearing
   ([line 215](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L213-L219))
   — it never drops a hit. With `eRes = {0,0,0}` here the setting has no
   effect at all.
5. `TrackClusterMergeSplitter` is given `EcalEndcapNClustersWithoutPID`, but
   `EcalEndcapNTrackClusterMatches` is built from `EcalEndcapNClusters` —
   which are **clones** made by `CalorimeterParticleIDPostML`. The seed
   clusters coming out of the match collection are therefore objects from a
   different collection than the merge candidates, and the algorithm compares
   them by object ID
   ([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L61-L72)).
   FEMC, EHCAL and LFHCAL pass the same collection that was used for
   matching. Needs a maintainer's confirmation.
6. The `capADC` comment *"65536, 16bit ADC"* does not match the value
   (`16384`, 14-bit); it appears copied from an older configuration.
7. `sampFrac = "0.96"` and `pedMeanADC = 20` are hard-coded with no
   provenance comment (which geometry version / calibration sample?).
8. All cellID field names (`row`, `column`) live in the **`epic` geometry
   description**, not in EICrecon.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
