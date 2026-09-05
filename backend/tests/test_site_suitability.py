from app.algorithms.site_suitability import SiteCandidate, score_sites


def test_best_site_ranked_first():
    good = SiteCandidate(
        id="1", name="Site A", water_availability=90, infrastructure_access=85,
        population_proximity=10, environmental_sensitivity=5, pollution_risk=10, land_suitability=90,
    )
    bad = SiteCandidate(
        id="2", name="Site B", water_availability=20, infrastructure_access=20,
        population_proximity=90, environmental_sensitivity=95, pollution_risk=80, land_suitability=20,
    )
    scored = score_sites([good, bad])
    assert scored[0].candidate.id == "1"
    assert scored[0].classification == "SUSTAINABLE"
    assert scored[1].classification == "UNSUSTAINABLE"


def test_scores_sorted_descending():
    sites = [
        SiteCandidate(id=str(i), name=f"Site {i}", water_availability=i * 10, infrastructure_access=i * 10,
                      population_proximity=50, environmental_sensitivity=50, pollution_risk=50, land_suitability=i * 10)
        for i in range(1, 5)
    ]
    scored = score_sites(sites)
    scores = [s.suitability_score for s in scored]
    assert scores == sorted(scores, reverse=True)


def test_rank_assigned_sequentially():
    sites = [
        SiteCandidate(id=str(i), name=f"Site {i}", water_availability=50, infrastructure_access=50,
                      population_proximity=50, environmental_sensitivity=50, pollution_risk=50, land_suitability=50)
        for i in range(3)
    ]
    scored = score_sites(sites)
    assert [s.rank for s in scored] == [1, 2, 3]
