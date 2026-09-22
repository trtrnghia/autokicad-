"""
sourcing_fab.py - Sourcing API & 1-Click Turnkey Fab Profiles for AutoKiCad.
Provides LCSC Part Number (Cxxxxx) mapping and generates turnkey BOM/CPL
for JLCPCB and PCBWay SMT assembly.
"""

import os
from typing import Dict, Any, List, Optional, Tuple

# Standard catalog mapping for common components
LCSC_CATALOG = {
    ("R", "330", "0805"): {"lcsc": "C17673", "mfr": "Yageo", "mpn": "RC0805FR-07330RL"},
    ("R", "10k", "0805"): {"lcsc": "C17414", "mfr": "Yageo", "mpn": "RC0805FR-0710KL"},
    ("R", "1k", "0805"): {"lcsc": "C17513", "mfr": "Yageo", "mpn": "RC0805FR-071KL"},
    ("C", "100n", "0805"): {"lcsc": "C49678", "mfr": "Samsung", "mpn": "CL21B104KBCNNNC"},
    ("C", "10u", "0805"): {"lcsc": "C15850", "mfr": "Samsung", "mpn": "CL21A106KOQNNNE"},
    ("LED", "LED_GREEN", "0805"): {"lcsc": "C84267", "mfr": "Lite-On", "mpn": "LTST-C170GKT"},
    ("LED", "LED_RED", "0805"): {"lcsc": "C84263", "mfr": "Lite-On", "mpn": "LTST-C170CKT"},
    ("CONN", "5V_IN", "PinHeader_1x02"): {"lcsc": "C2890035", "mfr": "Samtec / Generic", "mpn": "TSW-102-07-G-S"}
}

class SourcingFabEngine:
    def __init__(self, fab_name: str = "jlcpcb"):
        self.fab_name = fab_name.lower()

    def get_fab_rules(self) -> Dict[str, Any]:
        """Returns DRC design rule constraints for selected fab house."""
        if self.fab_name == "jlcpcb":
            return {
                "name": "JLCPCB Standard 2-Layer",
                "min_track_width_mm": 0.127,  # 5 mil
                "min_clearance_mm": 0.127,    # 5 mil
                "min_via_drill_mm": 0.30,
                "min_via_dia_mm": 0.60,
                "copper_weight_oz": 1.0,
                "board_thickness_mm": 1.6
            }
        else:  # pcbway default
            return {
                "name": "PCBWay Standard 2-Layer",
                "min_track_width_mm": 0.15,   # 6 mil
                "min_clearance_mm": 0.15,     # 6 mil
                "min_via_drill_mm": 0.30,
                "min_via_dia_mm": 0.60,
                "copper_weight_oz": 1.0,
                "board_thickness_mm": 1.6
            }

    def resolve_lcsc_part(self, comp_type: str, value: str, package: str) -> Dict[str, str]:
        """Looks up LCSC Cxxxxx part number for 1-click SMT ordering."""
        pkg_key = "0805" if "0805" in package else package
        for (c_t, v, p), info in LCSC_CATALOG.items():
            if c_t in comp_type and v.lower() in value.lower() and p in pkg_key:
                return info
        return {"lcsc": "N/A", "mfr": "Generic", "mpn": "Custom"}

    def export_turnkey_jlcpcb_bom_cpl(
        self,
        output_dir: str,
        components_data: List[Dict[str, Any]]
    ) -> Tuple[str, str]:
        """
        Exports turnkey JLCPCB BOM and CPL files with LCSC Part Numbers (Cxxxxx)
        for zero-effort instant upload on JLCPCB.com.
        """
        os.makedirs(output_dir, exist_ok=True)
        bom_file = os.path.join(output_dir, "BOM_JLCPCB.csv")
        cpl_file = os.path.join(output_dir, "CPL_JLCPCB.csv")

        # 1. JLCPCB BOM: Comment, Designator, Footprint, LCSC Part #
        with open(bom_file, "w", encoding="utf-8") as f:
            f.write("Comment,Designator,Footprint,LCSC Part #\n")
            for c in components_data:
                c_type = "LED" if c["ref"].startswith("D") else ("R" if c["ref"].startswith("R") else "CONN")
                info = self.resolve_lcsc_part(c_type, c["val"], c.get("package", ""))
                lcsc_code = info["lcsc"] if info["lcsc"] != "N/A" else c.get("spn", "")
                f.write(f'"{c["val"]}","{c["ref"]}","{c["footprint"]}","{lcsc_code}"\n')

        # 2. JLCPCB CPL: Designator, Val, Package, Mid X, Mid Y, Rotation, Layer
        with open(cpl_file, "w", encoding="utf-8") as f:
            f.write("Designator,Val,Package,Mid X,Mid Y,Rotation,Layer\n")
            for c in components_data:
                f.write(f'"{c["ref"]}","{c["val"]}","{c["package"]}",{c["x_mm"]:.3f},{c["y_mm"]:.3f},{c.get("rot_deg", 0):.1f},"top"\n')

        return bom_file, cpl_file
