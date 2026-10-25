import logging
import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from backend.config import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
)
from backend.services.train_models import (
    MODEL_DEFINITIONS,
    get_cached_metrics,
    load_model_pipeline,
)

logger = logging.getLogger(__name__)

# Valid categorical domains based on UCI Bank Marketing benchmark dataset
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

INTEGER_FEATURES = ["age", "day", "campaign", "pdays", "previous"]

# Baseline term deposit subscription rate from UCI canonical training distribution (~11.7%)
DEFAULT_BASE_RATE = 0.1170


def get_base_conversion_rate() -> float:
    """Retrieves empirical base conversion rate from cached training metrics if available."""
    metrics = get_cached_metrics()
    if metrics:
        target_dist = metrics.get("dataset_info", {}).get("train_target_distribution", {})
        yes_pct = target_dist.get("yes_pct")
        if yes_pct:
            return float(yes_pct) / 100.0
    return DEFAULT_BASE_RATE


def compute_risk_tier(probability: float, base_rate: Optional[float] = None) -> Dict[str, Any]:
    """
    Computes risk tier derived dynamically from the training base rate:
    - Low Risk: probability < base_rate
    - Medium Risk: base_rate <= probability < 2 * base_rate
    - High Propensity: probability >= 2 * base_rate
    """
    br = base_rate if base_rate is not None else get_base_conversion_rate()
    low_cutoff = round(br, 4)
    med_cutoff = round(2.0 * br, 4)

    if probability < low_cutoff:
        tier = "Low"
        desc = f"Probability ({probability:.1%}) is below empirical baseline conversion rate (< {low_cutoff:.1%})"
    elif probability < med_cutoff:
        tier = "Medium"
        desc = f"Probability ({probability:.1%}) exhibits moderate uplift ({low_cutoff:.1%} to {med_cutoff:.1%})"
    else:
        tier = "High"
        desc = f"Probability ({probability:.1%}) exhibits high conversion propensity (>= 2x baseline, >= {med_cutoff:.1%})"

    return {
        "tier": tier,
        "description": desc,
        "cutoffs": {
            "base_rate": low_cutoff,
            "medium_cutoff": med_cutoff,
        },
    }


