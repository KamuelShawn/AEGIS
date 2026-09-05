from app.algorithms.recommendations import (
    collect_recommendations,
    recommend_for_forest_decline,
    recommend_for_industrial_population_proximity,
    recommend_for_route_forest_intersection,
    recommend_for_water_stress,
)


def test_no_recommendation_when_safe():
    assert recommend_for_water_stress(0.5) is None


def test_recommendation_when_water_stressed():
    rec = recommend_for_water_stress(1.2)
    assert rec is not None
    assert rec.severity == "CRITICAL"
    assert len(rec.interventions) >= 3


def test_severe_water_stress():
    rec = recommend_for_water_stress(1.5)
    assert rec.severity == "SEVERE"


def test_route_forest_intersection_none_when_zero():
    assert recommend_for_route_forest_intersection(0) is None


def test_route_forest_intersection_flagged():
    rec = recommend_for_route_forest_intersection(3.2)
    assert rec is not None
    assert "redirect" in rec.interventions[0].lower()


def test_industrial_proximity_flagged():
    rec = recommend_for_industrial_population_proximity(90, distance_km=1.2)
    assert rec is not None
    assert rec.severity == "SEVERE"


def test_forest_decline_only_when_negative():
    assert recommend_for_forest_decline(2.0, None) is None
    rec = recommend_for_forest_decline(-4.0, 2040)
    assert rec is not None
    assert "2040" in rec.rationale


def test_collect_recommendations_aggregates_available_signals():
    recs = collect_recommendations(extraction_ratio=1.4, annual_rate_pct=-2.0, threshold_year=2035)
    problems = [r.problem for r in recs]
    assert any("water" in p.lower() or "extraction" in p.lower() for p in problems)
    assert any("forest" in p.lower() for p in problems)
