# AutoKiCad Internal Architecture & Conceptual Modules

AutoKiCad implements 28 conceptual modules to take full responsibility for transforming user engineering concepts into manufacturable KiCad PCB projects.

## 01_requirements
Parses user electronic concepts, architecture, voltage/current requirements, interface definitions, and mechanical constraints. Never silently substitutes user components or architecture.

## 02_schematic
Generates KiCad 10 schematic files (`.kicad_sch`) with standardized S-expressions, sheet instances, title blocks, wires, junctions, and annotations.

## 03_symbols
Manages KiCad symbol libraries (`.kicad_sym`). Pulls official symbol definitions from KiCad 10's installed libraries (`Device`, `Connector_Generic`, `power`, etc.) to guarantee 100% ERC symbol match.

## 04_components
Tracks component metadata: References, Values, Descriptions, Manufacturers, MPNs, Distributors, SPNs, Footprint links, and Datasheet references.

## 05_footprints
Verifies and assigns physical footprints from KiCad's 155 `.pretty` libraries. Checks pad counts, pad numbering, dimensions, SMD vs THT, and courtyard boundaries.

## 06_pcb_setup
Configures copper and dielectric layers, board thickness (1.6 mm standard), solder mask, silkscreen properties, and design rules.

## 07_stackup
Manages 2-layer and 4-layer standard PCB stackups (e.g. standard FR-4 1.6mm 1oz copper, JLC7628 4-layer).

## 08_board_outline
Defines physical board dimensions on the `Edge_Cuts` layer, including rectangular outlines, rounded corners, mounting holes, slots, and keepout regions.

## 09_placement
Places components according to electrical flow: power connectors at board borders, ICs centrally located, and decoupling capacitors immediately adjacent to power pins.

## 10_netclasses
Establishes net classes: Default (0.25mm trace, 0.20mm clearance), POWER (0.50mm trace, 0.25mm clearance), HIGH_CURRENT (1.0mm trace, 0.30mm clearance), USB (differential pairs).

## 11_routing
Generates actual physical copper traces on `F.Cu` and `B.Cu` using 45-degree and orthogonal segments, ensuring no trace collisions or net shorting.

## 12_vias
Places through-hole, signal, and power vias (0.8mm diameter / 0.4mm drill) to transition signals and connect SMD pads to internal/bottom ground planes.

## 13_zones
Creates and manages polygon copper pour zones with configurable thermal reliefs, spoke widths, and clearance rules.

## 14_grounding
Implements continuous ground return paths and ground planes on bottom and internal layers without unintentional plane splitting.

## 15_power
Routes dedicated power rails with appropriate trace widths (0.5mm - 1.0mm) to minimize IR drop and loop areas.

## 16_highspeed
Manages controlled impedance, length matching, and return paths for high-speed interfaces when specified by the user.

## 17_thermal
Manages thermal dissipation, exposed pad soldering, and thermal vias for power-dissipating components.

## 18_emc
Applies PCB-level EMC best practices: short return loops, TVS protection placement, and separation of noisy switching loops from sensitive analog traces.

## 19_silkscreen
Positions component reference designators, values, pin-1 markers, polarity indicators, and board revision text away from exposed copper pads and board edges.

## 20_erc
Executes headless Electrical Rules Check via `kicad-cli sch erc --format json` and automatically repairs unassigned pins or missing power flags.

## 21_drc
Executes headless Design Rules Check via `kicad-cli pcb drc --format json` and verifies 0 violations and 0 unconnected nets.

## 22_dfm
Performs Design for Manufacturability audits checking minimum trace widths, clearances, drill diameters, annular rings, and solder mask bridges.

## 23_dfa
Performs Design for Assembly checks: component spacing, orientation, polarity markers, and pick-and-place centroid access.

## 24_dft
Ensures testability with accessible headers, probe nodes, and test points.

## 25_fabrication
Generates all manufacturing outputs: Gerbers (F.Cu, B.Cu, F.Mask, B.Mask, F.SilkS, B.SilkS, F.Paste, B.Paste, Edge.Cuts), Excellon NC Drill (PTH/NPTH), ODB++, IPC-2581, IPC-D-356, and 3D STEP models.

## 26_documentation
Generates complete release documentation: Schematic PDF, multi-page PCB PDF, Fabrication Drawing PDF, Assembly Top/Bottom PDFs, Stackup PDF, Impedance PDF, Manufacturing Notes, and Release Notes.

## 27_verification
Cross-verifies schematic netlist against physical PCB connectivity and produces the audit report.

## 28_repair
Automated remediation loop that adjusts placement, routing, or clearances if DRC or ERC encounters violations during intermediate steps.
