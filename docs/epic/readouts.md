---
title: Readouts and segmentation
parent: ePIC geometry
nav_order: 2
source: eic/epic
source_commit: 216e4c2fd73411ebb79a340fab95ae08e74e294b
generated: 2026-08-19
status: draft
---

# Readouts, segmentation and cellIDs

{: .warning }
AI-generated draft derived from the ePIC geometry description at commit
[`216e4c2`](https://github.com/eic/epic/commit/216e4c2fd73411ebb79a340fab95ae08e74e294b).
Every claim links to the exact file — verify there before depending on it.

A **readout** is the contract between geometry and reconstruction. It declares
the name of the hit collection, how a cell's position is turned into an integer
index, and the bit layout of the 64-bit `cellID` carried by every simulated hit.
EICrecon never hard-codes that layout — it asks DD4hep for it by readout name.

## Anatomy of a `<readout>` block

Readouts live in a `<readouts>` element at the bottom of each subsystem's
compact XML, and are bound to a detector by the `readout="..."` attribute on
the `<detector>` element.

```xml
<readouts>
  <readout name="EcalBarrelScFiHits">
    <segmentation type="CartesianStripZ" strip_size_x="1.0*cm" identifier_x="z"/>
    <id>system:8,sector:6,layer:6,slice:4,grid:10,fiber:16,z:-14</id>
  </readout>
</readouts>
```
([`compact/ecal/bic/bic.xml`, lines 420–423](https://github.com/eic/epic/blob/main/compact/ecal/bic/bic.xml#L420-L423))

Two children:

- **`<id>`** — the *bitfield descriptor*, parsed by DD4hep's `BitFieldCoder`.
  Comma-separated `name:width` or `name:offset:width` entries. A **negative
  width means the field is signed**; offsets, when omitted, continue from the
  previous field. The total must fit in 64 bits.
- **`<segmentation>`** — the rule that maps a local position inside a sensitive
  volume onto the *segmentation* fields of the bitfield.

The remaining fields are **volume ID** fields, filled by DD4hep from the placed
volume hierarchy via `addPhysVolID` calls in the C++ plugin. Two different
mechanisms fill one integer:

| field kind | filled by | example |
|---|---|---|
| volume ID | `addPhysVolID("layer", l_num)` in the plugin | `system`, `sector`, `layer`, `slice`, `stave`, `module`, `sensor`, `grid`, `fiber` |
| segmentation | the `<segmentation>` object, from the hit's local position | `x`, `y`, `z`, `phi` |

## Example 1 — barrel ECal ScFi (`EcalBarrelScFiHits`)

```
system:8, sector:6, layer:6, slice:4, grid:10, fiber:16, z:-14
```

| field | width | bits | signed | meaning | filled by |
|---|---|---|---|---|---|
| `system` | 8 | 0–7 | no | detector ID (`EcalBarrel2_ID`) | [`env_phv.addPhysVolID("system", det_id)`](https://github.com/eic/epic/blob/main/src/BarrelCalorimeterScFi_geo.cpp#L86) |
| `sector` | 6 | 8–13 | no | azimuthal sector (1…`EcalBarrel_SectorRepeat`) | [line 185](https://github.com/eic/epic/blob/main/src/BarrelCalorimeterScFi_geo.cpp#L185) |
| `layer` | 6 | 14–19 | no | radial Pb/ScFi layer | [line 168](https://github.com/eic/epic/blob/main/src/BarrelCalorimeterScFi_geo.cpp#L168) |
| `slice` | 4 | 20–23 | no | sub-layer material slice | [line 157](https://github.com/eic/epic/blob/main/src/BarrelCalorimeterScFi_geo.cpp#L157) |
| `grid` | 10 | 24–33 | no | flattened 2-D fibre-grid index, `ix + iy*grid_n_phi + 1` | [line 290](https://github.com/eic/epic/blob/main/src/BarrelCalorimeterScFi_geo.cpp#L290) |
| `fiber` | 16 | 34–49 | no | individual fibre within the grid | [line 279](https://github.com/eic/epic/blob/main/src/BarrelCalorimeterScFi_geo.cpp#L279) |
| `z` | 14 | 50–63 | **yes** | 1 cm strip index along the fibre | the `CartesianStripZ` segmentation |

Segmentation:
`<segmentation type="CartesianStripZ" strip_size_x="1.0*cm" identifier_x="z"/>`
— a one-dimensional strip segmentation of pitch **1 cm**, whose index is stored
in the field named by `identifier_x`, here `z`. (The DD4hep `CartesianStrip*`
family uses the parameter name `strip_size_x` for its single axis regardless of
which axis the type selects.)

So `z` is the *only* segmentation-derived field: the fibre and its grid cell are
real placed volumes, while the longitudinal position along the fibre is a
virtual 1 cm binning laid over the continuous fibre length.

{: .note }
This is exactly why EICrecon's BEMC configuration keeps referring to
`{"fiber", "z"}`. In
[`SimCalorimeterHitProcessor`]({% link docs/eicrecon/detectors/bemc.md %})
`hitMergeFields = {"fiber","z"}` merges the z-segments back together after
attenuation, `contributionMergeFields = {"fiber"}` merges per-fibre, and in
`CalorimeterHitReco` `maskPosFields = {"fiber","z"}` with `maskPos = "xy"`
takes x/y from the masked (grid-centre) cell but keeps the finely segmented z.
None of those names exist anywhere in EICrecon — they are read out of this
`<id>` string at runtime.

The companion imaging readout in the same file
([lines 416–419](https://github.com/eic/epic/blob/main/compact/ecal/bic/bic.xml#L416-L419)):

```xml
<readout name="EcalBarrelImagingHits">
  <segmentation type="CartesianGridXY" grid_size_x="0.5 * mm" grid_size_y="0.5 * mm"/>
  <id>system:8,sector:6,layer:4,stave:4,module:8,slice:2,x:32:-16,y:-16</id>
</readout>
```

Here `x` and `y` are both signed 16-bit **bin indices** of a 0.5 mm Cartesian
grid in the sensor's local frame, not coordinates. `x:32:-16` states the offset
explicitly; since `8+6+4+4+8+2 = 32`, it is contiguous with the volume fields.

## Example 2 — vertex barrel tracker (`VertexBarrelHits`)

```xml
<readout name="VertexBarrelHits">
  <segmentation type="MultiSegmentation" key="layer">
    <segmentation name="L0" type="CylindricalGridPhiZ" key_value="0"
      grid_size_phi="0.02*mm/VertexBarrelSegL0_r" grid_size_z="0.02*mm"
      radius="VertexBarrelSegL0_r" />
    <segmentation name="L1" type="CylindricalGridPhiZ" key_value="1"
      grid_size_phi="0.02*mm/VertexBarrelSegL1_r" grid_size_z="0.02*mm"
      radius="VertexBarrelSegL1_r" />
    <segmentation name="L2" type="CylindricalGridPhiZ" key_value="2"
      grid_size_phi="0.02*mm/VertexBarrelSegL2_r" grid_size_z="0.02*mm"
      radius="VertexBarrelSegL2_r" />
  </segmentation>
  <id>system:8,layer:4,module:12,sensor:4,phi:32:-16,z:-16</id>
</readout>
```
([`compact/tracking/vertex_barrel.xml`, lines 225–239](https://github.com/eic/epic/blob/main/compact/tracking/vertex_barrel.xml#L225-L239))

| field | width | bits | signed | meaning |
|---|---|---|---|---|
| `system` | 8 | 0–7 | no | detector ID (`VertexBarrel_0_ID`) |
| `layer` | 4 | 8–11 | no | barrel layer 0/1/2 |
| `module` | 12 | 12–23 | no | one complete RSU (Repeated Sensor Unit) |
| `sensor` | 4 | 24–27 | no | sensor within the module |
| `phi` | 16 | 32–47 | **yes** | azimuthal pixel index |
| `z` | 16 | 48–63 | **yes** | longitudinal pixel index |

{: .note }
Bits 28–31 are **unused** — the explicit `phi:32:-16` offset leaves a four-bit
gap after `sensor`, deliberately reserving room to widen the volume fields
without renumbering the segmentation fields.

Two things make this readout instructive:

**`MultiSegmentation`** dispatches on the value of another field. `key="layer"`
means: look at the `layer` field, then apply the child segmentation whose
`key_value` matches. One readout, three different segmentation objects — needed
here because the layers sit at different radii.

**Radius-normalised φ pitch.** `grid_size_phi="0.02*mm/VertexBarrelSegL0_r"`
is an angular bin size expressed as *arc length ÷ radius*. Combined with
`grid_size_z="0.02*mm"`, every layer gets the same physical **20 µm × 20 µm**
pixel pitch despite different radii. The `radius=` attribute tells the
`CylindricalGridPhiZ` segmentation which cylinder to place cell centres on.

Contrast with the ScFi readout: a tracker's segmentation fields (`phi`, `z`)
carry nearly all the position information and the volume fields are coarse,
whereas a sampling calorimeter's position is dominated by volume fields
(`sector`, `layer`, `grid`, `fiber`) with only one segmentation axis.

## How a cellID encodes position, and how EICrecon decodes it

**Encoding (simulation).** When Geant4 registers a step in a sensitive volume,
DD4hep builds the cellID by OR-ing together (a) the volume IDs accumulated
along the placement path from the world down to the sensitive volume, and (b)
the segmentation indices computed from the step's local position. The result is
one 64-bit integer that uniquely names a cell.

**Decoding (reconstruction).** EICrecon asks the geometry service for the same
`IDDescriptor` by readout name and uses its decoder:

```cpp
id_spec = m_detector->readout(m_cfg.readout).idSpec();   // CalorimeterHitReco.cc:65
id_dec  = id_spec.decoder();                             //                    :72
...
layer = id_dec->get(cellID, layer_idx);                  //                    :193
```
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L65-L72))

Field *names* are resolved to *indices* once at initialisation
(`id_dec->index("fiber")`), so a field named in a config but absent from the
`<id>` string is a startup error, not a silent zero — see
[`EdepToNpeConversion.cc:52-58`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EdepToNpeConversion.cc#L52-L58).

Going back from cellID to a **position** requires the geometry, not just the
bitfield. EICrecon uses DD4hep's `CellIDPositionConverter`:

```cpp
gpos = m_converter->position(cellID);                       // CalorimeterHitReco.cc:212
...
auto mpos = m_converter->position(cellID & ~gpos_mask);     //                    :216
```
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/CalorimeterHitReco.cc#L212-L218))

The second line is the `maskPos` trick: clearing the bits of the
`maskPosFields` yields the cellID of the *containing* coarser cell, whose
centre is used for the masked coordinates. That is how the BEMC takes x/y from
the fibre-grid centre while keeping the segmented z.

{: .important }
A consequence worth internalising: **the readout name in an EICrecon config is
a geometry lookup key**, and the field names in its parameter lists are strings
resolved against this XML. Renaming a field in `eic/epic`, or changing a width,
silently changes every cellID and breaks reconstruction at runtime rather than
at compile time. Geometry and reconstruction versions must be kept in step.

## Where sampling fractions and calibration files come from

### The `bic_edepToNpe_layer.lut` question — resolved

EICrecon's [BEMC page]({% link docs/eicrecon/detectors/bemc.md %}) notes that
`EdepToNpeConversion` is configured with
`edep_to_npe_filename = "calibrations/bic_edepToNpe_layer.lut"`, that the
algorithm throws if it cannot open the file
([`EdepToNpeConversion.cc:62-65`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EdepToNpeConversion.cc#L62-L65)),
and that the file is **not in the EICrecon repository**.

It is declared in `eic/epic`. From
[`compact/calibrations.xml`, lines 87–91](https://github.com/eic/epic/blob/main/compact/calibrations.xml#L87-L91):

```xml
<plugin name="epic_FileLoader">
  <arg value="cache:$DETECTOR_CACHE:/opt/detector"/>
  <arg value="file:calibrations/bic_edepToNpe_layer.lut"/>
  <arg value="url:https://raw.githubusercontent.com/eic/epic-data/60925f0113301310929f53e52783062fc40e45e3/bic_edepToNpe_layer.lut"/>
</plugin>
```

The full resolution chain:

1. The LUT **data** lives in a separate repository,
   [`eic/epic-data`](https://github.com/eic/epic-data), pinned to commit
   `60925f0`.
2. `compact/calibrations.xml` is included unconditionally by every generated
   configuration
   ([template line 64](https://github.com/eic/epic/blob/main/templates/epic.xml.jinja2#L64)),
   so loading *any* `epic_*.xml` triggers the download.
3. The [`epic_FileLoader`](https://github.com/eic/epic/blob/main/src/FileLoader.cpp#L67)
   plugin looks for the file in `$DETECTOR_CACHE`, then `/opt/detector` (keyed
   by a hash of the URL), and downloads it with `curl` if absent.
4. It is materialised at the **relative** path `calibrations/bic_edepToNpe_layer.lut`
   ([`FileLoaderHelper.h:57`](https://github.com/eic/epic/blob/main/src/FileLoaderHelper.h#L57)),
   i.e. relative to the working directory of the process that loaded the geometry.
5. EICrecon opens that same relative path with a plain `std::ifstream`
   ([`EdepToNpeConversion.cc:62-65`](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/EdepToNpeConversion.cc#L62-L65)).

**So the two processes agree only because both use the same relative path from
the same working directory.** If EICrecon runs from a directory where the
geometry's FileLoader never ran (or that is not writable), the LUT is missing
and `EdepToNpeConversion` throws. In the standard eic-shell/container workflow
`$DETECTOR_CACHE` points at a pre-populated `/opt/detector`, which is what makes
this work in practice.

The same pattern explains every other `calibrations/…` string in EICrecon —
each has a matching `epic_FileLoader` entry in `compact/calibrations.xml`:

| EICrecon consumer | file |
|---|---|
| [`BEMC.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/BEMC/BEMC.cc) | `calibrations/bic_edepToNpe_layer.lut`, `calibrations/onnx/EcalBarrel_pi_rejection.onnx` |
| [`EEMC.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/EEMC/EEMC.cc) | `calibrations/onnx/EcalEndcapN_pi_rejection.onnx` |
| [`LOWQ2.cc`](https://github.com/eic/EICrecon/blob/main/src/detectors/LOWQ2/LOWQ2.cc) | `calibrations/onnx/Low-Q2_Steering_Reconstruction.onnx` |
| [`pid_lut.cc`](https://github.com/eic/EICrecon/blob/main/src/global/pid_lut/pid_lut.cc) | `calibrations/drich.lut.gz`, `hpdirc.lut.gz`, `pfrich.lut`, `tof.lut` |
| [`PolynomialMatrixReconstruction.cc`](https://github.com/eic/EICrecon/blob/main/src/algorithms/fardetectors/PolynomialMatrixReconstruction.cc) | `calibrations/RP_60_xL_100_beamEnergy_*.xL.lut` |

Field maps use the same machinery via `url=`/`cache=` attributes — see
[Repository structure]({% link docs/epic/structure.md %}#downloaded-blobs-fieldmaps-and-calibrations).

### Sampling fractions — *not* resolved the same way

The tracked
[`calibrations/`](https://github.com/eic/epic/tree/main/calibrations) directory
does contain barrel ECal sampling fractions, in
[`emcal_barrel_calibration.json`](https://github.com/eic/epic/blob/main/calibrations/emcal_barrel_calibration.json):

```json
{
  "electron": {
    "particle_name": "electron",
    "sampling_fraction": 0.10856976476514045,
    "sampling_fraction_img": 0.00595078393326404,
    "sampling_fraction_scfi": 0.10262666247845109,
    "thrown_energy": 4.975791477972636
  }
}
```

{: .warning }
**These are not the numbers EICrecon uses.** EICrecon's BEMC plugin hard-codes
`sampFrac = "0.09285755"` (ScFi) and `"0.00429453"` (imaging), which differ from
`0.10262666…` and `0.00595078…` here. A code search for `emcal_barrel_calibration`
and `calo_digi_default` across the `eic` organisation returns **no consumers**.
The same applies to
[`calo_digi_default.json`](https://github.com/eic/epic/blob/main/calibrations/calo_digi_default.json),
whose `ecal_barrel_scfi` entry (`dynamicRange: 750*MeV`, `pedestalMean: 20`)
does not match EICrecon's BEMC digitisation config (`dyRangeADC = 1500 MeV`,
`pedMeanADC = 100`) either.

Read that as: these JSONs appear to be **stale or aspirational** — a
calibration interface that was intended but is not currently wired up.
Sampling fractions in production reconstruction come from hard-coded constants
in EICrecon, with no provenance comment in either repository. Determining which
of the two sets is correct for a given geometry version needs a maintainer.

### Sampling-fraction *studies* in the geometry repo

Two artefacts in `eic/epic` exist to *measure* sampling fractions rather than
store them:
[`compact/hcal/backward_sampF.xml`](https://github.com/eic/epic/blob/main/compact/hcal/backward_sampF.xml)
and the configuration
[`backward_hcal_only_sampF.yml`](https://github.com/eic/epic/blob/main/configurations/backward_hcal_only_sampF.yml)
that builds a geometry variant for that purpose. There is no equivalent
mechanism that feeds the resulting number back into reconstruction
automatically.

## Caveats / needs human verification

1. The `CartesianStripZ` parameter `strip_size_x` naming the *z* axis is a
   DD4hep convention read from the type name; confirmed only by the parameter
   set present in the XML, not by reading DD4hep source.
2. Whether the 4-bit gap at bits 28–31 of `VertexBarrelHits` is intentional
   reservation or an artefact of an earlier layout is inferred, not documented.
3. The mismatch between `calibrations/emcal_barrel_calibration.json` and
   EICrecon's hard-coded sampling fractions is stated as observed fact; **which
   value is correct is unresolved** and should be raised with the calorimetry
   group.
4. The working-directory dependence of the downloaded LUT path is read from the
   source of both repositories; the container/eic-shell setup that makes it
   work in practice was not inspected.

---

*Generated from [eic/epic](https://github.com/eic/epic) @ `216e4c2`
and [eic/EICrecon](https://github.com/eic/EICrecon) `main`
(fetched 2026-08-19). AI-authored draft — verify against source.*
