---
title: Cluster mergers
parent: EICrecon
nav_order: 38
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# Cluster mergers

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

Three algorithms in `src/algorithms/calorimetry/` carry "merge" in their
name, and they solve three different problems. **EnergyPositionClusterMerger**
handles a calorimeter built from two sections that both see the same shower:
one section measures the energy well, the other measures the position well,
and the merged cluster takes energy from the first and position from the
second. **TruthEnergyPositionClusterMerger** does the same pairing, but
matches the two clusters through their MC-truth particle instead of through
geometry — the reference against which the geometric matcher can be judged.
**TrackClusterMergeSplitter** answers a different question: given a set of
calorimeter clusters and the track projections that land on the calorimeter
face, how many showers are really there? It merges clusters that together
belong to one charged particle, and splits one cluster into several when
several tracks point into it.

---

## EnergyPositionClusterMerger

**Source:**
[`EnergyPositionClusterMerger.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EnergyPositionClusterMerger.h) ·
[`.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EnergyPositionClusterMerger.cc) ·
[`Config.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EnergyPositionClusterMergerConfig.h)

Its own doc comment
([`.h#L25-L36`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EnergyPositionClusterMerger.h#L25-L36)):

> *"Simple algorithm to merge the energy measurement from cluster1 with the
> position measurement of cluster2 (in case matching clusters are found). If
> not, it will propagate the raw cluster from cluster1 or cluster2. Matching
> occurs based on the cluster phi, eta and E variables, with tolerances
> defined in the options file. A negative tolerance effectively disables a
> check. The energy tolerance is defined as a relative number (e.g. 0.1). In
> case of ambiguity the closest cluster is merged."*

### What it does physically

A hybrid calorimeter such as the ePIC barrel ECal has a sampling section
(ScFi/Pb) that absorbs most of the shower and therefore measures its energy,
and a finely pixellated imaging section that samples only a small fraction of
the energy but resolves where the shower entered. Neither cluster on its own
is a good particle measurement. The algorithm loops over the *position*
clusters and, for each, looks for the *energy* cluster that plausibly comes
from the same particle: the two must agree in pseudorapidity, in azimuth, and
in energy
([`.cc#L59-L71`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EnergyPositionClusterMerger.cc#L59-L71)).
The φ comparison is made on `|sin(Δφ/2)|` rather than on Δφ itself, so that
the wrap-around at ±π is handled and clusters in opposite hemispheres cannot
accidentally satisfy the cut. Where more than one energy cluster passes all
three cuts, the one whose energy is closest to the position cluster's energy
wins
([`.cc#L76-L80`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EnergyPositionClusterMerger.cc#L76-L80)),
and each energy cluster can be consumed only once.

The merged cluster is assembled field by field
([`.cc#L88-L102`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EnergyPositionClusterMerger.cc#L88-L102)):
energy and energy error from the energy cluster; time, position and position
error from the position cluster; `nhits` is the sum; both parent clusters are
attached as sub-clusters, all their hits are copied in, and each parent's
energy is recorded as a `subdetectorEnergy` entry. Note that the energy is
*taken*, not added — the imaging section's contribution is not summed into
the total, only kept in the sub-detector breakdown.

MC-truth bookkeeping is done at the same time
([`.cc#L123-L183`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EnergyPositionClusterMerger.cc#L123-L183)).
If both parents point to the same MC particle, one link/association of weight
1.0 is written. If they disagree — the geometric match crossed particles —
*two* links of weight 0.5 each are written, one to each MC particle, so the
ambiguity is preserved rather than silently resolved.

### Configuration

| field | struct default | meaning |
|---|---|---|
| `energyRelTolerance` | `0.5` | relative energy agreement, `\|E_pos − E_ene\|/E_ene`; a value ≤ 0 disables the check |
| `phiTolerance` | `0.1` | azimuthal tolerance in radians; compared as `\|sin(Δφ/2)\| ≤ sin(φ_tol/2)` |
| `etaTolerance` | `0.2` | pseudorapidity tolerance |

All three defaults come from
[`EnergyPositionClusterMergerConfig.h#L8-L13`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EnergyPositionClusterMergerConfig.h#L8-L13).
The "negative tolerance disables the check" behaviour is implemented as
`> 0`, so **zero also disables** the corresponding cut.

Inputs are four collections — energy clusters, their MC associations,
position clusters, their MC associations — and outputs are the merged
clusters plus links and associations
([`.h#L18-L23`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EnergyPositionClusterMerger.h#L18-L23)).

### Which detectors use it

Only the barrel ECal, once
([`BEMC.cc#L450-L462`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L450-L462)):

| instance | inputs | output | config |
|---|---|---|---|
| `EcalBarrelClustersWithoutShapes` | `EcalBarrelScFiClusters` (energy) + `EcalBarrelImagingClusters` (position), with their associations | `EcalBarrelClustersWithoutShapes` | `energyRelTolerance=0.5`, `phiTolerance=0.1`, `etaTolerance=0.2` — i.e. the struct defaults |

A `CalorimeterClusterShape` pass then turns that into the persisted
`EcalBarrelClusters`
([`BEMC.cc#L463-L467`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L463-L467)).

---

## TruthEnergyPositionClusterMerger

**Source:**
[`TruthEnergyPositionClusterMerger.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TruthEnergyPositionClusterMerger.h) ·
[`.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TruthEnergyPositionClusterMerger.cc)
(no config struct — it is `WithPodConfig<NoConfig>`)

Its doc comment
([`.h#L27-L34`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TruthEnergyPositionClusterMerger.h#L27-L34)):

> *"Simple algorithm to merge the energy measurement from cluster1 with the
> position measurement of cluster2 (in case matching clusters are found). If
> not, it will propagate the raw cluster from cluster1 or cluster2. Matching
> occurs based on the mc truth information of the clusters."*

### What it does physically

This is the same merge with the geometry replaced by cheating. Each input
collection is first turned into a map *MC particle index → cluster* by
walking the MC associations; clusters without a truth link are dropped, and
when two clusters of the same collection point to the same MC particle only
the higher-energy one is kept
([`.cc#L151-L187`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TruthEnergyPositionClusterMerger.cc#L151-L187)).
Two clusters therefore belong together exactly when they were made by the
same generated particle, which removes the mis-association that the
geometric matcher can suffer and makes this collection a useful reference
when studying merging efficiency.

The merge itself is field-for-field identical to the geometric version:
energy from the energy cluster, position and time from the position cluster,
hits and sub-detector energies from both
([`.cc#L62-L76`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TruthEnergyPositionClusterMerger.cc#L62-L76)).
Unlike the geometric version, the unmatched cases are *not* thrown away:

- a position cluster with no partner is cloned straight through
  ([`.cc#L95-L110`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TruthEnergyPositionClusterMerger.cc#L95-L110));
- an energy cluster left over at the end keeps its energy but is given a
  *fabricated* position: the direction of the MC particle's momentum, placed
  at a fixed radius
  ([`.cc#L116-L146`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TruthEnergyPositionClusterMerger.cc#L116-L146)).
  The code's own comment says such a leftover "should really have a match in
  the position clusters (and if they don't it [is] due to a clustering
  error)".

The fabricated radius is `78.5 cm`, next to a `FIXME` asking for the nominal
110 cm and for the start-vertex angles
([`.cc#L127-L129`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TruthEnergyPositionClusterMerger.cc#L127-L129)).
Every output cluster gets a truth link and association of weight 1.0 by
construction.

### Configuration

None. The factory is declared `JOmniFactory<…, NoConfig>`
([`TruthEnergyPositionClusterMerger_factory.h#L13-L16`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/TruthEnergyPositionClusterMerger_factory.h#L13-L16)),
so there are no runtime flags beyond the collection names. The extra input
relative to the geometric merger is `MCParticles`, needed to look up the
particle by index.

### Which detectors use it

Only the barrel ECal, once
([`BEMC.cc#L468-L475`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L468-L475)):
instance `EcalBarrelTruthClustersWithoutShapes`, from `MCParticles` +
`EcalBarrelScFiClusters` + `EcalBarrelImagingClusters` and their
associations, producing the collection that (after the shape pass) is
persisted as `EcalBarrelTruthClusters`.

---

## TrackClusterMergeSplitter

**Source:**
[`TrackClusterMergeSplitter.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.h) ·
[`.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc) ·
[`Config.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitterConfig.h)

Its doc comment
([`.h#L30-L38`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.h#L30-L38)):

> *"An algorithm which takes a collection of clusters, matches track
> projections, and then decides to merge or split those clusters based on
> average E/p from simulations. Heavily inspired by Eur. Phys. J. C (2017)
> 77:466"*

### The physics problem

Hadronic showers in an HCal are wide and irregular. A single pion deposits
energy in a sprawling, often disconnected pattern, so a topological or island
clusterer will happily break one pion's shower into several clusters. At the
same time, two nearby hadrons in a jet deposit overlapping energy that the
same clusterer will happily merge into one. Calorimeter information alone
cannot distinguish "one particle, badly fragmented" from "two particles,
partly overlapping".

The tracker can. Every charged particle that reaches the calorimeter leaves a
track, and the track can be extrapolated to the calorimeter's front face. The
number of projections landing in a region of the calorimeter face therefore
tells you how many charged particles actually entered it, and the momentum of
each projection tells you how much energy each of them should have deposited
(through the average `E/p`, calibrated from simulation). The algorithm uses
that count and those momenta to correct the clustering: too little energy for
the track that points at it means the shower is fragmented, so neighbouring
clusters are merged in; several tracks pointing at one merged blob means it
must be shared out again.

### Step 1 — cluster → projection map

The algorithm consumes an already-made track-cluster matching
(`edm4eic::TrackClusterMatch`), the clusters themselves, and the track
projections (`edm4eic::TrackSegment`). It builds a map from each matched
cluster to all projections of the track it was matched to
([`.cc#L62-L72`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L62-L72)).
The projection point actually used is the one whose `surface` index equals
`surfaceToUse`
([`.cc#L88-L96`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L88-L96));
every configured instance uses `1`, which in the upstream matcher
[`TrackClusterMatch.cc#L60`](https://github.com/eic/EICrecon/blob/main/src/algorithms/reco/TrackClusterMatch.cc#L60)
is the calorimeter front face.

The η/φ matching itself is *not* done here. It happens one step earlier, in
[`TrackClusterMatch`](https://github.com/eic/EICrecon/blob/main/src/algorithms/reco/TrackClusterMatch.cc),
which for each cluster takes the closest unused track projection within
`ΔR = √(Δη² + Δφ²) < matching_distance`, φ wrapped into (−π, π]
([`.cc#L40-L100`](https://github.com/eic/EICrecon/blob/main/src/algorithms/reco/TrackClusterMatch.cc#L40-L100)).
Its config has exactly two fields
([`TrackClusterMatchConfig.h#L10-L13`](https://github.com/eic/EICrecon/blob/main/src/algorithms/reco/TrackClusterMatchConfig.h#L10-L13)):
`matching_distance` (default `0.5`) and `calo_id` (default `""`, a DD4hep
geometry constant naming the calorimeter system; the algorithm throws if it
is empty). Those instances are registered per calorimeter in
[`reco.cc#L206-L235`](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L206-L235)
and all of them keep the default matching distance, setting only `calo_id`.

### Step 2 — significance, and what to merge

For the seed cluster of each matched pair, the algorithm compares the
measured cluster energy with the energy the track says it should have
([`.cc#L104-L120`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L104-L120)):

```
E_expected  = avgEP × |p_projection|
significance = (E_cluster − E_expected) / sigEP
```

If the significance is **above** `minSigCut` the cluster already carries at
least as much energy as the track can account for, and nothing is done. If it
is below — the cluster is short of energy, i.e. the shower looks fragmented —
the algorithm collects every other unused cluster within a fixed (Δη, Δφ)
radius of the seed
([`.cc#L140-L160`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L140-L160)):

```
Δr² = Δη² + Δφ²   (Δφ wrapped by std::remainder)  ≤  drAdd²
```

Each absorbed cluster is marked used and its energy added to a running sum.
Crucially, if an absorbed cluster had a matched track of its own, that
track's projections are appended to the seed's projection list
([`.cc#L164-L167`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L164-L167))
— this is what turns "merge" into "merge, then split": the merged blob now
knows how many charged particles entered it. The running significance of the
sum is only traced for debugging, not used as a stopping condition, so the
window is applied once around the seed and all clusters inside it are taken.

### Step 3 — split, and how the energy is divided

One output protocluster is created for every projection pointing at the
merged blob
([`.cc#L186-L207`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L186-L207)).
With a single track there is nothing to divide: all the hits of all the
merged clusters go into that one protocluster with weight 1
([`.cc#L240-L245`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L240-L245)).

With several tracks the hits are shared rather than assigned. Every hit is
added to *every* split protocluster, but with a fractional weight
([`.cc#L249-L299`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L249-L299)):

```
dist_i  = hypot(η_hit − η_proj,i , Δφ(hit, proj,i))
w_i     = exp(−dist_i / transverseEnergyProfileScale) × |p_i|
weight_i(hit) = w_i / Σ_j w_j
```

That is, a hit's energy is split between the candidate tracks in proportion
to an exponentially falling transverse shower profile around each track's
impact point, scaled by the track's momentum — a more energetic track is
expected to have deposited more of any given hit. The weights sum to one over
the tracks, so total energy is conserved by construction. The weights are
written into the protocluster alongside the hits
([`.cc#L307-L325`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L307-L325)),
and it is the downstream
[`CalorimeterClusterRecoCoG`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L116-L118)
that actually multiplies `hit.energy × weight` when it builds the final
cluster — so the split energies only materialise after that step.

Finally, one `TrackProtoClusterLink` per (track, split protocluster) pair is
emitted with a placeholder weight of 1.0 and an explicit `FIXME` that it
should encode the goodness of the match
([`.cc#L198-L206`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L198-L206)),
and every cluster that was never touched is copied through unchanged as a
one-to-one protocluster
([`.cc#L212-L225`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L212-L225)).

### Configuration

| field | struct default | meaning |
|---|---|---|
| `minSigCut` | `-1.0` | significance threshold; clusters *below* it are treated as energy-deficient and trigger merging (the header comment reads "any clusters below this will be merged") |
| `avgEP` | `1.0` | mean of the `E/p` distribution from simulation; sets the expected cluster energy `avgEP × p` |
| `sigEP` | `1.0` | RMS of the `E/p` distribution, used as the denominator of the significance |
| `drAdd` | `0.4` | radius in (Δη, Δφ) of the window inside which other clusters are absorbed into the seed |
| `surfaceToUse` | `1` | index of the track-projection surface to use (`1` = calorimeter front face) |
| `transverseEnergyProfileScale` | `1.0` | scale in the `exp(−dist/scale)` hit-to-track weight; larger values share hits more evenly |

Defaults from
[`TrackClusterMergeSplitterConfig.h#L8-L28`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitterConfig.h#L8-L28).
All six are exposed as JANA parameters under the instance name, with the
identical spelling
([`TrackClusterMergeSplitter_factory.h#L37-L43`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/TrackClusterMergeSplitter_factory.h#L37-L43)) —
e.g. `EHCAL:HcalEndcapNSplitMergeProtoClusters:drAdd`.

### Which detectors use it

Five calorimeters, all through the same track projections
(`CalorimeterTrackProjections`) and each with its own matched-track
collection from `reco.cc`:

| detector | instance | input clusters | `minSigCut` | `avgEP` | `sigEP` | `drAdd` |
|---|---|---|---|---|---|---|
| EEMC (backward ECal) | `EcalEndcapNSplitMergeProtoClusters` | `EcalEndcapNClustersWithoutPID` | `-1.0` | `1.0` | `0.10` | `0.08` |
| FEMC (forward ECal) | `EcalEndcapPSplitMergeProtoClusters` | `EcalEndcapPClusters` | `-2.0` | `1.0` | `0.10` | `0.30` |
| BHCAL (barrel HCal) | `HcalBarrelSplitMergeProtoClusters` | `HcalBarrelClustersWithoutShapes` | `-2.0` | `0.50` | `0.25` | `0.40` |
| EHCAL (backward HCal) | `HcalEndcapNSplitMergeProtoClusters` | `HcalEndcapNClusters` | `-2.0` | `0.60` | `0.40` | `0.40` |
| LFHCAL (forward HCal) | `LFHCALSplitMergeProtoClusters` | `LFHCALClusters` | `-2.0` | `0.50` | `0.25` | `0.30` |

Sources:
[`EEMC.cc#L194-L206`](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L194-L206),
[`FEMC.cc#L209-L220`](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L209-L220),
[`BHCAL.cc#L164-L176`](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L164-L176),
[`EHCAL.cc#L145-L156`](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L145-L156),
[`FHCAL.cc#L305-L316`](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L305-L316).
`surfaceToUse=1` and `transverseEnergyProfileScale=1.0` everywhere.

The pattern is physically sensible: the ECals expect `E/p ≈ 1` with a tight
10% spread and a narrow merging window, while the non-compensating HCals
expect `E/p ≈ 0.5–0.6` with a 25–40% spread and merge over a much wider
Δr ≈ 0.3–0.4 — exactly the "broad, fragmented hadronic shower" case.

**Downstream**, each `…SplitMergeProtoClusters` goes through
`CalorimeterClusterRecoCoG` (which applies the split weights) and
`CalorimeterClusterShape` to become `…SplitMergeClusters`, persisted by
default
([`JEventProcessorPODIO.cc#L345-L429`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L345-L429)),
and the `…TrackSplitMergeProtoClusterLinks` are promoted to cluster-level
matches by `TrackProtoClusterMatchPromoter` for particle flow
([`particle_flow.cc#L43-L75`](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L43-L75)).

---

## Caveats / needs human verification

1. **`EnergyPositionClusterMerger` drops unmatched clusters.** The doc
   comment promises that a cluster without a partner "will propagate the raw
   cluster", but the code only logs `"Unmatched position cluster"` and writes
   nothing
   ([`.cc#L197-L200`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EnergyPositionClusterMerger.cc#L197-L200));
   energy clusters that were never consumed are not revisited at all. So a
   barrel shower reconstructed only in ScFi, or only in the imaging layers,
   is absent from `EcalBarrelClusters`. The truth version *does* propagate
   both cases. Whether this is intentional is not determinable from the
   source.
2. **`TrackClusterMergeSplitter` returns nothing when there are no matched
   tracks.** The early return on an empty match collection
   ([`.cc#L53-L57`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L53-L57))
   happens *before* step 4, so a neutral-only event yields an empty
   `…SplitMergeProtoClusters` collection rather than a copy of the input
   clusters. Anything reading only the split-merge collections loses those
   clusters.
3. **The significance is dimensionally odd.** `sigEP` is documented as the
   RMS of the (dimensionless) `E/p` distribution, but it divides an energy
   difference in GeV
   ([`.cc#L105-L110`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L105-L110)).
   A true significance would use `sigEP × |p|` in the denominator. As
   written, the effective cut scales with momentum. Needs a maintainer's
   confirmation of which was intended.
4. **Weight normalisation can divide by zero.** In the splitting loop the
   per-projection weights are normalised by `wTotal`
   ([`.cc#L290-L293`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L290-L293)),
   which is zero if no projection in the list has a point on
   `surfaceToUse`; the `iProj` counter is also not incremented on that
   `continue`
   ([`.cc#L264-L266`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc#L264-L266)),
   so a missing surface point shifts the remaining projections' weights into
   the wrong slots. This is read from the code, not observed in a run.
5. **`matchDist` does not exist.** The η/φ matching threshold that feeds this
   algorithm is `matching_distance` in
   [`TrackClusterMatchConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/reco/TrackClusterMatchConfig.h),
   a separate algorithm in `src/algorithms/reco/`. There is no `matchDist`
   field anywhere in the tree at this commit.
6. **EHCAL registers two factories with the same instance name.**
   `CalorimeterClusterRecoCoG` appears as `HcalEndcapNClustersWithoutShapes`
   both before
   ([`EHCAL.cc#L123-L139`](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L123-L139))
   and after
   ([`EHCAL.cc#L157-L172`](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L157-L172))
   the split-merge step, with different output tags. Since the instance name
   is the JANA parameter prefix, the two share their runtime flags. Looks
   like a copy-paste slip; unverified.
7. **The `78.5 cm` fallback radius** in the truth merger is hard-coded next
   to a `FIXME` asking for 110 cm, and the position is built from the MC
   momentum direction, not the start vertex. Truth clusters carrying that
   position are not a geometric measurement of anything.
8. **Inconsistent inputs across detectors.** EEMC feeds the splitter
   `…ClustersWithoutPID`, BHCAL feeds it `…ClustersWithoutShapes`, and the
   rest feed the fully processed `…Clusters`. Whether the shape/PID passes
   are meant to be skipped in those two cases is not stated anywhere in the
   source.
9. **`avgEP`/`sigEP` values have no provenance comment.** The header calls
   them the average and RMS "from simulations", but which simulation sample,
   geometry version or energy range produced `0.50 ± 0.25` for the HCals is
   not recorded in EICrecon.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
(fetched 2026-08-19). AI-authored draft — verify against source.*
