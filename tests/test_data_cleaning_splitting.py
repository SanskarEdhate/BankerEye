import json
import pandas as pd

from backend.config import DATASET_DIR
from backend.services.preprocessing import get_dataset_stage_details


def test_manifest_file_exists_and_valid():
    """Verifies that dataset_manifest.json exists and has valid structure."""
    manifest_path = DATASET_DIR / "Data Cleaning & Splitting" / "dataset_manifest.json"
    assert manifest_path.exists(), "dataset_manifest.json must exist in Data Cleaning & Splitting"

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_datasets_discovered"] == 3
    assert len(data["datasets"]) == 3
    dataset_ids = [d["dataset_id"] for d in data["datasets"]]
    assert "1_uci_bank_marketing_canonical" in dataset_ids
    assert "2_bank_additional_socioeconomic" in dataset_ids
    assert "3_train_test_competition" in dataset_ids


def test_all_five_stages_exist_for_each_dataset():
    """Verifies that each dataset directory contains all 5 required stage subdirectories and data_summary.json."""
    base_split_dir = DATASET_DIR / "Data Cleaning & Splitting"
    expected_stages = ["01_Raw_Data", "02_Unclean_Data", "03_Clean_Data", "04_Train_Data", "05_Test_Data"]

    for ds_id in ["1_uci_bank_marketing_canonical", "2_bank_additional_socioeconomic", "3_train_test_competition"]:
        ds_dir = base_split_dir / ds_id
        assert ds_dir.exists(), f"Dataset folder {ds_id} must exist"

        summary_file = ds_dir / "data_summary.json"
        assert summary_file.exists(), f"data_summary.json must exist for {ds_id}"

        with open(summary_file, "r", encoding="utf-8") as f:
            summary = json.load(f)

        assert "cleaned_record_count" in summary
        assert "cleaning_actions" in summary
        assert "split_method" in summary

        for stage in expected_stages:
            stage_dir = ds_dir / stage
            assert stage_dir.exists(), f"Stage directory {stage} must exist in {ds_id}"
            csvs = list(stage_dir.glob("*.csv"))
            assert len(csvs) > 0, f"Stage {stage} in {ds_id} must contain at least one CSV file"


def test_split_reconciliation_canonical():
    """Verifies that canonical train and test sum exactly to clean records as defined in summary."""
    summary_file = DATASET_DIR / "Data Cleaning & Splitting" / "1_uci_bank_marketing_canonical" / "data_summary.json"
    with open(summary_file, "r", encoding="utf-8") as f:
        summary = json.load(f)
    expected_clean_count = summary["cleaned_record_count"]

    clean_csv = DATASET_DIR / "Data Cleaning & Splitting" / "1_uci_bank_marketing_canonical" / "03_Clean_Data" / "bank-full_clean.csv"
    train_csv = DATASET_DIR / "Data Cleaning & Splitting" / "1_uci_bank_marketing_canonical" / "04_Train_Data" / "train.csv"
    test_csv = DATASET_DIR / "Data Cleaning & Splitting" / "1_uci_bank_marketing_canonical" / "05_Test_Data" / "test.csv"

    df_clean = pd.read_csv(clean_csv, sep=";")
    df_train = pd.read_csv(train_csv, sep=";")
    df_test = pd.read_csv(test_csv, sep=";")

    assert len(df_clean) == expected_clean_count
    assert len(df_train) + len(df_test) == len(df_clean)
    assert "y" in df_train.columns and "y" in df_test.columns


def test_duplicate_removal_socioeconomic():
    """Verifies that 12 duplicate rows were cleanly removed from bank-additional-full in clean stage."""
    raw_csv = DATASET_DIR / "Data Cleaning & Splitting" / "2_bank_additional_socioeconomic" / "01_Raw_Data" / "bank-additional-full.csv"
    clean_csv = DATASET_DIR / "Data Cleaning & Splitting" / "2_bank_additional_socioeconomic" / "03_Clean_Data" / "bank-additional-full_clean.csv"

    df_raw = pd.read_csv(raw_csv, sep=";")
    df_clean = pd.read_csv(clean_csv, sep=";")

    assert len(df_raw) == 41188
    assert len(df_clean) == 41176
    assert df_clean.duplicated().sum() == 0


def test_service_stage_details():
    """Verifies get_dataset_stage_details service returns structured metadata and preview."""
    summary_file = DATASET_DIR / "Data Cleaning & Splitting" / "1_uci_bank_marketing_canonical" / "data_summary.json"
    with open(summary_file, "r", encoding="utf-8") as f:
        summary = json.load(f)
    expected_rows = summary["cleaned_record_count"]

    details = get_dataset_stage_details("1_uci_bank_marketing_canonical", "03_Clean_Data", preview_limit=5)
    assert details["exists"] is True
    assert details["dimensions"]["rows"] == expected_rows
    assert details["dimensions"]["columns"] == 17
    assert len(details["preview_records"]) == 5
    assert details["missing_cells"] == 0
    assert details["duplicate_rows"] == 0


def test_api_manifest_and_stage_endpoints(client):
    """Verifies Flask endpoints /api/dataset/manifest and /api/dataset/stage."""
    summary_file = DATASET_DIR / "Data Cleaning & Splitting" / "1_uci_bank_marketing_canonical" / "data_summary.json"
    with open(summary_file, "r", encoding="utf-8") as f:
        summary = json.load(f)
    expected_rows = summary["cleaned_record_count"]

    res_manifest = client.get("/api/dataset/manifest")
    assert res_manifest.status_code == 200
    data_m = res_manifest.get_json()
    assert data_m["total_datasets_discovered"] == 3

    res_stage = client.get("/api/dataset/stage?dataset_id=1_uci_bank_marketing_canonical&stage=03_Clean_Data")
    assert res_stage.status_code == 200
    data_s = res_stage.get_json()
    assert data_s["status"] == "success"
    assert data_s["stage_details"]["dimensions"]["rows"] == expected_rows

    res_summary = client.get("/api/dataset/summary/1_uci_bank_marketing_canonical")
    assert res_summary.status_code == 200
    data_sum = res_summary.get_json()
    assert data_sum["status"] == "success"
    assert data_sum["summary"]["cleaned_record_count"] == expected_rows
