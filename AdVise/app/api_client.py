import requests

API_BASE_URL = "http://localhost:8000"


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

    return {
        "platforms": ["Instagram", "Facebook", "TikTok", "Google Ads"],
        "campaign_intents": ["Sales", "Awareness", "Traffic", "Leads", "Engagement"],
        "cta_types": ["Buy Now", "Sign Up", "Learn More", "Go to Page"],
        "audience_temperatures": ["Cold", "Warm", "Hot"],
        "devices": ["Mobile", "Desktop", "Tablet"],
        "customer_types": ["New", "Returning"],
    }


def submit_preview_prediction(payload, files):
    try:
        response = requests.post(
            f"{API_BASE_URL}/v1/predictions/preview",
            data=payload,
            files=files,
            timeout=30,
        )
        return response.json(), response.status_code
    except requests.exceptions.RequestException:
        return None, None