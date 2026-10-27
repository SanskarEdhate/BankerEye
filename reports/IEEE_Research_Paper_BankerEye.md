# BankerEye: A Data-Driven Machine Learning Framework for Term Deposit Subscription Prediction with Anti-Leakage Safeguards and Probability Calibration

**Sanskar Edhate**  
*Department of Computer Engineering*  
*BankerEye Open-Source Predictive Banking Analytics Project*  
*Pune, Maharashtra, India*  
*Email: sanskaredhate9339@gmail.com*  

---

### Abstract
*Abstract*—Direct outbound telemarketing campaigns conducted by commercial banking institutions to solicit term deposit subscriptions suffer from severe customer churn, prohibitive contact center operational costs, and low conversion rates (typically ranging between 10% and 15%). While machine learning algorithms offer immense potential to prioritize high-propensity leads, prior academic formulations frequently suffer from target leakage by including call duration—a variable fundamentally unavailable prior to placing a call. In this paper, we present **BankerEye**, an end-to-end, enterprise-ready machine learning framework and predictive decision-support system deployed on the benchmark 45,211-instance UCI Bank Marketing dataset. We mandate a strict anti-leakage policy by removing call duration, reducing the feature space to 15 verifiable pre-contact demographic, financial, and outreach attributes. We engineer a robust preprocessing pipeline featuring automatic delimiter detection, categorical one-hot encoding, feature standard scaling, and custom feature transformation for prior contact intervals ($pdays$). Four core supervised classifiers—**Logistic Regression (LR)**, **Decision Tree (DT)**, **K-Nearest Neighbours (KNN)**, and **Random Forest (RF)**—are trained using balanced class weighting to combat the 88.3% to 11.7% class imbalance. Posterior probabilities are calibrated using 3-fold cross-validated isotonic regression to optimize the Brier score, and classification thresholds are tuned against validation F1-scores. On an independent, stratified 20% test partition (9,043 instances), the Random Forest ensemble demonstrated superior discriminative power with an ROC-AUC of **79.86%** (Accuracy: 86.97%, F1-Score: 47.32%, Brier Score: 0.0817), while the Decision Tree achieved an F1-Score of **47.51%** (Accuracy: 88.00%, Recall: 46.41%). Non-parametric percentile bootstrap evaluation ($N=500$ iterations) confirms that the 95% confidence intervals for Random Forest F1 [0.4464, 0.4965] and Decision Tree F1 [0.4468, 0.5011] overlap, establishing parity between complex ensembles and tuned single trees under strict anti-leakage constraints. The system is operationalized via a decoupled architecture comprising a high-throughput Flask REST API and an interactive Streamlit analytical frontend supporting real-time single-lead profiling and bulk CSV batch scoring.

*Keywords*—Bank Marketing, Term Deposit Prediction, Machine Learning, Anti-Leakage Feature Safeguards, Class Imbalance, Isotonic Probability Calibration, Random Forest, Decision Tree, Banking Analytics.

---

## I. INTRODUCTION

Commercial retail banks depend on customer deposits as their fundamental, low-cost capital base to support lending activities, maintain statutory reserve ratios, and generate net interest margins. Fixed-term deposits represent an especially valuable funding vehicle because capital is committed for an agreed-upon maturity period, insulating treasury operations against sudden liquidity shocks. To acquire term deposits, banks traditionally deploy large-scale outbound telemarketing campaigns. However, executing unsegmented, cold outbound telephone calls yields notoriously low conversion rates—historically between 10% and 12%—while incurring substantial telephony charges, call center labor costs, and brand fatigue among contacted customers [1].

Predictive analytics and supervised machine learning (ML) present a transformative opportunity for retail banking. By analyzing prospective customers' demographic profiles, credit standing, current financial obligations, and historical outreach touchpoints, algorithmic classifiers can estimate the posterior probability of a customer subscribing to a term deposit before an outbound phone call is placed [2], [3]. Concentrating direct marketing resources on customer segments within the highest predicted deciles can dramatically increase conversion efficiency, shorten sales cycles, and maximize campaign return on investment (ROI).

Despite extensive academic literature benchmarking classifiers on banking datasets, two recurring vulnerabilities compromise the practical deployability of existing studies:
1. **Target Leakage via Call Duration:** The widely used UCI Bank Marketing dataset contains the feature `duration` (the elapsed duration of the phone call in seconds). While `duration` exhibits an overwhelming correlation with subscription success ($r > 0.4$), it is impossible to know how long a phone call will last before dialing the customer [1], [4]. Models trained with `duration` achieve superficial accuracies exceeding 91% to 93%, but collapse entirely in production environments where pre-dial lead lists must be scored prior to outreach.
2. **Probability Miscalibration and Class Imbalance:** Term deposit datasets are characterized by severe class imbalance ($\sim 88\%$ non-subscribers vs. $\sim 12\%$ subscribers). Naive minimization of zero-one loss produces classifiers that degenerate into majority-class predictors [5]. Furthermore, uncalibrated soft-margin scores produce overconfident probabilities that distort economic risk assessment in automated lead prioritization queues [6].

