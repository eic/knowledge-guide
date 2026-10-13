---
title: Particle identification
parent: EICrecon
nav_order: 11
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# Particle identification in EICrecon

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

ePIC identifies charged hadrons and electrons with four systems: the **dRICH**
in the hadron endcap (a dual-radiator ring-imaging Cherenkov counter, aerogel
for low momentum plus a heavy gas for high momentum), the **pfRICH** in the
electron endcap, the **hpDIRC** in the barrel, and the barrel/endcap **TOF**
layers. Calorimeter **E/p** adds electron/hadron separation on top.

EICrecon does **not** treat these uniformly. Only the dRICH has a real
reconstruction chain — digitized photon hits are fed to the IRT (indirect ray
tracing) library, which produces `edm4eic::CherenkovParticleID` objects with a
likelihood per mass hypothesis per radiator. Everything else — pfRICH, TOF,
hpDIRC, **and the dRICH again** — is served by a parametrised **lookup table**
(`pid_lut`), which reads a pre-computed identification probability out of a
5-dimensional table and throws a die. The hpDIRC has **no** reconstruction
algorithm in EICrecon at all; its plugin stops at digitized hits. Calorimeter
E/p never becomes a `ParticleID` object; it is only a selection cut used to
build `ReconstructedElectrons`.

