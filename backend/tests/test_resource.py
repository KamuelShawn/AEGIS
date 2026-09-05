from app.algorithms.resource import SustainabilityStatus, calculate_resource_balance


def test_safe_when_extraction_well_below_limit():
    result = calculate_resource_balance(available_reserve=1000, annual_replenishment=100, current_extraction=50)
    assert result.status == SustainabilityStatus.SAFE
    assert result.years_to_depletion is None  # replenishment exceeds extraction


def test_severe_when_extraction_far_exceeds_limit():
    result = calculate_resource_balance(available_reserve=500, annual_replenishment=100, current_extraction=200)
    assert result.status == SustainabilityStatus.SEVERE
    assert result.years_to_depletion is not None
    # net change = 100 - 200 = -100/yr; 500/100 = 5 years
    assert result.years_to_depletion == 5.0


def test_warning_band():
    result = calculate_resource_balance(available_reserve=1000, annual_replenishment=100, current_extraction=85)
    # sustainable limit = 90 (0.9 * 100); ratio = 85/90 = 0.944 -> WARNING
    assert result.status == SustainabilityStatus.WARNING


def test_explanation_mentions_depletion_when_applicable():
    result = calculate_resource_balance(available_reserve=500, annual_replenishment=100, current_extraction=200)
    assert "deplete" in result.explanation.lower()
