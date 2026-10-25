import logging
from flask import Blueprint, Response, jsonify, send_file

from backend.config import REPORTS_DIR
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
    report = get_structured_evaluation_report()
    status_code = 200 if report.get("status") == "success" else 404
    return jsonify(report), status_code


@report_bp.route("/metrics-csv", methods=["GET"])
def download_metrics_csv():
    """Returns model metrics as a downloadable CSV."""
    csv_data = generate_metrics_csv()
    if not csv_data:
        return jsonify({"status": "error", "message": "No metrics available to export."}), 404

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=model_metrics_comparison.csv"},
    )


@report_bp.route("/pdf", methods=["GET"])
def download_report_pdf():
    """Generates and serves the formal academic PDF report."""
    try:
        pdf_path = REPORTS_DIR / "academic_evaluation_report.pdf"
        if not pdf_path.exists():
            pdf_path = generate_evaluation_pdf()

        return send_file(
            str(pdf_path),
            as_attachment=True,
            download_name="Bank_Marketing_ML_Evaluation_Report.pdf",
            mimetype="application/pdf",
        )
    except Exception as e:
        logger.error(f"Failed to serve PDF report: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