Both `pid` (IRT-based) and `pid_lut`/`global_pid_lut` (table-based) are in the
default plugin list
([`eicrecon.cc#L15-L56`](https://github.com/eic/EICrecon/blob/main/src/utilities/eicrecon/eicrecon.cc#L15-L56)),
so a standard reconstruction run produces both — into **different** particle
collections. Which one you read is the single most important choice on this
page.

## Where PID lives in the output

### The `edm4hep::ParticleID` datatype

One `ParticleID` object = **one mass hypothesis for one track**. Its fields:

| field | type | what EICrecon puts there |
|---|---|---|
| `PDG` | `int32` | signed PDG code of the hypothesis (11, 211, 321, 2212 and their antiparticles) |
| `likelihood` | `float` | LUT path: the tabulated identification probability. IRT path: the raw IRT hypothesis weight (a log-likelihood-like number, **not** normalised) |
| `type` | `int32` | LUT path: the DD4hep detector-system constant (`BarrelDIRC_ID`, `ForwardRICH_ID`, …) — i.e. *which detector said this*. IRT path: hard-coded `0` |
| `algorithmType` | `int32` | always `0` in both paths — marked `FIXME: not used yet` |
| `parameters` | `vector<float>` | IRT path: `parameters[0]` is the number of photoelectrons supporting this hypothesis. LUT path: empty |

Sources: LUT fill
[`PIDLookup.cc#L113-L136`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid_lut/PIDLookup.cc#L113-L136),
IRT conversion
[`ConvertParticleID.h#L61-L70`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/ConvertParticleID.h#L61-L70).

### The two relations on `ReconstructedParticle`

`edm4eic::ReconstructedParticle` carries

- **`particleIDs`** — a one-to-many relation to *all* hypotheses attached to
  this particle, and
- **`particleIDUsed`** — a single relation pointing at the one hypothesis that
  was actually adopted (and whose PDG was written into `ReconstructedParticle::PDG`).

`goodnessOfPID` is a float that is initialised to `0` when the track is turned
into a particle
([`TracksToParticles.cc#L40-L48`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TracksToParticles.cc#L40-L48),
comment: *"assume no PID until proven otherwise"*) and set to `1` by the IRT
matcher with the comment *"FIXME: not used yet, aside from 0=noPID vs
1=hasPID"*
([`MatchToRICHPID.cc#L160`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/MatchToRICHPID.cc#L160)).
**The LUT path never touches it**, so on the default
`ReconstructedChargedParticles` collection `goodnessOfPID` is `0` even for
particles that do have PID. Do not use it as a "has PID" flag; test
`getParticleIDUsed().isAvailable()` instead.

### Collections you actually read

**Default (LUT) chain** — this is what ends up in `ReconstructedChargedParticles`:

```
ReconstructedChargedWithoutPIDParticles          (from tracking)
  → RICHEndcapNLUTPID   → ReconstructedChargedWithPFRICHPIDParticles      + RICHEndcapNParticleIDs
  → CombinedTOFLUTPID   → ReconstructedChargedWithPFRICHTOFPIDParticles   + CombinedTOFParticleIDs
  → DIRCLUTPID          → ReconstructedChargedWithPFRICHTOFDIRCPIDParticles + DIRCParticleIDs
  → (+ TaggerTrackerReconstructedParticles merged in)
  → DRICHLUTPID         → ReconstructedChargedParticles                   + DRICHParticleIDs
  → MatchClusters       → ReconstructedParticles
```

Each stage `clone()`s the particle from the previous stage, so the
`particleIDs` relations **accumulate**: a barrel track that crossed TOF and the
hpDIRC ends up with hypotheses from both, in separate `…ParticleIDs`
collections, all hanging off the same particle in
`ReconstructedChargedParticles`. Wiring:
[`pid_lut.cc`](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc);
a truth-seeded twin of the whole chain ends in
`ReconstructedTruthSeededChargedParticles`. `MatchClusters` then clones once
more into `ReconstructedParticles`
([`reco.cc#L92-L106`](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L92-L106)).

**IRT chain** — a parallel, *separate* particle collection:

```
DRICHHits → PhotoMultiplierHitDigi → DRICHRawHits (+Links, +Associations)
CentralCKFTracks → RichTrack ×2 → DRICHAerogelTracks, DRICHGasTracks
                 → MergeTrack   → DRICHMergedTracks
  → IrtCherenkovParticleID → DRICHAerogelIrtCherenkovParticleID
                             DRICHGasIrtCherenkovParticleID
  → MergeCherenkovParticleID → DRICHMergedIrtCherenkovParticleID
  → MatchToRICHPID → ReconstructedChargedRealPIDParticles
                     ReconstructedChargedRealPIDParticleIDs
```

Wiring: [`DRICH.cc#L119-L147`](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L119-L147)
and [`pid.cc#L22-L35`](https://github.com/eic/EICrecon/blob/main/src/global/pid/pid.cc#L22-L35).

All of the collections named above are in the default persistency list
([`JEventProcessorPODIO.cc`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L127-L146)),
including `ReconstructedChargedRealPIDParticleIDs` and
`ReconstructedChargedParticles`
([L240-L241](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L240-L241))
and the DIRC ones
([L474-L475](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L474-L475)).

### Reading the best hypothesis

```cpp
// e.g. over ReconstructedChargedParticles (LUT) or
//      ReconstructedChargedRealPIDParticles (IRT)
for (const auto& part : recoParticles) {

  if (!part.getParticleIDUsed().isAvailable()) {
    continue;                       // this track got no PID at all
  }

  const auto best = part.getParticleIDUsed();
  const int   pdg  = best.getPDG();          // signed: 11 / 211 / 321 / 2212 …
  const float like = best.getLikelihood();   // LUT: probability. IRT: raw weight
  const int   sys  = best.getType();         // LUT: detector system ID; IRT: 0

  // part.getPDG() has already been set to `pdg` by the same algorithm

  // every hypothesis that was attached to this track:
  for (const auto& hyp : part.getParticleIDs()) {
    float npe = hyp.parameters_size() > 0 ? hyp.getParameters(0) : -1;  // IRT only
    // ...
  }
}
```

The DRICH plugin README shows the same access pattern for the
association-based route
([`DRICH/README.md#L236-L245`](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/README.md#L236-L245)):

```cpp
assoc.getRec().getParticleIDUsed().getPDG();  // most likely PDG from PID
assoc.getSim().getPDG();                      // true PDG
```

{: .note }
Ordering differs between the two paths. In the IRT path `particleIDs` is
**sorted by descending likelihood**, so `getParticleIDs().at(0)` is the best
hypothesis. In the LUT path the four hypotheses are created in a fixed
electron/pion/kaon/proton order and `particleIDUsed` is set explicitly.
Always go through `particleIDUsed`, never through index 0.

## Photon side: `PhotoMultiplierHitDigi`

**Algorithm:** [`PhotoMultiplierHitDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PhotoMultiplierHitDigi.cc)
— *"General PhotoMultiplier Digitization. Apply the given quantum efficiency
for photon detection. Converts the number of detected photons to signal
amplitude."*

Each Geant4 optical-photon hit on a sensor is thrown against three
independent acceptance tests before it becomes a photoelectron
([`#L63-L97`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PhotoMultiplierHitDigi.cc#L63-L97)):
a flat `safetyFactor` survival probability; the wavelength-dependent quantum
efficiency of the SiPM, evaluated by linear interpolation of the QE table after
converting the photon's deposited energy to eV
([`qe_pass`, #L230-L249](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PhotoMultiplierHitDigi.cc#L230-L249));
and a geometric pixel-gap mask that kills photons landing in the dead space
between pixels of a sensor tile. Survivors are grouped by cellID *and* by
arrival time: a photon joins an existing hit on the same pixel if it falls
within `hitTimeWindow`, adding one to that hit's photoelectron count and
adding a Gaussian single-photon amplitude `speMean ± speError` to its charge;
otherwise it opens a new hit and picks up a pedestal `pedMean ± pedError`
([`InsertHit`, #L253-L296](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PhotoMultiplierHitDigi.cc#L253-L296)).
The time is written as an integer TDC count `time / timeResolution`. Dark
noise, when enabled, sprinkles hits over random cellIDs with probability
`noiseRate × noiseTimeWindow` and a uniformly distributed time
([`#L115-L129`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PhotoMultiplierHitDigi.cc#L115-L129));
noise hits deliberately get **no** MC association, which is how the IRT
algorithm can tell them apart in cheat mode.

| field | struct default | dRICH / pfRICH | hpDIRC | meaning |
|---|---|---|---|---|
| `detectorName` | `""` | `"DRICH"` / `"PFRICH"` | not set | detector used for the pixel-gap mask |
| `readoutClass` | `""` | `"DRICHHits"` / `"PFRICHHits"` | not set | readout whose idSpec decodes cellIDs |
| `hitTimeWindow` | `20.0 ns` | `20.0 ns` | `20.0 ns` | photons within this window on one pixel merge into one hit |
| `timeResolution` | `1/16 ns` | `1/16 ns` | `1/16 ns` | TDC least count (1 / counts per ns) |
| `speMean` | `80.0` | `80.0` | `80.0` | mean ADC counts for a single photon |
| `speError` | `16.0` | `16.0` | `16.0` | sigma of ADC counts for a single photon |
| `pedMean` | `200.0` | `200.0` | `200.0` | mean ADC counts for the pedestal |
| `pedError` | `3.0` | `3.0` | `3.0` | sigma of ADC counts for the pedestal |
| `enableNoise` | `false` | `false` | not set (`false`) | inject dark-count hits |
| `noiseRate` | `20000 Hz` | `20000 Hz` | — | dark-count rate per pixel |
| `noiseTimeWindow` | `20.0 ns` | `20.0 ns` | — | window over which noise hits are generated |
| `enablePixelGaps` | `false` | `true` | `false` | reject photons in the gaps between pixels |
| `safetyFactor` | `1.0` | `0.7` | `1.0` | flat photon-survival derating, range (0,1] |
| `enableQuantumEfficiency` | `true` | `true` | **`false`** | apply the QE curve |
| `quantumEfficiency` | 17-point table, 315–1000 nm, peak 0.40 at 450 nm | same table, re-set explicitly | **cleared** | QE vs. wavelength [nm] |

Config struct:
[`PhotoMultiplierHitDigiConfig.h#L11-L47`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PhotoMultiplierHitDigiConfig.h#L11-L47);
per-detector values:
[`DRICH.cc#L46-L65`](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L46-L65),
[`PFRICH.cc#L29-L48`](https://github.com/eic/EICrecon/blob/main/src/detectors/PFRICH/PFRICH.cc#L29-L48),
[`DIRC.cc#L26-L43`](https://github.com/eic/EICrecon/blob/main/src/detectors/DIRC/DIRC.cc#L26-L43).
The DIRC instance disables QE with the comment *"Actual efficiency is
implemented in npsim via a stacking action"* — i.e. for the hpDIRC the photon
losses are applied during simulation, not here.

Outputs, per detector: `DRICHRawHits` / `RICHEndcapNRawHits` / `DIRCRawHits`
(`edm4eic::RawTrackerHit`) plus `…RawHitsLinks` and `…RawHitsAssociations`
back to the simulated photons.

## `IrtCherenkovParticleID` — the real dRICH reconstruction

**Algorithm:** [`IrtCherenkovParticleID`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/IrtCherenkovParticleID.cc)
— adapted from Alexander Kiselev's Juggler `IRTAlgorithm`, built on the
external **IRT** (Indirect Ray Tracing) library from the
[eic/irt](https://github.com/eic/irt) package.

The physics is a per-track, per-radiator likelihood. A ring-imaging counter
measures the Cherenkov angle θ, which for a given radiator refractive index
`n` fixes β and hence, together with the tracker's momentum, the mass. Instead
of fitting a ring, IRT works backwards: for each reconstructed track and each
mass hypothesis it computes the Cherenkov angle that hypothesis *would*
produce, ray-traces the resulting photon through the optics onto the sensor
plane, and asks how well the observed photoelectrons match. Each detected
photon is thereby assigned, per hypothesis, a probability of belonging to that
hypothesis's ring; summing over photons gives a weight per hypothesis per
radiator. The dRICH has two radiators with very different indices — aerogel
(`n ≈ 1.0260`) covering roughly the few-GeV range and the gas
(`n ≈ 1.00076`) taking over at high momentum — so the algorithm keeps their
results separate and lets `MergeParticleID` combine them afterwards.

Mechanically: the track is supplied not as a single point but as a
`TrackSegment` — a set of `TrackPoint`s propagated through the radiator volume
by `RichTrack_factory` (5 planes in the aerogel, 10 in the gas,
[`DRICH.cc#L67-L88`](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L67-L88))
— so IRT can integrate along the emission path. Every raw sensor hit is turned
into an IRT `OpticalPhoton` at the pixel position decoded from its cellID, and
**all** photons are handed to **both** radiators; the assignment of a photon to
a radiator emerges from `ChargedParticle::PIDReconstruction`
([`#L305-L314`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/IrtCherenkovParticleID.cc#L305-L314),
with a `FIXME` noting that a per-track fiducial sensor region would both speed
this up and suppress noise). Afterwards, per radiator, the algorithm collects
the photons that at least one hypothesis selected, averages their per-photon θ
estimates, and writes the result
([`#L335-L428`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/IrtCherenkovParticleID.cc#L335-L428)).

Output is `edm4eic::CherenkovParticleID`, one per track per radiator:

- `npe` — number of photoelectrons used,
- `thetaPhiPhotons` — the (θ, φ) pair of every contributing photoelectron, so
  you can rebuild the Cherenkov-angle distribution yourself,
- `refractiveIndex`, `photonEnergy` — NPE-averaged, but **only filled when
  `cheatPhotonVertex` is on**; otherwise both are 0,
- `hypotheses` — a `CherenkovParticleIDHypothesis{PDG, weight, npe}` per PDG in
  `pdgList` (NaN weights are dropped),
- `chargedParticle` — relation to the merged `TrackSegment`,
- `rawHitAssociations` — relation to the photon hit associations.

### Config

| field | struct default | dRICH value | meaning |
|---|---|---|---|
| `numRIndexBins` | `100` | `100` | bins used to re-interpolate the refractive-index-vs-energy table |
| `radiators` | `{}` (empty map) | `"Aerogel"`, `"Gas"` | per-radiator settings, keyed by the IRT radiator name; anything named `Filter` is skipped |
| `pdgList` | `{}` | `{11, 211, 321, 2212}` | mass hypotheses to test; masses come from `ParticleSvc` |
| `cheatPhotonVertex` | `false` | `false` | MC truth for photon vertex, momentum and refractive index |
| `cheatTrueRadiator` | `false` | `false` | MC truth to decide which radiator each photon came from |

Per-radiator (`RadiatorConfig`):

| field | struct default | Aerogel | Gas | meaning |
|---|---|---|---|---|
| `referenceRIndex` | *(uninitialised)* | `1.0260` | `1.00076` | reference refractive index of the radiator |
| `attenuation` | *(uninitialised)* | `48 mm` | `0` (disabled) | reference attenuation length |
| `smearingMode` | *(uninitialised)* | `"gaussian"` | `"gaussian"` | `"gaussian"` or `"uniform"` |
| `smearing` | *(uninitialised)* | `2e-3 rad` | `5e-3 rad` | angular smearing applied by IRT |

[`IrtCherenkovParticleIDConfig.h#L13-L44`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/IrtCherenkovParticleIDConfig.h#L13-L44),
[`DRICH.cc#L91-L110`](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L91-L110).
`RadiatorConfig` has no in-struct initialisers, so the DRICH plugin's explicit
assignment of all four members is what defines them; there is no safe
"default" radiator.

{: .note }
There is **no** `numberOfRings` parameter in this version of the config, and
the only cheat modes are the two listed above. Enabling either prints a loud
`CHEAT MODE ENABLED` warning at init
([`#L49-L57`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/IrtCherenkovParticleID.cc#L49-L57)).

The algorithm also asserts that the aerogel, gas and merged `TrackSegment`
collections have identical sizes and bails out with an error if not
([`#L156-L169`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/IrtCherenkovParticleID.cc#L156-L169)),
and it holds a static mutex around all IRT access because the `CherenkovRadiator`
objects are shared, stateful, and owned by `RichGeo_service`.

## hpDIRC: digitization only

The DIRC plugin registers exactly **one** factory — a
`PhotoMultiplierHitDigi_factory` producing `DIRCRawHits` from `DIRCBarHits`
([`DIRC.cc#L26-L43`](https://github.com/eic/EICrecon/blob/main/src/detectors/DIRC/DIRC.cc#L26-L43)).
There is no track propagation to the bars, no time-based imaging, no
likelihood, no `CherenkovParticleID` producer. `DIRCRawHits` has **no consumer
anywhere in EICrecon**; it is persisted and that is the end of it.

Barrel PID in the output therefore comes entirely from the `pid_lut` tables
`calibrations/hpdirc.lut.gz` and `calibrations/tof.lut`, which are
parametrisations of standalone studies — not from anything EICrecon computes
from `DIRCBarHits`. If you need hpDIRC pattern recognition, it lives outside
this repository.

## `MergeParticleID` — combining radiators

**Algorithm:** [`MergeParticleID`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/MergeParticleID.cc)
— *"Effectively 'zip' the input particle IDs"*. General enough to merge PID
across detectors; currently used only to merge the dRICH's aerogel and gas
results, as `MergeCherenkovParticleID_factory` instance
`DRICHMergedIrtCherenkovParticleID`.

It takes a *variadic* list of `CherenkovParticleIDCollection`s and groups their
entries by the **object ID of the `chargedParticle` `TrackSegment`** — so any
merging of the tracks themselves must already have happened upstream (that is
what `MergeTrack_factory` → `DRICHMergedTracks` is for). A track seen only by
the gas radiator, outside the aerogel acceptance, simply contributes one entry
instead of two; the worked example is in the source comment
([`#L33-L62`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/MergeParticleID.cc#L33-L62)).

For each track it emits one merged `CherenkovParticleID`:

- `npe` is **summed** over inputs;
- `refractiveIndex` and `photonEnergy` are **NPE-weighted averages**;
- `thetaPhiPhotons` are concatenated;
- hypotheses are matched by PDG; their `npe` are summed and their `weight`s
  combined according to `mergeMode`
  ([`#L142-L181`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/MergeParticleID.cc#L142-L181)).

| field | struct default | dRICH value | meaning |
|---|---|---|---|
| `mergeMode` | `kAddWeights` (`0`) | `kAddWeights` | `kAddWeights` = 0 sums the weights; `kMultiplyWeights` = 1 multiplies them; anything else throws |

[`MergeParticleIDConfig.h#L18-L19`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/MergeParticleIDConfig.h#L18-L19),
[`DRICH.cc#L112-L114`](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L112-L114).
Adding is the right combination for log-likelihoods and multiplying for
probabilities; the IRT weights are treated as the former.

## `MatchToRICHPID` — attaching PID to particles

**Algorithm:** [`MatchToRICHPID`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/MatchToRICHPID.cc)
— *"Matches tracks to Cherenkov PIDs"*.

Neutral particles are skipped outright. For each charged
`ReconstructedParticle` it computes (η, φ) from the particle momentum, and for
each `CherenkovParticleID` it computes (η, φ) from the **average momentum over
the `TrackPoint`s** of the associated `TrackSegment`. Candidates passing both
`|Δη| < etaTolerance` and `|Δφ| < phiTolerance` are collected, and the one with
the smallest `hypot(Δη, Δφ)` wins
([`#L84-L141`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/MatchToRICHPID.cc#L84-L141)).
The matched object's hypotheses are then converted to `edm4hep::ParticleID`
by [`ConvertParticleID::ConvertToParticleIDs`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/ConvertParticleID.h#L30-L74)
with `sort_by_likelihood = true`, appended to the output `ParticleID`
collection, related to the particle through `particleIDs`, and finally
`particleIDUsed` is set to `getParticleIDs().at(0)` — *"highest likelihood is
the first"* — with `goodnessOfPID = 1`
([`#L144-L160`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/MatchToRICHPID.cc#L144-L160)).

| field | struct default | meaning |
|---|---|---|
| `etaTolerance` | `0.2` | max \|Δη\| between particle and Cherenkov track |
| `phiTolerance` | `0.1` | max \|Δφ\| (radians) between particle and Cherenkov track |

[`MatchToRICHPIDConfig.h#L8-L11`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/MatchToRICHPIDConfig.h#L8-L11).
The `pid` plugin registers it once, consuming
`DRICHMergedIrtCherenkovParticleID` only — pfRICH is not wired in
([`pid.cc#L22-L35`](https://github.com/eic/EICrecon/blob/main/src/global/pid/pid.cc#L22-L35)).

{: .warning }
`MatchToRICHPID` does **not** update `ReconstructedParticle::PDG`, `mass` or
`energy`. It only attaches the hypotheses and sets `particleIDUsed`. So in
`ReconstructedChargedRealPIDParticles` the particle's own `getPDG()` is still
whatever tracking left there (`0`), and the PID is *only* in the relation.

## `pid_lut` / `PIDLookup` — the table-based path

**Algorithm:** [`PIDLookup`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid_lut/PIDLookup.cc).

Where a full reconstruction is not available, ePIC uses pre-computed
performance tables. The table is a 5-dimensional histogram over
**(true PDG, charge, momentum, polar angle, azimuthal angle)**; each cell holds
four numbers — the probability that a particle of that species, at that
kinematics, is identified as an electron, pion, kaon or proton. `PIDLookup`
finds the MC particle behind the reconstructed one (the association with the
largest weight), looks its **true** PDG and charge up in the table together
with the **reconstructed** momentum and angles
([`#L89-L102`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid_lut/PIDLookup.cc#L89-L102)),
attaches the four probabilities as four `ParticleID` objects, and then draws a
uniform random number to pick which identification this particular particle
gets — a Monte-Carlo realisation of the confusion matrix
([`#L138-L152`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid_lut/PIDLookup.cc#L138-L152)).
The chosen hypothesis is written to `particleIDUsed`, and unlike the IRT path
the particle's own `PDG`, `mass` and `energy` are updated to match
([`#L155-L159`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid_lut/PIDLookup.cc#L155-L159)).
The random seed is derived from the event header, so results are reproducible.

This is a **fast-simulation smearing, not a reconstruction**. It consumes MC
truth. Any analysis that depends on the default `ReconstructedChargedParticles`
PDG inherits that.

### LUT file format

Whitespace-separated ASCII, one row per bin, `#` comments and blank lines
ignored, optionally gzip-compressed (detected from a `.gz` suffix)
([`PIDLookupTable.cc#L38-L131`](https://github.com/eic/EICrecon/blob/main/src/services/pid_lut/PIDLookupTable.cc#L38-L131)):

```
pdg  charge  momentum  polar  azimuthal  [prob_electron]  prob_pion  prob_kaon  prob_proton
```

`prob_electron` is omitted when `missing_electron_prob` is set (the dRICH
table). Angles are degrees unless `use_radians` is set. Coordinates are bin
*centres* when the corresponding `*_bin_centers_in_lut` flag is true, otherwise
lower edges (the loader then adds half a bin width). Rows outside the polar
range are silently dropped, and any bin filled a number of times other than
exactly once is reported as an error at load time. If only one charge value is
configured, the table is treated as charge-symmetric.

{: .warning }
**The LUT files are not in EICrecon.** `calibrations/pfrich.lut`,
`calibrations/tof.lut`, `calibrations/hpdirc.lut.gz` and
`calibrations/drich.lut.gz` are resolved at runtime by `PIDLookupTableSvc`;
the algorithm throws `"Unable to open LUT file!"` if they are missing. Their
provenance — which detector study, which geometry version — is not
determinable from EICrecon source.

### Config

| field | struct default | meaning |
|---|---|---|
| `filename` | `""` | path to the LUT, `.gz` allowed |
| `system` | `""` | name of a DD4hep integer constant giving the detector system ID; written into `ParticleID::type` |
| `pdg_values` | `{}` | categorical axis of *unsigned* PDG codes present in the table |
| `charge_values` | `{}` | categorical charge axis; a single value means charge-symmetric |
| `momentum_edges` | `{}` | variable-width momentum bin edges [GeV] |
| `polar_edges` | `{}` | variable-width polar-angle bin edges |
| `azimuthal_binning` | `{}` | `{lower, upper, step}` for a circular azimuthal axis |
| `azimuthal_bin_centers_in_lut` | `false` | file stores bin centres rather than lower edges |
| `momentum_bin_centers_in_lut` | `false` | as above, momentum |
| `polar_bin_centers_in_lut` | `false` | as above, polar angle |
| `use_radians` | `false` | angles in the file are radians, not degrees |
| `missing_electron_prob` | `false` | file has no `prob_electron` column |

[`PIDLookupConfig.h#L10-L23`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid_lut/PIDLookupConfig.h#L10-L23).

### Instances

All four are registered twice — once for the standard chain and once for the
truth-seeded chain — in
[`pid_lut.cc`](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc):

| instance | file | `system` | hypotheses | momentum range | polar range |
|---|---|---|---|---|---|
| `RICHEndcapNLUTPID` (pfRICH) | `calibrations/pfrich.lut` | `BackwardRICH_ID` | 11, 211, 321, 2212 | 0.4–15.2 GeV | 2.65–3.0775 rad |
| `CombinedTOFLUTPID` (TOF) | `calibrations/tof.lut` | `BarrelTOF_ID` | 11, 211, 321, 2212 | 0.0–6.0 GeV | 2.50–154.60 deg |
| `DIRCLUTPID` (hpDIRC) | `calibrations/hpdirc.lut.gz` | `BarrelDIRC_ID` | 11, 211, 321, 2212 | 0.2–10.2 GeV | 25–160 deg, φ 0–30.5 deg |
| `DRICHLUTPID` (dRICH) | `calibrations/drich.lut.gz` | `ForwardRICH_ID` | 211, 321, 2212 | 0.75–61 GeV | 0.0635–0.4188 rad |

Only the hpDIRC table is charge-asymmetric (`charge_values = {-1, 1}`); the
other three use `{1}` and are symmetrised. Only the dRICH table sets
`missing_electron_prob`, i.e. has no electron column — yet `PIDLookup` still
creates an electron `ParticleID` for it, with an uninitialised probability
(see caveats).

## How to get PID for my particle

- **"Just give me the best guess."** Read
  `ReconstructedChargedParticles`, take `getParticleIDUsed()` and its
  `getPDG()`. If it is available, `ReconstructedParticle::getPDG()` already
  holds the same value. This is the LUT chain and it covers all four PID
  systems.

- **"I want the real Cherenkov likelihoods, not a table."** Use
  `ReconstructedChargedRealPIDParticles` and its
  `ReconstructedChargedRealPIDParticleIDs`. Hypotheses there are sorted by
  descending IRT weight, and `parameters[0]` of each is the photoelectron count
  supporting it. dRICH only.

- **"Per-radiator likelihoods."** Skip the particle level entirely and read
  `DRICHAerogelIrtCherenkovParticleID` and `DRICHGasIrtCherenkovParticleID`
  directly. Each object gives `npe`, the full `thetaPhiPhotons` list and one
  `{PDG, weight, npe}` per hypothesis. `DRICHMergedIrtCherenkovParticleID` is
  the aerogel+gas sum.

- **"Barrel vs. endcaps."** In the LUT chain everything lands in one particle
  collection; the detector that produced a given hypothesis is in
  `ParticleID::getType()` (`BarrelDIRC_ID`, `BarrelTOF_ID`, `ForwardRICH_ID`,
  `BackwardRICH_ID`), and the hypotheses are also grouped in per-detector
  collections `DIRCParticleIDs`, `CombinedTOFParticleIDs`,
  `DRICHParticleIDs`, `RICHEndcapNParticleIDs`. For the barrel there is no
  alternative — see the hpDIRC section above.

- **"`particleIDUsed` is empty."** Expected whenever the track fell outside
  every table's kinematic coverage, had no MC association, or (IRT path) had no
  Cherenkov match within the η/φ tolerances. Fall back to `getParticleIDs()`
  being empty as the "no PID" test — not to `goodnessOfPID`, which the LUT path
  never sets. For electrons specifically, `ReconstructedElectrons` /
  `ReconstructedElectronsForDIS` is an independent, calorimeter-based subset
  built from a plain `0.9 ≤ E/p ≤ 1.2` cut
  ([`ElectronReconstruction.cc#L38-L47`](https://github.com/eic/EICrecon/blob/main/src/algorithms/reco/ElectronReconstruction.cc#L38-L47),
  [`ElectronReconstructionConfig.h#L9-L10`](https://github.com/eic/EICrecon/blob/main/src/algorithms/reco/ElectronReconstructionConfig.h#L9-L10)),
  which produces no `ParticleID` objects at all.

## Caveats / needs human verification

1. **The default PID is truth-seeded smearing.** `PIDLookup` indexes the table
   by the MC particle's PDG and charge. `ReconstructedChargedParticles::PDG` is
   drawn from a random number against tabulated probabilities. It is a fast
   simulation of detector performance, not a reconstruction, and it cannot be
   run on real data.
2. **Two disjoint PID universes ship in the same file.** `pid` (IRT) and
   `global_pid_lut` are both default plugins, and both are fed from
   `ReconstructedChargedWithoutPIDParticles`, but they write to different
   particle collections. The dRICH is covered by **both** — a real IRT
   likelihood in `ReconstructedChargedRealPIDParticles` and a LUT draw in
   `ReconstructedChargedParticles`. Nothing in EICrecon reconciles them, and
   downstream reco (`MatchClusters`, jets, kinematics) uses the LUT branch.
3. **`goodnessOfPID` is meaningless.** Set to 1 by `MatchToRICHPID` with a
   `FIXME`, never set by `PIDLookup`, never read anywhere.
4. **`algorithmType` is always 0** in both paths, both marked
   `FIXME: not used yet`, so a `ParticleID` object does not record which
   algorithm made it. In the LUT path `type` at least identifies the detector;
   in the IRT path it is 0 too.
5. **`ParticleID::likelihood` is not on a common scale.** LUT values are
   probabilities in [0, 1]; IRT values are raw hypothesis weights from
   `MassHypothesis::GetWeight`, summed across radiators when `mergeMode =
   kAddWeights`. Comparing likelihoods between the two paths is not meaningful.
6. **The dRICH LUT has no electron column** (`missing_electron_prob = true`),
   but `PIDLookup` unconditionally creates an electron `ParticleID` from
   `entry->prob_electron`, which is never assigned for such tables
   ([`PIDLookupTable.cc#L98-L126`](https://github.com/eic/EICrecon/blob/main/src/services/pid_lut/PIDLookupTable.cc#L98-L126),
   [`PIDLookup.cc#L106-L118`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid_lut/PIDLookup.cc#L106-L118)).
   Whether `Entry` is zero-initialised by the boost::histogram dense storage
   determines whether this is harmless or an uninitialised read — worth a
   maintainer's confirmation before trusting `DRICHParticleIDs` electron
   entries.
7. **`chargedParticle` on the persisted IRT PID objects dangles.**
   `DRICHMergedTracks` is not written out, so
   `_DRICHAerogelIrtCherenkovParticleID_chargedParticle` and its gas twin are
   on the known-dangling-reference list
   ([`verify_for_dangling_references.py#L16-L18`](https://github.com/eic/EICrecon/blob/main/src/scripts/verify_for_dangling_references.py#L16-L18)).
   You cannot follow that relation from a file.
8. **The hpDIRC has no reconstruction and `DIRCRawHits` has no consumer.**
   Stated plainly because users ask: EICrecon digitizes DIRC bar hits and stops.
9. **IRT gives every photon to every radiator**, with a `FIXME` asking for a
   per-track fiducial sensor region. There are also no signal or timing cuts on
   the raw hits (`FIXME: signal and timing cuts (ADC, TDC, ToT, ...)`,
   [`#L256`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/IrtCherenkovParticleID.cc#L256)).
   Expected performance under realistic backgrounds is therefore not what this
   code currently delivers.
10. **`refractiveIndex` and `photonEnergy` on `CherenkovParticleID` are 0**
    unless `cheatPhotonVertex` is enabled — they are only accumulated inside
    that branch. Do not interpret zeros as a physics result.
11. **pfRICH has no IRT instance.** Its plugin registers only digitization, and
    `pid.cc` wires `MatchToRICHPID` to the dRICH collection alone, despite the
    algorithm being written generically. The electron-endcap PID in the output
    is LUT-only.
12. `RadiatorConfig` has no member initialisers, so any new detector plugin
    that forgets a field gets indeterminate values rather than a sensible
    default.
13. The reference refractive indices (`1.0260`, `1.00076`), attenuation length
    (`48 mm`) and smearings (`2e-3`, `5e-3` rad) are hard-coded in `DRICH.cc`
    with no provenance comment.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
(fetched 2026-08-19). AI-authored draft — verify against source.*
