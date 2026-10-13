---
title: dRICH — Forward RICH (DRICH)
parent: EICrecon
nav_order: 18
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Dual-Radiator RICH (DRICH) Reconstruction

*Also known as: dRICH, dual-radiator RICH, forward RICH, hadron-side RICH, aerogel + C₂F₆ gas RICH, DRICH (geometry detector name), DRICHHits (readout), DRICH… (collection prefix), DRICH (flag prefix), system ID 120 (`ForwardRICH_ID`).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The dRICH is the **only ePIC Cherenkov detector with a real reconstruction
chain in EICrecon**: photosensor digitization, track propagation to each
radiator, and an indirect-ray-tracing likelihood per mass hypothesis.
Everything is registered in
[`src/detectors/DRICH/DRICH.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc)
(151 lines). The runtime flag prefix is `DRICH:` (44 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

The algorithms themselves — `PhotoMultiplierHitDigi`,
`IrtCherenkovParticleID`, `MergeParticleID`, and how the results reach
`ReconstructedParticle` — are documented in full on the
[Particle identification page]({% link docs/eicrecon/pid.md %}).
This page covers the plugin's own wiring and constants.

## Chain overview

**Photon side:**

`DRICHHits` (edm4hep::SimTrackerHit) + `EventHeader`
→ **PhotoMultiplierHitDigi** → `DRICHRawHits` (+ `DRICHRawHitsLinks`, `DRICHRawHitsAssociations`)

**Track side** (two independent propagations, one per radiator):

(`CentralCKFTracks`, `CentralCKFActsTrackStates`, `CentralCKFActsTracks`)
→ **RichTrack** → `DRICHAerogelTracks`
→ **RichTrack** → `DRICHGasTracks`
→ **MergeTrack** → `DRICHMergedTracks`

**PID:**

(`DRICHAerogelTracks`, `DRICHGasTracks`, `DRICHMergedTracks`, `DRICHRawHits`, `DRICHRawHitsAssociations`)
→ **IrtCherenkovParticleID** → `DRICHAerogelIrtCherenkovParticleID` + `DRICHGasIrtCherenkovParticleID`
→ **MergeCherenkovParticleID** → **`DRICHMergedIrtCherenkovParticleID`**

## Stage 1 — Photosensor digitization

**Algorithm:** [`PhotoMultiplierHitDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PhotoMultiplierHitDigi.cc)
— explained on the
[PID page]({% link docs/eicrecon/pid.md %}).

| parameter | struct default | dRICH value | meaning |
|---|---|---|---|
| `detectorName` | `""` | `"DRICH"` | DD4hep detector element |
| `readoutClass` | `""` | `"DRICHHits"` | readout used for the pixel-gap lookup |
| `hitTimeWindow` | `20.0` | `20.0` | *"time gate in which 2 input hits will be grouped to 1 output hit // [ns]"* |
| `timeResolution` | `1/16` | `1/16` | *"time resolution (= 1 / TDC counts per unit time) // [ns]"* |
| `speMean` / `speError` | `80.0` / `16.0` | `80.0` / `16.0` | *"mean/sigma ADC counts for a single photon"* |
| `pedMean` / `pedError` | `200.0` / `3.0` | `200.0` / `3.0` | *"mean/sigma ADC counts for the pedestal"* |
| `enablePixelGaps` | `false` | **`true`** | *"enable/disable removal of hits in gaps between pixels"* |
| `safetyFactor` | `1.0` | **`0.7`** | *"use this safety factor to reduce the number of initial photon hits for a more conservative estimate of the number of photoelectrons"* |
| `enableNoise` | `false` | `false` | dark-count injection, off |
| `noiseRate` | `20000` | `20000` | `[Hz]` |
| `noiseTimeWindow` | `20.0` | `20.0 * dd4hep::ns` | see caveat 2 |
| `enableQuantumEfficiency` | `true` | `true` | the 17-point QE-vs-wavelength table is re-assigned with the same values as the struct default |

([`PhotoMultiplierHitDigiConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PhotoMultiplierHitDigiConfig.h),
[`DRICH.cc#L46-L65`](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L46-L65))

## Stage 2 — Track propagation to the radiators

**Algorithm:** `RichTrack_factory` wrapping `TrackPropagation`. The target
surfaces are **not** hard-coded — they are built at plugin-init time from the
RICH geometry service
([`DRICH.cc#L67-L88`](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L67-L88)):

| radiator | tracking planes | filter surface | track-point cut |
|---|---|---|---|
| Aerogel | `actsGeo->TrackingPlanes(richgeo::kAerogel, 5)` — 5 planes | last gas plane | `actsGeo->TrackPointCut(kAerogel)` |
| Gas | `actsGeo->TrackingPlanes(richgeo::kGas, 10)` — 10 planes | last gas plane | `actsGeo->TrackPointCut(kGas)` |

The whole block is guarded by
`dd4hepGeo->world().children().contains("DRICH")`, so with a geometry that
has no dRICH the two propagation configs stay empty rather than throwing.

`MergeTrack_factory` (`DRICHMergedTracks`) then zips the two `TrackSegment`
collections so that the IRT algorithm can index them consistently
([`DRICH.cc#L132-L134`](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L132-L134)).

## Stage 3 — The IRT chain

**Algorithm:** [`IrtCherenkovParticleID`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/IrtCherenkovParticleID.cc),
built on the external [eic/irt](https://github.com/eic/irt) library.

In one paragraph: a ring-imaging counter measures the Cherenkov angle θ, which
for a radiator of refractive index `n` fixes β, and together with the
tracker's momentum fixes the mass. IRT does **not** fit a ring. For each
reconstructed track and each mass hypothesis it ray-traces *backwards* from
the photosensor hits through the optics to work out the angle that hypothesis
*would* have produced, and accumulates a likelihood weight per hypothesis.
The output is one `edm4eic::CherenkovParticleID` per (track, radiator) with a
weight for each PDG code in `pdgList`. Because aerogel and gas cover different
momentum ranges, the two are reconstructed separately and then merged by
adding weights. Full treatment on the
[PID page]({% link docs/eicrecon/pid.md %}).

| parameter | struct default | dRICH value | meaning |
|---|---|---|---|
| `numRIndexBins` | `100` | `100` | *"number of bins to interpolate the refractive index vs. energy"* |
| `pdgList` | `{}` | `{11, 211, 321, 2212}` | mass hypotheses tested |
| `cheatPhotonVertex` | `false` | `false` | *"if true, use MC photon vertex, wavelength, and refractive index"* |
| `cheatTrueRadiator` | `false` | `false` | *"if true, use MC truth to obtain true radiator, for each hit"* |

Per radiator (`RadiatorConfig` — **no in-struct initialisers**, so these
assignments are the only definition):

| parameter | Aerogel | Gas | meaning |
|---|---|---|---|
| `referenceRIndex` | `1.0260` | `1.00076` | *"reference radiator refractive index"* |
| `attenuation` | `48` mm | `0` (disabled) | *"reference radiator attenuation length [mm]; set to 0 to disable"* |
| `smearingMode` | `"gaussian"` | `"gaussian"` | *"smearing type: 'gaussian', 'uniform'"* |
| `smearing` | `2e-3` rad | `5e-3` rad | *"smearing amount [radians]"* |

([`IrtCherenkovParticleIDConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/pid/IrtCherenkovParticleIDConfig.h),
[`DRICH.cc#L91-L110`](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L91-L110))

**Merging:** `MergeCherenkovParticleID_factory` with
`mergeMode = kAddWeights` (`0` in the flag dump) — the aerogel and gas
likelihood weights for the same track are summed
([`DRICH.cc#L113-L114`](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L113-L114)).

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc#L130-L139`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L130-L139)):
`DRICHRawHits`, `DRICHRawHitsLinks`, `DRICHRawHitsAssociations`,
`DRICHAerogelTracks`, `DRICHGasTracks`,
`DRICHAerogelIrtCherenkovParticleID`, `DRICHGasIrtCherenkovParticleID`,
plus the LUT-derived `DRICHTruthSeededParticleIDs` / `DRICHParticleIDs`.

**Transient** unless requested: `DRICHMergedTracks` and
`DRICHMergedIrtCherenkovParticleID`.

Downstream, there are **two parallel PID paths** and they do not agree by
construction:

- the IRT result reaches `ReconstructedChargedRealPIDParticles` via
  `MatchToRICHPID`;
- `ReconstructedChargedParticles` — what most analyses read — takes its PDG
  from the table-based `DRICHLUTPID` instance
  (`calibrations/drich.lut.gz`, keyed on `ForwardRICH_ID`).

Both are described on the
[PID page]({% link docs/eicrecon/pid.md %}).

## Caveats / needs human verification

1. **The `aerogel:` and `gas:` runtime flags appear to be swapped.** The
   plugin sets Aerogel `referenceRIndex = 1.0260`, `attenuation = 48`,
   `smearing = 2e-3` and Gas `referenceRIndex = 1.00076`, `attenuation = 0`,
   `smearing = 5e-3`
   ([`DRICH.cc#L95-L105`](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L91-L110)),
   which is physically right (aerogel n ≈ 1.026, C₂F₆ gas n ≈ 1.0008). But the
   [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
   reports `DRICH:DRICHIrtCherenkovParticleID:aerogel:referenceRIndex = 1.00076`,
   `aerogel:attenuation = 0`, `aerogel:smearing = 0.005` and the aerogel
   values under `gas:` — **consistently exchanged across all three fields.**
   The likely mechanism is that the factory binds its `ParameterRef`s to
   `config().radiators["Aerogel"]` / `["Gas"]` *before* the plugin's config is
   assigned
   ([`IrtCherenkovParticleID_factory.h#L41-L56`](https://github.com/eic/EICrecon/blob/main/src/factories/pid/IrtCherenkovParticleID_factory.h#L41-L56)),
   and `std::map` assignment reuses nodes in an order that leaves each
   reference pointing at the other radiator's entry. If that is what is
   happening, then **`-PDRICH:DRICHIrtCherenkovParticleID:aerogel:smearing=…`
   would actually modify the gas radiator**, while an un-overridden run still
   uses the correct values. This needs a maintainer's confirmation before
   anyone tunes these flags.
2. `noiseTimeWindow` is written `20.0 * dd4hep::ns` while the field is
   documented as being in ns; the flag dump shows `2e-08`, i.e. the DD4hep
   unit conversion has been applied where the algorithm expects a bare
   number. Harmless today because `enableNoise = false`, but it would bite if
   noise were enabled. The same line appears in
   [PFRICH]({% link docs/eicrecon/detectors/pfrich.md %}).
3. `safetyFactor = 0.7` — a 30% blanket reduction of photoelectrons — has no
   provenance beyond the struct comment describing what a safety factor is.
4. The five aerogel / ten gas tracking planes are magic numbers passed to
   `actsGeo->TrackingPlanes` with no comment.
5. The quantum-efficiency table is `clear()`ed and then re-assigned with the
   identical 17 points already in the struct default — dead code that looks
   like it once differed.
6. `IrtCherenkovParticleID` holds a **static mutex** around all IRT access
   because the `CherenkovRadiator` objects are shared and stateful, so this
   stage does not parallelise across threads.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
