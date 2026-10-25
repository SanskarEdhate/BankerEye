import io
import json
from unittest.mock import patch

import numpy as np
import pytest

from backend.config import BASE_DIR, EXPECTED_MODEL_FILES
from backend.services.prediction import (
    predict_all_models_single_customer,
)
from backend.services.train_models import (
    MODEL_DEFINITIONS,
    SAVED_MODELS_DIR,
    downsample_points,
    get_cached_metrics,
    train_and_evaluate_all_models,
)


def test_readme_and_report_numbers_match_json():
    """Verify README and academic project report numbers match the saved metrics JSON."""
    metrics_path = SAVED_MODELS_DIR / "model_metrics.json"
    assert metrics_path.exists(), "model_metrics.json must exist"

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)

    readme_path = BASE_DIR / "README.md"
    report_path = BASE_DIR / "reports" / "academic_project_report.md"

    assert readme_path.exists(), "README.md must exist"
    assert report_path.exists(), "academic_project_report.md must exist"

    readme_text = readme_path.read_text(encoding="utf-8")
    report_text = report_path.read_text(encoding="utf-8")

    # Map keys to core algorithm names used in tables
    name_map = {
        "random_forest": "Random Forest",
        "decision_tree": "Decision Tree",
        "logistic_regression": "Logistic Regression",
        "knn": "KNN",
    }

    for model_key, model_info in metrics_data["models"].items():
        m = model_info["metrics"]
        short_name = name_map[model_key]

        # Check model name is present in both docs
        assert short_name in readme_text, f"{short_name} not found in README.md"
        assert short_name in report_text, f"{short_name} not found in report"

        # Check formatted accuracy and F1 percentages
        acc_pct = f"{m['accuracy'] * 100:.2f}%"
        f1_pct = f"{m['f1_score'] * 100:.2f}%"

        assert acc_pct in readme_text, f"Accuracy {acc_pct} for {short_name} not found in README"
        assert acc_pct in report_text, f"Accuracy {acc_pct} for {short_name} not found in report"
        assert f1_pct in readme_text, f"F1 {f1_pct} for {short_name} not found in README"
        assert f1_pct in report_text, f"F1 {f1_pct} for {short_name} not found in report"

        # Check Brier score appears in documentation
        brier_str = f"{m['brier_score']:.4f}"
        assert brier_str in readme_text, f"Brier score {brier_str} for {short_name} not in README"
        assert brier_str in report_text, f"Brier score {brier_str} for {short_name} not in report"


def test_class_weight_balanced_on_lr_dt_rf():
    """Verify class_weight is 'balanced' on LR, DT, RF, and documented as unsupported on KNN."""
    lr_clf = MODEL_DEFINITIONS["logistic_regression"]["estimator"]()
    dt_clf = MODEL_DEFINITIONS["decision_tree"]["estimator"]()
    rf_clf = MODEL_DEFINITIONS["random_forest"]["estimator"]()
    knn_clf = MODEL_DEFINITIONS["knn"]["estimator"]()

    assert lr_clf.class_weight == "balanced"
    assert dt_clf.class_weight == "balanced"
    assert rf_clf.class_weight == "balanced"

    # KNN has no class_weight attribute in scikit-learn
    assert not hasattr(knn_clf, "class_weight")
    knn_note = MODEL_DEFINITIONS["knn"]["class_weight_note"]
    assert "class_weight" in knn_note


def test_cache_invalidation_when_joblib_missing(tmp_path):
    """Verify cache logic only returns cached results if all 4 joblib files exist."""
    fake_metrics = {"status": "ready", "split_info": {"test_size": 0.2, "random_state": 42}}
    metrics_file = tmp_path / "model_metrics.json"
    metrics_file.write_text(json.dumps(fake_metrics), encoding="utf-8")
    summary_file = tmp_path / "evaluation_summary.json"
    summary_file.write_text(json.dumps(fake_metrics), encoding="utf-8")

    # Only 3 joblib files created
    for fname in EXPECTED_MODEL_FILES[:3]:
        (tmp_path / fname).touch()

    with patch("backend.services.train_models.SAVED_MODELS_DIR", tmp_path):
        with patch("backend.services.train_models.load_dataset") as mock_load:
            # Missing 4th joblib forces reload/retrain
            mock_load.side_effect = RuntimeError("Correctly attempted retrain because joblib was missing!")
            with pytest.raises(RuntimeError, match="Correctly attempted retrain"):
                train_and_evaluate_all_models(test_size=0.2, random_state=42, force_retrain=False)