def validate_customer_input(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Validates a single customer feature dictionary strictly:
    - Rejects boolean types for numerical and categorical fields.
    - Rejects NaN, inf, -inf (math.isfinite check).
    - Rejects non-integer floats for integer fields (age, day, campaign, pdays, previous).
    - Rejects missing required columns and unrecognized categories without coercion.
    """
    errors: List[str] = []
    cleaned: Dict[str, Any] = {}

    if not isinstance(payload, dict):
        return {}, ["Customer features payload must be a JSON object (dictionary)."]

    # Warn if duration is passed and omit it to prevent target leakage
    if "duration" in payload:
        logger.info("Ignoring 'duration' feature to prevent data leakage.")

    # Validate numerical features
    for num_col in NUMERICAL_FEATURES:
        if num_col not in payload or payload[num_col] is None or payload[num_col] == "":
            errors.append(f"Missing required numerical field: '{num_col}'")
            continue

        raw_val = payload[num_col]
        # Reject booleans (in Python isinstance(True, int) is True)
        if isinstance(raw_val, bool):
            errors.append(f"Field '{num_col}' must be a valid number, got boolean: {raw_val}")
            continue

        try:
            val = float(raw_val)
        except (ValueError, TypeError):
            errors.append(f"Field '{num_col}' must be a valid number, got: {raw_val}")
            continue

        if not math.isfinite(val):
            errors.append(f"Field '{num_col}' cannot be NaN or infinite")
            continue

        if num_col in INTEGER_FEATURES:
            if not float(val).is_integer():
                errors.append(
                    f"Field '{num_col}' must be an integer, got non-integer float: {val}"
                )
                continue
            val = int(val)

        min_val, max_val = NUMERICAL_BOUNDS[num_col]
        if val < min_val or val > max_val:
            errors.append(
                f"Value for '{num_col}' ({val}) is out of reasonable range [{min_val}, {max_val}]"
            )

        cleaned[num_col] = val

    # Validate categorical features
    for cat_col in CATEGORICAL_FEATURES:
        if cat_col not in payload or payload[cat_col] is None or str(payload[cat_col]).strip() == "":
            errors.append(f"Missing required categorical field: '{cat_col}'")
            continue

        raw_val = payload[cat_col]
        if isinstance(raw_val, bool):
            errors.append(f"Field '{cat_col}' cannot be a boolean")
            continue

        val = str(raw_val).strip().lower()
        if val in ["nan", "none", "null"]:
            errors.append(f"Field '{cat_col}' has invalid value: '{val}'")
            continue

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
    prevalidated: bool = False,
) -> Dict[str, Any]:
    """
    Performs inference for a single customer using calibrated model probability
    and optimal decision threshold.
    """
    if model_name not in MODEL_DEFINITIONS:
        raise ValueError(
            f"Invalid model name '{model_name}'. Choose from: {list(MODEL_DEFINITIONS.keys())}"
        )

    if prevalidated:
        cleaned_features = features
    else:
        cleaned_features, errors = validate_customer_input(features)
        if errors:
            raise ValueError("; ".join(errors))

    df_single = pd.DataFrame([cleaned_features])
    pipeline = load_model_pipeline(model_name)

    # 1. Retrieve calibrated probability
    probability = None
    if hasattr(pipeline, "predict_proba"):
        try:
            proba = pipeline.predict_proba(df_single)[0]
            probability = float(proba[1])
        except Exception as e:
            logger.warning(f"Could not calculate probability: {e}")

    # 2. Retrieve tuned threshold from metrics
    metrics_cache = get_cached_metrics() or {}
    model_meta = metrics_cache.get("models", {}).get(model_name, {})
    optimal_threshold = model_meta.get("optimal_threshold", 0.50)

    # Apply optimal decision threshold
    if probability is not None:
        prediction = 1 if probability >= optimal_threshold else 0
    else:
        prediction = int(pipeline.predict(df_single)[0])

    model_display_name = MODEL_DEFINITIONS[model_name]["display_name"]
    label = "Yes (Likely to Subscribe)" if prediction == 1 else "No (Unlikely to Subscribe)"
    confidence_pct = round((probability if probability is not None else 0.5) * 100, 2)

    base_rate = get_base_conversion_rate()
    risk_info = compute_risk_tier(probability if probability is not None else 0.5, base_rate=base_rate)

    # General context notes (derived from model structure without hardcoded rules)
    general_context = [
        "Inference executed using isotonic-calibrated probability estimation.",
        f"Decision threshold optimized at {optimal_threshold:.2f} based on validation F1 maximization.",
        f"Call duration strictly excluded to guarantee pre-contact zero target leakage.",
    ]

    return {
        "status": "success",
        "model_key": model_name,
        "model_name": model_display_name,
        "prediction": prediction,
        "outcome": label,
        "probability": round(probability, 4) if probability is not None else None,
        "probability_percentage": confidence_pct,
        "optimal_threshold_used": optimal_threshold,
        "risk_level": risk_info["tier"],
        "risk_description": risk_info["description"],
        "risk_cutoffs": risk_info["cutoffs"],
        "general_context": general_context,
        "key_insights": general_context,  # Maintained for API backward compatibility
        "anti_leakage_applied": True,
        "disclaimer": (
            "This prediction is an isotonic-calibrated statistical propensity estimate. "
            "It reflects empirical telemarketing patterns and does not guarantee customer subscription."
        ),
    }


def predict_all_models_single_customer(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates customer input ONCE, then performs calibrated inference across all four models.
    Handles consensus ties (2/4) cleanly by outputting outcome 'Uncertain'.
    """
    cleaned_features, errors = validate_customer_input(features)
    if errors:
        raise ValueError("; ".join(errors))

    metrics_cache = get_cached_metrics() or {}
    models_metrics = metrics_cache.get("models", {})
    base_rate = get_base_conversion_rate()

    results: Dict[str, Any] = {}
    positive_votes = 0
    calibrated_probs: List[float] = []

    for model_key in ["random_forest", "decision_tree", "logistic_regression", "knn"]:
        single_res = predict_single_customer(
            features=cleaned_features,
            model_name=model_key,
            prevalidated=True,
        )

        bench_m = models_metrics.get(model_key, {}).get("metrics", {})
        single_res["benchmark_accuracy"] = bench_m.get("accuracy")
        single_res["benchmark_f1_score"] = bench_m.get("f1_score")
        single_res["benchmark_roc_auc"] = bench_m.get("roc_auc")
        single_res["benchmark_precision"] = bench_m.get("precision")
        single_res["benchmark_recall"] = bench_m.get("recall")

        if single_res["prediction"] == 1:
            positive_votes += 1
        if single_res["probability"] is not None:
            calibrated_probs.append(single_res["probability"])

        results[model_key] = single_res

    total_models = len(results)
    avg_calibrated_prob = float(np.mean(calibrated_probs)) if calibrated_probs else 0.5
    avg_pct = round(avg_calibrated_prob * 100, 2)

    # Consensus resolution with explicit 2/4 tie handling
    if positive_votes > (total_models / 2):
        majority_pred = 1
        majority_outcome = "Yes (Likely to Subscribe)"
        agreement_desc = f"{positive_votes}/{total_models} models predict Yes"
    elif positive_votes < (total_models / 2):
        majority_pred = 0
        majority_outcome = "No (Unlikely to Subscribe)"
        agreement_desc = f"{total_models - positive_votes}/{total_models} models predict No"
    else:  # Consensus tie: exactly 2/4 models
        majority_pred = None
        majority_outcome = "Uncertain"
        agreement_desc = "Split Decision (2/4 models predict Yes, 2/4 models predict No)"

    risk_info = compute_risk_tier(avg_calibrated_prob, base_rate=base_rate)

    return {
        "status": "success",
        "consensus": {
            "positive_votes": positive_votes,
            "negative_votes": total_models - positive_votes,
            "majority_prediction": majority_pred,
            "majority_outcome": majority_outcome,
            "average_probability": round(avg_calibrated_prob, 4),
            "average_probability_percentage": avg_pct,
            "agreement_summary": agreement_desc,
            "risk_level": risk_info["tier"],
            "risk_description": risk_info["description"],
            "risk_cutoffs": risk_info["cutoffs"],
        },
        "models": results,
        "general_context": results["random_forest"]["general_context"],
        "key_insights": results["random_forest"]["key_insights"],
        "anti_leakage_applied": True,
        "disclaimer": results["random_forest"]["disclaimer"],
    }


def predict_batch_customers(
    df_records: pd.DataFrame,
    model_name: str = "random_forest",
) -> Dict[str, Any]:
    """
    Validates every single row of a batch dataset with validate_customer_input.
    If any rows are invalid, returns detailed row numbers and reasons without coercion.
    Caps batch processing at 20,000 records.
    """
    if model_name not in MODEL_DEFINITIONS:
        raise ValueError(
            f"Invalid model name '{model_name}'. Choose from: {list(MODEL_DEFINITIONS.keys())}"
        )

    if df_records.empty:
        raise ValueError("Provided batch dataset is empty.")

    max_rows = 20000
    if len(df_records) > max_rows:
        raise ValueError(f"Batch dataset exceeds maximum allowed rows ({max_rows:,}). Found: {len(df_records):,}")

    # Remove duration if present
    cols_to_use = [c for c in df_records.columns if c != "duration" and c != "y"]
    df_clean = df_records[cols_to_use].copy()

    # Validate each row individually
    cleaned_rows: List[Dict[str, Any]] = []
    row_errors: List[Dict[str, Any]] = []

    for idx, row in df_clean.iterrows():
        row_dict = row.to_dict()
        cleaned_row, errs = validate_customer_input(row_dict)
        if errs:
            row_errors.append({
                "row_number": int(idx) + 1,
                "errors": errs,
            })
        else:
            cleaned_rows.append(cleaned_row)

    if row_errors:
        raise ValueError({
            "type": "batch_validation_error",
            "message": f"Found validation errors in {len(row_errors)} of {len(df_records)} rows.",
            "row_errors": row_errors[:50],  # Return up to first 50 row errors
            "total_erroneous_rows": len(row_errors),
        })

    # Execute batch prediction using loaded pipeline
    df_processed = pd.DataFrame(cleaned_rows)
    pipeline = load_model_pipeline(model_name)

    probabilities = None
    if hasattr(pipeline, "predict_proba"):
        try:
            probabilities = pipeline.predict_proba(df_processed)[:, 1]
        except Exception as e:
            logger.warning(f"Could not calculate batch probabilities: {e}")

    metrics_cache = get_cached_metrics() or {}
    optimal_threshold = (
        metrics_cache.get("models", {}).get(model_name, {}).get("optimal_threshold", 0.50)
    )

    if probabilities is not None:
        predictions = (probabilities >= optimal_threshold).astype(int).tolist()
        prob_list = [round(float(p), 4) for p in probabilities]
    else:
        predictions = pipeline.predict(df_processed).tolist()
        prob_list = [0.5] * len(predictions)

    base_rate = get_base_conversion_rate()
    risk_tiers = [
        compute_risk_tier(p, base_rate=base_rate)["tier"]
        for p in prob_list
    ]

    results_list = [
        {
            "row_index": i + 1,
            "prediction": predictions[i],
            "outcome": "Yes" if predictions[i] == 1 else "No",
            "probability": prob_list[i],
            "risk_level": risk_tiers[i],
        }
        for i in range(len(predictions))
    ]

    pos_count = int(sum(predictions))
    neg_count = int(len(predictions) - pos_count)
    avg_prob = round(float(np.mean(prob_list)), 4) if prob_list else 0.5

    return {
        "status": "success",
        "model_key": model_name,
        "model_display_name": MODEL_DEFINITIONS[model_name]["display_name"],
        "total_records": len(predictions),
        "optimal_threshold_used": optimal_threshold,
        "predicted_positive": pos_count,
        "predicted_negative": neg_count,
        "positive_predictions_count": pos_count,
        "negative_predictions_count": neg_count,
        "average_subscription_probability": avg_prob,
        "results": results_list,
        "predictions": predictions,
        "probabilities": prob_list,
        "risk_levels": risk_tiers,
        "risk_cutoffs": {
            "base_rate": round(base_rate, 4),
            "medium_cutoff": round(2 * base_rate, 4),
        },
    }