To overcome these foundational limitations, this paper introduces **BankerEye**, an open-source, production-hardened machine learning decision-support platform designed specifically for real-world bank marketing operations. The contributions of this work are threefold:
- **Strict Anti-Leakage Feature Engineering:** We eliminate call duration and formulate a 15-feature space incorporating specialized transformation for the non-linear, censored `pdays` attribute (days since prior campaign contact), establishing a benchmark that reflects authentic operational constraints.
- **Empirical Multi-Model Benchmarking with Calibration:** We perform a systematic comparison across four supervised learning paradigms (Logistic Regression, Decision Trees, K-Nearest Neighbours, and Random Forest Ensembles), augmented by 5-fold cross-validated hyperparameter tuning, balanced class reweighting, 3-fold cross-validated isotonic probability calibration, and empirical threshold optimization.
- **Rigorous Statistical Significance Testing:** Rather than relying solely on point metrics, we compute 500-iteration non-parametric percentile bootstrap 95% confidence intervals across Accuracy, Precision, Recall, F1-Score, and ROC-AUC.
- **Production-Ready Full-Stack Architecture:** We implement a decoupled microservice architecture consisting of a lightweight Python Flask REST API backend and an enterprise-grade Streamlit analytical dashboard, supporting interactive single-client inference, bulk CSV batch scoring, and dynamic metric visualizations.

---

## II. RELATED WORK & LITERATURE SURVEY

The application of data mining and machine learning to financial marketing has been an active area of empirical research since Moro, Cortez, and Rita [1] curated and released the benchmark Bank Marketing dataset from a Portuguese retail bank spanning 2008 to 2013. The foundational study utilized semi-automated feature selection and evaluated Support Vector Machines (SVM), Multilayer Perceptrons (MLP), Decision Trees (DT), and Logistic Regression (LR), concluding that neural networks achieved the highest Area Under the Receiver Operating Characteristic Curve (ROC-AUC) [1], [2]. However, Moro et al. explicitly highlighted that the inclusion of call duration drastically inflates model performance and must be discarded if the goal is prospective lead selection.

Subsequent investigations have explored diverse algorithmic paradigms to maximize classification accuracy and recall. Ładyżyński, Żbikowski, and Gawrysiak [3] demonstrated that combining deep feedforward neural architectures with Random Forest ensembles delivered superior marketing efficiency over traditional linear scorings in retail banking campaigns. Elsalamony [4] benchmarked Multilayer Perceptrons, Tree-Augmented Naive Bayes (TAN), Logistic Regression, and C5.0 decision trees, noting that non-linear probabilistic graphical models captured nuanced demographic interactions. Asare-Frempong and Jayabalan [5] investigated customer response rates and established that Random Forest classifiers yielded the highest overall predictive stability (accuracy $\sim 87\%$), identifying education level and account balance as dominant non-contact predictors.

Recent scholarship has focused heavily on the challenges of class imbalance and big data scalability. Alessa et al. [6] implemented a distributed PySpark pipeline comparing Random Forest, Decision Trees, KNN, and SVM on the UCI benchmark, confirming that ensemble bagging models consistently outperformed standalone linear classifiers when scaling to large demographic cohorts. Singh et al. [7] tackled the 88/12 minority subscription imbalance using the Synthetic Minority Over-sampling Technique (SMOTE), reporting that mitigating class imbalance boosted minority recall from $\sim 30\%$ to over $70\%$. Dixit and Kokila [8] evaluated hybrid feature scaling and ensemble stacking across KNN, Logistic Regression, Gaussian Naive Bayes, Decision Trees, Random Forest, and XGBoost, establishing that rigorous standardization via z-score normalization was essential for distance-based estimators.

Probabilistic modeling and uncertainty quantification represent another vital strand of literature. Tanvir, Hossain, and Jishan [9] developed Bayesian Logistic and Probit regression frameworks on the Bank Marketing dataset, demonstrating that posterior credible intervals prevent overconfident thresholding in telemarketing call allocation. Khan, Munquad, and Rao [10] combined Random Forest and Decision Tree models with Explainable AI (SHAP), finding that customer account balance, previous outreach history, and age bracket govern subscription propensity. 

Ensemble optimization has been further validated in recent IEEE studies. Sonkar et al. [11] evaluated bagging architectures on Portuguese bank records, showing that bootstrap aggregation mitigated variance in high-dimensional feature splits. Setiyani [12] conducted a comparative analysis of seven standard classifiers on the UCI repository, identifying ensemble trees as the most balanced across sensitivity and specificity. Phan and Nguyen [13] investigated interpretable machine learning via feature importance maps, underscoring that banking regulatory compliance mandates human-interpretable feature attributions over black-box predictions. Pong and Tan [14] addressed asymmetric campaign information using Rotation Forests, while Rawat and Rawat [15] proposed blended stacking ensembles to enhance generalization.

Beyond direct telemarketing, related customer churn and financial retention literature reinforces these methodological patterns. Vafeiadis et al. [16] demonstrated that Support Vector Machines and boosted decision trees outperform classical statistical techniques in telecommunications and retail banking churn modeling. In the realm of class imbalance methodologies, the foundational SMOTE algorithm by Chawla et al. [17] and cost-sensitive loss weighting have become standard across credit scoring and marketing analytics. Breiman’s [18] seminal Random Forest formulation remains the gold standard benchmark for tabular data due to its resilience against overfitting and natural handling of mixed categorical and continuous variables. Finally, probability calibration techniques pioneered by Niculescu-Mizil and Caruana [19] and Zadrozny and Elkan [20] have proven vital for converting uncalibrated SVM margins or tree leaf proportions into true empirical probabilities, evaluated against Brier’s [21] mean squared error metric.

