# Streamlit app

- [Home](index.md) · [API](api.md) · [API v1 examples](api/v1-endpoints.md) · [Project structure](project-structure.md)

::: app.app

## Pages (`AdVise/app/pages/`)

| Page | File | Role |
|------|------|------|
| Home | **`1_Home.py`** | Overview cards; optional sample from **`ds_outputs`** / **`predictions.csv`**. |
| Campaign Input | **`2_Campaign_Input.py`** | Builds **`PredictionPreviewRequest`**; **`POST /v1/campaigns/`** then preview with **`campaign_id`** / **`ad_id`** when saved. |
| Prediction Results | **`3_Prediction_Results.py`** | Live preview results + offline charts from **`ADVISE_DS_OUTPUTS`**. |

## HTTP client

**`api_client.py`** — **`API_URL`** (Compose: **`http://back:8000`**; host dev: often **`http://localhost:8008`**).
