from pathlib import Path
import pytest
import pandas as pd
from backend.services.preprocessing import (
    detect_csv_delimiter,
    resolve_dataset_path,
    load_dataset,
    get_dataset_summary,
    prepare_train_test_data,
    build_preprocessor,
)


def test_detect_csv_delimiter():
    """Verify delimiter detection accurately detects semicolon in bank-full.csv."""
    ds_path = resolve_dataset_path()
    delim = detect_csv_delimiter(ds_path)
    assert delim == ";", f"Expected semicolon delimiter, got: '{delim}'"


def test_resolve_dataset_path_valid():
    """Verify default candidate dataset exists and is located correctly."""
    ds_path = resolve_dataset_path()
    assert ds_path.exists()
    assert ds_path.name in ["bank-full.csv", "bank.csv", "bank-full_clean.csv"]


def test_resolve_dataset_path_missing():
    """Verify FileNotFoundError is raised when an invalid dataset path is requested."""
    with pytest.raises(FileNotFoundError):
        resolve_dataset_path("non_existent_dataset_file_123.csv")


def test_load_dataset():
    """Verify dataset loading loads all 45,211 rows and 17 columns."""
    df, meta = load_dataset()
    assert isinstance(df, pd.DataFrame)
    assert meta["total_rows"] == 45211
    assert meta["total_columns"] == 17
    assert "y" in df.columns
    assert "duration" in df.columns


def test_dataset_summary_structure():
    """Verify dataset summary metadata dictionary structure."""
    summary = get_dataset_summary()
    assert summary["status"] == "success"
    assert summary["total_rows"] == 45211
    assert summary["total_columns"] == 17
    assert summary["total_missing_cells"] == 0
    assert summary["duplicate_rows"] == 0
    assert "yes" in summary["target_distribution"]
    assert "no" in summary["target_distribution"]
    assert "duration" in summary["excluded_features_main"]


def test_prepare_train_test_data_leakage_prevention():
    """
    CRITICAL TEST: Verify feature 'duration' is strictly excluded from features,
    and target is correctly encoded as 0 and 1 with stratified 80/20 split.
    """
    X_train, X_test, y_train, y_test, meta = prepare_train_test_data(
        test_size=0.20,
        random_state=42,
        exclude_duration=True,
    )

    # 1. Anti-leakage duration check
    assert "duration" not in X_train.columns, "LEAKAGE: 'duration' found in X_train!"
    assert "duration" not in X_test.columns, "LEAKAGE: 'duration' found in X_test!"
    assert "y" not in X_train.columns, "Target 'y' found in X_train!"
    assert X_train.shape[1] == 15, f"Expected 15 features, got {X_train.shape[1]}"

    # 2. Split sizes check
    assert len(X_train) == 36168
    assert len(X_test) == 9043
    assert len(y_train) == 36168
    assert len(y_test) == 9043

    # 3. Target encoding check: only 0 and 1
    assert set(y_train.unique()) == {0, 1}
    assert set(y_test.unique()) == {0, 1}

    # 4. Stratification check: ratio should be approximately 11.7% in both
    train_pos_pct = (y_train == 1).mean() * 100
    test_pos_pct = (y_test == 1).mean() * 100
    assert abs(train_pos_pct - 11.70) < 0.2
    assert abs(test_pos_pct - 11.70) < 0.2


def test_build_preprocessor():
    """Verify ColumnTransformer successfully transforms numerical and categorical features."""
    preprocessor = build_preprocessor(scale_numerical=True)
    X_train, _, _, _, _ = prepare_train_test_data()

    # Fit and transform a small slice
    transformed = preprocessor.fit_transform(X_train.head(50))
    assert transformed.shape[0] == 50
    assert transformed.shape[1] > 15  # OneHotEncoder expands categories
