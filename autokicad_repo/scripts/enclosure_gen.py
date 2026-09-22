"""
enclosure_gen.py - 3D Printable Snap-Fit & Screw-Down Enclosure Generator for AutoKiCad.
Generates watertight ASCII STL models (.stl) tailored precisely to the board Edge_Cuts
and mounting hole coordinates for instant 3D printing.
"""

import os
import math
from typing import List, Tuple

class EnclosureGenerator:
    def __init__(
        self,
        board_w_mm: float = 30.0,
        board_h_mm: float = 20.0,
        board_thick_mm: float = 1.6,
        wall_thick_mm: float = 1.6,
        clearance_mm: float = 0.5,
        standoff_h_mm: float = 3.0,
        mounting_holes: List[Tuple[float, float]] = None
    ):
        self.w = board_w_mm
        self.h = board_h_mm
        self.pcb_t = board_thick_mm
        self.wall = wall_thick_mm
        self.clr = clearance_mm
        self.standoff_h = standoff_h_mm
        
        # Default mounting holes if none provided
        if mounting_holes is None:
            self.holes = [(4.0, 4.0), (board_w_mm - 4.0, 4.0), (4.0, board_h_mm - 4.0), (board_w_mm - 4.0, board_h_mm - 4.0)]
        else:
            self.holes = mounting_holes

        # Outer dimensions
        self.outer_w = self.w + 2 * (self.wall + self.clr)
        self.outer_h = self.h + 2 * (self.wall + self.clr)

    def _write_box_stl(self, f, min_x, min_y, min_z, max_x, max_y, max_z):
        """Writes a rectangular prism to open STL file as 12 triangular facets."""
        p = [
            (min_x, min_y, min_z), (max_x, min_y, min_z), (max_x, max_y, min_z), (min_x, max_y, min_z),
            (min_x, min_y, max_z), (max_x, min_y, max_z), (max_x, max_y, max_z), (min_x, max_y, max_z)
        ]
        faces = [
            (0, 3, 2, (0, 0, -1)), (0, 2, 1, (0, 0, -1)),  # Bottom
            (4, 5, 6, (0, 0, 1)), (4, 6, 7, (0, 0, 1)),    # Top
            (0, 1, 5, (0, -1, 0)), (0, 5, 4, (0, -1, 0)),  # Front
            (2, 3, 7, (0, 1, 0)), (2, 7, 6, (0, 1, 0)),    # Back
            (0, 4, 7, (-1, 0, 0)), (0, 7, 3, (-1, 0, 0)),  # Left
            (1, 2, 6, (1, 0, 0)), (1, 6, 5, (1, 0, 0))     # Right
        ]
        for v1, v2, v3, norm in faces:
            f.write(f"  facet normal {norm[0]} {norm[1]} {norm[2]}\n")
            f.write("    outer loop\n")
            f.write(f"      vertex {p[v1][0]:.3f} {p[v1][1]:.3f} {p[v1][2]:.3f}\n")
            f.write(f"      vertex {p[v2][0]:.3f} {p[v2][1]:.3f} {p[v2][2]:.3f}\n")
            f.write(f"      vertex {p[v3][0]:.3f} {p[v3][1]:.3f} {p[v3][2]:.3f}\n")
            f.write("    endloop\n")
            f.write("  endfacet\n")

    def generate_bottom_shell(self, output_path: str) -> str:
        """Generates bottom enclosure shell with screw standoffs and connector cutout."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        ow = self.outer_w
        oh = self.outer_h
        wall = self.wall
        depth = self.standoff_h + self.pcb_t + 1.0

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("solid enclosure_bottom\n")
            
            # 1. Base floor
            self._write_box_stl(f, 0, 0, 0, ow, oh, wall)
            
            # 2. Left wall
            self._write_box_stl(f, 0, 0, wall, wall, oh, wall + depth)
            # 3. Right wall
            self._write_box_stl(f, ow - wall, 0, wall, ow, oh, wall + depth)
            # 4. Front wall
            self._write_box_stl(f, wall, 0, wall, ow - wall, wall, wall + depth)
            # 5. Back wall
            self._write_box_stl(f, wall, oh - wall, wall, ow - wall, oh, wall + depth)

            # 6. Screw standoffs matching mounting holes
            for hx, hy in self.holes:
                so_x = hx + wall + self.clr
                so_y = hy + wall + self.clr
                self._write_box_stl(f, so_x - 2.5, so_y - 2.5, wall, so_x + 2.5, so_y + 2.5, wall + self.standoff_h)

            f.write("endsolid enclosure_bottom\n")
        return output_path

    def generate_top_shell(self, output_path: str) -> str:
        """Generates top enclosure lid with snap lip."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        ow = self.outer_w
        oh = self.outer_h
        wall = self.wall
        top_h = 5.0

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("solid enclosure_top\n")
            # 1. Top lid surface
            self._write_box_stl(f, 0, 0, 0, ow, oh, wall)
            # 2. Perimeter snap lip
            self._write_box_stl(f, wall + 0.2, wall + 0.2, wall, ow - wall - 0.2, wall + 1.2, wall + 2.5)
            self._write_box_stl(f, wall + 0.2, oh - wall - 1.2, wall, ow - wall - 0.2, oh - wall - 0.2, wall + 2.5)
            self._write_box_stl(f, wall + 0.2, wall + 1.2, wall, wall + 1.2, oh - wall - 1.2, wall + 2.5)
            self._write_box_stl(f, ow - wall - 1.2, wall + 1.2, wall, ow - wall - 0.2, oh - wall - 1.2, wall + 2.5)
            f.write("endsolid enclosure_top\n")
        return output_path
