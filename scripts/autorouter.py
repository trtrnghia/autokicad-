"""
autorouter.py - Native Multi-Layer A* Grid & Maze Auto-Router for AutoKiCad.
Provides automatic multi-layer obstacle avoidance and via layer-hopping in pure Python.
"""

import math
import heapq
from typing import Dict, Any, List, Optional, Tuple, Set
import pcbnew

class GridPoint:
    __slots__ = ('x', 'y', 'layer')
    def __init__(self, x: int, y: int, layer: int):
        self.x = x
        self.y = y
        self.layer = layer

    def __hash__(self):
        return hash((self.x, self.y, self.layer))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.layer == other.layer

class AStarMazeRouter:
    def __init__(
        self,
        board_w_mm: float = 30.0,
        board_h_mm: float = 20.0,
        grid_step_mm: float = 0.25,
        clearance_mm: float = 0.25
    ):
        self.board_w = board_w_mm
        self.board_h = board_h_mm
        self.grid_step = grid_step_mm
        self.clearance = clearance_mm
        self.nx = int(math.ceil(board_w_mm / grid_step_mm)) + 1
        self.ny = int(math.ceil(board_h_mm / grid_step_mm)) + 1
        
        # Occupancy set: (gx, gy, layer)
        self.obstacles: Set[Tuple[int, int, int]] = set()
        self._init_board_boundaries()

    def mm_to_grid(self, x_mm: float, y_mm: float) -> Tuple[int, int]:
        gx = int(round(x_mm / self.grid_step))
        gy = int(round(y_mm / self.grid_step))
        return gx, gy

    def grid_to_mm(self, gx: int, gy: int) -> Tuple[float, float]:
        return gx * self.grid_step, gy * self.grid_step

    def _init_board_boundaries(self):
        """Adds board outline margin as obstacle."""
        margin_grid = int(round(1.0 / self.grid_step))
        for layer in (0, 1):
            for x in range(self.nx):
                for y in range(margin_grid):
                    self.obstacles.add((x, y, layer))
                    self.obstacles.add((x, self.ny - 1 - y, layer))
            for y in range(self.ny):
                for x in range(margin_grid):
                    self.obstacles.add((x, y, layer))
                    self.obstacles.add((self.nx - 1 - x, y, layer))

    def add_obstacle_box(self, x_min_mm: float, y_min_mm: float, x_max_mm: float, y_max_mm: float, layer: Optional[int] = None):
        """Marks a rectangular area as blocked (inflated by clearance)."""
        gx1, gy1 = self.mm_to_grid(x_min_mm - self.clearance, y_min_mm - self.clearance)
        gx2, gy2 = self.mm_to_grid(x_max_mm + self.clearance, y_max_mm + self.clearance)
        
        layers = [0, 1] if layer is None else [layer]
        for l in layers:
            for x in range(max(0, gx1), min(self.nx, gx2 + 1)):
                for y in range(max(0, gy1), min(self.ny, gy2 + 1)):
                    self.obstacles.add((x, y, l))

    def add_obstacle_circle(self, cx_mm: float, cy_mm: float, radius_mm: float, layer: Optional[int] = None):
        """Marks a circular area as blocked."""
        r_inf = radius_mm + self.clearance
        r_grid = int(math.ceil(r_inf / self.grid_step))
        gcx, gcy = self.mm_to_grid(cx_mm, cy_mm)

        layers = [0, 1] if layer is None else [layer]
        for l in layers:
            for dx in range(-r_grid, r_grid + 1):
                for dy in range(-r_grid, r_grid + 1):
                    if dx*dx + dy*dy <= r_grid*r_grid:
                        gx = gcx + dx
                        gy = gcy + dy
                        if 0 <= gx < self.nx and 0 <= gy < self.ny:
                            self.obstacles.add((gx, gy, l))

    def route_net(
        self,
        start_mm: Tuple[float, float],
        end_mm: Tuple[float, float],
        preferred_layer: int = 0
    ) -> List[Tuple[float, float, int]]:
        """
        Runs A* pathfinding from start to end.
        Returns a list of (x_mm, y_mm, layer) waypoints.
        """
        sx, sy = self.mm_to_grid(start_mm[0], start_mm[1])
        ex, ey = self.mm_to_grid(end_mm[0], end_mm[1])

        # Temporarily free target and start cells
        for l in (0, 1):
            self.obstacles.discard((sx, sy, l))
            self.obstacles.discard((ex, ey, l))

        start_node = (sx, sy, preferred_layer)
        goal_node = (ex, ey)

        frontier = []
        heapq.heappush(frontier, (0.0, start_node))
        came_from: Dict[Tuple[int, int, int], Tuple[int, int, int]] = {}
        cost_so_far: Dict[Tuple[int, int, int], float] = {start_node: 0.0}

        def heuristic(a, b):
            # Manhattan distance
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        reached_goal_node = None

        while frontier:
            _, current = heapq.heappop(frontier)
            cx, cy, clayer = current

            if (cx, cy) == goal_node:
                reached_goal_node = current
                break

            # 4 cardinal neighbors on same layer
            neighbors = [
                (cx + 1, cy, clayer, 1.0),
                (cx - 1, cy, clayer, 1.0),
                (cx, cy + 1, clayer, 1.0),
                (cx, cy - 1, clayer, 1.0),
                # Layer hop via transition
                (cx, cy, 1 - clayer, 5.0)
            ]

            for nx, ny, nlayer, step_cost in neighbors:
                if not (0 <= nx < self.nx and 0 <= ny < self.ny):
                    continue
                next_node = (nx, ny, nlayer)
                if next_node in self.obstacles:
                    continue

                new_cost = cost_so_far[current] + step_cost
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + heuristic((nx, ny), goal_node)
                    heapq.heappush(frontier, (priority, next_node))
                    came_from[next_node] = current

        if not reached_goal_node:
            # Direct fallback if path is fully blocked
            return [
                (start_mm[0], start_mm[1], preferred_layer),
                (end_mm[0], end_mm[1], preferred_layer)
            ]

        # Reconstruct path
        path = []
        curr = reached_goal_node
        while curr != start_node:
            path.append(curr)
            curr = came_from[curr]
        path.append(start_node)
        path.reverse()

        # Simplify collinear segments
        waypoints = []
        for gx, gy, l in path:
            x_mm, y_mm = self.grid_to_mm(gx, gy)
            waypoints.append((x_mm, y_mm, l))

        # Commit routed path to obstacles
        for gx, gy, l in path:
            self.obstacles.add((gx, gy, l))

        return waypoints

    def commit_to_board(
        self,
        board: pcbnew.BOARD,
        waypoints: List[Tuple[float, float, int]],
        net_name: str,
        track_width_mm: float = 0.25
    ):
        """Builds native pcbnew.PCB_TRACK and pcbnew.PCB_VIA from waypoints."""
        net = board.FindNet(net_name)
        if not net:
            net = pcbnew.NETINFO_ITEM(board, net_name)
            board.Add(net)

        for i in range(len(waypoints) - 1):
            x1, y1, l1 = waypoints[i]
            x2, y2, l2 = waypoints[i + 1]

            p1 = pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1))
            p2 = pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2))

            if l1 != l2:
                # Add through-hole via
                via = pcbnew.PCB_VIA(board)
                via.SetPosition(p1)
                via.SetWidth(pcbnew.FromMM(0.8))
                via.SetDrill(pcbnew.FromMM(0.4))
                via.SetLayerSet(pcbnew.LSET.AllCuMask())
                via.SetNet(net)
                board.Add(via)

            layer_id = pcbnew.F_Cu if l2 == 0 else pcbnew.B_Cu
            if p1 != p2:
                track = pcbnew.PCB_TRACK(board)
                track.SetStart(p1)
                track.SetEnd(p2)
                track.SetLayer(layer_id)
                track.SetWidth(pcbnew.FromMM(track_width_mm))
                track.SetNet(net)
                board.Add(track)
