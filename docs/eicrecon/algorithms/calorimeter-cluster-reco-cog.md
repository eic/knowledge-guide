---
title: CalorimeterClusterRecoCoG
parent: EICrecon
nav_order: 34
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# CalorimeterClusterRecoCoG — centre-of-gravity cluster reconstruction

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

`CalorimeterClusterRecoCoG` is the step that turns a **protocluster** — a bare
bag of calorimeter hits produced by
[`CalorimeterIslandCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterIslandCluster.cc),
[`ImagingTopoCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingTopoCluster.cc),
[`CalorimeterTruthClustering`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterTruthClustering.cc)
or
[`TrackClusterMergeSplitter`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/TrackClusterMergeSplitter.cc)
— into a physics object: an `edm4eic::Cluster` carrying an **energy**, a
**position**, a **time**, and (for simulation) a set of links back to the
MC particles that made it. It is the single most widely instantiated
calorimetry algorithm in EICrecon: 28 instances across nine detector
plugins.

The algorithm's own header comment
([`CalorimeterClusterRecoCoG.h#L4-L9`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.h#L4-L9)):

*"Reconstruct the cluster with Center of Gravity method. Logarithmic
weighting is used for mimicking energy deposit in transverse direction."*

and its runtime description
([`#L72-L74`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.h#L72-L74)):

*"Reconstruct a cluster with the Center of Gravity method. For simulation
results it optionally creates a Cluster <-> MCParticle association provided
both optional arguments are provided."*

## Inputs and outputs

Declared in
[`CalorimeterClusterRecoCoG.h#L55-L61`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.h#L55-L61):

| slot | type | required |
|---|---|---|
| in `inputProtoClusterCollection` | `edm4eic::ProtoCluster` | yes |
| in `mcRawHitLinks` | `edm4eic::MCRecoCalorimeterHitLink` | optional |
| in `mcRawHitAssocations` *(sic)* | `edm4eic::MCRecoCalorimeterHitAssociation` | optional |
| out `outputClusterCollection` | `edm4eic::Cluster` | — |
| out `outputLinks` | `edm4eic::MCRecoClusterParticleLink` | optional |
| out `outputAssociations` | `edm4eic::MCRecoClusterParticleAssociation` | optional |

By convention the output collection is named `…ClustersWithoutShapes`,
because [`CalorimeterClusterShape`](calorimeter-cluster-shape.html) runs
immediately afterwards and re-emits the collection under its final name.

## The energy sum and the sampling-fraction correction

A protocluster stores hits *and* a per-hit weight (a fractional membership
used by the splitting clusterisers). The reconstructed energy is the
weight-scaled sum of the hit energies
([`CalorimeterClusterRecoCoG.cc#L114-L127`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L114-L127)):

```
E_total = Σ_i  E_hit,i · w_proto,i
E_cluster = E_total / sampFrac
```

In a sampling calorimeter only a fraction of the shower energy is deposited
in the active medium, so the measured sum must be divided by the sampling
fraction to recover the incident energy. In ePIC this correction is normally
applied one stage earlier, per hit, by
[`CalorimeterHitReco`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc)
(which supports a cellID-dependent string expression, e.g. per-layer sampling
fractions). Those detectors therefore leave `sampFrac = 1.0` here. Only two
subsystems apply it at cluster level instead — the forward HCal insert
(`0.0257`) and the ZDC HCal (`0.0273`) — and for those the cluster energy is
scaled up by a factor ~39 and ~37 relative to the raw hit sum. `energyError`
is unconditionally set to zero
([`#L128`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L128)).

## Energy weighting schemes

The position is a weighted centroid of the hit positions. The weight
function is chosen at `init()` by the case-insensitive string
`energyWeight`; exactly **three** schemes exist, defined as free functions in
[`CalorimeterClusterRecoCoG.h#L36-L47`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.h#L36-L47):

| `energyWeight` | function | weight of hit *i* |
|---|---|---|
| `"none"` | `constWeight` | `w = 1` |
| `"linear"` | `linearWeight` | `w = E_i` |
| `"log"` | `logWeight` | `w = max(0, logWeightBase + ln(E_i / E_total))` |

An unrecognised string is a fatal misconfiguration in practice: `init()`
logs an error listing the valid keys and returns without assigning
`weightFunc`
([`.cc#L40-L52`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L40-L52)).

The centroid is then
([`.cc#L145-L157`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L145-L157)):

```
x_cluster = Σ_i w_i · x_hit,i  /  Σ_i w_i
```

If `Σ w = 0` the algorithm emits *"zero total weights encountered, you may
want to adjust your weighting parameter"* and **drops the cluster entirely**
([`.cc#L153-L156`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L153-L156)).
With log weighting that happens whenever every hit satisfies
`E_i / E_total < exp(−logWeightBase)`, which is why the base is not a free
knob.

### Why logarithmic weighting

The transverse profile of an electromagnetic shower falls off roughly
exponentially with distance from the axis. Linear (energy) weighting is
therefore biased: the few very energetic cells at the core dominate the sum
and the reconstructed centroid is pulled toward the cell centre containing
the maximum, producing the familiar "S-curve" bias across a cell. Constant
weighting has the opposite failure — it treats a 1 MeV tail hit like a 1 GeV
core hit and lets the ragged shower periphery dominate. The logarithm sits
between the two: because position depends linearly on the *logarithm* of the
energy, and the energy falls exponentially with distance, the weights become
approximately linear in distance, which is what an unbiased centroid needs.
The `max(0, …)` clip is the second half of the scheme: it assigns zero weight
to every hit below `E_total · exp(−logWeightBase)`, so noise and the
low-energy tail are cut off rather than smeared into the centroid. Increasing
`logWeightBase` widens the effective integration window (more hits survive
the clip and the weights flatten); decreasing it tightens the centroid onto
the core. Values in the plugins run from 3.6 to 6.2.

{: .note }
The source states only *"Logarithmic weighting is used for mimicking energy
deposit in transverse direction"*
([`.h#L6`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.h#L6));
there is no comment in EICrecon giving the derivation or the origin of the
per-detector base values. The paragraph above is standard calorimeter
reasoning, not a claim quoted from the repository.

### Energy-dependent `logWeightBase`

The optimal base is not energy-independent — a higher-energy shower has a
larger dynamic range between the core cell and the tail, so a fixed clip
throws away a different fraction of the shower at 5 GeV than at 200 GeV. The
algorithm can therefore compute the base per cluster from a polynomial in the
logarithm of the cluster energy
([`.cc#L136-L143`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L136-L143),
documented at
[`CalorimeterClusterRecoCoGConfig.h#L19-L24`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoGConfig.h#L19-L24)):

```
l    = ln( E_cluster / logWeightBase_Eref )
base = Σ_k  logWeightBaseCoeffs[k] · l^k
```

If `logWeightBaseCoeffs` is empty — the default, and the case for 27 of the
28 instances — the scalar `logWeightBase` is used instead, "for backwards
compatibility". Note that `E_cluster` here is the **sampling-fraction
corrected** energy, since it is read back via `cl.getEnergy()` after
`setEnergy()`.

The one production user is the ZDC hadronic section
([`ZDC.cc#L230-L244`](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L230-L244)),
with `logWeightBaseCoeffs = {5.8, 0.65, 0.31}` and
`logWeightBase_Eref = 50 GeV`, i.e.
`base(E) = 5.8 + 0.65·l + 0.31·l²`. That gives base ≈ 5.8 at 50 GeV,
≈ 5.9 at 5 GeV and ≈ 8.9 at 500 GeV — a wider effective integration window
for the more penetrating, more spread-out high-energy hadronic showers.
No comment in the source records how the three coefficients were fitted.

## Time and hit bookkeeping

The cluster time is an energy-weighted mean of the hit times, accumulated
incrementally inside the same loop as the energy sum
([`.cc#L114-L130`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L114-L130)):

```
time ← time + (t_hit,i − time) · E_i / E_total,running
```

which for a full pass is algebraically `Σ E_i t_i / Σ E_i`. **`timeError` is
initialised to zero and never updated** — clusters always carry
`timeError = 0` (see caveats, where the accumulator type is also a problem).

Alongside this the algorithm fills the cluster's hit bookkeeping:

- `nhits` = number of hits in the protocluster, set up front
  ([`.cc#L98`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L98));
- `hits` — a relation to every contributing `edm4eic::CalorimeterHit`;
- `hitContributions` — one float per hit, the weight-scaled energy
  `E_hit,i · w_proto,i` that this hit contributed to the cluster energy
  ([`.cc#L121-L122`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L121-L122)).

Empty protoclusters are skipped before anything is written
([`.cc#L72-L75`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L72-L75)).

## Optional η bounding

`enableEtaBounds` guards against a centroid landing outside the angular
footprint of its own hits, which happens at the edges of endcap discs where
the weighted mean of a one-sided hit distribution can leave the acceptance.
If the cluster η exceeds the maximum (or falls below the minimum) hit η, the
position is re-projected: the radius and φ are kept, and θ is replaced by the
angle corresponding to the clipped η
([`.cc#L161-L173`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L161-L173)).
Only two instances enable it, both forward (`EcalEndcapPTruthClusters…`,
`HcalEndcapPInsertTruthClusters…`).

`positionError` is left empty with an explicit `@TODO: Covariance matrix`
([`.cc#L158`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L158)).

## MC-truth association

When the optional `MCRecoCalorimeterHitLink` input is present and non-empty,
the algorithm also emits cluster ↔ MCParticle links and associations. The
logic is spelled out in the source
([`.cc#L183-L194`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L183-L194)):

1. For each reconstructed hit in the cluster, follow its raw hit through a
   `podio::LinkNavigator` to the `edm4hep::SimCalorimeterHit`s behind it, and
   accumulate `eSimHitSum`, the total simulated energy under the cluster.
2. For every `CaloHitContribution` of every such sim hit, walk the MC parent
   chain back to the **primary**: `get_primary()` climbs `getParents(0)`
   until it reaches a particle with `generatorStatus != 0` or one with no
   parents
   ([`.cc#L268-L284`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L268-L284)).
   The contributed energy is accumulated per primary in a map.
3. Emit **one link and one association per contributing primary**, with
   `weight = E_contributed_by_primary / eSimHitSum`
   ([`.cc#L245-L265`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L245-L265)).

{: .note }
The algorithm does **not** pick a single dominant contributor. Every primary
that deposited anything in the cluster gets its own link, and the weights sum
to approximately one; selecting the dominant one (largest weight) is left to
the consumer. `get_primary()` carries a `TODO finalize primary selection.
This can be improved!!` in the source.

Links and associations carry identical information — the association type is
the older podio one-to-one relation, the link type the newer
`podio::Link`; both are written so that downstream code can use either.

## Configuration

Struct:
[`CalorimeterClusterRecoCoGConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoGConfig.h).

| field | struct default | meaning |
|---|---|---|
| `energyWeight` | *(none — default-constructed empty `std::string`)* | weighting scheme; one of `none`, `linear`, `log` (case-insensitive) |
| `sampFrac` | `1.` | sampling fraction; cluster energy is the hit sum **divided** by this |
| `logWeightBase` | `3.6` | the `w0` in `max(0, w0 + ln(E_i/E_tot))`; ignored when `logWeightBaseCoeffs` is non-empty |
| `logWeightBaseCoeffs` | `{}` (empty) | polynomial coefficients in `l = ln(E_cluster/logWeightBase_Eref)` giving an energy-dependent base; empty means use `logWeightBase` |
| `logWeightBase_Eref` | `50 * dd4hep::MeV` → **50 MeV** | reference energy of that polynomial |
| `enableEtaBounds` | `false` | clamp the cluster η to the η range of its contributing hits (endcap edge effects) |

JANA runtime flag names differ slightly from the field names — the factory
binds `sampFrac` as **`samplingFraction`**
([`CalorimeterClusterRecoCoG_factory.h#L32-L39`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/CalorimeterClusterRecoCoG_factory.h#L32-L39)).
The full set is
`energyWeight`, `samplingFraction`, `logWeightBase`, `logWeightBaseCoeffs`,
`logWeightBase_Eref`, `enableEtaBounds`, addressed as
`<PLUGIN>:<InstanceName>:<flag>`, e.g.
`BEMC:EcalBarrelScFiClustersWithoutShapes:logWeightBase`.

## Which detectors use it

Every instance in the tree, from
`grep -rn CalorimeterClusterRecoCoG_factory src/detectors/`. **All 28 use
`energyWeight = "log"`** — `none` and `linear` have no production user.
Unless noted, `sampFrac = 1.0` (the correction is already applied per hit by
`CalorimeterHitReco`) and `enableEtaBounds = false`.

| plugin | instance (= output collection) | `logWeightBase` | notable |
|---|---|---|---|
| [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L84-L113) | `B0ECalClustersWithoutShapes` | 3.6 | |
| B0ECAL | `B0ECalTruthClustersWithoutShapes` | 6.2 | |
| [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L299-L349) | `EcalBarrelScFiClustersWithoutShapes` | 6.2 | island protoclusters |
| BEMC | `EcalBarrelScFiTopoClustersWithoutShapes` | 6.2 | topo protoclusters |
| [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L125-L189) | `HcalBarrelClustersWithoutShapes` | 6.2 | |
| BHCAL | `HcalBarrelTruthClustersWithoutShapes` | 6.2 | |
| BHCAL | `HcalBarrelSplitMergeClustersWithoutShapes` | 6.2 | |
| [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L107-L221) | `EcalEndcapNTruthClustersWithoutShapes` | 4.6 | |
| EEMC | `EcalEndcapNClustersWithoutPIDAndShapes` | 3.6 | feeds the ONNX PID stage |
| EEMC | `EcalEndcapNSplitMergeClustersWithoutShapes` | 3.6 | |
| [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L105-L171) | `HcalEndcapNTruthClustersWithoutShapes` | 6.2 | |
| EHCAL | `HcalEndcapNClustersWithoutShapes` | 6.2 | island |
| EHCAL | `HcalEndcapNClustersWithoutShapes` *(duplicate name)* | 6.2 | split/merge — see caveats |
| [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L165-L239) | `EcalEndcapPTruthClustersWithoutShapes` | 6.2 | **`enableEtaBounds = true`** |
| FEMC | `EcalEndcapPClustersWithoutShapes` | 3.6 | |
| FEMC | `EcalEndcapPSplitMergeClustersWithoutShapes` | 3.6 | |
| [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L122-L334) | `HcalEndcapPInsertTruthClustersWithoutShapes` | 3.6 | **`sampFrac = 0.0257`**, **`enableEtaBounds = true`** |
| FHCAL | `HcalEndcapPInsertClustersWithoutShapes` | 6.2 | **`sampFrac = 0.0257`**, HEXPLIT + topo input |
| FHCAL | `LFHCALTruthClustersWithoutShapes` | 4.5 | |
| FHCAL | `LFHCALClustersWithoutShapes` | 4.5 | |
| FHCAL | `LFHCALSplitMergeClustersWithoutShapes` | 4.5 | |
| [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L89-L118) | `EcalLumiSpecClustersWithoutShapes` | 3.6 | |
| LUMISPECCAL | `EcalLumiSpecTruthClustersWithoutShapes` | 4.6 | |
| [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L93-L329) | `EcalFarForwardZDCTruthClustersWithoutShapes` | 3.6 | |
| ZDC | `EcalFarForwardZDCClustersWithoutShapes` | 6.2 | |
| ZDC | `HcalFarForwardZDCClustersWithoutShapes` | *polynomial* | **`sampFrac = 0.0273`**, `logWeightBaseCoeffs = {5.8, 0.65, 0.31}`, `logWeightBase_Eref = 50 GeV` |
| ZDC | `HcalFarForwardZDCTruthClustersWithoutShapes` | 3.6 | |
| ZDC | `HcalFarForwardZDCClustersBaselineWithoutShapes` | 6.2 | **`sampFrac = 0.0273`**, no-HEXPLIT reference chain |

Nothing in [`src/global/`](https://github.com/eic/EICrecon/tree/main/src/global)
instantiates this algorithm — it is purely per-subsystem.

## Source

- Algorithm: [`src/algorithms/calorimetry/CalorimeterClusterRecoCoG.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.h)
  · [`.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc)
- Config: [`CalorimeterClusterRecoCoGConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoGConfig.h)
- JANA factory: [`src/factories/calorimetry/CalorimeterClusterRecoCoG_factory.h`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/CalorimeterClusterRecoCoG_factory.h)
- Unit test: [`src/tests/algorithms_test/calorimetry_CalorimeterClusterRecoCoG.cc`](https://github.com/eic/EICrecon/blob/main/src/tests/algorithms_test/calorimetry_CalorimeterClusterRecoCoG.cc)

## Caveats / needs human verification

1. **The time accumulator is an `int`.**
   [`.cc#L112`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L112)
   declares `auto time = 0;`, which deduces `int`, not `float`. Every
   `time += (…)` therefore truncates toward zero, so the cluster time is
   quantised to whole units of the EDM time unit (ns) and small positive
   times collapse to 0. This looks unintended and should be confirmed with
   a maintainer.
2. **`timeError` is always zero.**
   [`.cc#L113`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L113)
   declares `auto timeError = 0;` (also `int`) and it is never assigned
   before `cl.setTimeError(timeError)`. Same for `energyError`, and
   `positionError` is an explicit `@TODO`.
3. **`maxHitEta` is seeded with `std::numeric_limits<float>::min()`**
   ([`.cc#L111`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L111)),
   which is the smallest *positive* normal float (~1.2e-38), not the most
   negative value. For a cluster whose hits all have negative η the running
   maximum never drops below ~0, so `enableEtaBounds` cannot clamp an
   overflow there. Both instances that enable the option are in the
   positive-η (forward) endcap, so this is currently latent — but it would
   bite if the option were switched on for EEMC or the backward HCal.
4. **`energyWeight` has no struct default.** It is a default-constructed
   empty string, which `init()` cannot match; the algorithm logs an error and
   leaves `weightFunc` unset, so the first `process()` call throws
   `std::bad_function_call`. Every production instance sets it explicitly, so
   this only affects new code paths and tests.
5. **The `mcRawHitAssocations` input is accepted but unused.** It is marked
   `[[maybe_unused]]` in `associate()`
   ([`.cc#L177-L182`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L177-L182));
   only the link collection is navigated. The misspelling
   (`mcRawHitAssocations`) is in the source.
6. **Duplicate instance name in EHCAL.** Two `CalorimeterClusterRecoCoG`
   generators are registered as `HcalEndcapNClustersWithoutShapes`
   ([`EHCAL.cc#L123`](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L123)
   and
   [`#L157`](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L157))
   with different inputs and outputs; the second is evidently meant to be
   `HcalEndcapNSplitMergeClustersWithoutShapes`. Their configs are identical
   so results are unaffected, but the JANA flag prefix collides, so
   `EHCAL:HcalEndcapNClustersWithoutShapes:logWeightBase` is ambiguous.
7. **The per-detector `logWeightBase` values (3.6 / 4.5 / 4.6 / 6.2) have no
   provenance comment** anywhere in EICrecon: no reference to the simulation
   study or geometry version they were tuned against. Same for the ZDC
   polynomial coefficients and the two cluster-level sampling fractions.
8. `eSimHitSum` is accumulated per *cluster hit*, so a sim hit linked to more
   than one reconstructed hit is counted more than once in the denominator of
   the association weights
   ([`.cc#L211-L221`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterRecoCoG.cc#L211-L221)).
   With the standard one-raw-hit-per-cell links this cannot happen; whether
   any ePIC digitisation produces such a many-to-many link map is not
   determinable from this file.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
(fetched 2026-08-19). AI-authored draft — verify against source.*
