"""
Prefect-backed creative extraction for the FastAPI app.

Runs a synchronous local flow/task when ``POST /v1/predictions/preview`` receives
``creative_image_base64``. Mirrors DS pipeline semantics (retries).

Set ``ADVISE_SKIP_PREFECT_CREATIVE=1`` to call ``creative_extract`` directly
without Prefect (debug only).
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

from prefect import flow, task

log = logging.getLogger(__name__)


def _extract_plain(image_path: str) -> Dict[str, Any]:
    from creative_extract import extract_creative_features

    return extract_creative_features(image_path)


@task(name="APICreativeExtract", retries=2, retry_delay_seconds=5)
def api_creative_extract_task(image_path: str) -> Dict[str, Any]:
    return _extract_plain(image_path)


@flow(name="api-creative-extraction-preview")
def api_creative_extraction_flow(image_path: str) -> Dict[str, Any]:
    """
    Blocking Prefect execution suitable for synchronous FastAPI handlers.
    """
    return api_creative_extract_task(image_path)


def extract_creative_for_preview(image_path: str) -> Dict[str, Any]:
    """
    Run extraction via Prefect unless ``ADVISE_SKIP_PREFECT_CREATIVE`` bypass is set.
    """
    if os.environ.get("ADVISE_SKIP_PREFECT_CREATIVE", "").lower() in (
        "1",
        "true",
        "yes",
    ):
        log.debug("ADVISE_SKIP_PREFECT_CREATIVE set; skipping Prefect wrapper")
        return _extract_plain(image_path)
    return api_creative_extraction_flow(image_path)
