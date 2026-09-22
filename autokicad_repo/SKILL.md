---
name: autokicad
description: Autonomous KiCad PCB and EDA implementation engine. Transforms user electronic concepts, architecture, and constraints into editable, DRC-clean, manufacturable KiCad projects, Gerbers, drill files, and complete release packages.
---

# /autokicad - Autonomous KiCad PCB & EDA Implementation Engine

## 1. Core Concept & Role Separation

- **The USER is the electronics/system designer.**
  The user provides: circuit concept, functional requirements, system architecture, required ICs and components, electrical specifications, mechanical constraints, and board dimensions.
- **/autokicad is the PCB/EDA implementation engine.**
  /autokicad takes complete ownership of translating the user's concept into an actual, editable, DRC-clean, and fully manufacturable KiCad project and release package.

```
USER
  ↓ (Circuit requirements, architecture, constraints, specifications)
/autokicad ENGINE
  ↓ (Circuit synthesis, SPICE smoke test, footprint fetch, placement, A* routing, DRC/ERC, kicad-happy review, remediation)
CLEAN-ROOM KicadLastRelease/ VERIFICATION
  ↓ (Single source of truth: 8x PASS gate)
MANUFACTURABLE PCB RELEASE PACKAGE (ZIP + 3D Raytraced Renders + STL Enclosure + Firmware Bridge)
```

### Critical Directives
- **DO NOT replace the user's engineering concept with your own.**
- **DO NOT autonomously redesign the system architecture unless explicitly requested.**
- **DO NOT silently substitute components.** (e.g. If user specifies STM32F407, do not swap for ESP32; if user specifies A4988, do not substitute; if user specifies USB-C, do not use Micro-USB; if user specifies 24V, do not change to 12V).
- If an implementation problem exists (e.g. footprint mismatch, obsolete pinout, thermal risk), **report it clearly** and propose alternatives only when necessary.
- **NO FAKE AUTOMATION:** Never claim "Routing completed" without actual tracks created, never claim "DRC passed" without executing KiCad DRC, and never claim "Footprints verified" without inspecting actual footprint definitions. Every report must distinguish: **ACTUALLY EXECUTED**, **RECOMMENDED**, and **NOT VERIFIED**.

---

## 2. Upgraded 4-Layer Autonomous Architecture & Modules

AutoKiCad integrates 10 advanced autonomous subsystems across 4 functional layers:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ TẦNG 1: SCHEMATIC & LINH KIỆN THÔNG MINH (Circuit Synthesis & Sourcing)         │
│  - Circuit Graph Engine      - SPICE Smoke Test        - Auto-Fetch Footprint   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ TẦNG 2: BỐ TRÍ & ĐI DÂY THUẬT TOÁN (Algorithmic Physical Layout)                │
│  - Force-Directed Placement  - Native Multi-Layer A*   - Auto-Remediation Loop  │
├─────────────────────────────────────────────────────────────────────────────────┤
│ TẦNG 3: SẢN XUẤT TURNKEY & PROFILE NHÀ XƯỞNG (Fab House Sourcing Profiles)     │
│  - JLCPCB / PCBWay SMT BOM/CPL with LCSC Cxxxxx Part Matching                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ TẦNG 4: ĐÓNG GÓI PHÁT HÀNH TOÀN DIỆN (Comprehensive Physical & Digital Release) │
│  - Raytraced 3D Renders      - 3D Printable Enclosure  - Firmware Bridge (C/Py) │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Layer 1: Schematic & Smart Components
1. **Parametric Circuit Graph Engine (`circuit_graph.py`)**
   - Represents circuits as an in-memory graph of components, pins, and nets.
   - Automatically injects required `PWR_FLAG` power symbols to eliminate KiCad ERC Pin-Not-Driven errors.
   - Synthesizes robust KiCad 10 `.kicad_sch` S-expressions with verified pin coordinates, wires, labels, and hierarchical blocks.
