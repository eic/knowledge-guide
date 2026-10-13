---
title: Pulse chain
parent: EICrecon
nav_order: 39
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# Pulse chain (waveform-level digitization)

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

Most EICrecon calorimeter digitization is a shortcut: `CalorimeterHitDigi`
takes a Geant4 energy deposit, smears it with a parametrized resolution, and
turns it straight into an ADC count. That is fast and adequate for physics
studies, but it models no electronics at all — no shaping time, no pile-up
between two particles hitting the same channel, no threshold behaviour, no
saturation, no correlated noise. The four algorithms on this page are the
*realistic* path: they build an actual sampled waveform for every channel and
run it through a model of the front-end ASIC, so that the output is what the
chip would really have written out.

```
edm4hep::SimCalorimeterHit / SimTrackerHit   (or npe hits from EdepToNpeConversion)
        |
        |  PulseGeneration      one analog waveform per hit
        v
edm4eic::SimPulse
        |
        |  PulseCombiner        sum overlapping pulses in the same channel
        v
edm4eic::SimPulse  (combined)
        |
        |  PulseNoise           add correlated 1/f^alpha noise + pedestal
        v
edm4eic::SimPulse  (combined + noise)
        |
        |  CALOROCDigitization  sample at the clock, discriminate
        v
edm4eic::RawCALOROCHit   (ADC / TOA / TOT words)
```

