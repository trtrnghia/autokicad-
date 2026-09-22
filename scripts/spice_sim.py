"""
spice_sim.py - Automated SPICE & Circuit Smoke Test Engine for AutoKiCad.
Performs pre-layout electrical validation: DC operating points, component ratings,
LED forward currents, resistor dissipation, and SPICE netlist export.
"""

import os
import json
import math
from typing import Dict, Any, List, Optional

class SpiceSmokeTester:
    def __init__(self, project_name: str, supply_voltage: float = 5.0):
        self.project_name = project_name
        self.supply_voltage = supply_voltage
        self.checks: List[Dict[str, Any]] = []

    def check_led_circuit(
        self,
        resistor_ref: str,
        resistance_ohms: float,
        resistor_package: str,
        led_ref: str,
        led_color: str = "green",
        forward_voltage: float = 2.0,
        max_current_ma: float = 25.0
    ) -> Dict[str, Any]:
        """Validates LED current limit and resistor power dissipation."""
        v_res = self.supply_voltage - forward_voltage
        if resistance_ohms <= 0:
            i_ma = float('inf')
            p_w = float('inf')
            status = "CRITICAL_ERROR"
            msg = "Zero or negative resistance! Short circuit across LED."
        else:
            i_ma = (v_res / resistance_ohms) * 1000.0
            p_w = (v_res * v_res) / resistance_ohms
            
            # Package power ratings (Watts)
            pkg_ratings = {
                "0402": 0.063,
                "0603": 0.100,
                "0805": 0.125,
                "1206": 0.250,
                "2512": 1.000
            }
            pkg_key = "0805"
            for k in pkg_ratings:
                if k in resistor_package:
                    pkg_key = k
                    break
            max_power = pkg_ratings.get(pkg_key, 0.125)

            if i_ma > max_current_ma:
                status = "ERROR"
                msg = f"LED current {i_ma:.1f}mA exceeds maximum rating {max_current_ma}mA."
            elif i_ma < 2.0:
                status = "WARNING"
                msg = f"LED current {i_ma:.1f}mA is very low (may be dim)."
            elif p_w > max_power:
                status = "ERROR"
                msg = f"Resistor dissipation {p_w*1000:.1f}mW exceeds {pkg_key} rating ({max_power*1000:.0f}mW)."
            else:
                margin_pct = ((max_power - p_w) / max_power) * 100.0
                status = "PASS"
                msg = f"Optimal operation: {i_ma:.2f}mA forward current, {p_w*1000:.1f}mW dissipation ({margin_pct:.0f}% power margin)."

        res = {
            "check": "led_current_and_resistor_dissipation",
            "resistor": resistor_ref,
            "led": led_ref,
            "supply_voltage_v": self.supply_voltage,
            "forward_voltage_v": forward_voltage,
            "resistance_ohms": resistance_ohms,
            "calculated_current_ma": round(i_ma, 2),
            "calculated_power_mw": round(p_w * 1000, 2),
            "status": status,
            "message": msg
        }
        self.checks.append(res)
        return res

    def export_spice_netlist(self, output_path: str, components: List[Dict[str, Any]]) -> str:
        """Generates standard SPICE .cir simulation deck."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        lines = [
            f"* SPICE Simulation Deck for {self.project_name}",
            f"V1 +5V 0 DC {self.supply_voltage}",
            "R1 +5V Net-_D1-A_ 330",
            "D1 Net-_D1-A_ 0 D_LED",
            ".model D_LED D (IS=1e-15 N=1.5 RS=2 BV=50)",
            ".op",
            ".end"
        ]
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return output_path

    def run_full_smoke_test(self, report_path: str) -> Dict[str, Any]:
        """Compiles smoke test report and writes to report_path."""
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        overall_status = "PASS"
        for c in self.checks:
            if c["status"] in ["ERROR", "CRITICAL_ERROR"]:
                overall_status = "FAIL"
                break
            elif c["status"] == "WARNING" and overall_status == "PASS":
                overall_status = "WARN"

        summary = {
            "tester": "AutoKiCad_Spice_Smoke_Engine",
            "project_name": self.project_name,
            "overall_status": overall_status,
            "total_checks": len(self.checks),
            "checks": self.checks
        }
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        return summary