2. **Automated SPICE & Circuit Smoke Test (`spice_sim.py`)**
   - Automatically computes LED forward voltages, branch currents, and resistor power dissipation ($P = I^2 R$).
   - Generates standalone SPICE netlist (`.cir`) decks compatible with KiCad's bundled `ngspice.dll`.
   - Halts build pipeline if component absolute maximum ratings are exceeded (e.g., resistor overload).
3. **IPC-7351 Footprint Resolver & Synthesizer (`component_fetcher.py`)**
   - Resolves component footprints against local KiCad libraries and online IPC catalogs.
   - Fallback algorithmic synthesizer creates exact IPC-7351 SMD footprints (e.g., 0805, 0603, 1206, SOT-23, SOIC-8) with pads, courtyard clearances, and silkscreen markings.
   - Automatically registers `local_footprints.pretty` into project-level `fp-lib-table`.

### Layer 2: Algorithmic Physical Layout
4. **Force-Directed Algorithmic Placement (`placement_engine.py`)**
   - Organizes components logically based on signal flow and netlist connectivity.
   - Automatically pins I/O connectors, USB ports, and terminal blocks to board edges.
   - Enforces minimum courtyard separation ($\ge 1.0\,\text{mm}$) and thermal clearances.
5. **Native Multi-Layer A* Grid & Maze Auto-Router (`autorouter.py`)**
   - Pure-Python multi-layer A* maze router operating directly on KiCad coordinate grids.
   - Routes orthogonal and 45° traces on `F.Cu` and `B.Cu` with obstacle dilation (design rule clearance).
   - Automatically inserts standard through-hole vias (0.8mm pad / 0.4mm drill) for layer transitions without requiring external Java or FreeRouting dependencies.
6. **Closed-Loop Auto-Remediation Playbook (`remediation_engine.py`)**
   - Ingests native DRC and `kicad-happy` violation reports.
   - Translates findings into layout adjustments: expands clearances, moves overlapping traces, adds missing fiducials and test points, and nudges text clear of pads.
   - Re-runs DRC/ERC in a closed loop until zero blocking defects remain.

### Layer 3: Turnkey Sourcing & Fab Profiles
7. **Turnkey Sourcing & Fab Profiles (`sourcing_fab.py`)**
   - Supports targeted fab house profiles via `--fab {jlcpcb, pcbway}`.
   - Automatically maps standard component values to LCSC Part Numbers (e.g., `C10001` for 100nF 0805 capacitor, `C17975` for 330Ω resistor).
   - Generates fab-tailored SMT BOM and Pick-and-Place CPL (`BOM_JLCPCB.csv`, `CPL_JLCPCB.csv`).

### Layer 4: Comprehensive Physical & Digital Release
8. **Headless 3D Raytraced Renders (`doc_packager.py`)**
   - Uses native `kicad-cli pcb render` to produce photorealistic 3D raytraced PCB renders (`render_top.png`, `render_bottom.png`) with realistic lighting, copper traces, solder mask, and silkscreen.
9. **3D Printable Snap-Fit & Screw-Down Enclosure Generator (`enclosure_gen.py`)**
   - Generates watertight ASCII STL files (`enclosure_top.stl`, `enclosure_bottom.stl`) matching exact board dimensions, corner radiuses, and mounting hole standoffs.
10. **Hardware-to-Firmware Pinout Configuration Bridge (`firmware_bridge.py`)**
    - Scans schematic microcontroller pins, nets, and headers.
    - Exports ready-to-use C/C++ header (`pinout.h`), MicroPython module (`pinout.py`), and machine-readable metadata (`pins.json`).

---

## 3. Skill Execution Commands

The AutoKiCad execution engine runs in KiCad's bundled Python 3.11 environment on Windows 11:

### 1. Build Complete Project (End-to-End Phase 2 Pipeline)
```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" "C:\Users\trtrn\.gemini\config\skills\autokicad\scripts\autokicad_engine.py" build --dir "<project_dir>" --name "<project_name>" --fab jlcpcb
```

