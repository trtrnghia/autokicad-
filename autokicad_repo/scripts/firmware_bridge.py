"""
firmware_bridge.py - Hardware-to-Firmware Pinout & Configuration Bridge for AutoKiCad.
Generates C/C++ headers (pinout.h), MicroPython definitions (pinout.py), and JSON maps
bridging physical board layout directly to embedded firmware developers.
"""

import os
import json
from typing import Dict, Any, List, Optional

class FirmwareBridge:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.pin_map: Dict[str, Dict[str, Any]] = {}

    def add_pin(self, label: str, ref: str, pin_num: str, net_name: str, direction: str = "OUTPUT", active_high: bool = True):
        self.pin_map[label] = {
            "ref": ref,
            "pin": str(pin_num),
            "net": net_name,
            "direction": direction,
            "active_high": active_high
        }

    def export_all(self, output_dir: str) -> Dict[str, str]:
        """Exports pinout.h, pinout.py, and pins.json."""
        os.makedirs(output_dir, exist_ok=True)
        h_file = os.path.join(output_dir, "pinout.h")
        py_file = os.path.join(output_dir, "pinout.py")
        json_file = os.path.join(output_dir, "pins.json")

        # 1. C/C++ Header
        h_lines = [
            f"/**",
            f" * @file pinout.h",
            f" * @brief Auto-generated hardware pinout configuration for {self.project_name}",
            f" * @date 2026-09-22",
            f" */",
            f"#ifndef {self.project_name.upper()}_PINOUT_H",
            f"#define {self.project_name.upper()}_PINOUT_H\n",
            f"#ifdef __cplusplus",
            f'extern "C" {{',
            f"#endif\n"
        ]
        for lbl, d in self.pin_map.items():
            h_lines.append(f"// {lbl}: {d['ref']} Pin {d['pin']} ({d['net']})")
            h_lines.append(f"#define {lbl.upper()}_PIN          {d['pin']}")
            h_lines.append(f"#define {lbl.upper()}_ACTIVE_HIGH  {'1' if d['active_high'] else '0'}")
            h_lines.append(f"#define {lbl.upper()}_DIRECTION    \"{d['direction']}\"\n")

        h_lines.append("#ifdef __cplusplus\n}\n#endif\n#endif // " + f"{self.project_name.upper()}_PINOUT_H\n")
        with open(h_file, "w", encoding="utf-8") as f:
            f.write("\n".join(h_lines))

        # 2. Python / MicroPython
        py_lines = [
            f'"""Auto-generated hardware pinout configuration for {self.project_name}"""\n'
        ]
        for lbl, d in self.pin_map.items():
            py_lines.append(f"{lbl.upper()}_PIN = {d['pin']}")
            py_lines.append(f"{lbl.upper()}_ACTIVE_HIGH = {d['active_high']}")
            py_lines.append(f"{lbl.upper()}_DIR = '{d['direction']}'\n")

        with open(py_file, "w", encoding="utf-8") as f:
            f.write("\n".join(py_lines))

        # 3. JSON Map
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump({
                "project_name": self.project_name,
                "pins": self.pin_map
            }, f, indent=2)

        return {
            "header": h_file,
            "python": py_file,
            "json": json_file
        }
