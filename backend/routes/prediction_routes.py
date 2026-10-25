import logging
from flask import Blueprint, jsonify, request
import pandas as pd

from backend.services.prediction import (
    predict_single_customer,
    predict_all_models_single_customer,
    predict_batch_customers,
)
from backend.services.train_models import MODEL_DEFINITIONS

logger = logging.getLogger(__name__)
prediction_bp = Blueprint("prediction", __name__, url_prefix="/api")


@prediction_bp.route("/predict/all", methods=["POST"])
def predict_all():
    """
    Accepts customer features as JSON, evaluates across all four models simultaneously,
    and returns per-model predictions, benchmark accuracy, and consensus.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "status": "error",
                "message": "Invalid request body. JSON payload is required.",
            }), 400

        features = data.get("features", data)
        result = predict_all_models_single_customer(features=features)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 422
    except FileNotFoundError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        logger.error(f"Multi-model prediction exception: {e}")
        return jsonify({"status": "error", "message": f"Prediction failed: {str(e)}"}), 500



@prediction_bp.route("/predict", methods=["POST"])
def predict():
    """
    Accepts customer features as JSON, validates schema and value bounds,
    and returns class prediction, probability, and contextual insights.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "status": "error",
                "message": "Invalid request body. JSON payload is required.",
            }), 400

        features = data.get("features", data)
        model_name = data.get("model", "random_forest").lower().strip()

        if model_name not in MODEL_DEFINITIONS:
            return jsonify({
                "status": "error",
                "message": f"Unsupported model '{model_name}'. Allowed: {list(MODEL_DEFINITIONS.keys())}",
            }), 400

        result = predict_single_customer(features=features, model_name=model_name)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 422
    except FileNotFoundError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        logger.error(f"Prediction exception: {e}")
        return jsonify({"status": "error", "message": f"Prediction failed: {str(e)}"}), 500


@prediction_bp.route("/predict/batch", methods=["POST"])
def predict_batch():
    """
    Accepts multiple customer records and returns predictions in the same order.
    Supports either JSON array in payload or multipart file upload (CSV).
    """
    try:
        model_name = request.form.get("model", "random_forest")
        if "file" in request.files:
            file = request.files["file"]
            if file.filename == "":
                return jsonify({"status": "error", "message": "No file selected."}), 400
            # Read CSV file
            df_records = pd.read_csv(file)
        else:
            data = request.get_json(silent=True)
            if not data:
                return jsonify({"status": "error", "message": "JSON body or file upload required."}), 400
            records = data.get("records", [])
            model_name = data.get("model", model_name)
            if not records:
                return jsonify({"status": "error", "message": "'records' array is empty."}), 400
            df_records = pd.DataFrame(records)

        result = predict_batch_customers(df_records=df_records, model_name=model_name)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 422
    except FileNotFoundError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({"status": "error", "message": f"Batch prediction failed: {str(e)}"}), 500