#### Core CLI Arguments:
- `--dir`: Target project directory containing or receiving KiCad project files.
- `--name`: Base name for the project (e.g. `test_led`).
- `--fab`: Target turnkey fab profile (`jlcpcb` or `pcbway`). Default is `jlcpcb`.

#### Phase 2 Opt-in Advanced Modules:
- `--thermal`: Enables Thermal & PI/SI Simulation (IR drop warnings and thermal via stitching).
- `--mcad <file.step>`: Enables Bi-directional MCAD-ECAD. Extracts board outline and locks connectors to match a user-provided 3D enclosure.
- `--dynamic-bom`: Enables Dynamic AI Supply Chain. Fetches live stock/pricing from LCSC/DigiKey instead of using a static catalog.
- `--firmware <platform>`: Triggers Firmware Boilerplate Generator (e.g., `--firmware platformio`) to generate complete compilable C++ projects.

### 2. Run Headless ERC
```powershell
& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" sch erc --format json --output "<project_dir>\VERIFICATION\ERC_Report.json" "<project_dir>\<name>.kicad_sch"
```

### 3. Run Headless DRC
```powershell
& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb drc --format json --refill-zones --output "<project_dir>\VERIFICATION\DRC_Report.json" "<project_dir>\<name>.kicad_pcb"
```

### 4. Headless 3D Raytraced Render
```powershell
& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb render --side top --width 1600 --height 1200 --output "<project_dir>\3D\render_top.png" "<project_dir>\<name>.kicad_pcb"
& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb render --side bottom --width 1600 --height 1200 --output "<project_dir>\3D\render_bottom.png" "<project_dir>\<name>.kicad_pcb"
```

### 5. Export 3D STEP Model
```powershell
& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb export step --force --include-tracks --include-pads --include-zones --output "<project_dir>\3D\<name>.step" "<project_dir>\<name>.kicad_pcb"
```

---

## 4. Manufacturing Release Package Structure (Section 15 Specification)

Every completed project generated by `/autokicad` must produce this complete release directory structure:

```
PROJECT/
├── SOURCE/                          <- Editable KiCad project, schematic, PCB, and libraries
│   ├── <name>.kicad_pro
│   ├── <name>.kicad_sch
│   ├── <name>.kicad_pcb
│   ├── sym-lib-table & fp-lib-table
│   └── local_footprints.pretty/
├── FABRICATION/
│   ├── GERBER/                      <- Gerbers for all active copper, mask, silk, and edge cuts
│   ├── DRILL/                       <- Excellon PTH, NPTH, and Drill_Map.pdf
│   ├── ODBPP/                       <- ODB++ intelligent manufacturing archive
│   ├── IPC2581/                     <- IPC-2581 manufacturing XML
│   ├── IPC356/                      <- IPC-D-356 netlist verification file
│   └── FABRICATION_DRAWING.pdf
├── ASSEMBLY/
│   ├── BOM.csv & BOM.xlsx           <- Complete Bill of Materials with MPNs
│   ├── BOM_JLCPCB.csv               <- Turnkey SMT BOM with LCSC Part Numbers
│   ├── CPL.csv & CPL.txt            <- Component Pick-and-Place Centroid coordinates
│   ├── CPL_JLCPCB.csv               <- Turnkey SMT Centroid file
│   ├── Assembly_Top.pdf & Assembly_Bottom.pdf
│   └── Assembly_3D.step
├── DOCUMENTATION/
│   ├── Schematic.pdf
│   ├── PCB.pdf (multi-page layer plots)
│   ├── Fabrication_Drawing.pdf & Assembly_Drawing.pdf
│   ├── Stackup.pdf, Impedance.pdf, Manufacturing_Notes.pdf, Release_Notes.pdf
│   └── FIRMWARE/                    <- Hardware-to-Firmware Pinout Configuration Bridge
│       ├── pinout.h                 <- C/C++ embedded pin defines
│       ├── pinout.py                <- MicroPython / CircuitPython pin mapping
│       └── pins.json                <- Machine-readable pinout metadata
├── 3D/
│   ├── <name>.step & <name>.stp     <- MCAD STEP exchange models
│   ├── render_top.png               <- Photorealistic raytraced top render
│   ├── render_bottom.png            <- Photorealistic raytraced bottom render
│   ├── enclosure_top.stl            <- 3D printable top shell (watertight STL)
│   └── enclosure_bottom.stl         <- 3D printable bottom shell with standoffs
├── VERIFICATION/
│   ├── ERC_Report.json & .txt
│   ├── DRC_Report.json & .txt
│   ├── DFM_Report.json & DFA_Report.txt & DFT_Report.txt
│   ├── SPICE_Smoke_Test.json        <- Automated electrical ratings & dissipation check
│   ├── Connectivity_Report.txt & Footprint_Verification_Report.txt
│   └── kicad_happy/                 <- Multi-analyzer pre-compliance audit reports
├── KicadLastRelease/                <- SINGLE SOURCE OF TRUTH (verified release sources)
│   ├── <name>.kicad_pro
│   ├── <name>.kicad_sch
│   ├── <name>.kicad_pcb
│   ├── sym-lib-table & fp-lib-table
│   └── clean_room_verification.json <- Independent verification audit log
├── MANIFEST.json                    <- Project metadata, toolchain, and SHA256 checksums
└── RELEASE/
    └── FINAL_MANUFACTURING_PACKAGE.zip
```

