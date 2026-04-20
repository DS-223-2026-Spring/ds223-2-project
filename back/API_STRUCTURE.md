# Backend API Structure Proposal

## Purpose
This document is a first backend API structure draft for team discussion with the Product Manager and Database Developer.

## Project Flow
The main backend flow of the project is expected to be:

1. User uploads 1–3 creatives
2. User enters campaign details
3. Backend processes the input
4. Backend runs campaign analysis and prediction logic
5. Backend returns results and recommendations

## Proposed Resources

### 1. Campaigns
Represents the campaign information entered by the user.

Possible data:
- budget
- product type
- audience metrics
- campaign intent
- platform
- campaign duration
- CTA type
- discount
- season or month

Suggested endpoints:
- POST /campaigns
- GET /campaigns/{id}

### 2. Creatives
Represents uploaded images or short videos and their extracted features.

Possible data:
- file name
- file type
- upload path
- aspect ratio
- brightness
- text amount
- number of faces
- dominant colors

Suggested endpoints:
- POST /creatives/upload
- GET /creatives/{id}

### 3. Analyses
Represents the main campaign analysis result. It combines campaign input and creative data, then returns prediction output.

Possible data:
- campaign id
- creative ids
- predicted result
- best creative
- summary

Suggested endpoints:
- POST /analyses
- GET /analyses/{id}

### 4. Recommendations
Represents improvement suggestions for the campaign and creative selection.

Possible data:
- best creative id
- recommendation text
- suggested improvement
- explanation

Suggested endpoints:
- GET /recommendations/{analysis_id}

### 5. Health
Represents backend running status.

Suggested endpoints:
- GET /health

## Notes for Team Discussion
- PM should confirm whether this matches the MVP flow and user screens
- DB Developer should confirm whether these names fit the database design
- Frontend can use these endpoints to submit inputs and receive results
- Resource names can still be adjusted after team discussion
