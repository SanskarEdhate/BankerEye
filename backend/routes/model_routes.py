import logging
from flask import Blueprint, jsonify, request

from backend.services.train_models import (
    MODEL_DEFINITIONS,
    get_cached_metrics,
    train_and_evaluate_all_models,
)

logger = logging.getLogger(__name__)
model_bp = Blueprint("models", __name__, url_prefix="/api/models")


@model_bp.route("/train", methods=["POST"])
def train_models():
    """
    Trains all four primary machine learning models, evaluates on the held-out test set,
    and returns metrics, rankings, and durations.
    """
    try:
        data = request.get_json(silent=True) or {}
        test_size = float(data.get("test_size", 0.20))
        force_retrain = bool(data.get("force_retrain", True))

        if not (0.05 <= test_size <= 0.5):
            return jsonify({
                "status": "error",
                "message": "test_size must be between 0.05 and 0.50",
            }), 400

        results = train_and_evaluate_all_models(
            test_size=test_size,
            force_retrain=force_retrain,
        )

        return jsonify({
            "status": "success",
            "message": "All four models trained and evaluated successfully.",
            "data": results,
        }), 200

    except RuntimeError as e:
        # Concurrent training attempt
        return jsonify({"status": "busy", "message": str(e)}), 429
    except FileNotFoundError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        logger.error(f"Error during model training: {e}")
        return jsonify({"status": "error", "message": f"Training failed: {str(e)}"}), 500


@model_bp.route("/compare", methods=["GET"])
def compare_models():
    """Returns actual evaluation metrics, rankings, and ROC/PR curve data for all trained models."""
    metrics = get_cached_metrics()
    if not metrics:
        return jsonify({
            "status": "not_trained",
            "message": "Models have not been trained yet. Please send a POST to /api/models/train.",
            "models": {},
            "rankings": {},
        }), 200

    return jsonify({
        "status": "ready",
        "trained_at": metrics.get("trained_at"),
        "dataset_info": metrics.get("dataset_info"),
        "split_info": metrics.get("split_info"),
        "models": metrics.get("models"),
        "rankings": metrics.get("rankings"),
        "total_training_time_sec": metrics.get("total_training_time_sec"),
    }), 200


@model_bp.route("/<model_name>/metrics", methods=["GET"])
def get_single_model_metrics(model_name: str):
    """Returns detailed metrics and confusion matrix for a specific algorithm."""
    model_key = model_name.lower().strip()
    if model_key not in MODEL_DEFINITIONS:
        return jsonify({
            "status": "error",
            "message": f"Unknown model name '{model_name}'. Allowed choices: {list(MODEL_DEFINITIONS.keys())}",
        }), 404

    metrics = get_cached_metrics()
    if not metrics or model_key not in metrics.get("models", {}):
        return jsonify({
            "status": "not_trained",
            "message": f"Metrics for '{model_name}' are not available yet. Please train models first.",
        }), 404

    return jsonify({
        "status": "success",
        "model_key": model_key,
        "model_data": metrics["models"][model_key],
    }), 200


@model_bp.route("/feature-importance", methods=["GET"])
def get_feature_importance():
    """
    Returns feature importance rankings for supported models.
    Explicitly clarifies that feature importance measures predictive contribution, not causation.
    """
    metrics = get_cached_metrics()
    if not metrics or "feature_importance" not in metrics:
        return jsonify({
            "status": "not_trained",
            "message": "Feature importance data is not available. Please train models first.",
            "feature_importance": {},
        }), 200

    return jsonify({
        "status": "success",
        "feature_importance": metrics.get("feature_importance", {}),
        "disclaimer": (
            "Feature importance rankings quantify statistical contribution within the decision trees and "
            "regularized linear coefficients. They indicate correlation with customer subscription behavior "
            "in the dataset and do not establish causal relationships."
        ),
    }), 200