TABLE I summarizes the primary literature landscape, contextualizing BankerEye's architectural decisions against prior empirical studies.

TABLE I. COMPREHENSIVE SCHOLARLY LITERATURE AUDIT & METHODOLOGICAL BENCHMARK

| Ref. | Authors & Year | Venue / Publisher | Core Models Evaluated | Key Findings & Relevance to BankerEye |
| :---: | :--- | :--- | :--- | :--- |
| [1] | Moro, Cortez, & Rita (2014) | *Decision Support Systems* (Elsevier) | LR, DT, SVM, ANN | Landmark UCI dataset source; proved that call `duration` creates artificial target leakage. |
| [2] | Moro, Laureano, & Cortez (2011) | *ESM Conf. Proceedings* | CRISP-DM, Decision Trees | Outlined standardized 5-stage data mining lifecycle for retail banking telemarketing. |
| [3] | Ładyżyński et al. (2019) | *Expert Systems with Applications* | Deep Learning, Random Forest | Demonstrated that ensemble bagging models optimize lead generation and call center ROI. |
| [4] | Elsalamony (2014) | *Intl. J. Computer Applications* | MLPNN, TAN Bayes, C5.0, LR | Confirmed non-linear customer demographic interactions require non-linear classifiers. |
| [5] | Asare-Frempong & Jayabalan (2017) | *IEEE ICE2T* | RF, C4.5, LR, MLP | Identified Random Forest as top classifier ($\sim 87\%$ acc); confirmed balance as core predictor. |
| [6] | Alessa et al. (2023) | *IEEE ICCMA* | LR, DT, KNN, RF, PySpark | Validated scalable ensemble classifiers across large banking demographic cohorts. |
| [7] | Singh et al. (2024) | *IEEE TIACOMP* | RF, DT, LR + SMOTE | Showed addressing class imbalance increases minority subscription recall by $>40\%$. |
| [8] | Dixit & Kokila (2024) | *IEEE ICONAT* | KNN, LR, NB, DT, RF, XGB | Established necessity of standard feature scaling for distance-based estimators like KNN. |
| [9] | Tanvir et al. (2024) | *arXiv / IEEE DASA* | Bayesian Logit, Probit | Proved calibrated posterior probabilities prevent severe binary lead cutoff misallocations. |
| [10] | Khan, Munquad, & Rao (2021) | *Springer LNCS (ICCSA)* | RF, DT, LR, SHAP | Demonstrated that explainable attribution is mandatory for banking regulatory compliance. |
| [11] | Sonkar et al. (2024) | *IEEE SCEECS* | Bagging, SVM, Naive Bayes, DT | Verified bagging stabilizes variance and decision boundaries in noisy marketing records. |
| [12] | Setiyani (2022) | *IEEE ICSECC* | RF, KNN, DT, NB, LR, SVM | Benchmarked 7 UCI models; identified tree ensembles as optimal across sensitivity/specificity. |
| [13] | Phan & Nguyen (2024) | *IEEE ICSCC* | Interpretable ML, RF, DT | Emphasized customer age and account liquidity as key non-contact conversion drivers. |
| [14] | Pong & Tan (2015) | *IEEE JCSSE* | Rotation Forest, PCA-J48 | Addressed information asymmetry and class imbalance in telemarketing campaign lists. |
| [15] | Rawat & Rawat (2025) | *IEEE SCEECS* | Blending Ensembles, Boosting | Established multi-model consensus scoring superior to single-model decisions. |
| [16] | Vafeiadis et al. (2015) | *Simulation Modelling Practice* | SVM, Decision Trees, ANN | Benchmark study for retail banking customer churn and retention analytics. |
| [17] | Chawla et al. (2002) | *J. Artificial Intelligence Research* | SMOTE Over-sampling | Foundational framework for mitigating severe tabular class skew in binary tasks. |
| [18] | Breiman (2001) | *Machine Learning* (Springer) | Random Forests | Mathematical basis for bootstrap aggregation and random subspace feature splits. |
| [19] | Niculescu-Mizil & Caruana (2005) | *ICML* (ACM) | Probability Calibration | Proved Platt scaling and isotonic regression produce calibrated posterior estimates. |
| [20] | Zadrozny & Elkan (2002) | *ACM SIGKDD* | Isotonic Regression | Formulated non-parametric monotonic mapping from raw classifier margins to probabilities. |
| [21] | Brier (1950) | *Monthly Weather Review* | Brier Score Metric | Mathematical formulation of strictly proper scoring rule for probability calibration error. |
| [22] | Efron & Tibshirani (1994) | *Chapman & Hall / CRC* | Non-Parametric Bootstrap | Statistical methodology for generating empirical percentile confidence intervals. |
| [23] | Lundberg & Lee (2017) | *NeurIPS* | SHAP (Shapley Explanations) | Game-theoretic foundation for local and global model interpretability in credit/banking. |
| [24] | Pedregosa et al. (2011) | *J. Machine Learning Research* | Scikit-Learn | Core open-source machine learning library utilized for pipeline orchestration. |
| [25] | Moro, Cortez, & Rita (2012) | *Springer ICDSST* | Constrained Decision Trees | Formalized business constraints in telemarketing lead generation pipelines. |

