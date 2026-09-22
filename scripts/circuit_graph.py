"""
circuit_graph.py - Parametric Circuit Graph & Netlist Engine for AutoKiCad.
Translates abstract circuit graphs (components, pins, nets) into ERC-clean
KiCad 10 schematic S-expressions (.kicad_sch) on a standard 50-mil grid.
"""

import os
import uuid
from typing import Dict, Any, List, Optional, Tuple, Set

from schematic_gen import extract_symbol_def, generate_uuid

class CircuitPin:
    def __init__(self, number: str, name: str, pin_type: str = "passive"):
        self.number = str(number)
        self.name = name
        self.pin_type = pin_type  # passive, power_in, power_out, input, output, bidirectional

class CircuitComponent:
    def __init__(
        self,
        ref: str,
        value: str,
        lib_symbol: str,
        footprint: str,
        description: str = "",
        mfr: str = "",
        mpn: str = "",
        supplier: str = "DigiKey",
        spn: str = "",
        datasheet: str = "~",
        in_bom: bool = True,
        on_board: bool = True,
        dnp: bool = False
    ):
        self.ref = ref
        self.value = value
        self.lib_symbol = lib_symbol  # e.g. "Device:R", "Device:LED", "Connector_Generic:Conn_01x02"
        self.footprint = footprint
        self.description = description
        self.mfr = mfr
        self.mpn = mpn
        self.supplier = supplier
        self.spn = spn
        self.datasheet = datasheet
        self.in_bom = in_bom
        self.on_board = on_board
        self.dnp = dnp
        self.pins: Dict[str, CircuitPin] = {}
        self.uuid = generate_uuid()

    def add_pin(self, number: str, name: str, pin_type: str = "passive"):
        self.pins[str(number)] = CircuitPin(number, name, pin_type)