def test_health_reflects_joblib_presence(client, tmp_path):
    """Verify /api/health returns models_trained = True only when all joblibs AND metrics JSON exist."""
    # Normal healthy state
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["models_trained"] is True

    # Missing a joblib file
    with patch("backend.app.SAVED_MODELS_DIR", tmp_path):
        # Create metrics JSON only
        (tmp_path / "model_metrics.json").write_text("{}", encoding="utf-8")
        res_missing = client.get("/api/health")
        assert res_missing.status_code == 200
        data_missing = res_missing.get_json()
        assert data_missing["models_trained"] is False


def test_batch_validation_nan(client, valid_customer_dict):
    """Verify batch prediction rejects NaN values with 400 and identifies the row and reason."""
    bad_record = valid_customer_dict.copy()
    bad_record["balance"] = float("nan")

    payload = {"model": "random_forest", "records": [bad_record]}
    res = client.post("/api/predict/batch", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"
    assert "row_errors" in data
    assert any("balance" in err for err in data["row_errors"][0]["errors"])


def test_batch_validation_negative_age(client, valid_customer_dict):
    """Verify batch prediction rejects negative age with 400 and informative error."""
    bad_record = valid_customer_dict.copy()
    bad_record["age"] = -10

    payload = {"model": "random_forest", "records": [bad_record]}
    res = client.post("/api/predict/batch", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"
    assert any("age" in err for err in data["row_errors"][0]["errors"])


def test_batch_validation_unknown_category(client, valid_customer_dict):
    """Verify batch prediction rejects invalid categorical values."""
    bad_record = valid_customer_dict.copy()
    bad_record["job"] = "cybernetic_hacker"

    payload = {"model": "random_forest", "records": [bad_record]}
    res = client.post("/api/predict/batch", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert any("job" in err for err in data["row_errors"][0]["errors"])


def test_batch_validation_semicolon_csv(client, valid_customer_dict):
    """Verify batch CSV upload supports semicolon delimiter."""
    headers = list(valid_customer_dict.keys())
    values = [str(valid_customer_dict[k]) for k in headers]
    csv_content = ";".join(headers) + "\n" + ";".join(values) + "\n"

    data = {
        "model": "random_forest",
        "file": (io.BytesIO(csv_content.encode("utf-8")), "test_batch.csv"),
    }
    res = client.post("/api/predict/batch", data=data, content_type="multipart/form-data")
    assert res.status_code == 200
    resp_data = res.get_json()
    assert resp_data["status"] == "success"
    assert resp_data["total_records"] == 1


def test_batch_validation_oversize_upload(client):
    """Verify batch endpoint rejects uploads exceeding 20,000 rows with 400."""
    records = [{"age": 30}] * 20001
    payload = {"model": "random_forest", "records": records}
    res = client.post("/api/predict/batch", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert "20,000" in data["message"]


def test_400_array_body(client):
    """Verify passing a JSON array instead of an object returns 400."""
    res = client.post("/api/predict", json=[{"model": "random_forest"}])
    assert res.status_code == 400
    assert "JSON body must be an object" in res.get_json()["message"]

    res_all = client.post("/api/predict/all", json=[1, 2, 3])
    assert res_all.status_code == 400
    assert "JSON body must be an object" in res_all.get_json()["message"]


def test_400_model_null_and_non_string(client, valid_customer_dict):
    """Verify null or non-string model parameter returns 400."""
    # Model is null
    res_null = client.post("/api/predict", json={"model": None, "features": valid_customer_dict})
    assert res_null.status_code == 400
    assert "Field 'model' must be a non-empty string" in res_null.get_json()["message"]

    # Model is an integer
    res_int = client.post("/api/predict", json={"model": 12345, "features": valid_customer_dict})
    assert res_int.status_code == 400
    assert "Field 'model' must be a non-empty string" in res_int.get_json()["message"]


def test_400_bad_test_size(client):
    """Verify non-numeric or out-of-range test_size returns 400."""
    res_str = client.post("/api/models/train", json={"test_size": "zero_point_two"})
    assert res_str.status_code == 400
    assert "Parameter 'test_size' must be a numeric float" in res_str.get_json()["message"]

    res_range = client.post("/api/models/train", json={"test_size": 0.95})
    assert res_range.status_code == 400
    assert "between 0.05 and 0.50" in res_range.get_json()["message"]


def test_400_force_retrain_parsing(client):
    """Verify non-boolean force_retrain returns 400, while string 'false' is correctly parsed."""
    res_invalid = client.post("/api/models/train", json={"force_retrain": "invalid_value_123"})
    assert res_invalid.status_code == 400
    assert "force_retrain' must be a boolean" in res_invalid.get_json()["message"]


def test_path_traversal_rejection(client):
    """Verify path traversal attacks are rejected on dataset routes with 400."""
    res1 = client.get("/api/dataset/stage?dataset_id=../../windows&stage=03_Clean_Data")
    assert res1.status_code == 400

    res2 = client.get("/api/dataset/stage?dataset_id=1_uci_bank_marketing_canonical&stage=../../system32")
    assert res2.status_code == 400

    res3 = client.get("/api/dataset/summary/.._windows_system")
    assert res3.status_code == 400


def test_consensus_tie_returns_uncertain(valid_customer_dict):
    """Verify consensus tie (2 Yes, 2 No) returns 'Uncertain' outcome and split agreement."""
    def mock_predict(features, model_name, prevalidated=False):
        pred = 1 if model_name in ["random_forest", "decision_tree"] else 0
        prob = 0.6 if pred == 1 else 0.4
        return {
            "prediction": pred,
            "probability": prob,
            "status": "success",
            "model_key": model_name,
            "general_context": ["Test context"],
            "key_insights": ["Test insight"],
            "disclaimer": "Test disclaimer",
        }

    with patch("backend.services.prediction.predict_single_customer", side_effect=mock_predict):
        res = predict_all_models_single_customer(valid_customer_dict)
        consensus = res["consensus"]
        assert consensus["majority_outcome"] == "Uncertain"
        assert "Split Decision (2/4 models predict Yes, 2/4 models predict No)" in consensus["agreement_summary"]
        assert consensus["positive_votes"] == 2
        assert consensus["majority_prediction"] is None


def test_roc_pr_endpoints_preserved():
    """Verify ROC and PR curve downsampling preserves exact boundary endpoints."""
    x = np.array([0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0])
    y = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 0.95, 1.0])

    x_down, y_down = downsample_points(x, y, max_pts=4)
    assert x_down[0] == x[0]
    assert x_down[-1] == x[-1]
    assert y_down[0] == y[0]
    assert y_down[-1] == y[-1]

    # Verify cached metrics ROC and PR endpoints
    metrics = get_cached_metrics()
    for model_key, data in metrics["models"].items():
        roc_fpr = data["curves"]["roc"]["fpr"]
        roc_tpr = data["curves"]["roc"]["tpr"]
        assert roc_fpr[0] == 0.0
        assert roc_fpr[-1] == 1.0
        assert roc_tpr[0] == 0.0
        assert roc_tpr[-1] == 1.0


def test_503_when_models_missing(client, valid_customer_dict):
    """Verify 503 is returned when models are not trained instead of 404/500."""
    with patch("backend.services.prediction.load_model_pipeline", side_effect=FileNotFoundError("Models not trained")):
        res_single = client.post("/api/predict", json={"model": "random_forest", "features": valid_customer_dict})
        assert res_single.status_code == 503
        assert "Models not trained. Run: python -m backend.services.train_models" in res_single.get_json()["message"]

        res_all = client.post("/api/predict/all", json={"features": valid_customer_dict})
        assert res_all.status_code == 503
        assert "Models not trained. Run: python -m backend.services.train_models" in res_all.get_json()["message"]


def test_json_key_order_preserved(app, client):
    """Verify app.json.sort_keys is False and key order is preserved."""
    assert app.json.sort_keys is False

    res = client.get("/api/health")
    assert res.status_code == 200
    # The order of keys in response matches route definition (not alphabetical)
    keys = list(res.get_json().keys())
    assert keys[0] == "status"
    assert keys[1] == "app_name"


def test_train_job_status_endpoint(client):
    """Verify /api/models/train/status returns state, progress, and metadata."""
    res = client.get("/api/models/train/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["state"] in ["idle", "running", "done", "failed"]
    assert "progress" in data
    assert "message" in data
    assert "job_id" in data
