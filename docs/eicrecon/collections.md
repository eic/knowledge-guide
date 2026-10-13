---
title: Collection index
parent: EICrecon
nav_order: 40
source: eic/EICrecon
source_commit: 3319124d3982ce95c797987c8b663a531030528d
generated: 2026-08-19
status: draft
---

# EICrecon collection index

{: .warning }
AI-generated draft derived from EICrecon source at commit
[`3319124`](https://github.com/eic/EICrecon/commit/3319124d3982ce95c797987c8b663a531030528d).
Every claim links to the exact file — verify there before depending on it.

{: .note }
This page is **auto-generated**. It was produced by parsing every
`JOmniFactoryGeneratorT<...>` registration in `src/detectors/*/*.cc` and
`src/global/*/*.cc` at commit `3319124`, and joining the result against the
hard-coded default output list in
[`JEventProcessorPODIO.cc`](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L52-L523).
It is a snapshot and **will drift** as EICrecon changes — collections are
added, renamed and re-tagged frequently. Treat it as a lookup aid, not as
an authority; the source is the authority.

## How to read this

A **plugin** is a JANA2 shared library. Each one lives in a single file —
`src/detectors/<NAME>/<NAME>.cc` for a subdetector, `src/global/<name>/<name>.cc`
for a detector-spanning stage — whose `InitPlugin` registers all of that
plugin's factories.

A **factory** is a lazily-evaluated producer of one or more PODIO collections.
Registrations look like

```cpp
app->Add(new JOmniFactoryGeneratorT<CalorimeterHitDigi_factory>(
    "EcalBarrelScFiRawHits",                      // instance (JANA tag)
    {"EventHeader", "EcalBarrelScFiHits"},        // input collection tags
    {"EcalBarrelScFiRawHits", "EcalBarrelScFiRawHitLinks",
     "EcalBarrelScFiRawHitAssociations"},         // output collection tags
    { /* config */ }, app));
```

The **instance name** is the JANA tag; it is what runtime flags are keyed on
(`BEMC:EcalBarrelScFiRawHits:capacityADC`, …). The **output tags** are the
collection names indexed below. One instance usually emits several
collections at once — a data collection plus its `…Links` and
`…Associations` MC-truth relations — which is why many rows share a producer.
Nothing is computed unless something downstream asks for it, so a collection
existing in this table does not mean it is computed in every run.

**"persisted by default = yes"** means the collection name appears in the
`output_collections` vector hard-coded in the `JEventProcessorPODIO`
constructor
([L52-L523](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L52-L523)).
Those collections land in the podio output ROOT file (`podio_output.root` by
default) with no extra flags — provided the collection is actually produced
in that run. Everything marked `no` is transient: computed if something needs
it, then dropped.

**Forcing a transient collection into the output.** The parameter is
`podio:output_collections`
([L525-L529](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L525-L529)),
with a companion `podio:output_exclude_collections`. Setting it **replaces**
the default list rather than appending to it. Each entry is compiled to a
`std::regex` and matched with `std::regex_match` against the collections
actually present in the first event
([L586-L600](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L586-L600)),
so the practical recipes are:

```bash
# write absolutely everything the event has
eicrecon -Ppodio:output_collections='.*' -Ppodio:output_file=out.root in.edm4hep.root

# write everything except a few
eicrecon -Ppodio:output_exclude_collections=MCParticles,CentralCKFTrajectories ...

# write a targeted subset (regexes, not globs)
eicrecon -Ppodio:output_collections='EcalBarrel.*,MCParticles' ...
```

Because the entries are regexes and not globs, `EcalBarrel*` does **not** mean
"names starting with EcalBarrel" — write `EcalBarrel.*`. A name in the include
list that no factory produces is silently skipped with a `warn`-level message.

## Totals

**679 collections indexed, 411 of them persisted by default**, produced by
**327 factory registrations** across 28 plugin files (22 detector plugins,
6 global plugins). 22 of the 411 persisted names have no producer in those
files (see [Caveats](#caveats)).

## EcalBarrel* — barrel ECal (BEMC)

64 collections, 36 persisted by default.

| collection | producing factory (instance) | plugin | persisted |
|---|---|---|---|
| `EcalBarrelCalorimeterTrackProjections` | `SubDivideCollection_factory<TrackSegment>` (`EndcapPBarrelEndcapNCalorimeterTrackProjections`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L106) | no |
| `EcalBarrelClusterAssociations` | `CalorimeterClusterShape_factory` (`EcalBarrelClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L463) | yes |
| `EcalBarrelClusterAssociationsWithoutShapes` | `EnergyPositionClusterMerger_factory` (`EcalBarrelClustersWithoutShapes`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L450) | no |
| `EcalBarrelClusterLinks` | `CalorimeterClusterShape_factory` (`EcalBarrelClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L463) | yes |
| `EcalBarrelClusterLinksWithoutShapes` | `EnergyPositionClusterMerger_factory` (`EcalBarrelClustersWithoutShapes`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L450) | no |
| `EcalBarrelClusters` | `CalorimeterClusterShape_factory` (`EcalBarrelClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L463) | yes |
| `EcalBarrelClustersWithoutShapes` | `EnergyPositionClusterMerger_factory` (`EcalBarrelClustersWithoutShapes`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L450) | no |
| `EcalBarrelExpectedClusters` | `TrackClusterSubtractor_factory` (`EcalBarrelRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L138) | yes |
| `EcalBarrelImagingClusterAssociations` | `CalorimeterClusterShape_factory` (`EcalBarrelImagingClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L442) | yes |
| `EcalBarrelImagingClusterAssociationsWithoutShapes` | `ImagingClusterReco_factory` (`EcalBarrelImagingClustersWithoutShapes`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L431) | no |
| `EcalBarrelImagingClusterLinks` | `CalorimeterClusterShape_factory` (`EcalBarrelImagingClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L442) | yes |
| `EcalBarrelImagingClusterLinksWithoutShapes` | `ImagingClusterReco_factory` (`EcalBarrelImagingClustersWithoutShapes`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L431) | no |
| `EcalBarrelImagingClusters` | `CalorimeterClusterShape_factory` (`EcalBarrelImagingClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L442) | yes |
| `EcalBarrelImagingClustersWithoutShapes` | `ImagingClusterReco_factory` (`EcalBarrelImagingClustersWithoutShapes`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L431) | no |
| `EcalBarrelImagingLayers` | `ImagingClusterReco_factory` (`EcalBarrelImagingClustersWithoutShapes`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L431) | no |
| `EcalBarrelImagingProcessedHitContributions` | `SimCalorimeterHitProcessor_factory` (`EcalBarrelImagingProcessedHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L370) | yes |
| `EcalBarrelImagingProcessedHits` | `SimCalorimeterHitProcessor_factory` (`EcalBarrelImagingProcessedHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L370) | yes |
| `EcalBarrelImagingProtoClusters` | `ImagingTopoCluster_factory` (`EcalBarrelImagingProtoClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L413) | no |
| `EcalBarrelImagingRawHitAssociations` | `CalorimeterHitDigi_factory` (`EcalBarrelImagingRawHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L379) | yes |
| `EcalBarrelImagingRawHitLinks` | `CalorimeterHitDigi_factory` (`EcalBarrelImagingRawHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L379) | yes |
| `EcalBarrelImagingRawHits` | `CalorimeterHitDigi_factory` (`EcalBarrelImagingRawHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L379) | yes |
| `EcalBarrelImagingRecHits` | `CalorimeterHitReco_factory` (`EcalBarrelImagingRecHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L396) | yes |
| `EcalBarrelRemnantClusters` | `TrackClusterSubtractor_factory` (`EcalBarrelRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L138) | yes |
| `EcalBarrelScFiClusterAssociations` | `CalorimeterClusterShape_factory` (`EcalBarrelScFiClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L312) | yes |
| `EcalBarrelScFiClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalBarrelScFiClustersWithoutShapes`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L299) | no |
| `EcalBarrelScFiClusterLinks` | `CalorimeterClusterShape_factory` (`EcalBarrelScFiClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L312) | yes |
| `EcalBarrelScFiClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalBarrelScFiClustersWithoutShapes`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L299) | no |
| `EcalBarrelScFiClusters` | `CalorimeterClusterShape_factory` (`EcalBarrelScFiClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L312) | yes |
| `EcalBarrelScFiClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalBarrelScFiClustersWithoutShapes`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L299) | no |
| `EcalBarrelScFiNAttenuatedHitContributions` | `SimCalorimeterHitProcessor_factory` (`EcalBarrelScFiNAttenuatedHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L114) | yes |
| `EcalBarrelScFiNAttenuatedHits` | `SimCalorimeterHitProcessor_factory` (`EcalBarrelScFiNAttenuatedHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L114) | yes |
| `EcalBarrelScFiNCALOROCHits` | `CALOROCDigitization_factory` (`EcalBarrelScFiNCALOROCHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L224) | yes |
| `EcalBarrelScFiNCombinedPulses` | `PulseCombiner_factory` (`EcalBarrelScFiNCombinedPulses`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L178) | no |
| `EcalBarrelScFiNCombinedPulsesWithNoise` | `PulseNoise_factory` (`EcalBarrelScFiNCombinedPulsesWithNoise`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L199) | no |
| `EcalBarrelScFiNNpeHits` | `EdepToNpeConversion_factory` (`EcalBarrelScFiNNpeHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L139) | yes |
| `EcalBarrelScFiNPulses` | `PulseGeneration_factory<SimCalorimeterHit>` (`EcalBarrelScFiNPulses`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L159) | no |
| `EcalBarrelScFiPAttenuatedHitContributions` | `SimCalorimeterHitProcessor_factory` (`EcalBarrelScFiPAttenuatedHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L99) | yes |
| `EcalBarrelScFiPAttenuatedHits` | `SimCalorimeterHitProcessor_factory` (`EcalBarrelScFiPAttenuatedHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L99) | yes |
| `EcalBarrelScFiPCALOROCHits` | `CALOROCDigitization_factory` (`EcalBarrelScFiPCALOROCHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L211) | yes |
| `EcalBarrelScFiPCombinedPulses` | `PulseCombiner_factory` (`EcalBarrelScFiPCombinedPulses`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L169) | no |
| `EcalBarrelScFiPCombinedPulsesWithNoise` | `PulseNoise_factory` (`EcalBarrelScFiPCombinedPulsesWithNoise`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L187) | no |
| `EcalBarrelScFiPNpeHits` | `EdepToNpeConversion_factory` (`EcalBarrelScFiPNpeHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L129) | yes |
| `EcalBarrelScFiPPulses` | `PulseGeneration_factory<SimCalorimeterHit>` (`EcalBarrelScFiPPulses`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L149) | no |
| `EcalBarrelScFiProtoClusters` | `CalorimeterIslandCluster_factory` (`EcalBarrelScFiProtoClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L277) | no |
| `EcalBarrelScFiProtoTopoClusters` | `ImagingTopoCluster_factory` (`EcalBarrelScFiProtoTopoClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L319) | no |
| `EcalBarrelScFiRawHitAssociations` | `CalorimeterHitDigi_factory` (`EcalBarrelScFiRawHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L237) | no |
| `EcalBarrelScFiRawHitLinks` | `CalorimeterHitDigi_factory` (`EcalBarrelScFiRawHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L237) | no |
| `EcalBarrelScFiRawHits` | `CalorimeterHitDigi_factory` (`EcalBarrelScFiRawHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L237) | yes |
| `EcalBarrelScFiRecHits` | `CalorimeterHitReco_factory` (`EcalBarrelScFiRecHits`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L255) | yes |
| `EcalBarrelScFiTopoClusterAssociations` | `CalorimeterClusterShape_factory` (`EcalBarrelScFiTopoClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L350) | yes |
| `EcalBarrelScFiTopoClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalBarrelScFiTopoClustersWithoutShapes`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L339) | no |
| `EcalBarrelScFiTopoClusterLinks` | `CalorimeterClusterShape_factory` (`EcalBarrelScFiTopoClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L350) | yes |
| `EcalBarrelScFiTopoClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalBarrelScFiTopoClustersWithoutShapes`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L339) | no |
| `EcalBarrelScFiTopoClusters` | `CalorimeterClusterShape_factory` (`EcalBarrelScFiTopoClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L350) | yes |
| `EcalBarrelScFiTopoClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalBarrelScFiTopoClustersWithoutShapes`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L339) | no |
| `EcalBarrelTrackClusterMatches` | `TrackClusterMatch_factory` (`EcalBarrelTrackClusterMatches`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L220) | yes |
| `EcalBarrelTrackExpectedClusterLinks` | `TrackClusterSubtractor_factory` (`EcalBarrelRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L138) | yes |
| `EcalBarrelTrackExpectedClusterMatches` | `TrackClusterSubtractor_factory` (`EcalBarrelRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L138) | yes |
| `EcalBarrelTruthClusterAssociations` | `CalorimeterClusterShape_factory` (`EcalBarrelTruthClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L476) | yes |
| `EcalBarrelTruthClusterAssociationsWithoutShapes` | `TruthEnergyPositionClusterMerger_factory` (`EcalBarrelTruthClustersWithoutShapes`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L468) | no |
| `EcalBarrelTruthClusterLinks` | `CalorimeterClusterShape_factory` (`EcalBarrelTruthClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L476) | yes |
| `EcalBarrelTruthClusterLinksWithoutShapes` | `TruthEnergyPositionClusterMerger_factory` (`EcalBarrelTruthClustersWithoutShapes`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L468) | no |
| `EcalBarrelTruthClusters` | `CalorimeterClusterShape_factory` (`EcalBarrelTruthClusters`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L476) | yes |
| `EcalBarrelTruthClustersWithoutShapes` | `TruthEnergyPositionClusterMerger_factory` (`EcalBarrelTruthClustersWithoutShapes`) | [BEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc#L468) | no |

## EcalEndcapN* — backward ECal (EEMC)

41 collections, 17 persisted by default.

| collection | producing factory (instance) | plugin | persisted |
|---|---|---|---|
| `EcalEndcapNCalorimeterTrackProjections` | `SubDivideCollection_factory<TrackSegment>` (`EndcapPBarrelEndcapNCalorimeterTrackProjections`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L106) | no |
| `EcalEndcapNClusterAssociations` | `CalorimeterParticleIDPostML_factory` (`EcalEndcapNParticleIDPostML`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L178) | yes |
| `EcalEndcapNClusterAssociationsWithoutPID` | `CalorimeterClusterShape_factory` (`EcalEndcapNClustersWithoutPID`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L146) | no |
| `EcalEndcapNClusterAssociationsWithoutPIDAndShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapNClustersWithoutPIDAndShapes`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L127) | no |
| `EcalEndcapNClusterLinks` | `CalorimeterParticleIDPostML_factory` (`EcalEndcapNParticleIDPostML`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L178) | yes |
| `EcalEndcapNClusterLinksWithoutPID` | `CalorimeterClusterShape_factory` (`EcalEndcapNClustersWithoutPID`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L146) | no |
| `EcalEndcapNClusterLinksWithoutPIDAndShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapNClustersWithoutPIDAndShapes`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L127) | no |
| `EcalEndcapNClusterParticleIDs` | `CalorimeterParticleIDPostML_factory` (`EcalEndcapNParticleIDPostML`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L178) | no |
| `EcalEndcapNClusters` | `CalorimeterParticleIDPostML_factory` (`EcalEndcapNParticleIDPostML`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L178) | yes |
| `EcalEndcapNClustersWithoutPID` | `CalorimeterClusterShape_factory` (`EcalEndcapNClustersWithoutPID`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L146) | no |
| `EcalEndcapNClustersWithoutPIDAndShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapNClustersWithoutPIDAndShapes`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L127) | no |
| `EcalEndcapNExpectedClusters` | `TrackClusterSubtractor_factory` (`EcalEndcapNRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L116) | yes |
| `EcalEndcapNIslandProtoClusters` | `CalorimeterIslandCluster_factory` (`EcalEndcapNIslandProtoClusters`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L84) | no |
| `EcalEndcapNParticleIDInput_features` | `CalorimeterParticleIDPreML_factory` (`EcalEndcapNParticleIDPreML`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L154) | no |
| `EcalEndcapNParticleIDOutput_label` | `ONNXInference_factory` (`EcalEndcapNParticleIDInference`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L165) | no |
| `EcalEndcapNParticleIDOutput_probability_tensor` | `ONNXInference_factory` (`EcalEndcapNParticleIDInference`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L165) | no |
| `EcalEndcapNParticleIDTarget` | `CalorimeterParticleIDPreML_factory` (`EcalEndcapNParticleIDPreML`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L154) | no |
| `EcalEndcapNRawHitAssociations` | `CalorimeterHitDigi_factory` (`EcalEndcapNRawHits`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L39) | no |
| `EcalEndcapNRawHitLinks` | `CalorimeterHitDigi_factory` (`EcalEndcapNRawHits`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L39) | no |
| `EcalEndcapNRawHits` | `CalorimeterHitDigi_factory` (`EcalEndcapNRawHits`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L39) | yes |
| `EcalEndcapNRecHits` | `CalorimeterHitReco_factory` (`EcalEndcapNRecHits`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L64) | yes |
| `EcalEndcapNRemnantClusters` | `TrackClusterSubtractor_factory` (`EcalEndcapNRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L116) | yes |
| `EcalEndcapNSplitMergeClusterAssociations` | `CalorimeterClusterShape_factory` (`EcalEndcapNSplitMergeClusters`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L223) | yes |
| `EcalEndcapNSplitMergeClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapNSplitMergeClustersWithoutShapes`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L207) | no |
| `EcalEndcapNSplitMergeClusterLinks` | `CalorimeterClusterShape_factory` (`EcalEndcapNSplitMergeClusters`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L223) | yes |
| `EcalEndcapNSplitMergeClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapNSplitMergeClustersWithoutShapes`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L207) | no |
| `EcalEndcapNSplitMergeClusters` | `CalorimeterClusterShape_factory` (`EcalEndcapNSplitMergeClusters`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L223) | yes |
| `EcalEndcapNSplitMergeClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapNSplitMergeClustersWithoutShapes`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L207) | no |
| `EcalEndcapNSplitMergeProtoClusters` | `TrackClusterMergeSplitter_factory` (`EcalEndcapNSplitMergeProtoClusters`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L194) | no |
| `EcalEndcapNTrackClusterMatches` | `TrackClusterMatch_factory` (`EcalEndcapNTrackClusterMatches`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L229) | yes |
| `EcalEndcapNTrackExpectedClusterLinks` | `TrackClusterSubtractor_factory` (`EcalEndcapNRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L116) | yes |
| `EcalEndcapNTrackExpectedClusterMatches` | `TrackClusterSubtractor_factory` (`EcalEndcapNRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L116) | yes |
| `EcalEndcapNTrackSplitMergeClusterMatches` | `TrackProtoClusterMatchPromoter_factory` (`EcalEndcapNTrackSplitMergeClusterMatches`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L43) | yes |
| `EcalEndcapNTrackSplitMergeProtoClusterLinks` | `TrackClusterMergeSplitter_factory` (`EcalEndcapNSplitMergeProtoClusters`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L194) | no |
| `EcalEndcapNTruthClusterAssociations` | `CalorimeterClusterShape_factory` (`EcalEndcapNTruthClusters`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L120) | yes |
| `EcalEndcapNTruthClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapNTruthClustersWithoutShapes`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L107) | no |
| `EcalEndcapNTruthClusterLinks` | `CalorimeterClusterShape_factory` (`EcalEndcapNTruthClusters`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L120) | yes |
| `EcalEndcapNTruthClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapNTruthClustersWithoutShapes`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L107) | no |
| `EcalEndcapNTruthClusters` | `CalorimeterClusterShape_factory` (`EcalEndcapNTruthClusters`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L120) | yes |
| `EcalEndcapNTruthClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapNTruthClustersWithoutShapes`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L107) | no |
| `EcalEndcapNTruthProtoClusters` | `CalorimeterTruthClustering_factory` (`EcalEndcapNTruthProtoClusters`) | [EEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc#L79) | no |

## EcalEndcapP* — forward ECal (FEMC)

33 collections, 17 persisted by default.

| collection | producing factory (instance) | plugin | persisted |
|---|---|---|---|
| `EcalEndcapPCalorimeterTrackProjections` | `SubDivideCollection_factory<TrackSegment>` (`EndcapPBarrelEndcapNCalorimeterTrackProjections`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L106) | no |
| `EcalEndcapPClusterAssociations` | `CalorimeterClusterShape_factory` (`EcalEndcapPClusters`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L203) | yes |
| `EcalEndcapPClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapPClustersWithoutShapes`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L185) | no |
| `EcalEndcapPClusterLinks` | `CalorimeterClusterShape_factory` (`EcalEndcapPClusters`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L203) | yes |
| `EcalEndcapPClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapPClustersWithoutShapes`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L185) | no |
| `EcalEndcapPClusters` | `CalorimeterClusterShape_factory` (`EcalEndcapPClusters`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L203) | yes |
| `EcalEndcapPClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapPClustersWithoutShapes`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L185) | no |
| `EcalEndcapPExpectedClusters` | `TrackClusterSubtractor_factory` (`EcalEndcapPRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L160) | yes |
| `EcalEndcapPIslandProtoClusters` | `CalorimeterIslandCluster_factory` (`EcalEndcapPIslandProtoClusters`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L144) | no |
| `EcalEndcapPRawHitAssociations` | `CalorimeterHitDigi_factory` (`EcalEndcapPRawHits`) **or** `CalorimeterHitDigi_factory` (`EcalEndcapPRawHits`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L70) / [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L95) | no |
| `EcalEndcapPRawHitLinks` | `CalorimeterHitDigi_factory` (`EcalEndcapPRawHits`) **or** `CalorimeterHitDigi_factory` (`EcalEndcapPRawHits`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L70) / [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L95) | no |
| `EcalEndcapPRawHits` | `CalorimeterHitDigi_factory` (`EcalEndcapPRawHits`) **or** `CalorimeterHitDigi_factory` (`EcalEndcapPRawHits`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L70) / [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L95) | yes |
| `EcalEndcapPRecHits` | `CalorimeterHitReco_factory` (`EcalEndcapPRecHits`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L122) | yes |
| `EcalEndcapPRemnantClusters` | `TrackClusterSubtractor_factory` (`EcalEndcapPRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L160) | yes |
| `EcalEndcapPSplitMergeClusterAssociations` | `CalorimeterClusterShape_factory` (`EcalEndcapPSplitMergeClusters`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L241) | yes |
| `EcalEndcapPSplitMergeClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapPSplitMergeClustersWithoutShapes`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L222) | no |
| `EcalEndcapPSplitMergeClusterLinks` | `CalorimeterClusterShape_factory` (`EcalEndcapPSplitMergeClusters`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L241) | yes |
| `EcalEndcapPSplitMergeClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapPSplitMergeClustersWithoutShapes`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L222) | no |
| `EcalEndcapPSplitMergeClusters` | `CalorimeterClusterShape_factory` (`EcalEndcapPSplitMergeClusters`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L241) | yes |
| `EcalEndcapPSplitMergeClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapPSplitMergeClustersWithoutShapes`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L222) | no |
| `EcalEndcapPSplitMergeProtoClusters` | `TrackClusterMergeSplitter_factory` (`EcalEndcapPSplitMergeProtoClusters`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L209) | no |
| `EcalEndcapPTrackClusterMatches` | `TrackClusterMatch_factory` (`EcalEndcapPTrackClusterMatches`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L206) | yes |
| `EcalEndcapPTrackExpectedClusterLinks` | `TrackClusterSubtractor_factory` (`EcalEndcapPRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L160) | yes |
| `EcalEndcapPTrackExpectedClusterMatches` | `TrackClusterSubtractor_factory` (`EcalEndcapPRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L160) | yes |
| `EcalEndcapPTrackSplitMergeClusterMatches` | `TrackProtoClusterMatchPromoter_factory` (`EcalEndcapPTrackSplitMergeClusterMatches`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L65) | yes |
| `EcalEndcapPTrackSplitMergeProtoClusterLinks` | `TrackClusterMergeSplitter_factory` (`EcalEndcapPSplitMergeProtoClusters`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L209) | no |
| `EcalEndcapPTruthClusterAssociations` | `CalorimeterClusterShape_factory` (`EcalEndcapPTruthClusters`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L178) | yes |
| `EcalEndcapPTruthClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapPTruthClustersWithoutShapes`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L165) | no |
| `EcalEndcapPTruthClusterLinks` | `CalorimeterClusterShape_factory` (`EcalEndcapPTruthClusters`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L178) | yes |
| `EcalEndcapPTruthClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapPTruthClustersWithoutShapes`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L165) | no |
| `EcalEndcapPTruthClusters` | `CalorimeterClusterShape_factory` (`EcalEndcapPTruthClusters`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L178) | yes |
| `EcalEndcapPTruthClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalEndcapPTruthClustersWithoutShapes`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L165) | no |
| `EcalEndcapPTruthProtoClusters` | `CalorimeterTruthClustering_factory` (`EcalEndcapPTruthProtoClusters`) | [FEMC](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L139) | no |

