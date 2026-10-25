import logging
import uuid
from flask import Blueprint, jsonify, request

from backend.services.train_models import (
    MODEL_DEFINITIONS,
    get_cached_metrics,
    get_training_job_status,
    start_background_training_job,
)

logger = logging.getLogger(__name__)
model_bp = Blueprint("models", __name__, url_prefix="/api/models")


@model_bp.route("/train", methods=["POST"])
def train_models():
    """
    Initiates asynchronous background model training across all four algorithms.
    Returns 202 Accepted immediately with a unique job ID for progress polling.
    """
    try:
        data = {}
        if request.data and request.data.strip():
            if not request.is_json:
                return jsonify({
                    "status": "error",
                    "message": "Content-type must be application/json when sending a request body.",
                }), 400

            data = request.get_json(silent=True)
            if data is None or not isinstance(data, dict):
                return jsonify({
                    "status": "error",
                    "message": "Request body must be a valid JSON object.",
                }), 400

        # Validate test_size
        test_size = 0.20
        if "test_size" in data:
            raw_ts = data["test_size"]
            if isinstance(raw_ts, bool) or not isinstance(raw_ts, (int, float)):
                return jsonify({
                    "status": "error",
                    "message": "Parameter 'test_size' must be a numeric float.",
                }), 400
            try:
                test_size = float(raw_ts)
                if not (0.05 <= test_size <= 0.50):
                    return jsonify({
                        "status": "error",
                        "message": "Parameter 'test_size' must be between 0.05 and 0.50.",
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    "status": "error",
                    "message": "Parameter 'test_size' must be a valid number.",
                }), 400

        # Validate force_retrain (parsing 'false', 'true', booleans properly)
        force_retrain = True
        if "force_retrain" in data:
            raw_force = data["force_retrain"]
            if isinstance(raw_force, bool):
                force_retrain = raw_force
            elif isinstance(raw_force, str):
                lower_val = raw_force.strip().lower()
                if lower_val in ("true", "1", "yes"):
                    force_retrain = True
                elif lower_val in ("false", "0", "no"):
                    force_retrain = False
                else:
                    return jsonify({
                        "status": "error",
                        "message": "Parameter 'force_retrain' must be a boolean ('true' or 'false').",
                    }), 400
            else:
                return jsonify({
                    "status": "error",
                    "message": "Parameter 'force_retrain' must be a boolean.",
                }), 400

        # Launch background training thread
        job_id = start_background_training_job(
            test_size=test_size,
            random_state=42,
            force_retrain=force_retrain,
        )

        return jsonify({
            "status": "accepted",
            "message": "Model training initiated as a background job.",
            "job_id": job_id,
        }), 202

    except RuntimeError as e:
        # Concurrent training attempt
        return jsonify({"status": "busy", "message": str(e)}), 429
    except FileNotFoundError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        req_id = str(uuid.uuid4())
        logger.exception(f"Error launching training job [req_id={req_id}]: {e}")
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred.",
            "request_id": req_id,
        }), 500


@model_bp.route("/train/status", methods=["GET"])
def get_training_status():
    """Returns current state (idle/running/done/failed), progress percentage, and error if any."""
    status_info = get_training_job_status()
    return jsonify(status_info), 200


@model_bp.route("/compare", methods=["GET"])
def compare_models():
    """Returns actual evaluation metrics, rankings, curves, CIs, and temporal checks for all trained models."""
    metrics = get_cached_metrics()
    if not metrics:
        return jsonify({
            "status": "not_trained",
            "message": "Models not trained. Run: python -m backend.services.train_models",
            "models": {},
            "rankings": {},
        }), 503

    return jsonify({
        "status": "ready",
        "trained_at": metrics.get("trained_at"),
        "dataset_info": metrics.get("dataset_info"),
        "split_info": metrics.get("split_info"),
        "models": metrics.get("models"),
        "rankings": metrics.get("rankings"),
        "statistical_verdict": metrics.get("statistical_verdict"),
        "is_top_model_distinguishable": metrics.get("is_top_model_distinguishable"),
        "temporal_check": metrics.get("temporal_check"),
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
            "message": "Models not trained. Run: python -m backend.services.train_models",
        }), 503

    return jsonify({
        "status": "success",
        "model_key": model_key,
        "model_data": metrics["models"][model_key],
    }), 200


@model_bp.route("/feature-importance", methods=["GET"])
def get_feature_importance():
    """Returns grouped permutation feature importances for ensemble models."""
    metrics = get_cached_metrics()
    if not metrics:
        return jsonify({
            "status": "not_trained",
            "message": "Models not trained. Run: python -m backend.services.train_models",
        }), 503

    importances = metrics.get("feature_importance", {})
    return jsonify({
        "status": "success",
        "feature_importance": importances,
        "disclaimer": "Feature importances are computed via permutation on the held-out test set with one-hot encoded features grouped back to their original domain attributes.",
    }), 200
