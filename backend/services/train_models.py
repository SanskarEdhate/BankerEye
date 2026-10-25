import functools
import json
import logging
import threading
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from backend.config import (
    CATEGORICAL_FEATURES,
    DEFAULT_TEST_SIZE,
    EXPECTED_MODEL_FILES,
    NUMERICAL_FEATURES,
    RANDOM_STATE,
    SAVED_MODELS_DIR,
)
from backend.services.preprocessing import (
    build_preprocessor,
    load_dataset,
    prepare_train_test_data,
)

logger = logging.getLogger(__name__)

# Mutex to prevent concurrent training race conditions
TRAINING_LOCK = threading.Lock()

# Background training job state tracking
TRAINING_JOB: Dict[str, Any] = {
    "state": "idle",  # "idle" | "running" | "done" | "failed"
    "progress": 0,
    "current_model": None,
    "message": "No training in progress",
    "job_id": None,
    "started_at": None,
    "completed_at": None,
    "error": None,
}

# Factual model definitions with balanced class weights where supported
MODEL_DEFINITIONS = {
    "logistic_regression": {
        "display_name": "Logistic Regression",
        "description": "Regularized linear logistic regression estimating log-odds of term deposit subscription with balanced class weights.",
        "estimator": lambda: LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            solver="lbfgs",
        ),
        "param_grid": {
            "C": [0.1, 1.0, 10.0],
        },
        "scale_numerical": True,
        "supports_feature_importance": True,
        "class_weight_note": "class_weight='balanced' inversely proportional to class frequencies.",
    },
    "decision_tree": {
        "display_name": "Decision Tree Classifier",
        "description": "Non-parametric CART decision tree partitioning feature space with balanced class weights.",
        "estimator": lambda: DecisionTreeClassifier(
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "param_grid": {
            "max_depth": [6, 10],
            "min_samples_split": [10, 20],
        },
        "scale_numerical": False,
        "supports_feature_importance": True,
        "class_weight_note": "class_weight='balanced' weighting inversely proportional to class frequencies.",
    },
    "knn": {
        "display_name": "K-Nearest Neighbours (KNN)",
        "description": "Instance-based non-parametric classifier voting in standardized feature space (KNN does not support a class_weight parameter).",
        "estimator": lambda: KNeighborsClassifier(
            weights="distance",
            n_jobs=1,
        ),
        "param_grid": {
            "n_neighbors": [5, 11],
        },
        "scale_numerical": True,
        "supports_feature_importance": False,
        "class_weight_note": "No class_weight parameter is supported by KNeighborsClassifier in scikit-learn.",
    },
    "random_forest": {
        "display_name": "Random Forest Classifier",
        "description": "Ensemble of bagging decision trees with balanced bootstrap subsamples and randomized feature subsets.",
        "estimator": lambda: RandomForestClassifier(
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=1,
        ),
        "param_grid": {
            "n_estimators": [50, 100],
            "max_depth": [8, 12],
        },
        "scale_numerical": False,
        "supports_feature_importance": True,
        "class_weight_note": "class_weight='balanced' adjusts weights inversely proportional to class frequencies.",
    },
}


def get_training_job_status() -> Dict[str, Any]:
    """Returns the current state and progress of the background training job."""
    return dict(TRAINING_JOB)


