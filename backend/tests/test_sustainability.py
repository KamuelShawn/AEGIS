from app.algorithms.sustainability import calculate_sustainability_score


def test_perfect_inputs_give_100():
    result = calculate_sustainability_score(environment=100, resources=100, infrastructure=100, social=100, pollution=100)
    assert result.overall == 100.0


def test_zero_inputs_give_0():
    result = calculate_sustainability_score(environment=0, resources=0, infrastructure=0, social=0, pollution=0)
    assert result.overall == 0.0


def test_weakest_factor_identified():
    result = calculate_sustainability_score(environment=90, resources=20, infrastructure=85, social=80, pollution=70)
    assert result.weakest_factor == "resources"


def test_contributions_sum_to_overall():
    result = calculate_sustainability_score(environment=82, resources=64, infrastructure=78, social=71, pollution=69)
    total = sum(f.contribution for f in result.factors)
    assert abs(total - result.overall) < 0.01


def test_explanation_names_weakest_factor():
    result = calculate_sustainability_score(environment=90, resources=20, infrastructure=85, social=80, pollution=70)
    assert "resources" in result.explanation.lower()
