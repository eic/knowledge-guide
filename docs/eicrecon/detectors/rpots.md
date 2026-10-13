---
title: Roman Pots (RPOTS)
parent: EICrecon
nav_order: 22
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Forward Roman Pots (RPOTS) Reconstruction

*Also known as: Roman pots, RP, RPOTS, forward Roman pots, far-forward proton taggers, ForwardRomanPot (geometry), ForwardRomanPotHits (readout), ForwardRomanPot… (collection prefix), RPOTS (flag prefix), system IDs 155–156 (`ForwardRomanPot_Station_1..2_ID`).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The Roman pots measure protons that stay inside the beam pipe. There is no
magnetic-field track fit here: reconstruction is a **transfer-matrix inversion**
that maps two hit positions in the two stations back to a momentum at the
interaction point, with a separate matrix per nominal beam energy. Everything
is registered in
[`src/detectors/RPOTS/RPOTS.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/RPOTS/RPOTS.cc)
(175 lines, mostly matrix coefficients). The runtime flag prefix is `RPOTS:`
(36 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)).

## Chain overview

`ForwardRomanPotHits` (edm4hep::SimTrackerHit) + `EventHeader`
→ **SiliconTrackerDigi** → `ForwardRomanPotRawHits` (+ Links, Associations)
→ **TrackerHitReconstruction** → `ForwardRomanPotRecHits`

*then two parallel, independent reconstructions of the same rec hits:*

(`MCParticles`, `ForwardRomanPotRecHits`)
→ **MatrixTransferStatic** → `ForwardRomanPotStaticRecParticles`
→ **PolynomialMatrixReconstruction** → **`ForwardRomanPotRecParticles`**

Both take `MCParticles` as an input — they read the beam proton from the truth
record to pick the right matrix (see caveats).

## Stage 1 — Digitization and hit reconstruction

| stage | algorithm | parameter | struct default | RPOTS value |
|---|---|---|---|---|
| digitization | [`SiliconTrackerDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconTrackerDigi.cc) | `threshold` | `0 keV` | `10.0 keV` |
| | | `timeResolution` | `8` | `8` |
| hit reco | [`TrackerHitReconstruction`](https://github.com/eic/EICrecon/blob/main/src/algorithms/tracking/TrackerHitReconstruction.cc) | `timeResolution` | `10` | `8` |

([`RPOTS.cc#L29-L43`](https://github.com/eic/EICrecon/blob/main/src/detectors/RPOTS/RPOTS.cc#L29-L43))
Identical to
[B0TRK]({% link docs/eicrecon/detectors/b0trk.md %}) and
[FOFFMTRK]({% link docs/eicrecon/detectors/foffmtrk.md %}).
Both algorithms are described on the
[Tracking page]({% link docs/eicrecon/tracking.md %}).

## Stage 2 — MatrixTransferStatic

**Algorithm:** [`MatrixTransferStatic`](https://github.com/eic/EICrecon/blob/main/src/algorithms/fardetectors/MatrixTransferStatic.cc)
— picks the two hits that fall inside the two station z-windows, converts them
to local coordinates, subtracts the offsets, and applies the inverse of a
2×2 transfer matrix per transverse plane to recover the momentum.

Shared configuration
([`MatrixTransferStaticConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/fardetectors/MatrixTransferStaticConfig.h)):

| parameter | struct default | RPOTS value | meaning |
|---|---|---|---|
| `partMass` | `0.938272` | default | assumed particle mass (proton) |
| `partCharge` | `1` | default | assumed charge |
| `partPDG` | `2212` | default | assumed PDG code |
| `crossingAngle` | `0.025` | default | beam crossing angle (rad) |
| `hit1minZ` / `hit1maxZ` | `0` / `0` | `32541.0` / `32554.0` | z-window of station 1 (mm) |
| `hit2minZ` / `hit2maxZ` | `0` / `0` | `34239.0` / `34252.0` | z-window of station 2 (mm) |
| `readout` | `""` | `"ForwardRomanPotRecHits"` | collection whose cellIDs are decoded |
| `requireBeamProton` | `true` | default `true` (**the CI dump shows `false` — see note**) | require a beam proton in `MCParticles` |
| `requireMatchingMatrix` | `true` | default `true` | require the beam energy to match one of the configured matrices |

Four `MatrixConfig` entries are supplied, one per nominal beam momentum
([`RPOTS.cc#L55-L133`](https://github.com/eic/EICrecon/blob/main/src/detectors/RPOTS/RPOTS.cc#L45-L141)).
`MatrixConfig` has **no in-struct initialisers**, so every field must be given:

{% raw %}
| `nomMomentum` | `aX` | `aY` | `local_x_offset` | `local_y_offset` | `local_x_slope_offset` | `local_y_slope_offset` |
|---|---|---|---|---|---|---|
| `275.0` | `{{3.251116, 30.285734}, {0.186036375, 0.196439472}}` | `{{0.47305, 3.062999454}, {0.0204108951, -0.139318692}}` | `-1209.29` | `0.00132511` | `-45.4772` | `0.000745498` |
| `130.0` *(“NOT TUNED — just for testing purposes”)* | `{{3.16912, 22.4693}, {0.182402, -0.218209}}` | `{{0.520743, 3.17339}, {0.0222482, -0.0923779}}` | `-1209.29` | `0.00132511` | `-45.4772` | `0.000745498` |
| `100.0` | `{{3.152158, 20.852072}, {0.181649517, -0.303998487}}` | `{{0.53061, 3.19623343}, {0.022628332, -0.082666019}}` | `-1209.27` | `0.00355218` | `-45.4737` | `0.00204394` |
| `41.0` | `{{3.135997, 18.482273}, {0.176479921, -0.497839483}}` | `{{0.49144, 4.53857451}, {0.0179664765, 0.004160679}}` | `-1209.22` | `0.00868737` | `-45.4641` | `0.00498786` |
{% endraw %}

The commented-out values next to each offset (*"these are the local coordinate
values"*) are an older parametrisation left in place.

## Stage 3 — PolynomialMatrixReconstruction

**Algorithm:** [`PolynomialMatrixReconstruction`](https://github.com/eic/EICrecon/blob/main/src/algorithms/fardetectors/PolynomialMatrixReconstruction.cc)
— the newer variant, producing the collection that carries the plain name
`ForwardRomanPotRecParticles`. Its config
([`PolynomialMatrixReconstructionConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/fardetectors/PolynomialMatrixReconstructionConfig.h))
mirrors `MatrixTransferStaticConfig` except that `PolynomialMatrixConfig`
holds **only** `nomMomentum` — the polynomial coefficients are not in the
config; the algorithm builds them internally (it includes `TGraph2D`).

| parameter | struct default | RPOTS value |
|---|---|---|
| `poly_matrix_configs` | `{}` | four entries: `nomMomentum` = `275.0`, `130.0`, `100.0`, `41.0` |
| `hit1minZ` / `hit1maxZ` | `0` / `0` | `32541.0` / `32554.0` |
| `hit2minZ` / `hit2maxZ` | `0` / `0` | `34239.0` / `34252.0` |
| `readout` | `""` | `"ForwardRomanPotRecHits"` |
| `partMass` / `partCharge` / `partPDG` / `crossingAngle` | `0.938272` / `1` / `2212` / `0.025` | defaults |
| `requireBeamProton` | `true` | default |
| `requireValidBeamEnergy` | `true` | default |

([`RPOTS.cc#L143-L173`](https://github.com/eic/EICrecon/blob/main/src/detectors/RPOTS/RPOTS.cc#L143-L173))

{: .note }
**The CI flag dump is not showing struct defaults for these two flags.** It
reports `requireBeamProton = false` for both factories because the CI job runs
with `-PRPOTS:ForwardRomanPotStaticRecParticles:requireBeamProton=false
-PRPOTS:ForwardRomanPotRecParticles:requireBeamProton=false` in its
`JANA_OPTIONS_GUN`
([`linux-eic-shell.yml#L54`](https://github.com/eic/EICrecon/blob/main/.github/workflows/linux-eic-shell.yml#L54))
— a particle-gun sample has no beam proton. In a normal run with a full event
generator the value is `true`.

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc#L213-L228`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L213-L228)):
`ForwardRomanPotHits`, `ForwardRomanPotRawHits`, `ForwardRomanPotRecHits`,
`ForwardRomanPotRawHitLinks`, `ForwardRomanPotRawHitAssociations`,
`ForwardRomanPotStaticRecParticles`, `ForwardRomanPotRecParticles`.

Downstream: the Roman-pot particles are far-forward reconstruction end
products. They do not enter central tracking, particle flow or the combined
`ReconstructedParticles`.

## Caveats / needs human verification

1. **Two reconstructions run on the same hits and both are persisted.** There
   is nothing in the source saying which one users should read;
   `ForwardRomanPotRecParticles` (polynomial) has the un-suffixed name, which
   suggests it is the intended default.
2. **The 130 GeV matrix is explicitly labelled `// NOT TUNED -- just for
   testing purposes`** and is nonetheless shipped in the default
   configuration.
3. Both algorithms consume `MCParticles`. Reconstruction that reads the truth
   record to select a transfer matrix cannot be run on real data unchanged;
   `requireBeamProton`/`requireValidBeamEnergy` gate this, and the CI turns
   the gate off.
4. The z-windows (`32541–32554`, `34239–34252` mm) are hard-coded and will
   silently produce nothing if the far-forward geometry moves.
5. `threshold = 10 keV` is shared with B0 and the off-momentum tracker with no
   detector-specific justification.
6. `PolynomialMatrixConfig` carries only `nomMomentum`, so the actual
   polynomial coefficients are invisible from the configuration — they must be
   read out of the algorithm source.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
