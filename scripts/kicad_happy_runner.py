"""
kicad_happy_runner.py - Internal Review, Analysis, and Verification Layer for AutoKiCad.
Orchestrates the kicad-happy analysis tool suite:
  - analyze_schematic.py
  - analyze_pcb.py
  - cross_analysis.py
  - analyze_emc.py
  - analyze_thermal.py
  - analyze_gerbers.py
  - fab_release_gate.py
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, List, Optional

PYTHON_EXE = r"C:\Program Files\KiCad\10.0\bin\python.exe"
KICAD_HAPPY_ROOT = r"C:\Users\trtrn\.gemini\config\plugins\kicad-happy"
KICAD_SCRIPTS = os.path.join(KICAD_HAPPY_ROOT, "skills", "kicad", "scripts")
EMC_SCRIPTS = os.path.join(KICAD_HAPPY_ROOT, "skills", "emc", "scripts")

class KicadHappyReviewer:
    def __init__(self, review_output_dir: str):
        self.review_dir = review_output_dir
        os.makedirs(self.review_dir, exist_ok=True)
        self.sch_json = os.path.join(self.review_dir, "schematic.json")
        self.pcb_json = os.path.join(self.review_dir, "pcb.json")
        self.cross_json = os.path.join(self.review_dir, "cross.json")
        self.emc_json = os.path.join(self.review_dir, "emc.json")
        self.thermal_json = os.path.join(self.review_dir, "thermal.json")
        self.gerbers_json = os.path.join(self.review_dir, "gerbers.json")
        self.fab_gate_json = os.path.join(self.review_dir, "fab_gate.json")

    def run_schematic_review(self, sch_file: str) -> Dict[str, Any]:
        """Runs analyze_schematic.py and returns findings."""
        cmd = [
            PYTHON_EXE,
            os.path.join(KICAD_SCRIPTS, "analyze_schematic.py"),
            sch_file,
            "-o", self.sch_json
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        if os.path.isfile(self.sch_json):
            with open(self.sch_json, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"findings": []}

    def run_pcb_review(self, pcb_file: str) -> Dict[str, Any]:
        """Runs analyze_pcb.py with schematic cross-reference."""
        cmd = [
            PYTHON_EXE,
            os.path.join(KICAD_SCRIPTS, "analyze_pcb.py"),
            pcb_file,
            "-o", self.pcb_json,
            "--full"
        ]
        if os.path.isfile(self.sch_json):
            cmd.extend(["--schematic", self.sch_json])

        subprocess.run(cmd, capture_output=True, text=True)
        if os.path.isfile(self.pcb_json):
            with open(self.pcb_json, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"findings": []}

    def run_cross_analysis(self) -> Dict[str, Any]:
        """Runs cross_analysis.py combining schematic and PCB."""
        if not (os.path.isfile(self.sch_json) and os.path.isfile(self.pcb_json)):
            return {"findings": []}
            
        cmd = [
            PYTHON_EXE,
            os.path.join(KICAD_SCRIPTS, "cross_analysis.py"),
            "-s", self.sch_json,
            "-p", self.pcb_json,
            "-o", self.cross_json
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        if os.path.isfile(self.cross_json):
            with open(self.cross_json, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"findings": []}

    def run_emc_review(self) -> Dict[str, Any]:
        """Runs analyze_emc.py pre-compliance risk analysis."""
        if not (os.path.isfile(self.sch_json) and os.path.isfile(self.pcb_json)):
            return {"findings": []}
            
        cmd = [
            PYTHON_EXE,
            os.path.join(EMC_SCRIPTS, "analyze_emc.py"),
            "-s", self.sch_json,
            "-p", self.pcb_json,
            "-o", self.emc_json
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        if os.path.isfile(self.emc_json):
            with open(self.emc_json, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"findings": []}

    def run_thermal_review(self) -> Dict[str, Any]:
        """Runs analyze_thermal.py hotspot estimation."""
        if not (os.path.isfile(self.sch_json) and os.path.isfile(self.pcb_json)):
            return {"findings": []}

        cmd = [
            PYTHON_EXE,
            os.path.join(KICAD_SCRIPTS, "analyze_thermal.py"),
            "-s", self.sch_json,
            "-p", self.pcb_json,
            "-o", self.thermal_json
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        if os.path.isfile(self.thermal_json):
            with open(self.thermal_json, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"findings": []}

    def run_gerber_review(self, gerber_dir: str) -> Dict[str, Any]:
        """Runs analyze_gerbers.py if gerbers exist."""
        if not os.path.isdir(gerber_dir):
            return {"findings": []}
            
        cmd = [
            PYTHON_EXE,
            os.path.join(KICAD_SCRIPTS, "analyze_gerbers.py"),
            gerber_dir,
            "-o", self.gerbers_json
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        if os.path.isfile(self.gerbers_json):
            with open(self.gerbers_json, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"findings": []}

    def run_fab_release_gate(self) -> Dict[str, Any]:
        """Runs fab_release_gate.py evaluating overall production readiness."""
        if not (os.path.isfile(self.sch_json) and os.path.isfile(self.pcb_json)):
            return {"verdict": "BLOCKED", "checks": []}

        cmd = [
            PYTHON_EXE,
            os.path.join(KICAD_SCRIPTS, "fab_release_gate.py"),
            "-s", self.sch_json,
            "-p", self.pcb_json,
            "-o", self.fab_gate_json
        ]
        if os.path.isfile(self.gerbers_json):
            cmd.extend(["-g", self.gerbers_json])
        if os.path.isfile(self.emc_json):
            cmd.extend(["-e", self.emc_json])
        if os.path.isfile(self.thermal_json):
            cmd.extend(["-t", self.thermal_json])

        res = subprocess.run(cmd, capture_output=True, text=True)
        gate_data = {}
        if os.path.isfile(self.fab_gate_json):
            with open(self.fab_gate_json, "r", encoding="utf-8") as f:
                gate_data = json.load(f)
        status = gate_data.get("overall_status", "BLOCKED")
        gate_data["verdict"] = status
        gate_data["stdout"] = res.stdout
        return gate_data

    def classify_all_findings(self) -> Dict[str, Any]:
        """
        Gathers all findings across analyzers and classifies them into:
          1. CRITICAL
          2. ERROR
          3. WARNING
          4. OPTIMIZATION
          5. INFORMATION
          6. NOT_APPLICABLE / FALSE_POSITIVE
        """
        all_findings = []
        for jpath, source in [
            (self.sch_json, "schematic"),
            (self.pcb_json, "pcb"),
            (self.cross_json, "cross"),
            (self.emc_json, "emc"),
            (self.thermal_json, "thermal"),
            (self.gerbers_json, "gerbers")
        ]:
            if os.path.isfile(jpath):
                with open(jpath, "r", encoding="utf-8") as f:
                    try:
                        d = json.load(f)
                        raw = d.get("findings", [])
                        for item in raw:
                            item["source_analyzer"] = source
                            all_findings.append(item)
                    except Exception:
                        pass

        classified = {
            "CRITICAL": [],
            "ERROR": [],
            "WARNING": [],
            "OPTIMIZATION": [],
            "INFORMATION": [],
            "FALSE_POSITIVE": []
        }

        for f in all_findings:
            sev = f.get("severity", "").lower()
            rule_id = f.get("rule_id", "")
            
            if sev in ["critical"]:
                classified["CRITICAL"].append(f)
            elif sev in ["error", "high"]:
                classified["ERROR"].append(f)
            elif sev in ["warning", "medium"]:
                # Check if it is an optimization recommendation
                if rule_id in ["TE-001", "FD-001", "PM-002"]:
                    classified["OPTIMIZATION"].append(f)
                else:
                    classified["WARNING"].append(f)
            elif sev in ["low", "info"]:
                classified["INFORMATION"].append(f)
            else:
                classified["INFORMATION"].append(f)

        return classified
