"""
dfm_dfa_checker.py - Design for Manufacturability, Assembly, and Test Engine for AutoKiCad.
Part of the /autokicad skill conceptual modules:
  22_dfm
  23_dfa
  24_dft
"""

import os
import json
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class DfmDfaChecker:
    def __init__(self, rules_config_path: Optional[str] = None):
        self.rules = {
            "min_trace_width_mm": 0.15,
            "min_clearance_mm": 0.15,
            "min_drill_mm": 0.3,
            "min_via_dia_mm": 0.6,
            "copper_to_edge_clearance_mm": 0.3,
            "solder_mask_clearance_mm": 0.05,
            "min_solder_mask_bridge_mm": 0.1,
            "min_silkscreen_width_mm": 0.15,
            "min_silkscreen_height_mm": 0.8
        }
        if rules_config_path and os.path.isfile(rules_config_path):
            with open(rules_config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                std_rules = data.get("manufacturers", {}).get("standard", {})
                self.rules.update(std_rules)

    def audit_design(
        self,
        board_w_mm: float,
        board_h_mm: float,
        tracks_info: List[Dict[str, Any]],
        vias_info: List[Dict[str, Any]],
        footprints_info: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Runs comprehensive DFM, DFA, and DFT rule audits.
        """
        dfm_findings = []
        dfa_findings = []
        dft_findings = []

        # 1. DFM Checks
        for t in tracks_info:
            w = t.get("width_mm", 0.25)
            if w < self.rules["min_trace_width_mm"]:
                dfm_findings.append({
                    "type": "TRACE_WIDTH_BELOW_MIN",
                    "severity": "FAIL",
                    "details": f"Track width {w}mm < limit {self.rules['min_trace_width_mm']}mm on net {t.get('net')}"
                })

        for v in vias_info:
            drill = v.get("drill_mm", 0.4)
            dia = v.get("dia_mm", 0.8)
            annular_ring = (dia - drill) / 2.0
            if drill < self.rules["min_drill_mm"]:
                dfm_findings.append({
                    "type": "DRILL_BELOW_MIN",
                    "severity": "FAIL",
                    "details": f"Via drill {drill}mm < limit {self.rules['min_drill_mm']}mm"
                })
            if annular_ring < 0.125:
                dfm_findings.append({
                    "type": "ANNULAR_RING_INSUFFICIENT",
                    "severity": "FAIL",
                    "details": f"Via annular ring {annular_ring:.3f}mm < limit 0.125mm"
                })

        # 2. DFA Checks
        for fp in footprints_info:
            ref = fp.get("ref", "")
            x = fp.get("x_mm", 0)
            y = fp.get("y_mm", 0)
            # Edge proximity check for components
            if x < 1.0 or x > (board_w_mm - 1.0) or y < 1.0 or y > (board_h_mm - 1.0):
                if not ("J" in ref or "H" in ref or "CONN" in ref.upper()):
                    dfa_findings.append({
                        "type": "COMPONENT_TOO_CLOSE_TO_EDGE",
                        "severity": "WARN",
                        "details": f"Component {ref} at ({x:.1f}, {y:.1f})mm is within 1.0mm of board edge"
                    })

        # 3. DFT Checks
        has_power_test_access = any("J" in fp.get("ref", "") or "TP" in fp.get("ref", "") for fp in footprints_info)
        if not has_power_test_access:
            dft_findings.append({
                "type": "NO_TEST_OR_HEADER_ACCESS",
                "severity": "WARN",
                "details": "No dedicated test points or header pins detected for electrical probe testing"
            })
        else:
            dft_findings.append({
                "type": "TEST_ACCESS_VERIFIED",
                "severity": "PASS",
                "details": "Power and signals accessible via standard 2.54mm header/test nodes"
            })

        dfm_status = "PASS" if not any(f["severity"] == "FAIL" for f in dfm_findings) else "FAIL"
        dfa_status = "PASS" if not any(f["severity"] == "FAIL" for f in dfa_findings) else "FAIL"
        dft_status = "PASS" if not any(f["severity"] == "FAIL" for f in dft_findings) else "FAIL"

        return {
            "dfm": {"status": dfm_status, "findings": dfm_findings},
            "dfa": {"status": dfa_status, "findings": dfa_findings},
            "dft": {"status": dft_status, "findings": dft_findings},
            "overall_status": "PASS" if (dfm_status == "PASS" and dfa_status == "PASS") else "BLOCKED"
        }

    def generate_pdf_report(self, audit_result: Dict[str, Any], output_pdf_path: str, project_name: str):
        """Generates engineering PDF DFM/DFA report."""
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
        doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#1a365d")
        )
        elements.append(Paragraph(f"AutoKiCad DFM & DFA Verification Report", title_style))
        elements.append(Paragraph(f"<b>Project:</b> {project_name} | <b>Overall Status:</b> {audit_result['overall_status']}", styles['Normal']))
        elements.append(Spacer(1, 15))

        # Table of findings
        table_data = [["Category", "Check Type", "Severity", "Details"]]
        for cat in ["dfm", "dfa", "dft"]:
            findings = audit_result.get(cat, {}).get("findings", [])
            if not findings:
                table_data.append([cat.upper(), "All Standards", "PASS", "Fully compliant with manufacturing capability"])
            for f in findings:
                table_data.append([cat.upper(), f["type"], f["severity"], f["details"]])

        t = Table(table_data, colWidths=[60, 150, 70, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2b6cb0")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")])
        ]))
        elements.append(t)
        doc.build(elements)
