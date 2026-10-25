import sys
from pathlib import Path
import pytest
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app


@pytest.fixture(scope="session")
def app():
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
