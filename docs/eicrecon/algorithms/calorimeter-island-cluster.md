---
title: CalorimeterIslandCluster
parent: EICrecon
nav_order: 32
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# CalorimeterIslandCluster — island (nearest-neighbour) proto-clustering

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

`CalorimeterIslandCluster` is EICrecon's workhorse proto-clusteriser for
calorimeters with a regular cell structure. It takes a flat collection of
calibrated `edm4eic::CalorimeterHit`s and returns
`edm4eic::ProtoCluster`s — connected "islands" of hits that touch each other
under a configurable adjacency rule. The physical picture is the one the
name suggests: an electromagnetic or hadronic shower deposits energy in a
contiguous patch of cells, patches separated by empty cells belong to
different particles, and a patch with more than one energy peak may be two
overlapping showers that should be pulled apart. The algorithm makes no
attempt to compute an energy or a position — that is
[`CalorimeterClusterRecoCoG`](calorimeter-cluster-reco-cog.html)'s job. It
only decides *which hits belong together*, and, when splitting is enabled,
*with what fractional weight*.

The source header cites two references
([`CalorimeterIslandCluster.cc#L4-L6`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L4-L6)):
the [CERN note on the island algorithm](https://cds.cern.ch/record/687345/files/note01_034.pdf)
and a [PrimEx-II talk](https://www.jlab.org/primex/weekly_meetings/primexII/slides_2012_01_20/island_algorithm.pdf).
The algorithm's own one-line runtime description is simply *"Island
clustering."*
([`CalorimeterIslandCluster.h#L42`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.h#L42)).

## What a protocluster is

`edm4eic::ProtoCluster` is a bag of references to `edm4eic::CalorimeterHit`
plus a **parallel vector of float weights**, one per hit. It carries no
energy, position or time of its own. A weight of `1.0` means "this hit
belongs entirely to this protocluster"; a fractional weight means the hit's
energy is shared with another protocluster that overlaps it. Downstream,
`CalorimeterClusterRecoCoG` sums `E_hit · w` over the protocluster to get the
cluster energy, so the weights are what makes cluster splitting energy
conserving. In this algorithm the protocluster is built with
`protoClusters->create()` followed by `addToHits` / `addToWeights`
([`#L344-L406`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L344-L406)).

## Inputs and outputs

Declared in
[`CalorimeterIslandCluster.h#L30-L42`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.h#L30-L42):

| slot | declared name | actual type |
|---|---|---|
| in | `inputProtoClusterCollection` | `edm4eic::CalorimeterHitCollection` |
| out | `outputClusterCollection` | `edm4eic::ProtoClusterCollection` |

{: .note }
The two slot names are wrong — the input is *rec hits*, not protoclusters,
and the output is *protoclusters*, not clusters. Only the types are
authoritative. See caveats.

## Step 1 — the adjacency (neighbour) criterion

Everything hinges on a single predicate,
`is_neighbour(h1, h2) -> bool`
([`.h#L61`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.h#L61)).
`init()` builds it in one of two mutually exclusive ways, and the choice is
made in a fixed priority order
([`.cc#L159-L193`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L159-L193)).

### 1a. String expression over cellID fields (`adjacencyMatrix`)

If `adjacencyMatrix` is a non-empty string it **wins outright** and no
coordinate method is even considered
([`#L162-L166`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L162-L166)).
The string is compiled to a native `std::function` by
[`EvaluatorSvc`](https://github.com/eic/EICrecon/blob/main/src/services/evaluator/EvaluatorSvc.h)
(a ROOT `TInterpreter` front end). The variables in scope are every field of
the readout's `IDDescriptor`, suffixed `_1` and `_2` for the two hits
([`#L136-L148`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L136-L148)) —
so a segmentation with fields `row`, `column`, `sector` gives you `row_1`,
`row_2`, `column_1`, … The expression must evaluate to a double that is
treated as a boolean. Because the field names come from the readout, setting
`adjacencyMatrix` (or `peakNeighbourhoodMatrix`) **requires** `readout`; the
algorithm throws otherwise
([`#L150-L157`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L150-L157)).

Real examples from the detector plugins:

- EEMC: `"(abs(row_1 - row_2) + abs(column_1 - column_2)) == 1"` — strict
  4-connectivity on a square grid
  ([`EEMC.cc#L87`](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L87)).
- BHCAL: vertical `eta` adjacency, horizontal `phi` adjacency, **plus** the
  φ wraparound term `abs(phi_1 - phi_2) == (320 - 1)` that closes the barrel
  ring of 320 tiles
  ([`BHCAL.cc#L41-L49`](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L41-L49)).
- LFHCAL: face-adjacency in the 3-D (x, y, layer) tower index *or* a 2-D
  corner touch, assembled from `moduleIDx`/`towerx`/`rlayerz` arithmetic
  ([`FHCAL.cc#L225-L243`](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L225-L243)).
- LumiSpecCAL: `sector_1 == sector_2` combined with a decoded 2-digit module
  index
  ([`LUMISPECCAL.cc#L67-L69`](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L67-L69)).

### 1b. Coordinate distance measures

If `adjacencyMatrix` is empty, `init()` walks a **fixed, ordered list** of
six two-component distance measures and takes the **first one whose config
vector is non-empty**
([`#L125-L132`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L125-L132)):

| order | config field | what the measure returns | unit constants |
|---|---|---|---|
| 1 | `localDistXY` | (Δx, Δy) of `getLocal()` | mm, mm |
| 2 | `localDistXZ` | (Δx, Δz) of `getLocal()` | mm, mm |
| 3 | `localDistYZ` | (Δy, Δz) of `getLocal()` | mm, mm |
| 4 | `globalDistRPhi` | (Δ\|r\|, Δφ) of the global position, φ wrapped to ±π | mm, rad |
| 5 | `globalDistEtaPhi` | (Δη, Δφ) of the global position | 1, rad |
| 6 | `dimScaledLocalDistXY` | (2Δx/(w₁ₓ+w₂ₓ), 2Δy/(w₁ᵧ+w₂ᵧ)) — local Δ divided by the mean cell size | 1, 1 |

The measures themselves are plain free functions
([`#L45-L77`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L45-L77));
the unit constants come from the `distMethods` table
([`#L94-L102`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L94-L102)).
Which one to use is a statement about the cell geometry: `localDistXY` for a
flat tower face, `localDistXZ` for the BEMC ScFi where the interesting
segmentation is (x, z), `globalDistEtaPhi` for projective towers, and
`dimScaledLocalDistXY` when cell sizes vary across the detector and you want
the criterion expressed in *cells* rather than millimetres (a value of
`{1.5, 1.5}` then means "up to one and a half cell pitches away").

Selection mechanics and failure modes
([`#L105-L123`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L105-L123)):

- **Several configured**: no error, no warning — the one earliest in the
  table above silently wins. The source comment on the list only notes
  *"default one should be the last one"*.
- **Wrong length**: a vector whose size is not 2 produces
  `"Expect 2 values from <name>, received N. ignored it."` and the search
  moves on.
- **None configured and no `adjacencyMatrix`**: the algorithm throws
  `"Cannot determine the clustering coordinates"`
  ([`#L191-L193`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L191-L193)).
- Each configured value is divided by its unit constant so that it can be
  compared directly against EDM4hep numbers (mm for lengths, rad for
  angles): `neighbourDist[i] = value[i] / units[i]`.

`localDistXY` is special: it is typed
`std::vector<std::variant<std::string, double>>`, so its two entries may be
**DD4hep constant expressions** resolved through `dd4hep::_toDouble` at
`init()` time
([`#L84-L92`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L84-L92)).
The ZDC HCal uses this to tie the clustering distance to the geometry:
`"0.55 * HcalFarForwardZDC_SiPMonTile_SquareSideLength"`
([`ZDC.cc#L215-L216`](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L215-L216)).
It is also the only distance field whose entries are read only when exactly
two are given.

### 1c. Transverse vs. sector: `sectorDist`

The coordinate branch wraps the chosen 2-D measure in a sector guard
([`#L174-L184`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L174-L184)):

```
if (h1.sector == h2.sector)
    neighbours  <=>  |d.a| <= neighbourDist[0]  &&  |d.b| <= neighbourDist[1]
else
    neighbours  <=>  |x1 - x2|_3D <= sectorDist        (full 3-D global distance)
```

The reason is stated in the source: local coordinates are defined per
sector, and a sector may be rotated relative to its neighbour (the barrel
case), so a local Δ across a sector boundary is meaningless. Across the
boundary the algorithm therefore falls back to a plain 3-D global distance,
including z, with its own threshold `sectorDist`. Setting `sectorDist = 0`
(LFHCAL, LumiSpecCAL) effectively disables cross-sector merging.

{: .warning }
`sectorDist` is **only** consulted in the coordinate branch. When
`adjacencyMatrix` is set, `is_neighbour` is replaced wholesale by the
compiled expression and the sector fallback disappears — cross-sector
adjacency must then be written into the expression itself (as LumiSpecCAL
does with `sector_1 == sector_2`), even though every such plugin still
passes a `sectorDist` value.

## Step 2 — grouping (breadth-first flood fill)

`process()` sweeps the hit collection and, for every not-yet-visited hit,
starts a new group and flood-fills it with `bfs_group`
([`#L222-L291`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L222-L291)).
The fill repeats "for every hit already in the group, add every unvisited
hit that `is_neighbour` of it" until the group stops growing, so the group is
the full transitive closure of the adjacency relation — an *island*. Because
`visits[]` is global to the event, every hit ends up in at most one group.

## Step 3 — the two energy thresholds

The algorithm has two distinct and often-confused cuts:

- **`minClusterHitEdep`** — the *hit* threshold. A hit below it is marked
  visited and is never inserted into any group, either as a seed
  ([`#L266-L272`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L266-L272))
  or as a neighbour
  ([`#L281-L283`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L281-L283)).
  Physically it suppresses noise cells and stops a shower from leaking into
  a neighbouring one through a chain of near-empty cells.
- **`minClusterCenterEdep`** — the *seed* threshold, applied in
  `find_maxima`
  ([`#L294-L340`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L294-L340)).
  A hit can only be a cluster centre if it reaches this energy. This is not
  a per-hit filter: if **no** hit in an island reaches it, `find_maxima`
  returns nothing, `split_group` logs *"No maxima found, not building any
  clusters"* and **the entire island is discarded**. It is therefore the de
  facto minimum-cluster-energy cut of the algorithm.

## Step 4 — one cluster, or splitting at local maxima

`find_maxima` runs in one of two modes, selected by `!splitCluster`
([`#L254`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L254)):

**`splitCluster = false` (global mode).** Only the single highest-energy hit
of the island is considered. If it passes `minClusterCenterEdep`, one
protocluster is emitted containing every hit of the island with weight
`1.0`; otherwise nothing is emitted.

**`splitCluster = true` (local-maxima mode).** Every hit above
`minClusterCenterEdep` that has no *strictly* higher-energy hit inside its
peak neighbourhood is a local maximum
([`#L315-L337`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L315-L337)).
The peak neighbourhood is a **separate** predicate,
`is_maximum_neighbourhood`: it is compiled from `peakNeighbourhoodMatrix` if
that string is set, and otherwise falls back to `is_neighbour`
([`#L195-L201`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L195-L201)).
The distinction matters: EEMC groups with 4-connectivity but searches for
peaks over the wider 8-connected neighbourhood
(`max(abs(row_1 - row_2), abs(column_1 - column_2)) == 1`), so that a
diagonal pair of cells cannot both be declared maxima.

### Weight sharing between maxima

With *n* > 1 maxima, `split_group` creates *n* protoclusters and assigns
**every hit of the island to every maximum** with a fractional weight
([`#L364-L404`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L364-L404)).
For hit *i* and maximum *c*:

```
w_c = E_c · exp( −|M(c, i)| · U / transverseEnergyProfileScale )
```

where `M` is the metric named by `transverseEnergyProfileMetric`, `|·|` is
the magnitude of the returned 2-vector, and `U` is that metric's unit
constant (so the exponent is dimensionless and `transverseEnergyProfileScale`
is given in DD4hep units). The weight is thus **the peak energy times an
exponentially falling transverse shower profile** — a hit far from a peak, or
near a weak peak, gets little of its energy. The weights are then

1. normalised to sum to 1,
2. truncated: anything below `0.02` is set to zero,
3. re-normalised,
4. and hits whose weight is `<= 1e-6` are simply not added to that
   protocluster.

Energy is conserved by construction, since the weights over the maxima sum to
one for every hit. A source `TODO` notes that iterating the profile, or an ML
split, could replace this
([`#L365`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L365)).

`transverseEnergyProfileMetric` is looked up in the same `distMethods` table
as the adjacency measures and is validated at `init()`
([`#L203-L218`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L203-L218)):
an unknown name throws `Unsupported value "…"`, and a metric whose two
components carry *different* unit constants throws
`Metric … has incompatible dimension units`. That second check rules out
`globalDistRPhi` (mm vs rad), while `globalDistEtaPhi` passes because
DD4hep's `rad` and the dimensionless `1.` are numerically equal. Note that
this validation only runs when `splitCluster` is true — a nonsense metric
name is silently ignored otherwise.

## Configuration

Every field of
[`CalorimeterIslandClusterConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandClusterConfig.h):

| field | struct default | meaning |
|---|---|---|
| `adjacencyMatrix` | *(none — empty string)* | expression over readout fields (`row_1`, `row_2`, …) deciding adjacency; overrides all distance measures |
| `peakNeighbourhoodMatrix` | *(none — empty string)* | expression deciding which hits compete for "is a local maximum"; defaults to the adjacency predicate |
| `readout` | *(none — empty string)* | readout name whose `IDDescriptor` supplies the field names; mandatory if either matrix is set |
| `sectorDist` | *(none — 0)* | max 3-D global distance for hits in **different** sectors; ignored when `adjacencyMatrix` is used |
| `localDistXY` | *(none — empty)* | (Δx, Δy) window in local coordinates; entries may be numbers **or** DD4hep constant expressions |
| `localDistXZ` | *(none — empty)* | (Δx, Δz) window in local coordinates |
| `localDistYZ` | *(none — empty)* | (Δy, Δz) window in local coordinates |
| `globalDistRPhi` | *(none — empty)* | (Δr, Δφ) window in global coordinates |
| `globalDistEtaPhi` | *(none — empty)* | (Δη, Δφ) window in global coordinates |
| `dimScaledLocalDistXY` | *(none — empty)* | (Δx, Δy) in units of the mean cell size of the two hits |
| `splitCluster` | `false` | split an island at each local maximum instead of emitting one protocluster |
| `minClusterHitEdep` | *(none — 0)* | hit energy below which a hit never joins any island |
| `minClusterCenterEdep` | *(none — 0)* | minimum energy of a cluster seed; an island with no such hit is dropped entirely |
| `transverseEnergyProfileMetric` | *(none — empty string)* | name of the distance measure used in the splitting weight; validated only when `splitCluster` is true |
| `transverseEnergyProfileScale` | *(none — 0)* | decay constant of the exponential profile, in DD4hep units of the chosen metric |
| `transverseEnergyProfileScaleUnits` | *(none — 0)* | **never read** — see caveats |

{: .note }
The config struct declares no in-class initialisers except
`splitCluster{false}`, so there are no meaningful "library defaults": every
call site uses designated aggregate initialisation, which value-initialises
the omitted members to `0` / empty. Read the per-detector values below as the
real defaults.

Runtime flags are declared in
[`CalorimeterIslandCluster_factory.h#L23-L42`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/CalorimeterIslandCluster_factory.h#L23-L42),
as `<PLUGIN>:<InstanceName>:<flag>`. Note that `readout` is exposed under the
flag name **`readoutClass`**, and that `localDistXY` (commented out because of
its `std::variant` type), `peakNeighbourhoodMatrix` and
`transverseEnergyProfileScaleUnits` are **not** exposed at all — they can only
be changed in C++.

## Which detectors use it

Eleven instances across nine plugins (`grep -rn CalorimeterIslandCluster
src/detectors/`). "TEP" = transverse energy profile.

| plugin | instance (output) | input | adjacency | split | hit / seed Edep | sectorDist | TEP metric, scale |
|---|---|---|---|---|---|---|---|
| [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L277-L298) | `EcalBarrelScFiProtoClusters` | `EcalBarrelScFiRecHits` | `localDistXZ = {80 mm, 80 mm}` | no | 5 / 100 MeV | 50 mm | — |
| [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L84-L105) | `EcalEndcapNIslandProtoClusters` | `EcalEndcapNRecHits` | matrix, 4-connected `row`/`column`; peak matrix 8-connected | **yes** | 1 / 30 MeV | 5 cm | `globalDistEtaPhi`, 0.08 |
| [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L144-L163) | `EcalEndcapPIslandProtoClusters` | `EcalEndcapPRecHits` | `dimScaledLocalDistXY = {1.5, 1.5}` | no | 0 / 60 MeV | 5 cm | `dimScaledLocalDistXY`, 1 |
| [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L62-L82) | `B0ECalIslandProtoClusters` | `B0ECalRecHits` | `dimScaledLocalDistXY = {1.8, 1.8}` | no | 1 / 30 MeV | 5 cm | `globalDistEtaPhi`, 1 |
| [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L104-L123) | `HcalBarrelIslandProtoClusters` | `HcalBarrelRecHits` | matrix on `eta`/`phi` tiles incl. φ wraparound (320) | no | 5 / 30 MeV | 5 cm | `globalDistEtaPhi`, 1 |
| [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L82-L104) | `HcalEndcapNIslandProtoClusters` | `HcalEndcapNMergedHits` | `localDistXY = {15 cm, 15 cm}` | **yes** | 0 / 30 MeV | 5 cm | `globalDistEtaPhi`, 1 |
| [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L240-L261) | `LFHCALIslandProtoClusters` | `LFHCALRecHits` | matrix: 3-D tower face-adjacency **or** 2-D corner touch | no | 1 / 100 MeV | 0 | `globalDistEtaPhi`, 1 |
| [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L69-L91) | `EcalFarForwardZDCIslandProtoClusters` | `EcalFarForwardZDCRecHits` | `localDistXY = {50 cm, 50 cm}` | **yes** | 0.1 / 3 MeV | 5 cm | `globalDistEtaPhi`, 1 |
| [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L208-L228) | `HcalFarForwardZDCIslandProtoClusters` | `HcalFarForwardZDCSubcellHits` ([HEXPLIT](hexplit.html)) | `localDistXY = {"0.55 * HcalFarForwardZDC_SiPMonTile_SquareSideLength", ×2}` | no | 100 keV / 1 MeV | 1.5 cm | — |
| [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L267-L287) | `HcalFarForwardZDCIslandProtoClustersBaseline` | `HcalFarForwardZDCRecHits` | `localDistXY = {50 cm, 50 cm}` | **yes** | 0.1 / 3 MeV | 5 cm | `globalDistEtaPhi`, 1 |
| [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L63-L87) | `EcalLumiSpecIslandProtoClusters` | `EcalLumiSpecRecHits` | matrix on `sector` + decoded `module` | **yes** | 1 / 30 MeV | 0 | `localDistXY`, 10 mm |

Patterns worth noting: the four detectors with a genuinely irregular or
index-only cell map (EEMC, BHCAL, LFHCAL, LumiSpecCAL) all use string
expressions rather than distances; splitting is on in five of eleven
instances; and the ZDC HCal runs island clustering twice, once on
HEXPLIT subcell hits and once on the raw rec hits as a labelled *baseline*
([`ZDC.cc#L266`](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L266)).

## Caveats / needs human verification

1. **The I/O slot names are wrong.** The input is declared
   `"inputProtoClusterCollection"` and the output `"outputClusterCollection"`
   ([`.h#L40-L41`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.h#L40-L41)),
   while the actual types are hits in, protoclusters out. Cosmetic today
   (JANA binds by position), but confusing in logs.
2. **Silent priority among distance measures.** Configuring two of them is
   not an error; the earlier entry in the hard-coded list wins with no
   warning.
3. **`sectorDist` is dead whenever `adjacencyMatrix` is set** — yet all four
   matrix-configured plugins still pass a value (5 cm, 5 cm, 0, 0). Worth
   confirming with a maintainer that no cross-sector merging is intended
   there.
4. **`m_cfg.transverseEnergyProfileScaleUnits` is never read.** `init()`
   writes the *class member* of the same name from the metric's unit table
   ([`#L218`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L218)),
   shadowing the config field. Every plugin leaves the config field empty, so
   nothing breaks, but it is a trap.
   `CalorimeterIslandCluster::u_transverseEnergyProfileScale`
   ([`.h#L57`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.h#L57))
   is likewise declared and never used.
5. **Tie-breaking between equal-energy maxima.** The local-maximum test uses
   a strict `>` comparison, so two adjacent cells with *exactly* equal energy
   are both declared maxima and the island is split. Rare with floats, but
   possible with quantised ADC-derived energies.
6. **Weight cut constants are hard-coded**: the `0.02` truncation and the
   `1e-6` drop threshold in `split_group` are not configurable.
7. The `bfs_group` inner loop is O(N²) per iteration over the whole hit
   collection, and the outer `while` repeats until convergence — fine for
   calorimeter occupancies, but it is not a spatial-index implementation.
8. `find_maxima` and the splitting profile assume the *transverse* metric is
   meaningful for the detector; for the longitudinally segmented LFHCAL the
   configured `globalDistEtaPhi` is never exercised because
   `splitCluster = false`.
9. A source `TODO` above `split_group` reads *"confirm protoclustering
   without protoclustercollection"*
   ([`#L343`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc#L343));
   its intent is not determinable from the code.
10. All cellID field names (`row`, `column`, `eta`, `phi`, `moduleIDx`,
    `rlayerz`, `module`, …) and the geometry constant
    `HcalFarForwardZDC_SiPMonTile_SquareSideLength` live in the **`epic`
    geometry description**, not in EICrecon. An expression is only as valid
    as the readout it was written against.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
(fetched 2026-08-19). AI-authored draft — verify against source.*
