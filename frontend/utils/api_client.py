import os
import logging
from typing import Any, Dict, List, Optional
import requests
import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

_RESOLVED_BASE_URL: Optional[str] = None


def get_base_url() -> str:
    """Dynamically resolves the backend API URL from st.secrets, env vars, or production Render."""
    global _RESOLVED_BASE_URL
    if _RESOLVED_BASE_URL:
        return _RESOLVED_BASE_URL

    # 1. Streamlit Secrets (highest priority for cloud deployments)
    try:
        if hasattr(st, "secrets"):
            for key in ("BACKEND_API_URL", "STREAMLIT_API_BASE_URL", "backend_api_url", "streamlit_api_base_url"):
                if key in st.secrets:
                    val = str(st.secrets[key]).strip().rstrip("/")
                    if val:
                        _RESOLVED_BASE_URL = val
                        return _RESOLVED_BASE_URL
    except Exception:
        pass

    # 2. Environment Variables
    for key in ("BACKEND_API_URL", "STREAMLIT_API_BASE_URL"):
        val = os.getenv(key)
        if val:
            _RESOLVED_BASE_URL = val.strip().rstrip("/")
            return _RESOLVED_BASE_URL

    # 3. Check if local backend is active on port 5000 (for local development)
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            if s.connect_ex(("127.0.0.1", 5000)) == 0:
                _RESOLVED_BASE_URL = "http://127.0.0.1:5000"
                return _RESOLVED_BASE_URL
    except Exception:
        pass

    # 4. Default to deployed production backend on Render
    _RESOLVED_BASE_URL = "https://bankereye-1.onrender.com"
    return _RESOLVED_BASE_URL


API_BASE_URL = get_base_url()
DEFAULT_TIMEOUT = 12.0
TRAIN_TIMEOUT = 90.0

__all__ = [
    "API_BASE_URL",
    "get_base_url",
    "check_api_health",
    "get_dataset_summary",
    "get_dataset_sample",
    "get_dataset_categories",
    "get_dataset_catalog",
    "trigger_model_training",
    "get_training_status",
    "clear_all_api_caches",
    "get_model_comparison",
    "get_feature_importance",
    "predict_single",
    "predict_all_models_api",
    "predict_batch_csv",
    "get_evaluation_report",
    "download_metrics_csv_url",
    "download_report_pdf_url",
    "fetch_metrics_csv_bytes",
    "fetch_report_pdf_bytes",
    "get_dataset_manifest",
    "get_dataset_cleaning_summary",
    "get_dataset_stage_details",
]


def _load_local_dataset_summary() -> Optional[Dict[str, Any]]:
    """Loads benchmark dataset summary from local canonical file in < 1ms."""
    try:
        from pathlib import Path
        import json
        summary_path = (
            Path(__file__).resolve().parent.parent.parent
            / "dataset"
            / "Data Cleaning & Splitting"
            / "1_uci_bank_marketing_canonical"
            / "data_summary.json"
        )
        if summary_path.exists():
            with open(summary_path, "r", encoding="utf-8") as f:
                raw_s = json.load(f)
            return {
                "total_rows": raw_s.get("cleaned_record_count", 45211),
                "total_columns": raw_s.get("cleaned_column_count", 17),
                "total_missing_cells": raw_s.get("missing_value_count", 0),
                "duplicate_rows": raw_s.get("duplicate_count", 0),
                "target_distribution": {
                    "no": {"count": 39922, "percentage": 88.3},
                    "yes": {"count": 5289, "percentage": 11.7},
                },
                "is_fallback": True,
            }
    except Exception as ex:
        logger.error(f"Local summary load failed: {ex}")
    return None


def _load_local_model_comparison() -> Optional[Dict[str, Any]]:
    """Loads benchmark model evaluation summary from local disk in < 1ms."""
    try:
        from pathlib import Path
        import json
        eval_path = (
            Path(__file__).resolve().parent.parent.parent
            / "backend"
            / "saved_models"
            / "evaluation_summary.json"
        )
        if eval_path.exists():
            with open(eval_path, "r", encoding="utf-8") as f:
                raw_eval = json.load(f)
            raw_eval["is_fallback"] = True
            return raw_eval
    except Exception as ex:
        logger.error(f"Local model comparison load failed: {ex}")
    return None


def _load_local_feature_importance() -> Optional[Dict[str, Any]]:
    """Loads feature importance rankings from local model_metrics.json in < 1ms."""
    try:
        from pathlib import Path
        import json
        metrics_path = (
            Path(__file__).resolve().parent.parent.parent
            / "backend"
            / "saved_models"
            / "model_metrics.json"
        )
        if metrics_path.exists():
            with open(metrics_path, "r", encoding="utf-8") as f:
                raw_metrics = json.load(f)
            fi = raw_metrics.get("feature_importance", {})
            if fi:
                return {
                    "status": "success",
                    "feature_importance": fi,
                    "is_fallback": True,
                }
    except Exception as ex:
        logger.error(f"Local feature importance load failed: {ex}")
    return None


