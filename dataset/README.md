# BankerEye Datasets Directory Guide

This directory is organized into three distinct, structured subfolders to make dataset variants easy to understand and work with.

---

## 📁 1. Canonical UCI Bank Marketing Dataset
**Path:** `dataset/1_uci_bank_marketing_canonical/`

The primary benchmark dataset introduced by Sérgio Moro, Paulo Cortez, and Paulo Rita (2011/2014) from the UCI Machine Learning Repository.
- **`bank-full.csv`**: Full benchmark dataset containing **45,211 rows** and **17 columns** (semicolon `;` delimited).
- **`bank.csv`**: 10% randomly sampled subset containing **4,521 rows** for quick benchmarking.
- **`bank-names.txt`**: Original attribute definitions and citation details.
- **Target Variable:** `y` (`'no'` = 39,922 [88.30%], `'yes'` = 5,289 [11.70%]).
- **Key Feature Safeguard:** Attribute `duration` is excluded during model training to prevent target leakage.

---

## 📁 2. Socioeconomic Extended Dataset (Bank-Additional)
**Path:** `dataset/2_bank_additional_socioeconomic/`

Extended dataset enriched with macroeconomic indicators from Banco de Portugal:
- **`bank-additional-full.csv`**: **41,188 rows** and **21 columns** (semicolon `;` delimited).
- **`bank-additional.csv`**: 10% subset with **4,119 rows**.
- **`bank-additional-names.txt`**: Detailed descriptions of macroeconomic features:
  - `emp.var.rate`: Employment variation rate (quarterly indicator)
  - `cons.price.idx`: Consumer price index (monthly indicator)
  - `cons.conf.idx`: Consumer confidence index (monthly indicator)
  - `euribor3m`: Euribor 3-month rate (daily indicator)
  - `nr.employed`: Number of employees (quarterly indicator)
- **Target Variable:** `y` (`'no'` / `'yes'`).

---

## 📁 3. Competition Train/Test Partition Dataset
**Path:** `dataset/3_train_test_competition/`

Kaggle / ML competition format pre-split into labeled training data and unlabeled testing data:
- **`train.csv`**: **22,501 labeled customer records** with `RecordID` and target column `subscribe` (`'no'`, `'yes'`).
- **`test.csv`**: **7,501 unlabeled customer records** for out-of-sample prediction and scoring.
- **`sample_submission.csv`**: Reference submission format containing `RecordID,subscribe`.
- **`data description.txt`**: Feature descriptions and attribute domains.
- **Delimiter:** Standard comma (`,`) delimited.

---

## ⚙️ Config & Automatic Dataset Discovery
`backend/config.py` and `backend/services/preprocessing.py` automatically detect and resolve datasets across these candidate folders in priority order, with custom overrides configurable via the `DATASET_PATH` environment variable.
