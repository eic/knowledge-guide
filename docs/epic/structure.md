---
title: Repository structure
parent: ePIC geometry
nav_order: 1
source: eic/epic
source_commit: 216e4c2fd73411ebb79a340fab95ae08e74e294b
generated: 2026-08-19
status: draft
---

# `eic/epic` repository structure

{: .warning }
AI-generated draft derived from the ePIC geometry description at commit
[`216e4c2`](https://github.com/eic/epic/commit/216e4c2fd73411ebb79a340fab95ae08e74e294b).
Every claim links to the exact file — verify there before depending on it.

## Top-level tour

| path | contents |
|---|---|
| [`compact/`](https://github.com/eic/epic/tree/main/compact) | all detector description XML — the bulk of the repo |
| [`src/`](https://github.com/eic/epic/tree/main/src) | 60+ C++ DD4hep detector-construction plugins |
| [`configurations/`](https://github.com/eic/epic/tree/main/configurations) | 73 YAMLs, one per generated `epic_*.xml` |
| [`templates/`](https://github.com/eic/epic/tree/main/templates) | `epic.xml.jinja2` master template, `thisepic.sh.in`, `version.xml.in`, parameter-table template |
| [`calibrations/`](https://github.com/eic/epic/tree/main/calibrations) | small tracked calibration JSONs + the mount point for downloaded blobs |
| [`bin/`](https://github.com/eic/epic/tree/main/bin) | build/CI helper scripts (`make_detector_configuration`, material scans, DAWN views, ACTS geometry check) |
| [`scripts/`](https://github.com/eic/epic/tree/main/scripts), [`macro/`](https://github.com/eic/epic/tree/main/macro) | analysis/visualisation helpers |
| [`views/`](https://github.com/eic/epic/tree/main/views), [`reports/`](https://github.com/eic/epic/tree/main/reports), [`_layouts/`](https://github.com/eic/epic/tree/main/_layouts) | CI artifact generation and the GitHub Pages site |
| [`cmake/`](https://github.com/eic/epic/tree/main/cmake), [`CMakeLists.txt`](https://github.com/eic/epic/blob/main/CMakeLists.txt) | build: compiles `src/` into one plugin library, renders the configurations, installs `compact/` and `calibrations/` |

{: .note }
There is **no `fieldmaps/` directory** in the repository, and `calibrations/`
holds almost nothing. Both are populated at *geometry load time* by download
plugins — see [Downloaded blobs](#downloaded-blobs-fieldmaps-and-calibrations)
below.

## `compact/` layout

Top-level files in [`compact/`](https://github.com/eic/epic/tree/main/compact)
are the global pieces, always included by the template:

| file | role |
|---|---|
| [`definitions.xml`](https://github.com/eic/epic/blob/main/compact/definitions.xml) | ~37 KB of global geometry constants (world size, subsystem envelopes, shared radii) |
| [`materials.xml`](https://github.com/eic/epic/blob/main/compact/materials.xml) | material and mixture definitions |
| [`optical_materials.xml`](https://github.com/eic/epic/blob/main/compact/optical_materials.xml) | optical properties (refractive index, absorption) for the RICH/DIRC radiators |
| [`calibrations.xml`](https://github.com/eic/epic/blob/main/compact/calibrations.xml) | `epic_FileLoader` plugin invocations that fetch calibration blobs |
| [`tracking_region.xml`](https://github.com/eic/epic/blob/main/compact/tracking_region.xml) | the ACTS tracking volume envelope |
| [`colors.xml`](https://github.com/eic/epic/blob/main/compact/colors.xml), [`display*.xml`](https://github.com/eic/epic/blob/main/compact/display.xml) | visualisation attributes (three display variants: default, detailed, geoviewer) |
| [`solenoid.xml`](https://github.com/eic/epic/blob/main/compact/solenoid.xml), [`central_beampipe.xml`](https://github.com/eic/epic/blob/main/compact/central_beampipe.xml), [`fields.xml`](https://github.com/eic/epic/blob/main/compact/fields.xml) | magnet, beam pipe, field wiring |

Subdirectories map one-to-one onto the `features` categories in the
configuration YAMLs:

| subdirectory | contents |
|---|---|
| [`compact/tracking/`](https://github.com/eic/epic/tree/main/compact/tracking) | `vertex_barrel`, `silicon_barrel`, `silicon_disks`, `mpgd_barrel`, `mpgd_outerbarrel`, `mpgd_{forward,backward}_endcap`, `tof_barrel`, `tof_endcap`, `support_service_craterlake`, `definitions_craterlake`, plus `*_2DStrip` variants and a `deprecated/` folder |
| [`compact/ecal/`](https://github.com/eic/epic/tree/main/compact/ecal) | `bic/` (barrel imaging calorimeter), `bic_default.xml`, `bic_6layers.xml`, `bic_layer1_only.xml`, `forward_ScFi.xml`, `forward_averaged_homogeneous.xml`, `backward_PbWO4.xml` |
| [`compact/hcal/`](https://github.com/eic/epic/tree/main/compact/hcal) | `lfhcal`, `forward_insert`, `barrel_gdml`, `barrel_flux_return`, `backward`, `{forward,backward}_endcap_flux`, `backward_sampF`, `backward_template` |
| [`compact/pid/`](https://github.com/eic/epic/tree/main/compact/pid) | `dirc.xml`, `drich.xml`, `pfrich.xml` |
| [`compact/fields/`](https://github.com/eic/epic/tree/main/compact/fields) | `marco.xml` (solenoid map) + ~40 `beamline_<ebeam>x<pbeam>[_species].xml` files |
| [`compact/far_forward/`](https://github.com/eic/epic/tree/main/compact/far_forward), [`compact/far_backward/`](https://github.com/eic/epic/tree/main/compact/far_backward) | B0, Roman Pots, off-momentum, ZDC / low-Q² taggers, luminosity |

A subsystem XML that offers variants uses a thin wrapper file. For example
[`bic_default.xml`](https://github.com/eic/epic/blob/main/compact/ecal/bic_default.xml)
is the whole "4 AstroPix layers" configuration — it sets six stave-enable
constants and then `<include ref="bic/bic.xml"/>`, which holds the real
description. That is why the `craterlake.yml` `ecal` feature lists
`bic_default` rather than `bic`.

## The detector plugin pattern

Every entry in [`src/`](https://github.com/eic/epic/tree/main/src) named
`*_geo.cpp` is a DD4hep **detector-element factory**: a C++ function that
receives the `<detector>` XML element and returns a constructed `DetElement`.
The function is registered under a plugin name by the `DECLARE_DETELEMENT`
macro at the bottom of the file:

```cpp
// src/CurvedBarrelTracker_geo.cpp:397
DECLARE_DETELEMENT(epic_CylinderSVTBarrel, create_CurvedBarrelTracker)

// src/BarrelCalorimeterScFi_geo.cpp:422
DECLARE_DETELEMENT(epic_EcalBarrelScFi, create_detector)
```

DD4hep then resolves a `<detector type="X">` element by looking up the factory
registered as `X`. So the `type` attribute is the *only* thing that selects the
construction code — everything else in the element is data handed to it.

A real example, the vertex barrel
([`compact/tracking/vertex_barrel.xml`, lines 90–105](https://github.com/eic/epic/blob/main/compact/tracking/vertex_barrel.xml#L90-L105)):

```xml
<detector
  id="VertexBarrel_0_ID"
  name="VertexBarrel"
  type="epic_CylinderSVTBarrel"
  readout="VertexBarrelHits"
  insideTrackingVolume="true">
  <type_flags type="DetType_TRACKER + DetType_BARREL" />
  <rsu_layout
    passive_vis="SVTReadoutVis"
    rows_rphi="RSURows_rphi"
    halves_z="RSUHalves_z"
```

Reading it attribute by attribute:

- `type="epic_CylinderSVTBarrel"` → dispatches to
  [`CurvedBarrelTracker_geo.cpp`](https://github.com/eic/epic/blob/main/src/CurvedBarrelTracker_geo.cpp).
- `name="VertexBarrel"` → the `DetElement` name; also the prefix used for the
  detector's constants.
- `id="VertexBarrel_0_ID"` → a constant (defined elsewhere in the compact
  files) giving the numeric detector ID that lands in the `system` field of
  every cellID.
- `readout="VertexBarrelHits"` → binds the detector to the `<readout>` block of
  the same name, which defines the cellID bitfield and the segmentation. This
  name is also the **hit collection name** in the simulation output, which is
  why EICrecon configs say `readout: "VertexBarrelHits"`.
- `insideTrackingVolume="true"` → placed inside the ACTS tracking region.
- child elements (`<type_flags>`, `<rsu_layout>`, `<dimensions>`, `<layer>`, …)
  are read by the plugin itself; their schema is defined by the plugin, not by
  DD4hep.

The same pattern in the barrel ECal ScFi section
([`bic.xml`, lines 323–334](https://github.com/eic/epic/blob/main/compact/ecal/bic/bic.xml#L323-L334)):

```xml
<detector
  id="EcalBarrel2_ID"
  name="EcalBarrelScFi"
  type="epic_EcalBarrelScFi"
  readout="EcalBarrelScFiHits"
  calorimeterType="EM_BARREL"
  region="EcalBarrelRegion"
  vis="EcalBarrelEnvelopeVis"
  offset="EcalBarrel_Calorimeter_offset">
```

Note that the barrel ECal is **two `<detector>` elements** in one file — the
imaging (AstroPix) section
([`type="epic_EcalBarrelImaging"`](https://github.com/eic/epic/blob/main/compact/ecal/bic/bic.xml#L142-L149))
and the ScFi section above — which is exactly why EICrecon's
[BEMC page]({% link docs/eicrecon/detectors/bemc.md %}) has two independent
reconstruction branches that are merged at the end.

Not every plugin is a detector. [`FileLoader.cpp`](https://github.com/eic/epic/blob/main/src/FileLoader.cpp#L67)
registers with `DECLARE_APPLY(epic_FileLoader, load_file)` instead, making it a
`<plugin>` you invoke rather than a `<detector>` you place.

## Where constants like `EcalBarrel_LightGuide_PositivePosZ` are defined

EICrecon's `SimCalorimeterHitProcessor` is configured with
`attenuationReferencePositionName = "EcalBarrel_LightGuide_{Positive,Negative}PosZ"`
but does not define those names — they live in the geometry. A code search
(`https://api.github.com/search/code?q=LightGuide+repo:eic/epic`) returns five
hits; the relevant one is
[`compact/ecal/bic/bic.xml`, lines 40–47](https://github.com/eic/epic/blob/main/compact/ecal/bic/bic.xml#L40-L47):

```xml
<constant name="EcalBarrel_LightGuide_length"       value="5*cm"/>
<constant name="EcalBarrel_EndOfSectorBox_length"   value="12*cm"/>
<constant name="EcalBarrel_LightGuide_zmin"         value="EcalBarrel_Calorimeter_zmin + EcalBarrel_LightGuide_length"/>
<constant name="EcalBarrel_LightGuide_zmax"         value="EcalBarrel_Calorimeter_zmax + EcalBarrel_LightGuide_length"/>
<constant name="EcalBarrel_Readout_zmin"            value="EcalBarrel_Calorimeter_zmin + EcalBarrel_EndOfSectorBox_length"/>
<constant name="EcalBarrel_Readout_zmax"            value="EcalBarrel_Calorimeter_zmax + EcalBarrel_EndOfSectorBox_length"/>
<constant name="EcalBarrel_LightGuide_NegativePosZ" value="-EcalBarrel_LightGuide_zmin"/>
<constant name="EcalBarrel_LightGuide_PositivePosZ" value="EcalBarrel_LightGuide_zmax"/>
```

with, [a few lines up](https://github.com/eic/epic/blob/main/compact/ecal/bic/bic.xml#L31-L34):

```xml
<constant name="EcalBarrel_Calorimeter_zmin" value="min(258.75*cm, EcalBarrelBackward_zmax)"/>
<constant name="EcalBarrel_Calorimeter_zmax" value="min(176.25*cm, EcalBarrelForward_zmax)"/>
```

Two things worth noting:

- `zmin` is the **backward** extent expressed as a positive length, so the
  negative-end reference is written `-EcalBarrel_LightGuide_zmin`. The two
  constants are deliberately asymmetric because the barrel is not centred on
  z = 0 (hence also `EcalBarrel_Calorimeter_offset`).
- Both are clamped with `min(...)` against neighbouring subsystem envelopes, so
  their value can change when an adjacent detector moves. This is a strong
  argument for reading the evaluated
  [constants dump](https://eic.github.io/epic/artifacts/constants/epic_craterlake_constants.toml)
  rather than transcribing the expression.

### The general rule for constants

| scope | file |
|---|---|
| global / cross-subsystem | [`compact/definitions.xml`](https://github.com/eic/epic/blob/main/compact/definitions.xml) |
| far-forward, far-backward | `compact/far_{forward,backward}/definitions.xml` |
| beam-energy dependent | `compact/fields/beamline_<E>x<E>.xml` |
| subsystem-local | the `<define>` block at the top of that subsystem's own compact XML |
| configuration override | the wrapper file, e.g. [`bic_default.xml`](https://github.com/eic/epic/blob/main/compact/ecal/bic_default.xml) setting `EcalBarrel_enable_staves_*` |

The template includes them in that order
([lines 47–52](https://github.com/eic/epic/blob/main/templates/epic.xml.jinja2#L47-L52)),
so beamline definitions are visible to everything downstream.

## How EICrecon consumes geometry constants at runtime

EICrecon does not parse the XML itself. It loads the same compact description
through DD4hep and queries the resulting `Detector` object by name:

```cpp
// EICrecon src/algorithms/calorimetry/SimCalorimeterHitProcessor.cc:138-141
if (!m_cfg.attenuationReferencePositionName.empty()) {
  m_attenuationReferencePosition =
      m_geo.detector()->constant<double>(m_cfg.attenuationReferencePositionName) * ...
```
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/SimCalorimeterHitProcessor.cc#L138-L141))

and, for the cellID bitfield:

```cpp
// SimCalorimeterHitProcessor.cc:107
m_id_spec = m_geo.detector()->readout(m_cfg.readout).idSpec();
```
([source](https://github.com/eic/EICrecon/blob/main/src/algorithms/calorimetry/SimCalorimeterHitProcessor.cc#L107))

The practical consequences:

- A geometry constant is referenced by EICrecon as a **string**, resolved at
  initialisation. A rename in `eic/epic` is not a compile error in EICrecon —
  it is a runtime failure.
- The geometry and reconstruction versions must match. `DETECTOR_CONFIG` picks
  which `epic_*.xml` EICrecon loads, and therefore which constants and readouts
  exist.
- The reverse dependency is real too: EICrecon parameter tables reference field
  names (`fiber`, `z`, `layer`, `grid`) that only exist because a `<readout>`
  block in `eic/epic` declares them. See
  [Readouts and segmentation]({% link docs/epic/readouts.md %}).

## Downloaded blobs: fieldmaps and calibrations

Large binary inputs are **not** stored in `eic/epic`. They live in
[`eic/epic-data`](https://github.com/eic/epic-data) and are fetched at geometry
load time, pinned to an exact commit.

Two mechanisms, same helper
([`FileLoaderHelper.h`](https://github.com/eic/epic/blob/main/src/FileLoaderHelper.h)):

**1. `epic_FileLoader` plugin** — used by
[`compact/calibrations.xml`](https://github.com/eic/epic/blob/main/compact/calibrations.xml)
for LUTs, ONNX models and JSON calibrations:

```xml
<plugin name="epic_FileLoader">
  <arg value="cache:$DETECTOR_CACHE:/opt/detector"/>
  <arg value="file:calibrations/drich.lut.gz"/>
  <arg value="url:https://github.com/eic/epic-data/raw/d512557.../drich.lut.gz"/>
</plugin>
```

**2. `url=`/`cache=` attributes on a field** — used by
[`compact/fields/marco.xml`](https://github.com/eic/epic/blob/main/compact/fields/marco.xml)
for the solenoid map:

```xml
<field type="epic_FieldMapB" name="GlobalSolenoid" field_type="magnetic" coord_type="BrBz"
       field_map="fieldmaps/MARCO_v.7.6.2.2.11_1.7T_Magnetic_Field_Map_2024_05_02_rad_coords_cm_T.BMap.txt"
       url="https://github.com/eic/epic-data/raw/81182bf.../MARCO_....BMap.txt"
       cache="$DETECTOR_CACHE:/opt/detector"
       scale="1.0">
```

The resolution algorithm, from
[`EnsureFileFromURLExists`](https://github.com/eic/epic/blob/main/src/FileLoaderHelper.h#L32):

1. Expand environment variables in `cache` and split it on `:` into a search
   path (`$DETECTOR_CACHE`, then `/opt/detector`).
2. Hash the **URL** (`hash64`, 16 hex chars). The hash is the real filename;
   the human-readable `file:` path becomes a symlink to it. This is what makes
   the pinning work — changing the URL changes the hash, so a stale file is
   never silently reused.
3. Search the cache directories recursively for that hash; symlink to it if
   found.
4. Otherwise download with `curl` (or `xrdcp` for `root://` URLs) into the hash
   path, then symlink.

{: .important }
The `file:` argument is a **relative path**
([`fs::path file_path(file)`](https://github.com/eic/epic/blob/main/src/FileLoaderHelper.h#L57)),
so blobs land under the **current working directory** of whichever process
loads the geometry — `$PWD/calibrations/…`, `$PWD/fieldmaps/…`. Running from a
directory you cannot write to, or from a different directory than the one where
the files were materialised, is a common failure mode. Setting `DETECTOR_CACHE`
to a shared read-only cache avoids re-downloading but does not remove the need
for a writable CWD.

The tracked
[`calibrations/`](https://github.com/eic/epic/tree/main/calibrations) directory
therefore holds only the small, human-editable files —
`calo_digi_default.json`, `emcal_barrel_calibration.json`, `ffi_zdc.json` — plus
a `.gitkeep` so the download target exists. Its
[README](https://github.com/eic/epic/blob/main/calibrations/README.md) states
the policy: calibrations are *"strongly versioned and tied directly to this
specific detector configuration"*, so no extra version suffixes in filenames —
the geometry commit *is* the version.

---

*Generated from [eic/epic](https://github.com/eic/epic) @ `216e4c2`
(fetched 2026-08-19). AI-authored draft — verify against source.*
