
def test_api_health_endpoint(client):
    """Verify /api/health returns 200 and healthy status."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["dataset_available"] is True
    assert data["models_trained"] is True
    assert data["version"] == "1.0.0"


def test_api_dataset_summary(client):
    """Verify /api/dataset/summary returns dataset metadata."""
    res = client.get("/api/dataset/summary")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["total_rows"] == 45211
    assert data["total_columns"] == 17
    assert data["total_missing_cells"] == 0
    assert "yes" in data["target_distribution"]


def test_api_dataset_sample(client):
    """Verify /api/dataset/sample returns bounded records without dumping entire dataset."""
    res = client.get("/api/dataset/sample?limit=7")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["records"]) == 7
    assert data["requested_limit"] == 7
    assert data["total_rows_in_dataset"] == 45211


def test_api_models_compare(client):
    """Verify /api/models/compare returns trained model comparison data."""
    res = client.get("/api/models/compare")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ready"
    assert len(data["models"]) == 4
    assert "random_forest" in data["models"]
    assert "f1_score" in data["rankings"]


def test_api_single_model_metrics(client):
    """Verify /api/models/<model_name>/metrics returns metrics for a valid model."""
    res = client.get("/api/models/random_forest/metrics")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["model_key"] == "random_forest"
    assert "metrics" in data["model_data"]
    assert "confusion_matrix" in data["model_data"]


def test_api_single_model_metrics_unknown_404(client):
    """Verify requesting an unknown model name returns 404."""
    res = client.get("/api/models/super_quantum_boost/metrics")
    assert res.status_code == 404
    data = res.get_json()
    assert data["status"] == "error"


def test_api_feature_importance(client):
    """Verify /api/models/feature-importance returns rankings and disclaimer."""
    res = client.get("/api/models/feature-importance")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "disclaimer" in data
    assert "feature_importance" in data


def test_api_predict_valid_payload(client, valid_customer_dict):
    """Verify /api/predict succeeds with valid customer features."""
    payload = {"model": "random_forest", "features": valid_customer_dict}
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["prediction"] in [0, 1]
    assert "probability" in data
    assert data["model_key"] == "random_forest"


def test_api_predict_all_models_endpoint(client, valid_customer_dict):
    """Verify /api/predict/all evaluates across all four models and returns consensus."""
    payload = {"features": valid_customer_dict}
    res = client.post("/api/predict/all", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "consensus" in data
    assert "models" in data
    assert len(data["models"]) == 4
    for k in ["random_forest", "decision_tree", "logistic_regression", "knn"]:
        assert k in data["models"]
        assert "benchmark_accuracy" in data["models"][k]
        assert "prediction" in data["models"][k]
        assert "probability" in data["models"][k]



def test_api_predict_invalid_payload_422(client):
    """Verify /api/predict rejects invalid / incomplete data with 422."""
    payload = {"model": "random_forest", "features": {"age": -5}}
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 422
    data = res.get_json()
    assert data["status"] == "error"


def test_api_predict_batch_endpoint(client, valid_customer_dict):
    """Verify /api/predict/batch processes list of records."""
    records = [valid_customer_dict.copy() for _ in range(3)]
    payload = {"model": "random_forest", "records": records}
    res = client.post("/api/predict/batch", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["total_records"] == 3
    assert len(data["results"]) == 3


def test_api_reports_evaluation(client):
    """Verify /api/reports/evaluation returns structured evaluation report."""
    res = client.get("/api/reports/evaluation")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "models" in data
    assert "rankings" in data


def test_api_reports_metrics_csv(client):
    """Verify /api/reports/metrics-csv streams CSV content."""
    res = client.get("/api/reports/metrics-csv")
    assert res.status_code == 200
    assert "text/csv" in res.content_type
    assert b"Model Name" in res.data
    assert b"F1-Score" in res.data


def test_api_reports_pdf(client):
    """Verify /api/reports/pdf serves the formal PDF document."""
    res = client.get("/api/reports/pdf")
    assert res.status_code == 200
    assert "application/pdf" in res.content_type
    assert res.data.startswith(b"%PDF")
