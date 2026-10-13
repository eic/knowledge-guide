---
title: HEXPLIT
parent: EICrecon
nav_order: 36
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# HEXPLIT — subcell splitting for staggered-tile calorimeters

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

`HEXPLIT` recovers transverse position information that a coarse
SiPM-on-tile calorimeter appears, at first sight, not to have. Its header
comment
([`HEXPLIT.h#L4-L8`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.h#L4-L8)):

*"An algorithm for splitting calorimeter hits in overlapping cells into
'subhits' based on the relative energies of hits on neighboring layers.
Author: Sebouh Paul. Date: 12/04/2023"*

and its runtime description is *"Split hits into subcell hits"*
([`HEXPLIT.h#L35`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.h#L35)).
The source cites one reference,
[arXiv:2308.06939](https://arxiv.org/abs/2308.06939)
([`HEXPLIT.cc#L4-L5`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L4-L5)).

## The physics

In a SiPM-on-tile hadronic calorimeter the transverse granularity is fixed
by the scintillator tile — for the ePIC forward HCal insert and the ZDC HCal
these are hexagonal or square tiles several centimetres across, far coarser
than the structure of the shower they sample. The trick these detectors use
is **staggering**: consecutive layers do not repeat the same tessellation,
but shift it by a fraction of the tile pitch, so a tile in layer *n* is
partially overlapped by several different tiles in layers *n±1* and *n±2*.
Superimposing the staggered tessellations divides each tile into a mosaic of
much smaller regions — 12 rhombic subcells for the hexagonal (`H4`) pattern,
4 quadrants for the staggered-square (`S2`) pattern — and each of those
regions is uniquely identified by *which* neighbouring-layer tiles cover it.

A shower is approximately continuous over two or three consecutive layers,
so the energies seen by the overlapping neighbours are a direct measurement
of *where inside the tile* the energy landed. HEXPLIT exploits that: for
each subcell it forms a weight from the energies of exactly the neighbouring
tiles that overlap it (their **product** for the hexagonal pattern, so all
of them must be lit for the subcell to be favoured), and redistributes the
tile's energy over its subcells in proportion to those weights. The output
is a `CalorimeterHit` collection with the same total energy but a factor 12
(or 4) finer effective granularity, which a topological clusteriser —
[`ImagingTopoCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc)
in both current users — then clusters. The code itself does not state the
resolution gain or motivate the exact weight form; for that, see the
reference paper.

## Inputs and outputs

Declared in
[`HEXPLIT.h#L26-L35`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.h#L26-L35):

| slot | name | type |
|---|---|---|
| in | `inputHits` | `edm4eic::CalorimeterHitCollection` (rec hits) |
| out | `outputSubcellHits` | `edm4eic::CalorimeterHitCollection` (subcell hits) |

## Staggering patterns

The pattern is a compile-time table (`stagger_pattern`,
[`HEXPLIT.h#L41-L101`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.h#L41-L101))
selected by `stag_type` in `init()`
([`HEXPLIT.cc#L90-L98`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L90-L98)):

| pattern | `SUBCELLS` | `NEIGHBORS` | `OVERLAP` | status |
|---|---|---|---|---|
| `H4` (hexagons) | 12 | 12 | 3 | default, used by the FHCAL insert |
| `S2` (squares) | 4 | 4 | 1 | used by the ZDC HCal |
| `H3` | — | — | — | **not implemented**; `init()` logs an error and silently keeps H4 |

`OVERLAP` is the number of neighbouring cells whose mutual overlap defines
one subcell — and hence the number of energies multiplied into that
subcell's weight.

### Geometry of the H4 pattern

All offsets are in units of the **hexagon side length** `sl`, which the
algorithm derives from the hit itself as `hit.getDimension().x / 2`
([`#L121`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L121)) —
i.e. it assumes the cell's x dimension is the vertex-to-vertex width `2·sl`.

- **Neighbour positions** — 12 of them, built as two rings of six
  ([`#L28-L50`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L28-L50)):
  radius `1.5·sl` at angles 0°, 60°, …, 300°, and radius `(√3/2)·sl` at
  90°, 150°, …, 30°. Both radii are smaller than the same-layer hexagon
  pitch `√3·sl`, which is exactly what makes them *overlapping* cells from
  staggered layers rather than same-layer neighbours.
- **Subcell centres** — the same two rings at **half** the radius,
  `0.75·sl` and `(√3/4)·sl`
  ([`#L58-L80`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L58-L80)).
  Subcell *k* therefore sits at the midpoint between the cell centre and
  neighbour *k* — the centroid of their overlap region.
- **Overlap triples** — a hard-coded 12×3 table
  ([`#L53-L55`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L53-L55)):
  `{0,11,10}, {1,6,11}, {2,7,6}, …`. Entry *k* always begins with *k*; the
  other two are the neighbours that also cover that subcell.

### Geometry of the S2 pattern

Trivially simpler
([`#L82-L88`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L82-L88)):
four neighbours at `(±sl, ±sl)`, four subcells at `(±0.5·sl, ±0.5·sl)`, and
each subcell defined by a single neighbour (`{% raw %}{{0},{1},{2},{3}}{% endraw %}`). Squares
staggered by half a cell in both x and y: each quadrant of a tile is covered
by exactly one diagonal neighbour.

## The algorithm, step by step

[`HEXPLIT::process`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L100-L222):

**1. MIP calibration.** All three energy parameters are expressed in MIPs —
the energy a minimum-ionising particle deposits in one cell — and converted
once per event
([`#L105-L108`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L105-L108)):

```
MIP   = MIP_config / GeV            (EDM4hep energies are in GeV)
delta = delta_in_MIPs · MIP
Emin  = Emin_in_MIPs  · MIP
tmax  = tmax_config / ns
```

Expressing the cuts in MIPs is what lets the same `Emin_in_MIPs = 0.5`
setting mean the same *physics* in the insert and in the ZDC despite their
different `MIP` values.

**2. Hit selection.** A hit is skipped entirely if `E < Emin` or
`t > tmax`
([`#L113-L116`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L113-L116)).
The same cut is applied again to each candidate neighbour
([`#L133-L135`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L133-L135)),
so out-of-time or sub-MIP tiles contribute nothing to the splitting.

**3. Collect neighbour energies.** For the hit under consideration, the
algorithm scans the whole collection for hits that are
([`#L119-L152`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L119-L152)):

- within **two layers** but not in the same layer: `1 <= |Δlayer| <= 2`;
- transversely close: `|Δx| <= 2·sl` and `|Δy| <= √3·sl` (a cheap
  pre-filter in local coordinates);
- and land on one of the `NEIGHBORS` ideal offsets to within a tolerance of
  `0.1` side lengths. The source explains the tolerance: *"Deviations could
  arise from rounding errors or from detector misalignment."*

Energies of all matching hits accumulate into `Eneighbors[k]` for that
offset — so several layers voting for the same offset add up.

**4. Weights.** Each neighbour energy is first floored at `delta`
([`#L155-L157`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L155-L157)),
then
([`#L158-L177`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L158-L177)):

```
H4:  w_k = E[n_k0] · E[n_k1] · E[n_k2]      (product of the 3 overlapping cells)
S2:  w_k = E[n_k0]                          (the single overlapping cell)
H3:  w_k = E[n_k0] · E[n_k1]                (unreachable — see caveats)
```

The `delta` floor is what keeps this well behaved: with no floor, a single
dark neighbour would zero a subcell outright and an all-dark cell would give
`0/0`. With it, an isolated hit whose neighbours are all empty gets equal
weights and its energy is spread uniformly over its subcells — the algorithm
degrades gracefully to "no information" rather than failing.

**5. Emit subcells.** For each of the `SUBCELLS` regions
([`#L178-L220`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L178-L220)):

- **local position** = the parent's local position plus
  `(subcell_offset_x, subcell_offset_y) · sl`; local z is unchanged;
- **global position** = that local position pushed through the DD4hep
  `VolumeManager` alignment of the parent cellID
  (`lookupDetElement(cellID).nominal().localToWorld(...)`). On any exception
  it warns and falls back to using the local position as global — a
  concession to the mock detector used in unit tests;
- **energy** = `E_parent · w_k / Σw` — the split is exactly energy
  conserving, which the unit test checks to 0.1 %
  ([`calorimetry_HEXPLIT.cc#L91-L98`](https://github.com/eic/EICrecon/blob/main/src/tests/algorithms_test/calorimetry_HEXPLIT.cc#L91-L98));
- **dimension** = the bounding box of the rhombus, which depends on its
  orientation: `(sl, √3·sl)` when `k % 3 == 0`, else `(1.5·sl, (√3/2)·sl)`;
  the parent's z dimension is kept
  ([`#L211-L215`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L211-L215));
- **cellID, time, sector, layer** are copied verbatim from the parent;
  energy error and time error are set to `0`.

The output size is therefore exactly `SUBCELLS × (number of hits passing the
E and t cuts)` — nothing is dropped for having a small weight.

## Configuration

Every field of
[`HEXPLITConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLITConfig.h):

| field | struct default | meaning |
|---|---|---|
| `MIP` | `472 keV` (`472. * dd4hep::keV`) | energy deposited in one cell by a minimum-ionising particle; the unit in which the two cuts below are expressed |
| `Emin_in_MIPs` | `0.1` | minimum hit energy, in MIPs, for a hit to be split **or** to count as a neighbour |
| `delta_in_MIPs` | `0.01` | floor applied to every neighbour energy before the weight product, so that dark neighbours neither zero a subcell nor cause `0/0` |
| `tmax` | `325 ns` (`325 * dd4hep::ns`) | maximum hit time; later hits are ignored entirely |
| `stag_type` | `H4` | staggering pattern: `H4` (hexagons, 12 subcells), `H3` (not implemented), `S2` (squares, 4 subcells) |

Runtime flags exposed by the factory
([`HEXPLIT_factory.h#L21-L24`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/HEXPLIT_factory.h#L21-L24)):
`MIP`, `Emin_in_MIPs`, `delta_in_MIPs`, `tmax`, as
`<PLUGIN>:<InstanceName>:<flag>`. **`stag_type` is not exposed** — it can
only be set in C++.

## Which detectors use it

Two instances (`grep -rn HEXPLIT src/detectors/`):

| plugin | instance (output) | input | consumed by | non-default config |
|---|---|---|---|---|
| [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L87-L96) | `HcalEndcapPInsertSubcellHits` | `HcalEndcapPInsertRecHits` | `ImagingTopoCluster` → `HcalEndcapPInsertImagingProtoClusters` ([`FHCAL.cc#L98`](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L98)) | `MIP = 480 keV`, `Emin_in_MIPs = 0.5`, `tmax = 162 ns` (*"150 ns + (z at front face)/(speed of light)"*); `stag_type` left at `H4` |
| [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L177-L188) | `HcalFarForwardZDCSubcellHits` | `HcalFarForwardZDCRecHits` | `ImagingTopoCluster` ([`ZDC.cc#L191`](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L191)) **and** [`CalorimeterIslandCluster`](calorimeter-island-cluster.md) ([`ZDC.cc#L208`](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L208)) | `MIP = 630 keV`, `Emin_in_MIPs = 0.5`, `delta_in_MIPs = 0.01`, `tmax = 269 ns`, **`stag_type = S2`** |

The ZDC plugin also registers a parallel chain explicitly labelled
*"Clusters with the baseline algorithm (no HEXPLIT)"*, running island
clustering directly on `HcalFarForwardZDCRecHits`
([`ZDC.cc#L266-L287`](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L266-L287)) —
so the effect of subcell splitting can be measured against a control in the
same job.

`HcalFarForwardZDCSubcellHits` is persisted by default
([`JEventProcessorPODIO.cc#L455`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L455));
`HcalEndcapPInsertSubcellHits` is **not**, and is transient unless requested.

## Caveats / needs human verification

1. **Subcell hits share their parent's `cellID`.** All 12 (or 4) subcells
   are created with `hit.getCellID()`
   ([`#L217`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L217)),
   so cellIDs are no longer unique in the output collection, and decoding a
   subcell hit's position from its cellID gives the *parent tile centre*, not
   the subcell. Any downstream consumer that keys on cellID — including
   anything reached via the persisted ZDC collection — must be aware of this.
2. **`H3` is half-implemented.** `init()` merely logs
   *"H3 staggering not implemented yet in EICrecon"* and does **not** throw
   ([`#L95-L97`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L95-L97)),
   leaving `stag` at its `H4` default; `process()` then takes the H3 weight
   branch, using only the first two of the H4 overlap triples. The result
   would be silently wrong. No detector configures `H3`.
3. **`double weights[12]` is a raw fixed-size array**
   ([`#L154`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L154))
   sized by the largest known pattern. Any future pattern with more than 12
   subcells would overflow it.
4. **The local→global transform carries a source `TODO`**: *"also convert
   this to the detector's global coordinates. To do: check if this is
   correct"*
   ([`#L194`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L194)).
   The `catch (...)` fallback that reuses local coordinates as global exists
   for the mock-detector test but would also mask a real geometry lookup
   failure, downgraded to a `warning`.
5. **The layer window `1 <= |Δlayer| <= 2` and the tolerance `0.1` side
   lengths are hard-coded**, not configurable
   ([`#L125-L132`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L125-L132)).
   Whether ±2 layers is right for a given sampling structure is a physics
   choice frozen into the code.
6. **`sl = dimension.x / 2` assumes a specific convention** — for hexagons,
   that `dimension.x` is the vertex-to-vertex width; for the S2 squares it
   makes `sl` half the square side, which is why the S2 offsets `±1` and
   `±0.5` come out as half and quarter of the tile pitch. The convention is
   set by the `epic` geometry description, not by EICrecon.
7. **`dimension` on the output is a bounding box**, not the rhombus area
   ([`#L211-L215`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/HEXPLIT.cc#L211-L215));
   anything computing a cell area or a `dimScaled` distance from it will
   overestimate.
8. **The `MIP` values have no provenance in EICrecon**: 472 keV as the struct
   default, 480 keV for the insert, 630 keV for the ZDC. Which simulation or
   test-beam study produced them is not recorded in the source.
9. The neighbour scan is O(N²) over the hit collection with no spatial
   index; and `Eneighbors[k]` sums *all* matching hits from both ±1 and ±2
   layers with equal weight, without any longitudinal weighting.
10. Because nothing prunes tiny-weight subcells, a single tile always yields
    exactly `SUBCELLS` output hits, some carrying a negligible fraction of
    the energy. Downstream thresholds are what remove them.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
(fetched 2026-08-19). AI-authored draft — verify against source.*
