import csv
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from backend.config import (
    DATASET_CANDIDATES,
    TARGET_COLUMN,
    EXCLUDED_FEATURES_MAIN,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    DEFAULT_TEST_SIZE,
    RANDOM_STATE,
)

logger = logging.getLogger(__name__)


def detect_csv_delimiter(file_path: Path) -> str:
    """Detects delimiter of a CSV file automatically using csv.Sniffer."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        sample = f.read(8192)

    try:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample)
        delimiter = dialect.delimiter
        # Validate that delimiter is reasonable
        if delimiter in [";", ",", "\t", "|"]:
            return delimiter
    except Exception as e:
        logger.warning(f"csv.Sniffer failed on {file_path}: {e}. Falling back to heuristic.")

    # Heuristic fallback: count frequency of ';' vs ',' in the header line
    lines = sample.splitlines()
    if lines:
        header = lines[0]
        if header.count(";") > header.count(","):
            return ";"
        return ","
    return ";"


def resolve_dataset_path(custom_path: Optional[str] = None) -> Path:
    """Finds the actual dataset path from custom argument or default candidates."""
    if custom_path:
        p = Path(custom_path)
        if p.exists():
            return p
        raise FileNotFoundError(f"Requested dataset file does not exist: {custom_path}")

    for candidate in DATASET_CANDIDATES:
        if candidate.exists() and candidate.is_file():
            return candidate

    raise FileNotFoundError(
        f"No dataset found in candidate paths: {[str(c) for c in DATASET_CANDIDATES]}. "
        "Please place bank-full.csv or bank.csv inside the dataset/ directory."
    )


def load_dataset(file_path: Optional[Path] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads dataset, detects delimiter, inspects structure, and returns DataFrame
    along with metadata.
    """
    resolved_path = resolve_dataset_path(str(file_path) if file_path else None)
    delimiter = detect_csv_delimiter(resolved_path)

    df = pd.read_csv(resolved_path, sep=delimiter)

    # Detect target column ('y' or 'subscribe')
    target_col = TARGET_COLUMN
    if target_col not in df.columns and "subscribe" in df.columns:
        target_col = "subscribe"

    # Basic metadata
    meta = {
        "file_name": resolved_path.name,
        "file_path": str(resolved_path),
        "delimiter": delimiter,
        "total_rows": int(df.shape[0]),
        "total_columns": int(df.shape[1]),
        "columns": df.columns.tolist(),
        "target_column": target_col,
        "has_target": target_col in df.columns,
    }

    if not meta["has_target"]:
        raise ValueError(f"Required target column ('{TARGET_COLUMN}' or 'subscribe') not found in dataset {resolved_path.name}")

    return df, meta


def get_available_datasets_list() -> List[Dict[str, Any]]:
    """Returns a structured catalog of all organized datasets in dataset/ directory."""
    from backend.config import DATASET_DIR
    catalog = []

    dataset_folders = [
        {
            "folder": "1_uci_bank_marketing_canonical",
            "name": "Canonical UCI Bank Marketing Dataset",
            "description": "Original benchmark dataset by Moro et al. (2011/2014) containing 45,211 rows.",
            "primary_file": "bank-full.csv",
        },
        {
            "folder": "2_bank_additional_socioeconomic",
            "name": "Socioeconomic Extended Dataset (bank-additional)",
            "description": "Enriched with 5 macroeconomic indicators from Banco de Portugal containing 41,188 rows.",
            "primary_file": "bank-additional-full.csv",
        },
        {
            "folder": "3_train_test_competition",
            "name": "Competition Train/Test Split Dataset",
            "description": "Partitioned into 22,501 labeled training records and 7,501 unlabeled test records.",
            "primary_file": "train.csv",
        },
    ]

    for item in dataset_folders:
        dir_path = DATASET_DIR / item["folder"]
        if dir_path.exists():
            files = [f.name for f in dir_path.iterdir() if f.is_file()]
            catalog.append({
                "folder": item["folder"],
                "name": item["name"],
                "description": item["description"],
                "primary_file": item["primary_file"],
                "files_count": len(files),
                "files": files,
                "exists": True,
            })
    return catalog


