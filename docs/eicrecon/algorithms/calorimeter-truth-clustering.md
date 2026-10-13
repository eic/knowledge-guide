---
title: CalorimeterTruthClustering
parent: EICrecon
nav_order: 37
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# CalorimeterTruthClustering — MC-truth "perfect clustering" reference

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

**Source:**
[`src/algorithms/calorimetry/CalorimeterTruthClustering.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.h) ·
[`.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc) ·
factory [`CalorimeterTruthClustering_factory.h`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/CalorimeterTruthClustering_factory.h)

**Signature:** (`edm4eic::CalorimeterHitCollection`,
`edm4eic::MCRecoCalorimeterHitLinkCollection`) →
`edm4eic::ProtoClusterCollection`
([`CalorimeterTruthClustering.h#L20-L33`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.h#L20-L33)).
Its own one-line description is simply *"Use truth information for
clustering."*

{: .warning }
The output of this algorithm **cannot be produced from real data**. It reads
the Geant4 particle history, so it exists only to give simulation studies an
upper bound: the clusters real clustering algorithms are measured against.

## What it does physically

Any real clustering algorithm — island, topological, splitting — has to guess
which energy deposits belong to which incident particle from geometry and
energy alone. That guess fails in the ways that limit calorimeter
performance: two showers overlap and get merged, a tail falls below threshold
and gets dropped, a fluctuation splits one shower in two. To quantify those
failures you need the answer key.

`CalorimeterTruthClustering` builds the answer key. It takes exactly the same
reconstructed hits that the real clustering sees — same digitisation, same
zero suppression, same calibration — and partitions them not by proximity but
by *which primary particle actually deposited the energy*, as recorded by the
simulation. One proto-cluster per contributing primary. The result is a
proto-cluster collection that is drop-in compatible with the real one, so the
whole downstream chain (centre-of-gravity position and energy, then shower
shape) can be run twice and compared. Any difference between
`…TruthClusters` and `…Clusters` is attributable to the clustering step, with
digitisation and calibration held fixed.

Note that "perfect" here means perfect *assignment of surviving hits*, not
perfect energy. A hit that fell below the reconstruction threshold is gone
before this algorithm sees it, and the energy is still the reconstructed,
sampling-fraction-corrected energy. So a truth cluster is not the MC particle
energy — it is what an ideal clustering algorithm could have recovered from
the hits that survived.

## How the truth association is looked up

The chain is three hops, and none of them is a direct rec-hit → MCParticle
link ([`CalorimeterTruthClustering.cc#L25-L66`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc#L25-L66)):

1. **Rec hit → raw hit.** Each `edm4eic::CalorimeterHit` carries a relation
   to the `edm4hep::RawCalorimeterHit` it was reconstructed from, read as
   `hit.getRawHit()`.
2. **Raw hit → sim hits.** The second input collection,
   `edm4eic::MCRecoCalorimeterHitLinkCollection`, is wrapped in a
   `podio::LinkNavigator`
   ([`#L31`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc#L31)),
   and `navigator.getLinked(hit.getRawHit())`
   ([`#L39`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc#L39))
   returns every `edm4hep::SimCalorimeterHit` linked to that raw hit, each
   with a weight. These links are produced by `CalorimeterHitDigi`, which sets
   `from = rawhit`, `to = simhit`
   ([`CalorimeterHitDigi.cc#L202-L204`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L202-L204));
   because digitisation may sum several sim hits into one channel, this step
   is genuinely one-to-many.
3. **Sim hit → primary MCParticle.** Each sim hit carries a list of
   `edm4hep::CaloHitContribution`, one per Geant4 step that deposited energy
   in that cell. For each contribution, `get_primary()`
   ([`#L68-L84`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc#L68-L84))
   takes `contrib.getParticle()` — the particle that actually made the step,
   typically a shower secondary — and walks *up the parent chain*, following
   `getParents(0)` only, until it reaches a particle whose
   `getGeneratorStatus() != 0` or a particle with no parents. The ancestor
   found is the "primary".

The primary is identified by `primary.getObjectID().index`, and a
`std::map<int32_t, int32_t>` maps that track ID to a proto-cluster index,
creating a new proto-cluster the first time each primary is seen
([`#L34`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc#L34),
[`#L52-L55`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc#L52-L55)).
The map is local to `process()`, so proto-cluster identity is per event.

### Hits with no contribution, and hits with several

- **No linked sim hit, or a sim hit with no contributions.** The set of
  primaries for that rec hit stays empty, the "add to proto-clusters" loop
  runs zero times, and the hit is **silently dropped** — it appears in no
  proto-cluster at all. The source comments this as *"Ignore hit if no
  associated sim hits"*
  ([`#L41-L42`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc#L41-L42)).
  There is no warning and no counter.
- **Several distinct primaries contributing to one hit.** The primaries are
  collected into a `std::set`, and the hit is then added to **every** matching
  proto-cluster, each time with weight `1`
  ([`#L60-L64`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc#L60-L64)).
  The hit is therefore shared, not split: truth proto-clusters may overlap,
  and the sum of their energies can exceed the total deposited energy. The
  contribution weights returned by the link navigator and the per-contribution
  energies are both available at that point but are **not** used to split the
  hit fractionally.

Because the same hit can land in several proto-clusters and no threshold is
applied anywhere, there is no minimum-hits or minimum-energy cut: a primary
that touched a single cell still gets its own one-hit proto-cluster.

## Configuration

**This algorithm has no configuration.** It derives from
`WithPodConfig<NoConfig>`
([`CalorimeterTruthClustering.h#L25-L26`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.h#L25-L26)),
the JANA wrapper is a `JOmniFactory<…, NoConfig>` with no `ParameterRef`s
([`CalorimeterTruthClustering_factory.h#L13-L23`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/CalorimeterTruthClustering_factory.h#L13-L23)),
and `init()` is an empty body
([`CalorimeterTruthClustering.cc#L23`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc#L23)).
There are no `-P…` runtime flags for it, and no `…Config.h` file exists. The
only thing a detector plugin chooses is the instance name and the input and
output collection tags.

## Downstream

The output is an ordinary `edm4eic::ProtoClusterCollection`, indistinguishable
in type from what `CalorimeterIslandCluster` or `ImagingTopoCluster` produce,
and it is consumed by exactly the same algorithms: every plugin feeds it into
`CalorimeterClusterRecoCoG` to get a `…TruthClustersWithoutShapes` collection,
then into `CalorimeterClusterShape` to get `…TruthClusters` — the same
`energyWeight` / `logWeightBase` settings as the corresponding real path in
that detector (see e.g.
[`EEMC.cc#L107-L125`](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L107-L125)).

Eight of these truth cluster collections are written to the output file by
default —
`EcalEndcapNTruthClusters`, `EcalEndcapPTruthClusters`,
`EcalLumiSpecTruthClusters`, `HcalEndcapNTruthClusters`,
`HcalBarrelTruthClusters`, `EcalFarForwardZDCTruthClusters`,
`HcalFarForwardZDCTruthClusters` (plus `EcalBarrelTruthClusters`, which comes
from a *different* algorithm, see below)
([`JEventProcessorPODIO.cc`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L330-L465)).
`B0ECalTruthClusters`, `LFHCALTruthClusters` and
`HcalEndcapPInsertTruthClusters` are built but are **not** in the default
persisted list. Nothing in `src/global/` consumes any truth cluster
collection — they are a study output, never an input to physics
reconstruction.

## Which detectors use it

Ten instances across eight plugins. All of them take the detector's rec hits
plus its `…RawHitLinks` collection and emit `…TruthProtoClusters`; there is
nothing else to configure, so the table is just the naming.

| plugin | instance name | inputs | output |
|---|---|---|---|
| [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L79-L83) | `EcalEndcapNTruthProtoClusters` | `EcalEndcapNRecHits`, `EcalEndcapNRawHitLinks` | `EcalEndcapNTruthProtoClusters` |
| [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L139-L143) | `EcalEndcapPTruthProtoClusters` | `EcalEndcapPRecHits`, `EcalEndcapPRawHitLinks` | `EcalEndcapPTruthProtoClusters` |
| [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L98-L102) | `HcalBarrelTruthProtoClusters` | `HcalBarrelRecHits`, `HcalBarrelRawHitLinks` | `HcalBarrelTruthProtoClusters` |
| [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L77-L81) | `HcalEndcapNTruthProtoClusters` | `HcalEndcapNMergedHits`, `HcalEndcapNRawHitLinks` | `HcalEndcapNTruthProtoClusters` |
| [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L80-L85) | `HcalEndcapPInsertTruthProtoClusters` | `HcalEndcapPInsertMergedHits`, `HcalEndcapPInsertRawHitLinks` | `HcalEndcapPInsertTruthProtoClusters` |
| [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L215-L219) | `LFHCALTruthProtoClusters` | `LFHCALRecHits`, `LFHCALRawHitLinks` | `LFHCALTruthProtoClusters` |
| [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L63-L68) | `EcalFarForwardZDCTruthProtoClusters` | `EcalFarForwardZDCRecHits`, `EcalFarForwardZDCRawHitLinks` | `EcalFarForwardZDCTruthProtoClusters` |
| [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L259-L264) | `HcalFarForwardZDCTruthProtoClusters` | `HcalFarForwardZDCRecHits`, `HcalFarForwardZDCRawHitLinks` | `HcalFarForwardZDCTruthProtoClusters` |
| [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L59-L61) | `B0ECalTruthProtoClusters` | `B0ECalRecHits`, `B0ECalRawHitLinks` | `B0ECalTruthProtoClusters` |
| [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L58-L62) | `EcalLumiSpecTruthProtoClusters` | `EcalLumiSpecRecHits`, `EcalLumiSpecRawHitLinks` | `EcalLumiSpecTruthProtoClusters` |

Note that EHCAL and the forward-insert HCal feed `…MergedHits` (the output of
`CalorimeterHitsMerger`) rather than `…RecHits`, matching what their real
clustering consumes.

{: .note }
The **BEMC does not use this algorithm.** `EcalBarrelTruthClusters` is
produced instead by
[`TruthEnergyPositionClusterMerger`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TruthEnergyPositionClusterMerger.cc)
([`BEMC.cc#L468-L481`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L468-L481)),
which truth-matches already-formed ScFi and Imaging clusters instead of
truth-partitioning raw hits. Same word in the collection name, different
meaning — do not compare the two directly.

## Caveats / needs human verification

1. `get_primary()` carries its own TODO in the source: *"finalize primary
   selection. This can be improved!!"*
   ([`CalorimeterTruthClustering.cc#L73-L75`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc#L73-L75)).
   The definition of "primary" is therefore explicitly provisional.
2. The parent walk follows `getParents(0)` only. For a particle with several
   parents (e.g. after a merged vertex in the MC record) the other branches
   are never examined, and the result depends on parent ordering in the
   generator record.
3. The loop condition checks `getGeneratorStatus() != 0` *after* confirming
   the particle has parents, so a contributor that itself has a non-zero
   generator status but no parents falls out of the loop by the
   `parents_size() > 0` test rather than the status test. The two paths agree
   on the returned particle, but the logic is easy to misread.
4. Hits with no truth link are dropped without any log message or counter, so
   a broken or missing `…RawHitLinks` collection would silently yield an empty
   truth cluster collection rather than an error.
5. Shared hits are duplicated at full weight into every contributing
   primary's proto-cluster. Downstream `CalorimeterClusterRecoCoG` will
   therefore count that energy once per cluster, and the summed truth cluster
   energy in a busy event is an over-count. Whether that is acceptable for the
   benchmark's purpose is a physics judgement not made in the source.
6. The weight returned by `LinkNavigator::getLinked` is destructured into
   `weight` and then never used
   ([`#L43`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc#L43)).
   Likewise `contrib.getEnergy()` is available but ignored. A
   fractional-sharing version of this algorithm would be a small change; it
   is not clear whether the simple version is deliberate.
7. `#include <edm4hep/RawCalorimeterHit.h>` and several other headers are
   pulled in, and the file's copyright year is 2026 while the factory's is
   2023 — the algorithm has clearly been reworked recently (the podio
   `LinkNavigator` API is new), so behaviour may differ from older EICrecon
   releases and from published benchmark plots.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
(fetched 2026-08-19). AI-authored draft — verify against source.*
