import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from backend.config import (
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    ALL_INPUT_FEATURES,
)
from backend.services.train_models import (
    MODEL_DEFINITIONS,
    load_model_pipeline,
)

logger = logging.getLogger(__name__)

# Valid categorical domains based on UCI Bank Marketing dataset
CATEGORICAL_VALID_VALUES = {
    "job": [
        "admin.", "blue-collar", "entrepreneur", "housemaid", "management",
        "retired", "self-employed", "services", "student", "technician",
        "unemployed", "unknown",
    ],
    "marital": ["divorced", "married", "single"],
    "education": ["primary", "secondary", "tertiary", "unknown"],
    "default": ["no", "yes"],
    "housing": ["no", "yes"],
    "loan": ["no", "yes"],
    "contact": ["cellular", "telephone", "unknown"],
    "month": [
        "jan", "feb", "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec",
    ],
    "poutcome": ["failure", "other", "success", "unknown"],
}

NUMERICAL_BOUNDS = {
    "age": (18, 120),
    "balance": (-20000, 200000),
    "day": (1, 31),
    "campaign": (1, 100),
    "pdays": (-1, 1000),
    "previous": (0, 300),
}


def validate_customer_input(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Validates a single customer feature dictionary.
    Returns cleaned payload and list of error messages.
    """
    errors = []
    cleaned = {}

    # Check for duration input and warn/strip it
    if "duration" in payload:
        logger.info("Ignoring 'duration' field to avoid feature leakage.")

    # Validate numerical features
    for num_col in NUMERICAL_FEATURES:
        if num_col not in payload or payload[num_col] is None or payload[num_col] == "":
            errors.append(f"Missing required numerical field: '{num_col}'")
            continue
        try:
            val = float(payload[num_col])
            min_val, max_val = NUMERICAL_BOUNDS[num_col]
            if val < min_val or val > max_val:
                errors.append(
                    f"Value for '{num_col}' ({val}) is out of reasonable range [{min_val}, {max_val}]"
                )
            cleaned[num_col] = int(val) if num_col in ["age", "day", "campaign", "pdays", "previous"] else val
        except (ValueError, TypeError):
            errors.append(f"Field '{num_col}' must be a valid number, got: {payload[num_col]}")

    # Validate categorical features
    for cat_col in CATEGORICAL_FEATURES:
        if cat_col not in payload or payload[cat_col] is None or str(payload[cat_col]).strip() == "":
            errors.append(f"Missing required categorical field: '{cat_col}'")
            continue
        val = str(payload[cat_col]).strip().lower()
        valid_options = CATEGORICAL_VALID_VALUES.get(cat_col, [])
        if valid_options and val not in valid_options:
            errors.append(
                f"Invalid value for '{cat_col}': '{val}'. Allowed options: {valid_options}"
            )
        cleaned[cat_col] = val

    return cleaned, errors


def predict_single_customer(
    features: Dict[str, Any],
    model_name: str = "random_forest",
) -> Dict[str, Any]:
    """
    Validates customer features and performs prediction using the requested trained model.
    """
    if model_name not in MODEL_DEFINITIONS:
        raise ValueError(
            f"Invalid model name '{model_name}'. Choose from: {list(MODEL_DEFINITIONS.keys())}"
        )

    cleaned_features, errors = validate_customer_input(features)
    if errors:
        raise ValueError("; ".join(errors))

    # Convert to single-row DataFrame matching the exact schema
    df_single = pd.DataFrame([cleaned_features])

    pipeline = load_model_pipeline(model_name)
    prediction = int(pipeline.predict(df_single)[0])

    probability = None
    if hasattr(pipeline, "predict_proba"):
        try:
            proba = pipeline.predict_proba(df_single)[0]
            probability = float(proba[1])
        except Exception as e:
            logger.warning(f"Could not calculate probability: {e}")

    model_display_name = MODEL_DEFINITIONS[model_name]["display_name"]
    label = "Yes (Likely to Subscribe)" if prediction == 1 else "No (Unlikely to Subscribe)"
    confidence_pct = round((probability if probability is not None else 0.5) * 100, 2)

    # Contextual insight
    insight_parts = []
    if cleaned_features.get("poutcome") == "success":
        insight_parts.append("Previous campaign success strongly correlates with subscription likelihood.")
    if cleaned_features.get("housing") == "yes":
        insight_parts.append("Existing housing loan obligations moderately reduce propensity to subscribe.")
    if cleaned_features.get("balance", 0) > 2000:
        insight_parts.append("Healthy average annual balance (> 2,000 EUR) indicates higher liquidity.")
    if cleaned_features.get("campaign", 1) > 4:
        insight_parts.append("High number of campaign contacts (> 4) typically exhibits diminishing conversion returns.")

    return {
        "status": "success",
        "model_key": model_name,
        "model_name": model_display_name,
        "prediction": prediction,
        "outcome": label,
        "probability": round(probability, 4) if probability is not None else None,
        "probability_percentage": confidence_pct,
        "risk_level": "High Probability" if confidence_pct >= 60 else ("Moderate" if confidence_pct >= 40 else "Low"),
        "key_insights": insight_parts or ["Customer falls within typical campaign baseline demographic profile."],
        "anti_leakage_applied": True,
        "disclaimer": (
            "This prediction is a statistical estimate produced by machine learning models trained "
            "on historical bank telemarketing data. It does not constitute a guaranteed customer commitment."
        ),
    }


def predict_all_models_single_customer(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates customer features and executes predictions across ALL FOUR models simultaneously.
    Returns per-model predictions, probabilities, benchmark accuracies, and ensemble consensus.
    """
    from backend.services.train_models import get_cached_metrics

    cleaned_features, errors = validate_customer_input(features)
    if errors:
        raise ValueError("; ".join(errors))

    metrics_cache = get_cached_metrics() or {}
    models_metrics = metrics_cache.get("models", {})

    results = {}
    positive_votes = 0
    probabilities_list = []

    for model_key in ["random_forest", "decision_tree", "logistic_regression", "knn"]:
        single_res = predict_single_customer(features=cleaned_features, model_name=model_key)

        bench_m = models_metrics.get(model_key, {}).get("metrics", {})
        single_res["benchmark_accuracy"] = bench_m.get("accuracy")
        single_res["benchmark_f1_score"] = bench_m.get("f1_score")
        single_res["benchmark_roc_auc"] = bench_m.get("roc_auc")
        single_res["benchmark_precision"] = bench_m.get("precision")
        single_res["benchmark_recall"] = bench_m.get("recall")

        if single_res["prediction"] == 1:
            positive_votes += 1
        if single_res["probability"] is not None:
            probabilities_list.append(single_res["probability"])

        results[model_key] = single_res

    total_models = len(results)
    avg_prob = float(np.mean(probabilities_list)) if probabilities_list else 0.5
    avg_pct = round(avg_prob * 100, 2)
    majority_pred = 1 if positive_votes > (total_models / 2) else 0
    majority_outcome = "Yes (Likely to Subscribe)" if majority_pred == 1 else "No (Unlikely to Subscribe)"

    agreement_desc = (
        f"{positive_votes}/{total_models} models predict Yes"
        if positive_votes >= 2
        else f"{total_models - positive_votes}/{total_models} models predict No"
    )

    return {
        "status": "success",
        "consensus": {
            "positive_votes": positive_votes,
            "negative_votes": total_models - positive_votes,
            "majority_prediction": majority_pred,
            "majority_outcome": majority_outcome,
            "average_probability": round(avg_prob, 4),
            "average_probability_percentage": avg_pct,
            "agreement_summary": agreement_desc,
            "risk_level": "High Probability" if avg_pct >= 60 else ("Moderate" if avg_pct >= 40 else "Low"),
        },
        "models": results,
        "key_insights": results["random_forest"]["key_insights"],
        "anti_leakage_applied": True,
        "disclaimer": results["random_forest"]["disclaimer"],
    }



def predict_batch_customers(
    df_records: pd.DataFrame,
    model_name: str = "random_forest",
) -> Dict[str, Any]:
    """
    Validates a batch DataFrame and performs batch predictions in matching order.
    """
    if model_name not in MODEL_DEFINITIONS:
        raise ValueError(f"Invalid model name '{model_name}'. Choose from: {list(MODEL_DEFINITIONS.keys())}")

    if df_records.empty:
        raise ValueError("Provided batch dataset is empty.")

    # Remove duration if present
    cols_to_use = [c for c in df_records.columns if c != "duration" and c != "y"]
    df_clean = df_records[cols_to_use].copy()

    # Validate presence of required features
    missing_cols = [f for f in ALL_INPUT_FEATURES if f not in df_clean.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in batch CSV: {missing_cols}")

    # Standardize categoricals
    for col in CATEGORICAL_FEATURES:
        df_clean[col] = df_clean[col].astype(str).str.strip().str.lower()

    # Coerce numericals
    for col in NUMERICAL_FEATURES:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").fillna(0)

    pipeline = load_model_pipeline(model_name)
    predictions = pipeline.predict(df_clean)

    probabilities = None
    if hasattr(pipeline, "predict_proba"):
        try:
            probabilities = pipeline.predict_proba(df_clean)[:, 1]
        except Exception as e:
            logger.warning(f"Batch predict_proba failed: {e}")

    results_list = []
    for idx in range(len(df_clean)):
        pred = int(predictions[idx])
        prob = float(probabilities[idx]) if probabilities is not None else None
        results_list.append(
            {
                "row_index": idx,
                "prediction": pred,
                "outcome": "Yes" if pred == 1 else "No",
                "probability": round(prob, 4) if prob is not None else None,
            }
        )

    pos_count = int((predictions == 1).sum())
    neg_count = int((predictions == 0).sum())
    total_count = len(predictions)

    return {
        "status": "success",
        "model_key": model_name,
        "model_name": MODEL_DEFINITIONS[model_name]["display_name"],
        "total_records": total_count,
        "predicted_positive": pos_count,
        "predicted_negative": neg_count,
        "positive_rate_percentage": round(pos_count / total_count * 100, 2) if total_count > 0 else 0.0,
        "average_subscription_probability": (
            round(float(np.mean(probabilities)), 4) if probabilities is not None else None
        ),
        "results": results_list,
    }
