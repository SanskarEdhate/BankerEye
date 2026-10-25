import pytest
from sklearn.pipeline import Pipeline

from backend.services.train_models import (
    MODEL_DEFINITIONS,
    load_model_pipeline,
    get_cached_metrics,
    compute_rankings,
)


def test_model_definitions():
    """Verify all 4 required models are defined with estimators."""
    expected_models = {"logistic_regression", "decision_tree", "knn", "random_forest"}
    assert set(MODEL_DEFINITIONS.keys()) == expected_models

    for k, meta in MODEL_DEFINITIONS.items():
        assert "display_name" in meta
        assert "description" in meta
        estimator = meta["estimator"]()
        assert hasattr(estimator, "fit")


def test_load_all_trained_model_pipelines():
    """Verify each of the 4 serialized pipelines can be loaded from disk."""
    for model_key in MODEL_DEFINITIONS.keys():
        pipeline = load_model_pipeline(model_key)
        assert isinstance(pipeline, Pipeline)
        assert hasattr(pipeline, "predict")
        assert hasattr(pipeline, "predict_proba")
        assert "preprocessor" in pipeline.named_steps
        assert "classifier" in pipeline.named_steps


def test_unknown_model_load_raises():
    """Verify loading an unknown model name raises ValueError."""
    with pytest.raises(ValueError):
        load_model_pipeline("unsupported_neural_network_123")


def test_cached_metrics_integrity():
    """Verify cached evaluation metrics contain real computed scores for all 4 algorithms."""
    metrics = get_cached_metrics()
    assert metrics is not None
    assert "models" in metrics
    assert len(metrics["models"]) == 4

    for model_key in ["logistic_regression", "decision_tree", "knn", "random_forest"]:
        assert model_key in metrics["models"]
        m = metrics["models"][model_key]["metrics"]

        # Validate score bounds
        for metric_name in ["accuracy", "precision", "recall", "f1_score", "roc_auc"]:
            val = m.get(metric_name)
            assert val is not None, f"Missing {metric_name} in {model_key}"
            assert 0.0 <= val <= 1.0, f"Metric {metric_name} out of bounds: {val}"

        # Confusion matrix checks
        cm = metrics["models"][model_key]["confusion_matrix"]
        total_eval = cm["true_negatives"] + cm["false_positives"] + cm["false_negatives"] + cm["true_positives"]
        assert total_eval == 9043, f"Expected 9,043 test instances, got: {total_eval}"


def test_feature_importance_availability():
    """Verify feature importances are extracted for Random Forest and Decision Tree."""
    metrics = get_cached_metrics()
    assert "feature_importance" in metrics
    assert "random_forest" in metrics["feature_importance"]
    assert "decision_tree" in metrics["feature_importance"]
    assert len(metrics["feature_importance"]["random_forest"]) > 0


def test_compute_rankings():
    """Verify multi-metric ranking calculation sorts correctly in descending order."""
    metrics = get_cached_metrics()
    rankings = compute_rankings(metrics["models"])
    assert "f1_score" in rankings
    assert "roc_auc" in rankings

    # Check that rank 1 has the maximum value
    for metric in ["f1_score", "roc_auc"]:
        ranked_list = rankings[metric]
        assert len(ranked_list) == 4
        assert ranked_list[0]["value"] >= ranked_list[1]["value"]
        assert ranked_list[1]["value"] >= ranked_list[2]["value"]
        assert ranked_list[2]["value"] >= ranked_list[3]["value"]
