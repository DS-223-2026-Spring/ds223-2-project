from prefect import task, flow
from creative_extract import extract_creative_features
import sys
import os
from dotenv import load_dotenv
import json

# Load environment variables dynamically
load_dotenv()

@task(name="Extract Image Features", retries=2, retry_delay_seconds=5)
def task_extract_features(image_path: str) -> dict:
    features = extract_creative_features(image_path)
    return features

@task(name="Save Features to DB")
def task_save_features(campaign_id: int, features: dict):
    # RELATIVE PATH: Dynamically find the path to your db_helpers file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    utils_path = os.path.join(current_dir, "..", "etl", "db", "scripts", "utils")
    sys.path.append(utils_path)
    
    from db_helpers import get_connection
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE ads
        SET creative_type = %s, aspect_ratio = %s, visual_complexity = %s, has_person = %s
        WHERE campaign_id = %s
    """, (features["creative_type"], features["aspect_ratio"], float(features["visual_complexity"]), bool(features["has_person"]), campaign_id))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Successfully saved features for campaign {campaign_id} to DB.")

@flow(name="Creative Feature Extraction Pipeline")
def process_new_creative_flow(image_path: str, campaign_id: int):
    """Main workflow triggered when a user uploads an image."""
    print(f"Starting pipeline for image: {image_path}")
    
    # Step 1: Extract
    extracted_data = task_extract_features(image_path)
    
    # Step 2: Save to Database (Active for submission)
    task_save_features(campaign_id, extracted_data)
    
    # Step 3: Save to JSON (Commented out fallback)
    # print("Bypassing database. Saving to local JSON file...")
    # json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "my_extracted_features.json")
    # with open(json_path, "w", encoding="utf-8") as f:
    #     json.dump(extracted_data, f, indent=4)
        
    return "Pipeline completed successfully!"

if __name__ == "__main__":
    # RELATIVE PATH FOR TEST IMAGE: 
    # This expects a file named 'test_image.jpg' in the exact same folder as this script.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_image_path = os.path.join(current_dir, "test_image.jpg")
    
    # 1. Standard local run
    process_new_creative_flow(test_image_path, campaign_id=101)
    
    # 2. DEPLOYMENT RUN (Uncomment this line below to create a deployment)
    process_new_creative_flow.serve(name="creative-pipeline-deployment")