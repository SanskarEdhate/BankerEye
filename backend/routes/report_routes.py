import logging
import uuid
from flask import Blueprint, Response, jsonify, send_file

from backend.config import REPORTS_DIR, SAVED_MODELS_DIR
from backend.services.report_service import (
    generate_evaluation_pdf,
    generate_metrics_csv,
    get_structured_evaluation_report,
)

logger = logging.getLogger(__name__)
report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@report_bp.route("/evaluation", methods=["GET"])
def get_evaluation_report():
    """Returns structured evaluation report in JSON format."""
    try:
        report = get_structured_evaluation_report()
        status_code = 200 if report.get("status") == "success" else 503
        return jsonify(report), status_code
    except Exception as e:
        req_id = str(uuid.uuid4())
        logger.exception(f"Error fetching evaluation report [req_id={req_id}]: {e}")
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred while retrieving evaluation report.",
            "request_id": req_id,
        }), 500


@report_bp.route("/metrics-csv", methods=["GET"])
def download_metrics_csv():
    """Returns model metrics as a downloadable CSV."""
    try:
        csv_data = generate_metrics_csv()
        if not csv_data:
            return jsonify({
                "status": "error",
                "message": "No metrics available to export. Please train models first.",
            }), 503

        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=model_metrics_comparison.csv"},
        )
    except Exception as e:
        req_id = str(uuid.uuid4())
        logger.exception(f"Error exporting metrics CSV [req_id={req_id}]: {e}")
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred while exporting CSV.",
            "request_id": req_id,
        }), 500


@report_bp.route("/pdf", methods=["GET"])
def download_report_pdf():
    """
    Generates and serves the formal academic PDF report.
    Automatically regenerates whenever model_metrics.json is newer than the existing PDF.
    """
    try:
        pdf_path = REPORTS_DIR / "academic_evaluation_report.pdf"
        metrics_file = SAVED_MODELS_DIR / "model_metrics.json"

        # Regenerate whenever model_metrics.json is newer than the PDF or PDF is missing
        needs_generation = not pdf_path.exists()
        if not needs_generation and metrics_file.exists():
            if metrics_file.stat().st_mtime > pdf_path.stat().st_mtime:
                needs_generation = True

        if needs_generation:
            pdf_path = generate_evaluation_pdf()

        return send_file(
            str(pdf_path),
            as_attachment=True,
            download_name="Bank_Marketing_ML_Evaluation_Report.pdf",
            mimetype="application/pdf",
        )
    except Exception as e:
        req_id = str(uuid.uuid4())
        logger.exception(f"Failed to serve PDF report [req_id={req_id}]: {e}")
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred while generating PDF report.",
            "request_id": req_id,
        }), 500
