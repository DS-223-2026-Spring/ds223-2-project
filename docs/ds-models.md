# Data science — training and live inference

## Layout (`AdVise/ds/`)

| Artifact / module | Role |
|-------------------|------|
| **`train.py`** | Trains per-metric tier classifiers; writes **`models/model_<metric>.pkl`**, **`encoders_<metric>.pkl`**, **`feature_cols_<metric>.pkl`**. |
| **`predict.py`** | Batch scores data; CSV output under **`outputs/`**; optional **`write_to_db`** updates **`predictions`**. |
| **`modeling_related_files.py`** | Shared **`FEATURE_COLS`**, **`engineer_features`**, loaders — training and API inference must stay aligned. |
| **`models/*.pkl`** | Joblib bundles; in Compose, **`./AdVise/ds/models`** is mounted read-only at **`/api/ds_models`** on **`back`**. |

## Live API preview (`/v1/predictions/preview`)

**`AdVise/api/prediction_models.py`** loads the same triple (`model_<metric>.pkl`, `encoders_<metric>.pkl`, `feature_cols_<metric>.pkl`) for the resolved **`target_metric`** (from campaign intent). It derives engineered fields (e.g. **`budget_per_day`**, **`engagement_per_day`**, **`copy_length_bucket`**, **`multi_metric_mean`**) when they are absent so the feature vector matches training.

**Env:** **`ADVISE_DS_MODELS`** (default under **`AdVise/api/ds_models`** if unset) must contain the files for that metric.

## Sklearn / joblib versions

Pickles are sensitive to **scikit-learn** version mismatches. Align **`AdVise/api/requirements.txt`** with the environment used to run **`train.py`** when you see unpickle warnings.

## Related docs

- [Prefect orchestration](api/prefect-orchestration.md) — optional creative extraction path.
- [ETL](etl.md) — **`training_dataset`** build.
