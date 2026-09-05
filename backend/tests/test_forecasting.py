from app.algorithms.forecasting import forecast_exponential_smoothing, forecast_linear


def test_linear_forecast_returns_range_not_point():
    result = forecast_linear([2000, 2005, 2010, 2015, 2020], [100, 90, 80, 70, 60], target_years=[2030])
    point = result.points[0]
    assert point.low < point.mid < point.high


def test_linear_forecast_confidence_high_for_clean_trend():
    result = forecast_linear([2000, 2005, 2010, 2015], [100, 90, 80, 70], target_years=[2020])
    assert result.confidence == "HIGH"
    assert result.r_squared > 0.9


def test_linear_forecast_respects_min_value():
    result = forecast_linear([2000, 2005, 2010], [30, 15, 2], target_years=[2030], min_value=0)
    assert result.points[0].low >= 0


def test_uncertainty_widens_with_distance():
    result = forecast_linear([2000, 2005, 2010, 2015, 2020], [100, 95, 85, 82, 70], target_years=[2025, 2050])
    near, far = result.points
    near_band = near.high - near.low
    far_band = far.high - far.low
    assert far_band > near_band


def test_exponential_smoothing_basic():
    result = forecast_exponential_smoothing([10, 12, 11, 13, 14], periods_ahead=3)
    assert len(result.points) == 3
    assert result.method == "exponential_smoothing"
