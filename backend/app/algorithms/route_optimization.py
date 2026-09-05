"""
Infrastructure route optimization.

Two pieces:
1. A weighted-grid Dijkstra/A* pathfinder that can generate candidate routes
   over a cost surface (terrain difficulty + environmental penalty).
2. A multi-objective scorer that ranks already-known candidate routes
   (e.g. from OSRM/Mapbox Directions, or from part 1) against user-adjustable
   weights — this is what powers the 0-100 sliders in the UI and must be a
   real recalculation, not decorative.
"""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Part 1: grid-based pathfinding (Dijkstra with an A* admissible heuristic)
# ---------------------------------------------------------------------------

Coord = tuple[int, int]


@dataclass
class GridPathResult:
    path: list[Coord]
    total_cost: float
    found: bool


def astar_path(
    cost_grid: list[list[float]],
    start: Coord,
    goal: Coord,
) -> GridPathResult:
    """
    cost_grid[y][x] = traversal cost of that cell (>= 0; use a very large
    number, not infinity, for impassable cells like protected core zones).
    8-directional movement, diagonal cost scaled by sqrt(2).
    """
    height = len(cost_grid)
    width = len(cost_grid[0]) if height else 0

    def in_bounds(c: Coord) -> bool:
        return 0 <= c[0] < width and 0 <= c[1] < height

    def heuristic(a: Coord, b: Coord) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def neighbors(c: Coord):
        x, y = c
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nc = (x + dx, y + dy)
                if in_bounds(nc):
                    step_cost = cost_grid[nc[1]][nc[0]] * (math.sqrt(2) if dx and dy else 1.0)
                    yield nc, step_cost

    open_heap: list[tuple[float, Coord]] = [(0.0, start)]
    came_from: dict[Coord, Coord] = {}
    g_score: dict[Coord, float] = {start: 0.0}
    visited: set[Coord] = set()

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return GridPathResult(path=path, total_cost=g_score[goal], found=True)

        for neighbor, step_cost in neighbors(current):
            tentative_g = g_score[current] + step_cost
            if tentative_g < g_score.get(neighbor, math.inf):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_heap, (f_score, neighbor))

    return GridPathResult(path=[], total_cost=math.inf, found=False)


# ---------------------------------------------------------------------------
# Part 2: multi-objective route scoring (economic / environmental / social /
# connectivity), matching the 0-100 weight sliders in the spec.
# ---------------------------------------------------------------------------

DEFAULT_ROUTE_WEIGHTS = {
    "economic_cost": 25,
    "environmental_impact": 30,
    "social_impact": 25,
    "connectivity_benefit": 20,
}


@dataclass
class RouteCandidate:
    id: str
    name: str
    distance_km: float
    construction_cost_cr: float  # crore INR, illustrative unit
    environmental_impact: float  # 0-100, higher = worse
    social_impact: float  # 0-100, higher = worse (displacement, community disruption)
    connectivity_benefit: float  # 0-100, higher = better
    terrain_difficulty: float  # 0-100, higher = harder
    affected_ecosystems: list[str] = field(default_factory=list)
    affected_villages: list[str] = field(default_factory=list)


@dataclass
class ScoredRoute:
    candidate: RouteCandidate
    normalized_cost_score: float  # 0-100, higher = worse (cost)
    weighted_score: float  # lower = better overall (it's a "badness" score)
    rank: int
    explanation: str


def score_routes(
    candidates: list[RouteCandidate],
    weights: dict[str, float] | None = None,
) -> list[ScoredRoute]:
    """
    Lower weighted_score = better route. Cost is normalized 0-100 relative to
    the most expensive candidate so weights are comparable to the other 0-100
    "badness" dimensions.
    """
    if not candidates:
        return []
    w = {**DEFAULT_ROUTE_WEIGHTS, **(weights or {})}
    total_weight = sum(w.values()) or 1.0

    max_cost = max(c.construction_cost_cr for c in candidates) or 1.0

    scored: list[ScoredRoute] = []
    for c in candidates:
        cost_score = (c.construction_cost_cr / max_cost) * 100
        connectivity_penalty = 100 - c.connectivity_benefit  # invert so higher = worse, consistent scale

        weighted = (
            cost_score * w["economic_cost"]
            + c.environmental_impact * w["environmental_impact"]
            + c.social_impact * w["social_impact"]
            + connectivity_penalty * w["connectivity_benefit"]
        ) / total_weight

        scored.append(
            ScoredRoute(
                candidate=c,
                normalized_cost_score=round(cost_score, 1),
                weighted_score=round(weighted, 2),
                rank=0,
                explanation="",
            )
        )

    scored.sort(key=lambda s: s.weighted_score)
    for i, s in enumerate(scored, start=1):
        s.rank = i

    # Explain the winner in terms of the dominant weight, per spec example.
    if scored:
        best = scored[0]
        dominant_factor = max(w, key=lambda k: w[k])
        if len(scored) > 1:
            runner_up = scored[1]
            cost_diff_pct = (
                (best.candidate.construction_cost_cr - runner_up.candidate.construction_cost_cr)
                / (runner_up.candidate.construction_cost_cr or 1)
                * 100
            )
            cost_clause = f"costs {abs(cost_diff_pct):.0f}% {'more' if cost_diff_pct > 0 else 'less'} than {runner_up.candidate.name}"
            env_diff_pct = runner_up.candidate.environmental_impact - best.candidate.environmental_impact
            env_clause = (
                f"reduces environmental exposure by {abs(env_diff_pct):.0f} points"
                if env_diff_pct > 0
                else f"increases environmental exposure by {abs(env_diff_pct):.0f} points"
            )
            best.explanation = (
                f"{best.candidate.name} is currently preferred because {dominant_factor.replace('_', ' ')} "
                f"has been weighted most heavily. It {cost_clause} but {env_clause}."
            )
        else:
            best.explanation = f"{best.candidate.name} is the only candidate route."
        for s in scored[1:]:
            s.explanation = f"Ranked #{s.rank} — higher weighted impact than {best.candidate.name} under current weights."

    return scored
