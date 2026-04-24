# Frontend Data Needs from Backend

## Purpose

The frontend will use backend data to display campaign prediction results, creative comparisons, and recommendations in the Streamlit application.

## 1. Campaign Submission Data

The frontend needs to send campaign input data to the backend.

Required fields:

- budget
- platform
- campaign intent
- campaign duration
- audience temperature
- CTA type
- uploaded creatives
- product type
- region
- age group
- customer type
- gender

## 2. Creative Upload Data

The frontend needs backend support for uploading 1–3 creatives.

Required backend response:

- creative ID
- file name
- file type
- upload status
- extracted creative features, if available

Example creative features:

- brightness
- text density
- aspect ratio
- number of faces
- dominant colors

## 3. Prediction Output Data

The frontend needs prediction results from the model through the backend.

Expected fields:

- predicted CTR
- predicted conversion rate
- predicted reach score
- predicted lead rate
- predicted engagement score
- creative score
- brand consistency score
- best creative ID or name

## 4. Creative Comparison Data

The frontend needs data to compare uploaded creatives.

Expected fields:

- creative name
- creative score
- predicted performance metric
- strengths
- weaknesses
- ranking position

## 5. Recommendation Data

The frontend needs backend-generated recommendation text.

Expected fields:

- recommendation ID
- recommendation message
- related creative
- recommendation type

Example recommendation types:

- improve CTA
- reduce text density
- improve brightness
- adjust audience
- change budget allocation

## 6. Dashboard Data

The frontend will need summarized dashboard data.

Expected fields:

- total campaigns analyzed
- average predicted CTR
- average predicted conversion rate
- best performing platform
- campaign history
- recent prediction results

## 7. API Endpoints Needed Later

Possible backend endpoints:

- POST `/campaigns/submit`
- POST `/creatives/upload`
- GET `/campaigns/{campaign_id}/prediction`
- GET `/campaigns/{campaign_id}/recommendations`
- GET `/campaigns/history`
- GET `/dashboard/summary`

## Notes

At the current stage, the frontend only contains placeholders. These data requirements will help the backend prepare API responses that can later be connected to the Streamlit interface.