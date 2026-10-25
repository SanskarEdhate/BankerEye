import pytest
import pandas as pd
from backend.services.prediction import (
    predict_single_customer,
    predict_batch_customers,
    validate_customer_input,
)


def test_predict_single_customer_all_models(valid_customer_dict):
    """Verify single-customer prediction succeeds across all four algorithms."""
    for model_name in ["random_forest", "decision_tree", "logistic_regression", "knn"]:
        res = predict_single_customer(features=valid_customer_dict, model_name=model_name)
        assert res["status"] == "success"
        assert res["model_key"] == model_name
        assert res["prediction"] in [0, 1]
        assert "probability" in res
        assert 0.0 <= res["probability"] <= 1.0
        assert "outcome" in res
        assert res["anti_leakage_applied"] is True
        assert "disclaimer" in res


def test_predict_single_ignores_duration(valid_customer_dict):
    """Verify passing 'duration' in input is safely stripped to prevent feature leakage."""
    payload_with_duration = valid_customer_dict.copy()
    payload_with_duration["duration"] = 500  # Highly correlated duration

    res = predict_single_customer(features=payload_with_duration, model_name="random_forest")
    assert res["status"] == "success"
    assert res["anti_leakage_applied"] is True


def test_validate_customer_input_missing_field():
    """Verify validation fails when a required field is missing."""
    incomplete = {"age": 40, "job": "services"}
    _cleaned, errors = validate_customer_input(incomplete)
    assert len(errors) > 0
    assert any("Missing required" in e for e in errors)


def test_validate_customer_input_invalid_category(valid_customer_dict):
    """Verify validation rejects arbitrary non-existent categorical values."""
    bad_cat = valid_customer_dict.copy()
    bad_cat["job"] = "astronaut_space_explorer"
    _cleaned, errors = validate_customer_input(bad_cat)
    assert any("Invalid value for 'job'" in e for e in errors)


def test_validate_customer_input_out_of_bounds(valid_customer_dict):
    """Verify validation rejects out of range numerical inputs."""
    bad_age = valid_customer_dict.copy()
    bad_age["age"] = 250  # Absurd age
    _cleaned, errors = validate_customer_input(bad_age)
    assert any("out of reasonable range" in e for e in errors)


def test_predict_unknown_model_raises(valid_customer_dict):
    """Verify requesting an unsupported model raises ValueError."""
    with pytest.raises(ValueError):
        predict_single_customer(features=valid_customer_dict, model_name="xgboost_not_installed")


def test_predict_batch_customers(sample_batch_df):
    """Verify batch prediction processes records and returns statistics."""
    res = predict_batch_customers(df_records=sample_batch_df, model_name="random_forest")
    assert res["status"] == "success"
    assert res["total_records"] == len(sample_batch_df)
    assert len(res["results"]) == len(sample_batch_df)
    assert res["predicted_positive"] + res["predicted_negative"] == len(sample_batch_df)
    assert 0.0 <= res["average_subscription_probability"] <= 1.0


def test_predict_batch_empty_df_raises():
    """Verify passing an empty DataFrame raises ValueError."""
    with pytest.raises(ValueError):
        predict_batch_customers(df_records=pd.DataFrame(), model_name="random_forest")
