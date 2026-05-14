# App — Streamlit frontend

The user-facing layer of AdVise. Built with **Streamlit**, served from the `front` Docker service on host port **8501**. It talks to the FastAPI backend over HTTP using a thin client (`api_client.py`) — there is no direct database access from the UI.

Source: `AdVise/app/`.

## Layout

```
AdVise/app/
├── app.py                     # Entry point (Streamlit "main" page)
├── api_client.py              # HTTP client to the FastAPI backend
├── ui_components.py           # Shared header / CSS helpers
└── pages/
    ├── 1_Home.py              # Overview cards + sample offline predictions
    ├── 2_Campaign_Input.py    # Campaign + audience + creative form
    └── 3_Prediction_Results.py# Live preview result + offline charts
```

Streamlit's multi-page convention names files `<order>_<title>.py` under `pages/`; the sidebar order matches the numeric prefix.

## Entry point — `app.py`

On boot the page:

1. Sets the global page config (`page_title="AdVise"`, wide layout, custom favicon).
2. Injects shared CSS via `ui_components.inject_global_css()`.
3. Calls `GET /v1/status` through `api_client.get_status()` to render a green **✓ Backend connected** banner — or a yellow "frontend can still be explored with placeholder data" warning if the API is unreachable. The UI degrades gracefully when the backend is down.
4. Renders two side-by-side cards: **User Flow** (the four-step pitch) and **API Readiness** (the four `/v1` endpoints the UI uses).

Module reference:

::: app.app

## Pages

### `pages/1_Home.py` — Home

Overview cards plus an optional table of recent offline predictions if `AdVise/ds/outputs/predictions.csv` (or the `ADVISE_DS_OUTPUTS` directory) is available. Acts as the visual landing page after the user opens the app.

### `pages/2_Campaign_Input.py` — Campaign Input

The form that drives the whole product. It:

- Pulls dropdown vocabularies from `GET /v1/meta/enums` so platforms, intents, age bands, interests, etc. **match the trained models' vocabulary exactly**. If the backend is unreachable, `api_client.get_enums()` falls back to a hard-coded vocabulary that mirrors the API's static enums.
- Accepts up to **3 creatives** (PNG / JPG / JPEG / PDF, ≤ 10 MB each — limits surfaced from `GET /v1/status`).
- Builds a `PredictionPreviewRequest` payload (campaign goal, platform, budget, duration, audience, CTA, optional base64-encoded creative image).
- **On Save:** calls `POST /v1/campaigns/` with the campaign + audience fields. This persists one row in `campaigns` and one in `audience` (single transaction); on success the response carries `campaign_id` and `audience_id`. The page then forwards those IDs into the preview request so the prediction can be linked to the persisted row in `ads` / `predictions`.
- **On Preview:** calls `POST /v1/predictions/preview` and redirects the user to the Results page.

### `pages/3_Prediction_Results.py` — Prediction Results

Renders the response of `POST /v1/predictions/preview`:

- The predicted tier (`low` / `medium` / `high`) and confidence for the resolved `target_metric` (`ctr`, `conversion_rate`, or `reach_score` — chosen by the campaign's intent).
- A ranked list of recommendation rows when the API returns multiple creatives.
- Offline charts read from `ADVISE_DS_OUTPUTS` (the `AdVise/ds/outputs/` folder when that's mounted). These are precomputed batch visuals, not live calls.

## HTTP client — `api_client.py`

A small wrapper around `requests` with three jobs:

| Function | Endpoint | Returns |
|----------|----------|---------|
| `get_status()` | `GET /v1/status` | `(json, status_code)` — feeds the connection banner. |
| `get_enums()` | `GET /v1/meta/enums` | Live JSON, or a static offline fallback. |
| `submit_preview_prediction(payload)` | `POST /v1/predictions/preview` | Live tier / confidence / recommendations. |
| `create_campaign(payload)` | `POST /v1/campaigns/` | Persists `campaigns` + `audience`, returns IDs (or a structured `{"error": ...}` on HTTP failure). |

The base URL is resolved from the environment:

| Variable | Default | When |
|----------|---------|------|
| `API_URL` | `http://localhost:8008` | Set on the `front` service in Compose to `http://back:8000` so containers talk over the Docker network. On the host (e.g. running Streamlit outside Compose), the default points at the published port `8008`. |

## Running

### Inside Compose (production-ish)

```bash
docker compose up --build
# UI:   http://localhost:8501
# API:  http://localhost:8008/docs
```

The `front` container sets `API_URL=http://back:8000`. The UI is available even if `etl_db` is mid-run (the connection banner just turns yellow until `back` is healthy).

### Locally for development

```bash
cd AdVise/app
pip install -r requirements.txt
export API_URL=http://localhost:8008   # or wherever your back service is exposed
streamlit run app.py
```

Streamlit auto-reloads on file save; the multi-page sidebar is built from `pages/`.

## Design notes

- **The UI never queries Postgres directly.** Every dropdown, save, and prediction goes through `/v1/*` endpoints. This keeps secrets and schema knowledge on the API side, where they belong.
- **Graceful degradation.** If the API is down, the connection banner warns the user but the form still renders (using the offline enum fallback). Submitting is what fails, not page navigation.
- **Single outcome per preview.** The Results page does **not** show CTR + conversion + reach at the same time — the API returns exactly one tier per request, picked by the campaign's intent. This matches the contract on the [API](api.md) and [Data Science](ds-models.md) pages.

## Related

- [API](api.md) for the endpoints the UI calls.
- [Data Science](ds-models.md) for what the tier predictions actually mean.
- [Orchestration](orchestration.md) for how the optional Prefect-wrapped creative extraction is wired in behind `POST /v1/predictions/preview`.
