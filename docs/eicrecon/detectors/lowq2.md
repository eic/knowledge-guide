---
title: Low-Q² Taggers (LOWQ2)
parent: EICrecon
nav_order: 24
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Low-Q² Taggers (LOWQ2) Reconstruction

*Also known as: low-Q2 taggers, LOWQ2, Q² taggers, tagger tracker, tagger 1 and tagger 2, far-backward electron taggers, luminosity/tagger spectrometer trackers, TaggerTracker (geometry), TaggerTrackerHits (readout), TaggerTracker… (collection prefix), LOWQ2 (flag prefix), system ID 198 (`TaggerTracker_ID`; the tagger calorimeter is 199, `TaggerCalorimeter_ID`).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The low-Q² taggers sit far downstream on the electron side and catch electrons
scattered at very small angles. Their plugin is the most elaborate of the
far-detector plugins: charge sharing, a full waveform branch **with noise**,
geometry-based collection splitting, per-module linear tracking, and finally
an **ONNX neural network** that inverts the beamline transport back to the
interaction point. 221 lines, registered in
[`src/detectors/LOWQ2/LOWQ2.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc).
The runtime flag prefix is `LOWQ2:` (87 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

The detector is **two modules × four layers**, and that 2 × 4 structure is
hard-coded in the plugin as `moduleIDs = {1, 2}`, `layerIDs = {0, 1, 2, 3}`
([`LOWQ2.cc#L111-L113`](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L109-L136)).

## Chain overview

**Waveform branch (produced, but not consumed by the tracking below):**

`TaggerTrackerHits` (edm4hep::SimTrackerHit)
→ **SiliconChargeSharing** → `TaggerTrackerSharedHits`
→ **PulseGeneration** → `TaggerTrackerHitPulses`
→ **PulseCombiner** → `TaggerTrackerCombinedPulses`
→ **PulseNoise** (+ `EventHeader`) → `TaggerTrackerCombinedPulsesWithNoise` *(terminal)*

**Tracking branch:**

`TaggerTrackerHits` + `EventHeader`
→ **SiliconTrackerDigi** → `TaggerTrackerRawHits` (+ `TaggerTrackerRawHitLinks`, `TaggerTrackerRawHitAssociations`)
→ **TrackerHitReconstruction** → `TaggerTrackerRecHits`
→ **SubDivideCollection** → `TaggerTrackerM{1,2}L{0..3}RecHits` (8 collections)
→ **FarDetectorTrackerCluster** → `TaggerTrackerM{1,2}L{0..3}ClusterPositions` (8 collections)
→ **FarDetectorLinearTracking** (once per module) → `TaggerTrackerM{1,2}LocalTracks` (+ Links, Associations)
→ **CollectionCollector** ×3 → `TaggerTrackerLocalTracks`, `TaggerTrackerLocalTrackLinks`, `TaggerTrackerLocalTrackAssociations`

**Transport inversion (ML):**

(`TaggerTrackerLocalTracks`, `TaggerTrackerLocalTrackAssociations`, `MCBeamElectrons`)
→ **FarDetectorTransportationPreML** → `TaggerTrackerFeatureTensor` + `TaggerTrackerTargetTensor`
→ **ONNXInference** → `TaggerTrackerPredictionTensor`
→ **FarDetectorTransportationPostML** → **`TaggerTrackerReconstructedParticles`** (+ Links, Associations)

Note that the tracking branch digitizes `TaggerTrackerHits` **directly**, not
the charge-shared or pulse-processed hits
([`LOWQ2.cc#L92-L99`](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L92-L99)).

## Stage 1 — Charge sharing and the waveform branch

**Algorithm:** [`SiliconChargeSharing`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconChargeSharing.cc)

| parameter | struct default | LOWQ2 value | meaning |
|---|---|---|---|
| `sigma_mode` | `abs` | default `abs` | *"abs means absolute, charge sharing range = sigma_sharingx directly"* |
| `sigma_sharingx` / `sigma_sharingy` | *(uninitialised)* | `15 µm` / `15 µm` | absolute sharing width |
| `min_edep` | *(uninitialised)* | `0.1 keV` | minimum shared deposit |
| `readout` | *(uninitialised)* | `"TaggerTrackerHits"` | segmentation source |

Unlike the [TOF plugins]({% link docs/eicrecon/detectors/btof.md %}),
which use `rel` (fractions of a cell), LOWQ2 uses absolute micrometres
([`LOWQ2.cc#L51-L59`](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L51-L59)).

The pulse stages are shared machinery — see the
[Pulse chain page]({% link docs/eicrecon/algorithms/pulse-chain.md %}):

| factory | algorithm | parameters |
|---|---|---|
| `TaggerTrackerPulseGeneration` | `PulseGeneration` | `pulse_shape_function = "LandauPulse"`, `pulse_shape_params = {1.0, 2 ns}`, `ignore_thres = 15.0e-8`, `timestep = 0.2 ns` |
| `TaggerTrackerPulseCombiner` | `PulseCombiner` | `minimum_separation = 25 ns` |
| `TaggerTrackerPulseNoise` | `PulseNoise` | `poles = 5`, `variance = 1.0`, `alpha = 0.5`, `scale = 0.000002` |

([`LOWQ2.cc#L61-L89`](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L61-L89))

## Stage 2 — Digitization and hit reconstruction

| stage | algorithm | parameter | struct default | LOWQ2 value |
|---|---|---|---|---|
| digitization | [`SiliconTrackerDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconTrackerDigi.cc) | `threshold` | `0 keV` | `1.5 keV` |
| | | `timeResolution` | `8` | `2` (ns) |
| hit reco | [`TrackerHitReconstruction`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerHitReconstruction.cc) | `timeResolution` | `10` | `2` |

([`LOWQ2.cc#L92-L107`](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L92-L107))
This is the one far-detector plugin whose digi and rec time resolutions agree
*and* are not the struct defaults.

## Stage 3 — Geometry splitting and clustering

**SubDivideCollection** with a `GeometrySplit` functor on the cellID fields
`{"module", "layer"}` fans `TaggerTrackerRecHits` out into the eight
per-module-per-layer collections
([`LOWQ2.cc#L138-L143`](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L138-L143)).
The source flags this as out of order:

> This should really be done before digitization as summing hits in the same
> cell couldn't even be mixed between layers. At the moment just prep for
> clustering.

**Algorithm:** [`FarDetectorTrackerCluster`](https://github.com/eic/EICrecon/blob/main/src/algorithms/fardetectors/FarDetectorTrackerCluster.cc)
— one instance handling all eight inputs → eight outputs.

| parameter | struct default | LOWQ2 value | meaning |
|---|---|---|---|
| `readout` | `""` | `"TaggerTrackerHits"` | *"Readout identifiers for dividing detector"* |
| `x_field` / `y_field` | `"x"` / `"y"` | `"x"` / `"y"` | cellID fields giving the transverse indices |
| `hit_time_limit` | `10 ns` | `10 ns` | *"Timing limit to add a hit to a cluster"* |

## Stage 4 — Per-module linear tracking

**Algorithm:** [`FarDetectorLinearTracking`](https://github.com/eic/EICrecon/blob/main/src/algorithms/fardetectors/FarDetectorLinearTracking.cc)
— a straight-line fit through one cluster per layer (there is no field inside
the tagger), registered once per module
([`LOWQ2.cc#L156-L179`](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L156-L179)).

| parameter | struct default | LOWQ2 value | meaning |
|---|---|---|---|
| `layer_hits_max` | `10` | **`200`** | max clusters considered per layer |
| `chi2_max` | `0.001` | `0.001` | maximum fit χ² |
| `n_layer` | `4` | `4` | layers required |
| `layer_weights` | `{1,1,1,1}` | `{1,1,1,1}` | per-layer weight in the fit |
| `restrict_direction` | `true` | `true` | reject tracks far from the expected direction |
| `optimum_theta` | `0.026` | **`-π + 0.026`** | expected polar direction — pointing *backwards*, i.e. toward −z |
| `optimum_phi` | `0` | `0` | expected azimuth |
| `step_angle_tolerance` | `0.05` | `0.05` | angular tolerance around the optimum |

Three `CollectionCollector` instances then merge the two modules' tracks,
links and associations into `TaggerTrackerLocalTracks` and friends
([`LOWQ2.cc#L182-L194`](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L182-L194)).

{: .note }
`optimum_theta = -M_PI + 0.026` is the clearest single line in EICrecon
showing the far-backward convention: the struct default `0.026` points forward
(+z, hadron side), and the taggers flip it to −z. Compare the
[EndcapP/EndcapN convention]({% link docs/eicrecon/naming.md %}).
Neither `optimum_theta` nor `optimum_phi` nor `restrict_direction` is exposed
as a runtime flag — only `chi2Max`, `layerHitsMax`, `layerWeights` and
`numLayers` appear in the CI dump.

## Stage 5 — ML transport inversion

The local track direction inside the tagger has to be transported back through
the beamline magnets to an electron momentum at the IP. EICrecon does this
with a trained network rather than an analytic transfer matrix.

| factory | algorithm | parameters |
|---|---|---|
| `TaggerTrackerTransportationPreML` | [`FarDetectorTransportationPreML`](https://github.com/eic/EICrecon/blob/main/src/algorithms/fardetectors/FarDetectorTransportationPreML.cc) | `beamE = 10.0` (GeV); `requireBeamElectron` default `true` |
| `TaggerTrackerTransportationInference` | [`ONNXInference`](https://github.com/eic/EICrecon/blob/main/src/algorithms/onnx/ONNXInference.cc) | `modelPath = "calibrations/onnx/Low-Q2_Steering_Reconstruction.onnx"` |
| `TaggerTrackerTransportationPostML` | [`FarDetectorTransportationPostML`](https://github.com/eic/EICrecon/blob/main/src/algorithms/fardetectors/FarDetectorTransportationPostML.cc) | `beamE = 10.0`; `requireBeamElectron` default `true`; `pdg_value` default `11` |

([`LOWQ2.cc#L196-L219`](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L196-L219))

The pre-ML stage also takes `MCBeamElectrons` — the truth beam electron — as
an input, both to build the target tensor and to normalise the features.

{: .note }
The CI flag dump shows `requireBeamElectron = false` for both ML factories
because the CI job passes
`-PLOWQ2:TaggerTrackerTransportationPreML:requireBeamElectron=false
-PLOWQ2:TaggerTrackerTransportationPostML:requireBeamElectron=false`
([`linux-eic-shell.yml#L54`](https://github.com/eic/EICrecon/blob/main/.github/workflows/linux-eic-shell.yml#L54)).
The struct default is `true`.

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc#L173-L201`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L173-L201)):
essentially everything — `TaggerTrackerHits`, `TaggerTrackerSharedHits`,
`TaggerTrackerHitPulses`, `TaggerTrackerCombinedPulses`,
`TaggerTrackerCombinedPulsesWithNoise`, `TaggerTrackerRawHits` (+ Links,
Associations), all eight `…ClusterPositions`, both
`TaggerTrackerM{1,2}LocalTracks` (+ Links, Associations), the merged
`TaggerTrackerLocalTracks` (+ Links, Associations), and
`TaggerTrackerReconstructedParticles` (+ Links, Associations).

**Transient** unless requested: the eight `TaggerTrackerM{1,2}L{0..3}RecHits`
split collections, `TaggerTrackerRecHits`, and the three ML tensors.

Downstream: `TaggerTrackerReconstructedParticles` is merged into the global
reconstructed-particle flow — see
[Particle identification]({% link docs/eicrecon/pid.md %}).

## Caveats / needs human verification

1. **The waveform branch is a dead end.** `TaggerTrackerCombinedPulsesWithNoise`
   is produced and persisted, but the tracking branch digitizes the raw sim
   hits directly and never sees a pulse. Charge sharing likewise only feeds
   the pulse chain.
2. The plugin itself flags the ordering problem: geometry splitting *"should
   really be done before digitization"*, because summing hits in one cell can
   mix layers.
3. `beamE = 10.0` GeV is hard-coded in **both** ML stages. The ONNX model
   `Low-Q2_Steering_Reconstruction.onnx` is presumably trained for that beam
   energy; nothing in EICrecon states its validity range, and the file is not
   in the repository (it is fetched at runtime — see
   [Repository structure → downloaded blobs]({% link docs/epic/structure.md %})).
4. The 2 modules × 4 layers structure is hard-coded in the plugin, so a
   geometry with a different tagger layout silently produces empty or partial
   collections.
5. `chi2_max = 0.001` is a very tight cut for a four-point straight-line fit;
   there is no comment explaining its normalisation.
6. `optimum_theta`, `optimum_phi`, `restrict_direction` and
   `step_angle_tolerance` are not exposed as runtime flags, so the direction
   restriction cannot be relaxed without a recompile.
7. The far-backward ID block in
   [`definitions.xml`](https://github.com/eic/epic/blob/main/compact/definitions.xml)
   has a stale prose description (*"Low-Q2 Tagger 1 ID: 195, Tagger 2 ID:
   196"*) that contradicts the actual constants (`TaggerTracker_ID` 198,
   `TaggerCalorimeter_ID` 199). Trust the constants — see
   [Detector naming & aliases]({% link docs/eicrecon/naming.md %}).

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
