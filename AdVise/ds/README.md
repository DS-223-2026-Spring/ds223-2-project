# AdVise - Data Science
## Milestone 3: Final Model & Pipeline

---

## What's in this folder

| File / Folder               | Description                                                         |
|-----------------------------|---------------------------------------------------------------------|
| `train.py`                  | Trains the final model and saves artifacts to `models/`             |
| `predict.py`                | Loads model, runs predictions, saves results to `outputs/`          |
| `creative_extract.py`       | Extracts features from ad creative images                           |
| `modeling_related_files.py` | Shared feature definitions, preprocessing helpers, artifact loaders |
| `pipeline_docs.md`          | Full pipeline documentation: features, models tried, results        |
| `experiments.ipynb`         | Milestone 2 EDA and baseline model experiments                      |
| `models/`                   | Saved model artifacts (`.pkl` files, git-ignored)                   |
| `outputs/`                  | Prediction output CSVs (git-ignored)                                |
| `requirements.txt`          | Required packages                                                   |

---

## How to run

Make sure you are inside the `ds/` folder and your virtual environment is active.

**1. Train the model:**
```bash
python train.py
```
Reads data from DB (falls back to CSV if DB is unavailable), trains a
Random Forest Classifier, and saves `model.pkl`, `encoders.pkl`,
and `feature_cols.pkl` to `models/`.

**2. Run predictions:**
```bash
python predict.py
```
Loads the saved model, runs predictions on all campaign data, and saves
`outputs/predictions.csv` with columns:
- `predicted_ctr_tier` — Low / Medium / High
- `confidence_score` — probability of the predicted class (0–1)
- `performance_segment` — human-readable recommendation

**3. Extract creative features from an image:**
```bash
python creative_extract.py --image path/to/image.jpg
```
Returns `creative_type`, `aspect_ratio`, `visual_complexity`, `has_person`.
Designed to be imported by the orchestration layer:
```python
from creative_extract import extract_creative_features
features = extract_creative_features("path/to/image.jpg")
```

---

## Model summary

| Model | Type | Metric | Score |
|---|---|---|---|
| Linear Regression (M2) | Regression | R² | 0.035 |
| Ridge Regression (M2) | Regression | R² | 0.035 |
| Random Forest Regressor (M2) | Regression | R² | 0.035 |
| Gradient Boosting Regressor (M2) | Regression | R² | 0.035 |
| Gradient Boosting Classifier (M3) | Classification | Accuracy | 0.377 |
| **Random Forest Classifier (M3)** | **Classification** | **Accuracy** | **0.377** |

Target: CTR binned into 3 equal-frequency tiers (Low / Medium / High).
See `pipeline_docs.md` for full details.

---

## Requirements
- pandas
- numpy
- scikit-learn
- joblib
- pillow
- opencv-python

See `requirements.txt` for the full list of dependencies.

Install all with:
```bash
pip install -r requirements.txt
```