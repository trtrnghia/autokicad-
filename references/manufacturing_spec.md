# AutoKiCad Manufacturing & Release Specification

## Release File Structure
Every complete AutoKiCad project release must follow this directory structure:

```
PROJECT/
├── SOURCE/
│   ├── project.kicad_pro
│   ├── project.kicad_sch
│   ├── project.kicad_pcb
│   ├── SYMBOLS/
│   ├── FOOTPRINTS/
│   ├── 3D_MODELS/
│   ├── RULES/
│   └── SCRIPTS/
│
├── FABRICATION/
│   ├── GERBER/
│   │   ├── F_Cu.gbr
│   │   ├── B_Cu.gbr
│   │   ├── F_Mask.gbr
│   │   ├── B_Mask.gbr
│   │   ├── F_SilkS.gbr
│   │   ├── B_SilkS.gbr
│   │   ├── F_Paste.gbr
│   │   ├── B_Paste.gbr
│   │   └── Edge_Cuts.gbr
│   ├── DRILL/
│   │   ├── project-PTH.drl
│   │   ├── project-NPTH.drl
│   │   └── project-drl_map.pdf
│   ├── ODBPP/
│   │   └── project_odb.zip
│   ├── IPC2581/
│   │   └── project_ipc2581.xml
│   ├── IPC356/
│   │   └── project.d356
│   └── FABRICATION_DRAWING.pdf
│
├── ASSEMBLY/
│   ├── BOM.csv
│   ├── BOM.xlsx
│   ├── CPL.csv
│   ├── CPL.txt
│   ├── Assembly_Top.pdf
│   ├── Assembly_Bottom.pdf
│   └── Assembly_3D.step
│
├── DOCUMENTATION/
│   ├── Schematic.pdf
│   ├── PCB.pdf
│   ├── Fabrication_Drawing.pdf
│   ├── Assembly_Drawing.pdf
│   ├── Stackup.pdf
│   ├── Impedance.pdf
│   ├── Manufacturing_Notes.pdf
│   └── Release_Notes.pdf
│
├── 3D/
│   ├── project.step
│   ├── project.stp
│   └── renders/
│
├── VERIFICATION/
│   ├── ERC_Report.json
│   ├── ERC_Report.txt
│   ├── DRC_Report.json
│   ├── DRC_Report.txt
│   ├── DFM_Report.json
│   ├── DFM_Report.pdf
│   ├── DFA_Report.txt
│   ├── DFT_Report.txt
│   ├── Connectivity_Report.txt
│   └── Footprint_Verification_Report.txt
│
├── MANIFEST.json
│
└── RELEASE/
    └── FINAL_MANUFACTURING_PACKAGE.zip
```

## Manufacturing Release Gate Checklist
A project cannot be marked `FINAL_MANUFACTURING_PACKAGE` unless all mandatory checks pass:
- [x] Schematic verified and complete
- [x] Symbol mapping verified (100% library match)
- [x] Footprint mapping verified (physical pad count & pitch validated)
- [x] PCB connectivity verified (100% connected, 0 unconnected nets)
- [x] Board outline verified on Edge.Cuts
- [x] Placement verified preserving circuit architecture
- [x] Routing completed (actual physical tracks created)
- [x] Vias verified
- [x] Copper zones filled and verified
- [x] Design rules verified
- [x] ERC executed headlessly (0 errors, 0 warnings)
- [x] DRC executed headlessly (0 violations, 0 unconnected)
- [x] DFM checked against fabricator capabilities
- [x] DFA checked for assembly clearance and polarity
- [x] DFT checked for test / probe accessibility
- [x] Gerbers generated for all active copper and tooling layers
- [x] Drill files generated (PTH, NPTH, Drill Map PDF)
- [x] BOM generated in CSV and XLSX
- [x] CPL / Centroid generated in CSV and TXT
- [x] 3D STEP exported with tracks, pads, and board body
- [x] Fabrication drawing generated
- [x] Assembly drawings generated (Top & Bottom)
- [x] Release consistency check verified (all files from final revision)
- [x] MANIFEST.json generated with SHA256 checksums
- [x] FINAL_MANUFACTURING_PACKAGE.zip compiled