def _load_local_categories() -> Dict[str, List[str]]:
    """Default categorical options for form fields to avoid network delay."""
    return {
        "job": ["blue-collar", "management", "technician", "admin.", "services", "retired", "self-employed", "entrepreneur", "unemployed", "housemaid", "student", "unknown"],
        "marital": ["married", "single", "divorced"],
        "education": ["secondary", "tertiary", "primary", "unknown"],
        "default": ["no", "yes"],
        "housing": ["yes", "no"],
        "loan": ["no", "yes"],
        "contact": ["cellular", "telephone", "unknown"],
        "month": ["may", "jul", "aug", "jun", "nov", "apr", "feb", "jan", "oct", "sep", "mar", "dec"],
        "poutcome": ["unknown", "failure", "other", "success"],
    }


def check_api_health(retries: int = 1) -> Dict[str, Any]:
    """Checks whether the Flask backend is running and healthy. NEVER CACHED."""
    base_url = get_base_url()
    timeout = 18.0 if "render.com" in base_url else DEFAULT_TIMEOUT
    for attempt in range(retries + 1):
        try:
            url = f"{base_url}/api/health"
            res = requests.get(url, timeout=timeout)
            if res.status_code == 200:
                return res.json()
            return {"status": "unhealthy", "code": res.status_code}
        except requests.exceptions.RequestException as e:
            if attempt < retries:
                continue
            logger.warning(f"Health check failed for {base_url}: {e}")
            is_render = "render.com" in base_url
            msg = (
                f"Flask API at {base_url} is currently waking up from idle mode (Render Free Tier spins down after 15 min of inactivity; takes ~30-45s on first wake-up). Please wait a moment and refresh."
                if is_render
                else f"Flask API unreachable at {base_url}. Ensure 'python backend/app.py' is running."
            )
            return {
                "status": "offline",
                "message": msg,
            }


