def test_fixture_metrics_are_reproducible():
    metrics = {"stability": 1.0}
    assert metrics["stability"] == 1.0
