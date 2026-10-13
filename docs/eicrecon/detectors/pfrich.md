---
title: pfRICH — Backward RICH (PFRICH)
parent: EICrecon
nav_order: 19
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# ePIC Proximity-Focusing RICH (PFRICH) Reconstruction

*Also known as: pfRICH, proximity-focusing RICH, backward RICH, electron-side RICH, electron-endcap RICH, mRICH / modular RICH (the superseded design in the same slot), PFRICH (geometry detector name), PFRICHHits (readout), **RICHEndcapN…** (collection prefix), PFRICH (flag prefix), system ID 131 (`BackwardRICH_ID`; 130 was the older Modular RICH slot).*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

The pfRICH plugin registers **exactly one factory**: a photosensor digitizer.
There is no track propagation, no ring finding, no IRT chain, no
`CherenkovParticleID` producer. 56 lines, registered in
[`src/detectors/PFRICH/PFRICH.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/PFRICH/PFRICH.cc).
The runtime flag prefix is `PFRICH:` (16 flags in the
[CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json), all
belonging to the single digitization factory).

{: .note }
**Four names, one detector.** The compact detector and its readout are
`PFRICH` / `PFRICHHits`; the plugin directory and flag prefix are `PFRICH`;
every output collection is named `RICHEndcapN…`; and the geometry constant is
`BackwardRICH_ID`. See
[Detector naming & aliases]({{ site.baseurl }}{% link docs/eicrecon/naming.md %}).

## Chain overview

`PFRICHHits` (edm4hep::SimTrackerHit) + `EventHeader`
→ **PhotoMultiplierHitDigi** → **`RICHEndcapNRawHits`** (+ `RICHEndcapNRawHitsLinks`, `RICHEndcapNRawHitsAssociations`)

That is the whole plugin
([`PFRICH.cc#L51-L54`](https://github.com/eic/EICrecon/blob/main/src/detectors/PFRICH/PFRICH.cc#L51-L54)).

## Digitization parameters

**Algorithm:** [`PhotoMultiplierHitDigi`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PhotoMultiplierHitDigi.cc)
— groups photon hits inside a time gate, applies quantum efficiency and a
safety factor, converts photoelectrons to ADC counts with a pedestal, and
quantises time. Described on the
[PID page]({{ site.baseurl }}{% link docs/eicrecon/pid.md %}).

| parameter | struct default | pfRICH value | meaning |
|---|---|---|---|
| `detectorName` | `""` | `"PFRICH"` | DD4hep detector element |
| `readoutClass` | `""` | `"PFRICHHits"` | readout used for the pixel-gap lookup |
| `hitTimeWindow` | `20.0` | `20.0` | *"time gate in which 2 input hits will be grouped to 1 output hit // [ns]"* |
| `timeResolution` | `1/16` | `1/16` | *"time resolution (= 1 / TDC counts per unit time) // [ns]"* |
| `speMean` / `speError` | `80.0` / `16.0` | `80.0` / `16.0` | single-photoelectron ADC mean and sigma |
| `pedMean` / `pedError` | `200.0` / `3.0` | `200.0` / `3.0` | pedestal ADC mean and sigma |
| `enablePixelGaps` | `false` | **`true`** | *"enable/disable removal of hits in gaps between pixels"* |
| `safetyFactor` | `1.0` | **`0.7`** | conservative reduction of the photoelectron yield |
| `enableNoise` | `false` | `false` | dark-count injection, off |
| `noiseRate` | `20000` | `20000` | `[Hz]` |
| `noiseTimeWindow` | `20.0` | `20.0 * dd4hep::ns` | see caveat 3 |
| `enableQuantumEfficiency` | `true` | `true` (table re-assigned with the same 17 points) | QE vs wavelength `[nm]` |

([`PhotoMultiplierHitDigiConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PhotoMultiplierHitDigiConfig.h),
[`PFRICH.cc#L29-L48`](https://github.com/eic/EICrecon/blob/main/src/detectors/PFRICH/PFRICH.cc#L29-L48))

The configuration is **identical to the dRICH's** apart from `detectorName`
and `readoutClass` — see
[DRICH]({{ site.baseurl }}{% link docs/eicrecon/detectors/drich.md %}).

## Where pfRICH PID actually comes from

`RICHEndcapNRawHits` has **no consumer inside EICrecon**. Backward-endcap
Cherenkov PID in the output is produced entirely by the table-based path:
the `RICHEndcapNLUTPID` instance of `PIDLookup`, reading
`calibrations/pfrich.lut`, keyed on `BackwardRICH_ID`, covering PDG
{11, 211, 321, 2212} over 0.4–15.2 GeV and θ 2.65–3.0775 rad
([`pid_lut.cc`](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc)).

That table is a parametrisation of standalone studies. **Nothing in EICrecon
derives it from `PFRICHHits`.** If you need pfRICH pattern recognition, it
lives outside this repository. Full detail on the
[PID page]({{ site.baseurl }}{% link docs/eicrecon/pid.md %}).

## What is persisted, and who consumes it

Persisted by default ([`JEventProcessorPODIO.cc#L141-L146`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L141-L146)):
`RICHEndcapNRawHits`, `RICHEndcapNRawHitsLinks`,
`RICHEndcapNRawHitsAssociations`, and the LUT products
`RICHEndcapNTruthSeededParticleIDs` / `RICHEndcapNParticleIDs`.

Note that `PFRICHHits` — the sim-hit collection — is **not** in the default
output list.

## Caveats / needs human verification

1. **Digitization is a dead end.** `RICHEndcapNRawHits` is produced,
   persisted, and never read. Same situation as
   [hpDIRC]({{ site.baseurl }}{% link docs/eicrecon/detectors/dirc.md %}).
2. The digitization constants are copied from the dRICH (`speMean = 80`,
   `pedMean = 200`, `safetyFactor = 0.7`, …) even though the sensors and
   optics differ. No pfRICH-specific tuning is visible in the source.
3. `noiseTimeWindow = 20.0 * dd4hep::ns` yields `2e-08` in the flag dump while
   the field is documented in ns — a unit mismatch, inert only because
   `enableNoise = false`.
4. The QE table is `clear()`ed and re-assigned with the identical struct
   defaults.
5. The four-way name mismatch (`PFRICH` / `PFRICHHits` / `RICHEndcapN…` /
   `BackwardRICH_ID`) is a permanent trap for collection lookups and for
   anyone grepping the flag dump.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