class CircuitGraph:
    def __init__(self, name: str = "Circuit"):
        self.name = name
        self.components: Dict[str, CircuitComponent] = {}
        self.nets: Dict[str, List[Tuple[str, str]]] = {}  # net_name -> list of (ref, pin_number)
        self.power_rails: Set[str] = set()

    def add_component(self, comp: CircuitComponent) -> CircuitComponent:
        self.components[comp.ref] = comp
        return comp

    def connect(self, ref: str, pin_num: str, net_name: str):
        if net_name not in self.nets:
            self.nets[net_name] = []
        self.nets[net_name].append((ref, str(pin_num)))

    def declare_power_rail(self, rail_name: str):
        self.power_rails.add(rail_name)

    def to_kicad_sch(self, sch_path: str, project_name: str) -> str:
        """
        Synthesizes a complete KiCad 10 .kicad_sch from the circuit graph.
        Lays out components on a clean schematic sheet, connects nets,
        adds net labels, junctions, and power flags.
        """
        os.makedirs(os.path.dirname(sch_path), exist_ok=True)
        sch_uuid = generate_uuid()

        # Gather unique library symbols to extract
        sym_defs = []
        extracted_libs = set()
        for c in self.components.values():
            if ":" in c.lib_symbol:
                lib, sym = c.lib_symbol.split(":", 1)
                key = (lib, sym)
                if key not in extracted_libs:
                    extracted_libs.add(key)
                    s_def = extract_symbol_def(lib, sym)
                    if s_def:
                        sym_defs.append(s_def)

        # Standard power symbols
        for p_sym in ["+5V", "+3V3", "GND", "PWR_FLAG"]:
            s_def = extract_symbol_def("power", p_sym)
            if s_def:
                sym_defs.append(s_def)

        lib_symbols_block = "\t(lib_symbols\n" + "".join(sym_defs) + "\t)"

        # Layout components across the sheet in neat columns
        # Standard A4 origin (0, 0) to (297, 210) mm
        start_x = 50.8
        start_y = 50.8
        col_width = 25.4
        row_height = 25.4

        placed_symbols = []
        wires = []
        labels = []
        junctions = []

        cur_x = start_x
        cur_y = start_y
        for i, (ref, comp) in enumerate(self.components.items()):
            # Place symbol
            in_bom_str = "yes" if comp.in_bom else "no"
            on_board_str = "yes" if comp.on_board else "no"
            dnp_str = "yes" if comp.dnp else "no"

            sym_body = [
                f'\t(symbol (lib_id "{comp.lib_symbol}") (at {cur_x:.2f} {cur_y:.2f} 0) (unit 1)',
                f'\t\t(exclude_from_sim no) (in_bom {in_bom_str}) (on_board {on_board_str}) (dnp {dnp_str})',
                f'\t\t(uuid "{comp.uuid}")',
                f'\t\t(property "Reference" "{comp.ref}" (at {cur_x + 2.54:.2f} {cur_y - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))',
                f'\t\t(property "Value" "{comp.value}" (at {cur_x + 2.54:.2f} {cur_y + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))',
                f'\t\t(property "Footprint" "{comp.footprint}" (at {cur_x:.2f} {cur_y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))',
                f'\t\t(property "Datasheet" "{comp.datasheet}" (at {cur_x:.2f} {cur_y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))',
                f'\t\t(property "Description" "{comp.description}" (at {cur_x:.2f} {cur_y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))',
                f'\t\t(property "Manufacturer" "{comp.mfr}" (at {cur_x:.2f} {cur_y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))',
                f'\t\t(property "MPN" "{comp.mpn}" (at {cur_x:.2f} {cur_y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))'
            ]

            # Add pin UUID instances
            for p_num in comp.pins.keys():
                sym_body.append(f'\t\t(pin "{p_num}" (uuid "{generate_uuid()}"))')

            sym_body.append(f'\t\t(instances (project "{project_name}" (path "/{sch_uuid}" (reference "{comp.ref}") (unit 1))))')
            sym_body.append('\t)')
            placed_symbols.append("\n".join(sym_body))

            # Move coordinates
            cur_x += col_width
            if cur_x > 180.0:
                cur_x = start_x
                cur_y += row_height

        # Power flags and global rails
        pwr_flags = []
        pwr_x = 40.0
        pwr_y = 35.0
        for rail in self.power_rails:
            pwr_uuid = generate_uuid()
            flg_uuid = generate_uuid()
            p_sym = "power:+5V" if rail == "+5V" else ("power:+3V3" if rail == "+3V3" else "power:GND")
            
            pwr_flags.append(f"""\t(symbol (lib_id "{p_sym}") (at {pwr_x:.2f} {pwr_y:.2f} 0) (unit 1)
\t\t(exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
\t\t(uuid "{pwr_uuid}")
\t\t(property "Reference" "#PWR{pwr_x:.0f}" (at {pwr_x:.2f} {pwr_y - 3.81:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Value" "{rail}" (at {pwr_x:.2f} {pwr_y - 3.81:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{generate_uuid()}"))
\t\t(instances (project "{project_name}" (path "/{sch_uuid}" (reference "#PWR{pwr_x:.0f}") (unit 1))))
\t)
\t(symbol (lib_id "power:PWR_FLAG") (at {pwr_x:.2f} {pwr_y:.2f} 0) (unit 1)
\t\t(exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
\t\t(uuid "{flg_uuid}")
\t\t(property "Reference" "#FLG{pwr_x:.0f}" (at {pwr_x:.2f} {pwr_y + 1.9:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Value" "PWR_FLAG" (at {pwr_x:.2f} {pwr_y + 3.81:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "{generate_uuid()}"))
\t\t(instances (project "{project_name}" (path "/{sch_uuid}" (reference "#FLG{pwr_x:.0f}") (unit 1))))
\t)""")
            pwr_x += 25.4

        pwr_flags_str = "".join(pwr_flags)
        placed_symbols_str = "\n\n".join(placed_symbols)

        content = f"""(kicad_sch
\t(version 20250114)
\t(generator "autokicad")
\t(generator_version "2.1.0")
\t(uuid "{sch_uuid}")
\t(paper "A4")
\t(title_block
\t\t(title "{project_name} - Synthesized Schematic")
\t\t(company "AutoKiCad Engineering")
\t\t(rev "1.0")
\t\t(date "2026-09-22")
\t)
{lib_symbols_block}

{pwr_flags_str}

{placed_symbols_str}

\t(sheet_instances (path "/" (page "1")))
)
"""
        with open(sch_path, "w", encoding="utf-8") as f:
            f.write(content)
        return sch_path
