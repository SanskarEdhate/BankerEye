import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
DATASET_DIR = BASE_DIR / "dataset"
SAVED_MODELS_DIR = BACKEND_DIR / "saved_models"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure runtime directories exist
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Default primary dataset candidate files
DATASET_CANDIDATES = [
    DATASET_DIR / "Data Cleaning & Splitting" / "1_uci_bank_marketing_canonical" / "03_Clean_Data" / "bank-full_clean.csv",
    DATASET_DIR / "Data Cleaning & Splitting" / "1_uci_bank_marketing_canonical" / "01_Raw_Data" / "bank-full.csv",
    DATASET_DIR / "Data Cleaning & Splitting" / "3_train_test_competition" / "04_Train_Data" / "train.csv",
    DATASET_DIR / "Data Cleaning & Splitting" / "2_bank_additional_socioeconomic" / "03_Clean_Data" / "bank-additional-full_clean.csv",
]


# Explicit dataset path override from env if set
ENV_DATASET_PATH = os.getenv("DATASET_PATH")
if ENV_DATASET_PATH:
    custom_path = Path(ENV_DATASET_PATH)
    if not custom_path.is_absolute():
        custom_path = BASE_DIR / custom_path
    DATASET_CANDIDATES.insert(0, custom_path)

# Flask configuration
FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")

# Training & Splitting configuration
DEFAULT_TEST_SIZE = 0.20
RANDOM_STATE = 42

# Target column name
TARGET_COLUMN = "y"

# Explicitly excluded columns for main prediction experiment (anti-leakage requirement)
EXCLUDED_FEATURES_MAIN = ["duration"]

# Expected features for validation
NUMERICAL_FEATURES = ["age", "balance", "day", "campaign", "pdays", "previous"]
CATEGORICAL_FEATURES = [
    "job", "marital", "education", "default", "housing", "loan", 
    "contact", "month", "poutcome"
]
ALL_INPUT_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
