import logging
import os
import sys
import uuid
from pathlib import Path

# Add project root to sys.path if not present
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from flask import Flask, jsonify
from flask_cors import CORS

from backend.config import (
    FLASK_HOST,
    FLASK_PORT,
    FLASK_DEBUG,
    SAVED_MODELS_DIR,
    EXPECTED_MODEL_FILES,
)
from backend.services.preprocessing import resolve_dataset_path
from backend.routes.dataset_routes import dataset_bp
from backend.routes.model_routes import model_bp
from backend.routes.prediction_routes import prediction_bp
from backend.routes.report_routes import report_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("backend")


def create_app() -> Flask:
    """Application factory for the Flask REST API."""
    app = Flask(__name__)
    app.json.sort_keys = False
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB payload cap

    # Configure CORS: allow all origins by default in production or explicit list from env
    cors_origins_env = os.getenv("CORS_ORIGINS", "*").strip()
    if cors_origins_env == "*" or not cors_origins_env:
        CORS(app, resources={r"/api/*": {"origins": "*"}, r"/*": {"origins": "*"}})
    else:
        allowed_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
        CORS(app, resources={r"/api/*": {"origins": allowed_origins}, r"/*": {"origins": allowed_origins}})

    # Register blueprints
    app.register_blueprint(dataset_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(report_bp)

    @app.route("/", methods=["GET"])
    def root_index():
        """Root endpoint confirming service operational status."""
        return jsonify(
            {
                "status": "online",
                "service": "BankerEye Machine Learning API",
                "version": "1.0.0",
                "health": "/api/health",
                "endpoints": [
                    "/api/health",
                    "/api/dataset/summary",
                    "/api/models/compare",
                    "/api/predict",
                    "/api/reports/evaluation",
                ],
            }
        ), 200

    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Health check endpoint providing runtime operational status."""
        # Check dataset availability
        dataset_available = False
        dataset_name = None
        try:
            ds_path = resolve_dataset_path()
            dataset_available = ds_path.exists()
            dataset_name = ds_path.name
        except Exception:
            dataset_available = False

        # Check if models have been trained and serialized (all 4 joblibs + metrics JSON)
        metrics_file = SAVED_MODELS_DIR / "model_metrics.json"
        all_joblib_exist = all((SAVED_MODELS_DIR / fname).exists() for fname in EXPECTED_MODEL_FILES)
        models_trained = metrics_file.exists() and all_joblib_exist

        return jsonify(
            {
                "status": "healthy",
                "app_name": "Bank Marketing Subscription Prediction System API",
                "version": "1.0.0",
                "dataset_available": dataset_available,
                "dataset_file": dataset_name,
                "models_trained": models_trained,
            }
        ), 200

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"status": "error", "message": "Resource not found"}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return jsonify({"status": "error", "message": "HTTP Method not allowed"}), 405

    @app.errorhandler(413)
    def handle_payload_too_large(e):
        return jsonify({
            "status": "error",
            "message": "Uploaded payload exceeds the maximum allowed file size limit of 10MB.",
        }), 413

    @app.errorhandler(500)
    def handle_internal_error(e):
        req_id = str(uuid.uuid4())
        logger.exception(f"Internal server error [req_id={req_id}]: {e}")
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred.",
            "request_id": req_id,
        }), 500

    return app


app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting BankerEye Flask API on {FLASK_HOST}:{FLASK_PORT}...")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
