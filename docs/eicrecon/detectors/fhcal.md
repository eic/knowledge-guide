---
title: Forward HCal — LFHCAL (FHCAL)
parent: EICrecon
nav_order: 6
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Forward (Hadron-Going) Hadronic Calorimeter (FHCAL) Reconstruction

*Also known as: LFHCAL, longitudinally-segmented forward HCal, forward HCal, hadron-going endcap HCal, positive-endcap HCal, pHCal, HcalEndcapP, plus the high-η insert (forward HCal insert, HcalEndcapPInsert); LFHCAL + HcalEndcapPInsert (collection prefixes), LFHCALHits + HcalEndcapPInsertHits (readouts), FHCAL (flag prefix), system IDs 116 (`LFHCAL_ID`) and 115 (`HcalEndcapPInsert_ID`, DEPRECATED spelling `HCalEndcapPInsert_ID`) — note there is no `HcalEndcapP_ID` constant in the geometry.*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The `FHCAL` plugin registers **two independent detectors** in one file
([`src/detectors/FHCAL/FHCAL.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc)):

- **`HcalEndcapPInsert`** — the high-η insert, a SiPM-on-tile detector with
  hexagonal, staggered cells reconstructed through the **HEXPLIT**
  sub-cell splitting algorithm and topological clustering;
- **`LFHCAL`** — the main longitudinally-segmented forward HCal, reconstructed
  with island clustering on an explicitly constructed 3-D tower adjacency
  expression.

They share nothing but the plugin. The runtime flag prefix is `FHCAL:` (214
flags in the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

## Chain overview

### Insert (`HcalEndcapPInsert`)

`HcalEndcapPInsertHits` + `EventHeader`
→ **CalorimeterHitDigi** → `HcalEndcapPInsertRawHits` (+ `…RawHitLinks`, `…RawHitAssociations`)
→ **CalorimeterHitReco** → `HcalEndcapPInsertRecHits`

*truth branch:* `HcalEndcapPInsertRecHits` → **CalorimeterHitsMerger** → `HcalEndcapPInsertMergedHits`
→ **CalorimeterTruthClustering** → `HcalEndcapPInsertTruthProtoClusters`
→ **CalorimeterClusterRecoCoG** → `…TruthClustersWithoutShapes` → **CalorimeterClusterShape** → `HcalEndcapPInsertTruthClusters`

*reconstruction branch:* `HcalEndcapPInsertRecHits`
→ **HEXPLIT** → `HcalEndcapPInsertSubcellHits`
→ **ImagingTopoCluster** → `HcalEndcapPInsertImagingProtoClusters`
→ **CalorimeterClusterRecoCoG** → `…ClustersWithoutShapes`
→ **CalorimeterClusterShape** → **`HcalEndcapPInsertClusters`**

There is **no** `TrackClusterMergeSplitter` for the insert.

### LFHCAL

`LFHCALHits` + `EventHeader`
→ **CalorimeterHitDigi** → `LFHCALRawHits` (+ `…RawHitLinks`, `…RawHitAssociations`)
→ **CalorimeterHitReco** → `LFHCALRecHits`

*truth branch:* (`LFHCALRecHits`, `LFHCALRawHitLinks`) → **CalorimeterTruthClustering** → `LFHCALTruthProtoClusters`
→ **CalorimeterClusterRecoCoG** → `…TruthClustersWithoutShapes` → **CalorimeterClusterShape** → `LFHCALTruthClusters`

*reconstruction branch:* `LFHCALRecHits`
→ **CalorimeterIslandCluster** → `LFHCALIslandProtoClusters`
→ **CalorimeterClusterRecoCoG** → `LFHCALClustersWithoutShapes`
→ **CalorimeterClusterShape** → **`LFHCALClusters`**

*split/merge branch:* (`LFHCALTrackClusterMatches`, `LFHCALClusters`, `CalorimeterTrackProjections`)
→ **TrackClusterMergeSplitter** → `LFHCALSplitMergeProtoClusters` (+ `…TrackSplitMergeProtoClusterLinks`)
→ **CalorimeterClusterRecoCoG** → `…SplitMergeClustersWithoutShapes`
→ **CalorimeterClusterShape** → `LFHCALSplitMergeClusters`

## Stage 1 — Digitization (both detectors)

**Algorithm:** [`CalorimeterHitDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc)
— explained on the [BEMC page]({% link docs/eicrecon/detectors/bemc.md %}).
Both instances leave `readoutType` at the default `"simple"` (linear ADC).

| parameter | Insert | LFHCAL | meaning |
|---|---|---|---|
| `eRes` | `{}` | `{}` | no energy-resolution smearing |
| `tRes` | `0 ns` | `0 ns` | no time smearing |
| `capADC` | `32768` | `65536` | ADC counts at full scale |
| `capTime` | not set → `1000 ns` | `100` | time dynamic range (only logged) |
| `dyRangeADC` | `200 MeV` | `1 GeV` | energy at full ADC scale |
| `pedMeanADC` / `pedSigmaADC` | `10` / `2` | `50` / `10` | pedestal mean and noise sigma |
| `resolutionTDC` | `10 ps` | `10 ps` | TDC least count |
| `corrMeanScale` | `"1.0"` | `"1.0"` | per-hit correction expression |
| `readout` | `"HcalEndcapPInsertHits"` | `"LFHCALHits"` | readout name |
| `fields` | not set | `{"layerz"}` | cellID fields over which signals are summed before digitizing |

## Stage 2 — Hit reconstruction (both detectors)

**Algorithm:** [`CalorimeterHitReco`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc)
— as on the BEMC page.

| parameter | Insert | LFHCAL | meaning |
|---|---|---|---|
| `capADC` / `dyRangeADC` / `pedMeanADC` / `pedSigmaADC` / `resolutionTDC` | `32768` / `200 MeV` / `10` / `2` / `10 ps` | `65536` / `1 GeV` / `50` / `10` / `10 ps` | must match the digi values |
| `thresholdFactor` | `0.0` | `0.0` | unused |
| `thresholdValue` | `41.0` — *"0.25 MeV --> 0.25 / 200 * 32768 = 41"* | `20` — *"0.3 MeV deposition --> adc = 50 + 0.3 / 1000 * 65536 == 70"* (see caveat 6) | pedestal-subtracted ADC cut |
| `sampFrac` | `"1.0"` | `"(rlayerz == 0) ? 0.019 : 0.037"` — *"0.019 only in the 0-th tile"* | sampling fraction, compiled per hit with all cellID fields in scope |
| `readout` | `"HcalEndcapPInsertHits"` | `"LFHCALHits"` | readout name |
| `layerField` | `"layer"` | `"rlayerz"` | cellID field giving the layer index |
| `sectorField` | not set | not set | rec hits carry sector 0 |

The two detectors use **opposite conventions** for the sampling fraction: the
insert leaves it at 1.0 here and applies `0.0257` at cluster level, LFHCAL
applies a layer-dependent fraction here and uses `1.0` at cluster level.

## Stage 3 — Insert: hit merging

**Algorithm:** [`CalorimeterHitsMerger`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitsMerger.cc)
— mechanics described on the
[EHCAL page]({% link docs/eicrecon/detectors/ehcal.md %}).

| parameter | Insert value | meaning |
|---|---|---|
| `readout` | `"HcalEndcapPInsertHits"` | readout whose idSpec supplies the field names |
| `fieldTransformations` | `{"layer:1", "slice:0"}` | `layer` forced to 1, `slice` to 0 — all layers/slices of a tower summed into one hit positioned at layer 1 |

Only `CalorimeterTruthClustering` consumes these merged hits; the physics
branch works from the un-merged rec hits.

## Stage 4 — Insert: HEXPLIT sub-cell splitting

**Algorithm:** [`HEXPLIT`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc)
— *"An algorithm for splitting calorimeter hits in overlapping cells into
'subhits' based on the relative energies of hits on neighboring layers"*
(Sebouh Paul, 12/04/2023). New relative to BEMC, so in full.

In a staggered SiPM-on-tile geometry, consecutive layers are offset so that a
cell in one layer partially overlaps several cells in the neighbouring
layers. HEXPLIT exploits this: each hit is divided into `SUBCELLS` sub-hits
positioned at the overlap regions, and the parent hit's energy is distributed
among them in proportion to the energy seen in the corresponding neighbouring
cells. The effective transverse granularity improves without changing the
hardware.

Procedure ([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L105-L190)):

1. Drop hits with `E < Emin_in_MIPs × MIP` or `time > tmax`.
2. For every surviving hit, scan all other hits within ±2 layers (excluding
   the same layer) and within 2 side lengths in x / √3 in y. Distances are
   expressed **in units of the hexagon side length** taken from the hit's own
   `dimension.x / 2`, and a hit is assigned to neighbour position *k* if it
   falls within `tol = 0.1` side lengths of the ideal staggered position —
   *"Deviations could arise from rounding errors or from detector
   misalignment."*
3. Floor each neighbour energy at `delta_in_MIPs × MIP` so that empty
   neighbours still get a small weight.
4. Weight each sub-cell by the product of the energies of the neighbouring
   cells that overlap there (H4: 3 factors; H3: 2 factors; S2: 1 factor), and
   distribute the parent hit energy in proportion.
5. Place each sub-hit at the sub-cell centre in local coordinates and convert
   to global via the DD4hep volume manager (falling back to local coordinates
   with a warning if no transform is found).

Staggering patterns
([header](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.h#L52-L102)):

| `stag_type` | subcells | neighbour positions | overlap factors | status |
|---|---|---|---|---|
| `H4` (0, default) | 12 | 12 | 3 | hexagonal, 4-fold stagger |
| `H3` (1) | — | — | 2 | **not implemented** — `init()` logs *"H3 staggering not implemented yet in EICrecon"* |
| `S2` (2) | 4 | 4 | 1 | square, 2-fold stagger (used by the ZDC HCal) |

| parameter | struct default | Insert value | meaning |
|---|---|---|---|
| `MIP` | `472 keV` | `480 keV` | energy deposit of a minimum-ionizing particle in one cell |
| `Emin_in_MIPs` | `0.1` | `0.5` | minimum hit energy to be used, in MIPs |
| `delta_in_MIPs` | `0.01` | not set → `0.01` | floor applied to neighbour energies, in MIPs |
| `tmax` | `325 ns` | `162 ns` | *"150 ns + (z at front face)/(speed of light)"* |
| `stag_type` | `H4` | not set → `H4` | staggering pattern |

## Stage 5 — Insert: topological proto-clustering

**Algorithm:** [`ImagingTopoCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc)
— *"Topological Cell Clustering Algorithm for Imaging Calorimetry"*, as on
the BEMC page, but here run on sub-cell hits in **xy mode** with distances
given as **string expressions evaluated against DD4hep geometry constants**.

| parameter | struct default | Insert value | meaning |
|---|---|---|---|
| `neighbourLayersRange` | `1` | `1` | max layer-number difference for neighbours |
| `sameLayerMode` | `xy` | `xy` (explicit) | how same-layer neighbours are determined |
| `diffLayerMode` | `xy` | not set → `xy` | how cross-layer neighbours are determined |
| `sameLayerDistXY` | `{1 mm, 1 mm}` | `{"0.5 * max(HcalEndcapPInsertCellSizeLGRight, HcalEndcapPInsertCellSizeLGLeft)", "… * sin(pi / 3)"}` | same-layer (x, y) neighbour window — half a cell, hexagonally scaled in y |
| `diffLayerDistXY` | `{1 mm, 1 mm}` | same expressions with `0.25 *` | cross-layer (x, y) neighbour window |
| `sectorDist` | `1.0 cm` | `10.0 cm` | max global distance across sectors |
| `minClusterHitEdep` | `0` | `5.0 keV` | *"minimum hit energy to participate clustering"* |
| `minClusterCenterEdep` | `0` | `3.0 MeV` | *"minimum cluster center energy (to be considered as a seed for cluster)"* |
| `minClusterEdep` | `0.5 MeV` | `11.0 MeV` | *"minimum cluster energy (to save this cluster)"* |
| `minClusterNhits` | `10` | `100` | *"minimum number of hits (to save this cluster)"* — high, because HEXPLIT multiplies the hit count by 12 |

## Stage 6 — LFHCAL: island proto-clustering

**Algorithm:** [`CalorimeterIslandCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc)
— see the BEMC page. LFHCAL assembles its adjacency expression in the plugin
from tower indices
([source](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L221-L243)),
with the magic constants documented inline:

> *54 - number of modules in a row/column; 2 - number of towers in a module;
> sign for towerx and towery are \*negative\* to maintain linearity with global X and Y*

```
cellIdx = (54*2 - moduleIDx*2 - towerx)     cellIdy = (54*2 - moduleIDy*2 - towery)     cellIdz = rlayerz
dX = |Δ cellIdx|,  dY = |Δ cellIdy|,  dZ = |Δ cellIdz|
neighbor = (dX + dY + dZ == 1)                                  // face-sharing in 3-D
corner2D = (dZ==0 && dX==1 && dY==1) || (dY==0 && dX==1 && dZ==1) || (dX==0 && dY==1 && dZ==1)
adjacencyMatrix = neighbor || corner2D
```

i.e. face-adjacent towers **plus** the in-plane diagonals of each of the three
coordinate planes.

| parameter | LFHCAL value | meaning |
|---|---|---|
| `adjacencyMatrix` | expression above | 3-D tower adjacency incl. planar diagonals |
| `peakNeighbourhoodMatrix` | empty | (no separate local-maximum neighbourhood) |
| `readout` | `"LFHCALHits"` | readout supplying the tower fields |
| `sectorDist` | `0 cm` | no cross-sector neighbours |
| `localDistXY` … `dimScaledLocalDistXY` | all empty | metric criteria disabled |
| `splitCluster` | `false` | no splitting at local maxima |
| `minClusterHitEdep` | `1 MeV` | min hit energy to enter clustering |
| `minClusterCenterEdep` | `100.0 MeV` | min seed-hit energy |
| `transverseEnergyProfileMetric` | `"globalDistEtaPhi"` | metric for the splitting profile |
| `transverseEnergyProfileScale` | `1.0` | profile scale |

## Stage 7 — Truth proto-clustering (both detectors)

**Algorithm:** [`CalorimeterTruthClustering`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc)
(no configuration) — described on the
[EEMC page]({% link docs/eicrecon/detectors/eemc.md %}).
The insert instance runs on `HcalEndcapPInsertMergedHits`; the LFHCAL
instance runs on `LFHCALRecHits`.

## Stage 8 — Cluster reconstruction and shapes

[`CalorimeterClusterRecoCoG`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc)
+ [`CalorimeterClusterShape`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc),
both explained on the BEMC page.

| instance | `energyWeight` | `sampFrac` | `logWeightBase` | `enableEtaBounds` | `longitudinalShowerInfoAvailable` |
|---|---|---|---|---|---|
| `HcalEndcapPInsertTruthClustersWithoutShapes` | `log` | `0.0257` | `3.6` | **`true`** | — |
| `HcalEndcapPInsertTruthClusters` (shape) | `log` | default `1.0` | `3.6` | — | `true` |
| `HcalEndcapPInsertClustersWithoutShapes` | `log` | `0.0257` | `6.2` | `false` | — |
| `HcalEndcapPInsertClusters` (shape) | `log` | `0.0257` | `6.2` | — | `true` |
| `LFHCALTruthClustersWithoutShapes` | `log` | `1.0` | `4.5` | `false` | — |
| `LFHCALTruthClusters` (shape) | `log` | default `1.0` | `4.5` | — | `true` |
| `LFHCALClustersWithoutShapes` | `log` | `1.0` | `4.5` | `false` | — |
| `LFHCALClusters` (shape) | `log` | default `1.0` | `4.5` | — | `true` |
| `LFHCALSplitMergeClustersWithoutShapes` | `log` | `1.0` | `4.5` | `false` | — |
| `LFHCALSplitMergeClusters` (shape) | **not set → `"none"`** | default `1.0` | default `3.6` | — | `true` |

The shape config's `sampFrac` exists because *"if the fraction is applied
\*after\* clustering, this parameter can be used to determine the total energy
of the cluster before applying the fraction, which is a necessary input for
the log-weight calculation"*
([config struct](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShapeConfig.h#L19-L26)).
It is set on the insert's production shape instance but **not** on the
insert's truth shape instance (see caveat 4).

## Stage 9 — LFHCAL: track-driven merging and splitting

**Algorithm:** [`TrackClusterMergeSplitter`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc)
— procedure described on the
[EEMC page]({% link docs/eicrecon/detectors/eemc.md %}).

| parameter | struct default | LFHCAL value | meaning |
|---|---|---|---|
| `minSigCut` | `-1.0` | `-2.0` | *"any clusters below this will be merged"* |
| `avgEP` | `1.0` | `0.50` | *"average of E/p distribution"* |
| `sigEP` | `1.0` | `0.25` | *"RMS of E/p distribution"* |
| `drAdd` | `0.4` | `0.30` | *"window to merge clusters"* |
| `surfaceToUse` | `1` | `1` | *"index of surface to use for track projections"* |
| `transverseEnergyProfileScale` | `1.0` | `1.0` | *"scale for hit-track distance"* |

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L407-L420)):
`HcalEndcapPInsertRawHits`, `HcalEndcapPInsertRecHits`,
`HcalEndcapPInsertMergedHits`,
`HcalEndcapPInsertClusters(+Links/Associations)`, `LFHCALRawHits`,
`LFHCALRecHits`, `LFHCALClusters(+Links/Associations)`,
`LFHCALSplitMergeClusters(+Links/Associations)`, plus
`LFHCALTrackClusterMatches`, `ReconstructedLFHCALNeutrals` and the
particle-flow collections for both detectors
([L506-L518](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L506-L518)).

**Not persisted by default:** `HcalEndcapPInsertTruthClusters`,
`LFHCALTruthClusters`, `HcalEndcapPInsertSubcellHits`, all proto-cluster and
`…WithoutShapes` collections.

Downstream: `LFHCALClusters` is matched to track projections and is an input
to `FarForwardNeutralsReconstruction` → `ReconstructedLFHCALNeutrals`
([reco.cc](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L242-L250));
`HcalEndcapPInsertClusters` is matched to track projections
([reco.cc](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L214-L218)).
Neither enters the combined `EcalClusters` collection.

## Caveats / needs human verification

1. **The insert's `HcalEndcapPInsertClusterMatches` naming is inconsistent.**
   The factory tag is `"HcalEndcapPInsertClusterMatches"` but the output
   collection it produces is `"HcalEndcapPInsertTrackClusterMatches"`
   ([reco.cc](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L214-L218)),
   while the PODIO output list asks for `"HcalEndcapPInsertClusterMatches"`
   ([podio](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L479)).
   Every other detector's tag and collection name agree. Needs confirmation
   that the intended collection actually reaches the output file.
2. **The insert's `MergedHits` are only used by the truth branch.** They are
   produced and persisted, but the physics chain goes
   `RecHits → HEXPLIT → ImagingTopoCluster`. So the persisted "merged hits"
   describe a path that no reconstructed cluster came from.
3. **The two detectors apply the sampling fraction at different stages** —
   insert at cluster level (`0.0257`), LFHCAL at hit level
   (`0.019` / `0.037`). Neither value carries a provenance comment. The
   EHCAL plugin explicitly states the opposite preference
   (*"implement at level of reco hits rather than clusters"*).
4. `enableEtaBounds = true` on the insert's **truth** branch only, `false` on
   the production branch — the same asymmetry as FEMC. Similarly, the shape
   `sampFrac = 0.0257` is set on the insert's production shape instance but
   not on its truth shape instance, so the two log-weight calculations use
   different total-energy scales.
5. **`LFHCALSplitMergeClusters` gets no `energyWeight`.** Its shape factory is
   configured with `{.longitudinalShowerInfoAvailable = true}` only
   ([source](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L336-L341)),
   so `energyWeight` falls back to the struct default `"none"` and
   `logWeightBase` to `3.6` — different from the `log` / `4.5` used by every
   other LFHCAL instance. Looks unintentional.
6. **The LFHCAL threshold comment does not match the value.** The comment
   computes `adc = 50 + 0.3 / 1000 * 65536 == 70` but the configured value is
   `20`. `CalorimeterHitReco` compares against the **pedestal-subtracted**
   ADC, where 0.3 MeV ≈ 19.7 ADC — so `20` is right and the comment's
   pedestal term (and its stated result of 70) is wrong.
7. `HcalEndcapPInsertCellSizeLGRight` / `…Left` are DD4hep constants defined
   in the **`epic` geometry description**, not in EICrecon. Note also that
   the string-valued `sameLayerDistXY` / `diffLayerDistXY` do **not** appear
   in the CI flags dump (only the `…DistTZ` / `…DistEtaPhi` variants do), so
   these particular windows are not runtime-tunable through the usual flags.
8. `MIP = 480 keV`, `tmax = 162 ns`, `minClusterNhits = 100` and the LFHCAL
   magic constants `54` / `2` are hard-coded with no reference to the study
   or geometry version they came from.
9. HEXPLIT's `H3` staggering is selectable in the config enum but
   `init()` only logs an error and leaves `stag` at `H4` — a partially
   implemented option that fails silently at runtime rather than throwing.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
