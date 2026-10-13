---
title: CalorimeterClusterShape
parent: EICrecon
nav_order: 35
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# CalorimeterClusterShape — shower shape observables

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

`CalorimeterClusterShape` is a decorator stage. It consumes clusters that
already have an energy and a position — from
[`CalorimeterClusterRecoCoG`](calorimeter-cluster-reco-cog.html),
[`ImagingClusterReco`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/ImagingClusterReco.cc)
or the two
[cluster mergers](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EnergyPositionClusterMerger.cc)
— computes the second moments of the hit distribution, and **re-emits the
whole collection** with those numbers attached. Because podio collections are
immutable once written, decorating in place is impossible; the algorithm
clones each cluster instead
([`CalorimeterClusterShape.cc#L78`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L78)).
That is the reason every ePIC cluster collection has a `…WithoutShapes` twin:
the twin is the upstream producer's output, and the plain name is this
algorithm's.

Its own doc comment
([`.h#L34-L40`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.h#L34-L40)):

*"An algorithm which takes a collection of clusters, computes their cluster
shape parameters, and saves outputs the same clusters with computed
parameters."*

and the list it advertises
([`.cc#L50-L60`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L50-L60)):

*"Parameters calculated: radius, dispersion (energy weighted radius),
theta-phi cluster widths (2D), x-y-z cluster widths (3D)."*

Physically these are the handles that separate an electromagnetic shower from
a hadronic one and a single shower from two overlapping ones: an EM shower is
short and narrow, a hadronic shower long and broad, and the principal-axis
decomposition gives both the direction the shower travelled and how wide it
is transverse to that direction.

## Inputs and outputs

Declared in
[`CalorimeterClusterShape.h#L27-L32`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.h#L27-L32):

| slot | type |
|---|---|
| in `inputClusters` | `edm4eic::Cluster` |
| in `inputMCClusterAssociations` | `edm4eic::MCRecoClusterParticleAssociation` |
| out `outputClusters` | `edm4eic::Cluster` |
| out `outputMCClusterLinks` | `edm4eic::MCRecoClusterParticleLink` |
| out `outputMCClusterAssociations` | `edm4eic::MCRecoClusterParticleAssociation` |

The MC associations are not recomputed — they are copied across from the
input cluster to its clone, preserving the weight
([`.cc#L231-L243`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L231-L243)),
and re-emitted in both the (older) association and the (newer) link form.

## Energy weighting

Shape moments need a weight per hit, and the same three schemes as the
centre-of-gravity algorithm are available — the functions are duplicated as
private statics
([`.h#L58-L71`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.h#L58-L71)):

| `energyWeight` | weight of hit *i* |
|---|---|
| `"none"` (default) | `w = 1` |
| `"linear"` | `w = E_i` |
| `"log"` | `w = max(0, logWeightBase + ln(E_i / E_total))` |

The denominator is reconstructed as
`E_total = cluster.getEnergy() · sampFrac`
([`.cc#L113-L114`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L113-L114)).
This is the point of the `sampFrac` field, and the config header says so
explicitly
([`CalorimeterClusterShapeConfig.h#L20-L26`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShapeConfig.h#L20-L26)):
*"if the fraction is applied after clustering, this parameter can be used to
determine the total energy of the cluster before applying the fraction, which
is a necessary input for the log-weight calculation."* The hit energies are
raw, so the cluster energy has to be un-corrected before the ratio
`E_i / E_total` is meaningful — otherwise every log weight is shifted by
`ln(sampFrac)`, which for a ~2.7 % sampling fraction is −3.6, enough to clip
the entire cluster to zero weight. `sampFrac` here **must therefore match the
`sampFrac` of the upstream `CalorimeterClusterRecoCoG` instance** (see
caveats — one instance does not).

The energy-dependent base works exactly as in the CoG algorithm
([`.cc#L81-L88`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L81-L88)):
with a non-empty `logWeightBaseCoeffs`,
`base = Σ_k coeffs[k]·l^k` where `l = ln(E_cluster / logWeightBase_Eref)`;
otherwise the scalar `logWeightBase` is used.

## What is computed

Everything happens in a single pass over the cluster's hits, and **only if
`nhits > 1`**
([`.cc#L109-L134`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L109-L134)).
For each hit, with `Δ = x_cluster − x_hit`:

**Radius** — the unweighted RMS distance of the hits from the cluster
centroid, normalised like a sample standard deviation
([`.cc#L122`, `#L136`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L136)):

```
radius = sqrt( (1/(nhits − 1)) · Σ_i |Δ_i|² )
```

**Dispersion** — the same quantity weighted by the hit weights, i.e. the
*energy-weighted* shower radius
([`.cc#L123`, `#L138`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L138)):

```
dispersion = sqrt( Σ_i w_i |Δ_i|² / Σ_i w_i )
```

Radius is a geometric measure ("how far do the lit cells extend"),
dispersion an energy-flow measure ("where is the energy actually sitting").
A hadronic shower with a few far-flung satellite cells has a large radius but
a much smaller dispersion; a broad EM shower has the two close together.

**Covariance and principal axes** — the algorithm accumulates the weighted
first and second moments of the hit positions in two coordinate systems
([`.cc#L117-L133`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L117-L133)):
a 2-vector `(θ, φ)` of the hit direction, and the 3-vector `(x, y, z)`. After
normalising by `Σ w`, the covariance matrices are formed as
`cov = ⟨x xᵀ⟩ − ⟨x⟩⟨x⟩ᵀ`
([`.cc#L146-L148`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L146-L148))
and diagonalised with `Eigen::SelfAdjointEigenSolver`, which is used
deliberately: for a symmetric real matrix it guarantees real eigenvalues and
returns them sorted ascending
([`.cc#L150-L166`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L150-L166)).
The eigenvalues are then re-ordered **descending** for storage.

The eigenvalues are variances: their square roots are the RMS widths of the
shower along the three principal directions. The largest is the shower
*length* (along the direction of travel, since a shower is longer than it is
wide), the two smaller ones the transverse widths. For a detector with no
depth segmentation the smallest 3D eigenvalue is essentially zero — the
source notes this inline: *"smallest (0 for flat-z detectors)"*
([`.cc#L165`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L165)).

**Shower axis and intrinsic direction** — the axis is the eigenvector of the
largest 3D eigenvalue
([`.cc#L167-L173`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L167-L173)).
An eigenvector has no intrinsic sign, so it is flipped when necessary to
point away from the interaction point — `position · axis < 0` triggers a
negation
([`.cc#L203-L207`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L203-L207)).
The polar and azimuthal angles of that axis become `intrinsicTheta` and
`intrinsicPhi`
([`.cc#L209-L213`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L209-L213)).
These are the shower's *own* direction, as opposed to the θ/φ of the cluster
centroid seen from the origin — the difference is the pointing information
that lets a longitudinally segmented calorimeter tell a photon from the
interaction point apart from one from a displaced decay. `intrinsicDirectionError`
is an explicit `TODO` and is not filled.

## `shapeParameters`: index → meaning

Seven values are appended, always in this order, for every cluster
([`.cc#L177-L186`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L177-L186)):

| index | quantity | units |
|---|---|---|
| `0` | `radius` — unweighted RMS hit distance from the centroid | mm |
| `1` | `dispersion` — weighted RMS hit distance (energy-weighted radius) | mm |
| `2` | 2D θ-φ width 1 — **largest** eigenvalue of the (θ, φ) covariance | rad² |
| `3` | 2D θ-φ width 2 — smallest eigenvalue of the (θ, φ) covariance | rad² |
| `4` | 3D x-y-z width 1 — **largest** eigenvalue of the (x, y, z) covariance | mm² |
| `5` | 3D x-y-z width 2 — middle eigenvalue | mm² |
| `6` | 3D x-y-z width 3 — smallest eigenvalue (≈ 0 for unsegmented depth) | mm² |

{: .warning }
Indices 2–6 are **raw covariance-matrix entries** — squared quantities. Only
indices 0 and 1 are already lengths. The source flags this: *"shapeParameters
stores raw covariance-matrix values ([mm^2], [rad^2]), kept as-is for backward
compatibility. shapeParameters will go away eventually."*
([`.cc#L177-L179`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L177-L179))

Consumers in the tree confirm the mapping:
[`FarForwardNeutralsReconstruction`](https://github.com/eic/EICrecon/blob/main/src/algorithms/reco/FarForwardNeutralsReconstruction.cc#L39-L43)
reads indices 4, 5, 6 and takes their square roots to get the three principal
lengths of a ZDC cluster for its photon/neutron separation cut;
[`CalorimeterParticleIDPreML`](https://github.com/eic/EICrecon/blob/main/src/algorithms/onnx/CalorimeterParticleIDPreML.cc#L67-L69)
feeds the whole vector, in order, into the EEMC PID network's feature tensor
— so the count and order are part of that model's input contract.

### The typed members (edm4eic ≥ 8.10)

When built against edm4eic 8.10 or newer, the same numbers are also written
to dedicated, correctly-dimensioned members
([`.cc#L188-L201`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L188-L201)):
`radius`, `dispersion`, `principalAxesLengthsXYZ` (3 floats) and
`principalAxesLengthsThetaPhi` (2 floats). Unlike `shapeParameters`, the
principal-axes members hold `sqrt(|eigenvalue|)`, i.e. widths in mm and rad.
This is the replacement path for `shapeParameters`; the block is compiled out
for older event models (EICrecon's minimum is edm4eic 8.7,
[`CMakeLists.txt#L63`](https://github.com/eic/EICrecon/blob/main/CMakeLists.txt#L63)).

### `longitudinalShowerInfoAvailable`

The config carries a documented switch — *"determines if intrinsic theta/phi
are calculated"*
([`CalorimeterClusterShapeConfig.h#L14-L15`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShapeConfig.h#L14-L15))
— which the JANA factory exposes as a runtime parameter
([`CalorimeterClusterShape_factory.h#L33-L34`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/CalorimeterClusterShape_factory.h#L33-L34))
and which 14 of the 29 instances set explicitly.

**At this commit the algorithm never reads it.** `grep -rn
longitudinalShowerInfoAvailable src/` returns only the config struct, the
factory binding, the detector plugins and the unit test — there is no
reference anywhere in
[`CalorimeterClusterShape.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc).
`intrinsicTheta` / `intrinsicPhi` are computed and set unconditionally, and no
other quantity is gated. The name and the BEMC imaging instance
(the one place it is deliberately set to `false`,
[`BEMC.cc#L448`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L448))
suggest the intent is to suppress the pointing angles for detectors without
depth segmentation, where the "longest axis" is an artefact of the readout
plane rather than the shower direction. That intent is currently not
implemented; treat `intrinsicTheta`/`intrinsicPhi` as always present and
judge their meaningfulness from the detector, not the flag.

## Configuration

Struct:
[`CalorimeterClusterShapeConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShapeConfig.h).

| field | struct default | meaning |
|---|---|---|
| `longitudinalShowerInfoAvailable` | `false` | documented as "determines if intrinsic theta/phi are calculated" — **not read by the algorithm at this commit** |
| `energyWeight` | `"none"` | weighting scheme for the moments; `none`, `linear` or `log` (case-insensitive) |
| `sampFrac` | `1.` | sampling fraction, used only to undo the cluster-level correction when forming `E_total` for the log weights |
| `logWeightBaseCoeffs` | `{}` (empty) | polynomial coefficients in `l = ln(E_cluster/logWeightBase_Eref)` for an energy-dependent base; empty means use `logWeightBase` |
| `logWeightBase_Eref` | `50 * dd4hep::MeV` → **50 MeV** | reference energy of that polynomial |
| `logWeightBase` | `3.6` | the `w0` in `max(0, w0 + ln(E_i/E_tot))` |

All six are bound as JANA flags under the same names — note that here the
sampling fraction keeps its field name `sampFrac`, whereas the CoG factory
renames it to `samplingFraction`
([`CalorimeterClusterShape_factory.h#L33-L41`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/CalorimeterClusterShape_factory.h#L33-L41)).
Address them as `<PLUGIN>:<InstanceName>:<flag>`, e.g.
`ZDC:HcalFarForwardZDCClusters:logWeightBase_Eref`.

## Which detectors use it

29 instances across nine plugins — one for essentially every persisted
cluster collection in ePIC. Unless noted, `sampFrac` is left at its default
`1.0` and `logWeightBaseCoeffs` is empty. "longit." is
`longitudinalShowerInfoAvailable`.

| plugin | instance (= output collection) | `energyWeight` / base | longit. | notable |
|---|---|---|---|---|
| [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L97-L120) | `B0ECalClusters` | log / 3.6 | *(unset)* | |
| B0ECAL | `B0ECalTruthClusters` | log / 6.2 | *(unset)* | |
| [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L312-L316) | `EcalBarrelScFiClusters` | log / 6.2 | true | |
| [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L350-L356) | `EcalBarrelScFiTopoClusters` | log / 6.2 | true | |
| [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L442-L449) | `EcalBarrelImagingClusters` | log / 6.2 | **false** | input from `ImagingClusterReco` |
| [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L463-L467) | `EcalBarrelClusters` | log / 6.2 | true | input from `EnergyPositionClusterMerger` |
| [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L476-L481) | `EcalBarrelTruthClusters` | log / 6.2 | true | input from the truth merger |
| [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L138-L196) | `HcalBarrelClusters` | log / 6.2 | *(unset)* | |
| BHCAL | `HcalBarrelTruthClusters` | log / 6.2 | *(unset)* | |
| BHCAL | `HcalBarrelSplitMergeClusters` | log / 6.2 | *(unset)* | |
| [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L120-L230) | `EcalEndcapNTruthClusters` | log / 4.6 | *(unset)* | |
| EEMC | `EcalEndcapNClustersWithoutPID` | log / 3.6 | *(unset)* | shapes feed the ONNX PID tensor |
| EEMC | `EcalEndcapNSplitMergeClusters` | log / 3.6 | *(unset)* | |
| [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L117-L179) | `HcalEndcapNTruthClusters` | log / 6.2 | *(unset)* | |
| EHCAL | `HcalEndcapNClusters` | log / 6.2 | *(unset)* | |
| EHCAL | `HcalEndcapNSplitMergeClusters` | log / 6.2 | *(unset)* | |
| [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L178-L247) | `EcalEndcapPTruthClusters` | log / 6.2 | *(unset)* | |
| FEMC | `EcalEndcapPClusters` | log / 3.6 | *(unset)* | |
| FEMC | `EcalEndcapPSplitMergeClusters` | log / 3.6 | *(unset)* | |
| [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L136-L141) | `HcalEndcapPInsertTruthClusters` | log / 3.6 | true | **`sampFrac` left at 1.0 though upstream CoG uses 0.0257 — see caveats** |
| [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L162-L172) | `HcalEndcapPInsertClusters` | log / 6.2 | true | **`sampFrac = 0.0257`** |
| FHCAL | `LFHCALTruthClusters` | log / 4.5 | true | |
| FHCAL | `LFHCALClusters` | log / 4.5 | true | |
| [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L336-L341) | `LFHCALSplitMergeClusters` | **none / —** | true | only the longit. flag is set, so weighting falls back to the `"none"` default |
| [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L101-L125) | `EcalLumiSpecClusters` | log / 3.6 | *(unset)* | |
| LUMISPECCAL | `EcalLumiSpecTruthClusters` | log / 4.6 | *(unset)* | |
| [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L107-L138) | `EcalFarForwardZDCTruthClusters` | log / 3.6 | true | |
| ZDC | `EcalFarForwardZDCClusters` | log / 6.2 | true | |
| [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L246-L257) | `HcalFarForwardZDCClusters` | log / *polynomial* | true | **`sampFrac = 0.0273`**, `logWeightBaseCoeffs = {5.8, 0.65, 0.31}`, `logWeightBase_Eref = 50 GeV`; shapes consumed by `FarForwardNeutralsReconstruction` |
| ZDC | `HcalFarForwardZDCTruthClusters` | log / 3.6 | true | |
| [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L330-L341) | `HcalFarForwardZDCClustersBaseline` | log / 6.2 | true | **`sampFrac = 0.0273`** |

Nothing in [`src/global/`](https://github.com/eic/EICrecon/tree/main/src/global)
instantiates this algorithm.

## Source

- Algorithm: [`src/algorithms/calorimetry/CalorimeterClusterShape.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.h)
  · [`.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc)
- Config: [`CalorimeterClusterShapeConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShapeConfig.h)
- JANA factory: [`src/factories/calorimetry/CalorimeterClusterShape_factory.h`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/CalorimeterClusterShape_factory.h)
- Unit test: [`src/tests/algorithms_test/calorimetry_CalorimeterClusterShape.cc`](https://github.com/eic/EICrecon/blob/main/src/tests/algorithms_test/calorimetry_CalorimeterClusterShape.cc)
- Consumers: [`FarForwardNeutralsReconstruction.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/reco/FarForwardNeutralsReconstruction.cc#L39-L43),
  [`CalorimeterParticleIDPreML.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/onnx/CalorimeterParticleIDPreML.cc#L67-L69)

## Caveats / needs human verification

1. **`longitudinalShowerInfoAvailable` is dead at this commit** — configured
   in 14 places, exposed as a runtime flag, documented in the config header,
   and never read by the algorithm. See the section above. Flipping it has no
   effect on the output today.
2. **`HcalEndcapPInsertTruthClusters` looks misconfigured.** Its upstream
   `CalorimeterClusterRecoCoG` uses `sampFrac = 0.0257`
   ([`FHCAL.cc#L132`](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L132))
   but the shape instance leaves `sampFrac` at the default `1.0`
   ([`FHCAL.cc#L136-L141`](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L136-L141)).
   `E_total` is then ~39× too large, so every log weight becomes
   `max(0, 3.6 − 3.66 + ln(E_i/ΣE))`, which is zero for every hit. With
   `w_sum = 0` the whole `if (w_sum > 0)` block is skipped
   ([`.cc#L137`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L137)):
   dispersion, all five eigenvalues, the axis and both intrinsic angles stay
   at zero, and only `radius` is filled. The sibling
   `HcalEndcapPInsertClusters` does set `sampFrac = 0.0257`, matching its
   own CoG instance, which is what makes the truth chain look like an
   omission. Needs a maintainer's confirmation — this is inferred from the
   code, not observed in output.
3. **`LFHCALSplitMergeClusters` uses constant weighting.** Its config is
   `{.longitudinalShowerInfoAvailable = true}` only
   ([`FHCAL.cc#L336-L341`](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L336-L341)),
   so `energyWeight` falls back to the struct default `"none"` while its two
   LFHCAL siblings use `log` with base 4.5. Its dispersion and widths are
   therefore not comparable with theirs. Probably an oversight.
4. **The protocluster hit weights are ignored here.** `CalorimeterClusterRecoCoG`
   weights each hit by its protocluster membership fraction
   (`E_i · w_proto,i`, also stored in `hitContributions`), but the shape
   algorithm uses the bare `hit.getEnergy()`
   ([`.cc#L114`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L114)).
   For split clusters, whose hits are shared fractionally between the pieces,
   the shape moments are therefore computed from unsplit hit energies.
5. **The φ covariance has no wrap-around handling.** `angleAzimuthal` returns
   φ in (−π, π]; a cluster straddling that branch cut contributes hits at
   both ends of the range, inflating the 2D θ-φ widths (indices 2 and 3)
   arbitrarily. Nothing in the code compensates. This affects barrel and
   endcap clusters near φ = ±π.
6. **The association input is dereferenced without a null check.**
   The algorithm's declared signature makes `inputMCClusterAssociations`
   `std::optional`
   ([`.h#L27-L32`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.h#L27-L32))
   but `process()` does `for (auto in_assoc : *in_associations)`
   ([`.cc#L231`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L231))
   with no guard. The JANA factory declares the input as non-optional, so in
   the standard pipeline it is always present; a direct algorithm caller
   passing `nullptr` (real data, no MC) would crash.
7. **Single-hit clusters get seven zeros.** The moment block is guarded by
   `nhits > 1`
   ([`.cc#L109`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterClusterShape.cc#L109)),
   but the seven `shapeParameters` are appended unconditionally, and the axis
   is a default-constructed `(0,0,0)` — so `intrinsicTheta`/`intrinsicPhi`
   are the angles of a null vector. Consumers must not read a zero width as a
   measured zero.
8. **`radius` and `dispersion` use different normalisations** — `1/(nhits−1)`
   versus `1/Σw`. With `energyWeight = "none"` the two differ by
   `sqrt(nhits/(nhits−1))` rather than being identical, which is deliberate
   for a sample RMS but easy to trip over when comparing them.
9. `addToShapeParameters` **appends**. No producer in the tree fills
   `shapeParameters` before this stage, so the index map above holds for
   every ePIC collection today — but running the algorithm twice on the same
   collection, or introducing a producer that pre-fills the vector, would
   silently shift every index.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
(fetched 2026-08-19). AI-authored draft — verify against source.*
