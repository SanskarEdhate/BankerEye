import json
import logging
import time
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from backend.config import (
    RANDOM_STATE,
    SAVED_MODELS_DIR,
    DEFAULT_TEST_SIZE,
)
from backend.services.preprocessing import (
    build_preprocessor,
    prepare_train_test_data,
    load_dataset,
)

logger = logging.getLogger(__name__)

# Mutex to prevent concurrent training race conditions
TRAINING_LOCK = threading.Lock()
IS_TRAINING = False

MODEL_DEFINITIONS = {
    "logistic_regression": {
        "display_name": "Logistic Regression",
        "description": "Linear baseline model estimating subscription probabilities with optimized L2 regularization.",
        "estimator": lambda: LogisticRegression(
            max_iter=1000,
            C=1.0,
            class_weight=None,
            random_state=RANDOM_STATE,
            solver="lbfgs",
        ),
        "scale_numerical": True,
        "supports_feature_importance": True,
    },
    "decision_tree": {
        "display_name": "Decision Tree Classifier",
        "description": "Hierarchical decision rules calibrated to optimize node purity and classification accuracy.",
        "estimator": lambda: DecisionTreeClassifier(
            max_depth=7,
            min_samples_split=20,
            min_samples_leaf=10,
            class_weight=None,
            random_state=RANDOM_STATE,
        ),
        "scale_numerical": True,
        "supports_feature_importance": True,
    },
    "knn": {
        "display_name": "K-Nearest Neighbours (KNN)",
        "description": "Distance-weighted nearest-neighbor classifier voting in standard scaled feature space.",
        "estimator": lambda: KNeighborsClassifier(
            n_neighbors=15,
            weights="distance",
            metric="minkowski",
            p=2,
            n_jobs=-1,
        ),
        "scale_numerical": True,
        "supports_feature_importance": False,
    },
    "random_forest": {
        "display_name": "Random Forest Classifier",
        "description": "Ensemble of 200 bagging decision trees maximizing generalization and overall accuracy.",
        "estimator": lambda: RandomForestClassifier(
            n_estimators=200,
            max_depth=14,
            min_samples_split=10,
            min_samples_leaf=4,
            class_weight=None,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "scale_numerical": True,
        "supports_feature_importance": True,
    },
}



def get_transformed_feature_names(preprocessor: Any) -> List[str]:
    """Extracts human-readable feature names after ColumnTransformer preprocessing."""
    try:
        feature_names = []
        for name, trans, cols in preprocessor.transformers_:
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


def train_and_evaluate_all_models(
    test_size: float = DEFAULT_TEST_SIZE,
    random_state: int = RANDOM_STATE,
    force_retrain: bool = False,
) -> Dict[str, Any]:
    """
    Trains all four algorithms on the stratified training set, evaluates them on the held-out
    test set, saves models to disk, and persists comprehensive evaluation metrics.
    """
    global IS_TRAINING

    metrics_file = SAVED_MODELS_DIR / "model_metrics.json"
    summary_file = SAVED_MODELS_DIR / "evaluation_summary.json"

    # If already trained and not forced, return cached metrics
    if not force_retrain and metrics_file.exists() and summary_file.exists():
        try:
            with open(metrics_file, "r", encoding="utf-8") as f:
                saved_metrics = json.load(f)
            return saved_metrics
        except Exception as e:
            logger.warning(f"Failed to read existing metrics cache: {e}. Retraining...")

    if not TRAINING_LOCK.acquire(blocking=False):
        raise RuntimeError("Model training is already currently in progress. Please wait.")

    IS_TRAINING = True
    start_total_time = time.time()

    try:
        df, dataset_meta = load_dataset()
        X_train, X_test, y_train, y_test, split_meta = prepare_train_test_data(
            df=df,
            test_size=test_size,
            random_state=random_state,
            exclude_duration=True,
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
                    "Call duration is excluded because it is only known after marketing contact, "
                    "preventing data leakage and unrealistic performance claims."
                ),
            },
            "split_info": split_meta,
            "models": {},
            "feature_importance": {},
        }

        # Train each model
        for model_key, meta in MODEL_DEFINITIONS.items():
            logger.info(f"Training {meta['display_name']}...")
            preprocessor = build_preprocessor(scale_numerical=meta["scale_numerical"])
            estimator = meta["estimator"]()

            pipeline = Pipeline(
                steps=[
                    ("preprocessor", preprocessor),
                    ("classifier", estimator),
                ]
            )

            # Measure training time
            t0 = time.time()
            pipeline.fit(X_train, y_train)
            train_duration = round(time.time() - t0, 3)

            # Measure prediction time on test set
            t1 = time.time()
            y_pred = pipeline.predict(X_test)
            pred_duration = round(time.time() - t1, 4)

            # Probability predictions
            y_proba = None
            if hasattr(pipeline, "predict_proba"):
                try:
                    y_proba = pipeline.predict_proba(X_test)[:, 1]
                except Exception as e:
                    logger.warning(f"predict_proba failed for {model_key}: {e}")

            # Calculate classification metrics
            acc = float(accuracy_score(y_test, y_pred))
            prec = float(precision_score(y_test, y_pred, pos_label=1, zero_division=0))
            rec = float(recall_score(y_test, y_pred, pos_label=1, zero_division=0))
            f1 = float(f1_score(y_test, y_pred, pos_label=1, zero_division=0))

            roc_auc = None
            if y_proba is not None:
                try:
                    roc_auc = float(roc_auc_score(y_test, y_proba))
                except Exception as e:
                    logger.warning(f"roc_auc_score failed for {model_key}: {e}")

            # Confusion Matrix: [[TN, FP], [FN, TP]]
            cm = confusion_matrix(y_test, y_pred).tolist()
            tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]

            # ROC Curve points (downsampled for lightweight JSON storage)
            roc_data = {}
            if y_proba is not None:
                try:
                    fpr, tpr, thresh = roc_curve(y_test, y_proba)
                    step = max(1, len(fpr) // 100)
                    roc_data = {
                        "fpr": [round(float(x), 4) for x in fpr[::step]],
                        "tpr": [round(float(x), 4) for x in tpr[::step]],
                    }
                except Exception as e:
                    logger.warning(f"roc_curve failed for {model_key}: {e}")

            # Precision-Recall curve
            pr_data = {}
            if y_proba is not None:
                try:
                    p_curve, r_curve, _ = precision_recall_curve(y_test, y_proba)
                    step = max(1, len(p_curve) // 100)
                    pr_data = {
                        "precision": [round(float(x), 4) for x in p_curve[::step]],
                        "recall": [round(float(x), 4) for x in r_curve[::step]],
                    }
                except Exception as e:
                    logger.warning(f"precision_recall_curve failed for {model_key}: {e}")

            # Save pipeline model
            model_file = SAVED_MODELS_DIR / f"{model_key}_pipeline.joblib"
            joblib.dump(pipeline, model_file)

            # Feature importance extraction
            feature_imp_list = []
            fitted_clf = pipeline.named_steps["classifier"]
            fitted_prep = pipeline.named_steps["preprocessor"]
            feature_names = get_transformed_feature_names(fitted_prep)

            if meta["supports_feature_importance"]:
                if hasattr(fitted_clf, "feature_importances_") and feature_names:
                    raw_importances = fitted_clf.feature_importances_
                    if len(raw_importances) == len(feature_names):
                        sorted_idx = np.argsort(raw_importances)[::-1]
                        for idx in sorted_idx[:15]:
                            feature_imp_list.append(
                                {
                                    "feature": feature_names[idx],
                                    "importance": round(float(raw_importances[idx]), 4),
                                }
                            )
                elif hasattr(fitted_clf, "coef_") and feature_names:
                    # Logistic Regression coefficients
                    coefs = np.abs(fitted_clf.coef_[0])
                    if len(coefs) == len(feature_names):
                        sorted_idx = np.argsort(coefs)[::-1]
                        for idx in sorted_idx[:15]:
                            feature_imp_list.append(
                                {
                                    "feature": feature_names[idx],
                                    "importance": round(float(coefs[idx]), 4),
                                    "direction": "positive" if fitted_clf.coef_[0][idx] > 0 else "negative",
                                }
                            )

            if feature_imp_list:
                results["feature_importance"][model_key] = feature_imp_list

            results["models"][model_key] = {
                "key": model_key,
                "display_name": meta["display_name"],
                "description": meta["description"],
                "metrics": {
                    "accuracy": round(acc, 4),
                    "precision": round(prec, 4),
                    "recall": round(rec, 4),
                    "f1_score": round(f1, 4),
                    "roc_auc": round(roc_auc, 4) if roc_auc is not None else None,
                },
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
                    "roc": roc_data,
                    "pr": pr_data,
                },
                "interpretation": generate_model_interpretation(
                    model_name=meta["display_name"],
                    acc=acc,
                    prec=prec,
                    rec=rec,
                    f1=f1,
                    roc_auc=roc_auc,
                    fp=fp,
                    fn=fn,
                ),
            }

        # Model Ranking across metrics
        results["rankings"] = compute_rankings(results["models"])
        results["total_training_time_sec"] = round(time.time() - start_total_time, 2)

        # Save to disk
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        # Save summary report for fast dashboard loading
        summary_payload = {
            "status": "ready",
            "trained_at": results["trained_at"],
            "total_models": len(results["models"]),
            "best_f1_model": results["rankings"]["f1_score"][0]["display_name"],
            "best_roc_auc_model": results["rankings"]["roc_auc"][0]["display_name"],
            "rankings": results["rankings"],
            "models_summary": {
                k: {
                    "display_name": v["display_name"],
                    "metrics": v["metrics"],
                    "timing": v["timing"],
                }
                for k, v in results["models"].items()
            },
        }
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_payload, f, indent=2)

        logger.info(f"Training complete in {results['total_training_time_sec']}s.")
        return results

    finally:
        IS_TRAINING = False
        TRAINING_LOCK.release()


def compute_rankings(models_dict: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Ranks models across key metrics (f1_score, roc_auc, recall, accuracy)."""
    metrics_to_rank = ["f1_score", "roc_auc", "recall", "accuracy", "precision"]
    rankings = {}

    for metric in metrics_to_rank:
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
            reverse=True,
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
    roc_auc: Optional[float],
    fp: int,
    fn: int,
) -> str:
    """Generates an objective, non-fabricated interpretation of the model's performance trade-off."""
    auc_str = f"{roc_auc:.2%}" if roc_auc is not None else "N/A"
    return (
        f"{model_name} achieved an Accuracy of {acc:.2%}, F1-score of {f1:.2%}, "
        f"and ROC-AUC of {auc_str}. In this bank marketing scenario, it produced {fp} false positives "
        f"(outreach costs to non-subscribers) and {fn} false negatives (missed potential term deposits). "
        f"With a Recall of {rec:.2%} and Precision of {prec:.2%}, this classifier balances "
        f"campaign conversion reach against operational outbound calling expenses."
    )


def load_model_pipeline(model_key: str) -> Pipeline:
    """Loads a serialized model pipeline from backend/saved_models/."""
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

    pipeline = joblib.load(model_file)
    return pipeline


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