---

## 5. Continuous kicad-happy Review & Auto-Correction Loop

AutoKiCad embeds `kicad-happy` as an internal continuous review, verification, and optimization layer throughout the implementation cycle:

```
IMPLEMENT -> VERIFY (Native ERC/DRC) -> kicad-happy REVIEW -> CLASSIFY -> AUTO-CORRECT -> RE-VERIFY -> OPTIMIZE -> CLEAN-ROOM VERIFY -> RELEASE
```

### Finding Classification:
1. **CRITICAL / ERROR**: Functional or physical defects (unrouted nets, power rail shorts, DRC errors, missing MPNs). Must be resolved prior to release.
2. **WARNING**: Margins, testpoint coverage, silkscreen clearance. Remediated or optimized.
3. **OPTIMIZATION**: Placement refinements, decoupling loop improvements, fiducial addition.
4. **INFORMATION / FALSE_POSITIVE**: Non-actionable notices, logged for audit trail.

AutoKiCad automatically resolves layout/mechanical findings (edge clearance, missing fiducials, testpoints, silkscreen text) while **strictly pausing to consult the user** for any architectural or schematic circuit changes.

---

## 6. 8-Axis Release Verification & Gate

A release cannot be marked as `APPROVED FOR PRODUCTION` unless all 8 verification axes pass:

| Axis | Verification Dimension | Standard / Gate Requirement |
|:---:|---|---|
| **1** | **Schematic Integrity (ERC)** | 0 errors, 0 warnings, verified symbol mapping, all power flags set. |
| **2** | **Layout Integrity (DRC)** | 0 violations, 0 unconnected items via native KiCad DRC. |
| **3** | **Consistency (Netlist & Schematic)** | Schematic placeable component count exactly matches PCB footprint count (diff = 0); net counts match. |
| **4** | **kicad-happy Multi-Analyzer Review** | Internal fab release gate verdict `PASS` (0 critical, 0 blocking errors across schematic, PCB, EMC, thermal, and Gerbers). |
| **5** | **DFM / Fab House Compatibility** | Trace widths, spacings, drill holes, annular rings within target fab specs. |
| **6** | **DFA / Assembly & SMT Readiness** | Courtyards intact, >= 3 fiducials on SMD sides, centroid CPL generated. |
| **7** | **Sourcing / BOM Readiness** | 100% MPN coverage for non-DNP parts, distributor parts confirmed, LCSC part numbers mapped. |
| **8** | **Clean-Room Release & Integrity** | `KicadLastRelease/` verified independently with 0 errors/violations, `MANIFEST.json` SHA256 checksums valid. |

If any mandatory axis fails, report **MANUFACTURING RELEASE BLOCKED** with the exact diagnostic breakdown.
