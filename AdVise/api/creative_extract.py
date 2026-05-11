"""
creative_extract.py
AdVise — Milestone 3
Extracts creative features from an uploaded image file.
Returns a dict that can be fed directly into the prediction pipeline.

Usage (standalone test):
    python creative_extract.py --image path/to/image.jpg

Imported by orchestration:
    from creative_extract import extract_creative_features
    features = extract_creative_features("path/to/image.jpg")
"""

import os
import argparse
import numpy as np

from PIL import Image
import cv2

# Path to OpenCV's built-in haar cascade for face detection
HAAR_CASCADE_PATH = os.path.join(
    cv2.data.haarcascades,
    "haarcascade_frontalface_default.xml"
)


def get_creative_type(image_path: str) -> str:
    """
    Detect creative type based on file extension.
    MVP: only images supported. Video is skipped.
    """
    ext = os.path.splitext(image_path)[1].lower()
    video_extensions = [".mp4", ".mov", ".avi", ".mkv", ".webm"]
    if ext in video_extensions:
        return "video"
    return "image"


def get_aspect_ratio(img: Image.Image) -> str:
    """
    Calculate aspect ratio from image dimensions.
    Returns a string like '4:5', '16:9', '1:1', etc.
    Snaps to the closest known standard ratio.
    """
    width, height = img.size
    raw = width / height

    # Standard ratios used in advertising
    standard_ratios = {
        "1:1":  1.0,
        "4:5":  0.8,
        "9:16": 0.5625,
        "16:9": 1.7778,
        "4:3":  1.3333,
    }

    # Find the closest standard ratio
    closest = min(standard_ratios, key=lambda r: abs(standard_ratios[r] - raw))
    return closest


def get_visual_complexity(img: Image.Image) -> float:
    """
    Estimate visual complexity using edge density.
    Converts image to grayscale, applies Canny edge detector,
    and returns the fraction of edge pixels as a 0-1 float.
    Higher = more complex / busier image.
    """
    # Convert PIL image to OpenCV format (numpy array, grayscale)
    img_gray = np.array(img.convert("L"))

    # Apply Canny edge detection
    edges = cv2.Canny(img_gray, threshold1=50, threshold2=150)

    # Complexity = fraction of pixels that are edges
    complexity = float(np.sum(edges > 0)) / float(edges.size)

    # Clip to 0-1 range and round
    return round(min(max(complexity, 0.0), 1.0), 4)


def get_has_person(img: Image.Image) -> bool:
    """
    Detect whether the image contains a person (face detection).
    Uses OpenCV Haar Cascade face detector.
    Returns True if at least one face is detected.
    """
    # Load the cascade classifier
    face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)

    # Convert PIL image to OpenCV grayscale
    img_gray = np.array(img.convert("L"))

    # Detect faces
    faces = face_cascade.detectMultiScale(
        img_gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
    )

    return len(faces) > 0


def extract_creative_features(image_path: str) -> dict:
    """
    Main function. Takes a path to an image file and returns a dict
    with all creative features needed by the prediction pipeline.

    Args:
        image_path: Path to the image file (jpg, png, webp, etc.)

    Returns:
        dict with keys:
            - creative_type     : str   — 'image' or 'video'
            - aspect_ratio      : str   — e.g. '4:5', '16:9', '1:1'
            - visual_complexity : float — 0.0 to 1.0
            - has_person        : bool  — True if a face is detected

    Raises:
        FileNotFoundError: if the image path does not exist
        ValueError:        if the file is a video (MVP skips video)
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Detect creative type first
    creative_type = get_creative_type(image_path)

    if creative_type == "video":
        raise ValueError(
            f"Video files are not supported in MVP. "
            f"Got: {image_path}. Only image files are processed."
        )

    # Load image with Pillow
    img = Image.open(image_path).convert("RGB")

    # Extract all features
    aspect_ratio      = get_aspect_ratio(img)
    visual_complexity = get_visual_complexity(img)
    has_person        = get_has_person(img)

    features = {
        "creative_type":     creative_type,
        "aspect_ratio":      aspect_ratio,
        "visual_complexity": visual_complexity,
        "has_person":        has_person,
    }

    return features


# ──────────────────────────────────────────────────────────────────────────────
# MAIN — for standalone testing
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--image",
        required=True,
        help="Path to the image file to extract features from",
    )
    args = parser.parse_args()

    print(f"Extracting features from: {args.image}")
    features = extract_creative_features(args.image)

    print("\nExtracted features:")
    for key, value in features.items():
        print(f"  {key:20s}: {value}")