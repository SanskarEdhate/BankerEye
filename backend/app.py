import logging
import os
import sys
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
    app.config["JSON_SORT_KEYS"] = False

    # Configure CORS for local development and Streamlit frontend
    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:8501", "http://127.0.0.1:8501", "*"]}},
        supports_credentials=True,
    )

    # Register blueprints
    app.register_blueprint(dataset_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(report_bp)

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

        # Check if models have been trained and serialized
        metrics_file = SAVED_MODELS_DIR / "model_metrics.json"
        models_trained = metrics_file.exists()

        return jsonify(
            {
                "status": "healthy",
                "app_name": "Bank Marketing Subscription Prediction System API",
                "version": "1.0.0",
                "dataset_available": dataset_available,
                "dataset_file": dataset_name,
                "models_trained": models_trained,
                "environment": os.getenv("FLASK_ENV", "production"),
            }
        ), 200

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"status": "error", "message": "Resource not found"}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return jsonify({"status": "error", "message": "HTTP Method not allowed"}), 405

    @app.errorhandler(500)
    def handle_internal_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({"status": "error", "message": "An internal server error occurred."}), 500

    return app


app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting BankerEye Flask API on {FLASK_HOST}:{FLASK_PORT}...")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
