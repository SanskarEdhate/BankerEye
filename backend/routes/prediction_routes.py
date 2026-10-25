import io
import logging
import uuid
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
        # Enforce valid JSON object body
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Request content-type must be application/json.",
            }), 400

        data = request.get_json(silent=True)
        if data is None or not isinstance(data, dict):
            return jsonify({
                "status": "error",
                "message": "Invalid request body. JSON body must be an object.",
            }), 400

        features = data.get("features", data)
        if not isinstance(features, dict):
            return jsonify({
                "status": "error",
                "message": "Field 'features' must be a JSON object (dictionary).",
            }), 400

        result = predict_all_models_single_customer(features=features)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 422
    except FileNotFoundError as e:
        logger.warning(f"Predict all requested before training: {e}")
        return jsonify({
            "status": "error",
            "message": "Models not trained. Run: python -m backend.services.train_models",
        }), 503
    except Exception as e:
        req_id = str(uuid.uuid4())
        logger.exception(f"Multi-model prediction exception [req_id={req_id}]: {e}")
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred.",
            "request_id": req_id,
        }), 500


@prediction_bp.route("/predict", methods=["POST"])
def predict():
    """
    Accepts customer features as JSON, validates schema and value bounds,
    and returns class prediction, probability, and contextual insights.
    """
    try:
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Request content-type must be application/json.",
            }), 400

        data = request.get_json(silent=True)
        if data is None or not isinstance(data, dict):
            return jsonify({
                "status": "error",
                "message": "Invalid request body. JSON body must be an object.",
            }), 400

        # Validate 'model' field strictly
        if "model" in data:
            model_val = data["model"]
            if model_val is None or not isinstance(model_val, str) or not model_val.strip():
                return jsonify({
                    "status": "error",
                    "message": "Field 'model' must be a non-empty string.",
                }), 400
            model_name = model_val.lower().strip()
        else:
            model_name = "random_forest"

        if model_name not in MODEL_DEFINITIONS:
            return jsonify({
                "status": "error",
                "message": f"Unsupported model '{model_name}'. Allowed: {list(MODEL_DEFINITIONS.keys())}",
            }), 400

        features = data.get("features", data)
        if not isinstance(features, dict):
            return jsonify({
                "status": "error",
                "message": "Field 'features' must be a JSON object (dictionary).",
            }), 400

        result = predict_single_customer(features=features, model_name=model_name)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 422
    except FileNotFoundError as e:
        logger.warning(f"Predict requested before training: {e}")
        return jsonify({
            "status": "error",
            "message": "Models not trained. Run: python -m backend.services.train_models",
        }), 503
    except Exception as e:
        req_id = str(uuid.uuid4())
        logger.exception(f"Prediction exception [req_id={req_id}]: {e}")
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred.",
            "request_id": req_id,
        }), 500


@prediction_bp.route("/predict/batch", methods=["POST"])
def predict_batch():
    """
    Accepts batch records via multipart CSV file upload or JSON payload.
    Validates delimiter with detect_csv_delimiter and validates every row.
    """
    try:
        model_name = "random_forest"
        if request.content_type and "multipart/form-data" in request.content_type:
            model_param = request.form.get("model", "random_forest")
            if not isinstance(model_param, str) or not model_param.strip():
                return jsonify({"status": "error", "message": "Field 'model' must be a string."}), 400
            model_name = model_param.lower().strip()

            if "file" not in request.files:
                return jsonify({"status": "error", "message": "No file part in multipart request."}), 400

            file = request.files["file"]
            if file.filename == "":
                return jsonify({"status": "error", "message": "No file selected for upload."}), 400

            # Read raw bytes to detect delimiter and construct DataFrame
            raw_bytes = file.read()
            if not raw_bytes:
                return jsonify({"status": "error", "message": "Uploaded CSV file is empty."}), 400

            # Sniff delimiter from sample
            sample_str = raw_bytes[:4096].decode("utf-8", errors="ignore")
            first_line = sample_str.splitlines()[0] if sample_str.splitlines() else ""
            delim = ";" if first_line.count(";") > first_line.count(",") else ","

            try:
                df_records = pd.read_csv(io.BytesIO(raw_bytes), sep=delim)
            except Exception as e:
                return jsonify({"status": "error", "message": f"Malformed CSV file: {e}"}), 400

        elif request.is_json:
            data = request.get_json(silent=True)
            if data is None or not isinstance(data, dict):
                return jsonify({
                    "status": "error",
                    "message": "JSON body must be an object with 'records' list.",
                }), 400

            if "model" in data:
                m_val = data["model"]
                if m_val is None or not isinstance(m_val, str) or not m_val.strip():
                    return jsonify({"status": "error", "message": "Field 'model' must be a string."}), 400
                model_name = m_val.lower().strip()

            records = data.get("records")
            if not isinstance(records, list) or not records:
                return jsonify({"status": "error", "message": "Field 'records' must be a non-empty list."}), 400

            df_records = pd.DataFrame(records)
        else:
            return jsonify({
                "status": "error",
                "message": "Content-Type must be application/json or multipart/form-data.",
            }), 400

        if model_name not in MODEL_DEFINITIONS:
            return jsonify({
                "status": "error",
                "message": f"Unsupported model '{model_name}'. Choose from: {list(MODEL_DEFINITIONS.keys())}",
            }), 400

        # Run batch prediction with row-by-row validation
        results = predict_batch_customers(df_records=df_records, model_name=model_name)
        return jsonify(results), 200

    except ValueError as e:
        # Check if structured batch error
        val = e.args[0] if e.args else str(e)
        if isinstance(val, dict) and val.get("type") == "batch_validation_error":
            return jsonify({
                "status": "error",
                "message": val["message"],
                "total_erroneous_rows": val["total_erroneous_rows"],
                "row_errors": val["row_errors"],
            }), 400
        return jsonify({"status": "error", "message": str(val)}), 400

    except FileNotFoundError as e:
        logger.warning(f"Batch predict requested before training: {e}")
        return jsonify({
            "status": "error",
            "message": "Models not trained. Run: python -m backend.services.train_models",
        }), 503
    except Exception as e:
        req_id = str(uuid.uuid4())
        logger.exception(f"Batch prediction exception [req_id={req_id}]: {e}")
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred during batch prediction.",
            "request_id": req_id,
        }), 500