def get_dataset_manifest() -> Dict[str, Any]:
    """Returns the dataset manifest generated in dataset/Data Cleaning & Splitting/."""
    from backend.config import DATASET_DIR
    manifest_file = DATASET_DIR / "Data Cleaning & Splitting" / "dataset_manifest.json"
    if manifest_file.exists():
        with open(manifest_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"status": "error", "message": "dataset_manifest.json not found"}


def get_dataset_cleaning_summary(dataset_id: str) -> Dict[str, Any]:
    """Loads data_summary.json for a given dataset."""
    from backend.config import DATASET_DIR
    summary_file = DATASET_DIR / "Data Cleaning & Splitting" / dataset_id / "data_summary.json"
    if summary_file.exists():
        with open(summary_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"status": "error", "message": f"Summary for {dataset_id} not found"}


def get_dataset_stage_details(dataset_id: str, stage: str, preview_limit: int = 15) -> Dict[str, Any]:
    """
    Loads information and preview rows for a specific stage of a dataset.
    Supported stages: '01_Raw_Data', '02_Unclean_Data', '03_Clean_Data', '04_Train_Data', '05_Test_Data'.
    """
    from backend.config import DATASET_DIR
    stage_dir = DATASET_DIR / "Data Cleaning & Splitting" / dataset_id / stage
    if not stage_dir.exists():
        return {
            "exists": False,
            "dataset_id": dataset_id,
            "stage": stage,
            "error": f"Stage directory '{stage}' does not exist",
            "is_applicable": False,
        }

    # Find the primary CSV in that stage
    csv_files = sorted(list(stage_dir.glob("*.csv")), key=lambda p: p.stat().st_size, reverse=True)
    if not csv_files:
        return {
            "exists": False,
            "dataset_id": dataset_id,
            "stage": stage,
            "error": f"No tabular data file in {stage}",
            "is_applicable": False,
        }

    primary_csv = csv_files[0]
    sep = detect_csv_delimiter(primary_csv)
    df = pd.read_csv(primary_csv, sep=sep)

    return {
        "exists": True,
        "is_applicable": True,
        "dataset_id": dataset_id,
        "stage": stage,
        "file_name": primary_csv.name,
        "relative_path": str(primary_csv.relative_to(DATASET_DIR.parent)),
        "available_files": [f.name for f in stage_dir.iterdir() if f.is_file()],
        "dimensions": {
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
        },
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_cells": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "preview_records": df.head(preview_limit).to_dict(orient="records"),
    }


def get_dataset_summary(file_path: Optional[Path] = None) -> Dict[str, Any]:
    """Generates a comprehensive summary of the dataset for the API and frontend."""
    df, meta = load_dataset(file_path)
    target_col = meta.get("target_column", TARGET_COLUMN)

    missing_series = df.isnull().sum()
    missing_summary = {col: int(cnt) for col, cnt in missing_series.items() if cnt > 0}

    duplicates_count = int(df.duplicated().sum())

    # Target distribution
    target_counts = df[target_col].value_counts()
    target_distribution = {
        str(k): {
            "count": int(v),
            "percentage": round(float(v / len(df) * 100), 2),
        }
        for k, v in target_counts.items()
    }


    # Categorical distributions and 'unknown' counts
    cat_summary = {}
    cat_columns = df.select_dtypes(include=["object"]).columns.tolist()
    for col in cat_columns:
        counts = df[col].value_counts().to_dict()
        unknown_cnt = int((df[col] == "unknown").sum())
        cat_summary[col] = {
            "unique_values_count": len(counts),
            "unknown_count": unknown_cnt,
            "unknown_percentage": round(unknown_cnt / len(df) * 100, 2),
            "top_values": {str(k): int(v) for k, v in list(counts.items())[:10]},
        }

    # Numerical statistics
    num_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    num_summary = {}
    for col in num_columns:
        num_summary[col] = {
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "mean": round(float(df[col].mean()), 2),
            "median": round(float(df[col].median()), 2),
            "std": round(float(df[col].std()), 2),
        }

    return {
        "status": "success",
        "file_name": meta["file_name"],
        "delimiter": meta["delimiter"],
        "total_rows": meta["total_rows"],
        "total_columns": meta["total_columns"],
        "columns": meta["columns"],
        "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": missing_summary,
        "total_missing_cells": int(missing_series.sum()),
        "duplicate_rows": duplicates_count,
        "target_distribution": target_distribution,
        "categorical_summary": cat_summary,
        "numerical_summary": num_summary,
        "excluded_features_main": EXCLUDED_FEATURES_MAIN,
        "leakage_explanation": (
            "Feature 'duration' (last contact duration) is excluded from the main prediction "
            "model because call duration is unknown prior to initiating a telemarketing call. "
            "Including it causes severe target leakage and creates an unrealistic model."
        ),
    }