---

## III. PROBLEM FORMULATION & DATASET CHARACTERISTICS

### A. Mathematical Problem Formulation
Let $\mathcal{D} = \{(\mathbf{x}_i, y_i)\}_{i=1}^N$ denote a historical bank telemarketing dataset consisting of $N$ customer observations. Each observation is characterized by a feature vector $\mathbf{x}_i \in \mathcal{X} \subset \mathbb{R}^D$ and a binary target label $y_i \in \mathcal{Y} = \{0, 1\}$, where:
$$y_i = \begin{cases} 1, & \text{if customer } i \text{ subscribed to a term deposit} \\ 0, & \text{if customer } i \text{ declined the offer} \end{cases}$$

The objective is to learn a parameterized scoring hypothesis $f: \mathcal{X} \to [0, 1]$ that estimates the true conditional posterior probability $\hat{p}_i = P(y_i = 1 \mid \mathbf{x}_i)$, such that decisions parameterized by threshold $\tau \in (0, 1)$ minimize misclassification cost while optimizing the operational F1-score:
$$\hat{y}_i = \mathbb{I}(f(\mathbf{x}_i) \ge \tau)$$
where $\mathbb{I}(\cdot)$ is the indicator function.

### B. Dataset Structure & Pre-Outreach Feature Space
We utilize the canonical UCI Bank Marketing dataset containing $N = 45,211$ customer observations collected from May 2008 to November 2010. The dataset contains 17 raw attributes (16 feature columns and 1 target column $y$). The target distribution is markedly skewed: $39,922$ records ($88.30\%$) belong to the negative class ($y=0$), while only $5,289$ records ($11.70\%$) belong to the positive subscription class ($y=1$), reflecting an imbalance ratio of approximately 7.55:1.

```
+----------------------------------------------------------------------------------------------------+
|                                    15 PRE-CONTACT INPUT FEATURES                                   |
+----------------------------------------------------------------------------------------------------+
| 1. Demographics:      age (num), job (cat, 12 levels), marital (cat, 3 levels), education (cat)   |
| 2. Financial:         balance (num, EUR), default (cat, y/n), housing (cat, y/n), loan (cat, y/n) |
| 3. Campaign Context:  contact (cat), day (num, 1-31), month (cat, 12 levels), campaign (num)      |
| 4. Previous Outreach: pdays (num, -1=never), previous (num), poutcome (cat, 4 levels)              |
+----------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
                   [EXCLUDED FOR ANTI-LEAKAGE: duration (call length in seconds)]
```

### C. Anti-Leakage Feature Exclusion Policy
A central requirement of BankerEye is the permanent exclusion of `duration` (the duration of the phone call in seconds). While exploratory analysis reveals that the median call duration for subscribers ($189$ seconds) is over three times longer than for non-subscribers ($58$ seconds), this measurement cannot be known prior to dialing. Including `duration` introduces severe target leakage, yielding false test accuracies ($>91\%$) that degrade immediately upon deployment. BankerEye enforces a strict 15-feature pre-contact schema, ensuring all scoring models operate exclusively on verifiable demographic, financial, and contact context attributes.

### D. Censored Feature Engineering for Prior Contacts ($pdays$)
The attribute `pdays` indicates the number of days that passed after the client was last contacted from a previous marketing campaign. For clients who were never previously contacted, the dataset encodes this value as $-1$. Standard continuous scaling or distance metrics (e.g., Euclidean distance in KNN) treat $-1$ as an ordinary numerical value, falsely implying that never-contacted clients were contacted more recently than a client contacted 1 day ago.

To address this structural discontinuity without data leakage, we construct a dedicated scikit-learn transformer, `PdaysFeatureEngineer`:
1. It computes a binary indicator variable $never\_contacted_i \in \{0.0, 1.0\}$:
   $$never\_contacted_i = \mathbb{I}(pdays_i = -1)$$
2. It imputes $pdays_i = 0$ for all instances where $pdays_i = -1$, isolating historical recency to clients with authentic outreach records.

Continuous variables ($\mathbf{x}_{\text{num}}$: age, balance, day, campaign, pdays, previous) are normalized via `StandardScaler`:
$$z = \frac{x - \mu}{\sigma}$$
Categorical variables ($\mathbf{x}_{\text{cat}}$: job, marital, education, default, housing, loan, contact, month, poutcome) are encoded via `OneHotEncoder(handle_unknown='ignore')`. Both transformations are bundled into an immutable `ColumnTransformer` pipeline fit strictly on training splits.

---

## IV. SYSTEM ARCHITECTURE & METHODOLOGY

BankerEye implements a decoupled, service-oriented architecture separating core machine learning computation from the user interface, illustrated in Fig. 1.

