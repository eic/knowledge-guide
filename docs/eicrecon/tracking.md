---
title: Tracking
parent: EICrecon
nav_order: 10
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Central Tracking Reconstruction

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

This page is a **map**, not an algorithm reference: it follows one charged
particle from its Geant4 energy deposits in the silicon/MPGD trackers all the
way to a row in `ReconstructedChargedParticles`, and tells you which
collection to open at each step. The whole chain is wired in a single JANA2
plugin,
[`src/global/tracking/tracking.cc`](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc)
— when in doubt, that file is the authority on tag names.

{: .note }
EICrecon maintains its **own** design document with mermaid workflow diagrams
and the collection glossary:
[`docs/design/tracking.md`](https://github.com/eic/EICrecon/blob/main/docs/design/tracking.md).
Read it for the authoritative picture. This page complements it with the
per-stage physics and the config tables; where the two disagree, the source
wins (see caveats — the design doc's digitization diagram predates
`MPGDTrackerDigi`).

Track finding and fitting are done with [ACTS](https://acts.readthedocs.io/);
EICrecon supplies the geometry, the space points and the EDM conversion, and
ACTS supplies the seeder, the combinatorial Kalman filter, the ambiguity
solver and the vertex finders.

## Chain overview

**Per-subdetector hit digitization and hit reconstruction** (seven collections
feed central tracking):

`VertexBarrelHits` → **SiliconTrackerDigi** → `SiBarrelVertexRawHits` → **TrackerHitReconstruction** → `SiBarrelVertexRecHits`
`SiBarrelHits` → **SiliconTrackerDigi** (+ **RandomNoisePixel**) → `SiBarrelRawHitsWithNoise` → **TrackerHitReconstruction** → `SiBarrelTrackerRecHits`
`TrackerEndcapHits` → … → `SiEndcapTrackerRecHits`
`MPGDBarrelHits` → **SiliconTrackerDigi** *or* **MPGDTrackerDigi** → `MPGDBarrelRawHits` → **TrackerHitReconstruction** *or* **MPGDHitReconstruction** → `MPGDBarrelRecHits`
`OuterMPGDBarrelHits` → … → `OuterMPGDBarrelRecHits`
`BackwardMPGDEndcapHits` → … → `BackwardMPGDEndcapRecHits`
`ForwardMPGDEndcapHits` → … → `ForwardMPGDEndcapRecHits`

→ **CollectionCollector** → **`CentralTrackingRecHits`** (edm4eic::TrackerHit)

*TOF enters later, and already as a measurement:*

`TOFBarrelHits` → **SiliconChargeSharing** → `TOFBarrelSharedHits` → **SiliconTrackerDigi** → `TOFBarrelSharedRawHits` → **TrackerHitReconstruction** → `TOFBarrelSharedRecHits` → **LGADHitClustering** → `TOFBarrelClusterHits` *(edm4eic::Measurement2D)*
(identically for `TOFEndcapHits` → `TOFEndcapClusterHits`)

**Central track finding:**

`CentralTrackingRecHits`
→ **TrackerMeasurementFromHits** → `CentralWithoutTOFTrackerMeasurements`
→ **CollectionCollector** (+ `TOFBarrelClusterHits`, `TOFEndcapClusterHits`)
→ **`CentralTrackerMeasurements`**

*in parallel, from the same rec hits:*
`CentralTrackingRecHits` → **TrackSeeding** → `CentralTrackSeeds` + `CentralTrackSeedParameters`

(`CentralTrackSeeds`, `CentralTrackerMeasurements`)
→ **CKFTracking** → `CentralCKFActsTrackStatesUnfiltered` + `CentralCKFActsTracksUnfiltered` *(in-memory ACTS containers, not podio)*
→ **AmbiguitySolver** → `CentralCKFActsTrackStates` + `CentralCKFActsTracks`
→ **ActsToTracks** → **`CentralCKFTracks`**, `CentralCKFTrajectories`, `CentralCKFTrackParameters`, `CentralCKFTrackLinks`, `CentralCKFTrackAssociations`

*(the unfiltered ACTS containers are also run through **ActsToTracks** in
parallel to give the `…Unfiltered` EDM twins)*

**Downstream of the tracks:**

`CentralCKFActs*` + `CentralCKFTracks` → **TrackProjector** → **`CentralTrackSegments`**
`CentralCKFTracks` + `CentralCKFActs*` → **TrackPropagation** → **`CalorimeterTrackProjections`**
`CentralCKFActs*` + `ReconstructedChargedParticles` → **IterativeVertexFinder** → **`CentralTrackVertices`**
`ReconstructedParticles` + `CentralCKFActs*` → **SecondaryVertexFinder** → `PrimaryVerticesAMVF` / `SecondaryVerticesAMVF`
(`CentralCKFActs*`, `B0TrackerCKFActs*`) → **ActsTrackMerger** → **IterativeVertexFinder** → `CentralAndB0TrackVertices`

(`CentralCKFTracks`, `B0TrackerCKFTracks`) → **CollectionCollector** → `CombinedTracks`
(`CombinedTracks`, `CombinedTrackAssociations`) → **TracksToParticles** → `ReconstructedChargedWithoutPIDParticles`
→ *(PID cascade in [`pid_lut.cc`](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc))* → **`ReconstructedChargedParticles`**

## Stage 1 — Per-subdetector hit digitization

Each tracker plugin turns `edm4hep::SimTrackerHit` into
`edm4eic::RawTrackerHit` plus the MC link/association collections. The
algorithm is
[`SiliconTrackerDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconTrackerDigi.cc)
almost everywhere: it applies an energy-deposit threshold and quantises the
hit time. Its config
([`SiliconTrackerDigiConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconTrackerDigiConfig.h#L10-L15))
has only two fields.

| field | struct default | meaning |
|---|---|---|
| `threshold` | `0 keV` | minimum deposited energy for a hit to survive |
| `timeResolution` | `8` | time smearing/quantisation; the source itself says *"TODO 8 of what units??? Same TODO in juggler. Probably [ns]"* |

Per-detector values (from the plugin registration files):

| detector | plugin | raw-hit collection | threshold | timeResolution |
|---|---|---|---|---|
| Si vertex barrel | [`BVTX.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/BVTX/BVTX.cc#L28-L34) | `SiBarrelVertexRawHits` | `0.54 keV` | default |
| Si barrel tracker | [`BTRK.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTRK/BTRK.cc#L27-L33) | `SiBarrelRawHits` | `0.54 keV` | default |
| Si endcap tracker | [`ECTRK.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTRK/ECTRK.cc#L27-L33) | `SiEndcapTrackerRawHits` | `0.54 keV` | default |
| MPGD (all four) | [`MPGD.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L102-L109) | `…MPGD…RawHits` | `100 eV` | `10` |
| B0 tracker | [`B0TRK.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/B0TRK/B0TRK.cc#L23-L30) | `B0TrackerRawHits` | `10 keV` | `8` |
| Barrel/endcap TOF | [`BTOF.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L72-L79) / [`ECTOF.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L60-L67) | `TOF…SharedRawHits` | `0.0` | `0.025` (ns) |

Two variations matter for tracking:

- **Noise.** The three silicon subsystems add uncorrelated pixel noise with
  [`RandomNoisePixel`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTRK/BTRK.cc#L35-L45)
  (`noise_rate_per_pixel_per_event = 2.0e-7`) and merge it into a
  `…RawHitsWithNoise` collection, which is what hit reconstruction actually
  reads. The MPGDs and B0 have no noise stage.
- **MPGD 2D-strip readout.** Barrel MPGDs can instead run
  [`MPGDTrackerDigi`](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L111-L134),
  which models charge amplification (`gain = 10000`) and two crossed strip
  planes (`stripResolutions = {150 µm, 150 µm}`, `stripNumbers` taken from the
  geometry constants `MMnStripsPhi` / `MMnStripsZ`). Which path runs is chosen
  by the bit mask `MPGD:SiFactoryPattern` (default `0x3` = pixel-style
  `SiliconTrackerDigi`), overridden from the geometry XML constants
  `InnerMPGDBarrel_2DStrip` / `MPGDOuterBarrel_2DStrip`
  ([MPGD.cc#L54-L89](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L54-L89)).
  The output collection names are identical either way, so downstream code
  does not know which ran.

Full per-detector digitization details belong on the detector pages; from
here on only the **RecHit** names matter.

## Stage 2 — TrackerHitReconstruction (raw hit → 3D space point)

**Algorithm:**
[`TrackerHitReconstruction`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerHitReconstruction.cc)
— *"Produces edm4eic::TrackerHit with geometric info from
edm4eic::RawTrackerHit"*.

This is where a cell ID becomes a point in space. For each raw hit the
algorithm asks DD4hep's `CellIDPositionConverter` for the **centre** of the
cell and for the cell's dimensions, then writes a `edm4eic::TrackerHit` with
that position (mm), a diagonal covariance, the time (`timeStamp/1000`, ns) and
the collected charge converted to GeV
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerHitReconstruction.cc#L70-L81)).

The **position resolution is purely geometric**: the variance on each axis is
`(cell_size / √12)²`, the digital (binary-readout) resolution of a uniformly
illuminated pixel
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerHitReconstruction.cc#L20-L29)).
There is no charge-weighted centroid and no multi-pixel clustering — one raw
hit gives one space point at the cell centre. So the tracker's pointing
resolution in EICrecon is set by the segmentation in the `epic` geometry
description, not by anything in EICrecon.

The covariance is written in **DD4hep surface coordinates, not global
coordinates**: for an XY-segmented sensor `xx → σ_x`, `yy → σ_y`, `zz → 0`;
for XZ segmentation `yy` actually holds `σ_z`
([note in source](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerHitReconstruction.cc#L61-L69)).
This matters if you read `positionError` off a rec hit expecting global x/y/z.

| field | struct default | meaning |
|---|---|---|
| `timeResolution` | `10` (ns) | copied verbatim into `TrackerHit::timeError` |

Per-detector overrides are small: B0 and the far-forward trackers use `8`, the
MPGDs `10`, the TOF layers the default. The MPGD 2D-strip variant uses
[`MPGDHitReconstruction`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/MPGDHitReconstructionConfig.h)
instead, which additionally takes `readout` and `stripResolutions`
(`{150 µm, 150 µm}`) because the resolution there comes from the strip pitch
rather than from the cell dimensions.

The seven central RecHit collections are then merged into
**`CentralTrackingRecHits`** by a `CollectionCollector`
([tracking.cc#L71-L77](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L71-L77)),
and the corresponding MC links/associations — **including** the two TOF
layers — into `CentralTrackingRawHitLinks` / `CentralTrackingRawHitAssociations`
([tracking.cc#L80-L100](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L80-L100)).

## Stage 3 — TrackerMeasurementFromHits (space point → ACTS measurement)

**Algorithm:**
[`TrackerMeasurementFromHits`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerMeasurementFromHits.cc)
— *"convert tracker hits to measurements"*.

ACTS does not fit points in space; it fits **local 2D coordinates on a
surface**. This stage performs that translation. For every `TrackerHit` it
looks up the DD4hep volume ID, finds the matching `Acts::Surface` in the
geometry provider's surface map, and projects the global position onto the
surface with `globalToLocal` (tolerance 0.1 µm, relaxed to 1 µm for B0 —
an explicitly flagged hack). The result is an `edm4eic::Measurement2D` holding
the surface's `geometryId`, the local `(loc0, loc1)`, the time, and a
covariance built from the rec hit's position error and time error
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerMeasurementFromHits.cc#L181-L227)).
Hits whose volume ID is not in the surface map, or which fail the on-surface
projection, are dropped with a warning.

Two subtleties:

- **One hit = one measurement.** The code says so explicitly: *"To do: add
  clustering to allow forming one measurement from several hits. For now, one
  hit = one measurement."*
  ([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerMeasurementFromHits.cc#L131-L133)).
- **UV-strip rotation.** For `OuterMPGDBarrel` with a `CartesianGridUV`
  segmentation, the covariance is rotated by the grid angle so that the large
  uncertainty runs along the strip rather than along a Cartesian axis
  ([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerMeasurementFromHits.cc#L137-L149)).

This algorithm has **no config** (`WithPodConfig<NoConfig>`).

The TOF layers bypass it entirely: `LGADHitClustering` already emits
`edm4eic::Measurement2D` (`TOFBarrelClusterHits`, `TOFEndcapClusterHits`), and
a `CollectionCollector` concatenates all three into
**`CentralTrackerMeasurements`**
([tracking.cc#L102-L111](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L102-L111)).
That collection is the measurement pool the CKF searches, and its **index** is
the source-link index used everywhere inside ACTS.

## Stage 4 — TrackSeeding (orthogonal seed finder)

**Algorithm:**
[`TrackSeeding`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackSeeding.cc)
— *"create track seeds from tracker hits"*, wrapping
`Acts::SeedFinderOrthogonal`.

A seed is a **triplet** of space points (bottom, middle, top) that is
compatible with a helix originating near the beam line. The "orthogonal"
finder is the range-search variant: instead of binning hits into a fixed
φ–z–r grid, ACTS stores the space points in a k-d tree and, for each candidate
middle point, queries the axis-aligned box (an *orthogonal range*) in
(r, φ, z) that could possibly contain a compatible bottom or top point given
the pT, impact-parameter and cot θ limits. That makes the search adaptive to
the very non-uniform ePIC layout instead of requiring a hand-tuned binning.

Note that seeding runs on `CentralTrackingRecHits` — the raw 3D space points —
**not** on the measurement collection, so TOF hits never take part in seeding
([tracking.cc#L168-L170](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L168-L170)).

Surviving triplets are then turned into initial track parameters entirely in
EICrecon
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackSeeding.cc#L163-L246)):

1. A **Taubin algebraic circle fit** in the x–y plane gives the helix radius
   `R` and centre `(X0, Y0)`
   ([circleFit](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackSeeding.cc#L287-L388),
   after N. Chernov).
2. A straight-line fit in the r–z plane gives the slope → `θ`, hence `η`.
3. The charge sign comes from the direction of the cross product of the
   radius vector and the first hit, relative to `+z`.
4. `pT = R · B` with the **configured, uniform** `bFieldInZ`; `p = pT·cosh η`;
   `q/p` follows.
5. The point of closest approach of the fitted circle to the origin becomes
   the perigee local position; `z0` is the seed's fitted vertex z.

The covariance on those parameters is **not** propagated from the fit — it is
a fixed diagonal matrix from the config (`locaError`, `phiError`, …). Seeds
whose circle fit diverges, or whose circle is centred on the origin, are
silently dropped.

Selected config from
[`OrthogonalTrackSeedingConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/OrthogonalTrackSeedingConfig.h)
— the struct has ~50 fields; the ones below are the geometric/kinematic
acceptance and the seed covariance, i.e. what a user would plausibly retune.
The seed-*filter* block (`compatSeedWeight`, the central/forward seed
confirmation ranges, …) is omitted and is in any case inactive by default
because `seedConfirmation = false`.

| field | struct default | meaning |
|---|---|---|
| `rMax` / `rMin` | `440 mm` / `33 mm` | radial window searched for space points |
| `zMax` / `zMin` | `1700 mm` / `-1500 mm` | z window searched for space points |
| `rMinMiddle` / `rMaxMiddle` | `20 mm` / `400 mm` | radial window for the **middle** point of the triplet |
| `deltaRMinTopSP` / `deltaRMaxTopSP` | `10 mm` / `450 mm` | Δr allowed between middle and top point |
| `deltaRMinBottomSP` / `deltaRMaxBottomSP` | `10 mm` / `200 mm` | Δr allowed between middle and bottom point |
| `deltaPhiMax` | `0.085` (rad) | max Δφ between middle and top/bottom |
| `collisionRegionMin` / `Max` | `-250 mm` / `250 mm` | allowed z of the extrapolated origin |
| `impactMax` | `3 mm` | max transverse impact parameter of the seed helix. The factory notes *"rMin should be larger than impactMax"* |
| `cotThetaMax` | `1/tan(2·atan(e^-4))` ≈ `27.29` | acceptance limit, i.e. \|η\| ≤ 4 |
| `minPt` | `100 MeV / cotThetaMax` ≈ **`3.66 MeV`** | minimum transverse momentum — see caveats, this is *not* 100 MeV |
| `maxSeedsPerSpM` | `0` | max extra seeds sharing one middle point |
| `sigmaScattering` | `5` | how many σ of multiple scattering to allow |
| `radLengthPerSeed` | `0.1` | assumed material budget over a seed's length |
| `bFieldInZ` | `1.7 T` | uniform solenoid field assumed for the helix estimate |
| `beamPosX` / `beamPosY` | `0` / `0` | beam position offset |
| `locaError` / `locbError` | `√1.5 mm` | fixed σ on the perigee local coordinates |
| `phiError` / `thetaError` | `√0.02 rad` / `√0.002 rad` | fixed σ on the seed direction |
| `qOverPError` | `√0.025 /GeV` | fixed σ on q/p |
| `timeError` | `√(0.1 mm/ns)·ns` | fixed σ on time; the source flags that this evaluates to `0.0183` ≈ 5.5 ns in ACTS units |

`tracking.cc` passes **no overrides** for the central or B0 seeders — both run
the struct defaults
([tracking.cc#L168-L170](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L168-L170),
[#L377-L379](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L377-L379)).
Everything in the table above is exposed as a JANA flag through
[`TrackSeeding_factory.h`](https://github.com/eic/EICrecon/blob/main/src/factories/tracking/TrackSeeding_factory.h);
the seed-filter fields are **not**.

Outputs: `CentralTrackSeeds` (`edm4eic::TrackSeed`, carrying the three hits
and a quality score) and `CentralTrackSeedParameters`
(`edm4eic::TrackParameters` with `type = -1`, meaning "seed").

## Stage 5 — CKFTracking (combinatorial Kalman filter)

**Algorithm:**
[`CKFTracking`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/CKFTracking.cc)
— *"Combinatorial Kalman Filter track finding"*, wrapping
`Acts::CombinatorialKalmanFilter`.

This is track **finding and fitting at once**. Starting from a seed's
parameters at the perigee, the filter propagates the track state outward
through the ACTS tracking geometry (Eigen stepper + navigator, with a material
interactor, `maxSteps = 10000`). On each surface it reaches, it asks the
source-link accessor for all measurements on that surface, computes the
predicted-vs-measured χ² for each, and keeps every measurement whose χ² is
below `chi2CutOff` — up to `numMeasurementsCutOff` of them. Each accepted
measurement **branches** the trajectory: the filter therefore explores a tree
of candidate trajectories per seed, not a single one. Surfaces where no
compatible measurement is found are recorded as *holes*; measurements that
were considered but rejected as incompatible become *outliers*.

Both cut-offs are vectors indexed by `etaBins`, so they can be made
η-dependent; with `etaBins = {}` the single value applies everywhere.

Each surviving candidate is then filtered and finished
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/CKFTracking.cc#L262-L315)):
candidates with no valid measurement state are dropped, candidates with fewer
than `numMeasurementsMin` measurements are dropped, the track is **smoothed**
(backward Kalman pass), and finally extrapolated back to the perigee surface
at the origin. Only then is it copied into the output container, tagged with
the index of the seed it came from (an ACTS dynamic column named `"seed"`).

| field | struct default | meaning |
|---|---|---|
| `etaBins` | `{}` | η bin edges for the cuts below; empty = one global bin |
| `chi2CutOff` | `{15.}` | max χ² for a measurement to be attached to a branch |
| `numMeasurementsCutOff` | `{10}` | max compatible measurements kept per surface (i.e. max branching factor) |
| `numMeasurementsMin` | `4` | minimum measurements for a candidate track to be kept |

`tracking.cc` uses the defaults for the central chain. The one override in the
plugin is the **B0 truth-seeded** CKF, which lowers `numMeasurementsMin` to
`3` because the B0 tracker has fewer layers
([tracking.cc#L317-L326](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L317-L326)).

Outputs are **not** podio collections: they are raw
`Acts::ConstVectorMultiTrajectory` / `Acts::ConstVectorTrackContainer`
pointers passed in memory between JANA factories
(`CentralCKFActsTrackStatesUnfiltered`, `CentralCKFActsTracksUnfiltered`).
You cannot read these from a ROOT file.

## Stage 6 — AmbiguitySolver (duplicate and shared-hit removal)

**Algorithm:**
[`AmbiguitySolver`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/AmbiguitySolver.cc)
— *"Reco Track Filtering Based on Greedy ambiguity resolution solver adopted
from ACTS"*, wrapping `Acts::GreedyAmbiguityResolution`.

Because the CKF branches, one real particle typically yields several
reconstructed candidates that share most of their hits, plus fake candidates
built from the tails of other tracks. The greedy solver builds the
track ↔ measurement incidence graph (measurements are identified by their
source-link index) and iteratively removes the "worst" track that still shares
more than `maximum_shared_hits` measurements with another track, until no
conflicts remain. Tracks with fewer than `n_measurements_min` measurements are
discarded outright. The surviving track indices are copied into a fresh
container, so downstream stages see a clean, mostly one-track-per-particle set.

| field | struct default | meaning |
|---|---|---|
| `maximum_shared_hits` | `1` | how many measurements two kept tracks may share |
| `maximum_iterations` | `100000` | safety bound on the greedy loop |
| `n_measurements_min` | `4` | minimum measurements to survive |

`tracking.cc` uses defaults everywhere except the **B0 truth-seeded** solver,
which uses `n_measurements_min = 3`
([tracking.cc#L346-L357](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L346-L357)).

Outputs: `CentralCKFActsTrackStates`, `CentralCKFActsTracks` — again ACTS
containers, not podio.

## Stage 7 — ActsToTracks (ACTS → EDM4eic)

**Algorithm:**
[`ActsToTracks`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/ActsToTracks.cc)
— *"Converts ACTS tracks to EDM4eic"*.

This is the stage whose output users actually read. It takes five inputs
(`CentralTrackerMeasurements`, `CentralTrackSeeds`, the two ACTS containers,
and `CentralTrackingRawHitAssociations`) and emits **five** collections
([signature](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/ActsToTracks.h#L25-L32)):

| output | EDM type | contents |
|---|---|---|
| `…Trajectories` | `edm4eic::Trajectory` | fit-quality summary: `nMeasurements`, `nStates`, `nOutliers`, `nHoles`, `nSharedHits`, the per-state `measurementChi2` / `outlierChi2` vectors, a relation to the originating `TrackSeed`, and a relation to the `TrackParameters` |
| `…TrackParameters` | `edm4eic::TrackParameters` | the fitted perigee-bound parameters: `loc(a,b)` [mm], `phi`, `theta` [rad], `qOverP` [e/GeV], `time` [ns], and the 6×6 covariance; `type = 0` ("track head") |
| `…Tracks` | `edm4eic::Track` | the analysis object: 3-position and 3-momentum at the perigee, `charge`, `time`/`timeError`, `chi2`, `ndf`, PDG hypothesis, a relation to its `Trajectory`, and one-to-many relations to the `Measurement2D` objects that were actually used |
| `…TrackLinks` | `edm4eic::MCRecoTrackParticleLink` | track → `edm4hep::MCParticle` |
| `…TrackAssociations` | `edm4eic::MCRecoTrackParticleAssociation` | the same relation in the older Rec/Sim form |

The MC truth match is **hit-based, not parameter-based**: for every
measurement on the track the algorithm walks
`Measurement2D → TrackerHit → RawTrackerHit`, looks that raw hit up in
`CentralTrackingRawHitAssociations` to find the `SimTrackerHit` and hence the
`MCParticle`, and counts. Each contributing MCParticle then gets a link whose
`weight` is its share of the track's measurements
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/ActsToTracks.cc#L190-L272)).
So a track can be associated with several MCParticles, and you should cut on
weight rather than assume one match.

Outliers are attached to the `Trajectory` (via the deprecated `outliers`
relation), measurements to both the `Track` and the `Trajectory`. Holes are
counted but carry no measurement.

No config. `tracking.cc` instantiates it **twice** per branch — once on the
unfiltered ACTS containers (giving `CentralCKFTracksUnfiltered` etc.) and once
after ambiguity resolution (giving `CentralCKFTracks` etc.)
([tracking.cc#L180-L222](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L180-L222)).

## Stage 8 — TrackProjector and TrackPropagation

Two different things, both producing `edm4eic::TrackSegment`.

**[`TrackProjector`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackProjector.cc)**
— *"Exports track states as segments"*. It walks the Kalman track states that
already exist and converts each one into an `edm4eic::TrackPoint`: global
position, local position with error, momentum, path length, and the surface /
volume identifiers. This is a **dump of the fit**, not new propagation, so the
points sit on the tracking surfaces the track actually crossed. Note that it
reads each state's `predicted()` parameters, not the smoothed ones
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackProjector.cc#L93-L95)).
Output:
**`CentralTrackSegments`**, one segment per track, each linked back to its
`Track`
([tracking.cc#L224-L233](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L224-L233)).
No config.

**[`TrackPropagation`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackPropagation.cc)**
— *"Track propagation to surfaces"*. This one genuinely extrapolates each
track outward to a list of artificial ACTS surfaces defined in the config, and
records a `TrackPoint` on each surface it reaches. That is how the calorimeters
and the DIRC learn where a charged track should have arrived. Output:
**`CalorimeterTrackProjections`**.

| field | struct default | meaning |
|---|---|---|
| `target_surfaces` | `{}` | cylinders/discs to propagate to |
| `filter_surfaces` | `{}` | surfaces a track must reach to be considered at all |
| `track_point_cut` | always-true lambda | per-point acceptance predicate |
| `skip_track_on_track_point_cut_failure` | `false` | drop the whole track if a point fails the cut |

The single instance in `tracking.cc` (`CalorimeterTrackPropagator`) sets only
`target_surfaces`, with **13** surfaces
([tracking.cc#L247-L310](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L247-L310)):
the DIRC cylinder, and for each of EcalEndcapN, EcalBarrel, EcalEndcapP,
HcalEndcapN, HcalBarrel and LFHCAL a *pair* of surfaces — one at the front
face and one 50 mm (ECal) or 150 mm (HCal) deeper, so that cluster matching
has both an entry point and a shower-depth point. The geometry is not
hard-coded: each bound is a **string expression** evaluated against DD4hep
constants (e.g. `"EcalBarrel_rmin + 50*mm"`,
`"1.1*max(EcalBarrelBackward_zmax,EcalBarrelForward_zmax)"`), so the surfaces
follow the `epic` geometry version in use.

`CalorimeterTrackProjections` is consumed by every
`…TrackClusterMatches` factory in
[`reco.cc`](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L207-L236)
and by particle flow.

## Stage 9 — Vertexing

**[`IterativeVertexFinder`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/IterativeVertexFinder.cc)**
— *"Iterative vertex finder"*, wrapping the ACTS iterative vertex finder with
a full-billoir fitter and a z-scan seeder. It fits a vertex from the best
seed, removes the compatible tracks, and repeats until no seed is left or
`maxVertices` is reached. Tracks with fewer than `minTrackHits` measurements
are excluded up front
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/IterativeVertexFinder.cc#L120-L128)).

| field | struct default | meaning |
|---|---|---|
| `maxVertices` | `10` | stop after this many vertices |
| `reassignTracksAfterFirstFit` | `true` | allow tracks to move to a better vertex after the first pass |
| `minTrackHits` | `4` | minimum measurements for a track to enter vertexing |

Each output `edm4eic::Vertex` carries position (x, y, z, t), the 4×4
covariance, `chi2`, `ndf`, and `type = 1` (primary). It also gets an
`associatedParticles` relation, but that relation is resolved by **matching
the track's perigee local coordinates to within 1e-4 mm** against the
`TrackParameters` of every `ReconstructedChargedParticle`
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/IterativeVertexFinder.cc#L178-L193))
— which is why this factory takes `ReconstructedChargedParticles` as an input
and therefore runs *after* particle creation. Outputs:
**`CentralTrackVertices`** (central tracks only) and
`CentralAndB0TrackVertices` (central + B0, merged first by `ActsTrackMerger`).

**[`SecondaryVertexFinder`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/SecondaryVertexFinder.cc)**
— *"Finds vertices using ACTS Adaptive Multi-Vertex Finder (AMVF)"*. The AMVF
fits all vertices simultaneously with per-track weights, rather than peeling
them off one at a time. The same algorithm runs in two modes selected by
`isPrimary`: in **primary** mode all tracks go into one AMVF call; in
**secondary** mode the finder is run on every *pair* of tracks in turn and all
resulting vertices are accumulated
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/SecondaryVertexFinder.cc#L221-L262)).
`type` is set to `1` for primary, `0` for secondary.

| field | struct default | `SecondaryVerticesAMVF` value | meaning |
|---|---|---|---|
| `isPrimary` | `true` | `false` | primary (all tracks) vs secondary (pairwise) mode |
| `maxVertices` | `20` | — | max vertices returned |
| `maxIterations` | `500` | `1000` | AMVF iteration bound |
| `tracksMaxZinterval` | `3 mm` | `10 mm` | max Δz at PCA for a track to join a new vertex |
| `useSeedConstraint` | `false` | `true` | constrain the fit with the seed vertex |
| `maxVertexChi2` | `18.42` | — | χ² above which a track is dropped from the seed list |
| `tracksMaxSignificance` | `6.7` | — | compatibility significance for track–vertex assignment |
| `maxMergeVertexSignificance` | `3` | — | below this, two vertices are merged |
| `minWeight` | `1e-04` | — | minimum track weight in the multi-vertex fit |
| `maxDistToLinPoint` | `5.5 mm` | — | max distance to the linearisation point |
| `spatialBinExtent` | `25 µm` | — | z bin width of the track density grid |
| `temporalBinExtent` | `19 mm` | — | t bin width (ACTS time units — mm/c) |
| `initialVariances` | `{1e2, 1e2, 1e2, 1e8} mm` | — | seed covariance (x, y, z, t) |
| `doSmoothing` | `true` | — | smooth track parameters onto the vertex |
| `reassignTracksAfterFirstFit` | `true` | — | as above |
| `doFullSplitting` | `false` | — | ACTS full vertex-splitting mode |
| `useTime` | `false` | — | use track time in the fit |

Both AMVF instances read `ReconstructedParticles` (the combined charged +
neutral collection built in
[`reco.cc`](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L92-L106))
plus the central ACTS containers
([tracking.cc#L466-L489](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L466-L489)).
Separately, `reco.cc` derives `PrimaryVertices` from `CentralTrackVertices`
and `SecondaryVerticesHelix` from `PrimaryVertices` + `ReconstructedParticles`
([reco.cc#L311-L316](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L311-L316)).

## Stage 10 — TracksToParticles (Track → ReconstructedParticle)

**Algorithm:**
[`TracksToParticles`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TracksToParticles.cc)
— *"Converts track to particles with associations"*. No config.

Central and B0 tracks are first concatenated into `CombinedTracks` (and their
associations into `CombinedTrackAssociations`), then converted
([tracking.cc#L463-L525](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L463-L525)).
For each track the algorithm reads the `TrackParameters` off the track's
`Trajectory` and builds one `edm4eic::ReconstructedParticle` with
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TracksToParticles.cc#L29-L68)):

- momentum from `(1/|q/p|, θ, φ)`,
- `charge = sign(q/p)`,
- **`mass = 0`**, and therefore `energy = |p|`,
- `type = 0`, `goodnessOfPID = 0` — *"assume no PID until proven otherwise"*,
- `referencePoint` = the track's perigee position,
- a relation back to the `Track`,
- MC links/associations copied straight from the track associations (same
  weights).

So the output of this stage, `ReconstructedChargedWithoutPIDParticles`, has
**no mass and no PID hypothesis**. Both are filled in afterwards by the
lookup-table PID cascade in
[`pid_lut.cc`](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc)
(pfRICH → TOF → DIRC → low-Q² merge → dRICH), whose final stage produces the
user-facing **`ReconstructedChargedParticles`**,
`ReconstructedChargedParticleLinks` and
`ReconstructedChargedParticleAssociations`. If you read
`ReconstructedChargedParticles`, the mass you see came from PID, not from
tracking.

## What comes out

Persisted by default per
[`JEventProcessorPODIO.cc`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L52-L523).
The **★** rows are what a typical analyser should open.

| collection | EDM type | what it is | persisted |
|---|---|---|---|
| ★ `ReconstructedChargedParticles` | `edm4eic::ReconstructedParticle` | charged particles with PID-assigned mass; the standard analysis object | yes ([L241](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L233-L243)) |
| ★ `ReconstructedChargedParticleAssociations` / `…Links` | `MCRecoParticleAssociation` / `Link` | reco ↔ MCParticle, weighted by shared hits | yes (L242-L243) |
| ★ `CentralCKFTracks` | `edm4eic::Track` | ambiguity-resolved central tracks: perigee p, q, χ², ndf, used measurements | yes ([L264](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L255-L279)) |
| ★ `CentralCKFTrajectories` | `edm4eic::Trajectory` | fit quality per track: nMeasurements/nStates/nOutliers/nHoles/nSharedHits, χ² lists, seed link | yes (L263) |
| `CentralCKFTrackParameters` | `edm4eic::TrackParameters` | perigee-bound parameters + 6×6 covariance | yes (L267) |
| ★ `CentralCKFTrackAssociations` / `…TrackLinks` | `MCRecoTrackParticleAssociation` / `Link` | track ↔ MCParticle, hit-weighted | yes (L265-L266) |
| `CentralCKFTracksUnfiltered` (+ `…Trajectories`, `…TrackParameters`, `…Links`, `…Associations`) | as above | the same, **before** ambiguity resolution — for efficiency/duplicate studies | yes (L275-L279) |
| `CentralCKFTruthSeeded…` (5 collections) | as above | the MC-seeded reference chain — see below | yes (L258-L262) |
| `CentralCKFTruthSeeded…Unfiltered` (5) | as above | truth-seeded, before ambiguity resolution | yes (L269-L273) |
| ★ `CentralTrackVertices` | `edm4eic::Vertex` | primary vertices from the iterative finder | yes (L257) |
| `CentralAndB0TrackVertices` | `edm4eic::Vertex` | same, central + B0 tracks merged | yes ([L305](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L305)) |
| `PrimaryVerticesAMVF` / `SecondaryVerticesAMVF` | `edm4eic::Vertex` | adaptive multi-vertex finder output | yes ([L328-L329](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L326-L329)) |
| `CentralTrackSegments` | `edm4eic::TrackSegment` | Kalman track states at every tracking surface crossed | yes (L256) |
| ★ `CalorimeterTrackProjections` | `edm4eic::TrackSegment` | track points on the DIRC + calorimeter faces; input to all track–cluster matching | yes ([L334](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L334)) |
| `CentralTrackingRecHits` | `edm4eic::TrackerHit` | merged 3D space points of the seven central subdetectors | yes ([L68](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L64-L74)) |
| `CentralTrackerMeasurements` / `CentralWithoutTOFTrackerMeasurements` | `edm4eic::Measurement2D` | the CKF's measurement pool (with / without TOF) | yes (L73-L74) |
| `CentralTrackingRawHitLinks` / `…RawHitAssociations` | `MCRecoTrackerHitLink` / `Association` | raw hit ↔ SimTrackerHit, the basis of all MC track matching | yes (L69-L70) |
| `CentralTrackSeeds` / `CentralTrackSeedParameters` | `TrackSeed` / `TrackParameters` | orthogonal-seeder triplets and their helix estimates | yes (L71-L72) |
| `TrackerTruthSeeds`, `TrackerTruthSeedParameters`, `CentralTrackerTruthSeeds` | `TrackSeed` / `TrackParameters` | MC-truth seeds and their θ-split central subset | yes (L65-L67) |
| `B0TrackerCKFTracks` (+ trajectories, parameters, links, associations, and truth-seeded/unfiltered twins) | as central | the parallel B0 chain | yes ([L281-L303](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L281-L303)) |
| `ReconstructedTruthSeededChargedParticles` (+ links, associations) | `ReconstructedParticle` | particles from the truth-seeded chain | yes (L236-L238) |
| `ReconstructedParticles` | `ReconstructedParticle` | charged **+** neutral, built in `reco.cc` from charged particles and ECal clusters | yes (L233) |
| `CentralCKFActsTracks`, `CentralCKFActsTrackStates` (and the `…Unfiltered` twins) | ACTS containers | in-memory only — **not podio, cannot be read from file** | no |
| `CombinedTracks`, `CombinedTrackAssociations`, `CombinedTruthSeededTracks…` | `edm4eic::Track` etc. | central + B0 concatenation, an internal input to `TracksToParticles` | no |
| `ReconstructedChargedWithoutPIDParticles` (+ links/associations) | `ReconstructedParticle` | massless, PID-less intermediate | no |

Rules of thumb: use **`ReconstructedChargedParticles`** for physics
four-vectors, **`CentralCKFTracks`** when you need track-level quantities
(χ², ndf, hits used, perigee), **`CentralCKFTrackAssociations`** for MC truth
matching, **`CentralTrackVertices`** for the primary vertex, and
**`CalorimeterTrackProjections`** when you need where a track hit a
calorimeter. Reach for the `…Unfiltered` and `…TruthSeeded` twins only when
you are studying the tracking itself.

## Truth-seeded variant

EICrecon runs a **complete second copy of the chain** seeded from MC truth
instead of from hits. It is the reference against which realistic seeding is
benchmarked: everything after the seed — measurements, CKF, ambiguity
resolution, EDM conversion, particle creation — is byte-for-byte the same
code, so any difference between `CentralCKFTracks` and
`CentralCKFTruthSeededTracks` is attributable to seeding (and to the seed
covariance).

The seeds come from
[`TrackParamTruthInit`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackParamTruthInit.cc),
which loops over `MCParticles`, keeps generator-stable particles and Geant4
secondaries, applies fiducial cuts, computes the exact perigee parameters
analytically, and **deliberately smears the momentum** so that truth does not
leak into the result when the fit fails
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackParamTruthInit.cc#L87-L88)).
The charge is looked up from the PDG code, because *"we cannot trust the
mcparticles charge, as DD4hep sets this value to zero"*. Neutrals are skipped.

| field | struct default | meaning |
|---|---|---|
| `maxVertexX` / `maxVertexY` | `80 mm` / `80 mm` | transverse production-vertex window |
| `maxVertexZ` | `200 mm` | longitudinal production-vertex window |
| `minMomentum` | `100 MeV` | minimum true momentum |
| `maxEtaForward` | `6.0` | forward η acceptance |
| `maxEtaBackward` | `4.1` | backward η acceptance |
| `momentumSmear` | `0.1` | Gaussian relative smearing applied to \|p\| |

The seed covariance is hard-coded rather than configurable: `1.0` on both
local coordinates, `0.05` on φ, `0.01` on θ, `0.1` on q/p and `10e9` on time
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackParamTruthInit.cc#L123-L130)).

`TrackParamTruthInit` produces one global `TrackerTruthSeeds` collection,
which is then split by polar angle with a `SubDivideCollection`: θ < 50 mrad
goes to `B0TrackerTruthSeeds`, 50 mrad – 180° to `CentralTrackerTruthSeeds`
([tracking.cc#L52-L66](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L52-L66)).
From there the naming is mechanical: insert `TruthSeeded` after `CentralCKF`
(`CentralCKFTruthSeededTracks`, `CentralCKFTruthSeededTrajectories`, …), and
the particle-level endpoint is `ReconstructedTruthSeededChargedParticles`.

{: .note }
The truth-seeded chain has **no** `TrackProjector`, `TrackPropagation` or
vertex-finder instance — projections and vertices exist only for the
realistically seeded tracks.

## Caveats and things to verify

1. **`minPt` is not 100 MeV.** `OrthogonalTrackSeedingConfig::minPt` is
   written as `100 MeV / cotThetaMax`, which with the default
   `cotThetaMax ≈ 27.29` gives **≈ 3.66 MeV**. The trailing comment says only
   "minimum transverse momentum". The construction is plausibly deliberate —
   it makes the *total* momentum floor ~100 MeV at the most forward angle —
   but the source does not say so.
2. **Seeding assumes a uniform 1.7 T field.** `bFieldInZ` is a scalar used
   directly as `pT = R · B`; the real ePIC field map is only used later, by
   the CKF propagator. The `TrackSeeding_factory` help string additionally
   describes the flag as being in *kiloTesla*, which contradicts the
   `Acts::UnitConstants::T` in the struct. Worth a maintainer's confirmation.
3. **Position resolution is geometric only.** `TrackerHitReconstruction` uses
   `cell_size/√12` and the cell centre; there is no clustering or
   charge-weighted centroid anywhere in the tracker chain
   (`TrackerMeasurementFromHits` says so in a TODO). Real detector resolution
   will differ.
4. **Covariances are in surface coordinates.** Both `TrackerHit::positionError`
   and the `Measurement2D` covariance are local, not global. The
   `Measurement2D` covariance also has **no off-diagonal position term** —
   `cov(0,1)` is set to zero and then written into the `xy` slot, with a
   `fixme` in the source.
5. **`Track::positionMomentumCovariance` is empty.** `ActsToTracks` sets it to
   a default-constructed `edm4eic::Cov6f`
   ([L174-L175](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/ActsToTracks.cc#L174-L175));
   the real covariance lives on the associated `TrackParameters`.
6. **The MC-association optional input is not actually optional.**
   `ActsToTracks` dereferences `raw_hit_assocs` unconditionally, with a
   `FIXME: not able to check whether optional inputs were provided`
   ([L236-L237](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/ActsToTracks.cc#L236-L237)).
   The same pattern appears in `TracksToParticles`.
7. **Vertex ↔ particle association is done by float comparison.**
   `IterativeVertexFinder` matches perigee local coordinates to 1e-4 mm rather
   than following object relations, and does so in a quadruple-nested loop.
   Fragile, and the reason the vertex factory depends on
   `ReconstructedChargedParticles`.
8. **Secondary-vertex mode is O(N²) AMVF calls.** `SecondaryVertexFinder` in
   `isPrimary = false` mode runs a fresh finder on every track pair; it also
   indexes `allTrackParameters.size() - 1` without guarding against an empty
   or single-track container.
9. **`OuterMPGDBarrel` strip timing is inconsistent.** The 2D-strip digitizer
   sets `timeResolution = 5` while the matching reconstruction sets `10`
   ([MPGD.cc#L170-L209](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L170-L209));
   the inner barrel uses `10` on both sides. Probably unintentional.
10. **`LGADHitClusteringConfig::deltaT`** (`1 ns`) is never overridden by
    either TOF plugin even though `useAve = true` is set explicitly in both.
11. **The upstream design doc is partly stale.**
    [`docs/design/tracking.md`](https://github.com/eic/EICrecon/blob/main/docs/design/tracking.md)
    shows all MPGDs going through `SiliconTrackerDigi` (the `MPGDTrackerDigi`
    /`MPGDHitReconstruction` path is not drawn), routes TOF rec hits into the
    `CentralTrackingRecHits` collector (in the source TOF enters as
    `Measurement2D` instead), labels a seed collection
    `CentralTrackSeedingResults` (the real tag is `CentralTrackSeeds`), and
    has a copy-paste error where `BTOFHitReconstruction` outputs
    `TOFBarrelRawHits`. Trust `tracking.cc`.
12. **Units in several config structs are unlabelled.** `timeResolution` in
    `SiliconTrackerDigiConfig` carries a literal *"TODO 8 of what units???"*;
    `temporalBinExtent = 19_mm` in `SecondaryVertexFinderConfig` is a time in
    ACTS's mm/c convention. Values above are copied literally from the
    structs; where the unit is ambiguous it is flagged in the table.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
(fetched 2026-08-19). AI-authored draft — verify against source.*
