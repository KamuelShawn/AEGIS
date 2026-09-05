from app.algorithms.risk import RiskLevel, calculate_risk, project_threshold_year


def test_low_pressure_is_safe():
    result = calculate_risk(
        environmental_degradation=5,
        resource_pressure=5,
        development_pressure=5,
        pollution=5,
        population_pressure=5,
    )
    assert result.level == RiskLevel.SAFE
    assert result.score < 30


def test_high_pressure_is_severe():
    result = calculate_risk(
        environmental_degradation=95,
        resource_pressure=90,
        development_pressure=95,
        pollution=85,
        population_pressure=80,
    )
    assert result.level == RiskLevel.SEVERE
    assert result.score >= 80


def test_factor_contributions_sum_to_score():
    result = calculate_risk(
        environmental_degradation=60,
        resource_pressure=40,
        development_pressure=50,
        pollution=30,
        population_pressure=20,
    )
    total_contribution = sum(f.contribution for f in result.factors)
    assert abs(total_contribution - result.score) < 0.01


def test_top_driver_identified():
    result = calculate_risk(
        environmental_degradation=90,
        resource_pressure=10,
        development_pressure=10,
        pollution=10,
        population_pressure=10,
    )
    assert result.top_driver == "environmental_degradation"


def test_values_clamped_to_0_100():
    result = calculate_risk(
        environmental_degradation=150,
        resource_pressure=-20,
        development_pressure=0,
        pollution=0,
        population_pressure=0,
    )
    env_factor = next(f for f in result.factors if f.name == "environmental_degradation")
    res_factor = next(f for f in result.factors if f.name == "resource_pressure")
    assert env_factor.value == 100
    assert res_factor.value == 0


def test_threshold_projection_future():
    year = project_threshold_year(current_value=80, annual_rate=-2, threshold=50, current_year=2026)
    assert year == 2026 + 15


def test_threshold_projection_never_reached():
    year = project_threshold_year(current_value=80, annual_rate=2, threshold=50, current_year=2026)
    assert year is None