def start_background_training_job(
    test_size: float = DEFAULT_TEST_SIZE,
    random_state: int = RANDOM_STATE,
    force_retrain: bool = True,
) -> str:
    """Launches model training as a non-blocking background thread."""
    if TRAINING_JOB["state"] == "running":
        raise RuntimeError("Model training is already currently running.")

    job_id = str(uuid.uuid4())
    TRAINING_JOB["state"] = "running"
    TRAINING_JOB["progress"] = 5
    TRAINING_JOB["current_model"] = None
    TRAINING_JOB["message"] = "Initializing background training..."
    TRAINING_JOB["job_id"] = job_id
    TRAINING_JOB["started_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    TRAINING_JOB["completed_at"] = None
    TRAINING_JOB["error"] = None

    def _worker():
        try:
            train_and_evaluate_all_models(
                test_size=test_size,
                random_state=random_state,
                force_retrain=force_retrain,
                is_background=True,
            )
            TRAINING_JOB["state"] = "done"
            TRAINING_JOB["progress"] = 100
            TRAINING_JOB["message"] = "Training and evaluation successfully completed."
            TRAINING_JOB["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logger.exception("Background training job failed")
            TRAINING_JOB["state"] = "failed"
            TRAINING_JOB["error"] = str(e)
            TRAINING_JOB["message"] = f"Training failed: {e}"

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    return job_id


@functools.lru_cache(maxsize=16)
def _load_model_cached(model_key: str, file_mtime: float) -> Pipeline:
    """Loads a serialized pipeline cached by model key and file modification timestamp."""
    model_file = SAVED_MODELS_DIR / f"{model_key}_pipeline.joblib"
    return joblib.load(model_file)


def load_model_pipeline(model_key: str) -> Pipeline:
    """Loads a serialized model pipeline from backend/saved_models/ using in-memory mtime caching."""
    if model_key not in MODEL_DEFINITIONS:
        raise ValueError(
            f"Unknown model key '{model_key}'. Valid choices: {list(MODEL_DEFINITIONS.keys())}"
        )

    model_file = SAVED_MODELS_DIR / f"{model_key}_pipeline.joblib"
    if not model_file.exists():
        raise FileNotFoundError(
            f"Model pipeline for '{model_key}' has not been trained yet at {model_file}. "
            "Please trigger training via POST /api/models/train."
        )

    mtime = model_file.stat().st_mtime
    return _load_model_cached(model_key, mtime)


def get_cached_metrics() -> Optional[Dict[str, Any]]:
    """Retrieves saved metrics if available, without retraining."""
    metrics_file = SAVED_MODELS_DIR / "model_metrics.json"
    if metrics_file.exists():
        try:
            with open(metrics_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read model_metrics.json: {e}")
    return None


def get_transformed_feature_names(preprocessor: Any) -> List[str]:
    """Extracts transformed column names from ColumnTransformer or unified Pipeline."""
    try:
        col_trans = preprocessor
        if hasattr(preprocessor, "named_steps") and "col_transformer" in preprocessor.named_steps:
            col_trans = preprocessor.named_steps["col_transformer"]

        feature_names = []
        for name, trans, cols in col_trans.transformers_:
            if name == "num":
                feature_names.extend(cols)
            elif name == "cat":
                if hasattr(trans, "get_feature_names_out"):
                    cat_names = trans.get_feature_names_out(cols).tolist()
                    feature_names.extend(cat_names)
                else:
                    feature_names.extend(cols)
        return feature_names
    except Exception as e:
        logger.warning(f"Could not retrieve transformed feature names: {e}")
        return []


def downsample_points(x_arr: np.ndarray, y_arr: np.ndarray, max_pts: int = 101) -> Tuple[List[float], List[float]]:
    """
    Downsamples curve points while strictly guaranteeing first (0) and last (len-1) points are kept.
    Uses np.linspace indices and np.unique to preserve end-point boundary integrity.
    """
    n = len(x_arr)
    if n <= max_pts:
        return [round(float(v), 4) for v in x_arr], [round(float(v), 4) for v in y_arr]

    idx = np.round(np.linspace(0, n - 1, max_pts)).astype(int)
    idx = np.unique(idx)
    return [round(float(x_arr[i]), 4) for i in idx], [round(float(y_arr[i]), 4) for i in idx]


def compute_bootstrap_ci(
    y_true: pd.Series,
    y_pred: np.ndarray,
    y_proba: Optional[np.ndarray],
    n_bootstraps: int = 500,
    random_state: int = RANDOM_STATE,
) -> Dict[str, Any]:
    """Computes empirical 95% bootstrap confidence intervals for F1 and ROC-AUC on test data."""
    rng = np.random.RandomState(random_state)
    n = len(y_true)
    y_true_arr = np.array(y_true)
    y_pred_arr = np.array(y_pred)
    y_proba_arr = np.array(y_proba) if y_proba is not None else None

    f1_bootstraps = []
    roc_bootstraps = []

    for _ in range(n_bootstraps):
        idx = rng.randint(0, n, n)
        y_t = y_true_arr[idx]
        if len(np.unique(y_t)) < 2:
            continue
        y_p = y_pred_arr[idx]
        f1_bootstraps.append(f1_score(y_t, y_p, pos_label=1, zero_division=0))
        if y_proba_arr is not None:
            roc_bootstraps.append(roc_auc_score(y_t, y_proba_arr[idx]))

    f1_ci = [
        round(float(np.percentile(f1_bootstraps, 2.5)), 4),
        round(float(np.percentile(f1_bootstraps, 97.5)), 4),
    ] if f1_bootstraps else [0.0, 0.0]

    roc_ci = [
        round(float(np.percentile(roc_bootstraps, 2.5)), 4),
        round(float(np.percentile(roc_bootstraps, 97.5)), 4),
    ] if roc_bootstraps else None

    return {
        "f1_ci_95": f1_ci,
        "roc_auc_ci_95": roc_ci,
    }


def compute_grouped_permutation_importance(
    classifier: Any,
    X_test_proc: np.ndarray,
    y_test: pd.Series,
    feature_names: List[str],
    random_state: int = RANDOM_STATE,
    n_repeats: int = 5,
) -> List[Dict[str, Any]]:
    """
    Computes permutation importance on the processed test feature matrix and groups
    one-hot encoded columns back to their original feature name by summing importances.
    """
    try:
        perm = permutation_importance(
            classifier,
            X_test_proc,
            y_test,
            n_repeats=n_repeats,
            random_state=random_state,
            scoring="f1",
            n_jobs=1,
        )
        grouped: Dict[str, float] = {}

        for feat_name, imp in zip(feature_names, perm.importances_mean):
            # Identify original feature root
            orig_feat = feat_name
            for cat_col in CATEGORICAL_FEATURES:
                if feat_name.startswith(f"{cat_col}_") or feat_name == cat_col:
                    orig_feat = cat_col
                    break
            if feat_name == "never_contacted":
                orig_feat = "pdays"
            elif orig_feat not in CATEGORICAL_FEATURES and orig_feat not in NUMERICAL_FEATURES:
                for num_col in NUMERICAL_FEATURES:
                    if feat_name.startswith(num_col):
                        orig_feat = num_col
                        break

            grouped[orig_feat] = grouped.get(orig_feat, 0.0) + max(0.0, float(imp))

        total_imp = sum(grouped.values())
        result = []
        for feat, val in sorted(grouped.items(), key=lambda x: x[1], reverse=True):
            normalized = round(val / total_imp, 4) if total_imp > 0 else 0.0
            result.append({
                "feature": feat,
                "importance": round(val, 4),
                "relative_importance": normalized,
            })
        return result
    except Exception as e:
        logger.warning(f"Failed to compute grouped permutation importance: {e}")
        return []


def train_and_evaluate_all_models(
    test_size: float = DEFAULT_TEST_SIZE,
    random_state: int = RANDOM_STATE,
    force_retrain: bool = False,
    is_background: bool = False,
) -> Dict[str, Any]:
    """
    Trains all four models using 5-fold CV hyperparameter tuning on TRAIN set only,
    applies isotonic calibration, performs validation-split threshold tuning,
    evaluates on test set with 95% bootstrap CIs, downsamples curves safely,
    and runs a chronological temporal sensitivity check.
    """
    metrics_file = SAVED_MODELS_DIR / "model_metrics.json"
    summary_file = SAVED_MODELS_DIR / "evaluation_summary.json"

    # Strict cache validation: all 4 joblibs must exist AND cached split configuration must match
    all_joblib_exist = all((SAVED_MODELS_DIR / fname).exists() for fname in EXPECTED_MODEL_FILES)
    if not force_retrain and all_joblib_exist and metrics_file.exists() and summary_file.exists():
        try:
            with open(metrics_file, "r", encoding="utf-8") as f:
                saved_metrics = json.load(f)
            cached_split = saved_metrics.get("split_info", {})
            if (
                cached_split.get("test_size") == test_size
                and cached_split.get("random_state") == random_state
            ):
                return saved_metrics
        except Exception as e:
            logger.warning(f"Cache validation check failed: {e}. Retraining...")

    if not TRAINING_LOCK.acquire(blocking=False):
        raise RuntimeError("Model training is already currently in progress. Please wait.")

    start_total_time = time.time()
    try:
        if is_background:
            TRAINING_JOB["progress"] = 10
            TRAINING_JOB["message"] = "Loading and partitioning dataset..."

        df, dataset_meta = load_dataset()
        X_train, X_test, y_train, y_test, split_meta = prepare_train_test_data(
            df=df,
            test_size=test_size,
            random_state=random_state,
            exclude_duration=True,
        )

        # Carve an internal validation split from TRAIN for threshold tuning
        X_tune_tr, X_tune_val, y_tune_tr, y_tune_val = train_test_split(
            X_train,
            y_train,
            test_size=0.20,
            random_state=random_state,
            stratify=y_train,
        )

        results = {
            "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dataset_info": {
                "file_name": dataset_meta["file_name"],
                "total_rows": dataset_meta["total_rows"],
                "train_rows": split_meta["train_rows"],
                "test_rows": split_meta["test_rows"],
                "features_used": split_meta["feature_count"],
                "excluded_features": ["duration"],
                "anti_leakage_note": (
                    "Call duration is strictly excluded because it is only known after marketing contact, "
                    "preventing data leakage and unrealistic performance claims."
                ),
            },
            "split_info": split_meta,
            "models": {},
            "feature_importance": {},
            "temporal_check": {},
        }

        progress_step = 60 / len(MODEL_DEFINITIONS)
        current_progress = 15

        for model_idx, (model_key, meta) in enumerate(MODEL_DEFINITIONS.items()):
            logger.info(f"Training and calibrating {meta['display_name']}...")
            if is_background:
                TRAINING_JOB["current_model"] = meta["display_name"]
                TRAINING_JOB["progress"] = int(current_progress)
                TRAINING_JOB["message"] = f"Tuning and calibrating {meta['display_name']}..."

            t0 = time.time()
            preprocessor = build_preprocessor(scale_numerical=meta["scale_numerical"])

            # 1. Fit preprocessor on train data and transform
            X_train_proc = preprocessor.fit_transform(X_train)
            X_test_proc = preprocessor.transform(X_test)
            feature_names = get_transformed_feature_names(preprocessor)

            # 2. 5-Fold Stratified CV GridSearch on TRAIN set only, scored on F1
            base_estimator = meta["estimator"]()
            cv_splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
            grid_search = GridSearchCV(
                estimator=base_estimator,
                param_grid=meta["param_grid"],
                cv=cv_splitter,
                scoring="f1",
                n_jobs=1,
            )
            grid_search.fit(X_train_proc, y_train)

            best_estimator = grid_search.best_estimator_
            best_params = grid_search.best_params_
            cv_mean_f1 = float(grid_search.best_score_)
            cv_std_f1 = float(grid_search.cv_results_["std_test_score"][grid_search.best_index_])

            # 3. Threshold tuning: evaluate on validation split carved from train to maximize F1
            X_tune_tr_proc = preprocessor.transform(X_tune_tr)
            X_tune_val_proc = preprocessor.transform(X_tune_val)
            cal_tune = CalibratedClassifierCV(estimator=best_estimator, method="isotonic", cv=3)
            cal_tune.fit(X_tune_tr_proc, y_tune_tr)
            tune_val_proba = cal_tune.predict_proba(X_tune_val_proc)[:, 1]

            candidate_thresholds = np.linspace(0.10, 0.90, 81)
            best_thresh = 0.50
            best_val_f1 = -1.0
            for thresh in candidate_thresholds:
                pred_binary = (tune_val_proba >= thresh).astype(int)
                score = f1_score(y_tune_val, pred_binary, pos_label=1, zero_division=0)
                if score > best_val_f1:
                    best_val_f1 = score
                    best_thresh = float(round(thresh, 2))

            # 4. Final probability calibration: wrap best estimator with CalibratedClassifierCV on full train
            final_calibrated_clf = CalibratedClassifierCV(
                estimator=best_estimator,
                method="isotonic",
                cv=3,
            )
            final_calibrated_clf.fit(X_train_proc, y_train)

            # Construct final production pipeline
            pipeline = Pipeline(
                steps=[
                    ("preprocessor", preprocessor),
                    ("classifier", final_calibrated_clf),
                ]
            )
            train_duration = round(time.time() - t0, 3)

            # 5. Evaluate on held-out test set
            t1 = time.time()
            y_test_proba = pipeline.predict_proba(X_test)[:, 1]
            pred_duration = round(time.time() - t1, 4)

            # Use optimal decision threshold for binary prediction
            y_test_pred = (y_test_proba >= best_thresh).astype(int)

            acc = float(accuracy_score(y_test, y_test_pred))
            prec = float(precision_score(y_test, y_test_pred, pos_label=1, zero_division=0))
            rec = float(recall_score(y_test, y_test_pred, pos_label=1, zero_division=0))
            f1 = float(f1_score(y_test, y_test_pred, pos_label=1, zero_division=0))
            roc_auc = float(roc_auc_score(y_test, y_test_proba))
            brier = float(brier_score_loss(y_test, y_test_proba))

            cm = confusion_matrix(y_test, y_test_pred).tolist()
            tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]

            # 6. Downsample ROC and PR curves with endpoint preservation
            fpr_raw, tpr_raw, _ = roc_curve(y_test, y_test_proba)
            fpr_pts, tpr_pts = downsample_points(fpr_raw, tpr_raw, max_pts=101)

            prec_raw, rec_raw, _ = precision_recall_curve(y_test, y_test_proba)
            rec_pts, prec_pts = downsample_points(rec_raw, prec_raw, max_pts=101)

            # 7. Bootstrap 95% Confidence Intervals (n=500)
            ci_data = compute_bootstrap_ci(y_test, y_test_pred, y_test_proba, n_bootstraps=500, random_state=random_state)

            # 8. Save serialized pipeline to disk
            model_file = SAVED_MODELS_DIR / f"{model_key}_pipeline.joblib"
            joblib.dump(pipeline, model_file)

            # 9. Grouped permutation feature importance for tree models
            if meta["supports_feature_importance"]:
                grouped_imp = compute_grouped_permutation_importance(
                    classifier=final_calibrated_clf,
                    X_test_proc=X_test_proc,
                    y_test=y_test,
                    feature_names=feature_names,
                    random_state=random_state,
                    n_repeats=5,
                )
                if grouped_imp:
                    results["feature_importance"][model_key] = grouped_imp

            results["models"][model_key] = {
                "key": model_key,
                "display_name": meta["display_name"],
                "description": meta["description"],
                "class_weight_note": meta["class_weight_note"],
                "hyperparameters": {
                    "best_params": best_params,
                    "cv_mean_f1": round(cv_mean_f1, 4),
                    "cv_std_f1": round(cv_std_f1, 4),
                    "tuning_cv_folds": 5,
                    "scoring": "f1",
                },
                "calibration": {
                    "method": "isotonic",
                    "cv": 3,
                    "brier_score": round(brier, 4),
                },
                "optimal_threshold": best_thresh,
                "metrics": {
                    "accuracy": round(acc, 4),
                    "precision": round(prec, 4),
                    "recall": round(rec, 4),
                    "f1_score": round(f1, 4),
                    "roc_auc": round(roc_auc, 4),
                    "brier_score": round(brier, 4),
                },
                "bootstrap_ci_95": ci_data,
                "confusion_matrix": {
                    "raw": cm,
                    "true_negatives": int(tn),
                    "false_positives": int(fp),
                    "false_negatives": int(fn),
                    "true_positives": int(tp),
                },
                "timing": {
                    "training_time_sec": train_duration,
                    "prediction_time_sec": pred_duration,
                },
                "curves": {
                    "roc": {"fpr": fpr_pts, "tpr": tpr_pts},
                    "pr": {"recall": rec_pts, "precision": prec_pts},
                },
                "interpretation": generate_model_interpretation(
                    model_name=meta["display_name"],
                    acc=acc,
                    prec=prec,
                    rec=rec,
                    f1=f1,
                    roc_auc=roc_auc,
                    brier=brier,
                    fp=fp,
                    fn=fn,
                ),
            }
            current_progress += progress_step

        # 10. Time-Aware Sensitivity Check (Last 20% of rows held out in chronological file order)
        if is_background:
            TRAINING_JOB["progress"] = 85
            TRAINING_JOB["message"] = "Running time-aware temporal sensitivity check..."

        temporal_results = run_temporal_sensitivity_check(df, results["models"])
        results["temporal_check"] = temporal_results

        # 11. Statistical CI Overlap Analysis and Ranking
        rankings = compute_rankings(results["models"])
        results["rankings"] = rankings
        ci_verdict, is_distinguishable = evaluate_ci_distinguishability(results["models"])
        results["statistical_verdict"] = ci_verdict
        results["is_top_model_distinguishable"] = is_distinguishable

        results["total_training_time_sec"] = round(time.time() - start_total_time, 2)

        # Save metrics to disk
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        # Save lightweight evaluation summary
        summary_payload = {
            "status": "ready",
            "trained_at": results["trained_at"],
            "total_models": len(results["models"]),
            "statistical_verdict": ci_verdict,
            "is_top_model_distinguishable": is_distinguishable,
            "rankings": rankings,
            "models_summary": {
                k: {
                    "display_name": v["display_name"],
                    "metrics": v["metrics"],
                    "bootstrap_ci_95": v["bootstrap_ci_95"],
                    "calibration": v["calibration"],
                    "optimal_threshold": v["optimal_threshold"],
                    "timing": v["timing"],
                }
                for k, v in results["models"].items()
            },
            "temporal_check": temporal_results,
        }
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_payload, f, indent=2)

        # Clear pipeline memory cache after retraining
        _load_model_cached.cache_clear()
        logger.info(f"Model training and calibration completed in {results['total_training_time_sec']}s.")
        return results

    finally:
        TRAINING_LOCK.release()


def run_temporal_sensitivity_check(df: pd.DataFrame, trained_models: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates sensitivity to time-series distribution shift by holding out the chronological
    last 20% of campaign records in file order without shuffling.
    """
    try:
        from backend.config import TARGET_COLUMN
        target_col = TARGET_COLUMN if TARGET_COLUMN in df.columns else "subscribe"
        y = df[target_col].astype(str).str.strip().str.lower().map({"no": 0, "yes": 1, "0": 0, "1": 1})
        drop_cols = [target_col]
        if "duration" in df.columns:
            drop_cols.append("duration")
        if "RecordID" in df.columns:
            drop_cols.append("RecordID")
        X = df.drop(columns=drop_cols)

        split_idx = int(len(X) * 0.80)
        X_tr = X.iloc[:split_idx]
        X_te = X.iloc[split_idx:]
        y_tr = y.iloc[:split_idx]
        y_te = y.iloc[split_idx:]

        temporal_models = {}
        for model_key, meta in MODEL_DEFINITIONS.items():
            preprocessor = build_preprocessor(scale_numerical=meta["scale_numerical"])
            X_tr_proc = preprocessor.fit_transform(X_tr)
            X_te_proc = preprocessor.transform(X_te)

            best_params = trained_models[model_key]["hyperparameters"]["best_params"]
            base_estimator = meta["estimator"]().set_params(**best_params)

            calibrated = CalibratedClassifierCV(estimator=base_estimator, method="isotonic", cv=3)
            calibrated.fit(X_tr_proc, y_tr)

            proba = calibrated.predict_proba(X_te_proc)[:, 1]
            optimal_thresh = trained_models[model_key]["optimal_threshold"]
            pred = (proba >= optimal_thresh).astype(int)

            temporal_models[model_key] = {
                "display_name": meta["display_name"],
                "accuracy": round(float(accuracy_score(y_te, pred)), 4),
                "precision": round(float(precision_score(y_te, pred, pos_label=1, zero_division=0)), 4),
                "recall": round(float(recall_score(y_te, pred, pos_label=1, zero_division=0)), 4),
                "f1_score": round(float(f1_score(y_te, pred, pos_label=1, zero_division=0)), 4),
                "roc_auc": round(float(roc_auc_score(y_te, proba)), 4),
                "brier_score": round(float(brier_score_loss(y_te, proba)), 4),
            }

        return {
            "is_sensitivity_check": True,
            "description": "Chronological holdout of last 20% records in file order without shuffling.",
            "train_rows": len(X_tr),
            "test_rows": len(X_te),
            "models": temporal_models,
        }
    except Exception as e:
        logger.warning(f"Failed to complete temporal sensitivity check: {e}")
        return {"is_sensitivity_check": True, "error": str(e), "models": {}}


def evaluate_ci_distinguishability(models_dict: Dict[str, Any]) -> Tuple[str, bool]:
    """
    Compares 95% bootstrap confidence intervals for top F1 models.
    If intervals overlap, returns an explicit non-distinguishable statement.
    """
    sorted_models = sorted(
        models_dict.items(),
        key=lambda item: item[1]["metrics"]["f1_score"],
        reverse=True,
    )
    if len(sorted_models) < 2:
        return "Single model trained.", True

    m1_key, m1 = sorted_models[0]
    m2_key, m2 = sorted_models[1]

    ci1 = m1["bootstrap_ci_95"]["f1_ci_95"]
    ci2 = m2["bootstrap_ci_95"]["f1_ci_95"]

    # Check for interval overlap: max(L1, L2) <= min(U1, U2)
    overlap = max(ci1[0], ci2[0]) <= min(ci1[1], ci2[1])
    if overlap:
        msg = (
            f"The 95% confidence intervals for {m1['display_name']} [{ci1[0]:.4f}, {ci1[1]:.4f}] and "
            f"{m2['display_name']} [{ci2[0]:.4f}, {ci2[1]:.4f}] overlap. "
            "Their performances are not statistically distinguishable on this test set."
        )
        return msg, False
    else:
        msg = (
            f"{m1['display_name']} [{ci1[0]:.4f}, {ci1[1]:.4f}] demonstrates statistically "
            f"distinguishable superior performance over {m2['display_name']} [{ci2[0]:.4f}, {ci2[1]:.4f}]."
        )
        return msg, True


def compute_rankings(models_dict: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Ranks models across key metrics (f1_score, roc_auc, recall, accuracy, brier_score)."""
    metrics_to_rank = ["f1_score", "roc_auc", "recall", "accuracy", "precision", "brier_score"]
    rankings = {}

    for metric in metrics_to_rank:
        # For Brier score, lower is better; for others, higher is better
        reverse_order = metric != "brier_score"
        ranked = sorted(
            [
                {
                    "key": k,
                    "display_name": m["display_name"],
                    "value": m["metrics"].get(metric) or 0.0,
                }
                for k, m in models_dict.items()
            ],
            key=lambda x: x["value"],
            reverse=reverse_order,
        )
        for rank, entry in enumerate(ranked, start=1):
            entry["rank"] = rank
        rankings[metric] = ranked

    return rankings


def generate_model_interpretation(
    model_name: str,
    acc: float,
    prec: float,
    rec: float,
    f1: float,
    roc_auc: float,
    brier: float,
    fp: int,
    fn: int,
) -> str:
    """Generates an objective, non-fabricated interpretation of the model's performance trade-off."""
    return (
        f"{model_name} achieved an Accuracy of {acc:.2%}, F1-score of {f1:.2%}, "
        f"ROC-AUC of {roc_auc:.2%}, and Brier score of {brier:.4f}. "
        f"Under optimal thresholding on the held-out test partition, it produced {fp} false positives "
        f"(unconverted outbound calls) and {fn} false negatives (missed conversion prospects). "
        f"With a Recall of {rec:.2%} and Precision of {prec:.2%}, this calibrated pipeline balances "
        f"term deposit conversion capture against outbound campaign resource expenditure."
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print("Starting BankerEye model training and evaluation pipeline...")
    results = train_and_evaluate_all_models(force_retrain=True)
    print("Model training complete! Evaluation results:")
    for k, v in results["models"].items():
        m = v["metrics"]
        print(f"  - {v['display_name']}: Acc={m['accuracy']:.2%}, F1={m['f1_score']:.2%}, ROC-AUC={m['roc_auc']:.2%}, Brier={m['brier_score']:.4f}")
    print(f"Statistical verdict: {results.get('statistical_verdict')}")
