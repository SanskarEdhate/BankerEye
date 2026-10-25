import logging
from flask import Blueprint, jsonify, request

from backend.services.preprocessing import (
    get_dataset_summary,
    load_dataset,
    get_feature_categories,
)

logger = logging.getLogger(__name__)
dataset_bp = Blueprint("dataset", __name__, url_prefix="/api/dataset")


@dataset_bp.route("/summary", methods=["GET"])
def dataset_summary():
    """Returns comprehensive metadata, shape, distributions, and missing values."""
    try:
        summary = get_dataset_summary()
        return jsonify(summary), 200
    except FileNotFoundError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        logger.error(f"Error generating dataset summary: {e}")
        return jsonify({"status": "error", "message": f"Failed to inspect dataset: {str(e)}"}), 500


@dataset_bp.route("/sample", methods=["GET"])
def dataset_sample():
    """
    Returns a limited, configurable sample of dataset rows.
    Guarantees that the entire dataset is never exposed through this endpoint.
    """
    try:
        limit_param = request.args.get("limit", default=10, type=int)
        # Enforce bounds between 1 and 100
        limit = max(1, min(limit_param, 100))

        df, meta = load_dataset()
        # Return first 'limit' rows as JSON records
        sample_df = df.head(limit)
        records = sample_df.to_dict(orient="records")

        return jsonify(
            {
                "status": "success",
                "sample_size": len(records),
                "requested_limit": limit,
                "total_rows_in_dataset": meta["total_rows"],
                "columns": meta["columns"],
                "records": records,
            }
        ), 200
    except FileNotFoundError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching dataset sample: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@dataset_bp.route("/categories", methods=["GET"])
def dataset_categories():
    """Returns valid unique values for each categorical feature for UI dropdowns."""
    try:
        categories = get_feature_categories()
        return jsonify({"status": "success", "categories": categories}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@dataset_bp.route("/catalog", methods=["GET"])
def dataset_catalog():
    """Returns the catalog of all organized dataset folders in dataset/."""
    from backend.services.preprocessing import get_available_datasets_list
    try:
        catalog = get_available_datasets_list()
        return jsonify({"status": "success", "catalog": catalog}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@dataset_bp.route("/manifest", methods=["GET"])
def dataset_manifest_endpoint():
    """Returns the full dataset manifest from Data Cleaning & Splitting."""
    from backend.services.preprocessing import get_dataset_manifest
    try:
        manifest = get_dataset_manifest()
        return jsonify(manifest), 200
    except Exception as e:
        logger.error(f"Error fetching dataset manifest: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@dataset_bp.route("/summary/<dataset_id>", methods=["GET"])
def dataset_id_summary_endpoint(dataset_id: str):
    """Returns the data_summary.json for a specific dataset."""
    from backend.services.preprocessing import get_dataset_cleaning_summary
    try:
        summary = get_dataset_cleaning_summary(dataset_id)
        if summary.get("status") == "error":
            return jsonify(summary), 404
        return jsonify({"status": "success", "summary": summary}), 200
    except Exception as e:
        logger.error(f"Error fetching dataset summary for {dataset_id}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@dataset_bp.route("/stage", methods=["GET"])
def dataset_stage_endpoint():
    """Returns dimensions, columns, missing values, and preview records for a dataset stage."""
    from backend.services.preprocessing import get_dataset_stage_details
    try:
        dataset_id = request.args.get("dataset_id")
        stage = request.args.get("stage")
        limit = request.args.get("limit", default=15, type=int)

        if not dataset_id or not stage:
            return jsonify({"status": "error", "message": "dataset_id and stage query parameters are required"}), 400

        details = get_dataset_stage_details(dataset_id=dataset_id, stage=stage, preview_limit=limit)
        return jsonify({"status": "success", "stage_details": details}), 200
    except Exception as e:
        logger.error(f"Error fetching stage details: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