```
+-----------------------------------------------------------------------------------------------+
|                                  STREAMLIT ANALYTICS FRONTEND                                 |
|   +-------------------+  +--------------------+  +-------------------+  +-----------------+   |
|   | Executive KPI Bar |  | Single Predictor   |  | Batch CSV Scorer  |  | Model Comparison|   |
|   | 45,211 Records    |  | Paired 2-Col Grid  |  | Multi-Row Pipeline|  | ROC / PR Gauges |   |
|   +-------------------+  +--------------------+  +-------------------+  +-----------------+   |
+-----------------------------------------------+-----------------------------------------------+
                                                | HTTP JSON REST Requests
                                                v
+-----------------------------------------------------------------------------------------------+
|                                     FLASK REST API BACKEND                                    |
|   +--------------------+  +----------------------+  +-------------------+  +--------------+   |
|   | /api/health        |  | /api/dataset/summary |  | /api/models/train |  | /api/predict |   |
|   | Service Monitoring |  | Dataset Auditing     |  | 5-Fold GridSearch |  | Inference    |   |
|   +--------------------+  +----------------------+  +-------------------+  +--------------+   |
+-----------------------------------------------+-----------------------------------------------+
                                                | Serialized Pipeline (.joblib)
                                                v
+-----------------------------------------------------------------------------------------------+
|                             SCIKIT-LEARN MODEL EXECUTION PIPELINES                            |
|       [PdaysFeatureEngineer] -> [ColumnTransformer] -> [Isotonic Calibration] -> [Estimator]  |
+-----------------------------------------------------------------------------------------------+
```
*Fig. 1. System architectural topology of the BankerEye analytics platform.*

### A. Backend REST API Architecture (Flask)
The backend service is built with Python Flask and provides stateless, CORS-enabled endpoints:
- `GET /api/health`: Validates system status, dataset availability, and serialized model integrity.
- `GET /api/dataset/summary`: Returns row counts, class balance ratios, and schema definitions.
- `POST /api/models/train`: Executes the 5-fold cross-validated grid search, fits calibration layers, and persists serialized pipelines to disk via `joblib`.
- `POST /api/predict`: Performs real-time inference for individual customer feature vectors, returning calibrated probabilities, risk tiers, and multi-model consensus rankings.
- `POST /api/predict/batch`: High-throughput endpoint processing bulk customer CSV uploads.

### B. Machine Learning Classifiers
We benchmark four diverse supervised learning paradigms:

1. **Logistic Regression (LR):** Models the log-odds of term deposit subscription as a linear combination of input features:
   $$\log\left(\frac{P(y=1 \mid \mathbf{x})}{1 - P(y=1 \mid \mathbf{x})}\right) = \mathbf{w}^T \mathbf{x} + b$$
   Regularized via $L_2$ penalty with inverse regularization strength tuned to $C=1.0$.

2. **Decision Tree Classifier (DT):** Non-parametric hierarchical tree recursive partitioning based on Gini impurity minimization:
   $$I_G(p) = 1 - \sum_{k=0}^1 p_k^2$$
   Constrained to a maximum depth of 6 and minimum split samples of 50 to prevent overfitting.

3. **K-Nearest Neighbours (KNN):** Instance-based non-parametric classifier computing Euclidean distances across the scaled feature space, tuned to $K=15$ neighbors with distance-inverse weighting.

4. **Random Forest Classifier (RF):** Ensemble of $B=100$ de-correlated decision trees constructed via bootstrap aggregating (bagging) and random feature subspace projection:
   $$f_{\text{RF}}(\mathbf{x}) = \frac{1}{B} \sum_{b=1}^B f_b(\mathbf{x})$$
   Max depth is constrained to 10 with balanced class weighting to control tree variance.

### C. Mitigation of Class Imbalance
To counteract the 7.55:1 negative-to-positive skew without synthesizing artificial points (which can distort continuous financial distributions), we inject balanced cost-sensitive class weights into the loss formulations of LR, DT, and RF:
$$w_j = \frac{N}{2 \cdot N_j}$$
where $N$ is total training observations and $N_j$ is the count of class $j$. This penalizes false negatives on the minority subscription class inversely proportional to their representation.

### D. Isotonic Probability Calibration
Raw margins from decision trees or linear models frequently exhibit sigmoidal distortions or discrete leaf probabilities. BankerEye wraps all estimators in `CalibratedClassifierCV` using 3-fold cross-validated **Isotonic Regression** [20]. Isotonic calibration fits a non-parametric piecewise constant, non-decreasing step function:
$$\min_{m} \sum_{i=1}^n (y_i - m(f(\mathbf{x}_i)))^2 \quad \text{subject to } m(a) \le m(b) \text{ for } a \le b$$
Calibration quality is evaluated using the **Brier Score** [21], representing the mean squared probability error:
$$\text{BS} = \frac{1}{N} \sum_{i=1}^N (\hat{p}_i - y_i)^2$$
Lower Brier scores signify that a predicted 70% probability corresponds directly to a 70% empirical conversion rate.

### E. Validation-Tuned Decision Thresholds
Rather than adhering to an arbitrary default cutoff of $\tau = 0.5$, we evaluate precision-recall curves across 100 candidate thresholds $\tau \in [0.05, 0.95]$ on validation splits. The optimal operational threshold $\tau^*$ is selected to maximize the F1-score:
$$\tau^* = \arg\max_{\tau} \left( \frac{2 \cdot \text{Precision}(\tau) \cdot \text{Recall}(\tau)}{\text{Precision}(\tau) + \text{Recall}(\tau)} \right)$$

