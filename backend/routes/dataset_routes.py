import logging
import uuid
from flask import Blueprint, jsonify, request
import numpy as np
import pandas as pd

from backend.config import DATASET_DIR
from backend.services.preprocessing import (
    get_available_datasets_list,
    get_dataset_cleaning_summary,
    get_dataset_manifest,
    get_dataset_stage_details,
    get_dataset_summary,
    get_feature_categories,
    load_dataset,
)

logger = logging.getLogger(__name__)
dataset_bp = Blueprint("dataset", __name__, url_prefix="/api/dataset")

ALLOWED_DATASET_IDS = {
    "1_uci_bank_marketing_canonical",
    "2_bank_additional_socioeconomic",
    "3_train_test_competition",
}

ALLOWED_STAGES = {
    "01_Raw_Data",
    "02_Unclean_Data",
    "03_Clean_Data",
    "04_Train_Data",
    "05_Test_Data",
}


@dataset_bp.route("/summary", methods=["GET"])
def dataset_summary():
    """Returns comprehensive metadata, shape, distributions, and missing values."""
    try:
        summary = get_dataset_summary()
        return jsonify(summary), 200
    except FileNotFoundError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        req_id = str(uuid.uuid4())
        logger.exception(f"Error generating dataset summary [req_id={req_id}]: {e}")
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred while inspecting dataset.",
            "request_id": req_id,
        }), 500


@dataset_bp.route("/sample", methods=["GET"])
def dataset_sample():
    """
    Returns a limited sample of dataset rows.
    Converts NaN/inf values to None so that the JSON response is strictly valid.
    """
    try:
        limit_param = request.args.get("limit", default=10, type=int)
        limit = max(1, min(limit_param, 100))

        df, meta = load_dataset()
        sample_df = df.head(limit).copy()

        # Convert NaN, inf, -inf to None for valid JSON serialization
        sample_df = sample_df.replace([np.inf, -np.inf], np.nan)
        clean_records = sample_df.where(pd.notnull(sample_df), None).to_dict(orient="records")

        return jsonify(
            {
                "status": "success",
                "sample_size": len(clean_records),
                "requested_limit": limit,
                "total_rows_in_dataset": meta["total_rows"],
                "columns": meta["columns"],
                "records": clean_records,
            }
        ), 200
    except FileNotFoundError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        req_id = str(uuid.uuid4())
        logger.exception(f"Error fetching dataset sample [req_id={req_id}]: {e}")
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred while retrieving sample.",
            "request_id": req_id,
        }), 500


@dataset_bp.route("/categories", methods=["GET"])
def dataset_categories():
    """Returns valid unique values for each categorical feature for UI dropdowns."""
    try:
        categories = get_feature_categories()
        return jsonify({"status": "success", "categories": categories}), 200
    except Exception as e:
        req_id = str(uuid.uuid4())
        logger.exception(f"Error in categories endpoint [req_id={req_id}]: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to load categorical options.",
            "request_id": req_id,
        }), 500


@dataset_bp.route("/catalog", methods=["GET"])
def dataset_catalog():
    """Returns the catalog of all organized dataset folders in dataset/."""
    try:
        catalog = get_available_datasets_list()
        return jsonify({"status": "success", "catalog": catalog}), 200
    except Exception as e:
        req_id = str(uuid.uuid4())
        logger.exception(f"Error in catalog endpoint [req_id={req_id}]: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to load dataset catalog.",
            "request_id": req_id,
        }), 500


@dataset_bp.route("/manifest", methods=["GET"])
def dataset_manifest_endpoint():
    """Returns the full dataset manifest from Data Cleaning & Splitting."""
    try:
        manifest = get_dataset_manifest()
        return jsonify(manifest), 200
    except Exception as e:
        req_id = str(uuid.uuid4())
        logger.exception(f"Error fetching dataset manifest [req_id={req_id}]: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to load dataset manifest.",
            "request_id": req_id,
        }), 500


@dataset_bp.route("/summary/<dataset_id>", methods=["GET"])
def dataset_id_summary_endpoint(dataset_id: str):
    """
    Returns data_summary.json for a specific dataset.
    Protected against path traversal via strict ID whitelisting and resolved path assertion.
    """
    try:
        # 1. Whitelist validation
        if dataset_id not in ALLOWED_DATASET_IDS:
            return jsonify({
                "status": "error",
                "message": f"Invalid dataset_id '{dataset_id}'. Allowed choices: {list(ALLOWED_DATASET_IDS)}",
            }), 400

        # 2. Strict path confinement validation
        base_split_dir = (DATASET_DIR / "Data Cleaning & Splitting").resolve()
        target_path = (base_split_dir / dataset_id / "data_summary.json").resolve()

        if base_split_dir not in target_path.parents:
            logger.warning(f"Path traversal attempted: dataset_id='{dataset_id}' resolved to '{target_path}'")
            return jsonify({"status": "error", "message": "Access denied: Path traversal detected."}), 400

        summary = get_dataset_cleaning_summary(dataset_id)
        if summary.get("status") == "error":
            return jsonify(summary), 404
        return jsonify({"status": "success", "summary": summary}), 200

    except Exception as e:
        req_id = str(uuid.uuid4())
        logger.exception(f"Error fetching dataset summary for {dataset_id} [req_id={req_id}]: {e}")
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred.",
            "request_id": req_id,
        }), 500


@dataset_bp.route("/stage", methods=["GET"])
def dataset_stage_endpoint():
    """
    Returns dimensions, columns, missing values, and preview records for a dataset stage.
    Protected against path traversal via strict whitelisting and resolved path assertion.
    """
    try:
        dataset_id = request.args.get("dataset_id")
        stage = request.args.get("stage")
        limit = request.args.get("limit", default=15, type=int)

        if not dataset_id or not stage:
            return jsonify({
                "status": "error",
                "message": "Parameters 'dataset_id' and 'stage' are both required.",
            }), 400

        # 1. Whitelist validation
        if dataset_id not in ALLOWED_DATASET_IDS:
            return jsonify({
                "status": "error",
                "message": f"Invalid dataset_id '{dataset_id}'. Allowed choices: {list(ALLOWED_DATASET_IDS)}",
            }), 400

        if stage not in ALLOWED_STAGES:
            return jsonify({
                "status": "error",
                "message": f"Invalid stage '{stage}'. Allowed stages: {list(ALLOWED_STAGES)}",
            }), 400

        # 2. Path confinement assertion
        base_split_dir = (DATASET_DIR / "Data Cleaning & Splitting").resolve()
        stage_dir = (base_split_dir / dataset_id / stage).resolve()

        if base_split_dir not in stage_dir.parents:
            logger.warning(f"Path traversal attempted on stage: dataset_id='{dataset_id}', stage='{stage}'")
            return jsonify({"status": "error", "message": "Access denied: Path traversal detected."}), 400

        details = get_dataset_stage_details(dataset_id=dataset_id, stage=stage, preview_limit=limit)
        return jsonify({
            "status": "success",
            "stage_details": details,
            **details,
        }), 200

    except Exception as e:
        req_id = str(uuid.uuid4())
        logger.exception(f"Error in dataset stage details [req_id={req_id}]: {e}")
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred while retrieving stage details.",
            "request_id": req_id,
        }), 500
