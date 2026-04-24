# AdVise — Data Science (Milestone 2)

## Overview
This folder contains the exploratory data analysis and baseline modeling work
for the AdVise ad performance prediction project. The goal is to predict
**Click-Through Rate (CTR)** from campaign configuration and audience features.

---

## Files
| File | Description |
|------|-------------|
| `experiments.ipynb` | Main EDA and modeling notebook |
| `modeling_related_files.py` | Placeholder for shared modeling utilities (future use) |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | DS service container definition |
| `README.md` | This file |

---

## Running Jupyter in Docker

The **`ds`** service in the **repository root** `docker-compose.yml` is assigned the Compose profile **`data-science`**. Services with a profile are **not** started by plain `docker compose up` / `docker compose up --build`; that is intentional so the default stack (database, ETL, API, Streamlit) stays the main path.

From the **repository root**, start the DS container with:

```bash
docker compose --profile data-science up -d --build ds
```

Open **http://localhost:8888** in a **normal browser** (Chrome, Safari, Firefox). Some IDE-embedded or Simple-Browser views can still show a “token or password” screen even when the server has auth disabled; use an external browser for the least hassle.

The **`ds`** service mounts the whole **`AdVise/`** tree at **`/advise`** in the container (not only `AdVise/ds/`), so paths like `../etl/db/...` and imports from `db_helpers` work the same as on your host, and the Jupyter file browser can list **ds**, **etl**, **api**, etc. After changing **`requirements.txt`**, rebuild: **`docker compose --profile data-science up -d --build ds`**. For Postgres from inside the container, start **`db`** on the same Compose project (e.g. full **`up`**) and keep a root **`.env`** with **`DB_NAME`**, **`DB_USER`**, **`DB_PASSWORD`**, and related variables.

To bring up **everything** (default services **and** Jupyter) in one command:

```bash
docker compose --profile data-science up --build
```

See also the **Docker** section in the root **`README.md`**.

---

## Data
- **Primary source:** PostgreSQL DB via CRUD helpers (`etl/db/scripts/utils/db_helpers.py`)
- **Fallback source:** `../etl/db/data_clean/training_dataset.csv` (used when DB is unavailable locally)
- **Size:** 210,000 rows × 25 columns
- **Synthetic data:** None — confirmed 100% real data (`is_synthetic = False`)

### DB CRUD Integration
The notebook uses `db_helpers.py` (added by the DB developer) to read from the
database when running inside Docker. It connects and reads from four tables:
`campaigns`, `ads`, `audience`, `predictions`.

When running locally without Docker, it gracefully falls back to the CSV file.
The full 210,000 row training dataset is used for EDA and modeling in both cases.

### Key data quality findings
- `budget` is constant (500.0 for all rows) — dropped as a feature
- `engagement_score` has 10,000 missing values (4.76%) — imputed with median
- No duplicate rows
- No other missing values

---

## Notebook Structure (`experiments.ipynb`)

### Cell 1 — Imports
All required libraries imported: pandas, numpy, matplotlib, seaborn, sklearn.

### Cell 2 — DB CRUD Read (Task 5)
Attempts to connect to PostgreSQL via `db_helpers.get_connection()` and reads
all four app tables using `select_all()`. Falls back to CSV if DB is unavailable.

### Cell 3 — Load Data + Basic EDA
- Shape, column types, missing value counts, duplicate check
- Numerical and categorical descriptive statistics

### Cell 4 — Target Definition + Cleaning
- Target variable: `ctr` (Click-Through Rate, continuous float)
- Dropped `budget` (zero variance)
- Imputed `engagement_score` NaNs with median

### Cell 5 — Encoding
- Label-encoded all categorical and boolean columns (16 total)
- All columns verified numeric before modeling

### Cell 6 — EDA Visualizations
- CTR distribution histogram
- CTR vs Conversion Rate scatter plot
- Average CTR by Platform (bar chart)
- Average CTR by Campaign Intent (bar chart)
- Full correlation heatmap (encoded features)
- Top 10 correlations with CTR

### Cell 7 — Baseline Models
Four regression models trained and compared on 80/20 train/test split:

| Model | MAE | R² |
|-------|-----|----|
| Gradient Boosting | 0.086903 | 0.0350 |
| Linear Regression | 0.089423 | 0.0048 |
| Ridge Regression | 0.089423 | 0.0048 |
| Random Forest (100 trees) | 0.093226 | 0.0006 |

**Best model: Gradient Boosting** (R² = 0.035, MAE = 0.087)

**Why R² scores are low:** CTR is a noisy real-world metric influenced by many
factors not captured in the dataset (ad quality, timing, competition, etc.).
Low R² at baseline is expected and normal. Linear models barely outperform a
mean predictor (R² ~0.005), while Gradient Boosting captures some non-linear
patterns (R² 0.035). Further feature engineering and hyperparameter tuning
are recommended as next steps.

### Cell 8 — Feature Importance + Documentation
Random Forest feature importances ranked. Top 15 features identified.
Full assumptions and target variable definition documented inline.

---

## Top 15 Features (by Random Forest importance)
1. `visual_complexity` — numerical score for ad creative complexity
2. `reach_score` — estimated audience reach
3. `duration_days` — campaign length in days
4. `copy_text_length` — character length of ad copy
5. `lead_rate` — ratio of leads generated
6. `conversion_rate` — ratio of conversions
7. `interests` — audience interest category
8. `product_type` — advertised product category
9. `engagement_score` — user engagement signal
10. `career` — audience occupation segment
11. `location` — target geographic region
12. `platform` — ad platform (facebook, instagram, etc.)
13. `campaign_intent` — campaign goal (awareness, leads, traffic, etc.)
14. `age` — audience age group
15. `creative_type` — ad format (video, image, etc.)

---

## Key Findings
- CTR ranges from ~0.001 to ~0.992, median ~0.096
- `data_source` showed suspicious correlation with CTR (0.19) — likely a
  data labeling artifact, excluded from models
- Gradient Boosting is the most promising direction for further tuning
- Visual and reach-related features dominate importance scores

---

## Next Steps
- Fix DB connection for local development (load `.env` correctly in notebook)
- Hyperparameter tuning on Gradient Boosting
- Feature engineering (interaction terms, binning)
- Extract reusable functions into `modeling_related_files.py`