import os
import logging
from typing import Any, Dict, List, Optional
import requests
import pandas as pd

logger = logging.getLogger(__name__)

API_BASE_URL = os.getenv("STREAMLIT_API_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
DEFAULT_TIMEOUT = 12.0
TRAIN_TIMEOUT = 90.0

__all__ = [
    "API_BASE_URL",
    "check_api_health",
    "get_dataset_summary",
    "get_dataset_sample",
    "get_dataset_categories",
    "get_dataset_catalog",
    "trigger_model_training",
    "get_model_comparison",
    "get_feature_importance",
    "predict_single",
    "predict_all_models_api",
    "predict_batch_csv",
    "get_evaluation_report",
    "download_metrics_csv_url",
    "download_report_pdf_url",
    "get_dataset_manifest",
    "get_dataset_cleaning_summary",
    "get_dataset_stage_details",
]


def check_api_health() -> Dict[str, Any]:
    """Checks whether the Flask backend is running and healthy."""
    try:
        url = f"{API_BASE_URL}/api/health"
        res = requests.get(url, timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json()
        return {"status": "unhealthy", "code": res.status_code}
    except requests.exceptions.RequestException as e:
        logger.warning(f"Health check failed: {e}")
        return {
            "status": "offline",
            "message": f"Flask API unreachable at {API_BASE_URL}. Ensure 'python backend/app.py' is running.",
        }


def get_dataset_summary() -> Optional[Dict[str, Any]]:
    """Retrieves dataset summary from the Flask API."""
    try:
        res = requests.get(f"{API_BASE_URL}/api/dataset/summary", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json()
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch dataset summary: {e}")
        return None


def get_dataset_sample(limit: int = 15) -> Optional[List[Dict[str, Any]]]:
    """Retrieves a preview sample from the Flask API."""
    try:
        res = requests.get(f"{API_BASE_URL}/api/dataset/sample?limit={limit}", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json().get("records", [])
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch dataset sample: {e}")
        return None


def get_dataset_categories() -> Dict[str, List[str]]:
    """Retrieves unique categorical options for form fields."""
    try:
        res = requests.get(f"{API_BASE_URL}/api/dataset/categories", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json().get("categories", {})
        return {}
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch categories: {e}")
        return {}


def get_dataset_catalog() -> List[Dict[str, Any]]:
    """Retrieves structured catalog of all organized dataset folders."""
    try:
        res = requests.get(f"{API_BASE_URL}/api/dataset/catalog", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json().get("catalog", [])
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch dataset catalog: {e}")
        return []



def trigger_model_training(test_size: float = 0.20, force_retrain: bool = True) -> Dict[str, Any]:
    """Sends training request to the Flask backend."""
    try:
        payload = {"test_size": test_size, "force_retrain": force_retrain}
        res = requests.post(f"{API_BASE_URL}/api/models/train", json=payload, timeout=TRAIN_TIMEOUT)
        return res.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Training request failed: {str(e)}"}


def get_model_comparison() -> Optional[Dict[str, Any]]:
    """Retrieves model metrics and comparison data."""
    try:
        res = requests.get(f"{API_BASE_URL}/api/models/compare", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json()
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch model comparison: {e}")
        return None


def get_feature_importance() -> Optional[Dict[str, Any]]:
    """Retrieves feature importance rankings."""
    try:
        res = requests.get(f"{API_BASE_URL}/api/models/feature-importance", timeout=DEFAULT_TIMEOUT)
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
        res = requests.post(f"{API_BASE_URL}/api/predict", json=payload, timeout=DEFAULT_TIMEOUT)
        return res.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Prediction request failed: {str(e)}"}


def predict_all_models_api(features: Dict[str, Any]) -> Dict[str, Any]:
    """Sends customer features to predict and compare across all 4 models simultaneously."""
    try:
        payload = {"features": features}
        res = requests.post(f"{API_BASE_URL}/api/predict/all", json=payload, timeout=DEFAULT_TIMEOUT)
        return res.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Multi-model prediction request failed: {str(e)}"}



def predict_batch_csv(df: pd.DataFrame, model_name: str) -> Dict[str, Any]:
    """Sends batch dataframe for predictions."""
    try:
        records = df.to_dict(orient="records")
        payload = {"records": records, "model": model_name}
        res = requests.post(f"{API_BASE_URL}/api/predict/batch", json=payload, timeout=TRAIN_TIMEOUT)
        return res.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Batch prediction failed: {str(e)}"}


def get_evaluation_report() -> Optional[Dict[str, Any]]:
    """Retrieves structured evaluation report."""
    try:
        res = requests.get(f"{API_BASE_URL}/api/reports/evaluation", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json()
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch evaluation report: {e}")
        return None


def download_metrics_csv_url() -> str:
    """Returns direct endpoint URL for downloading metrics CSV."""
    return f"{API_BASE_URL}/api/reports/metrics-csv"


def download_report_pdf_url() -> str:
    """Returns direct endpoint URL for downloading academic PDF report."""
    return f"{API_BASE_URL}/api/reports/pdf"


def get_dataset_manifest() -> Optional[Dict[str, Any]]:
    """Retrieves dataset manifest from Data Cleaning & Splitting."""
    try:
        res = requests.get(f"{API_BASE_URL}/api/dataset/manifest", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json()
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch dataset manifest: {e}")
        return None


def get_dataset_cleaning_summary(dataset_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves data_summary.json for a specific dataset."""
    try:
        res = requests.get(f"{API_BASE_URL}/api/dataset/summary/{dataset_id}", timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json().get("summary")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch dataset summary for {dataset_id}: {e}")
        return None


def get_dataset_stage_details(dataset_id: str, stage: str, limit: int = 15) -> Optional[Dict[str, Any]]:
    """Retrieves metadata and preview for a specific dataset stage."""
    try:
        params = {"dataset_id": dataset_id, "stage": stage, "limit": limit}
        res = requests.get(f"{API_BASE_URL}/api/dataset/stage", params=params, timeout=DEFAULT_TIMEOUT)
        if res.status_code == 200:
            return res.json().get("stage_details")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch stage details for {dataset_id}/{stage}: {e}")
        return None

