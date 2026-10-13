---
title: ImagingTopoCluster
parent: EICrecon
nav_order: 33
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ImagingTopoCluster — topological cell clustering for imaging calorimetry

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

**Source:**
[`src/algorithms/calorimetry/ImagingTopoCluster.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.h) ·
[`.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc) ·
[`ImagingTopoClusterConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoClusterConfig.h) ·
factory [`ImagingTopoCluster_factory.h`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/ImagingTopoCluster_factory.h)

**Signature:** `edm4eic::CalorimeterHitCollection` →
`edm4eic::ProtoClusterCollection`
([`ImagingTopoCluster.h#L39-L52`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.h#L39-L52)).
No MC truth, no geometry service, no readout decoding — it works purely on
the reconstructed hit positions, energies, and the `layer` / `sector`
integers already attached to each `edm4eic::CalorimeterHit`.

The file header states its purpose and origin
([`ImagingTopoCluster.h#L4-L20`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.h#L4-L20)):

> *Topological Cell Clustering Algorithm for Imaging Calorimetry*
> *1. group all the adjacent pixels*
> *Author: Chao Peng (ANL), 06/02/2021*
> *Original reference: <https://arxiv.org/pdf/1603.02934.pdf>*

## What it does physically

A high-granularity imaging calorimeter records a shower as a cloud of small
energy deposits spread over many longitudinal layers. The physical object to
recover is the connected three-dimensional blob those deposits form: within a
layer the shower has a transverse footprint of order the Molière radius, and
from layer to layer the same shower reappears displaced slightly along the
particle's direction of flight. `ImagingTopoCluster` reconstructs that blob by
treating hits as nodes of a graph, joining two hits with an edge whenever they
are "close enough", and returning each connected component as a proto-cluster.

The essential design choice is that *closeness means something different
within a layer than across layers*
([`ImagingTopoCluster.cc#L283-L354`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc#L283-L354)).
Inside one layer the natural coordinates are the local pixel coordinates of
the sensor plane, and the natural scale is the pixel pitch. Across layers the
hits sit on different physical surfaces, so a local-coordinate comparison is
meaningless; what stays approximately constant along a shower is its angular
direction, or its global transverse offset. The algorithm therefore exposes
two independent metric selectors, `sameLayerMode` and `diffLayerMode`, and a
layer window `neighbourLayersRange` outside which no pair is ever joined.

Growth is seeded only from hits above `minClusterCenterEdep` and extended only
through hits above `minClusterHitEdep`, which is the usual seed/grow threshold
pair of topological clustering: a low grow threshold keeps the shower tails
attached, a high seed threshold prevents noise cells from nucleating clusters
of their own. At the end, a group survives only if it has at least
`minClusterNhits` hits and a total energy of at least `minClusterEdep`
([`ImagingTopoCluster.cc#L254-L270`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc#L254-L270)).
Every surviving hit enters the proto-cluster with weight exactly `1` — this
algorithm assigns hits, it does not share them fractionally and it does not
compute positions or energies. Those come later, from
`CalorimeterClusterRecoCoG` or `ImagingClusterReco`.

## Neighbour criteria

`is_neighbour(h1, h2)` is evaluated in this order
([`ImagingTopoCluster.cc#L274-L358`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc#L274-L358)):

1. **Different sector** — if `h1.getSector() != h2.getSector()`, the layer
   structure is abandoned entirely and the pair is joined when the plain 3D
   global distance `hypot(Δx, Δy, Δz)` is `<= sectorDist`
   ([`#L277-L281`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc#L277-L281)).
   This is what stitches a shower that straddles a sector boundary; note it
   applies regardless of how far apart the two layer indices are.
2. **Same sector, same layer** (`ldiff == 0`) — the `sameLayerMode` metric.
3. **Same sector, `0 < ldiff <= neighbourLayersRange`** — the `diffLayerMode`
   metric.
4. Otherwise not neighbours.

Both selectors take the same enum,
`ImagingTopoClusterConfig::ELayerMode { etaphi = 0, xy = 1, tz = 2, xyz = 3 }`
([`ImagingTopoClusterConfig.h#L39`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoClusterConfig.h#L39)),
and the streaming operators accept either the spelling or the integer
([`#L58-L94`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoClusterConfig.h#L58-L94)).
All four modes are supported on both sides, and each reads its own config
field — setting `sameLayerMode = tz` means `sameLayerDistTZ` is consulted and
the other three `sameLayerDist*` fields are ignored.

### Same-layer modes (`sameLayerMode`)

| mode | config field read | test applied |
|---|---|---|
| `xy` | `sameLayerDistXY` (2 values) | `\|Δlocal.x\| <= d0` and `\|Δlocal.y\| <= d1` |
| `xyz` | `sameLayerDistXYZ` (3 values) | `\|Δlocal.x\|`, `\|Δlocal.y\|`, `\|Δlocal.z\|` each within the corresponding limit |
| `etaphi` | `sameLayerDistEtaPhi` (2 values) | `\|Δη\| <= d0` and `\|Δφ\| <= d1` on **global** positions |
| `tz` | `sameLayerDistTZ` (2 values) | `\|Δt\| <= d0` and `\|Δz\| <= d1` on **global** positions |

([`ImagingTopoCluster.cc#L287-L319`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc#L287-L319))

The `tz` metric is specific to barrel-like geometries. The source comments it
as *"Layer mode 'tz' uses the average phi of the hits to define a rotated
direction. The coordinate is a distance, not an angle."*
([`#L304`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc#L304)).
Concretely, with `φ = ½(φ₁ + φ₂)`, each hit gets
`t = x·sin φ − y·cos φ`, the signed distance along the azimuthal tangent at
the pair's mean azimuth; `z` is used as-is. So `tz` is "arc-length-like
transverse separation, and separation along the beam" — a cylinder-friendly
substitute for local `xy` when the sensors are tiles wrapped around the beam
line.

### Cross-layer modes (`diffLayerMode`)

| mode | config field read | test applied |
|---|---|---|
| `etaphi` | `diffLayerDistEtaPhi` (2 values) | `\|Δη\|`, `\|Δφ\|` on global positions |
| `xy` | `diffLayerDistXY` (2 values) | `\|Δx\|`, `\|Δy\|` on **global** positions |
| `xyz` | `diffLayerDistXYZ` (3 values) | `\|Δx\|`, `\|Δy\|`, `\|Δz\|` on global positions |
| `tz` | `diffLayerDistTZ` (2 values) | rotated `t` and `z`, as above, on global positions |

([`ImagingTopoCluster.cc#L320-L354`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc#L320-L354))

Note the asymmetry between the two `xy` entries: same-layer `xy` uses
**local** coordinates, cross-layer `xy` uses **global** ones, with the source
comment *"the xy layer mode is based on global XY positions rather than local
XY positions, and thus it only works for endcap detectors"*
([`#L329`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc#L329)).
For an endcap stack the layers are parallel planes at different `z`, so global
`(x, y)` is exactly the right "same transverse spot, next plane" test.
`etaphi` is the projective equivalent for a barrel: a shower travelling
radially outward keeps its `(η, φ)` while its `(x, y, z)` change, so an
angular window is the correct cross-layer criterion there.

`init()` validates that the selected mode's vector has the right length and
throws otherwise, and logs the effective millimetre/radian values
([`ImagingTopoCluster.cc#L90-L183`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc#L90-L183)).
It also refuses to start if `minClusterCenterEdep < minClusterHitEdep`
([`#L53-L58`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc#L53-L58)).

## Group growing (flood fill)

`process()` first builds a `std::set` of hit indices ordered by layer, with
the object index as tie-breaker
([`ImagingTopoCluster.cc#L192-L206`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc#L192-L206));
the set holds exactly those hits **not yet assigned** to any group, so hits
leave the pool as they are consumed. It then sweeps the pool
([`#L219-L239`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc#L219-L239)):

- A hit below `minClusterCenterEdep` is skipped (left in the pool — it can
  still be absorbed later as a non-seed member of somebody else's group).
- A hit at or above the seed threshold starts a new group and is handed to
  `bfs_group`.
- After the flood fill returns, the seed itself is erased from the pool.

`bfs_group`
([`ImagingTopoCluster.h#L79-L116`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.h#L79-L116))
is a breadth-first flood fill written as a single loop over a `std::list` that
grows while it is being iterated: for each member already in the group it
scans the remaining pool, moves every `is_neighbour` hit into the group, and
because the new member is appended to the same list the scan will later be
repeated from it. The recursion therefore terminates when a full pass adds
nothing. Hits below `minClusterHitEdep` are *erased from the pool outright*
during the scan ([`#L103-L106`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.h#L103-L106))
— they are permanently removed from consideration for all later groups too,
which is the intended optimisation described in the modification log.

Because groups are grown to exhaustion and never split, two overlapping
showers that share even one bridging hit come out as one proto-cluster. There
is no local-maximum splitting stage in this algorithm.

## Configuration

`ImagingTopoClusterConfig`
([full struct](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoClusterConfig.h#L14-L56)).
Distances are stored in DD4hep units and divided by `dd4hep::mm` (energies by
`dd4hep::GeV`) in `init()`, so the numbers below are the effective values.

| field | struct default | meaning |
|---|---|---|
| `neighbourLayersRange` | `1` | max `\|Δlayer\|` for two same-sector hits to be considered at all |
| `sameLayerDistXY` | `{1 mm, 1 mm}` | local (x, y) window, used only when `sameLayerMode == xy` |
| `sameLayerDistXYZ` | `{1 mm, 1 mm, 20 mm}` | local (x, y, z) window, used only when `sameLayerMode == xyz` |
| `sameLayerDistEtaPhi` | `{0.01, 0.01}` | global (η, φ) window (second value in rad), used only when `sameLayerMode == etaphi` |
| `sameLayerDistTZ` | `{1 mm, 1 mm}` | global (t, z) window, used only when `sameLayerMode == tz` |
| `diffLayerDistXY` | `{1 mm, 1 mm}` | global (x, y) window, used only when `diffLayerMode == xy` |
| `diffLayerDistXYZ` | `{1 mm, 1 mm, 20 mm}` | global (x, y, z) window, used only when `diffLayerMode == xyz` |
| `diffLayerDistEtaPhi` | `{0.01, 0.01}` | global (η, φ) window (second value in rad), used only when `diffLayerMode == etaphi` |
| `diffLayerDistTZ` | `{1 mm, 1 mm}` | global (t, z) window, used only when `diffLayerMode == tz` |
| `sameLayerMode` | `ELayerMode::xy` | metric for `ldiff == 0` |
| `diffLayerMode` | `ELayerMode::xy` | metric for `0 < ldiff <= neighbourLayersRange` |
| `sectorDist` | `1 cm` | max 3D global distance for hits in *different* sectors |
| `minClusterHitEdep` | `0.` | min hit energy to participate in clustering at all |
| `minClusterCenterEdep` | `0.` | min hit energy to seed a new group |
| `minClusterEdep` | `0.5 MeV` | min summed group energy to emit a proto-cluster |
| `minClusterNhits` | `10` | min number of hits to emit a proto-cluster |

The `*DistXY` / `*DistXYZ` fields are
`std::vector<std::variant<std::string, double>>`, so a detector plugin may
pass a **DD4hep expression string** instead of a number — FHCAL does exactly
that, e.g. `"0.5 * max(HcalEndcapPInsertCellSizeLGRight, …)"`, evaluated by
`dd4hep::_toDouble` at `init()`
([`ImagingTopoCluster.cc#L46-L74`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc#L46-L74)).
The `*DistEtaPhi` / `*DistTZ` fields are plain `std::vector<double>`.

{: .note }
Not every field is settable at runtime. In the JANA factory the
`ParameterRef`s for `sameLayerDistXY`, `diffLayerDistXY`, `sameLayerDistXYZ`
and `diffLayerDistXYZ` are **commented out**
([`ImagingTopoCluster_factory.h#L24-L37`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/ImagingTopoCluster_factory.h#L24-L37));
only the EtaPhi and TZ distances, both mode selectors,
`neighbourLayersRange`, `sectorDist` and the four `minCluster*` values are
exposed as `-P<prefix>:<field>` flags.

## How it differs from island clustering

[`CalorimeterIslandCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc)
joins hits with a *single* adjacency rule for every pair — one of
`localDistXY / localDistXZ / localDistYZ / globalDistRPhi / globalDistEtaPhi`,
or a compiled `adjacencyMatrix` expression — and can then split a group at its
local energy maxima (`splitCluster`). It is effectively a 2D-surface notion of
adjacency.

`ImagingTopoCluster` instead makes the layer index a first-class concept: it
uses one metric for hits sharing a layer and a *different* metric, with a
*different* scale, for hits up to `neighbourLayersRange` layers apart, plus a
third plain-3D rule across sectors. That is what makes it appropriate for a
finely segmented imaging stack, where the transverse pixel pitch is far
smaller than the layer-to-layer spacing and the two directions genuinely need
different tolerances. The trade-off is that it has no splitting stage at all,
so two nearby showers are merged rather than separated.

{: .note }
Despite the name, it is not restricted to pixel imaging layers. The BEMC runs
a second instance directly on the **ScFi** (scintillating-fibre) rec hits
using `xyz` on both sides with an 80 × 80 × 40 mm window
([`BEMC.cc#L319-L337`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L319-L337)),
and the ZDC and forward-insert HCal use it on HEXPLIT sub-cell hits from a
tiled scintillator readout.

## Which detectors use it

Four instances, in three plugins.

| plugin | instance name | input → output | key settings |
|---|---|---|---|
| [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L413-L429) | `EcalBarrelImagingProtoClusters` | `EcalBarrelImagingRecHits` → `EcalBarrelImagingProtoClusters` | `sameLayerMode=tz` `{2 mm, 2 mm}`, `diffLayerMode=etaphi` `{10 mrad, 10 mrad}`, `neighbourLayersRange=2`, `sectorDist=3 cm`, `minClusterEdep=100 MeV`, `minClusterNhits=10` |
| [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L319-L337) | `EcalBarrelScFiProtoTopoClusters` | `EcalBarrelScFiRecHits` → `EcalBarrelScFiProtoTopoClusters` | `sameLayerMode=diffLayerMode=xyz` `{80, 80, 40} mm`, `neighbourLayersRange=2`, `sectorDist=5 cm`, `minClusterEdep=100 MeV`, `minClusterNhits=10` |
| [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L98-L120) | `HcalEndcapPInsertImagingProtoClusters` | `HcalEndcapPInsertSubcellHits` → `HcalEndcapPInsertImagingProtoClusters` | `sameLayerMode=xy` with expression-valued distances built from the DD4hep cell size (`diffLayerMode` **not set** → default `xy`), `neighbourLayersRange=1`, `sectorDist=10 cm`, `minClusterHitEdep=5 keV`, `minClusterCenterEdep=3 MeV`, `minClusterEdep=11 MeV`, `minClusterNhits=100` |
| [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L190-L206) | `HcalFarForwardZDCImagingProtoClusters` | `HcalFarForwardZDCSubcellHits` → `HcalFarForwardZDCImagingProtoClusters` | `sameLayerMode=diffLayerMode=xy` at `0.75 × 48.8 mm`, `neighbourLayersRange=1`, `sectorDist=10 cm`, `minClusterHitEdep=315 keV`, `minClusterCenterEdep=25 MeV`, `minClusterEdep=50 MeV`, `minClusterNhits=10` |

Downstream, every one of these proto-cluster collections is consumed by
`CalorimeterClusterRecoCoG` (or, for `EcalBarrelImagingProtoClusters`, by
`ImagingClusterReco`) and then by `CalorimeterClusterShape`. In FHCAL and ZDC
the ImagingTopoCluster output is the **default** cluster path — it produces
`HcalEndcapPInsertClusters` and `HcalFarForwardZDCClusters`, the collections
that are written out and used downstream — not a side study.

## Caveats / needs human verification

1. The `sameLayerDistXY` comment in the config header says *"maximum distance
   of global (x, y)"*
   ([`ImagingTopoClusterConfig.h#L18`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoClusterConfig.h#L18)),
   but the same-layer `xy` branch compares `getLocal()`
   ([`ImagingTopoCluster.cc#L289-L290`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc#L289-L290)),
   and the `init()` log line agrees with the code by printing "Local [x, y]".
   The header comment appears to be stale; the code is local.
2. All `etaphi` comparisons use a bare subtraction of azimuthal angles with
   **no ±π wrap-around**
   ([`#L300-L301`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc#L300-L301),
   [`#L325-L326`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc#L325-L326)).
   Hits straddling the φ = ±π seam will not be joined by an `etaphi`
   criterion. Whether the sector rule rescues those cases in practice is not
   determinable from the source.
3. The cross-sector branch runs *before* any layer check, so two hits in
   different sectors are joined on 3D distance alone even if their layer
   indices differ by far more than `neighbourLayersRange`. This looks
   deliberate but is nowhere justified in a comment.
4. `bfs_group` contains a commented-out early `break` that would exploit the
   layer-sorted pool to stop scanning once past the relevant layers
   ([`ImagingTopoCluster.h#L97-L100`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.h#L97-L100)).
   With it disabled, every flood-fill step scans the whole remaining pool;
   the reason it is disabled is not recorded.
5. The cited reference (arXiv:1603.02934) defines topological clustering in
   terms of cell-noise *significance* thresholds (4-2-0 style). This
   implementation uses plain absolute energy thresholds
   (`minClusterHitEdep`, `minClusterCenterEdep`) with no noise-sigma input,
   so it is an adaptation rather than a reimplementation of the reference.
6. The BEMC ScFi instance sets both `minClusterHitEdep` and
   `minClusterCenterEdep` to `0`, which means every single rec hit is a valid
   seed. Combined with the 80 mm windows this makes the ScFi topo branch far
   more permissive than the island branch on the same hits; whether that is
   tuned or provisional is not stated.
7. `neighbourLayersRange` is an `int` compared against
   `std::abs(h1.getLayer() - h2.getLayer())`; the hit `layer` field is
   whatever the readout's `layerField` produced in `CalorimeterHitReco`, so
   its meaning (and therefore the right value of the range) is a property of
   the `epic` geometry description, not of EICrecon.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
(fetched 2026-08-19). AI-authored draft — verify against source.*
