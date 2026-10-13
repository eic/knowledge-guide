---
title: CalorimeterHitDigi
parent: EICrecon
nav_order: 30
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# CalorimeterHitDigi — sim hits to raw ADC/TDC words

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

`CalorimeterHitDigi` is the front-end emulator that stands between Geant4 and
everything else in the calorimeter chain. Its own header summarises it as
*"A general digitization for CalorimeterHit from simulation: 1. Smear energy
deposit with a/sqrt(E/GeV) + b + c/E or a/sqrt(E/GeV) (relative value);
2. Digitize the energy with dynamic ADC range and add pedestal (mean +- sigma);
3. Time conversion with smearing resolution (absolute value); 4. Signal is
summed if the SumFields are provided"*
([CalorimeterHitDigi.h#L4-L8](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.h#L4-L8)).
It consumes `edm4hep::EventHeader` + `edm4hep::SimCalorimeterHit` and emits an
`edm4hep::RawCalorimeterHit` collection plus MC-truth links and associations
([CalorimeterHitDigi.h#L34-L50](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.h#L34-L50)).

## What it does to the data

**Readout-segmentation collapse.** Geant4 records a deposition per sensitive
volume, which for a segmented readout means one sim hit per fibre, per
longitudinal slice, per strip. A real channel does not see that granularity: it
sees one summed signal. The algorithm therefore builds a mask from the cellID
fields listed in `fields`, and groups sim hits by `cellID & ~mask`
([L102-L110](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L102-L110),
[L149-L160](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L149-L160)).
Every hit whose cellID differs *only* in the listed fields lands in the same
group. With `fields` empty the mask is all-ones and each cellID stays its own
channel. Within a group the energies are added, and the output raw hit inherits
the cellID of the *most energetic* member, so that the written cellID is always
a real MC cellID rather than a synthetic masked value
([L164-L207](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L164-L207),
[L268](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L268)).

**Energy resolution smearing.** The summed deposit is multiplied by
`max(0, 1 + eResRel)`, where `eResRel` is a unit Gaussian scaled by the
three-term relative resolution
([L214-L230](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L214-L230)):

```
eResRel = N(0,1) * sqrt( (eRes[0]/sqrt(edep))^2 + eRes[1]^2 + (eRes[2]/edep)^2 )
edep   *= max(0.0, 1.0 + eResRel)
```

`eRes[0]` is the stochastic term (photostatistics and sampling fluctuations,
falling as 1/sqrt(E)), `eRes[1]` the constant term (calibration spread, leakage,
non-uniformity), `eRes[2]` the noise term (rising as 1/E). Energies are in GeV
in `edm4hep`, so `eRes[0]/sqrt(edep)` is the usual `a/sqrt(E/GeV)`. Note that
the code adds the three terms **in quadrature**, while the header comment writes
them as a plain sum — see caveats. The smearing is only applied when
`edep > threshold`; below that the hit passes through unsmeared but is **not
dropped**. The `max(0.0, ...)` clamp is what stops an unlucky downward
fluctuation from producing a negative deposit.

**ADC quantisation.** A pedestal `ped = pedMeanADC + N(0,1)*pedSigmaADC` is
drawn per channel and the smeared energy is projected onto the ADC scale
([L223](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L223),
[L232-L234](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L232-L234)):

```
adc = max( llround( ped + edep * corrMeanScale / dyRangeADC * capADC ), 0 )
amplitude = min( adc, capADC )
```

`dyRangeADC` is the energy that saturates the channel and `capADC` the number of
counts at full scale, so `dyRangeADC/capADC` is the LSB. The `max(..., 0)` guards
against a negative pedestal fluctuation wrapping the unsigned amplitude, and the
`min(..., capADC)` implements hard saturation of the front end
([L269](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L269)).
`corrMeanScale` is a string expression compiled once at `init()` with all cellID
fields of the readout in scope, evaluated per hit on the leading sim hit — it
exists so a detector can fold a position-dependent response correction (or, in
FEMC's ScFi mode, the inverse sampling fraction) into digitisation
([L112-L125](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L112-L125)).

**Photon-counting readout models.** Two alternatives to the linear `simple`
model exist ([L235-L261](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L235-L261)).
`poisson_photon` converts the deposit into a mean photon count
`edep * lightYield * photonDetectionEfficiency`, draws a Poisson realisation and
scales it against the photon count corresponding to `dyRangeADC` — this puts
genuine photostatistics into the digitised amplitude instead of parameterising
it through `eRes[0]`. `sipm` goes further: it draws the detected photons from a
binomial with success probability `photonDetectionEfficiency`, then applies the
SiPM pixel-saturation law
`N_fired = N_pix * (1 - exp(-N_det/N_pix))` with `N_pix = numEffectiveSipmPixels`,
so the response becomes non-linear at high occupancy exactly as a real SiPM does.

**Time.** For each sim hit the earliest Geant4 contribution time is taken; the
group time is that of the leading (most energetic) hit
([L179-L195](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L179-L195)).
It is smeared by a Gaussian of width `tRes` and quantised with
`stepTDC = 1 ns / resolutionTDC`
([L82-L83](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L82-L83),
[L227](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L227)):
`tdc = llround((time + N(0,1)*tRes) * stepTDC)`. `capTime` is compared against
the hit time, but only to emit a debug message — the hit is retained either way
([L183-L186](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L183-L186),
[L208-L211](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L208-L211)).

**Zero suppression: there is none here.** Every merge group produces exactly one
raw hit, including groups that digitise to pure pedestal. This is deliberate in
the ePIC configuration — most plugins set `threshold = 0` with a comment such as
*"threshold is set in ADC in reco"* ([BEMC.cc#L243](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L243))
or *"Use ADC cut instead"* ([BHCAL.cc#L57](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L57)),
and the actual cut lives in
[CalorimeterHitReco](calorimeter-hit-reco.md).
Only B0ECAL sets a non-zero `threshold` (5 MeV), and even there it only disables
smearing, it does not suppress the hit
([B0ECAL.cc#L34](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L34)).

**MC truth.** One `MCRecoCalorimeterHitLink` and one
`MCRecoCalorimeterHitAssociation` are written per contributing sim hit, with the
weight set to that hit's fractional share of the group energy
([L197-L206](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L197-L206),
[L273-L280](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L273-L280)).
Note the divisor is the *smeared* total, so weights do not sum to exactly one.

**Randomness.** The generator is seeded per event via `UniqueIDGenSvc` from the
event header and the algorithm's instance name, which makes results reproducible
independently of thread scheduling
([L144-L146](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L144-L146));
the long comment block at
[L59-L72](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L59-L72)
explains why a global RNG service was rejected.

## Configuration

Every field of
[`CalorimeterHitDigiConfig`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigiConfig.h#L14-L40).
Defaults are the literal struct initialisers; dd4hep's base units are GeV, mm,
ns, so a bare `1` in an energy field means 1 GeV and in a time field 1 ns.

| field | struct default | meaning |
|---|---|---|
| `eRes` | *no initialiser* (`std::vector<double> eRes;`) | Relative energy-resolution coefficients `{a, b, c}`: stochastic, constant, noise. `init()` resizes an empty vector to three zeros and throws if the size is anything other than 0 or 3 ([L74-L79](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L74-L79)). |
| `tRes` | *no initialiser* (`double tRes;`) | Gaussian sigma of the absolute time smearing, divided by `dd4hep::ns` at init. |
| `threshold` | `1.0 * dd4hep::keV` → 1 keV | Deposit above which energy smearing is applied. **Not** a zero-suppression cut — sub-threshold hits are still digitised and written. |
| `readoutType` | `"simple"` | Readout model: `simple` (linear), `poisson_photon`, or `sipm`. Any other string throws at init ([L127-L134](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L127-L134)). |
| `lightYield` | `0. / edm4eic::unit::GeV` → 0 | Photons produced per unit deposited energy. Used only by `poisson_photon` and `sipm`. |
| `photonDetectionEfficiency` | `0.0` | (light collection efficiency) × (quantum efficiency), per the struct comment. Used only by `poisson_photon` and `sipm`. |
| `numEffectiveSipmPixels` | `0` | Effective SiPM pixel count driving the saturation law `N_pix*(1-exp(-N_det/N_pix))`. Used only by `sipm`. |
| `capADC` | `1` | ADC counts at full scale (the dynamic range in counts). Amplitudes are clipped to this value. |
| `capTime` | `1000` → 1000 ns | Struct comment: *"dynamic range in ns"*. In the current code it only triggers a debug message; no hit is discarded because of it. |
| `dyRangeADC` | `1` → 1 GeV | Deposited energy corresponding to full ADC scale. |
| `pedMeanADC` | `0` | Pedestal mean in ADC counts, added to every channel. |
| `pedSigmaADC` | `0` | Pedestal (electronics-noise) Gaussian sigma in ADC counts. |
| `resolutionTDC` | `1` → 1 ns | TDC least count; `stepTDC = 1 ns / resolutionTDC` counts per ns. |
| `corrMeanScale` | `"1.0"` | Multiplicative response correction, a **string expression** compiled by `EvaluatorSvc` with every cellID field of `readout` in scope, evaluated per hit on the leading sim hit. |
| `readout` | `""` | DD4hep readout name. **Required** — an empty value, or a name whose idSpec cannot be loaded, throws at init ([L86-L100](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L86-L100)). |
| `fields` | `{}` | cellID fields summed over: hits differing only in these fields are merged into one channel. Empty means no merging. |

## Which detectors use it

Thirteen instances across nine JANA2 plugins. Each row is one
`JOmniFactoryGeneratorT<CalorimeterHitDigi_factory>` registration; the instance
name equals the output raw-hit collection name in every case. All of them take
`{"EventHeader", "<...>Hits"}` as input and produce
`{"<name>", "<name>Links", "<name>Associations"}` — spelled `<X>RawHitLinks` /
`<X>RawHitAssociations`.

| plugin | instance / output collection | readout |
|---|---|---|
| [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L237-L254) | `EcalBarrelScFiRawHits` | `EcalBarrelScFiHits` |
| [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L379-L395) | `EcalBarrelImagingRawHits` | `EcalBarrelImagingHits` |
| [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L39-L63) | `EcalEndcapNRawHits` | `EcalEndcapNHits` |
| [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L70-L119) | `EcalEndcapPRawHits` (two mutually exclusive variants) | `EcalEndcapPHits` |
| [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L31-L47) | `EcalFarForwardZDCRawHits` | `EcalFarForwardZDCHits` |
| [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L141-L157) | `HcalFarForwardZDCRawHits` | `HcalFarForwardZDCHits` |
| [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L38-L54) | `HcalEndcapNRawHits` | `HcalEndcapNHits` |
| [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L41-L57) | `HcalEndcapPInsertRawHits` | `HcalEndcapPInsertHits` |
| [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L181-L198) | `LFHCALRawHits` | `LFHCALHits` |
| [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L27-L42) | `EcalLumiSpecRawHits` | `EcalLumiSpecHits` |
| [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L27-L43) | `B0ECalRawHits` | `B0ECalHits` |
| [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L51-L68) | `HcalBarrelRawHits` | `HcalBarrelHits` |

### Key parameters compared

`resolutionTDC` is 10 ps everywhere except BEMC Imaging (3.25 ns), BHCAL (1 ps)
and B0ECAL (`1e-11`, i.e. 10 ps written as a raw number).

| instance | `capADC` | `dyRangeADC` | `pedMeanADC` / `pedSigmaADC` | `eRes` = {a, b, c} | `readoutType` | `fields` |
|---|---|---|---|---|---|---|
| `EcalBarrelScFiRawHits` | 16384 (14-bit) | 1500 MeV | 100 / 1 | {0, 0, 0} | simple | `{fiber, z}` |
| `EcalBarrelImagingRawHits` | 8192 (13-bit) | 3 MeV | 14 / 5 | {0, 0.02, 0} | simple | — |
| `EcalEndcapNRawHits` | 16384 | 20 GeV | 20 / 1 | {0, 0, 0} | **sipm** | — |
| `EcalEndcapPRawHits` (homogeneous) | 16384 | 100 GeV | 200 / 2.4576 | {0.11333, 0.03, 0} | **sipm** | — |
| `EcalEndcapPRawHits` (ScFi) | 16384 | 100 GeV | 200 / 2.4576 | {0, 0.022, 0} | **sipm** | `{fiber_x, fiber_y}` |
| `EcalFarForwardZDCRawHits` | 32768 | 2000 MeV | 400 / 3.2 | {} | simple | — |
| `HcalFarForwardZDCRawHits` | 65536 | 1000 MeV | 400 / 2 | {} | simple | — |
| `HcalEndcapNRawHits` | 32768 | 200 MeV | 10 / 2 | {} | simple | — |
| `HcalEndcapPInsertRawHits` | 32768 | 200 MeV | 10 / 2 | {} | simple | — |
| `LFHCALRawHits` | 65536 | 1 GeV | 50 / 10 | {} | simple | `{layerz}` |
| `EcalLumiSpecRawHits` | 16384 | 20 GeV | 100 / 1 | {0, 0.02, 0} | simple | — |
| `B0ECalRawHits` | 16384 | 170 GeV | 100 / 1 | {0.0326, 0, 0} | simple | — |
| `HcalBarrelRawHits` | 65536 | 1 GeV | 300 / 2 | {} | simple | — |

Three instances use `fields`, and each collapses a different kind of
segmentation: BEMC ScFi merges individual fibres and longitudinal `z` segments
into one readout channel, FEMC in ScFi mode merges the `fiber_x`/`fiber_y` grid
inside a tower, and LFHCAL merges the eight `layerz` slices that make up one
longitudinal readout block.

The three photon-counting instances are the two ECal endcaps. EEMC states its
numbers explicitly: 18 pe/MeV measured with a 25 % QE PMT, a geometric factor of
16 × 3×3 mm² sensors over a 20×20 mm² cell at 28 % QE, and 39984 × 16 effective
S14160-3015PS pixels
([EEMC.cc#L46-L53](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L46-L53)).
FEMC uses 1500 photons/GeV at 28.5 % collection efficiency and 4 × 159565 pixels
([FEMC.cc#L51-L53](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L51-L53)).

FEMC is the only plugin that chooses its digitisation at runtime: it reads the
DD4hep constant `EcalEndcapP_Homogeneous_ScFi` and registers either the
homogeneous-crystal variant (flag ≤ 1) or the ScFi variant (flag == 2)
([FEMC.cc#L55-L120](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L55-L120)).
The ScFi variant is also the only user of a non-trivial `corrMeanScale`: it sets
it to `1/0.029043`, folding the inverse sampling fraction into digitisation so
that the downstream reco can run with `sampFrac = "1.00"`
([FEMC.cc#L48-L50](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L48-L50)).

## Runtime flags: names differ from config fields

The JANA2 parameter names are declared in
[`CalorimeterHitDigi_factory.h#L28-L43`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/CalorimeterHitDigi_factory.h#L28-L43)
and do **not** match the C++ config field names. A flag is
`<PLUGIN>:<instance>:<flag name>`, e.g.
`BEMC:EcalBarrelScFiRawHits:capacityADC`.

| config field | runtime flag |
|---|---|
| `eRes` | `energyResolutions` |
| `tRes` | `timeResolution` |
| `capADC` | `capacityADC` |
| `dyRangeADC` | `dynamicRangeADC` |
| `pedMeanADC` | `pedestalMean` |
| `pedSigmaADC` | `pedestalSigma` |
| `corrMeanScale` | `scaleResponse` |
| `fields` | `signalSumFields` |
| `readout` | `readoutClass` |
| `resolutionTDC`, `readoutType`, `lightYield`, `photonDetectionEfficiency`, `numEffectiveSipmPixels` | unchanged |
| `threshold`, `capTime` | **not exposed** — compile-time only |

Note that the digi factory calls the readout flag `readoutClass` while the reco
factory calls the same field `readout`
([CalorimeterHitReco_factory.h#L33](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/CalorimeterHitReco_factory.h#L33)).

## Source

- [`src/algorithms/calorimetry/CalorimeterHitDigi.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.h)
- [`src/algorithms/calorimetry/CalorimeterHitDigi.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc)
- [`src/algorithms/calorimetry/CalorimeterHitDigiConfig.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigiConfig.h)
- [`src/factories/calorimetry/CalorimeterHitDigi_factory.h`](https://github.com/eic/EICrecon/blob/main/src/factories/calorimetry/CalorimeterHitDigi_factory.h)
- [`src/tests/algorithms_test/calorimetry_CalorimeterHitDigi.cc`](https://github.com/eic/EICrecon/blob/main/src/tests/algorithms_test/calorimetry_CalorimeterHitDigi.cc)
  — the only unit test, one case with a single hit and a couple of contributions

## Caveats

1. **Header comment vs. code.** The header says the smearing is
   `a/sqrt(E/GeV) + b + c/E`, but
   [L216-L218](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L216-L218)
   sums the three terms **in quadrature**. Quadrature is the physically
   conventional choice; the comment appears to be stale. For the ePIC
   configurations this is mostly moot — every instance sets at most one non-zero
   coefficient except FEMC's homogeneous variant, whose own comment
   *"(11.333% / sqrt(E)) \oplus 3%"* already spells out quadrature.
2. **`threshold` does not threshold.** Despite the struct comment *"single hit
   energy deposition threshold"*, the value is only used to decide whether to
   apply smearing. No hit is ever dropped by `CalorimeterHitDigi`.
3. **`capTime` is effectively dead.** It is compared to the hit time, and the
   only consequence is a debug message that says the hit is retained anyway. The
   messages at
   [L184-L185](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L184-L185)
   and [L209-L210](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L209-L210)
   also use printf-style `%f` placeholders inside what is an fmt-style logger,
   so the arguments will not be substituted. Whether `capTime` was intended to
   drop out-of-time hits is not determinable from the source.
4. **TDC values are not clamped.** The comment at
   [L225](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L225)
   says *"both adc and tdc values must be positive numbers to avoid integer
   wraparound"*, and `adc` is clamped with `max(..., 0LL)` — but `tdc` is not.
   A negative smeared time assigned to `unsigned long long tdc` wraps around.
5. **Empty-energy merge group.** `max_edep` starts at 0, so if every sim hit in a
   group has exactly zero energy the `time` variable stays at
   `numeric_limits<double>::max()` and the TDC computation overflows
   ([L172](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L172),
   [L191-L195](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L191-L195)).
   The link/association weights are also divided by `edep`
   ([L274](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L274)),
   which is a division by zero in the same situation. Not observed in practice,
   but nothing in the code prevents it.
6. **Group time is a running minimum over maxima.** `time` is updated only inside
   the `if (hit.getEnergy() > max_edep)` branch, as `min(timeC, time)`. It is
   therefore the minimum over the sequence of successive energy leaders, not
   strictly the time of the final leading hit. Probably harmless, arguably
   accidental.
7. **`eRes` and `tRes` have no default member initialiser.** Every ePIC plugin
   uses aggregate initialisation, which value-initialises them to zero, but a
   default-constructed `CalorimeterHitDigiConfig` would leave `tRes`
   indeterminate.
8. **Debug print of `id_mask` is always zero.** At
   [L108](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L108)
   the mask is logged before it is assigned at
   [L110](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitDigi.cc#L110).
   Cosmetic, but misleading when debugging a signal-sum configuration.
9. **Link weights do not sum to one.** They are divided by the smeared,
   post-resolution `edep`, not by the raw sum of contributions.
10. **`resolutionTDC = 1e-11`** in B0ECAL is written as a bare number rather than
    `10 * dd4hep::picosecond`. In dd4hep base units these agree, but the intent
    is only inferable, not stated.
11. B0ECAL is also the only plugin with a non-zero `threshold` (5 MeV), and its
    file does not say why it differs from the "threshold in reco" convention used
    everywhere else.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
(fetched 2026-08-19). AI-authored draft — verify against source.*