## HcalBarrel* — barrel HCal (BHCAL)

34 collections, 18 persisted by default.

| collection | producing factory (instance) | plugin | persisted |
|---|---|---|---|
| `HcalBarrelCalorimeterTrackProjections` | `SubDivideCollection_factory<TrackSegment>` (`EndcapPBarrelEndcapNCalorimeterTrackProjections`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L106) | no |
| `HcalBarrelClusterAssociations` | `CalorimeterClusterShape_factory` (`HcalBarrelClusters`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L138) | yes |
| `HcalBarrelClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalBarrelClustersWithoutShapes`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L125) | no |
| `HcalBarrelClusterLinks` | `CalorimeterClusterShape_factory` (`HcalBarrelClusters`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L138) | yes |
| `HcalBarrelClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalBarrelClustersWithoutShapes`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L125) | no |
| `HcalBarrelClusters` | `CalorimeterClusterShape_factory` (`HcalBarrelClusters`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L138) | yes |
| `HcalBarrelClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalBarrelClustersWithoutShapes`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L125) | no |
| `HcalBarrelExpectedClusters` | `TrackClusterSubtractor_factory` (`HcalBarrelRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L148) | yes |
| `HcalBarrelIslandProtoClusters` | `CalorimeterIslandCluster_factory` (`HcalBarrelIslandProtoClusters`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L104) | no |
| `HcalBarrelMergedHits` | `CalorimeterHitsMerger_factory` (`HcalBarrelMergedHits`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L92) | yes |
| `HcalBarrelRawHitAssociations` | `CalorimeterHitDigi_factory` (`HcalBarrelRawHits`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L51) | no |
| `HcalBarrelRawHitLinks` | `CalorimeterHitDigi_factory` (`HcalBarrelRawHits`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L51) | no |
| `HcalBarrelRawHits` | `CalorimeterHitDigi_factory` (`HcalBarrelRawHits`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L51) | yes |
| `HcalBarrelRecHits` | `CalorimeterHitReco_factory` (`HcalBarrelRecHits`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L70) | yes |
| `HcalBarrelRemnantClusters` | `TrackClusterSubtractor_factory` (`HcalBarrelRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L148) | yes |
| `HcalBarrelSplitMergeClusterAssociations` | `CalorimeterClusterShape_factory` (`HcalBarrelSplitMergeClusters`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L191) | yes |
| `HcalBarrelSplitMergeClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalBarrelSplitMergeClustersWithoutShapes`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L178) | no |
| `HcalBarrelSplitMergeClusterLinks` | `CalorimeterClusterShape_factory` (`HcalBarrelSplitMergeClusters`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L191) | yes |
| `HcalBarrelSplitMergeClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalBarrelSplitMergeClustersWithoutShapes`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L178) | no |
| `HcalBarrelSplitMergeClusters` | `CalorimeterClusterShape_factory` (`HcalBarrelSplitMergeClusters`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L191) | yes |
| `HcalBarrelSplitMergeClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalBarrelSplitMergeClustersWithoutShapes`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L178) | no |
| `HcalBarrelSplitMergeProtoClusters` | `TrackClusterMergeSplitter_factory` (`HcalBarrelSplitMergeProtoClusters`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L164) | no |
| `HcalBarrelTrackClusterMatches` | `TrackClusterMatch_factory` (`HcalBarrelTrackClusterMatches`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L224) | yes |
| `HcalBarrelTrackExpectedClusterLinks` | `TrackClusterSubtractor_factory` (`HcalBarrelRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L148) | yes |
| `HcalBarrelTrackExpectedClusterMatches` | `TrackClusterSubtractor_factory` (`HcalBarrelRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L148) | yes |
| `HcalBarrelTrackSplitMergeClusterMatches` | `TrackProtoClusterMatchPromoter_factory` (`HcalBarrelTrackSplitMergeClusterMatches`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L57) | yes |
| `HcalBarrelTrackSplitMergeProtoClusterLinks` | `TrackClusterMergeSplitter_factory` (`HcalBarrelSplitMergeProtoClusters`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L164) | no |
| `HcalBarrelTruthClusterAssociations` | `CalorimeterClusterShape_factory` (`HcalBarrelTruthClusters`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L157) | yes |
| `HcalBarrelTruthClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalBarrelTruthClustersWithoutShapes`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L144) | no |
| `HcalBarrelTruthClusterLinks` | `CalorimeterClusterShape_factory` (`HcalBarrelTruthClusters`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L157) | yes |
| `HcalBarrelTruthClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalBarrelTruthClustersWithoutShapes`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L144) | no |
| `HcalBarrelTruthClusters` | `CalorimeterClusterShape_factory` (`HcalBarrelTruthClusters`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L157) | yes |
| `HcalBarrelTruthClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalBarrelTruthClustersWithoutShapes`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L144) | no |
| `HcalBarrelTruthProtoClusters` | `CalorimeterTruthClustering_factory` (`HcalBarrelTruthProtoClusters`) | [BHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/BHCAL/BHCAL.cc#L98) | no |

## HcalEndcapN* — backward HCal (EHCAL)

34 collections, 18 persisted by default.

| collection | producing factory (instance) | plugin | persisted |
|---|---|---|---|
| `HcalEndcapNCalorimeterTrackProjections` | `SubDivideCollection_factory<TrackSegment>` (`EndcapPBarrelEndcapNCalorimeterTrackProjections`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L106) | no |
| `HcalEndcapNClusterAssociations` | `CalorimeterClusterShape_factory` (`HcalEndcapNClusters`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L140) | yes |
| `HcalEndcapNClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalEndcapNClustersWithoutShapes`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L123) | no |
| `HcalEndcapNClusterLinks` | `CalorimeterClusterShape_factory` (`HcalEndcapNClusters`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L140) | yes |
| `HcalEndcapNClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalEndcapNClustersWithoutShapes`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L123) | no |
| `HcalEndcapNClusters` | `CalorimeterClusterShape_factory` (`HcalEndcapNClusters`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L140) | yes |
| `HcalEndcapNClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalEndcapNClustersWithoutShapes`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L123) | no |
| `HcalEndcapNExpectedClusters` | `TrackClusterSubtractor_factory` (`HcalEndcapNRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L126) | yes |
| `HcalEndcapNIslandProtoClusters` | `CalorimeterIslandCluster_factory` (`HcalEndcapNIslandProtoClusters`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L82) | no |
| `HcalEndcapNMergedHits` | `CalorimeterHitsMerger_factory` (`HcalEndcapNMergedHits`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L72) | yes |
| `HcalEndcapNRawHitAssociations` | `CalorimeterHitDigi_factory` (`HcalEndcapNRawHits`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L38) | no |
| `HcalEndcapNRawHitLinks` | `CalorimeterHitDigi_factory` (`HcalEndcapNRawHits`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L38) | no |
| `HcalEndcapNRawHits` | `CalorimeterHitDigi_factory` (`HcalEndcapNRawHits`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L38) | yes |
| `HcalEndcapNRecHits` | `CalorimeterHitReco_factory` (`HcalEndcapNRecHits`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L55) | yes |
| `HcalEndcapNRemnantClusters` | `TrackClusterSubtractor_factory` (`HcalEndcapNRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L126) | yes |
| `HcalEndcapNSplitMergeClusterAssociations` | `CalorimeterClusterShape_factory` (`HcalEndcapNSplitMergeClusters`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L173) | yes |
| `HcalEndcapNSplitMergeClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalEndcapNClustersWithoutShapes`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L157) | no |
| `HcalEndcapNSplitMergeClusterLinks` | `CalorimeterClusterShape_factory` (`HcalEndcapNSplitMergeClusters`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L173) | yes |
| `HcalEndcapNSplitMergeClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalEndcapNClustersWithoutShapes`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L157) | no |
| `HcalEndcapNSplitMergeClusters` | `CalorimeterClusterShape_factory` (`HcalEndcapNSplitMergeClusters`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L173) | yes |
| `HcalEndcapNSplitMergeClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalEndcapNClustersWithoutShapes`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L157) | no |
| `HcalEndcapNSplitMergeProtoClusters` | `TrackClusterMergeSplitter_factory` (`HcalEndcapNSplitMergeProtoClusters`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L145) | no |
| `HcalEndcapNTrackClusterMatches` | `TrackClusterMatch_factory` (`HcalEndcapNTrackClusterMatches`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L233) | yes |
| `HcalEndcapNTrackExpectedClusterLinks` | `TrackClusterSubtractor_factory` (`HcalEndcapNRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L126) | yes |
| `HcalEndcapNTrackExpectedClusterMatches` | `TrackClusterSubtractor_factory` (`HcalEndcapNRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L126) | yes |
| `HcalEndcapNTrackSplitMergeClusterMatches` | `TrackProtoClusterMatchPromoter_factory` (`HcalEndcapNTrackSplitMergeClusterMatches`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L49) | yes |
| `HcalEndcapNTrackSplitMergeProtoClusterLinks` | `TrackClusterMergeSplitter_factory` (`HcalEndcapNSplitMergeProtoClusters`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L145) | no |
| `HcalEndcapNTruthClusterAssociations` | `CalorimeterClusterShape_factory` (`HcalEndcapNTruthClusters`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L117) | yes |
| `HcalEndcapNTruthClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalEndcapNTruthClustersWithoutShapes`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L105) | no |
| `HcalEndcapNTruthClusterLinks` | `CalorimeterClusterShape_factory` (`HcalEndcapNTruthClusters`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L117) | yes |
| `HcalEndcapNTruthClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalEndcapNTruthClustersWithoutShapes`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L105) | no |
| `HcalEndcapNTruthClusters` | `CalorimeterClusterShape_factory` (`HcalEndcapNTruthClusters`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L117) | yes |
| `HcalEndcapNTruthClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalEndcapNTruthClustersWithoutShapes`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L105) | no |
| `HcalEndcapNTruthProtoClusters` | `CalorimeterTruthClustering_factory` (`HcalEndcapNTruthProtoClusters`) | [EHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/EHCAL/EHCAL.cc#L77) | no |

## HcalEndcapPInsert* and LFHCAL* — forward HCal (FHCAL)

60 collections, 25 persisted by default.

| collection | producing factory (instance) | plugin | persisted |
|---|---|---|---|
| `HcalEndcapPInsertCalorimeterTrackProjections` | `SubDivideCollection_factory<TrackSegment>` (`EndcapPBarrelEndcapNCalorimeterTrackProjections`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L106) | no |
| `HcalEndcapPInsertClusterAssociations` | `CalorimeterClusterShape_factory` (`HcalEndcapPInsertClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L162) | yes |
| `HcalEndcapPInsertClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalEndcapPInsertClustersWithoutShapes`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L144) | no |
| `HcalEndcapPInsertClusterLinks` | `CalorimeterClusterShape_factory` (`HcalEndcapPInsertClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L162) | yes |
| `HcalEndcapPInsertClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalEndcapPInsertClustersWithoutShapes`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L144) | no |
| `HcalEndcapPInsertClusterMatches` | (unresolved — no producer found) | — | yes |
| `HcalEndcapPInsertClusters` | `CalorimeterClusterShape_factory` (`HcalEndcapPInsertClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L162) | yes |
| `HcalEndcapPInsertClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalEndcapPInsertClustersWithoutShapes`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L144) | no |
| `HcalEndcapPInsertExpectedClusters` | `TrackClusterSubtractor_factory` (`HcalEndcapPInsertRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L179) | yes |
| `HcalEndcapPInsertImagingProtoClusters` | `ImagingTopoCluster_factory` (`HcalEndcapPInsertImagingProtoClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L98) | no |
| `HcalEndcapPInsertMergedHits` | `CalorimeterHitsMerger_factory` (`HcalEndcapPInsertMergedHits`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L75) | yes |
| `HcalEndcapPInsertRawHitAssociations` | `CalorimeterHitDigi_factory` (`HcalEndcapPInsertRawHits`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L41) | no |
| `HcalEndcapPInsertRawHitLinks` | `CalorimeterHitDigi_factory` (`HcalEndcapPInsertRawHits`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L41) | no |
| `HcalEndcapPInsertRawHits` | `CalorimeterHitDigi_factory` (`HcalEndcapPInsertRawHits`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L41) | yes |
| `HcalEndcapPInsertRecHits` | `CalorimeterHitReco_factory` (`HcalEndcapPInsertRecHits`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L58) | yes |
| `HcalEndcapPInsertRemnantClusters` | `TrackClusterSubtractor_factory` (`HcalEndcapPInsertRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L179) | yes |
| `HcalEndcapPInsertSubcellHits` | `HEXPLIT_factory` (`HcalEndcapPInsertSubcellHits`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L87) | no |
| `HcalEndcapPInsertTrackClusterMatches` | `TrackClusterMatch_factory` (`HcalEndcapPInsertClusterMatches`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L214) | no |
| `HcalEndcapPInsertTrackExpectedClusterLinks` | `TrackClusterSubtractor_factory` (`HcalEndcapPInsertRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L179) | yes |
| `HcalEndcapPInsertTrackExpectedClusterMatches` | `TrackClusterSubtractor_factory` (`HcalEndcapPInsertRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L179) | yes |
| `HcalEndcapPInsertTruthClusterAssociations` | `CalorimeterClusterShape_factory` (`HcalEndcapPInsertTruthClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L136) | no |
| `HcalEndcapPInsertTruthClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalEndcapPInsertTruthClustersWithoutShapes`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L122) | no |
| `HcalEndcapPInsertTruthClusterLinks` | `CalorimeterClusterShape_factory` (`HcalEndcapPInsertTruthClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L136) | no |
| `HcalEndcapPInsertTruthClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalEndcapPInsertTruthClustersWithoutShapes`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L122) | no |
| `HcalEndcapPInsertTruthClusters` | `CalorimeterClusterShape_factory` (`HcalEndcapPInsertTruthClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L136) | no |
| `HcalEndcapPInsertTruthClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalEndcapPInsertTruthClustersWithoutShapes`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L122) | no |
| `HcalEndcapPInsertTruthProtoClusters` | `CalorimeterTruthClustering_factory` (`HcalEndcapPInsertTruthProtoClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L80) | no |
| `LFHCALClusterAssociations` | `CalorimeterClusterShape_factory` (`LFHCALClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L300) | yes |
| `LFHCALClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`LFHCALClustersWithoutShapes`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L282) | no |
| `LFHCALClusterLinks` | `CalorimeterClusterShape_factory` (`LFHCALClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L300) | yes |
| `LFHCALClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`LFHCALClustersWithoutShapes`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L282) | no |
| `LFHCALClusters` | `CalorimeterClusterShape_factory` (`LFHCALClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L300) | yes |
| `LFHCALClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`LFHCALClustersWithoutShapes`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L282) | no |
| `LFHCALExpectedClusters` | `TrackClusterSubtractor_factory` (`LFHCALRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L170) | yes |
| `LFHCALIslandProtoClusters` | `CalorimeterIslandCluster_factory` (`LFHCALIslandProtoClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L240) | no |
| `LFHCALRawHitAssociations` | `CalorimeterHitDigi_factory` (`LFHCALRawHits`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L181) | no |
| `LFHCALRawHitLinks` | `CalorimeterHitDigi_factory` (`LFHCALRawHits`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L181) | no |
| `LFHCALRawHits` | `CalorimeterHitDigi_factory` (`LFHCALRawHits`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L181) | yes |
| `LFHCALRecHits` | `CalorimeterHitReco_factory` (`LFHCALRecHits`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L199) | yes |
| `LFHCALRemnantClusters` | `TrackClusterSubtractor_factory` (`LFHCALRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L170) | yes |
| `LFHCALSplitMergeClusterAssociations` | `CalorimeterClusterShape_factory` (`LFHCALSplitMergeClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L336) | yes |
| `LFHCALSplitMergeClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`LFHCALSplitMergeClustersWithoutShapes`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L318) | no |
| `LFHCALSplitMergeClusterLinks` | `CalorimeterClusterShape_factory` (`LFHCALSplitMergeClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L336) | yes |
| `LFHCALSplitMergeClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`LFHCALSplitMergeClustersWithoutShapes`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L318) | no |
| `LFHCALSplitMergeClusters` | `CalorimeterClusterShape_factory` (`LFHCALSplitMergeClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L336) | yes |
| `LFHCALSplitMergeClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`LFHCALSplitMergeClustersWithoutShapes`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L318) | no |
| `LFHCALSplitMergeProtoClusters` | `TrackClusterMergeSplitter_factory` (`LFHCALSplitMergeProtoClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L305) | no |
| `LFHCALTrackClusterMatches` | `TrackClusterMatch_factory` (`LFHCALTrackClusterMatches`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L210) | yes |
| `LFHCALTrackExpectedClusterLinks` | `TrackClusterSubtractor_factory` (`LFHCALRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L170) | yes |
| `LFHCALTrackExpectedClusterMatches` | `TrackClusterSubtractor_factory` (`LFHCALRemnantClusters`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L170) | yes |
| `LFHCALTrackProjections` | `SubDivideCollection_factory<TrackSegment>` (`EndcapPBarrelEndcapNCalorimeterTrackProjections`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L106) | no |
| `LFHCALTrackSplitMergeClusterMatches` | `TrackProtoClusterMatchPromoter_factory` (`LFHCALTrackSplitMergeClusterMatches`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L71) | yes |
| `LFHCALTrackSplitMergeProtoClusterLinks` | `TrackClusterMergeSplitter_factory` (`LFHCALSplitMergeProtoClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L305) | no |
| `LFHCALTruthClusterAssociations` | `CalorimeterClusterShape_factory` (`LFHCALTruthClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L276) | no |
| `LFHCALTruthClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`LFHCALTruthClustersWithoutShapes`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L263) | no |
| `LFHCALTruthClusterLinks` | `CalorimeterClusterShape_factory` (`LFHCALTruthClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L276) | no |
| `LFHCALTruthClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`LFHCALTruthClustersWithoutShapes`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L263) | no |
| `LFHCALTruthClusters` | `CalorimeterClusterShape_factory` (`LFHCALTruthClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L276) | no |
| `LFHCALTruthClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`LFHCALTruthClustersWithoutShapes`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L263) | no |
| `LFHCALTruthProtoClusters` | `CalorimeterTruthClustering_factory` (`LFHCALTruthProtoClusters`) | [FHCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/FHCAL/FHCAL.cc#L215) | no |

## ZDC*, B0*, LumiSpec*, RomanPot*, OffM* — far-forward and luminosity

131 collections, 75 persisted by default.

| collection | producing factory (instance) | plugin | persisted |
|---|---|---|---|
| `B0ECalClusterAssociations` | `CalorimeterClusterShape_factory` (`B0ECalClusters`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L97) | yes |
| `B0ECalClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`B0ECalClustersWithoutShapes`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L84) | no |
| `B0ECalClusterLinks` | `CalorimeterClusterShape_factory` (`B0ECalClusters`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L97) | yes |
| `B0ECalClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`B0ECalClustersWithoutShapes`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L84) | no |
| `B0ECalClusters` | `CalorimeterClusterShape_factory` (`B0ECalClusters`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L97) | yes |
| `B0ECalClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`B0ECalClustersWithoutShapes`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L84) | no |
| `B0ECalIslandProtoClusters` | `CalorimeterIslandCluster_factory` (`B0ECalIslandProtoClusters`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L62) | no |
| `B0ECalRawHitAssociations` | `CalorimeterHitDigi_factory` (`B0ECalRawHits`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L27) | no |
| `B0ECalRawHitLinks` | `CalorimeterHitDigi_factory` (`B0ECalRawHits`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L27) | no |
| `B0ECalRawHits` | `CalorimeterHitDigi_factory` (`B0ECalRawHits`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L27) | yes |
| `B0ECalRecHits` | `CalorimeterHitReco_factory` (`B0ECalRecHits`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L44) | yes |
| `B0ECalTruthClusterAssociations` | `CalorimeterClusterShape_factory` (`B0ECalTruthClusters`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L115) | no |
| `B0ECalTruthClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`B0ECalTruthClustersWithoutShapes`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L102) | no |
| `B0ECalTruthClusterLinks` | `CalorimeterClusterShape_factory` (`B0ECalTruthClusters`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L115) | no |
| `B0ECalTruthClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`B0ECalTruthClustersWithoutShapes`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L102) | no |
| `B0ECalTruthClusters` | `CalorimeterClusterShape_factory` (`B0ECalTruthClusters`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L115) | no |
| `B0ECalTruthClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`B0ECalTruthClustersWithoutShapes`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L102) | no |
| `B0ECalTruthProtoClusters` | `CalorimeterTruthClustering_factory` (`B0ECalTruthProtoClusters`) | [B0ECAL](https://github.com/eic/EICrecon/blob/main/src/detectors/B0ECAL/B0ECAL.cc#L59) | no |
| `B0TrackerCKFActsTrackStates` | `AmbiguitySolver_factory` (`B0TrackerAmbiguityResolutionSolver`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L407) | no |
| `B0TrackerCKFActsTrackStatesUnfiltered` | `CKFTracking_factory` (`B0TrackerCKFTrajectories`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L381) | no |
| `B0TrackerCKFActsTracks` | `AmbiguitySolver_factory` (`B0TrackerAmbiguityResolutionSolver`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L407) | no |
| `B0TrackerCKFActsTracksUnfiltered` | `CKFTracking_factory` (`B0TrackerCKFTrajectories`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L381) | no |
| `B0TrackerCKFTrackAssociations` | `ActsToTracks_factory` (`B0TrackerCKFTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L416) | yes |
| `B0TrackerCKFTrackLinks` | `ActsToTracks_factory` (`B0TrackerCKFTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L416) | yes |
| `B0TrackerCKFTrackParameters` | `ActsToTracks_factory` (`B0TrackerCKFTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L416) | yes |
| `B0TrackerCKFTrackParametersUnfiltered` | `ActsToTracks_factory` (`B0TrackerCKFTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L389) | yes |
| `B0TrackerCKFTrackUnfilteredAssociations` | `ActsToTracks_factory` (`B0TrackerCKFTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L389) | yes |
| `B0TrackerCKFTrackUnfilteredLinks` | `ActsToTracks_factory` (`B0TrackerCKFTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L389) | yes |
| `B0TrackerCKFTracks` | `ActsToTracks_factory` (`B0TrackerCKFTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L416) | yes |
| `B0TrackerCKFTracksUnfiltered` | `ActsToTracks_factory` (`B0TrackerCKFTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L389) | yes |
| `B0TrackerCKFTrajectories` | `ActsToTracks_factory` (`B0TrackerCKFTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L416) | yes |
| `B0TrackerCKFTrajectoriesUnfiltered` | `ActsToTracks_factory` (`B0TrackerCKFTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L389) | yes |
| `B0TrackerCKFTruthSeededActsTrackStates` | `AmbiguitySolver_factory` (`B0TrackerTruthSeededAmbiguityResolutionSolver`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L346) | no |
| `B0TrackerCKFTruthSeededActsTrackStatesUnfiltered` | `CKFTracking_factory` (`B0TrackerCKFTruthSeededTrajectories`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L317) | no |
| `B0TrackerCKFTruthSeededActsTracks` | `AmbiguitySolver_factory` (`B0TrackerTruthSeededAmbiguityResolutionSolver`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L346) | no |
| `B0TrackerCKFTruthSeededActsTracksUnfiltered` | `CKFTracking_factory` (`B0TrackerCKFTruthSeededTrajectories`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L317) | no |
| `B0TrackerCKFTruthSeededTrackAssociations` | `ActsToTracks_factory` (`B0TrackerCKFTruthSeededTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L359) | yes |
| `B0TrackerCKFTruthSeededTrackLinks` | `ActsToTracks_factory` (`B0TrackerCKFTruthSeededTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L359) | yes |
| `B0TrackerCKFTruthSeededTrackParameters` | `ActsToTracks_factory` (`B0TrackerCKFTruthSeededTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L359) | yes |
| `B0TrackerCKFTruthSeededTrackParametersUnfiltered` | `ActsToTracks_factory` (`B0TrackerCKFTruthSeededTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L328) | yes |
| `B0TrackerCKFTruthSeededTrackUnfilteredAssociations` | `ActsToTracks_factory` (`B0TrackerCKFTruthSeededTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L328) | yes |
| `B0TrackerCKFTruthSeededTrackUnfilteredLinks` | `ActsToTracks_factory` (`B0TrackerCKFTruthSeededTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L328) | yes |
| `B0TrackerCKFTruthSeededTracks` | `ActsToTracks_factory` (`B0TrackerCKFTruthSeededTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L359) | yes |
| `B0TrackerCKFTruthSeededTracksUnfiltered` | `ActsToTracks_factory` (`B0TrackerCKFTruthSeededTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L328) | yes |
| `B0TrackerCKFTruthSeededTrajectories` | `ActsToTracks_factory` (`B0TrackerCKFTruthSeededTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L359) | yes |
| `B0TrackerCKFTruthSeededTrajectoriesUnfiltered` | `ActsToTracks_factory` (`B0TrackerCKFTruthSeededTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L328) | yes |
| `B0TrackerHits` | (simulation input) | — | yes |
| `B0TrackerMeasurements` | `TrackerMeasurementFromHits_factory` (`B0TrackerMeasurements`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L314) | yes |
| `B0TrackerRawHitAssociations` | `SiliconTrackerDigi_factory` (`B0TrackerRawHits`) | [B0TRK](https://github.com/eic/EICrecon/blob/main/src/detectors/B0TRK/B0TRK.cc#L23) | yes |
| `B0TrackerRawHitLinks` | `SiliconTrackerDigi_factory` (`B0TrackerRawHits`) | [B0TRK](https://github.com/eic/EICrecon/blob/main/src/detectors/B0TRK/B0TRK.cc#L23) | yes |
| `B0TrackerRawHits` | `SiliconTrackerDigi_factory` (`B0TrackerRawHits`) | [B0TRK](https://github.com/eic/EICrecon/blob/main/src/detectors/B0TRK/B0TRK.cc#L23) | yes |
| `B0TrackerRecHits` | `TrackerHitReconstruction_factory` (`B0TrackerRecHits`) | [B0TRK](https://github.com/eic/EICrecon/blob/main/src/detectors/B0TRK/B0TRK.cc#L33) | yes |
| `B0TrackerSeedParameters` | `TrackSeeding_factory` (`B0TrackerSeeds`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L377) | yes |
| `B0TrackerSeeds` | `TrackSeeding_factory` (`B0TrackerSeeds`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L377) | yes |
| `B0TrackerTruthSeeds` | `SubDivideCollection_factory<TrackSeed>` (`CentralB0TrackerTruthSeeds`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L58) | yes |
| `EcalFarForwardZDCClusterAssociations` | `CalorimeterClusterShape_factory` (`EcalFarForwardZDCClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L133) | yes |
| `EcalFarForwardZDCClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalFarForwardZDCClustersWithoutShapes`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L115) | no |
| `EcalFarForwardZDCClusterLinks` | `CalorimeterClusterShape_factory` (`EcalFarForwardZDCClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L133) | yes |
| `EcalFarForwardZDCClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalFarForwardZDCClustersWithoutShapes`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L115) | no |
| `EcalFarForwardZDCClusters` | `CalorimeterClusterShape_factory` (`EcalFarForwardZDCClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L133) | yes |
| `EcalFarForwardZDCClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalFarForwardZDCClustersWithoutShapes`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L115) | no |
| `EcalFarForwardZDCIslandProtoClusters` | `CalorimeterIslandCluster_factory` (`EcalFarForwardZDCIslandProtoClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L69) | no |
| `EcalFarForwardZDCRawHitAssociations` | `CalorimeterHitDigi_factory` (`EcalFarForwardZDCRawHits`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L31) | no |
| `EcalFarForwardZDCRawHitLinks` | `CalorimeterHitDigi_factory` (`EcalFarForwardZDCRawHits`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L31) | no |
| `EcalFarForwardZDCRawHits` | `CalorimeterHitDigi_factory` (`EcalFarForwardZDCRawHits`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L31) | yes |
| `EcalFarForwardZDCRecHits` | `CalorimeterHitReco_factory` (`EcalFarForwardZDCRecHits`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L48) | yes |
| `EcalFarForwardZDCTruthClusterAssociations` | `CalorimeterClusterShape_factory` (`EcalFarForwardZDCTruthClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L107) | yes |
| `EcalFarForwardZDCTruthClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalFarForwardZDCTruthClustersWithoutShapes`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L93) | no |
| `EcalFarForwardZDCTruthClusterLinks` | `CalorimeterClusterShape_factory` (`EcalFarForwardZDCTruthClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L107) | yes |
| `EcalFarForwardZDCTruthClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalFarForwardZDCTruthClustersWithoutShapes`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L93) | no |
| `EcalFarForwardZDCTruthClusters` | `CalorimeterClusterShape_factory` (`EcalFarForwardZDCTruthClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L107) | yes |
| `EcalFarForwardZDCTruthClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalFarForwardZDCTruthClustersWithoutShapes`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L93) | no |
| `EcalFarForwardZDCTruthProtoClusters` | `CalorimeterTruthClustering_factory` (`EcalFarForwardZDCTruthProtoClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L63) | no |
| `EcalLumiSpecClusterAssociations` | `CalorimeterClusterShape_factory` (`EcalLumiSpecClusters`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L101) | yes |
| `EcalLumiSpecClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalLumiSpecClustersWithoutShapes`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L89) | no |
| `EcalLumiSpecClusterLinks` | `CalorimeterClusterShape_factory` (`EcalLumiSpecClusters`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L101) | yes |
| `EcalLumiSpecClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalLumiSpecClustersWithoutShapes`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L89) | no |
| `EcalLumiSpecClusters` | `CalorimeterClusterShape_factory` (`EcalLumiSpecClusters`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L101) | yes |
| `EcalLumiSpecClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalLumiSpecClustersWithoutShapes`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L89) | no |
| `EcalLumiSpecIslandProtoClusters` | `CalorimeterIslandCluster_factory` (`EcalLumiSpecIslandProtoClusters`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L63) | no |
| `EcalLumiSpecRawHitAssociations` | `CalorimeterHitDigi_factory` (`EcalLumiSpecRawHits`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L27) | no |
| `EcalLumiSpecRawHitLinks` | `CalorimeterHitDigi_factory` (`EcalLumiSpecRawHits`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L27) | no |
| `EcalLumiSpecRawHits` | `CalorimeterHitDigi_factory` (`EcalLumiSpecRawHits`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L27) | yes |
| `EcalLumiSpecRecHits` | `CalorimeterHitReco_factory` (`EcalLumiSpecRecHits`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L43) | yes |
| `EcalLumiSpecTruthClusterAssociations` | `CalorimeterClusterShape_factory` (`EcalLumiSpecTruthClusters`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L119) | yes |
| `EcalLumiSpecTruthClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalLumiSpecTruthClustersWithoutShapes`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L107) | no |
| `EcalLumiSpecTruthClusterLinks` | `CalorimeterClusterShape_factory` (`EcalLumiSpecTruthClusters`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L119) | yes |
| `EcalLumiSpecTruthClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalLumiSpecTruthClustersWithoutShapes`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L107) | no |
| `EcalLumiSpecTruthClusters` | `CalorimeterClusterShape_factory` (`EcalLumiSpecTruthClusters`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L119) | yes |
| `EcalLumiSpecTruthClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`EcalLumiSpecTruthClustersWithoutShapes`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L107) | no |
| `EcalLumiSpecTruthProtoClusters` | `CalorimeterTruthClustering_factory` (`EcalLumiSpecTruthProtoClusters`) | [LUMISPECCAL](https://github.com/eic/EICrecon/blob/main/src/detectors/LUMISPECCAL/LUMISPECCAL.cc#L58) | no |
| `ForwardOffMRecParticles` | `MatrixTransferStatic_factory` (`ForwardOffMRecParticles`) | [FOFFMTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/FOFFMTRK/FOFFMTRK.cc#L41) | yes |
| `ForwardOffMTrackerHits` | (simulation input) | — | yes |
| `ForwardOffMTrackerRawHitAssociations` | `SiliconTrackerDigi_factory` (`ForwardOffMTrackerRawHits`) | [FOFFMTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/FOFFMTRK/FOFFMTRK.cc#L24) | yes |
| `ForwardOffMTrackerRawHitLinks` | `SiliconTrackerDigi_factory` (`ForwardOffMTrackerRawHits`) | [FOFFMTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/FOFFMTRK/FOFFMTRK.cc#L24) | yes |
| `ForwardOffMTrackerRawHits` | `SiliconTrackerDigi_factory` (`ForwardOffMTrackerRawHits`) | [FOFFMTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/FOFFMTRK/FOFFMTRK.cc#L24) | yes |
| `ForwardOffMTrackerRecHits` | `TrackerHitReconstruction_factory` (`ForwardOffMTrackerRecHits`) | [FOFFMTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/FOFFMTRK/FOFFMTRK.cc#L34) | yes |
| `ForwardRomanPotHits` | (simulation input) | — | yes |
| `ForwardRomanPotRawHitAssociations` | `SiliconTrackerDigi_factory` (`ForwardRomanPotRawHits`) | [RPOTS](https://github.com/eic/EICrecon/blob/main/src/detectors/RPOTS/RPOTS.cc#L29) | yes |
| `ForwardRomanPotRawHitLinks` | `SiliconTrackerDigi_factory` (`ForwardRomanPotRawHits`) | [RPOTS](https://github.com/eic/EICrecon/blob/main/src/detectors/RPOTS/RPOTS.cc#L29) | yes |
| `ForwardRomanPotRawHits` | `SiliconTrackerDigi_factory` (`ForwardRomanPotRawHits`) | [RPOTS](https://github.com/eic/EICrecon/blob/main/src/detectors/RPOTS/RPOTS.cc#L29) | yes |
| `ForwardRomanPotRecHits` | `TrackerHitReconstruction_factory` (`ForwardRomanPotRecHits`) | [RPOTS](https://github.com/eic/EICrecon/blob/main/src/detectors/RPOTS/RPOTS.cc#L38) | yes |
| `ForwardRomanPotRecParticles` | `PolynomialMatrixReconstruction_factory` (`ForwardRomanPotRecParticles`) | [RPOTS](https://github.com/eic/EICrecon/blob/main/src/detectors/RPOTS/RPOTS.cc#L143) | yes |
| `ForwardRomanPotStaticRecParticles` | `MatrixTransferStatic_factory` (`ForwardRomanPotStaticRecParticles`) | [RPOTS](https://github.com/eic/EICrecon/blob/main/src/detectors/RPOTS/RPOTS.cc#L45) | yes |
| `HcalFarForwardZDCClusterAssociations` | `CalorimeterClusterShape_factory` (`HcalFarForwardZDCClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L246) | yes |
| `HcalFarForwardZDCClusterAssociationsBaseline` | `CalorimeterClusterShape_factory` (`HcalFarForwardZDCClustersBaseline`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L330) | yes |
| `HcalFarForwardZDCClusterAssociationsBaselineWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalFarForwardZDCClustersBaselineWithoutShapes`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L311) | no |
| `HcalFarForwardZDCClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalFarForwardZDCClustersWithoutShapes`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L230) | no |
| `HcalFarForwardZDCClusterLinks` | `CalorimeterClusterShape_factory` (`HcalFarForwardZDCClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L246) | yes |
| `HcalFarForwardZDCClusterLinksBaseline` | `CalorimeterClusterShape_factory` (`HcalFarForwardZDCClustersBaseline`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L330) | yes |
| `HcalFarForwardZDCClusterLinksBaselineWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalFarForwardZDCClustersBaselineWithoutShapes`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L311) | no |
| `HcalFarForwardZDCClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalFarForwardZDCClustersWithoutShapes`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L230) | no |
| `HcalFarForwardZDCClusters` | `CalorimeterClusterShape_factory` (`HcalFarForwardZDCClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L246) | yes |
| `HcalFarForwardZDCClustersBaseline` | `CalorimeterClusterShape_factory` (`HcalFarForwardZDCClustersBaseline`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L330) | yes |
| `HcalFarForwardZDCClustersBaselineWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalFarForwardZDCClustersBaselineWithoutShapes`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L311) | no |
| `HcalFarForwardZDCClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalFarForwardZDCClustersWithoutShapes`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L230) | no |
| `HcalFarForwardZDCImagingProtoClusters` | `ImagingTopoCluster_factory` (`HcalFarForwardZDCImagingProtoClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L191) | no |
| `HcalFarForwardZDCIslandProtoClusters` | `CalorimeterIslandCluster_factory` (`HcalFarForwardZDCIslandProtoClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L208) | no |
| `HcalFarForwardZDCIslandProtoClustersBaseline` | `CalorimeterIslandCluster_factory` (`HcalFarForwardZDCIslandProtoClustersBaseline`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L267) | no |
| `HcalFarForwardZDCRawHitAssociations` | `CalorimeterHitDigi_factory` (`HcalFarForwardZDCRawHits`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L141) | no |
| `HcalFarForwardZDCRawHitLinks` | `CalorimeterHitDigi_factory` (`HcalFarForwardZDCRawHits`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L141) | no |
| `HcalFarForwardZDCRawHits` | `CalorimeterHitDigi_factory` (`HcalFarForwardZDCRawHits`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L141) | yes |
| `HcalFarForwardZDCRecHits` | `CalorimeterHitReco_factory` (`HcalFarForwardZDCRecHits`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L159) | yes |
| `HcalFarForwardZDCSubcellHits` | `HEXPLIT_factory` (`HcalFarForwardZDCSubcellHits`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L177) | yes |
| `HcalFarForwardZDCTruthClusterAssociations` | `CalorimeterClusterShape_factory` (`HcalFarForwardZDCTruthClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L303) | yes |
| `HcalFarForwardZDCTruthClusterAssociationsWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalFarForwardZDCTruthClustersWithoutShapes`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L289) | no |
| `HcalFarForwardZDCTruthClusterLinks` | `CalorimeterClusterShape_factory` (`HcalFarForwardZDCTruthClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L303) | yes |
| `HcalFarForwardZDCTruthClusterLinksWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalFarForwardZDCTruthClustersWithoutShapes`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L289) | no |
| `HcalFarForwardZDCTruthClusters` | `CalorimeterClusterShape_factory` (`HcalFarForwardZDCTruthClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L303) | yes |
| `HcalFarForwardZDCTruthClustersWithoutShapes` | `CalorimeterClusterRecoCoG_factory` (`HcalFarForwardZDCTruthClustersWithoutShapes`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L289) | no |
| `HcalFarForwardZDCTruthProtoClusters` | `CalorimeterTruthClustering_factory` (`HcalFarForwardZDCTruthProtoClusters`) | [ZDC](https://github.com/eic/EICrecon/blob/main/src/detectors/ZDC/ZDC.cc#L259) | no |

## TaggerTracker* — low-Q2 tagger (LOWQ2)

40 collections, 28 persisted by default.

| collection | producing factory (instance) | plugin | persisted |
|---|---|---|---|
| `TaggerTrackerCombinedPulses` | `PulseCombiner_factory` (`TaggerTrackerPulseCombiner`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L72) | yes |
| `TaggerTrackerCombinedPulsesWithNoise` | `PulseNoise_factory` (`TaggerTrackerPulseNoise`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L80) | yes |
| `TaggerTrackerFeatureTensor` | `FarDetectorTransportationPreML_factory` (`TaggerTrackerTransportationPreML`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L196) | no |
| `TaggerTrackerHitPulses` | `PulseGeneration_factory<SimTrackerHit>` (`TaggerTrackerPulseGeneration`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L61) | yes |
| `TaggerTrackerHits` | (simulation input) | — | yes |
| `TaggerTrackerLocalTrackAssociations` | `CollectionCollector_factory<MCRecoTrackParticleAssociation, true>` (`TaggerTrackerLocalTrackAssociations`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L191) | yes |
| `TaggerTrackerLocalTrackLinks` | `CollectionCollector_factory<MCRecoTrackParticleLink, true>` (`TaggerTrackerLocalTrackLinks`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L186) | yes |
| `TaggerTrackerLocalTracks` | `CollectionCollector_factory<Track, true>` (`TaggerTrackerLocalTracks`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L182) | yes |
| `TaggerTrackerM1L0ClusterPositions` | `FarDetectorTrackerCluster_factory` (`TaggerTrackerClustering`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L145) | yes |
| `TaggerTrackerM1L0RecHits` | `SubDivideCollection_factory<TrackerHit>` (`TaggerTrackerSplitHits`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L138) | no |
| `TaggerTrackerM1L1ClusterPositions` | `FarDetectorTrackerCluster_factory` (`TaggerTrackerClustering`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L145) | yes |
| `TaggerTrackerM1L1RecHits` | `SubDivideCollection_factory<TrackerHit>` (`TaggerTrackerSplitHits`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L138) | no |
| `TaggerTrackerM1L2ClusterPositions` | `FarDetectorTrackerCluster_factory` (`TaggerTrackerClustering`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L145) | yes |
| `TaggerTrackerM1L2RecHits` | `SubDivideCollection_factory<TrackerHit>` (`TaggerTrackerSplitHits`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L138) | no |
| `TaggerTrackerM1L3ClusterPositions` | `FarDetectorTrackerCluster_factory` (`TaggerTrackerClustering`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L145) | yes |
| `TaggerTrackerM1L3RecHits` | `SubDivideCollection_factory<TrackerHit>` (`TaggerTrackerSplitHits`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L138) | no |
| `TaggerTrackerM1LocalTrackAssociations` | `FarDetectorLinearTracking_factory` (`outputTrackTag`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L165) | yes |
| `TaggerTrackerM1LocalTrackLinks` | `FarDetectorLinearTracking_factory` (`outputTrackTag`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L165) | yes |
| `TaggerTrackerM1LocalTracks` | `FarDetectorLinearTracking_factory` (`outputTrackTag`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L165) | yes |
| `TaggerTrackerM2L0ClusterPositions` | `FarDetectorTrackerCluster_factory` (`TaggerTrackerClustering`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L145) | yes |
| `TaggerTrackerM2L0RecHits` | `SubDivideCollection_factory<TrackerHit>` (`TaggerTrackerSplitHits`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L138) | no |
| `TaggerTrackerM2L1ClusterPositions` | `FarDetectorTrackerCluster_factory` (`TaggerTrackerClustering`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L145) | yes |
| `TaggerTrackerM2L1RecHits` | `SubDivideCollection_factory<TrackerHit>` (`TaggerTrackerSplitHits`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L138) | no |
| `TaggerTrackerM2L2ClusterPositions` | `FarDetectorTrackerCluster_factory` (`TaggerTrackerClustering`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L145) | yes |
| `TaggerTrackerM2L2RecHits` | `SubDivideCollection_factory<TrackerHit>` (`TaggerTrackerSplitHits`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L138) | no |
| `TaggerTrackerM2L3ClusterPositions` | `FarDetectorTrackerCluster_factory` (`TaggerTrackerClustering`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L145) | yes |
| `TaggerTrackerM2L3RecHits` | `SubDivideCollection_factory<TrackerHit>` (`TaggerTrackerSplitHits`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L138) | no |
| `TaggerTrackerM2LocalTrackAssociations` | `FarDetectorLinearTracking_factory` (`outputTrackTag`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L165) | yes |
| `TaggerTrackerM2LocalTrackLinks` | `FarDetectorLinearTracking_factory` (`outputTrackTag`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L165) | yes |
| `TaggerTrackerM2LocalTracks` | `FarDetectorLinearTracking_factory` (`outputTrackTag`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L165) | yes |
| `TaggerTrackerPredictionTensor` | `ONNXInference_factory` (`TaggerTrackerTransportationInference`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L204) | no |
| `TaggerTrackerRawHitAssociations` | `SiliconTrackerDigi_factory` (`TaggerTrackerRawHits`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L92) | yes |
| `TaggerTrackerRawHitLinks` | `SiliconTrackerDigi_factory` (`TaggerTrackerRawHits`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L92) | yes |
| `TaggerTrackerRawHits` | `SiliconTrackerDigi_factory` (`TaggerTrackerRawHits`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L92) | yes |
| `TaggerTrackerRecHits` | `TrackerHitReconstruction_factory` (`TaggerTrackerRecHits`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L102) | no |
| `TaggerTrackerReconstructedParticleAssociations` | `FarDetectorTransportationPostML_factory` (`TaggerTrackerTransportationPostML`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L211) | yes |
| `TaggerTrackerReconstructedParticleLinks` | `FarDetectorTransportationPostML_factory` (`TaggerTrackerTransportationPostML`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L211) | yes |
| `TaggerTrackerReconstructedParticles` | `FarDetectorTransportationPostML_factory` (`TaggerTrackerTransportationPostML`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L211) | yes |
| `TaggerTrackerSharedHits` | `SiliconChargeSharing_factory` (`TaggerTrackerChargeSharing`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L51) | yes |
| `TaggerTrackerTargetTensor` | `FarDetectorTransportationPreML_factory` (`TaggerTrackerTransportationPreML`) | [LOWQ2](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L196) | no |

## Si* and Tracker*/VertexBarrel* — silicon tracker and vertex hits

23 collections, 23 persisted by default.

| collection | producing factory (instance) | plugin | persisted |
|---|---|---|---|
| `SiBarrelHits` | (simulation input) | — | yes |
| `SiBarrelNoiseRawHits` | `RandomNoisePixel_factory` (`SiBarrelNoiseRawHits`) | [BTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/BTRK/BTRK.cc#L35) | yes |
| `SiBarrelRawHitAssociations` | `SiliconTrackerDigi_factory` (`SiBarrelRawHits`) | [BTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/BTRK/BTRK.cc#L27) | yes |
| `SiBarrelRawHitLinks` | `SiliconTrackerDigi_factory` (`SiBarrelRawHits`) | [BTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/BTRK/BTRK.cc#L27) | yes |
| `SiBarrelRawHits` | `SiliconTrackerDigi_factory` (`SiBarrelRawHits`) | [BTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/BTRK/BTRK.cc#L27) | yes |
| `SiBarrelRawHitsWithNoise` | `CollectionCollector_factory<RawTrackerHit>` (`SiBarrelRawHitsWithNoise`) | [BTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/BTRK/BTRK.cc#L40) | yes |
| `SiBarrelTrackerRecHits` | `TrackerHitReconstruction_factory` (`SiBarrelTrackerRecHits`) | [BTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/BTRK/BTRK.cc#L48) | yes |
| `SiBarrelVertexNoiseRawHits` | `RandomNoisePixel_factory` (`SiBarrelVertexNoiseRawHits`) | [BVTX](https://github.com/eic/EICrecon/blob/main/src/detectors/BVTX/BVTX.cc#L35) | yes |
| `SiBarrelVertexRawHitAssociations` | `SiliconTrackerDigi_factory` (`SiBarrelVertexRawHits`) | [BVTX](https://github.com/eic/EICrecon/blob/main/src/detectors/BVTX/BVTX.cc#L28) | yes |
| `SiBarrelVertexRawHitLinks` | `SiliconTrackerDigi_factory` (`SiBarrelVertexRawHits`) | [BVTX](https://github.com/eic/EICrecon/blob/main/src/detectors/BVTX/BVTX.cc#L28) | yes |
| `SiBarrelVertexRawHits` | `SiliconTrackerDigi_factory` (`SiBarrelVertexRawHits`) | [BVTX](https://github.com/eic/EICrecon/blob/main/src/detectors/BVTX/BVTX.cc#L28) | yes |
| `SiBarrelVertexRawHitsWithNoise` | `CollectionCollector_factory<RawTrackerHit>` (`SiBarrelVertexRawHitsWithNoise`) | [BVTX](https://github.com/eic/EICrecon/blob/main/src/detectors/BVTX/BVTX.cc#L41) | yes |
| `SiBarrelVertexRecHits` | `TrackerHitReconstruction_factory` (`SiBarrelVertexRecHits`) | [BVTX](https://github.com/eic/EICrecon/blob/main/src/detectors/BVTX/BVTX.cc#L46) | yes |
| `SiEndcapTrackerNoiseRawHits` | `RandomNoisePixel_factory` (`SiEndcapTrackerNoiseRawHits`) | [ECTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTRK/ECTRK.cc#L35) | yes |
| `SiEndcapTrackerRawHitAssociations` | `SiliconTrackerDigi_factory` (`SiEndcapTrackerRawHits`) | [ECTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTRK/ECTRK.cc#L27) | yes |
| `SiEndcapTrackerRawHitLinks` | `SiliconTrackerDigi_factory` (`SiEndcapTrackerRawHits`) | [ECTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTRK/ECTRK.cc#L27) | yes |
| `SiEndcapTrackerRawHits` | `SiliconTrackerDigi_factory` (`SiEndcapTrackerRawHits`) | [ECTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTRK/ECTRK.cc#L27) | yes |
| `SiEndcapTrackerRawHitsWithNoise` | `CollectionCollector_factory<RawTrackerHit>` (`SiEndcapTrackerRawHitsWithNoise`) | [ECTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTRK/ECTRK.cc#L41) | yes |
| `SiEndcapTrackerRecHits` | `TrackerHitReconstruction_factory` (`SiEndcapTrackerRecHits`) | [ECTRK](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTRK/ECTRK.cc#L45) | yes |
| `TrackerEndcapHits` | (simulation input) | — | yes |
| `TrackerTruthSeedParameters` | `TrackParamTruthInit_factory` (`TrackerTruthSeeds`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L52) | yes |
| `TrackerTruthSeeds` | `TrackParamTruthInit_factory` (`TrackerTruthSeeds`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L52) | yes |
| `VertexBarrelHits` | (simulation input) | — | yes |

## *MPGD* — micro-pattern gas detectors

20 collections, 20 persisted by default.

| collection | producing factory (instance) | plugin | persisted |
|---|---|---|---|
| `BackwardMPGDEndcapHits` | (simulation input) | — | yes |
| `BackwardMPGDEndcapRawHitAssociations` | `SiliconTrackerDigi_factory` (`BackwardMPGDEndcapRawHits`) | [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L214) | yes |
| `BackwardMPGDEndcapRawHitLinks` | `SiliconTrackerDigi_factory` (`BackwardMPGDEndcapRawHits`) | [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L214) | yes |
| `BackwardMPGDEndcapRawHits` | `SiliconTrackerDigi_factory` (`BackwardMPGDEndcapRawHits`) | [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L214) | yes |
| `BackwardMPGDEndcapRecHits` | `TrackerHitReconstruction_factory` (`BackwardMPGDEndcapRecHits`) | [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L225) | yes |
| `ForwardMPGDEndcapHits` | (simulation input) | — | yes |
| `ForwardMPGDEndcapRawHitAssociations` | `SiliconTrackerDigi_factory` (`ForwardMPGDEndcapRawHits`) | [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L235) | yes |
| `ForwardMPGDEndcapRawHitLinks` | `SiliconTrackerDigi_factory` (`ForwardMPGDEndcapRawHits`) | [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L235) | yes |
| `ForwardMPGDEndcapRawHits` | `SiliconTrackerDigi_factory` (`ForwardMPGDEndcapRawHits`) | [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L235) | yes |
| `ForwardMPGDEndcapRecHits` | `TrackerHitReconstruction_factory` (`ForwardMPGDEndcapRecHits`) | [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L246) | yes |
| `MPGDBarrelHits` | (simulation input) | — | yes |
| `MPGDBarrelRawHitAssociations` | `SiliconTrackerDigi_factory` (`MPGDBarrelRawHits`) **or** `MPGDTrackerDigi_factory` (`MPGDBarrelRawHits`) | [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L102) / [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L131) | yes |
| `MPGDBarrelRawHitLinks` | `SiliconTrackerDigi_factory` (`MPGDBarrelRawHits`) **or** `MPGDTrackerDigi_factory` (`MPGDBarrelRawHits`) | [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L102) / [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L131) | yes |
| `MPGDBarrelRawHits` | `SiliconTrackerDigi_factory` (`MPGDBarrelRawHits`) **or** `MPGDTrackerDigi_factory` (`MPGDBarrelRawHits`) | [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L102) / [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L131) | yes |
| `MPGDBarrelRecHits` | `TrackerHitReconstruction_factory` (`MPGDBarrelRecHits`) **or** `MPGDHitReconstruction_factory` (`MPGDBarrelRecHits`) | [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L139) / [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L151) | yes |
| `OuterMPGDBarrelHits` | (simulation input) | — | yes |
| `OuterMPGDBarrelRawHitAssociations` | `SiliconTrackerDigi_factory` (`OuterMPGDBarrelRawHits`) **or** `MPGDTrackerDigi_factory` (`OuterMPGDBarrelRawHits`) | [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L160) / [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L185) | yes |
| `OuterMPGDBarrelRawHitLinks` | `SiliconTrackerDigi_factory` (`OuterMPGDBarrelRawHits`) **or** `MPGDTrackerDigi_factory` (`OuterMPGDBarrelRawHits`) | [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L160) / [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L185) | yes |
| `OuterMPGDBarrelRawHits` | `SiliconTrackerDigi_factory` (`OuterMPGDBarrelRawHits`) **or** `MPGDTrackerDigi_factory` (`OuterMPGDBarrelRawHits`) | [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L160) / [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L185) | yes |
| `OuterMPGDBarrelRecHits` | `TrackerHitReconstruction_factory` (`OuterMPGDBarrelRecHits`) **or** `MPGDHitReconstruction_factory` (`OuterMPGDBarrelRecHits`) | [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L194) / [MPGD](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L206) | yes |

## TOF* — time-of-flight (BTOF / ECTOF)

27 collections, 20 persisted by default.

| collection | producing factory (instance) | plugin | persisted |
|---|---|---|---|
| `TOFBarrelADCTDC` | `CFDROCDigitization_factory` (`CFDROCDigitization`) | [BTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L127) | yes |
| `TOFBarrelCalibratedHits` | `LGADHitCalibration_factory` (`TOFBarrelCalibratedHits`) | [BTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L41) | no |
| `TOFBarrelClusterHits` | `LGADHitClustering_factory` (`TOFBarrelClusterHits`) | [BTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L50) | yes |
| `TOFBarrelCombinedPulses` | `PulseCombiner_factory` (`TOFBarrelPulseCombiner`) | [BTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L110) | no |
| `TOFBarrelHits` | (simulation input) | — | yes |
| `TOFBarrelPulses` | `SiliconPulseDiscretization_factory` (`TOFBarrelPulses`) | [BTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L118) | no |
| `TOFBarrelRawHitAssociations` | (unresolved — no producer found) | — | yes |
| `TOFBarrelRawHitLinks` | (unresolved — no producer found) | — | yes |
| `TOFBarrelSharedHits` | `SiliconChargeSharing_factory` (`TOFBarrelSharedHits`) | [BTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L59) | yes |
| `TOFBarrelSharedRawHitAssociations` | `SiliconTrackerDigi_factory` (`TOFBarrelSharedRawHits`) | [BTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L72) | yes |
| `TOFBarrelSharedRawHitLinks` | `SiliconTrackerDigi_factory` (`TOFBarrelSharedRawHits`) | [BTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L72) | yes |
| `TOFBarrelSharedRawHits` | `SiliconTrackerDigi_factory` (`TOFBarrelSharedRawHits`) | [BTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L72) | yes |
| `TOFBarrelSharedRecHits` | `TrackerHitReconstruction_factory` (`TOFBarrelSharedRecHits`) | [BTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L82) | yes |
| `TOFBarrelSmoothPulses` | `PulseGeneration_factory<SimTrackerHit>` (`LGADPulseGeneration`) | [BTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/BTOF/BTOF.cc#L100) | no |
| `TOFEndcapADCTDC` | `EICROCDigitization_factory` (`TOFEndcapADCTDC`) | [ECTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L111) | yes |
| `TOFEndcapClusterHits` | `LGADHitClustering_factory` (`TOFEndcapClusterHits`) | [ECTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L37) | yes |
| `TOFEndcapCombinedPulses` | `PulseCombiner_factory` (`TOFEndcapCombinedPulses`) | [ECTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L94) | no |
| `TOFEndcapHits` | (simulation input) | — | yes |
| `TOFEndcapPulses` | `SiliconPulseDiscretization_factory` (`TOFEndcapPulses`) | [ECTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L102) | no |
| `TOFEndcapRawHitAssociations` | (unresolved — no producer found) | — | yes |
| `TOFEndcapRawHitLinks` | (unresolved — no producer found) | — | yes |
| `TOFEndcapSharedHits` | `SiliconChargeSharing_factory` (`TOFEndcapSharedHits`) | [ECTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L46) | yes |
| `TOFEndcapSharedRawHitAssociations` | `SiliconTrackerDigi_factory` (`TOFEndcapSharedRawHits`) | [ECTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L60) | yes |
| `TOFEndcapSharedRawHitLinks` | `SiliconTrackerDigi_factory` (`TOFEndcapSharedRawHits`) | [ECTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L60) | yes |
| `TOFEndcapSharedRawHits` | `SiliconTrackerDigi_factory` (`TOFEndcapSharedRawHits`) | [ECTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L60) | yes |
| `TOFEndcapSharedRecHits` | `TrackerHitReconstruction_factory` (`TOFEndcapSharedRecHits`) | [ECTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L70) | yes |
| `TOFEndcapSmoothPulses` | `PulseGeneration_factory<SimTrackerHit>` (`TOFEndcapSmoothPulses`) | [ECTOF](https://github.com/eic/EICrecon/blob/main/src/detectors/ECTOF/ECTOF.cc#L84) | no |

## Central*, Combined*, *Vertices, *TrackProjections — central tracking

52 collections, 38 persisted by default.

| collection | producing factory (instance) | plugin | persisted |
|---|---|---|---|
| `CalorimeterTrackProjections` | `TrackPropagation_factory` (`CalorimeterTrackPropagator`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L247) | yes |
| `CentralAndB0TrackVertices` | `IterativeVertexFinder_factory` (`CentralAndB0TrackVertices`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L450) | yes |
| `CentralAndB0TrackerCKFActsTrackStates` | `ActsTrackMerger_factory` (`CentralAndB0TrackerCKFActsTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L436) | no |
| `CentralAndB0TrackerCKFActsTracks` | `ActsTrackMerger_factory` (`CentralAndB0TrackerCKFActsTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L436) | no |
| `CentralCKFActsTrackStates` | `AmbiguitySolver_factory` (`AmbiguityResolutionSolver`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L198) | no |
| `CentralCKFActsTrackStatesUnfiltered` | `CKFTracking_factory` (`CentralCKFTrajectories`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L172) | no |
| `CentralCKFActsTracks` | `AmbiguitySolver_factory` (`AmbiguityResolutionSolver`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L198) | no |
| `CentralCKFActsTracksUnfiltered` | `CKFTracking_factory` (`CentralCKFTrajectories`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L172) | no |
| `CentralCKFTrackAssociations` | `ActsToTracks_factory` (`CentralCKFTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L207) | yes |
| `CentralCKFTrackLinks` | `ActsToTracks_factory` (`CentralCKFTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L207) | yes |
| `CentralCKFTrackParameters` | `ActsToTracks_factory` (`CentralCKFTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L207) | yes |
| `CentralCKFTrackParametersUnfiltered` | `ActsToTracks_factory` (`CentralCKFTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L181) | yes |
| `CentralCKFTrackUnfilteredAssociations` | `ActsToTracks_factory` (`CentralCKFTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L181) | yes |
| `CentralCKFTrackUnfilteredLinks` | `ActsToTracks_factory` (`CentralCKFTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L181) | yes |
| `CentralCKFTracks` | `ActsToTracks_factory` (`CentralCKFTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L207) | yes |
| `CentralCKFTracksUnfiltered` | `ActsToTracks_factory` (`CentralCKFTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L181) | yes |
| `CentralCKFTrajectories` | `ActsToTracks_factory` (`CentralCKFTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L207) | yes |
| `CentralCKFTrajectoriesUnfiltered` | `ActsToTracks_factory` (`CentralCKFTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L181) | yes |
| `CentralCKFTruthSeededActsTrackStates` | `AmbiguitySolver_factory` (`TruthSeededAmbiguityResolutionSolver`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L140) | no |
| `CentralCKFTruthSeededActsTrackStatesUnfiltered` | `CKFTracking_factory` (`CentralCKFTruthSeededTrajectories`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L113) | no |
| `CentralCKFTruthSeededActsTracks` | `AmbiguitySolver_factory` (`TruthSeededAmbiguityResolutionSolver`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L140) | no |
| `CentralCKFTruthSeededActsTracksUnfiltered` | `CKFTracking_factory` (`CentralCKFTruthSeededTrajectories`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L113) | no |
| `CentralCKFTruthSeededTrackAssociations` | `ActsToTracks_factory` (`CentralCKFTruthSeededTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L151) | yes |
| `CentralCKFTruthSeededTrackLinks` | `ActsToTracks_factory` (`CentralCKFTruthSeededTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L151) | yes |
| `CentralCKFTruthSeededTrackParameters` | `ActsToTracks_factory` (`CentralCKFTruthSeededTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L151) | yes |
| `CentralCKFTruthSeededTrackParametersUnfiltered` | `ActsToTracks_factory` (`CentralCKFTruthSeededTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L122) | yes |
| `CentralCKFTruthSeededTrackUnfilteredAssociations` | `ActsToTracks_factory` (`CentralCKFTruthSeededTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L122) | yes |
| `CentralCKFTruthSeededTrackUnfilteredLinks` | `ActsToTracks_factory` (`CentralCKFTruthSeededTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L122) | yes |
| `CentralCKFTruthSeededTracks` | `ActsToTracks_factory` (`CentralCKFTruthSeededTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L151) | yes |
| `CentralCKFTruthSeededTracksUnfiltered` | `ActsToTracks_factory` (`CentralCKFTruthSeededTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L122) | yes |
| `CentralCKFTruthSeededTrajectories` | `ActsToTracks_factory` (`CentralCKFTruthSeededTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L151) | yes |
| `CentralCKFTruthSeededTrajectoriesUnfiltered` | `ActsToTracks_factory` (`CentralCKFTruthSeededTracksUnfiltered`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L122) | yes |
| `CentralTrackSeedParameters` | `TrackSeeding_factory` (`CentralTrackSeeds`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L168) | yes |
| `CentralTrackSeeds` | `TrackSeeding_factory` (`CentralTrackSeeds`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L168) | yes |
| `CentralTrackSegments` | `TrackProjector_factory` (`CentralTrackSegments`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L224) | yes |
| `CentralTrackVertices` | `IterativeVertexFinder_factory` (`CentralTrackVertices`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L236) | yes |
| `CentralTrackerMeasurements` | `CollectionCollector_factory<Measurement2D, true>` (`CentralTrackerMeasurements`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L107) | yes |
| `CentralTrackerTruthSeeds` | `SubDivideCollection_factory<TrackSeed>` (`CentralB0TrackerTruthSeeds`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L58) | yes |
| `CentralTrackingRawHitAssociations` | `CollectionCollector_factory<MCRecoTrackerHitAssociation, true>` (`CentralTrackingRawHitAssociations`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L80) | yes |
| `CentralTrackingRawHitLinks` | `CollectionCollector_factory<MCRecoTrackerHitLink, true>` (`CentralTrackingRawHitLinks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L93) | yes |
| `CentralTrackingRecHits` | `CollectionCollector_factory<TrackerHit, true>` (`CentralTrackingRecHits`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L71) | yes |
| `CentralWithoutTOFTrackerMeasurements` | `TrackerMeasurementFromHits_factory` (`CentralWithoutTOFTrackerMeasurements`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L102) | yes |
| `CombinedTOFParticleIDs` | `PIDLookup_factory` (`CombinedTOFLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L110) | yes |
| `CombinedTOFTruthSeededParticleIDs` | `PIDLookup_factory` (`CombinedTOFTruthSeededLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L95) | yes |
| `CombinedTrackAssociations` | `CollectionCollector_factory<MCRecoTrackParticleAssociation, true>` (`CombinedTrackAssociations`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L491) | no |
| `CombinedTracks` | `CollectionCollector_factory<Track, true>` (`CombinedTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L463) | no |
| `CombinedTruthSeededTrackAssociations` | `CollectionCollector_factory<MCRecoTrackParticleAssociation, true>` (`CombinedTruthSeededTrackAssociations`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L500) | no |
| `CombinedTruthSeededTracks` | `CollectionCollector_factory<Track, true>` (`CombinedTruthSeededTracks`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L496) | no |
| `PrimaryVertices` | `PrimaryVertices_factory` (`PrimaryVertices`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L311) | yes |
| `PrimaryVerticesAMVF` | `SecondaryVertexFinder_factory` (`PrimaryVerticesAMVF`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L466) | yes |
| `SecondaryVerticesAMVF` | `SecondaryVertexFinder_factory` (`SecondaryVerticesAMVF`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L477) | yes |
| `SecondaryVerticesHelix` | `SecondaryVerticesHelix_factory` (`SecondaryVerticesHelix`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L314) | yes |