@st.cache_data(ttl=3600, show_spinner=False)
def get_dataset_summary() -> Optional[Dict[str, Any]]:
    """Retrieves dataset summary (instant local benchmark first, avoids cold-start freeze)."""
    # 1. Instant local load (< 1ms) so home & dashboard render immediately
    local_data = _load_local_dataset_summary()
    if local_data:
        return local_data

    # 2. Network fallback if running outside repo structure
    try:
        res = requests.get(f"{get_base_url()}/api/dataset/summary", timeout=3.0)
        if res.status_code == 200:
            return res.json()
    except requests.exceptions.RequestException as e:
        logger.warning(f"Live API dataset summary unavailable: {e}.")

    return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_dataset_sample(limit: int = 15) -> Optional[List[Dict[str, Any]]]:
    """Retrieves a preview sample from the Flask API (cached for 1h, no spinner)."""
    try:
        res = requests.get(f"{get_base_url()}/api/dataset/sample?limit={limit}", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json().get("records", [])
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch dataset sample: {e}")
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_dataset_categories() -> Dict[str, List[str]]:
    """Retrieves unique categorical options for form fields (cached for 1h, no spinner)."""
    try:
        res = requests.get(f"{get_base_url()}/api/dataset/categories", timeout=3.0)
        if res.status_code == 200:
            cats = res.json().get("categories", {})
            if cats:
                return cats
    except requests.exceptions.RequestException as e:
        logger.warning(f"Using default categories: {e}")
    return _load_local_categories()


@st.cache_data(ttl=3600, show_spinner=False)
def get_dataset_catalog() -> List[Dict[str, Any]]:
    """Retrieves structured catalog of all organized dataset folders (cached for 1h, no spinner)."""
    try:
        res = requests.get(f"{get_base_url()}/api/dataset/catalog", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json().get("catalog", [])
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch dataset catalog: {e}")
        return []


def trigger_model_training(test_size: float = 0.20, force_retrain: bool = True) -> Dict[str, Any]:
    """Sends training request to the Flask backend (returns 202 Accepted + job_id immediately)."""
    try:
        payload = {"test_size": test_size, "force_retrain": force_retrain}
        res = requests.post(f"{get_base_url()}/api/models/train", json=payload, timeout=DEFAULT_TIMEOUT)
        return res.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Training request failed: {str(e)}"}


def get_training_status() -> Dict[str, Any]:
    """Polls background training job status. NEVER CACHED."""
    try:
        res = requests.get(f"{get_base_url()}/api/models/train/status", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json()
        return {"state": "unknown", "error": f"HTTP {res.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"state": "error", "error": str(e)}


def clear_all_api_caches():
    """Clears all Streamlit cached data across the app after training finishes."""
    global _RESOLVED_BASE_URL
    _RESOLVED_BASE_URL = None
    st.cache_data.clear()


@st.cache_data(ttl=3600, show_spinner=False)
def get_model_comparison() -> Optional[Dict[str, Any]]:
    """Retrieves model metrics and comparison data (instant local benchmark first, no spinner)."""
    # 1. Instant local load (< 1ms) so home & comparison render immediately
    local_eval = _load_local_model_comparison()
    if local_eval:
        return local_eval

    # 2. Network fallback if running outside repo structure
    try:
        res = requests.get(f"{get_base_url()}/api/models/compare", timeout=3.0)
        if res.status_code == 200:
            return res.json()
    except requests.exceptions.RequestException as e:
        logger.warning(f"Live API model comparison unavailable: {e}.")

    return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_feature_importance() -> Optional[Dict[str, Any]]:
    """Retrieves feature importance rankings (cached for 1h, with local fallback)."""
    local_fi = _load_local_feature_importance()
    if local_fi:
        return local_fi

    try:
        res = requests.get(f"{get_base_url()}/api/models/feature-importance", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json()
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch feature importance: {e}")
        return None


def predict_single(features: Dict[str, Any], model_name: str) -> Dict[str, Any]:
    """Sends single customer feature set for subscription prediction."""
    try:
        payload = {"features": features, "model": model_name}
        res = requests.post(f"{get_base_url()}/api/predict", json=payload, timeout=DEFAULT_TIMEOUT)
        return res.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Prediction request failed: {str(e)}"}


def predict_all_models_api(features: Dict[str, Any]) -> Dict[str, Any]:
    """Sends customer features to predict and compare across all 4 models simultaneously."""
    try:
        payload = {"features": features}
        res = requests.post(f"{get_base_url()}/api/predict/all", json=payload, timeout=DEFAULT_TIMEOUT)
        return res.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Multi-model prediction request failed: {str(e)}"}


def predict_batch_csv(df: pd.DataFrame, model_name: str) -> Dict[str, Any]:
    """Sends batch dataframe for predictions."""
    try:
        records = df.to_dict(orient="records")
        payload = {"records": records, "model": model_name}
        res = requests.post(f"{get_base_url()}/api/predict/batch", json=payload, timeout=TRAIN_TIMEOUT)
        return res.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Batch prediction failed: {str(e)}"}


@st.cache_data(ttl=3600, show_spinner=False)
def get_evaluation_report() -> Optional[Dict[str, Any]]:
    """Retrieves structured evaluation report (cached for 1h, no spinner)."""
    try:
        res = requests.get(f"{get_base_url()}/api/reports/evaluation", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json()
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch evaluation report: {e}")
        return None


def download_metrics_csv_url() -> str:
    """Returns direct endpoint URL for downloading metrics CSV."""
    return f"{get_base_url()}/api/reports/metrics-csv"


def download_report_pdf_url() -> str:
    """Returns direct endpoint URL for downloading academic PDF report."""
    return f"{get_base_url()}/api/reports/pdf"


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_metrics_csv_bytes() -> Optional[bytes]:
    """Fetches and caches the metrics CSV content bytes for instant in-app download."""
    try:
        res = requests.get(f"{get_base_url()}/api/reports/metrics-csv", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.content
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch metrics CSV bytes: {e}")
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_report_pdf_bytes() -> Optional[bytes]:
    """Fetches and caches the generated evaluation PDF content bytes."""
    try:
        res = requests.get(f"{get_base_url()}/api/reports/pdf", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.content
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch evaluation PDF bytes: {e}")
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_dataset_manifest() -> Optional[Dict[str, Any]]:
    """Retrieves dataset manifest from Data Cleaning & Splitting (cached for 1h, no spinner)."""
    try:
        from pathlib import Path
        import json
        manifest_path = Path(__file__).resolve().parent.parent.parent / "dataset" / "Data Cleaning & Splitting" / "dataset_manifest.json"
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass

    try:
        res = requests.get(f"{get_base_url()}/api/dataset/manifest", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json()
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch dataset manifest: {e}")
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_dataset_cleaning_summary(dataset_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves data_summary.json for a specific dataset (cached for 1h, no spinner)."""
    try:
        res = requests.get(f"{get_base_url()}/api/dataset/summary/{dataset_id}", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json().get("summary")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch dataset summary for {dataset_id}: {e}")
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_dataset_stage_details(dataset_id: str, stage: str, limit: int = 15) -> Optional[Dict[str, Any]]:
    """Retrieves metadata and preview for a specific dataset stage (cached for 1h, no spinner)."""
    try:
        params = {"dataset_id": dataset_id, "stage": stage, "limit": limit}
        res = requests.get(f"{get_base_url()}/api/dataset/stage", params=params, timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json().get("stage_details")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch stage details for {dataset_id}/{stage}: {e}")
        return None
