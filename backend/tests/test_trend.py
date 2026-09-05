from app.algorithms.trend import Direction, analyze_trend


def test_decreasing_trend_detected():
    years = [2000, 2005, 2010, 2015, 2020]
    values = [100, 90, 80, 70, 60]
    result = analyze_trend(years, values)
    assert result.direction == Direction.DECREASING
    assert result.annual_rate < 0
    assert result.r_squared > 0.95


def test_increasing_trend_detected():
    years = [2000, 2005, 2010]
    values = [10, 20, 30]
    result = analyze_trend(years, values)
    assert result.direction == Direction.INCREASING


def test_stable_trend_detected():
    years = [2000, 2005, 2010]
    values = [100, 100.1, 99.9]
    result = analyze_trend(years, values)
    assert result.direction == Direction.STABLE


def test_accelerating_decline():
    years = [2000, 2005, 2010, 2015, 2020]
    values = [100, 98, 94, 84, 60]  # decline speeds up in the second half
    result = analyze_trend(years, values)
    assert result.direction == Direction.DECREASING
    assert result.is_accelerating is True


def test_mismatched_lengths_raise():
    import pytest

    with pytest.raises(ValueError):
        analyze_trend([2000, 2001], [1.0])