## DRICH*, RICHEndcapN*, DIRC* — Cherenkov PID

21 collections, 17 persisted by default.

| collection | producing factory (instance) | plugin | persisted |
|---|---|---|---|
| `DIRCParticleIDs` | `PIDLookup_factory` (`DIRCLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L169) | yes |
| `DIRCRawHits` | `PhotoMultiplierHitDigi_factory` (`DIRCRawHits`) | [DIRC](https://github.com/eic/EICrecon/blob/main/src/detectors/DIRC/DIRC.cc#L39) | yes |
| `DIRCRawHitsAssociations` | `PhotoMultiplierHitDigi_factory` (`DIRCRawHits`) | [DIRC](https://github.com/eic/EICrecon/blob/main/src/detectors/DIRC/DIRC.cc#L39) | no |
| `DIRCRawHitsLinks` | `PhotoMultiplierHitDigi_factory` (`DIRCRawHits`) | [DIRC](https://github.com/eic/EICrecon/blob/main/src/detectors/DIRC/DIRC.cc#L39) | no |
| `DIRCTruthSeededParticleIDs` | `PIDLookup_factory` (`DIRCTruthSeededLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L154) | yes |
| `DRICHAerogelIrtCherenkovParticleID` | `IrtCherenkovParticleID_factory` (`DRICHIrtCherenkovParticleID`) | [DRICH](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L137) | yes |
| `DRICHAerogelTracks` | `RichTrack_factory` (`DRICHAerogelTracks`) | [DRICH](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L124) | yes |
| `DRICHGasIrtCherenkovParticleID` | `IrtCherenkovParticleID_factory` (`DRICHIrtCherenkovParticleID`) | [DRICH](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L137) | yes |
| `DRICHGasTracks` | `RichTrack_factory` (`DRICHGasTracks`) | [DRICH](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L128) | yes |
| `DRICHMergedIrtCherenkovParticleID` | `MergeCherenkovParticleID_factory` (`DRICHMergedIrtCherenkovParticleID`) | [DRICH](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L144) | no |
| `DRICHMergedTracks` | `MergeTrack_factory` (`DRICHMergedTracks`) | [DRICH](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L132) | no |
| `DRICHParticleIDs` | `PIDLookup_factory` (`DRICHLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L262) | yes |
| `DRICHRawHits` | `PhotoMultiplierHitDigi_factory` (`DRICHRawHits`) | [DRICH](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L119) | yes |
| `DRICHRawHitsAssociations` | `PhotoMultiplierHitDigi_factory` (`DRICHRawHits`) | [DRICH](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L119) | yes |
| `DRICHRawHitsLinks` | `PhotoMultiplierHitDigi_factory` (`DRICHRawHits`) | [DRICH](https://github.com/eic/EICrecon/blob/main/src/detectors/DRICH/DRICH.cc#L119) | yes |
| `DRICHTruthSeededParticleIDs` | `PIDLookup_factory` (`DRICHTruthSeededLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L247) | yes |
| `RICHEndcapNParticleIDs` | `PIDLookup_factory` (`RICHEndcapNLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L62) | yes |
| `RICHEndcapNRawHits` | `PhotoMultiplierHitDigi_factory` (`RICHEndcapNRawHits`) | [PFRICH](https://github.com/eic/EICrecon/blob/main/src/detectors/PFRICH/PFRICH.cc#L51) | yes |
| `RICHEndcapNRawHitsAssociations` | `PhotoMultiplierHitDigi_factory` (`RICHEndcapNRawHits`) | [PFRICH](https://github.com/eic/EICrecon/blob/main/src/detectors/PFRICH/PFRICH.cc#L51) | yes |
| `RICHEndcapNRawHitsLinks` | `PhotoMultiplierHitDigi_factory` (`RICHEndcapNRawHits`) | [PFRICH](https://github.com/eic/EICrecon/blob/main/src/detectors/PFRICH/PFRICH.cc#L51) | yes |
| `RICHEndcapNTruthSeededParticleIDs` | `PIDLookup_factory` (`RICHEndcapNTruthSeededLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L47) | yes |

