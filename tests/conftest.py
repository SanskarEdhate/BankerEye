import sys
from pathlib import Path
import pytest
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app
import tempfile
from unittest.mock import patch


@pytest.fixture(scope="session", autouse=True)
def ensure_models_trained():
    """
    If saved models are missing, train tiny models on a small sample into a temp dir
    (monkeypatch SAVED_MODELS_DIR) so a fresh clone passes pytest with no manual step.
    """
    import backend.config as cfg
    from backend.config import EXPECTED_MODEL_FILES, SAVED_MODELS_DIR
    import backend.services.train_models as tm
    import backend.routes.report_routes as rr
    import backend.app as ba

    metrics_file = SAVED_MODELS_DIR / "model_metrics.json"
    all_joblib_exist = all((SAVED_MODELS_DIR / fname).exists() for fname in EXPECTED_MODEL_FILES)

    if all_joblib_exist and metrics_file.exists():
        yield
        return

    # Create temporary directory for tiny models
    temp_dir = tempfile.TemporaryDirectory()
    tmp_path = Path(temp_dir.name)

    orig_cfg = cfg.SAVED_MODELS_DIR
    orig_tm = tm.SAVED_MODELS_DIR
    orig_rr = rr.SAVED_MODELS_DIR
    orig_ba = ba.SAVED_MODELS_DIR

    cfg.SAVED_MODELS_DIR = tmp_path
    tm.SAVED_MODELS_DIR = tmp_path
    rr.SAVED_MODELS_DIR = tmp_path
    ba.SAVED_MODELS_DIR = tmp_path

    # Train tiny models on a small balanced sample
    df, meta = tm.load_dataset()
    df_sample = pd.concat(
        [df[df["y"] == "no"].head(80), df[df["y"] == "yes"].head(20)]
    ).sample(frac=1.0, random_state=42).reset_index(drop=True)
    meta_sample = dict(meta)
    meta_sample["total_rows"] = len(df_sample)

    with patch.object(tm, "load_dataset", return_value=(df_sample, meta_sample)):
        tm.train_and_evaluate_all_models(force_retrain=True)

    yield

    cfg.SAVED_MODELS_DIR = orig_cfg
    tm.SAVED_MODELS_DIR = orig_tm
    rr.SAVED_MODELS_DIR = orig_rr
    ba.SAVED_MODELS_DIR = orig_ba
    temp_dir.cleanup()


@pytest.fixture(scope="session")
def app(ensure_models_trained):
    """Session-scoped Flask application instance."""
    app_instance = create_app()
    app_instance.config.update({"TESTING": True})
    return app_instance


@pytest.fixture(scope="session")
def client(app):
    """Test client for HTTP requests."""
    return app.test_client()


@pytest.fixture
def valid_customer_dict():
    """A valid single customer input matching all schema constraints."""
    return {
        "age": 35,
        "job": "management",
        "marital": "married",
        "education": "tertiary",
        "default": "no",
        "balance": 3500,
        "housing": "no",
        "loan": "no",
        "contact": "cellular",
        "day": 12,
        "month": "aug",
        "campaign": 1,
        "pdays": -1,
        "previous": 0,
        "poutcome": "unknown",
    }


@pytest.fixture
def sample_batch_df(valid_customer_dict):
    """Small dataframe fixture for testing batch predictions."""
    rows = [valid_customer_dict.copy() for _ in range(5)]
    # Vary age and balance
    for idx, r in enumerate(rows):
        r["age"] = 30 + idx * 5
        r["balance"] = 1000 + idx * 1000
    return pd.DataFrame(rows)