def get_feature_categories(df: Optional[pd.DataFrame] = None) -> Dict[str, List[str]]:
    """Extracts valid unique values for each categorical feature for UI dropdowns and validation."""
    if df is None:
        df, _ = load_dataset()

    categories = {}
    for col in CATEGORICAL_FEATURES:
        if col in df.columns:
            # Sorted unique values
            unique_vals = sorted(df[col].dropna().unique().tolist())
            categories[col] = unique_vals
    return categories


def build_preprocessor(scale_numerical: bool = True) -> ColumnTransformer:
    """
    Builds a ColumnTransformer for preprocessing numerical and categorical features.
    Numerical features: StandardScaler (if scale_numerical=True) or passthrough.
    Categorical features: OneHotEncoder with handle_unknown='ignore'.
    """
    num_transformer = StandardScaler() if scale_numerical else "passthrough"
    cat_transformer = OneHotEncoder(handle_unknown="ignore", sparse_output=False)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, NUMERICAL_FEATURES),
            ("cat", cat_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )
    return preprocessor


def prepare_train_test_data(
    df: Optional[pd.DataFrame] = None,
    test_size: float = DEFAULT_TEST_SIZE,
    random_state: int = RANDOM_STATE,
    exclude_duration: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, Dict[str, Any]]:
    """
    Splits dataset into stratified train and test sets, strictly isolating features.
    Applies target encoding: 'no' -> 0, 'yes' -> 1.
    Prevents leakage by excluding 'duration' for the primary experiment.
    """
    if df is None:
        df, _ = load_dataset()

    # Verify target column ('y' or 'subscribe')
    target_col = TARGET_COLUMN
    if target_col not in df.columns:
        if "subscribe" in df.columns:
            target_col = "subscribe"
        else:
            raise ValueError(f"Missing target column: '{TARGET_COLUMN}' or 'subscribe'")

    # Encode target: handle 'no'/'yes' as well as 0/1
    if df[target_col].dtype == object or str(df[target_col].iloc[0]).lower() in ["no", "yes"]:
        y = df[target_col].astype(str).str.strip().str.lower().map({"no": 0, "yes": 1, "0": 0, "1": 1})
    else:
        y = df[target_col].astype(int)

    if y.isnull().any():
        raise ValueError("Target column contains values other than 'yes', 'no', '0', or '1'")

    # Features
    drop_cols = [target_col]
    if "RecordID" in df.columns:
        drop_cols.append("RecordID")
    if exclude_duration and "duration" in df.columns:
        drop_cols.append("duration")


    X = df.drop(columns=drop_cols)

    # Validate that expected features exist
    for f in NUMERICAL_FEATURES + CATEGORICAL_FEATURES:
        if f not in X.columns:
            raise ValueError(f"Required feature '{f}' missing from dataset")

    # Stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
        shuffle=True,
    )

    metadata = {
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "test_size": test_size,
        "random_state": random_state,
        "exclude_duration": exclude_duration,
        "feature_count": int(X_train.shape[1]),
        "feature_names": X_train.columns.tolist(),
        "train_target_distribution": {
            "0 (no)": int((y_train == 0).sum()),
            "1 (yes)": int((y_train == 1).sum()),
            "yes_pct": round(float((y_train == 1).mean() * 100), 2),
        },
        "test_target_distribution": {
            "0 (no)": int((y_test == 0).sum()),
            "1 (yes)": int((y_test == 1).sum()),
            "yes_pct": round(float((y_test == 1).mean() * 100), 2),
        },
    }

    return X_train, X_test, y_train, y_test, metadata
