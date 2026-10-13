---
title: hpDIRC (DIRC)
parent: EICrecon
nav_order: 20
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC High-Performance DIRC (DIRC) Reconstruction

*Also known as: hpDIRC, DIRC, barrel DIRC, high-performance DIRC, barrel Cherenkov detector, detection of internally reflected Cherenkov light, quartz bar detector, DIRC (geometry detector name), DIRCBarHits (readout), DIRC… (collection prefix), DIRC (flag prefix), system ID 90 (`BarrelDIRC_ID`).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The hpDIRC plugin is the **shortest detector plugin in EICrecon**: 43 lines,
one factory, and the reconstruction stops at raw hits. There is no track
propagation to the bars, no time-based imaging, no likelihood, and no
`CherenkovParticleID` producer. Everything is registered in
[`src/detectors/DIRC/DIRC.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/DIRC/DIRC.cc).
The runtime flag prefix is `DIRC:` (16 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json), all
belonging to the single digitization factory).

## Chain overview

`DIRCBarHits` (edm4hep::SimTrackerHit) + `EventHeader`
→ **PhotoMultiplierHitDigi** → **`DIRCRawHits`** (+ `DIRCRawHitsLinks`, `DIRCRawHitsAssociations`)

That is the entire plugin
([`DIRC.cc#L39-L41`](https://github.com/eic/EICrecon/blob/main/src/detectors/DIRC/DIRC.cc#L39-L41)).

## Digitization parameters

**Algorithm:** [`PhotoMultiplierHitDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PhotoMultiplierHitDigi.cc)
— described on the
[PID page]({{ site.baseurl }}{% link docs/eicrecon/pid.md %}).

| parameter | struct default | DIRC value | meaning |
|---|---|---|---|
| `detectorName` | `""` | **not set** (stays `""`) | DD4hep detector element |
| `readoutClass` | `""` | **not set** (stays `""`) | readout for the pixel-gap lookup |
| `hitTimeWindow` | `20.0` | `20.0` | *"time gate in which 2 input hits will be grouped to 1 output hit // [ns]"* |
| `timeResolution` | `1/16` | `1/16` | *"time resolution (= 1 / TDC counts per unit time) // [ns]"* |
| `speMean` / `speError` | `80.0` / `16.0` | `80.0` / `16.0` | single-photoelectron ADC mean and sigma |
| `pedMean` / `pedError` | `200.0` / `3.0` | `200.0` / `3.0` | pedestal ADC mean and sigma |
| `enablePixelGaps` | `false` | `false` | pixel-gap hit removal disabled |
| `safetyFactor` | `1.0` | `1.0` | *"or set to 1 to apply no such factor"* |
| `enableQuantumEfficiency` | `true` | **`false`**, and the table is `clear()`ed | *"Actual efficiency is implemented in npsim via a stacking action"* |
| `enableNoise` | `false` | not set (`false`) | dark counts off |

([`PhotoMultiplierHitDigiConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PhotoMultiplierHitDigiConfig.h),
[`DIRC.cc#L25-L36`](https://github.com/eic/EICrecon/blob/main/src/detectors/DIRC/DIRC.cc#L25-L36))

Two of these differ from the two RICH detectors in a way that matters:

- **Quantum efficiency is disabled here on purpose** — the comment says it is
  applied upstream in npsim's stacking action. For the dRICH and pfRICH,
  EICrecon applies it. So a photon-counting comparison across the three
  detectors is not apples-to-apples.
- `detectorName` and `readoutClass` are left empty, so the pixel-gap machinery
  has nothing to look up (consistent with `enablePixelGaps = false`).

## Where barrel PID actually comes from

`DIRCRawHits` has **no consumer anywhere in EICrecon**. It is persisted and
that is the end of it.

Barrel Cherenkov PID in the output comes entirely from the table-based path:
the `DIRCLUTPID` instance of `PIDLookup`, reading
`calibrations/hpdirc.lut.gz`, keyed on `BarrelDIRC_ID`, covering PDG
{11, 211, 321, 2212} over 0.2–10.2 GeV, θ 25–160°, φ 0–30.5°
([`pid_lut.cc`](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc)).
It is the only one of the four LUTs that is charge-asymmetric
(`charge_values = {-1, 1}`).

That table is a parametrisation of standalone studies — **not** something
EICrecon computes from `DIRCBarHits`. If you need hpDIRC pattern recognition,
it lives outside this repository. Full detail on the
[PID page]({{ site.baseurl }}{% link docs/eicrecon/pid.md %}).

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc#L472-L475`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L472-L475)):
`DIRCRawHits`, plus the LUT products `DIRCTruthSeededParticleIDs` and
`DIRCParticleIDs`.

`DIRCRawHitsLinks` and `DIRCRawHitsAssociations` are produced by the factory
but do **not** appear in the default output list; `DIRCBarHits` (the sim hits)
does not either.

## Caveats / needs human verification

1. **This is a known gap, not an oversight of this page.** The hpDIRC has no
   reconstruction in EICrecon beyond digitization. Any statement about ePIC
   barrel PID performance traces back to the LUT, not to code in this
   repository.
2. The MC link/association collections the factory emits are not persisted,
   so even the raw hits cannot be matched back to particles from a default
   output file.
3. `speMean`/`pedMean`/`timeResolution` are copied from the RICH
   configurations with no DIRC-specific justification.
4. Quantum efficiency being applied in npsim rather than EICrecon is stated in
   a single source comment with no link to the npsim implementation —
   worth verifying against the simulation actually used.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
