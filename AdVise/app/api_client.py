import os

import requests

# In Docker Compose, `front` sets API_URL=http://back:8000. On the host, mapped port is 8008.
API_BASE_URL = os.environ.get("API_URL", "http://localhost:8008").rstrip("/")


def get_status():
    try:
        response = requests.get(f"{API_BASE_URL}/v1/status", timeout=3)
        return response.json(), response.status_code
    except requests.exceptions.RequestException:
        return None, None


def get_enums():
    try:
        response = requests.get(f"{API_BASE_URL}/v1/meta/enums", timeout=3)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass

    # Offline fallback — same vocabulary as API ``_static_enums`` / ``training_vocab`` pools.
    return {
        "platforms": ["facebook", "instagram", "google", "tiktok", "youtube"],
        "campaign_intents": ["sales", "awareness", "traffic", "leads", "engagement"],
        "cta_types": ["buy_now", "learn_more", "sign_up", "go_to_page"],
        "audience_temperature": ["cold", "warm", "hot"],
        "devices": ["mobile", "desktop", "tablet"],
        "customer_types": ["new", "returning"],
        "product_types": [
            "electronics",
            "fashion",
            "food",
            "beauty",
            "fitness",
            "finance",
            "travel",
            "education",
            "home",
            "software",
        ],
        "regions": ["US", "UK", "India", "Canada", "Germany", "France", "Armenia"],
        "age_bands": ["18-24", "25-34", "35-44", "45-54", "55+"],
    }


def submit_preview_prediction(payload: dict):
    """
    POST /v1/predictions/preview with a JSON body (PredictionPreviewRequest).
    Include optional ``creative_image_base64`` (first creative) so the API runs image extraction.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/v1/predictions/preview",
            json=payload,
            timeout=60,
        )
        return response.json(), response.status_code
    except requests.exceptions.RequestException:
        return None, None