## Reconstructed*, Generated*, Inclusive*, Scattered* — physics level

75 collections, 43 persisted by default.

| collection | producing factory (instance) | plugin | persisted |
|---|---|---|---|
| `GeneratedBreitFrameParticles` | `TransformBreitFrame_factory` (`GeneratedBreitFrameParticles`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L284) | yes |
| `GeneratedCentauroJets` | `JetReconstruction_factory<ReconstructedParticle>` (`GeneratedCentauroJets`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L289) | yes |
| `GeneratedChargedJets` | `JetReconstruction_factory<ReconstructedParticle>` (`GeneratedChargedJets`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L173) | yes |
| `GeneratedChargedParticles` | `ChargedReconstructedParticleSelector_factory` (`GeneratedChargedParticles`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L164) | no |
| `GeneratedJets` | `JetReconstruction_factory<ReconstructedParticle>` (`GeneratedJets`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L157) | yes |
| `GeneratedParticles` | `MC2ReconstructedParticle_factory` (`GeneratedParticles`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L78) | yes |
| `HadronicFinalState` | `HadronicFinalState_factory<HadronicFinalState>` (`HadronicFinalState`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L278) | yes |
| `InclusiveKinematicsDA` | `InclusiveKinematicsReconstructed_factory<InclusiveKinematicsDA>` (`InclusiveKinematicsDA`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L124) | yes |
| `InclusiveKinematicsESigma` | `InclusiveKinematicsReconstructed_factory<InclusiveKinematicsESigma>` (`InclusiveKinematicsESigma`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L129) | yes |
| `InclusiveKinematicsElectron` | `InclusiveKinematicsReconstructed_factory<InclusiveKinematicsElectron>` (`InclusiveKinematicsElectron`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L111) | yes |
| `InclusiveKinematicsJB` | `InclusiveKinematicsReconstructed_factory<InclusiveKinematicsJB>` (`InclusiveKinematicsJB`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L118) | yes |
| `InclusiveKinematicsML` | `InclusiveKinematicsML_factory` (`InclusiveKinematicsML`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L146) | yes |
| `InclusiveKinematicsSigma` | `InclusiveKinematicsReconstructed_factory<InclusiveKinematicsSigma>` (`InclusiveKinematicsSigma`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L140) | yes |
| `InclusiveKinematicsTruth` | `InclusiveKinematicsTruth_factory` (`InclusiveKinematicsTruth`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L108) | yes |
| `InclusiveKinematicseSigma` | `CollectionCollector_factory<InclusiveKinematics>` (`InclusiveKinematicseSigma_legacy`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L136) | yes |
| `ReconstructedB0EcalNeutrals` | `FarForwardNeutralsReconstruction_factory` (`ReconstructedFarForwardNeutrals`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L242) | yes |
| `ReconstructedBreitFrameParticles` | `TransformBreitFrame_factory` (`ReconstructedBreitFrameParticles`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L237) | yes |
| `ReconstructedCentauroJets` | `JetReconstruction_factory<ReconstructedParticle>` (`ReconstructedCentauroJets`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L294) | yes |
| `ReconstructedChargedJets` | `JetReconstruction_factory<ReconstructedParticle>` (`ReconstructedChargedJets`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L177) | yes |
| `ReconstructedChargedParticleAssociations` | `PIDLookup_factory` (`DRICHLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L262) | yes |
| `ReconstructedChargedParticleLinks` | `PIDLookup_factory` (`DRICHLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L262) | yes |
| `ReconstructedChargedParticles` | `PIDLookup_factory` (`DRICHLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L262) | yes |
| `ReconstructedChargedRealPIDParticleAssociations` | `MatchToRICHPID_factory` (`ChargedParticlesWithAssociations`) | [pid](https://github.com/eic/EICrecon/blob/main/src/global/pid/pid.cc#L22) | no |
| `ReconstructedChargedRealPIDParticleIDs` | `MatchToRICHPID_factory` (`ChargedParticlesWithAssociations`) | [pid](https://github.com/eic/EICrecon/blob/main/src/global/pid/pid.cc#L22) | yes |
| `ReconstructedChargedRealPIDParticleLinks` | `MatchToRICHPID_factory` (`ChargedParticlesWithAssociations`) | [pid](https://github.com/eic/EICrecon/blob/main/src/global/pid/pid.cc#L22) | no |
| `ReconstructedChargedRealPIDParticles` | `MatchToRICHPID_factory` (`ChargedParticlesWithAssociations`) | [pid](https://github.com/eic/EICrecon/blob/main/src/global/pid/pid.cc#L22) | yes |
| `ReconstructedChargedWithPFRICHPIDParticleAssociations` | `PIDLookup_factory` (`RICHEndcapNLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L62) | no |
| `ReconstructedChargedWithPFRICHPIDParticleLinks` | `PIDLookup_factory` (`RICHEndcapNLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L62) | no |
| `ReconstructedChargedWithPFRICHPIDParticles` | `PIDLookup_factory` (`RICHEndcapNLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L62) | no |
| `ReconstructedChargedWithPFRICHTOFDIRCLOWQ2PIDParticleAssociations` | `CollectionCollector_factory<MCRecoParticleAssociation, true>` (`ReconstructedChargedWithPFRICHTOFDIRCLOWQ2PIDParticleAssociations`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L195) | no |
| `ReconstructedChargedWithPFRICHTOFDIRCPIDParticleAssociations` | `PIDLookup_factory` (`DIRCLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L169) | no |
| `ReconstructedChargedWithPFRICHTOFDIRCPIDParticleLinks` | `PIDLookup_factory` (`DIRCLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L169) | no |
| `ReconstructedChargedWithPFRICHTOFDIRCPIDParticles` | `PIDLookup_factory` (`DIRCLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L169) | no |
| `ReconstructedChargedWithPFRICHTOFPIDParticleAssociations` | `PIDLookup_factory` (`CombinedTOFLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L110) | no |
| `ReconstructedChargedWithPFRICHTOFPIDParticleLinks` | `PIDLookup_factory` (`CombinedTOFLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L110) | no |
| `ReconstructedChargedWithPFRICHTOFPIDParticles` | `PIDLookup_factory` (`CombinedTOFLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L110) | no |
| `ReconstructedChargedWithoutPIDParticleAssociations` | `TracksToParticles_factory` (`ChargedParticlesWithAssociations`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L517) | no |
| `ReconstructedChargedWithoutPIDParticleLinks` | `TracksToParticles_factory` (`ChargedParticlesWithAssociations`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L517) | no |
| `ReconstructedChargedWithoutPIDParticles` | `TracksToParticles_factory` (`ChargedParticlesWithAssociations`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L517) | no |
| `ReconstructedEcalEndcapPNeutrals` | `FarForwardNeutralsReconstruction_factory` (`ReconstructedFarForwardNeutrals`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L242) | yes |
| `ReconstructedElectrons` | `ReconstructedElectrons_factory` (`ReconstructedElectrons`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L150) | yes |
| `ReconstructedElectronsForDIS` | `ReconstructedElectrons_factory` (`ReconstructedElectronsForDIS`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L153) | no |
| `ReconstructedHcalFarForwardZDCNeutrals` | `FarForwardNeutralsReconstruction_factory` (`ReconstructedFarForwardNeutrals`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L242) | yes |
| `ReconstructedJets` | `JetReconstruction_factory<ReconstructedParticle>` (`ReconstructedJets`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L160) | yes |
| `ReconstructedLFHCALNeutrals` | `FarForwardNeutralsReconstruction_factory` (`ReconstructedFarForwardNeutrals`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L242) | yes |
| `ReconstructedLambdaDecayProductsCM` | `LambdaReconstruction_factory` (`ReconstructedLambdas`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L266) | yes |
| `ReconstructedLambdas` | `LambdaReconstruction_factory` (`ReconstructedLambdas`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L266) | yes |
| `ReconstructedNeutralJets` | `JetReconstruction_factory<ReconstructedParticle>` (`ReconstructedNeutralJets`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L181) | yes |
| `ReconstructedNeutralParticleAssociations` | `ClustersToParticles_factory` (`ReconstructedNeutralParticles`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L167) | yes |
| `ReconstructedNeutralParticleLinks` | `ClustersToParticles_factory` (`ReconstructedNeutralParticles`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L167) | yes |
| `ReconstructedNeutralParticles` | `ClustersToParticles_factory` (`ReconstructedNeutralParticles`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L167) | yes |
| `ReconstructedParticleAssociations` | `MatchClusters_factory` (`ReconstructedParticlesWithAssoc`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L92) | yes |
| `ReconstructedParticleLinks` | `MatchClusters_factory` (`ReconstructedParticlesWithAssoc`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L92) | yes |
| `ReconstructedParticles` | `MatchClusters_factory` (`ReconstructedParticlesWithAssoc`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L92) | yes |
| `ReconstructedTruthSeededChargedParticleAssociations` | `PIDLookup_factory` (`DRICHTruthSeededLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L247) | yes |
| `ReconstructedTruthSeededChargedParticleLinks` | `PIDLookup_factory` (`DRICHTruthSeededLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L247) | yes |
| `ReconstructedTruthSeededChargedParticles` | `PIDLookup_factory` (`DRICHTruthSeededLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L247) | yes |
| `ReconstructedTruthSeededChargedWithPFRICHPIDParticleAssociations` | `PIDLookup_factory` (`RICHEndcapNTruthSeededLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L47) | no |
| `ReconstructedTruthSeededChargedWithPFRICHPIDParticleLinks` | `PIDLookup_factory` (`RICHEndcapNTruthSeededLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L47) | no |
| `ReconstructedTruthSeededChargedWithPFRICHPIDParticles` | `PIDLookup_factory` (`RICHEndcapNTruthSeededLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L47) | no |
| `ReconstructedTruthSeededChargedWithPFRICHTOFDIRCLOWQ2PIDParticleAssociations` | `CollectionCollector_factory<MCRecoParticleAssociation, true>` (`ReconstructedTruthSeededChargedWithPFRICHTOFDIRCLOWQ2PIDParticleAssociations`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L211) | no |
| `ReconstructedTruthSeededChargedWithPFRICHTOFDIRCLOWQ2PIDParticles` | `CollectionCollector_factory<ReconstructedParticle, true>` (`ReconstructedTruthSeededChargedWithPFRICHTOFDIRCLOWQ2PIDParticles`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L205) | no |
| `ReconstructedTruthSeededChargedWithPFRICHTOFDIRCPIDParticleAssociations` | `PIDLookup_factory` (`DIRCTruthSeededLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L154) | no |
| `ReconstructedTruthSeededChargedWithPFRICHTOFDIRCPIDParticleLinks` | `PIDLookup_factory` (`DIRCTruthSeededLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L154) | no |
| `ReconstructedTruthSeededChargedWithPFRICHTOFDIRCPIDParticles` | `PIDLookup_factory` (`DIRCTruthSeededLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L154) | no |
| `ReconstructedTruthSeededChargedWithPFRICHTOFPIDParticleAssociations` | `PIDLookup_factory` (`CombinedTOFTruthSeededLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L95) | no |
| `ReconstructedTruthSeededChargedWithPFRICHTOFPIDParticleLinks` | `PIDLookup_factory` (`CombinedTOFTruthSeededLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L95) | no |
| `ReconstructedTruthSeededChargedWithPFRICHTOFPIDParticles` | `PIDLookup_factory` (`CombinedTOFTruthSeededLUTPID`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L95) | no |
| `ReconstructedTruthSeededChargedWithoutPIDParticleAssociations` | `TracksToParticles_factory` (`ChargedTruthSeededParticlesWithAssociations`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L506) | no |
| `ReconstructedTruthSeededChargedWithoutPIDParticleLinks` | `TracksToParticles_factory` (`ChargedTruthSeededParticlesWithAssociations`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L506) | no |
| `ReconstructedTruthSeededChargedWithoutPIDParticles` | `TracksToParticles_factory` (`ChargedTruthSeededParticlesWithAssociations`) | [tracking](https://github.com/eic/EICrecon/blob/main/src/global/tracking/tracking.cc#L506) | no |
| `ReconstructedWithPFRICHTOFDIRCLOWQ2PIDChargedParticles` | `CollectionCollector_factory<ReconstructedParticle, true>` (`ReconstructedWithPFRICHTOFDIRCLOWQ2PIDChargedParticles`) | [pid_lut](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc#L189) | no |
| `ScatteredElectronsEMinusPz` | `ScatteredElectronsEMinusPz_factory` (`ScatteredElectronsEMinusPz`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L190) | yes |
| `ScatteredElectronsEMinusPzByPt` | `SortSubsetCollection_factory<ReconstructedParticle, reco_particle_pt>` (`ScatteredElectronsEMinusPzByPt`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L200) | yes |
| `ScatteredElectronsTruth` | `ScatteredElectronsTruth_factory` (`ScatteredElectronsTruth`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L185) | yes |

## MC* and EventHeader — truth record

14 collections, 11 persisted by default.

| collection | producing factory (instance) | plugin | persisted |
|---|---|---|---|
| `EventHeader` | (simulation input) | — | yes |
| `MCBeamElectrons` | `SubDivideCollection_factory<MCParticle>` (`BeamParticles`) | [beam](https://github.com/eic/EICrecon/blob/main/src/global/beam/beam.cc#L35) | yes |
| `MCBeamHadrons` | `CollectionCollector_factory<MCParticle, true>` (`MCBeamHadrons`) | [beam](https://github.com/eic/EICrecon/blob/main/src/global/beam/beam.cc#L45) | no |
| `MCBeamNeutrons` | `SubDivideCollection_factory<MCParticle>` (`BeamParticles`) | [beam](https://github.com/eic/EICrecon/blob/main/src/global/beam/beam.cc#L35) | no |
| `MCBeamProtons` | `SubDivideCollection_factory<MCParticle>` (`BeamParticles`) | [beam](https://github.com/eic/EICrecon/blob/main/src/global/beam/beam.cc#L35) | yes |
| `MCNonScatteredElectronAssociations` | `FilterMatching_factory< MCRecoParticleAssociation, lambda, MCParticle, lambda>` (`MCScatteredElectronAssociations`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L71) | yes |
| `MCNonScatteredElectronLinks` | `FilterMatching_factory< MCRecoParticleLink, lambda, MCParticle, lambda>` (`MCScatteredElectronLinks`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L65) | yes |
| `MCParticles` | (simulation input) | — | yes |
| `MCParticlesHeadOnFrameNoBeamFX` | `UndoAfterBurnerMCParticles_factory` (`MCParticlesHeadOnFrameNoBeamFX`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L300) | yes |
| `MCScatteredElectronAssociations` | `FilterMatching_factory< MCRecoParticleAssociation, lambda, MCParticle, lambda>` (`MCScatteredElectronAssociations`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L71) | yes |
| `MCScatteredElectronLinks` | `FilterMatching_factory< MCRecoParticleLink, lambda, MCParticle, lambda>` (`MCScatteredElectronLinks`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L65) | yes |
| `MCScatteredElectrons` | `SubDivideCollection_factory<MCParticle>` (`BeamParticles`) | [beam](https://github.com/eic/EICrecon/blob/main/src/global/beam/beam.cc#L35) | yes |
| `MCScatteredNeutrons` | `SubDivideCollection_factory<MCParticle>` (`BeamParticles`) | [beam](https://github.com/eic/EICrecon/blob/main/src/global/beam/beam.cc#L35) | no |
| `MCScatteredProtons` | `SubDivideCollection_factory<MCParticle>` (`BeamParticles`) | [beam](https://github.com/eic/EICrecon/blob/main/src/global/beam/beam.cc#L35) | yes |

## Other

10 collections, 5 persisted by default.

| collection | producing factory (instance) | plugin | persisted |
|---|---|---|---|
| `BarrelChargedCandidateParticlesAlpha` | `ChargedCandidateMaker_factory` (`BarrelChargedCandidateParticlesAlpha`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L214) | yes |
| `BarrelClusters` | (unresolved — no producer found) | — | yes |
| `BarrelTrackClusterMatches` | `CollectionCollector_factory<TrackClusterMatch, false>` (`BarrelTrackClusterMatches`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L209) | no |
| `EcalClusterAssociations` | `CollectionCollector_factory<MCRecoClusterParticleAssociation, true>` (`EcalClusterAssociations`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L85) | no |
| `EcalClusters` | `CollectionCollector_factory<Cluster, true>` (`EcalClusters`) | [reco](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L81) | no |
| `EndcapNChargedCandidateParticlesAlpha` | `ChargedCandidateMaker_factory` (`EndcapNChargedCandidateParticlesAlpha`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L202) | yes |
| `EndcapNTrackClusterMatches` | `CollectionCollector_factory<TrackClusterMatch, false>` (`EndcapNTrackClusterMatches`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L197) | no |
| `EndcapPChargedCandidateParticlesAlpha` | `ChargedCandidateMaker_factory` (`EndcapPChargedCandidateParticlesAlpha`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L227) | yes |
| `EndcapPInsertChargedCandidateParticlesAlpha` | (unresolved — no producer found) | — | yes |
| `EndcapPTrackClusterMatches` | `CollectionCollector_factory<TrackClusterMatch, false>` (`EndcapPTrackClusterMatches`) | [particle_flow](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L221) | no |

## Caveats

**Persisted names that no factory produces (22).** Fifteen of them are
Geant4/DD4hep *simulation input* collections that arrive with the input file
rather than being produced by EICrecon, and are marked `(simulation input)`:
`EventHeader`, `MCParticles`, `SiBarrelHits`, `VertexBarrelHits`,
`TrackerEndcapHits`, `TOFBarrelHits`, `TOFEndcapHits`, `MPGDBarrelHits`,
`OuterMPGDBarrelHits`, `BackwardMPGDEndcapHits`, `ForwardMPGDEndcapHits`,
`TaggerTrackerHits`, `B0TrackerHits`, `ForwardRomanPotHits`,
`ForwardOffMTrackerHits`. (Their exact names are fixed by the `epic` geometry
readouts, not by EICrecon.)

The remaining **seven look like stale entries in the persist list** — they
match nothing in the factory set and would trigger the "Explicitly included
collection … not present in factory set, omitting" warning:

| persisted name | line | apparent situation |
|---|---|---|
| `TOFBarrelRawHitLinks` | [L122](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L122) | the real tag is `TOFBarrelSharedRawHitLinks` (also listed) |
| `TOFBarrelRawHitAssociations` | [L123](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L123) | the real tag is `TOFBarrelSharedRawHitAssociations` (also listed) |
| `TOFEndcapRawHitLinks` | [L124](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L124) | the real tag is `TOFEndcapSharedRawHitLinks` (also listed) |
| `TOFEndcapRawHitAssociations` | [L125](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L125) | the real tag is `TOFEndcapSharedRawHitAssociations` (also listed) |
| `BarrelClusters` | [L330](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L330) | no producer anywhere in `src/`; purpose unknown |
| `HcalEndcapPInsertClusterMatches` | [L479](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L479) | this is the *instance* name; the factory's output tag is `HcalEndcapPInsertTrackClusterMatches` ([reco.cc#L214-L217](https://github.com/eic/EICrecon/blob/main/src/global/reco/reco.cc#L214-L217)), which is **not** in the persist list — so the forward-insert track/cluster matches are effectively not written |
| `EndcapPInsertChargedCandidateParticlesAlpha` | [L522](https://github.com/eic/EICrecon/blob/main/src/services/io/podio/JEventProcessorPODIO.cc#L522) | particle flow registers only the `EndcapN`, `Barrel` and `EndcapP` variants ([particle_flow.cc#L203-L229](https://github.com/eic/EICrecon/blob/main/src/global/particle_flow/particle_flow.cc#L203-L229)) |

I have not verified with a maintainer that these are genuinely dead; they may
be placeholders for work in progress.

**No wildcards in the default persist list.** All 411 entries are plain
literal names — none contains a regex metacharacter — even though the code
path treats them as regexes. So the join is an exact string match and nothing
was matched fuzzily.

**Collections with two producers (11).** These are registered twice inside
mutually exclusive `if`/`else` branches, so exactly one producer is live per
run; the table shows both joined with **or**.

- `EcalEndcapPRawHits`, `EcalEndcapPRawHitLinks`, `EcalEndcapPRawHitAssociations`
  — two `CalorimeterHitDigi_factory` configurations selected by the DD4hep
  constant `EcalEndcapP_Homogeneous_ScFi`
  ([FEMC.cc#L55-L110](https://github.com/eic/EICrecon/blob/main/src/detectors/FEMC/FEMC.cc#L55-L110)).
  The table shows the second (ScFi) registration's line for both.
- `MPGDBarrel*` and `OuterMPGDBarrel*` raw/rec hits — `SiliconTrackerDigi_factory`
  vs `MPGDTrackerDigi_factory`, and `TrackerHitReconstruction_factory` vs
  `MPGDHitReconstruction_factory`, selected by the `SiFactoryPattern` bitmask
  ([MPGD.cc#L110-L200](https://github.com/eic/EICrecon/blob/main/src/detectors/MPGD/MPGD.cc#L110-L200)).

**Names built programmatically.** Four registrations pass a
`std::vector<std::string>` variable instead of a brace-literal, so the names
had to be resolved by reading the loop that fills it. All four were resolved
by hand and are listed with concrete names; the resolutions are:

| registration | resolved to |
|---|---|
| `BeamParticles` ([beam.cc#L35](https://github.com/eic/EICrecon/blob/main/src/global/beam/beam.cc#L35)) | `MCBeam{Electrons,Protons,Neutrons}`, `MCScattered{Electrons,Protons,Neutrons}` |
| `TaggerTrackerSplitHits` ([LOWQ2.cc#L138](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L138)) | `TaggerTrackerM{1,2}L{0,1,2,3}RecHits` (8) |
| `TaggerTrackerClustering` ([LOWQ2.cc#L145](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L145)) | `TaggerTrackerM{1,2}L{0,1,2,3}ClusterPositions` (8) |
| `FarDetectorLinearTracking`, registered in a loop over `moduleIDs = {1, 2}` ([LOWQ2.cc#L165](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc#L165)) | `TaggerTrackerM{1,2}LocalTrack{s,Links,Associations}` (6) |

The module and layer ranges (`moduleIDs = {1, 2}`, `layerIDs = {0..3}`) are
hard-coded in `LOWQ2.cc`, not read from geometry, so those 22 names are stable
at this commit but would change if the loop bounds changed. **Zero** output
tags remain statically unresolved after these substitutions.

**Scope of the scan.** Only `src/detectors/*/*.cc` (22 files) and
`src/global/*/*.cc` (6 files) were parsed. `JOmniFactoryGeneratorT` is the
only registration template used in those files — there are no
`JFactoryGeneratorT` or `JChainMultifactoryGeneratorT` registrations left in
the plugin sources at this commit. One further registration lives in
`src/tests/tracking_test/tracking_test.cc` and is **excluded** here (it is a
test harness, not a production plugin). Headers under `src/factories/` were
not scanned, since collection names are supplied at registration, not in the
factory class.

**What the "persisted" column does not tell you.** It is a static join. It
does not know whether a given detector plugin is loaded, whether the geometry
provides the readout a factory needs, or whether a conditional branch is
taken. A `yes` therefore means "in the default include list", not "guaranteed
present in your output file". For the ground truth of a particular
reconstruction configuration, dump the collections in the produced ROOT file.

**Grouping is cosmetic.** Groups are assigned by name prefix on a first-match
basis, so a few collections sit under a detector heading although they are
produced by a global plugin — for example `EcalBarrelCalorimeterTrackProjections`
appears under `EcalBarrel*` but is produced by `particle_flow`, and
`LFHCALTrackProjections` appears under the forward-HCal group for the same
reason. The plugin column is always the truth.

---

*Generated from [eic/EICrecon](https://github.com/eic/EICrecon) @ `3319124`
(fetched 2026-08-19). AI-authored draft — verify against source.*
