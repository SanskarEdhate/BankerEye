# BankerEye Datasets Directory Guide

All project datasets are organized into the **`dataset/Data Cleaning & Splitting/`** directory. Each dataset is structured into 5 standardized lifecycle stages accompanied by auditable JSON summary files and a top-level manifest.

---

## 📂 Directory Structure

```text
dataset/
├── Data Cleaning & Splitting/
│   ├── dataset_manifest.json                          # Global registry and dataset catalog
│   ├── 1_uci_bank_marketing_canonical/                # Canonical UCI Bank Marketing benchmark
│   │   ├── 01_Raw_Data/                               # Untouched originals (bank-full.csv, bank.csv, bank-names.txt)
│   │   ├── 02_Unclean_Data/                           # Exact duplicate state prior to cleaning
│   │   ├── 03_Clean_Data/                             # Cleaned & validated dataset (45,211 rows, 17 cols)
│   │   ├── 04_Train_Data/                             # Stratified training split (80% = 36,168 rows)
│   │   ├── 05_Test_Data/                              # Stratified testing split (20% = 9,043 rows)
│   │   └── data_summary.json                          # Audit log & metadata metrics
│   ├── 2_bank_additional_socioeconomic/               # Macroeconomic enriched dataset
│   │   ├── 01_Raw_Data/                               # Raw files (bank-additional-full.csv, bank-additional.csv)
│   │   ├── 02_Unclean_Data/                           # Prior to deduplication
│   │   ├── 03_Clean_Data/                             # Cleaned & deduplicated (41,176 rows, 12 dups removed)
│   │   ├── 04_Train_Data/                             # Stratified training split (80% = 32,940 rows)
│   │   ├── 05_Test_Data/                              # Stratified testing split (20% = 8,236 rows)
│   │   └── data_summary.json                          # Audit log & metadata metrics
│   └── 3_train_test_competition/                      # Kaggle / Competition partition
│       ├── 01_Raw_Data/                               # Raw files (train.csv, test.csv, sample_submission.csv)
│       ├── 02_Unclean_Data/                           # Prior to audit
│       ├── 03_Clean_Data/                             # Cleaned train (22,500 rows) & test (7,500 rows)
│       ├── 04_Train_Data/                             # Clean train & validation train splits
│       ├── 05_Test_Data/                              # Unlabeled test & validation test splits
│       └── data_summary.json                          # Audit log & metadata metrics
└── README.md                                          # This documentation guide
```

---

## 📁 1. Canonical UCI Bank Marketing Dataset
**Path:** `dataset/Data Cleaning & Splitting/1_uci_bank_marketing_canonical/`

The primary benchmark dataset introduced by Sérgio Moro, Paulo Cortez, and Paulo Rita (2011/2014) from the UCI Machine Learning Repository.
- **Clean File:** `03_Clean_Data/bank-full_clean.csv` — **45,211 rows** and **17 columns** (semicolon `;` delimited).
- **Train Split:** `04_Train_Data/train.csv` — **36,168 rows** (stratified 80%).
- **Test Split:** `05_Test_Data/test.csv` — **9,043 rows** (stratified 20%).
- **Target Variable:** `y` (`'no'` = 39,922 [88.30%], `'yes'` = 5,289 [11.70%]).
- **Key Feature Safeguard:** Attribute `duration` is excluded during model training to prevent target leakage.

---

## 📁 2. Socioeconomic Extended Dataset (Bank-Additional)
**Path:** `dataset/Data Cleaning & Splitting/2_bank_additional_socioeconomic/`

Extended dataset enriched with macroeconomic indicators from Banco de Portugal:
- **Clean File:** `03_Clean_Data/bank-additional-full_clean.csv` — **41,176 rows** and **21 columns** (12 exact duplicate rows removed).
- **Train Split:** `04_Train_Data/train.csv` — **32,940 rows** (stratified 80%).
- **Test Split:** `05_Test_Data/test.csv` — **8,236 rows** (stratified 20%).
- **Macroeconomic Features:** `emp.var.rate`, `cons.price.idx`, `cons.conf.idx`, `euribor3m`, `nr.employed`.
- **Target Variable:** `y` (`'no'` / `'yes'`).

---

## 📁 3. Competition Train/Test Partition Dataset
**Path:** `dataset/Data Cleaning & Splitting/3_train_test_competition/`

Kaggle / ML competition format partitioned into labeled training data and unlabeled testing data:
- **Clean Train:** `03_Clean_Data/train_clean.csv` — **22,500 rows** (1 duplicate removed).
- **Clean Test:** `03_Clean_Data/test_clean.csv` — **7,500 rows** (1 duplicate removed).
- **Train Split:** `04_Train_Data/train.csv` (22,500 rows) & `val_train.csv` (18,000 rows).
- **Test Split:** `05_Test_Data/test.csv` (7,500 rows) & `val_test.csv` (4,500 rows).
- **Delimiter:** Standard comma (`,`) delimited.

---

## ⚙️ Automated Integration
`backend/config.py` and `backend/services/preprocessing.py` natively resolve and inspect these datasets via `dataset_manifest.json` and provide interactive inspection tabs in the Streamlit frontend.
