from app.algorithms.route_optimization import RouteCandidate, astar_path, score_routes


def test_astar_finds_direct_path_on_uniform_grid():
    grid = [[1.0] * 5 for _ in range(5)]
    result = astar_path(grid, (0, 0), (4, 4))
    assert result.found
    assert result.path[0] == (0, 0)
    assert result.path[-1] == (4, 4)


def test_astar_avoids_high_cost_region():
    grid = [[1.0] * 5 for _ in range(5)]
    for x in range(5):
        grid[2][x] = 1000.0  # wall of high cost across the middle row
    grid[2][0] = 1.0  # leave one cheap gap at the edge
    result = astar_path(grid, (0, 0), (4, 4))
    assert result.found
    assert (0, 2) in result.path  # routed through the cheap gap


def test_astar_no_path_when_unreachable():
    grid = [[1.0]]
    result = astar_path(grid, (0, 0), (0, 0))
    assert result.found
    assert result.total_cost == 0.0


def test_route_scoring_ranks_lower_impact_higher():
    low_impact = RouteCandidate(
        id="B", name="Route B", distance_km=40, construction_cost_cr=200,
        environmental_impact=15, social_impact=20, connectivity_benefit=70, terrain_difficulty=30,
    )
    high_impact_cheap = RouteCandidate(
        id="A", name="Route A", distance_km=30, construction_cost_cr=100,
        environmental_impact=80, social_impact=40, connectivity_benefit=75, terrain_difficulty=20,
    )
    scored = score_routes([high_impact_cheap, low_impact])
    # With default weights, environmental_impact carries the most weight (30),
    # so the low-impact route should win despite costing more.
    assert scored[0].candidate.id == "B"
    assert scored[0].rank == 1
    assert "preferred" in scored[0].explanation.lower()


def test_route_scoring_respects_custom_weights_favoring_cost():
    cheap_dirty = RouteCandidate(
        id="A", name="Route A", distance_km=30, construction_cost_cr=50,
        environmental_impact=90, social_impact=50, connectivity_benefit=60, terrain_difficulty=20,
    )
    expensive_clean = RouteCandidate(
        id="C", name="Route C", distance_km=60, construction_cost_cr=500,
        environmental_impact=5, social_impact=5, connectivity_benefit=60, terrain_difficulty=50,
    )
    # Weight cost extremely heavily, everything else near zero.
    weights = {"economic_cost": 1000, "environmental_impact": 1, "social_impact": 1, "connectivity_benefit": 1}
    scored = score_routes([cheap_dirty, expensive_clean], weights=weights)
    assert scored[0].candidate.id == "A"


def test_empty_candidates_returns_empty():
    assert score_routes([]) == []