The first three stages are detector-agnostic and are shared with the
tracker/TOF chain; only the last stage is calorimeter-specific. The tracker
analogues are noted at the [bottom of this page](#sibling-roc-digitizers).

{: .note }
Only the ePIC barrel ECal ScFi section currently runs the full four-stage
chain, and its output is not yet consumed by reconstruction — see caveats.

---

## PulseGeneration

**Source:**
[`PulseGeneration.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.h) ·
[`.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.cc) ·
[`Config.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGenerationConfig.h)

The file header says it plainly: *"Convert energy deposition into analog
pulses"*
([`.h#L1-L6`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.h#L1-L6)).

### What it does physically

A sensor does not report an energy; it reports a current that rises, peaks
and decays. This algorithm replaces each simulated hit with that waveform,
sampled on a fixed grid. The hit supplies two numbers — a time and a charge —
extracted by a small adapter per hit type
([`.cc#L179-L202`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.cc#L179-L202)):
for a `SimTrackerHit` they are `getTime()` and `getEDep()`; for a
`SimCalorimeterHit` they are the time of the *earliest* Geant4 contribution
and the total hit energy. The shape function is then evaluated as
`f(t − t_hit, charge)` on a grid of `timestep` bins.

The grid is anchored to an absolute clock, not to the hit: the first bin sits
at `timestep × floor(t_hit / timestep)`, with the code's comment "assume
clocks aligned with time 0"
([`.cc#L225-L226`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.cc#L225-L226)).
That is what makes it legitimate to add two pulses from different hits
sample-by-sample later on.

Only the interesting part of the waveform is stored
([`.cc#L234-L281`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.cc#L234-L281)).
Bins whose amplitude is below `ignore_thres` in absolute value are skipped
while the pulse is still rising (they are counted in `skip_bins` and folded
into the stored start time), and once the pulse has been above threshold the
sampling continues until the amplitude has fallen back below threshold *and*
`min_sampling_time` has elapsed — so the tail is kept long enough for a
time-over-threshold measurement downstream. A pulse that never crosses
`ignore_thres` produces no output object at all. `max_time_bins` is the hard
safety stop on the loop.

The early-exit logic depends on whether the shape is known to have a single
peak. `LandauPulse` declares itself unimodal, so as soon as the amplitude
starts falling before ever crossing threshold the loop can stop; an arbitrary
user expression makes no such promise, so the scan continues to
`max_time_bins` looking for a later peak
([`.cc#L238-L267`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.cc#L238-L267)).

The output `edm4eic::SimPulse` carries the cellID, `interval` (= `timestep`),
the start time, the amplitude vector, the summed integral, the hit position,
and relations back to the originating hit and MC particle
([`.cc#L278-L290`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.cc#L278-L290)).

### Available pulse shapes

The registry is
[`PulseShapeFactory::createPulseShape`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.cc#L160-L177),
and at this commit it recognises exactly one name, with an expression-based
fallback:

| `pulse_shape_function` | implementation | parameters |
|---|---|---|
| `"LandauPulse"` | [`LandauPulse`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.cc#L63-L102) — `charge × gain × TMath::Landau(t, offset·σ, σ, normalized)` | 2 or 3: `gain`, `sigma_analog`, optional `hit_sigma_offset` (default `3.5`); anything else throws |
| *anything else* | [`EvaluatorPulse`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.cc#L106-L158) — the string is compiled as a formula by `EvaluatorSvc` | the expression **must** contain `time` and `charge`, and one `param0`, `param1`, … for each entry of `pulse_shape_params`, or construction throws |

The source comment `// Add more pulse shape variants here as needed`
([`.cc#L166-L168`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.cc#L166-L168))
confirms that the list is meant to grow; there is no CR-RC, gaussian or
bipolar shaper in the tree today.

The Landau shape is a reasonable stand-in for a fast sensor pulse: sharp
leading edge, long tail. Its analytic peak (the Landau MPV) sits at
`(hit_sigma_offset − 0.22278) × sigma_analog`
([`.cc#L86-L96`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.cc#L86-L96)),
which is why the third parameter exists: it shifts the peak away from t = 0
so that the rising edge is actually sampled. That peak time is also used as
a floor on `min_sampling_time`
([`.cc#L204-L210`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.cc#L204-L210)),
guaranteeing the peak is never cut off. The evaluator shape reports a maximum
time of 0 and so gets no such protection.

### Configuration

| field | struct default | meaning |
|---|---|---|
| `pulse_shape_function` | `"LandauPulse"` | shape name, or an EvaluatorSvc expression in `time`, `charge`, `param0`… |
| `pulse_shape_params` | `{1.0, 0.1}` | parameters of the shape; for `LandauPulse` these are gain and `sigma_analog` (a time), optionally the sigma offset |
| `ignore_thres` | `10` | amplitude below which a bin is not sampled; in whatever units the shape returns (ADC-like counts in practice), **not** an energy |
| `timestep` | `0.2 ns` (`0.2 * edm4eic::unit::ns`) | sampling period of the generated waveform, stored as the pulse `interval` |
| `min_sampling_time` | `0 ns` | minimum time to keep sampling after the threshold crossing; raised at init to at least the shape's peak time |
| `max_time_bins` | `10000` | hard cap on samples per pulse |

Defaults from
[`PulseGenerationConfig.h#L10-L18`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGenerationConfig.h#L10-L18).
Runtime flag names differ from the field names:
`pulseShapeFunction`, `pulseShapeParams`, `timestep`, `ignoreThreshold`,
`minSamplingTime`, `maxTimeBins`
([`PulseGeneration_factory.h#L28-L39`](https://github.com/eic/EICrecon/blob/main/src/factories/digi/PulseGeneration_factory.h#L28-L39)).

### Which detectors use it

The algorithm is templated on the hit type and both instantiations are
compiled
([`.cc#L295-L296`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseGeneration.cc#L295-L296)).

| detector | instance | in → out | shape | notable settings |
|---|---|---|---|---|
| BEMC ScFi, +z end ([`BEMC.cc#L149-L158`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L149-L158)) | `EcalBarrelScFiPPulses` | `EcalBarrelScFiPNpeHits` → `EcalBarrelScFiPPulses` | `LandauPulse` | `params={55.37, 10 ns}`, `ignore_thres=1`, `timestep=0.5 ns` |
| BEMC ScFi, −z end ([`BEMC.cc#L159-L168`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L159-L168)) | `EcalBarrelScFiNPulses` | `EcalBarrelScFiNNpeHits` → `EcalBarrelScFiNPulses` | `LandauPulse` | identical to the +z end |
| BTOF ([`BTOF.cc#L100-L108`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L100-L108)) | `LGADPulseGeneration` | `TOFBarrelSharedHits` → `TOFBarrelSmoothPulses` | `LandauPulse` | `params={gain, 0.293951 ns, 3}`, `ignore_thres=0.05×256`, `timestep=0.01 ns` |
| ECTOF ([`ECTOF.cc#L84-L92`](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L84-L92)) | `TOFEndcapSmoothPulses` | `TOFEndcapSharedHits` → `TOFEndcapSmoothPulses` | `LandauPulse` | same as BTOF |
| LOWQ2 tagger ([`LOWQ2.cc#L61-L69`](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L61-L69)) | `TaggerTrackerPulseGeneration` | `TaggerTrackerSharedHits` → `TaggerTrackerHitPulses` | `LandauPulse` | `params={1.0, 2 ns}`, `ignore_thres=1.5e-7`, `timestep=0.2 ns` |

The BEMC instances are the only `SimCalorimeterHit` ones, and they read
photoelectron counts rather than energies, because `EdepToNpeConversion` has
already run. The TOF gain is derived in the plugin so that a deposit of
`Vm = 3e-4 GeV` produces a pulse reaching the full 256-count ADC range, and
is deliberately **negative** — "gain is negative as LGAD voltage is always
negative"
([`BTOF.cc#L91-L99`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L91-L99)) —
which is why the threshold logic uses `std::abs(signal)`.

---

## PulseCombiner

**Source:**
[`PulseCombiner.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseCombiner.h) ·
[`.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseCombiner.cc) ·
[`Config.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseCombinerConfig.h)

File comment: *"Combine pulses into a larger pulse if they are within a
certain time of each other"*
([`.cc#L1-L5`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseCombiner.cc#L1-L5)).

### What it does physically

`PulseGeneration` produces one waveform per simulated hit, but a readout
channel has one amplifier. If two particles deposit energy in the same
channel a few nanoseconds apart, the chip sees a single distorted pulse, not
two — that is pile-up, and reproducing it is the whole point of this stage.

Two things happen. First, pulses are grouped by channel. The grouping key is
the cellID masked down to a chosen granularity
([`.cc#L30-L55`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseCombiner.cc#L30-L55)):
at `init` the algorithm walks the readout's ID descriptor accumulating field
masks in declaration order and stops after `combine_field`, so every cellID
field *finer* than that one is masked away. For the BEMC that field is
`grid`, which merges the many individual fibres of one ScFi cell onto the one
SiPM that actually reads them out. With both `readout` and `combine_field`
left empty the mask stays all-ones and pulses are grouped by exact cellID.

Second, within a channel the pulses are sorted in time and cut into clusters:
a pulse joins the current cluster if it starts before the cluster's current
end time plus `minimum_separation`, otherwise it opens a new one
([`.cc#L113-L148`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseCombiner.cc#L113-L148)).
So `minimum_separation` is the dead-time-like parameter that decides whether
two deposits are seen as one hit or two. Each cluster is summed
sample-by-sample onto a common grid anchored at the earliest pulse's start
time
([`.cc#L150-L176`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseCombiner.cc#L150-L176)),
and the summed pulse inherits the constituents' cellID, interval, position
and all their MC relations; a lone pulse is simply cloned through.

### Configuration

| field | struct default | meaning |
|---|---|---|
| `minimum_separation` | `50 ns` (`50 * edm4eic::unit::ns`) | pulses closer in time than this (measured from the end of the running cluster) are summed into one |
| `readout` | `""` | readout name whose ID descriptor supplies the field masks |
| `combine_field` | `""` | last cellID field to keep; everything declared after it is masked off, merging those cells |

Defaults from
[`PulseCombinerConfig.h#L10-L15`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseCombinerConfig.h#L10-L15).
Flags: `minimumSeperation` *(sic — misspelled in the factory)*, `readout`,
`combineField`
([`PulseCombiner_factory.h#L24-L26`](https://github.com/eic/EICrecon/blob/main/src/factories/digi/PulseCombiner_factory.h#L24-L26)).

### Which detectors use it

| detector | instance | in → out | settings |
|---|---|---|---|
| BEMC ScFi +z ([`BEMC.cc#L169-L177`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L169-L177)) | `EcalBarrelScFiPCombinedPulses` | `EcalBarrelScFiPPulses` → `EcalBarrelScFiPCombinedPulses` | `minimum_separation=100 ns`, `readout="EcalBarrelScFiHits"`, `combine_field="grid"` |
| BEMC ScFi −z ([`BEMC.cc#L178-L186`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L178-L186)) | `EcalBarrelScFiNCombinedPulses` | `EcalBarrelScFiNPulses` → `EcalBarrelScFiNCombinedPulses` | identical |
| BTOF ([`BTOF.cc#L110-L115`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L110-L115)) | `TOFBarrelPulseCombiner` | `TOFBarrelSmoothPulses` → `TOFBarrelCombinedPulses` | `minimum_separation=25 ns`; no readout/field, so exact cellID grouping |
| ECTOF ([`ECTOF.cc#L94-L99`](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L94-L99)) | `TOFEndcapCombinedPulses` | `TOFEndcapSmoothPulses` → `TOFEndcapCombinedPulses` | same as BTOF |
| LOWQ2 tagger ([`LOWQ2.cc#L72-L77`](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L72-L77)) | `TaggerTrackerPulseCombiner` | `TaggerTrackerHitPulses` → `TaggerTrackerCombinedPulses` | `minimum_separation=25 ns` |

The 25 ns used by the trackers is the EIC bunch-crossing period; why the BEMC
uses 100 ns is not commented in the source.

---

## PulseNoise

**Source:**
[`PulseNoise.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseNoise.h) ·
[`.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseNoise.cc) ·
[`Config.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseNoiseConfig.h)

File comment: *"Adds noise to a time series pulse"*
([`.h#L1-L5`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseNoise.h#L1-L5)).

### What it does physically

Electronics noise is not white. Amplifier and sensor noise has a spectrum
that rises towards low frequency, usually parametrized as `1/f^α`, and it is
*correlated* between consecutive samples — which matters, because a threshold
discriminator responds very differently to correlated noise than to
independent per-sample jitter. This stage therefore does not simply add a
gaussian to each bin. It instantiates DD4hep's
`dd4hep::detail::FalphaNoise(poles, alpha, variance)` from DDDigi and draws
one correlated sample per waveform bin
([`.cc#L28-L47`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseNoise.cc#L28-L47)):

```
amplitude[i] += falpha(generator) × scale + pedestal
```

In that model, **`alpha`** is the spectral index of the noise: `α = 0` is a
flat (white) spectrum, `α = 1` is pink/flicker noise, `α = 2` is a
random-walk-like spectrum. **`poles`** is the number of first-order recursive
filter stages the generator uses to approximate that power law — each pole
contributes one exponentially correlated component with its own time
constant, and summing several of them reproduces `1/f^α` over a range of
frequencies. More poles means a better approximation over a wider band at
proportionally more cost; with `α = 0` the spectral shaping is trivial and
the pole count matters little. `variance` sets the variance of the generated
(dimensionless) noise series, `scale` converts it into the amplitude units of
the pulse, and `pedestal` is a constant DC offset added to every sample —
the baseline the discriminator sits on.

The random seed comes from `UniqueIDGenSvc` keyed on the event header and the
algorithm's name
([`.cc#L28-L29`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseNoise.cc#L28-L29)),
so results are reproducible per event and independent of processing order.
Noise is added only to bins of existing pulses: this stage cannot create a
hit out of noise alone, and channels with no pulse stay silent.

### Configuration

| field | struct default | meaning |
|---|---|---|
| `poles` | `5` | number of recursive filter poles used to synthesise the `1/f^α` spectrum |
| `variance` | `1` | variance of the generated noise series before scaling |
| `alpha` | `0.5` | spectral index α of the `1/f^α` noise; 0 = white |
| `scale` | `1000` | multiplies the noise sample into pulse-amplitude units |
| `pedestal` | `0` | constant offset added to every sample |

Defaults from
[`PulseNoiseConfig.h#L8-L24`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseNoiseConfig.h#L8-L24).
Flags: `poles`, `variance`, `alpha`, `scale` — **`pedestal` is not exposed**
as a runtime parameter
([`PulseNoise_factory.h#L24-L27`](https://github.com/eic/EICrecon/blob/main/src/factories/digi/PulseNoise_factory.h#L24-L27)).

### Which detectors use it

| detector | instance | in → out | settings |
|---|---|---|---|
| BEMC ScFi +z ([`BEMC.cc#L187-L198`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L187-L198)) | `EcalBarrelScFiPCombinedPulsesWithNoise` | `EcalBarrelScFiPCombinedPulses` → same + noise | `poles=2`, `variance=0.5`, `alpha=0`, `scale=5.4e-5`, `pedestal=1.6e-4` |
| BEMC ScFi −z ([`BEMC.cc#L199-L210`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L199-L210)) | `EcalBarrelScFiNCombinedPulsesWithNoise` | `EcalBarrelScFiNCombinedPulses` → same + noise | identical |
| LOWQ2 tagger ([`LOWQ2.cc#L80-L89`](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L80-L89)) | `TaggerTrackerPulseNoise` | `TaggerTrackerCombinedPulses` → `TaggerTrackerCombinedPulsesWithNoise` | `poles=5`, `variance=1.0`, `alpha=0.5`, `scale=2e-6`, pedestal left at 0 |

The BEMC deliberately picks white noise (`alpha=0`) with only two poles,
plus a small positive pedestal; the tagger keeps the struct defaults for the
spectrum and only rescales. Neither choice carries a provenance comment.
Both TOF plugins skip this stage entirely.

---

## CALOROCDigitization

**Source:**
[`CALOROCDigitization.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CALOROCDigitization.h) ·
[`.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CALOROCDigitization.cc) ·
[`Config.h`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CALOROCDigitizationConfig.h)

Its algorithm description string: *"Digitizes simulated pulses from a CALOROC
chip"*
([`.h#L25-L29`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CALOROCDigitization.h#L25-L29)).

### What the chip does, and what the code reproduces

CALOROC is the ePIC calorimeter front-end ASIC. It does not integrate the
pulse; it samples the waveform at the machine clock and, in parallel, runs
two discriminators. The algorithm reproduces all three measurements per
channel per event.

**ADC sampling.** The chip samples on a fixed 25 ns grid whose phase relative
to the accelerator clock is `adc_phase`. The code computes which clock tick
first falls inside the pulse (`time_stamp`, the coarse timestamp written to
the output hit), converts it to an index into the amplitude vector, and then
reads `n_samples` amplitudes spaced `time_window / interval` bins apart
([`.cc#L34-L55`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CALOROCDigitization.cc#L34-L55)).
The comment is explicit that "CALOROC measures pulse amplitude for ADC" —
each ADC word is an instantaneous sample, not a charge integral, which is why
seven of them are kept: the shape across samples is what carries the energy
and timing information. Samples that fall past the end of the stored waveform
are left at zero.

**TOA — time of arrival.** A discriminator fires on the first upward crossing
of `toa_thres`. Because the sampled grid is coarse compared to the timing
resolution wanted, the crossing time is linearly interpolated between the two
straddling samples
([`.cc#L132-L138`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CALOROCDigitization.cc#L132-L138)).
The value stored is *not* the absolute time but the interval from the
crossing to the clock edge of the sample it is attached to
([`.cc#L72-L79`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CALOROCDigitization.cc#L72-L79)):

```
TOA = adc_phase + (time_stamp + idx_toa) × time_window − t_upcross
```

so a *larger* TOA count means an *earlier* arrival within the bunch crossing —
the usual TDC-counting-back-from-the-clock-edge convention. This is where the
sub-nanosecond timing of the calorimeter comes from.

**TOT — time over threshold.** When the waveform falls back below
`tot_thres`, the width above threshold is recorded on the same sample as the
TOA
([`.cc#L81-L88`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CALOROCDigitization.cc#L81-L88)).
TOT exists because the ADC saturates: for a large signal every sample is
clipped at full scale and the amplitude carries no information, but the pulse
stays above threshold for longer the larger it is, so the width recovers the
energy. TOT extends the dynamic range at the top end, ADC covers the bottom
end, and the two overlap in the middle.

**Gain ranges.** Two CALOROC variants are modelled and both are written out
for every hit
([`.cc#L97-L128`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CALOROCDigitization.cc#L97-L128)):

- **CALOROC 1A** (`ASamples`, of type `edm4eic::CALOROC1ASample`) — a
  *single* gain range, `dyRangeSingleGainADC`, plus TOA and TOT. Large
  signals saturate the ADC and are recovered from the TOT.
- **CALOROC 1B** (`BSamples`, of type `edm4eic::CALOROC1BSample`) — *dual*
  gain: the
  same amplitude is digitized twice, once against `dyRangeHighGainADC` for
  small signals (fine least count, saturates early) and once against
  `dyRangeLowGainADC` for large ones (coarse least count, wide range), plus
  TOA. There is no TOT field on the 1B sample; the low-gain range plays that
  role instead.

Every word is `round(value / dyRange × cap)` clamped into `[0, cap − 1]`, so
saturation is explicit. The BEMC configures `dyRangeHighGainADC` equal to
`dyRangeSingleGainADC` (250) and `dyRangeLowGainADC` ten times larger (2500),
i.e. a factor-10 gain ratio between the two 1B ranges.

### Configuration

| field | struct default | meaning |
|---|---|---|
| `n_samples` | `7` | number of ADC samples taken per pulse |
| `time_window` | `25 ns` (`25 * edm4eic::unit::ns`) | interval between ADC samples — the bunch-crossing clock period |
| `adc_phase` | `0 ns` | phase of the sampling clock relative to t = 0; also written to the hit as `samplePhase` in TOA counts |
| `toa_thres` | `1` | amplitude threshold for the time-of-arrival discriminator, in pulse-amplitude units |
| `tot_thres` | `1` | amplitude threshold whose down-crossing ends the time-over-threshold measurement |
| `capADC` | `1024` | ADC full scale in counts (10-bit) |
| `dyRangeSingleGainADC` | `1` | amplitude at ADC full scale for the single-gain (1A) chip |
| `dyRangeHighGainADC` | `1` | amplitude at full scale for the 1B high-gain range |
| `dyRangeLowGainADC` | `1` | amplitude at full scale for the 1B low-gain range |
| `capTOA` | `1024` | TOA full scale in counts |
| `dyRangeTOA` | `25 ns` | time at TOA full scale — least count 25 ns / 1024 ≈ 24 ps |
| `capTOT` | `4096` | TOT full scale in counts |
| `dyRangeTOT` | `200 ns` (`200 * edm4eic::unit::ns`) | time at TOT full scale |

Defaults from
[`CALOROCDigitizationConfig.h#L10-L30`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CALOROCDigitizationConfig.h#L10-L30).
The dynamic-range defaults of `1` are placeholders — every real instance must
set them. Flags mirror the field names in camel case (`timeWindow`,
`adcPhase`, `toaThres`, `totThres`, `capADC`, `dyRange*`, `capTOA`, `capTOT`),
except that **`n_samples` is not exposed**
([`CALOROCDigitization_factory.h#L24-L37`](https://github.com/eic/EICrecon/blob/main/src/factories/digi/CALOROCDigitization_factory.h#L24-L37)).

### Which detectors use it

Only the barrel ECal ScFi section, twice:

| instance | input | output | settings |
|---|---|---|---|
| `EcalBarrelScFiPCALOROCHits` ([`BEMC.cc#L211-L223`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L211-L223)) | `EcalBarrelScFiPCombinedPulsesWithNoise` | `EcalBarrelScFiPCALOROCHits` | `adc_phase=10 ns`, `toa_thres=7`, `tot_thres=200`, `dyRangeSingleGainADC=250`, `dyRangeHighGainADC=250`, `dyRangeLowGainADC=2500` |
| `EcalBarrelScFiNCALOROCHits` ([`BEMC.cc#L224-L236`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L224-L236)) | `EcalBarrelScFiNCombinedPulses` **(no noise)** | `EcalBarrelScFiNCALOROCHits` | identical config |

Both output collections are persisted by default
([`JEventProcessorPODIO.cc#L381-L382`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L381-L382)).
The values `n_samples=7`, `time_window=25 ns`, `capADC=1024`, `capTOA=1024`,
`capTOT=4096` are left at their struct defaults.

---

## Sibling ROC digitizers

The tracker and TOF equivalents of the last stage are:

- [`EICROCDigitization`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/EICROCDigitization.cc)
  ([config](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/EICROCDigitizationConfig.h)) —
  *"Convert ADC pulses from EICROCGeneration into ADC and TDC values"*;
  8-bit ADC, 10-bit TDC, `t_thres` in ADC units, `tMax = 25 ns` (the 40 MHz
  EIC clock). Used by ECTOF as `TOFEndcapADCTDC`
  ([`ECTOF.cc#L111-L112`](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L111-L112)).
- [`CFDROCDigitization`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CFDROCDigitization.cc)
  ([config](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CFDROCDigitizationConfig.h)) —
  *"Discriminate and digitize signals with timing based on what is expected
  from a CFD"*; same word widths but a ten-times-wider ADC range and a
  constant-fraction `fraction = 0.5` instead of a fixed threshold. Used by
  BTOF as `CFDROCDigitization`
  ([`BTOF.cc#L127-L128`](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L127-L128)).

Both differ from `CALOROCDigitization` in their input as well as their
output: they consume `edm4hep::RawTimeSeries` produced by
[`SiliconPulseDiscretization`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/SiliconPulseDiscretization.cc)
— an extra stage that re-samples the combined `SimPulse` onto the sensor's
own clock — and emit `edm4eic::RawTrackerHit` rather than
`edm4eic::RawCALOROCHit`. So the tracker chain is
`PulseGeneration → PulseCombiner → SiliconPulseDiscretization → {EICROC,
CFDROC}Digitization`, and unlike the calorimeter chain it is fully connected:
`TOFBarrelADCTDC` feeds `LGADHitCalibration`
([`LGADHitCalibration.h#L29`](https://github.com/eic/EICrecon/blob/main/src/algorithms/reco/LGADHitCalibration.h#L29)).

---

## Caveats / needs human verification

1. **The BEMC CALOROC branch is a dead end.** Nothing consumes
   `EcalBarrelScFi{P,N}CALOROCHits`; the rec hits that feed clustering come
   from the simple `CalorimeterHitDigi` path applied to the *unprocessed*
   sim hits. There is no `RawCALOROCHit` → `CalorimeterHit` reconstruction
   algorithm in the tree at this commit. The chain is validated output, not
   yet a reconstruction path.
2. **The −z BEMC digitizer skips the noise stage.** `…PCALOROCHits` reads
   `…PCombinedPulsesWithNoise` while `…NCALOROCHits` reads
   `…NCombinedPulses`
   ([`BEMC.cc#L211-L236`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L211-L236)),
   even though `…NCombinedPulsesWithNoise` is produced. Looks unintentional;
   needs a maintainer's confirmation.
3. **The LOWQ2 noisy pulses are also unconsumed.**
   `TaggerTrackerCombinedPulsesWithNoise` is persisted
   ([`JEventProcessorPODIO.cc#L176-L178`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L176-L178))
   but the tagger's raw hits come from `SiliconTrackerDigi` running on the
   sim hits directly.
4. **The noise model itself lives in DD4hep, not EICrecon.**
   `dd4hep::detail::FalphaNoise` is included from
   `DDDigi/noise/FalphaNoise.h`; the meaning of `poles`, `alpha` and
   `variance` given above is the standard `1/f^α` multi-pole synthesis and is
   consistent with the field comments, but the exact recursion, the pole
   spacing, and whether `variance` is the pre- or post-shaping variance can
   only be confirmed in the DD4hep source.
5. **Amplitude units are undefined and inconsistent across detectors.**
   `ignore_thres`, `toa_thres`, `tot_thres`, `scale` and the `dyRange*`
   values are all in "whatever the pulse shape function returns". For the
   TOFs that is ADC counts by construction of the gain; for the BEMC it is
   photoelectrons times a gain of 55.37. Comparing thresholds between
   detectors is meaningless.
6. **Two config fields cannot be set at runtime**: `PulseNoise::pedestal` and
   `CALOROCDigitization::n_samples` have no `ParameterRef` in their
   factories, so they can only be changed in C++.
7. **The `minimumSeperation` flag is misspelled** in
   [`PulseCombiner_factory.h#L24`](https://github.com/eic/EICrecon/blob/main/src/factories/digi/PulseCombiner_factory.h#L24).
   Scripts must use the misspelling.
8. **`PulseCombiner::init` throws if `readout` is empty but `combine_field`
   is set** — the guard tests `!(readout.empty() && combine_field.empty())`
   ([`.cc#L33`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/PulseCombiner.cc#L33)),
   so a half-filled configuration reaches the DD4hep lookup and fails there.
9. **A TOA crossing before the first ADC sample is attributed to sample 0.**
   `idx_sample` is only advanced once `i > idx_amp_first`
   ([`.cc#L66-L67`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CALOROCDigitization.cc#L66-L67)),
   so an early crossing lands on the first sample by default. Whether that
   matches the chip's behaviour is not stated.
10. **`get_crossing_time`'s parameter names are misleading.** It is called
    with `(amplitude[i], amplitude[i-1])` bound to `(amp1, amp2)`
    ([`.cc#L74-L75`](https://github.com/eic/EICrecon/blob/main/src/algorithms/digi/CALOROCDigitization.cc#L74-L75)),
    i.e. current then previous. The arithmetic works out to the correct
    linear back-interpolation from `t`, but the naming invites the opposite
    reading, and there is no guard against two equal consecutive samples
    (division by zero).
11. **The pulse-shape registry has one entry.** Anything other than
    `"LandauPulse"` is silently reinterpreted as an EvaluatorSvc expression,
    so a typo in the shape name surfaces as an "Unable to make pulse shape
    type" exception rather than an unknown-name error.
12. **No BEMC provenance.** `pulse_shape_params={55.37, 10 ns}`,
    `toa_thres=7`, `tot_thres=200`, and the 250/2500 dynamic ranges are
    hard-coded with no comment recording which CALOROC prototype
    measurement or SiPM working point they come from.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
(fetched 2026-08-19). AI-authored draft — verify against source.*