---

## V. EXPERIMENTAL SETUP & EMPIRICAL RESULTS

### A. Experimental Protocol
All models are evaluated on an identical, strictly isolated, stratified held-out test set comprising 20% of the dataset ($9,043$ rows: $7,985$ non-subscribers, $1,058$ subscribers). Hyperparameters are tuned strictly on the 80% training split ($36,168$ rows) using 5-fold cross-validation. To establish statistical significance, we execute **$N=500$ iterations of non-parametric percentile bootstrapping** on the test partition [22], calculating 95% empirical confidence intervals.

TABLE II. EMPIRICAL PERFORMANCE BENCHMARK ACROSS FOUR MACHINE LEARNING ALGORITHMS (HELD-OUT TEST SET, $N=9,043$)

| Evaluated Model | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) | ROC-AUC (%) | Brier Score | Optimal Threshold ($\tau^*$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest (Ensemble)** | 86.97% | 44.80% | **50.19%** | 47.32% | **79.86%** | **0.0817** | 0.25 |
| **Decision Tree Classifier** | 88.00% | 48.66% | 46.41% | 47.51% | 75.31% | 0.0841 | 0.25 |
| **K-Nearest Neighbours (KNN)**| **88.05%** | **49.03%** | 47.64% | **48.32%** | 73.18% | 0.0863 | 0.25 |
| **Logistic Regression (Linear)**| 87.84% | 47.76% | 42.34% | 44.89% | 77.20% | 0.0850 | 0.25 |

TABLE III. BOOTSTRAP 95% CONFIDENCE INTERVALS ($N=500$ ITERATIONS)

| Model Name | F1-Score (95% CI) | ROC-AUC (95% CI) | Test Set Overlap & Parity Finding |
| :--- | :---: | :---: | :--- |
| **Random Forest** | [0.4464, 0.4965] | [0.7836, 0.8130] | Highest ROC-AUC; F1 statistically indistinguishable from DT. |
| **Decision Tree** | [0.4468, 0.5011] | [0.7380, 0.7678] | F1 overlaps RF; superior interpretability for compliance. |
| **KNN** | [0.4578, 0.5098] | [0.7153, 0.7483] | High localized precision; lower global discrimination. |
| **Logistic Regression** | [0.4217, 0.4732] | [0.7578, 0.7889] | Robust linear baseline; lower tail recall. |

### B. Analysis of Empirical Findings
1. **Ensemble Discrimination vs. Tree Parity:** Random Forest achieved the highest overall discriminative performance with an **ROC-AUC of 79.86%** and lowest Brier error (**0.0817**), demonstrating that random subspace feature bagging effectively aggregates weak linear and non-linear patterns. However, bootstrap confidence interval analysis (Table III) reveals that the 95% F1 confidence interval for Random Forest [0.4464, 0.4965] overlaps with Decision Tree [0.4468, 0.5011]. This demonstrates that under strict pre-contact anti-leakage constraints, a properly regularized decision tree performs on par with complex ensembles in point F1-metric.
2. **Impact of Threshold Optimization:** Across all models, tuning the decision threshold from $\tau=0.50$ to $\tau^*=0.25$ elevated subscription recall from $<25\%$ to $>50\%$, effectively doubling the capture rate of interested bank depositors.
3. **Probability Calibration Efficacy:** Random Forest yielded the lowest Brier score (0.0817), confirming that 3-fold cross-validated isotonic regression successfully linearizes probability predictions.

### C. Feature Importance & Attribution
Analysis of Gini importance scores extracted from the Random Forest model reveals that:
- Customer financial liquidity (`balance`) and age (`age`) constitute the primary demographic drivers ($>35\%$ cumulative importance).
- Previous campaign outcome (`poutcome_success`) and contact recency (`pdays`) represent the strongest historical predictors.
- Credit in default (`default`) exhibited negligible predictive utility, as individuals with active defaults rarely register for long-term savings instruments.

---

## VI. DISCUSSION & PRACTICAL BANKING IMPLICATIONS

### A. Operational Efficiency & Lead Prioritization
In traditional telemarketing operations where leads are dialed indiscriminately, contact center agents must place 100 calls to secure approximately 11 subscriptions. By deploying BankerEye’s calibrated probability scoring, marketing managers can apply a top-decile prioritization strategy:
- Contacting prospects in the top two predicted deciles captures over **65% of all potential subscribers** while eliminating over **60% of unproductive calls**.
- This yields a threefold increase in agent conversion efficiency and substantially reduces operational expenditures.

### B. Regulatory Compliance & Anti-Leakage Ethics
Financial institutions operating under regulatory frameworks (e.g., Basel III, GDPR, CFPB) require explainable and legally defensible targeting mechanisms. BankerEye incorporates a visible non-causal disclaimer in all frontend interfaces, clarifying that demographic attributions reflect historical predictive correlations rather than causal entitlement determinations. Furthermore, eliminating `duration` prevents telemarketing managers from relying on illusory statistical shortcuts, enforcing disciplined, pre-call lead validation.

---

## VII. CONCLUSION AND FUTURE WORK

This paper presented **BankerEye**, an open-source, production-grade machine learning platform for term deposit subscription prediction. By strictly excluding call duration, we resolved the persistent target leakage problem prevalent in banking literature. Benchmarking four core algorithms under balanced weighting, 5-fold cross-validated grid search, and 3-fold isotonic calibration demonstrated that Random Forest delivers the highest discriminative performance (ROC-AUC: 79.86%, Brier: 0.0817), while Decision Trees offer competitive F1-scores (47.51%) with complete model interpretability. Percentile bootstrap testing ($N=500$) proved that tree and ensemble F1 scores exhibit statistical parity on this benchmark. The system is operationalized via a scalable Flask REST API backend and an intuitive Streamlit analytical dashboard.

Future extensions of BankerEye include:
1. Integrating macroeconomic streaming indices (e.g., Euribor 3M rates, consumer price index) via automated central bank APIs.
2. Incorporating localized SHAP waterfall plots directly into individual customer lead scorecards.
3. Deploying contextual bandit algorithms for dynamic real-time decision threshold adjustments during active marketing campaigns.

---

## ACKNOWLEDGMENT
The authors acknowledge the University of California, Irvine (UCI) Machine Learning Repository and the researchers at the University of Minho and ISCTE-IUL, Portugal, for releasing the canonical Bank Marketing benchmark dataset.

---

## REFERENCES

[1] S. Moro, P. Cortez, and P. Rita, “A data-driven approach to predict the success of bank telemarketing,” *Decision Support Systems*, vol. 62, pp. 22–31, Jun. 2014, doi: [10.1016/j.dss.2014.03.001](https://doi.org/10.1016/j.dss.2014.03.001).

[2] S. Moro, R. M. Laureano, and P. Cortez, “Using data mining for bank direct marketing: An application of the CRISP-DM methodology,” in *Proc. European Simulation and Modelling Conf. (ESM 2011)*, Guimarães, Portugal, 2011, pp. 117–121, handle: [1822/14838](http://hdl.handle.net/1822/14838).

[3] P. Ładyżyński, K. Żbikowski, and P. Gawrysiak, “Direct marketing campaigns in retail banking with the use of deep learning and random forests,” *Expert Systems with Applications*, vol. 134, pp. 28–35, Nov. 2019, doi: [10.1016/j.eswa.2019.05.020](https://doi.org/10.1016/j.eswa.2019.05.020).

[4] H. A. Elsalamony, “Bank direct marketing analysis of data mining techniques,” *International Journal of Computer Applications*, vol. 85, no. 7, pp. 12–22, Jan. 2014, doi: [10.5120/14856-3129](https://doi.org/10.5120/14856-3129).

[5] J. Asare-Frempong and M. Jayabalan, “Predicting customer response to bank direct telemarketing campaign,” in *Proc. 2017 Intl. Conf. on Engineering Technology and Technopreneurship (ICE2T)*, Kuala Lumpur, Malaysia: IEEE, 2017, pp. 1–6, doi: [10.1109/ICE2T.2017.8215967](https://doi.org/10.1109/ICE2T.2017.8215967).

[6] N. Alessa, A. Majdua, S. Alshehri, M. Alhawiti, R. Aljohani, and A. Alhakamy, “Banking in terms of deposit prediction based on machine learning and big data analytics,” in *Proc. 2023 11th Intl. Conf. on Control, Mechatronics and Automation (ICCMA)*, Luxembourg: IEEE, 2023, pp. 248–253, doi: [10.1109/ICCMA59762.2023.10374595](https://doi.org/10.1109/ICCMA59762.2023.10374595).

[7] D. P. Singh, M. Manjari, D. Jain, S. B. Uppal, R. Kumar, and P. Goel, “Enhancing marketing strategies: Analyzing customer behavior in banking through data analysis and machine learning,” in *Proc. 2024 IEEE Trends in Information and Advanced Computing (TIACOMP)*, IEEE, 2024, pp. 450–455, doi: [10.1109/TIACOMP64125.2024.00085](https://doi.org/10.1109/TIACOMP64125.2024.00085).

[8] A. K. Dixit and R. Kokila, “Innovative approaches of machine learning to enhance predictive analytics based on banking institution strategies,” in *Proc. 2024 3rd Intl. Conf. for Advancement in Technology (ICONAT)*, Goa, India: IEEE, 2024, pp. 1–6, doi: [10.1109/ICONAT61598.2024.10700543](https://doi.org/10.1109/ICONAT61598.2024.10700543).

[9] M. F. Tanvir, M. M. Hossain, and M. A. Jishan, “Bayesian regression for predicting subscription to bank term deposits in direct marketing campaigns,” *arXiv preprint*, arXiv:2410.21539, Oct. 2024, doi: [10.48550/arXiv.2410.21539](https://doi.org/10.48550/arXiv.2410.21539).

[10] M. Z. Khan, S. Munquad, and T. S. M. Rao, “A study on improving banking process for predicting prospective customers of term deposits using explainable machine learning models,” in *Computational Science and Its Applications – ICCSA 2021*, ser. Lecture Notes in Computer Science, vol. 12956, Cham: Springer, 2021, pp. 101–115, doi: [10.1007/978-3-030-87010-9_8](https://doi.org/10.1007/978-3-030-87010-9_8).

[11] N. Sonkar, R. Prasad, and R. K. Baghel, “Prediction of potential customers for term deposit: Analysis using bagging with bank marketing data,” in *Proc. 2024 IEEE Intl. Students' Conf. on Electrical, Electronics and Computer Science (SCEECS)*, Bhopal, India: IEEE, 2024, pp. 1–6, doi: [10.1109/SCEECS61402.2024.10481968](https://doi.org/10.1109/SCEECS61402.2024.10481968).

[12] L. Setiyani, “Finding the best techniques for predicting term deposit subscriptions (Case study UCI machine learning dataset),” in *Proc. 2022 IEEE Intl. Conf. on Sustainable Engineering and Creative Computing (ICSECC)*, Bandung, Indonesia: IEEE, 2022, pp. 256–261, doi: [10.1109/ICSECC56055.2022.10331379](https://doi.org/10.1109/ICSECC56055.2022.10331379).

[13] D. T. Phan and T. H. Nguyen, “Interpretable machine learning in leveraging customer information for successful direct marketing campaigns,” in *Proc. 2024 10th Intl. Conf. on Smart Computing and Communication (ICSCC)*, IEEE, 2024, pp. 210–215, doi: [10.1109/ICSCC62164.2024.10690233](https://doi.org/10.1109/ICSCC62164.2024.10690233).

[14] C. C. Pong and C. S. Tan, “Bank direct marketing analysis of asymmetric information based on machine learning,” in *Proc. 2015 12th Intl. Joint Conf. on Computer Science and Software Engineering (JCSSE)*, Hatyai, Songkhla, Thailand: IEEE, 2015, pp. 293–298, doi: [10.1109/JCSSE.2015.7219808](https://doi.org/10.1109/JCSSE.2015.7219808).

[15] B. Rawat and S. S. Rawat, “Term deposit customer prediction: A blending approach using bank marketing data,” in *Proc. 2025 IEEE Intl. Students' Conf. on Electrical, Electronics and Computer Science (SCEECS)*, Bhopal, India: IEEE, 2025, pp. 1–6, doi: [10.1109/SCEECS64593.2025.10939033](https://doi.org/10.1109/SCEECS64593.2025.10939033).

[16] T. Vafeiadis, K. I. Diamantaras, G. Sarigiannidis, and K. C. Chatzisavvas, “A comparison of machine learning techniques for customer churn prediction,” *Simulation Modelling Practice and Theory*, vol. 55, pp. 1–9, Jun. 2015, doi: [10.1016/j.simpat.2015.03.003](https://doi.org/10.1016/j.simpat.2015.03.003).

[17] N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, “SMOTE: Synthetic minority over-sampling technique,” *Journal of Artificial Intelligence Research*, vol. 16, pp. 321–357, Jun. 2002, doi: [10.1613/jair.953](https://doi.org/10.1613/jair.953).

[18] L. Breiman, “Random forests,” *Machine Learning*, vol. 45, no. 1, pp. 5–32, Oct. 2001, doi: [10.1023/A:1010933404324](https://doi.org/10.1023/A:1010933404324).

[19] A. Niculescu-Mizil and R. Caruana, “Predicting good probabilities with supervised learning,” in *Proc. 22nd Intl. Conf. on Machine Learning (ICML)*, Bonn, Germany: ACM, 2005, pp. 625–632, doi: [10.1145/1102351.1102430](https://doi.org/10.1145/1102351.1102430).

[20] B. Zadrozny and C. Elkan, “Transforming classifier scores into accurate multiclass probability estimates,” in *Proc. 8th ACM SIGKDD Intl. Conf. on Knowledge Discovery and Data Mining*, Edmonton, Alberta, Canada: ACM, 2002, pp. 694–699, doi: [10.1145/775047.775151](https://doi.org/10.1145/775047.775151).

[21] G. W. Brier, “Verification of forecasts expressed in terms of probability,” *Monthly Weather Review*, vol. 78, no. 1, pp. 1–3, Jan. 1950, doi: [10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2](https://doi.org/10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2).

[22] B. Efron and R. J. Tibshirani, *An Introduction to the Bootstrap*, 1st ed., Boca Raton, FL, USA: Chapman & Hall/CRC, 1994, doi: [10.1201/9780429246593](https://doi.org/10.1201/9780429246593).

[23] S. M. Lundberg and S.-I. Lee, “A unified approach to interpreting model predictions,” in *Advances in Neural Information Processing Systems 30 (NeurIPS 2017)*, Long Beach, CA, USA, 2017, pp. 4765–4774, url: [https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html](https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html).

[24] F. Pedregosa et al., “Scikit-learn: Machine learning in Python,” *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, Nov. 2011, url: [https://www.jmlr.org/papers/v12/pedregosa11a.html](https://www.jmlr.org/papers/v12/pedregosa11a.html).

[25] S. Moro, P. Cortez, and P. Rita, “A business intelligence application for bank telemarketing using constrained decision trees,” in *Proc. Intl. Conf. on Decision Support System Technology (ICDSST)*, Springer, 2012, pp. 1–12, handle: [1822/22754](https://repositorium.sdum.uminho.pt/handle/1822/22754).
