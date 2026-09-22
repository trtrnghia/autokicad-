"""
drc_erc_runner.py - KiCad ERC, DRC, and Connectivity Verification Engine for AutoKiCad.
Part of the /autokicad skill conceptual modules:
  20_erc
  21_drc
  27_verification
  28_repair
"""

import os
import json
import subprocess
from typing import Dict, Any, List, Optional

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"

def run_erc(sch_file: str, report_json_path: str) -> Dict[str, Any]:
    """
    Executes KiCad electrical rules check (ERC) headlessly and returns structured results.
    """
    os.makedirs(os.path.dirname(report_json_path), exist_ok=True)
    cmd = [
        KICAD_CLI,
        "sch", "erc",
        "--format", "json",
        "--output", report_json_path,
        sch_file
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    
    if not os.path.isfile(report_json_path):
        return {
            "status": "FAILED_TO_RUN",
            "error": res.stderr or res.stdout,
            "violations_count": 0,
            "violations": []
        }
        
    with open(report_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    all_violations = []
    for sheet in data.get("sheets", []):
        all_violations.extend(sheet.get("violations", []))
        
    error_count = sum(1 for v in all_violations if v.get("severity") == "error")
    warning_count = sum(1 for v in all_violations if v.get("severity") == "warning")
    
    status = "PASSED"
    if error_count > 0:
        status = "ERRORS_FOUND"
    elif warning_count > 0:
        status = "WARNINGS_FOUND"
        
    return {
        "status": status,
        "total_violations": len(all_violations),
        "errors": error_count,
        "warnings": warning_count,
        "violations": all_violations,
        "report_file": report_json_path
    }

def run_drc(pcb_file: str, report_json_path: str, refill_zones: bool = True) -> Dict[str, Any]:
    """
    Executes KiCad design rules check (DRC) headlessly and returns structured results.
    """
    os.makedirs(os.path.dirname(report_json_path), exist_ok=True)
    cmd = [
        KICAD_CLI,
        "pcb", "drc",
        "--format", "json",
        "--output", report_json_path
    ]
    if refill_zones:
        cmd.append("--refill-zones")
    cmd.append(pcb_file)
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    
    if not os.path.isfile(report_json_path):
        return {
            "status": "FAILED_TO_RUN",
            "error": res.stderr or res.stdout,
            "violations_count": 0,
            "unconnected_count": 0,
            "violations": [],
            "unconnected_items": []
        }
        
    with open(report_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    violations = data.get("violations", [])
    unconnected = data.get("unconnected_items", [])
    
    error_count = sum(1 for v in violations if v.get("severity") == "error")
    warning_count = sum(1 for v in violations if v.get("severity") == "warning")
    
    status = "PASSED"
    if len(unconnected) > 0:
        status = "UNCONNECTED_ITEMS"
    elif error_count > 0:
        status = "ERRORS_FOUND"
    elif warning_count > 0:
        status = "WARNINGS_FOUND"
        
    return {
        "status": status,
        "total_violations": len(violations),
        "errors": error_count,
        "warnings": warning_count,
        "unconnected_count": len(unconnected),
        "violations": violations,
        "unconnected_items": unconnected,
        "report_file": report_json_path
    }

def generate_verification_summary(erc_res: Dict[str, Any], drc_res: Dict[str, Any]) -> str:
    """Formats an engineering verification summary."""
    lines = [
        "============================================================",
        "AUTOKICAD DESIGN VERIFICATION REPORT",
        "============================================================",
        f"ERC Status:          {erc_res.get('status')}",
        f"  Total Violations:  {erc_res.get('total_violations')}",
        f"  Errors:            {erc_res.get('errors')}",
        f"  Warnings:          {erc_res.get('warnings')}",
        "",
        f"DRC Status:          {drc_res.get('status')}",
        f"  Total Violations:  {drc_res.get('total_violations')}",
        f"  Errors:            {drc_res.get('errors')}",
        f"  Warnings:          {drc_res.get('warnings')}",
        f"  Unconnected Items: {drc_res.get('unconnected_count')}",
        "============================================================",
    ]
    if erc_res.get("total_violations", 0) > 0:
        lines.append("ERC VIOLATIONS:")
        for v in erc_res.get("violations", []):
            lines.append(f"  [{v.get('severity', '').upper()}] {v.get('type')}: {v.get('description')}")
            
    if drc_res.get("total_violations", 0) > 0:
        lines.append("DRC VIOLATIONS:")
        for v in drc_res.get("violations", []):
            lines.append(f"  [{v.get('severity', '').upper()}] {v.get('type')}: {v.get('description')}")

    if drc_res.get("unconnected_count", 0) > 0:
        lines.append("UNCONNECTED NETS / ITEMS:")
        for u in drc_res.get("unconnected_items", []):
            lines.append(f"  {u.get('description')}")

    return "\n".join(lines)
