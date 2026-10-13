---
title: Detector naming & aliases
parent: EICrecon
nav_order: 0
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# Detector naming & aliases

*Also known as: detector name map, subsystem cheat sheet, acronym table, system ID table, collection prefix lookup, plugin name lookup, EndcapP vs EndcapN convention, what is nHCal / LFHCAL / pfRICH / hpDIRC / dRICH / RPOTS / OMD called in the code.*

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d)
and [`eic/epic@main`](https://github.com/eic/epic/blob/main/compact/definitions.xml).
Every claim links to the exact file — verify there before depending on it.

Every ePIC subsystem has **at least three different names**, and people mix
them freely in the same sentence:

1. **Geometry / collection name** — the DD4hep detector name from the `epic`
   compact description. It becomes the prefix of every EDM4eic collection
   (`HcalEndcapNRawHits`, `EcalEndcapPClusters`, …) and of the readout name
   (`HcalEndcapNHits`).
2. **EICrecon plugin name** — the directory under
   [`src/detectors/`](https://github.com/eic/EICrecon/tree/main/src/detectors)
   and, identically, the **runtime flag prefix** (`-PEHCAL:…`).
3. **Colloquial name** — what people say out loud: *nHCal*, *LFHCAL*,
   *pfRICH*, *hpDIRC*, *Roman pots*, *CyMBaL*.

These three rarely coincide. The backward hadronic calorimeter is
`HcalEndcapN` in the geometry, `EHCAL` in EICrecon, and "nHCal" in
conversation. The forward hadronic calorimeter is `LFHCAL` in **both** the
geometry and colloquially, but `FHCAL` in EICrecon — and the `FHCAL` plugin
also contains a second, unrelated detector (`HcalEndcapPInsert`).

## The EndcapP / EndcapN convention

This is the single most common source of confusion, and the geometry
[documents it explicitly](https://github.com/eic/epic/blob/main/compact/definitions.xml):

> - **EndcapP** — Positive Endcap (+z direction). This is the ion beam side.
> - **EndcapN** — Negative Endcap (−z direction). This is the electron beam side.

So, reading across all the words used for the same thing:

| suffix | z | beam | direction words | typical prefixes |
|---|---|---|---|---|
| **`EndcapP`** | +z | hadron / ion / proton beam | forward, positive, hadron-going, ion-side, "p-side" | `EcalEndcapP`, `LFHCAL`, `HcalEndcapPInsert`, `ForwardMPGDEndcap`, `ForwardRICH` |
| **`EndcapN`** | −z | electron beam | backward, negative, electron-going, "n-side" | `EcalEndcapN`, `HcalEndcapN`, `BackwardMPGDEndcap`, `BackwardRICH`, `RICHEndcapN` |

Two traps:

- **P ≠ "primary", N ≠ "north".** They are strictly the sign of z.
- **"Forward" in the far-forward / far-backward detectors means the same
  thing** — far-forward (B0, Roman pots, off-momentum, ZDC) is the +z hadron
  side, far-backward (low-Q² taggers, luminosity spectrometer) is the −z
  electron side. But the *tracker* endcaps do **not** follow the split: a
  single EICrecon plugin (`ECTRK`) and a single collection
  (`SiEndcapTrackerRecHits`) cover **both** silicon tracker endcaps.

The geometry constants also carry the additional oddity that ACTS needs the
barrel/endcap structure built inside-out, so most tracking subsystems get a
*block* of system IDs (one per layer) rather than one
([rationale in `definitions.xml`](https://github.com/eic/epic/blob/main/compact/definitions.xml)).

## Master table

System IDs are the `<constant name="…_ID">` values in
[`compact/definitions.xml`](https://github.com/eic/epic/blob/main/compact/definitions.xml).
Constants marked `<!-- DEPRECATED -->` there are older spellings of the same
number (usually `ECal…`/`HCal…` instead of `Ecal…`/`Hcal…`) and are flagged
below where they exist.

### Trackers

| colloquial name(s) | geometry / collection prefix | EICrecon plugin (flag prefix) | system ID(s) | guide page |
|---|---|---|---|---|
| SVT vertex barrel, vertex layers, MAPS vertex detector, inner barrel | `VertexBarrel` (readout `VertexBarrelHits`) → `SiBarrelVertex…` | `BVTX` | 31–33 (`VertexBarrel_0..2_ID`); subassemblies 25–27; supports `SVT_IB_Support_0..3_ID` 50–53 | [BVTX]({{ site.baseurl }}{% link docs/eicrecon/detectors/bvtx.md %}) |
| SVT barrel tracker, sagitta layers, outer barrel silicon, MAPS barrel | `TrackerBarrel` (readout `SiBarrelHits`) → `SiBarrel…` | `BTRK` | 59–67 (`TrackerBarrel_0..8_ID`) | [BTRK]({{ site.baseurl }}{% link docs/eicrecon/detectors/btrk.md %}) |
| silicon tracker endcaps, forward + backward silicon discs, EndcapP/EndcapN silicon | `TrackerEndcapN` / `TrackerEndcapP` (readout `TrackerEndcapHits`) → `SiEndcapTracker…` | `ECTRK` | N: 68–76 (`TrackerEndcapN_0..8_ID`); P: 77–83 (`TrackerEndcapP_0..6_ID`) | [ECTRK]({{ site.baseurl }}{% link docs/eicrecon/detectors/ectrk.md %}) |
| CyMBaL, inner MPGD barrel, µRWELL barrel, MPGD barrel | `MPGDBarrel` (XML detector `InnerMPGDBarrel`) | `MPGD` | in the 40–85 tracker block; not a dedicated `…_ID` constant | [MPGD]({{ site.baseurl }}{% link docs/eicrecon/detectors/mpgd.md %}) |
| outer MPGD barrel, µRWELL outer barrel | `OuterMPGDBarrel` (XML detector `MPGDOuterBarrel`) | `MPGD` | as above | [MPGD]({{ site.baseurl }}{% link docs/eicrecon/detectors/mpgd.md %}) |
| forward MPGD endcap, forward µRWELL / GEM disc | `ForwardMPGDEndcap` | `MPGD` | as above | [MPGD]({{ site.baseurl }}{% link docs/eicrecon/detectors/mpgd.md %}) |
| backward MPGD endcap, backward µRWELL / GEM disc | `BackwardMPGDEndcap` | `MPGD` | as above | [MPGD]({{ site.baseurl }}{% link docs/eicrecon/detectors/mpgd.md %}) |
| tracker support structures | — | none | 84–85 (`TrackerSupport_0..1_ID`) | — |

Track finding and fitting on top of these lives in
[Tracking]({{ site.baseurl }}{% link docs/eicrecon/tracking.md %}), not in the
per-detector plugins.

### Time of flight

| colloquial name(s) | geometry / collection prefix | EICrecon plugin (flag prefix) | system ID(s) | guide page |
|---|---|---|---|---|
| BTOF, barrel TOF, barrel AC-LGAD, TOF barrel, barrel timing layer | `TOFBarrel` (readout `TOFBarrelHits`) | `BTOF` | 92 (`BarrelTOF_ID`); `TOFSubAssembly_ID` 93 | [BTOF]({{ site.baseurl }}{% link docs/eicrecon/detectors/btof.md %}) |
| ECTOF, FTOF, forward TOF, endcap TOF, TOF endcap, endcap AC-LGAD | `TOFEndcap` (readout `TOFEndcapHits`) | `ECTOF` | 122 (`ForwardTOF_ID`); `BackwardTOF_ID` 132 is reserved but unused by the plugin | [ECTOF]({{ site.baseurl }}{% link docs/eicrecon/detectors/ectof.md %}) |

{: .note }
The EICrecon plugin is called `ECTOF` ("endcap TOF") but the geometry ID it
maps to is `ForwardTOF_ID`, and the LUT-based TOF PID instance is keyed on
`BarrelTOF_ID`
([`pid_lut.cc`](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc)).
"FTOF" and "ECTOF" refer to the same detector.

### Calorimeters

| colloquial name(s) | geometry / collection prefix | EICrecon plugin (flag prefix) | system ID(s) | guide page |
|---|---|---|---|---|
| BEMC, barrel ECal, BIC, barrel imaging calorimeter, ScFi + AstroPix | `EcalBarrel` (`EcalBarrelScFi`, `EcalBarrelImaging`) | `BEMC` | 101 (`EcalBarrel_ID`; DEPRECATED `ECalBarrel_ID`), 105 (`EcalBarrel2_ID`) | [BEMC]({{ site.baseurl }}{% link docs/eicrecon/detectors/bemc.md %}) |
| EEMC, backward ECal, electron endcap ECal, crystal endcap, PbWO₄ endcap | `EcalEndcapN` | `EEMC` | 103 (`EcalEndcapN_ID`; DEPRECATED `ECalEndcapN_ID`) | [EEMC]({{ site.baseurl }}{% link docs/eicrecon/detectors/eemc.md %}) |
| FEMC, forward ECal, hadron endcap ECal | `EcalEndcapP` | `FEMC` | 102 (`EcalEndcapP_ID`; DEPRECATED `ECalEndcapP_ID`); insert 106 (`EcalEndcapPInsert_ID`) has no plugin | [FEMC]({{ site.baseurl }}{% link docs/eicrecon/detectors/femc.md %}) |
| BHCal, barrel HCal, outer HCal, re-used sPHENIX HCal | `HcalBarrel` | `BHCAL` | 111 (`HcalBarrel_ID`; DEPRECATED `HCalBarrel_ID`) | [BHCAL]({{ site.baseurl }}{% link docs/eicrecon/detectors/bhcal.md %}) |
| nHCal, backward HCal, electron endcap HCal | `HcalEndcapN` | `EHCAL` | 113 (`HcalEndcapN_ID`; DEPRECATED `HCalEndcapN_ID`) | [EHCAL]({{ site.baseurl }}{% link docs/eicrecon/detectors/ehcal.md %}) |
| LFHCAL, forward HCal, hadron endcap HCal, pHCal | `LFHCAL` | `FHCAL` | 116 (`LFHCAL_ID`) | [FHCAL]({{ site.baseurl }}{% link docs/eicrecon/detectors/fhcal.md %}) |
| forward HCal insert, high-η insert | `HcalEndcapPInsert` | `FHCAL` | 115 (`HcalEndcapPInsert_ID`; DEPRECATED `HCalEndcapPInsert_ID`) | [FHCAL]({{ site.baseurl }}{% link docs/eicrecon/detectors/fhcal.md %}) |
| ZDC ECal, crystal ZDC, LYSO ZDC | `EcalFarForwardZDC` | `ZDC` | 164 (`ZDC_Crystal_ID`); also 163/165/166 for the silicon and W/Pb-Si layers | [ZDC]({{ site.baseurl }}{% link docs/eicrecon/detectors/zdc.md %}) |
| ZDC HCal, SiPM-on-tile ZDC, Pb/Sci ZDC | `HcalFarForwardZDC` | `ZDC` | 167 (`ZDC_PbSci_ID` = `HcalFarForwardZDC_SiPMonTile_ID`) | [ZDC]({{ site.baseurl }}{% link docs/eicrecon/detectors/zdc.md %}) |
| B0 ECal, B0 calorimeter, B0 preshower | `B0ECal` | `B0ECAL` | 169 (`B0ECal_ID`); `B0Preshower_Station_1_ID` 154 | [B0ECAL]({{ site.baseurl }}{% link docs/eicrecon/detectors/b0ecal.md %}) |
| LumiSpecCAL, lumi ECal, luminosity calorimeter | `EcalLumiSpec` | `LUMISPECCAL` | 194 (`LumiSpecCAL_ID`) | [LUMISPECCAL]({{ site.baseurl }}{% link docs/eicrecon/detectors/lumispeccal.md %}) |

The geometry also defines `HCalSubAssembly_ID` 110 (marked `UNUSED`),
`CrystalEndcap_ID` 104 (`UNUSED`), and `PassiveSteelRingEndcapP_ID` 114.
There is **no `HcalEndcapP_ID` constant** — the forward HCal is `LFHCAL_ID`.

### Particle identification

| colloquial name(s) | geometry / collection prefix | EICrecon plugin (flag prefix) | system ID(s) | guide page |
|---|---|---|---|---|
| dRICH, dual-radiator RICH, forward RICH, aerogel + gas RICH | `DRICH` (readout `DRICHHits`) → `DRICH…` | `DRICH` | 120 (`ForwardRICH_ID`) | [DRICH]({{ site.baseurl }}{% link docs/eicrecon/detectors/drich.md %}) |
| pfRICH, proximity-focusing RICH, backward RICH, electron-side RICH, mRICH (superseded) | `PFRICH` (readout `PFRICHHits`) → collections named **`RICHEndcapN…`** | `PFRICH` | 131 (`BackwardRICH_ID`); 130 was the older Modular RICH slot | [PFRICH]({{ site.baseurl }}{% link docs/eicrecon/detectors/pfrich.md %}) |
| hpDIRC, DIRC, barrel DIRC, high-performance DIRC, barrel Cherenkov | `DIRC` (readout `DIRCBarHits`) → `DIRC…` | `DIRC` | 90 (`BarrelDIRC_ID`) | [DIRC]({{ site.baseurl }}{% link docs/eicrecon/detectors/dirc.md %}) |
| TOF PID (barrel + endcap combined) | see TOF row above | `BTOF` / `ECTOF` + `pid_lut` | 92 (`BarrelTOF_ID`) | [Particle identification]({{ site.baseurl }}{% link docs/eicrecon/pid.md %}) |
| barrel TRD, forward TRD | — | none (reserved in geometry only) | 91 (`BarrelTRD_ID`), 121 (`ForwardTRD_ID`) | — |

{: .note }
**pfRICH is the worst offender in the whole table.** The compact detector and
readout are called `PFRICH`/`PFRICHHits`, the EICrecon plugin directory and
flag prefix are `PFRICH`, but every output collection is named
`RICHEndcapN…` (`RICHEndcapNRawHits`, `RICHEndcapNParticleIDs`), and the
geometry constant is `BackwardRICH_ID`. Four names, one detector.

### Far-forward (+z, hadron side)

| colloquial name(s) | geometry / collection prefix | EICrecon plugin (flag prefix) | system ID(s) | guide page |
|---|---|---|---|---|
| B0 tracker, B0 silicon, B0pf tracker | `B0Tracker` (readout `B0TrackerHits`) | `B0TRK` | 150–153 (`B0Tracker_Station_1..4_ID`); companion 157, subassembly 158 | [B0TRK]({{ site.baseurl }}{% link docs/eicrecon/detectors/b0trk.md %}) |
| Roman pots, RP, RPOTS, forward Roman pots | `ForwardRomanPot` | `RPOTS` | 155–156 (`ForwardRomanPot_Station_1..2_ID`) | [RPOTS]({{ site.baseurl }}{% link docs/eicrecon/detectors/rpots.md %}) |
| OMD, off-momentum detector, off-momentum tracker, FOFFMTRK | `ForwardOffMTracker` | `FOFFMTRK` | 159–162 (`ForwardOffMTracker_station_1..4_ID`) | [FOFFMTRK]({{ site.baseurl }}{% link docs/eicrecon/detectors/foffmtrk.md %}) |
| ZDC | see calorimeter table | `ZDC` | 163–167 | [ZDC]({{ site.baseurl }}{% link docs/eicrecon/detectors/zdc.md %}) |
| B0 ECal | see calorimeter table | `B0ECAL` | 169 | [B0ECAL]({{ site.baseurl }}{% link docs/eicrecon/detectors/b0ecal.md %}) |
| far-forward beamline magnets (B0pf, B0apf, Q1apf, Q1bpf, Q2pf, B1pf, B1apf, B2pf) | `B0PF`, `B0APF`, `Q1APF`, `Q1BPF`, `Q2PF`, `B1PF`, `B1APF`, `B2PF` | none | 170–177 | — |

### Far-backward (−z, electron side)

| colloquial name(s) | geometry / collection prefix | EICrecon plugin (flag prefix) | system ID(s) | guide page |
|---|---|---|---|---|
| low-Q² taggers, LOWQ2, tagger tracker, Q² taggers, tagger 1 / tagger 2 | `TaggerTracker` (readout `TaggerTrackerHits`) | `LOWQ2` | 198 (`TaggerTracker_ID`); tagger calorimeter 199 (`TaggerCalorimeter_ID`) | [LOWQ2]({{ site.baseurl }}{% link docs/eicrecon/detectors/lowq2.md %}) |
| luminosity spectrometer calorimeter, LumiSpecCAL | `EcalLumiSpec` | `LUMISPECCAL` | 194 | [LUMISPECCAL]({{ site.baseurl }}{% link docs/eicrecon/detectors/lumispeccal.md %}) |
| luminosity spectrometer tracker | `LumiSpecTracker` | none | 193 | — |
| luminosity direct photon calorimeter | `LumiDirectPCAL` | none | 195 | — |
| lumi collimator / dipole / window, backwards beamline | — | none | 190, 191, 192, 197 | — |

### Non-detector system IDs

| what | constants | IDs |
|---|---|---|
| beam pipe | `BeamPipe_ID`, `BeamPipeB0_ID` | 10, 11 |
| solenoid + support + yoke | `Solenoid_ID`, `SolenoidSupport_ID`, `SolenoidYoke_ID` | 140–142 |
| electron-side magnets | `Q0EF_ID`, `Q1EF_ID`, `B0Window_ID` | 180, 181, 182 |
| vacuum magnet element | `VacuumMagnetElement_1_ID` | 168 |

## Plugin ↔ flag prefix, at a glance

Every directory under
[`src/detectors/`](https://github.com/eic/EICrecon/tree/main/src/detectors) is
one JANA2 plugin, and its name is *exactly* the runtime flag prefix. The flag
counts are from the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json):

| plugin / flag prefix | flags | what it covers |
|---|---|---|
| `BEMC` | 244 | barrel ECal (ScFi + imaging) |
| `EEMC` | 125 | backward endcap ECal |
| `FEMC` | 116 | forward endcap ECal |
| `BHCAL` | 120 | barrel HCal |
| `EHCAL` | 111 | backward endcap HCal |
| `FHCAL` | 214 | LFHCAL **and** the forward HCal insert |
| `ZDC` | 232 | ZDC ECal **and** ZDC HCal |
| `B0ECAL` | 88 | B0 ECal |
| `LUMISPECCAL` | 88 | luminosity spectrometer ECal |
| `BVTX` | 9 | vertex barrel silicon |
| `BTRK` | 9 | barrel silicon tracker |
| `ECTRK` | 9 | **both** silicon tracker endcaps |
| `MPGD` | 37 | **all four** MPGDs |
| `BTOF` | 55 | barrel TOF |
| `ECTOF` | 48 | endcap TOF |
| `DRICH` | 44 | dRICH digitization + IRT PID |
| `PFRICH` | 16 | pfRICH digitization only |
| `DIRC` | 16 | hpDIRC digitization only |
| `B0TRK` | 9 | B0 tracker |
| `RPOTS` | 36 | Roman pots |
| `FOFFMTRK` | 23 | off-momentum tracker |
| `LOWQ2` | 87 | low-Q² taggers |

Note the plugins that cover more than one detector (`FHCAL`, `ZDC`, `MPGD`,
`ECTRK`): a flag under those prefixes still names the *factory instance*, so
`FHCAL:LFHCALRecHits:…` and `FHCAL:HcalEndcapPInsertRecHits:…` are separate
namespaces inside one prefix.

## Caveats / needs human verification

1. **The ID range documentation blocks in `definitions.xml` are stale.** The
   prose block for the far-forward region says *"Forward Roman Pot ID: 150,
   Forward B0 Tracker ID: 151, Zero Degree Cal. Ecal ID: 160, Hcal ID: 161"*,
   but the constants immediately below it assign 150–153 to
   `B0Tracker_Station_1..4_ID`, 155–156 to the Roman pots, and 160–161 to
   `ForwardOffMTracker_station_2..3_ID`. Likewise the far-backward block says
   *"Low-Q2 Tagger 1 ID: 195, Tagger 2 ID: 196, Tagger Vacuum ID: 199"* while
   the constants give `LumiDirectPCAL_ID` 195, `TaggerTracker_ID` 198 and
   `TaggerCalorimeter_ID` 199. **Trust the `<constant>` values, not the
   surrounding `<documentation>`.**
2. The MPGD detectors have no dedicated `…_ID` constants in
   `definitions.xml`; they draw from the 40–85 tracker block via the
   subassembly mechanism. The exact assignment lives in the MPGD compact
   files, which this page has not traced.
3. `ZDC_PbSci_ID` and `HcalFarForwardZDC_SiPMonTile_ID` are both defined as
   167 in the same file — a duplicate that is presumably intentional
   (rename in progress) but is not commented as such.
4. The colloquial names are collected from usage, not from any authoritative
   list; there is no canonical glossary in either repository. Additions
   welcome.
5. `BackwardTOF_ID` (132) and `ForwardTRD_ID`/`BarrelTRD_ID` (121/91) are
   allocated but no compact detector or EICrecon plugin uses them at this
   commit.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`,
[eic/epic](https://github.com/eic/epic) `compact/definitions.xml` @ `main`,
and the [CI flags dump](https://eicrecon.epic-eic.org/e_craterlake_flags.json)
(fetched 2026-08-19). AI-authored draft — verify against source.*
