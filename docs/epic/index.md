---
title: ePIC geometry
nav_order: 3
has_children: true
source: eic/epic
source_commit: 216e4c2fd73411ebb79a340fab95ae08e74e294b
generated: 2026-08-19
status: draft
---

# ePIC geometry — the `eic/epic` detector description

{: .warning }
AI-generated draft derived from the ePIC geometry description at commit
[`216e4c2`](https://github.com/eic/epic/commit/216e4c2fd73411ebb79a340fab95ae08e74e294b).
Every claim links to the exact file — verify there before depending on it.

[`eic/epic`](https://github.com/eic/epic) is the **DD4hep** description of the
ePIC detector. It is the single source of truth for geometry, materials,
readout segmentation, and named geometry constants — consumed by DD4hep-based
simulation (`ddsim`/`npsim`) *and* by [EICrecon]({{ site.baseurl }}{% link docs/eicrecon/index.md %})
at reconstruction time, which loads the same compact description to decode
cellIDs and look up constants.

## The two halves: XML and C++

DD4hep splits a detector description in two, and `eic/epic` follows that split
exactly:

| | what it is | where |
|---|---|---|
| **Compact XML** | declarative: constants, materials, placements, visualisation, `<readout>` segmentation | [`compact/`](https://github.com/eic/epic/tree/main/compact) |
| **Detector plugins** | imperative C++ factories that turn one `<detector>` element into TGeo/Geant4 volumes | [`src/`](https://github.com/eic/epic/tree/main/src) |

The link between them is the `type` attribute. A `<detector>` element in XML
names a plugin, and the plugin is registered under that same name by a
`DECLARE_DETELEMENT` macro in C++ — for example
[`vertex_barrel.xml`](https://github.com/eic/epic/blob/main/compact/tracking/vertex_barrel.xml#L90-L95)
declares `type="epic_CylinderSVTBarrel"`, which resolves to
[`CurvedBarrelTracker_geo.cpp`](https://github.com/eic/epic/blob/main/src/CurvedBarrelTracker_geo.cpp#L397).
The XML carries all the numbers; the C++ carries the construction logic and is
reused across many detectors. See
[Repository structure]({{ site.baseurl }}{% link docs/epic/structure.md %}) for the full pattern.

## Configurations are generated, not checked in

{: .important }
There is **no `epic_craterlake.xml` in the repository**. Looking for one is the
most common first wrong turn. The top-level configuration XMLs are *rendered at
build time*.

The mechanism, in three files:

1. [`templates/epic.xml.jinja2`](https://github.com/eic/epic/blob/main/templates/epic.xml.jinja2)
   — the master template. It unconditionally includes materials, definitions,
   calibrations and the tracking region, then conditionally includes one XML per
   entry of a `features` dictionary.
2. [`configurations/*.yml`](https://github.com/eic/epic/tree/main/configurations)
   — one small YAML per configuration, listing the beam energies and the
   `features` to include.
3. [`bin/make_detector_configuration`](https://github.com/eic/epic/blob/main/bin/make_detector_configuration)
   — a ~30-line Python script that renders the template with the YAML as context.

[`CMakeLists.txt`](https://github.com/eic/epic/blob/main/CMakeLists.txt#L81-L97)
globs every YAML and emits one XML each:

```
configurations/craterlake.yml  →  epic_craterlake.xml
configurations/full.yml        →  epic_full.xml
configurations/vertex_only.yml →  epic_vertex_only.xml
```

`epic_full.xml` is additionally installed a second time under the bare name
[`epic.xml`](https://github.com/eic/epic/blob/main/CMakeLists.txt#L99-L102), so
"the default geometry" means *full*. All of them are installed into
`$DETECTOR_PATH/`.

### What the YAML looks like

[`configurations/craterlake.yml`](https://github.com/eic/epic/blob/main/configurations/craterlake.yml)
in full — this is the whole definition of the flagship configuration:

```yaml
ebeam: 5
pbeam: 41
features:
  beampipe:
  tracking:
    definitions_craterlake:
    vertex_barrel:
    vertex_barrel_support:
    silicon_barrel:
    mpgd_barrel:
    support_service_craterlake:
    mpgd_outerbarrel:
    mpgd_forward_endcap:
    mpgd_backward_endcap:
    silicon_disks:
    tof_barrel:
    tof_endcap:
  pid:
    dirc:
    pfrich:
    drich:
  ecal:
    forward_averaged_homogeneous:
    bic_default:
    backward_PbWO4:
  solenoid:
  hcal:
    lfhcal:
    forward_insert:
    barrel_gdml:
    barrel_flux_return:
    forward_endcap_flux:
    backward:
    backward_endcap_flux:
  far_forward:
    default:
  far_backward:
    default:
```

Each key under a feature category is a **file basename** inside the matching
`compact/` subdirectory. The template turns `tracking: {vertex_barrel:}` into
an include of `${DETECTOR_PATH}/compact/tracking/vertex_barrel.xml`
([template loop](https://github.com/eic/epic/blob/main/templates/epic.xml.jinja2#L140-L148)):

{% raw %}
```jinja
{% if 'tracking' in features %}
  {% for tracker in features['tracking'] -%}
  <include ref="${DETECTOR_PATH}/compact/tracking/{{ tracker }}.xml"/>
  {% endfor -%}
{% endif -%}
```
{% endraw %}

`ebeam`/`pbeam` select the beamline field/definitions file
([line 47](https://github.com/eic/epic/blob/main/templates/epic.xml.jinja2#L47)):
`compact/fields/beamline_5x41.xml` for the YAML above, defaulting to `18x275`
when unset.

{: .note }
Note that the plain `craterlake.yml` pins **5 GeV × 41 GeV**, not the headline
18×275. Beam-energy-specific variants (`craterlake_18x275.yml`,
`craterlake_10x100.yml`, …) exist precisely because the beamline magnet field
maps differ per energy.

### The configuration families

73 YAMLs are present. They fall into a few groups:

| family | examples | purpose |
|---|---|---|
| flagship | `craterlake`, `full` | the complete detector |
| beam energy / species | `craterlake_18x275`, `craterlake_10x100_Au197`, `craterlake_5x41_He3` | same detector, per-beam beamline fields |
| detector variants | `craterlake_bic_6layers`, `craterlake_bic_layer1_only`, `craterlake_no_bhcal`, `craterlake_no_zdc_lyso`, `craterlake_tracking_2DStrip` | studies with one subsystem changed |
| subsystem-only | `vertex_only`, `drich_only`, `dirc_only`, `pfrich_only`, `imaging_only`, `lfhcal_only`, `tof_only`, `bhcal`, `fhcal` | fast standalone studies |
| grouped subsets | `inner_detector`, `tracking_only`, `calorimeters`, `forward_detectors`, `pid_only`, `tracking_and_drich` | multi-subsystem slices |
| interaction region | `ip6`, `ip6_extended` | beamline only |
| special-purpose | `craterlake_material_map` | material scans / ACTS maps |

The authoritative list is the
[directory listing](https://github.com/eic/epic/tree/main/configurations) — it
changes often.

## Environment variables

[`templates/thisepic.sh.in`](https://github.com/eic/epic/blob/main/templates/thisepic.sh.in)
is installed as `install/bin/thisepic.sh` and defines the variables everything
downstream keys off:

| variable | meaning |
|---|---|
| `DETECTOR` | project name (`epic`) |
| `DETECTOR_PATH` | install data dir — where the generated `epic_*.xml` and `compact/` live |
| `DETECTOR_CACHE` | search path for downloaded calibration/field-map blobs; defaults to `DETECTOR_PATH` |
| `DETECTOR_CONFIG` | which configuration to load, e.g. `epic_craterlake` |
| `DETECTOR_VERSION` | version stamp |

`${DETECTOR_PATH}` is textually substituted inside every `<include ref="...">`
in the generated XML, so a compact file is only resolvable with the variable set.

## How to find a detector's dimensions, materials or readout

| you want | where to look |
|---|---|
| a **dimension** (radius, z extent, thickness) | the `<define>` block of the subsystem's compact XML — e.g. `EcalBarrel_*` constants in [`compact/ecal/bic/bic.xml`](https://github.com/eic/epic/blob/main/compact/ecal/bic/bic.xml#L30-L47). Global/shared ones are in [`compact/definitions.xml`](https://github.com/eic/epic/blob/main/compact/definitions.xml) |
| **all** resolved constants, numerically | the CI artifact dumps: [`epic_craterlake_constants.out`](https://eic.github.io/epic/artifacts/constants/epic_craterlake_constants.out) / [`.toml`](https://eic.github.io/epic/artifacts/constants/epic_craterlake_constants.toml) — expressions already evaluated |
| a curated **parameter table** | [`epic_craterlake.html`](https://eic.github.io/epic/artifacts/DetectorParameterTable/epic_craterlake.html) / [`.csv`](https://eic.github.io/epic/artifacts/DetectorParameterTable/epic_craterlake.csv), generated from [`templates/DetectorParameterTable.csv.jinja2`](https://github.com/eic/epic/blob/main/templates/DetectorParameterTable.csv.jinja2) |
| a **material** | [`compact/materials.xml`](https://github.com/eic/epic/blob/main/compact/materials.xml) and [`compact/optical_materials.xml`](https://github.com/eic/epic/blob/main/compact/optical_materials.xml) |
| a **readout / cellID layout** | the `<readouts>` block at the bottom of the subsystem XML — see [Readouts and segmentation]({{ site.baseurl }}{% link docs/epic/readouts.md %}) |
| **what the thing looks like** | the [geoviewer](https://eic.github.io/epic/geoviewer?nobrowser&file=artifacts/tgeo/epic_craterlake.root&item=default;1&opt=clipx;clipy;transp30;zoom120;ROTY320;ROTZ340;trz0;trr0;ctrl;all) and the view/STEP artifacts linked from the [README](https://github.com/eic/epic/blob/main/README.md) |
| **how a volume is built** | the `src/*_geo.cpp` plugin named by the `<detector type="...">` attribute |

{: .note }
Constants are **expressions**, not numbers — e.g.
`EcalBarrel_LightGuide_zmax = EcalBarrel_Calorimeter_zmax + EcalBarrel_LightGuide_length`
where `EcalBarrel_Calorimeter_zmax = min(176.25*cm, EcalBarrelForward_zmax)`.
Chasing a value by hand across files is error-prone; prefer the evaluated
constants dump above.

## Pages in this section

- **[Repository structure]({{ site.baseurl }}{% link docs/epic/structure.md %})** — directory tour,
  the plugin pattern, where constants are declared and how EICrecon reads them.
- **[Readouts and segmentation]({{ site.baseurl }}{% link docs/epic/readouts.md %})** — cellID
  bitfields, segmentation types, and where calibration files actually come from.

---

*Generated from [eic/epic](https://github.com/eic/epic) @ `216e4c2`
(fetched 2026-08-19). AI-authored draft — verify against source.*
