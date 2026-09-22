<div align="center">
  <h1>🚀 AutoKiCad</h1>
  <p><strong>The Autonomous Full-Stack Hardware EDA Agent for KiCad 10</strong></p>
</div>

<p align="center">
  AutoKiCad is an AI-native EDA engine that transforms abstract electronic concepts into fully verified, manufacturable KiCad PCB release packages. It operates autonomously to synthesize schematics, route multi-layer boards, run SPICE simulations, export 3D enclosures, and generate turnkey assembly files.
</p>

---

## 🌟 Capabilities Overview

AutoKiCad orchestrates a **4-Layer Autonomous Architecture** composed of 10 advanced modules:

### 1️⃣ Schematic & Smart Sourcing
- **Circuit Graph Engine:** Synthesizes `kicad_sch` files dynamically, auto-injecting `PWR_FLAG`s to eliminate ERC Pin-Not-Driven errors.
- **SPICE Smoke Test:** Validates operating points (e.g., LED current, resistor power dissipation) against component absolute maximum ratings.
- **IPC-7351 Footprint Synthesizer:** Resolves libraries or algorithmically generates compliant SMD/THT footprints on-the-fly.

### 2️⃣ Algorithmic Physical Layout
- **Force-Directed Placement:** Organizes components logically, pinning connectors to edges and enforcing $\ge 1.0\text{mm}$ thermal/courtyard spacing.
- **Multi-Layer A* Router:** Pure-Python native grid router. Automatically generates Solid Copper Pours for PDN and routes High-Speed Differential Pairs with length matching.
- **Auto-Remediation Playbook:** Closed-loop engine that reads KiCad DRC violations and automatically nudges traces, clearances, and vias until 0 errors remain.

### 3️⃣ Turnkey Sourcing & Fab Profiles
- **Dynamic LCSC / JLCPCB / PCBWay Integration:** Generates `BOM_JLCPCB.csv` and `CPL_JLCPCB.csv` with automatically mapped LCSC (Cxxxxx) part numbers for 1-click SMT assembly.

### 4️⃣ Comprehensive Digital & Physical Release
- **Headless 3D Raytracing:** Uses KiCad 10 CLI to export photorealistic PCB renders.
- **Enclosure Co-Design:** Generates watertight ASCII STL shells (top/bottom) matching board outlines and screw holes. (Supports Bi-directional MCAD-ECAD).
- **Firmware Bridge:** Scans schematic nets and exports `pinout.h`, `pinout.py`, and `pins.json` for seamless software integration.

---

## ⚙️ Installation

AutoKiCad is designed as a **Google Antigravity Agent Skill**, but its Python CLI engine can be run entirely standalone.

### Standalone Python Setup
Requires **KiCad 10** (Windows). AutoKiCad uses the Python 3.11 environment bundled with KiCad.

```bash
git clone https://github.com/yourusername/autokicad.git
cd autokicad
```

### Antigravity Skill Installation
Copy the repository into your global skills directory:
```bash
cp -r autokicad ~/.gemini/config/skills/
```
In your chat, simply type `/autokicad` to summon the hardware engineer.

---

## 💻 CLI Usage (Command Bus)

You can invoke the pipeline manually via KiCad's Python executable:

```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" scripts/autokicad_engine.py build --dir "my_project" --name "my_board" --fab jlcpcb
```

### Opt-In Advanced Modules
AutoKiCad Phase 2 introduces enterprise capabilities that can be toggled on demand:
- `--thermal`: Enables IR drop analysis and thermal via stitching.
- `--mcad enclosure.step`: Derives the board outline and connector placements dynamically from a user-provided 3D STEP enclosure.
- `--dynamic-bom`: Fetches live stock/pricing from distributor APIs.
- `--firmware platformio`: Generates full compilable C++ projects instead of just headers.

---

## 📁 Manufacturing Release Structure (Section 15 Spec)

A successful AutoKiCad run generates a fully verified release package:
```text
my_board/
├── SOURCE/                      # Editable KiCad 10 Project
├── FABRICATION/                 # Gerbers, Excellon Drill, ODB++, IPC-2581
├── ASSEMBLY/                    # SMT BOM & Pick-and-Place (CPL) files
├── DOCUMENTATION/               # Schematics & Firmware Bridge (pinout.h)
├── 3D/                          # Raytraced PNGs, STEP models, STL Enclosures
├── VERIFICATION/                # ERC, DRC, SPICE, and kicad-happy multi-analyzer logs
├── KicadLastRelease/            # Clean-room Single Source of Truth
└── RELEASE/
    └── FINAL_MANUFACTURING_PACKAGE.zip
```

---

## 🛡️ The 8-Axis Release Gate

AutoKiCad refuses to package a release unless all 8 verification axes pass natively:
1. **Schematic Integrity** (0 ERC errors)
2. **Layout Integrity** (0 DRC errors, 0 unconnected)
3. **Netlist Consistency** (Schematic vs PCB diff = 0)
4. **kicad-happy Review** (0 critical violations)
5. **DFM / Fab Compatibility** (Trace widths & clearances meet fab house rules)
6. **DFA / SMT Readiness** (Fiducials present, courtyards clear)
7. **BOM Readiness** (100% MPN coverage)
8. **Clean-Room Integrity** (Independent `KicadLastRelease/` checksums valid)

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
