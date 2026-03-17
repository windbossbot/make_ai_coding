from app.guards import NumericBounds, detect_price_anomaly, validate_numeric


def test_validate_numeric_accepts_value_in_range() -> None:
    assert validate_numeric("balance", 10, NumericBounds(minimum=0, maximum=100)) == 10.0


def test_validate_numeric_rejects_negative_balance() -> None:
    try:
        validate_numeric("balance", -1, NumericBounds(minimum=0, maximum=100))
    except ValueError as exc:
        assert ">= 0" in str(exc)
    else:
        raise AssertionError("Expected a ValueError for negative balance.")


def test_detect_price_anomaly_raises_on_outlier() -> None:
    try:
        detect_price_anomaly(price=500, moving_average=100, sigma=10, sigma_limit=3)
    except ValueError as exc:
        assert "z-score" in str(exc)
    else:
        raise AssertionError("Expected anomaly detection to raise.")
