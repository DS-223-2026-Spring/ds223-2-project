# API Assumptions and Pending Dependencies

## Current API Status
The backend currently includes:
- FastAPI project with a clean folder structure
- health endpoint
- dummy CRUD endpoints for campaigns
- placeholder request/response schemas for campaigns
- Swagger/OpenAPI documentation generated automatically by FastAPI

The current implementation is intended for MVP backend setup and local testing.

## API Assumptions
The current backend implementation is based on the following assumptions:

1. The `campaigns` resource is used as a representative example for CRUD operations.
2. Campaign data is currently stored only in memory using dummy storage, not in a database.
3. The current campaign schema is simplified and only includes:
   - name
   - budget
4. The backend assumes that frontend will communicate with the API through HTTP requests.
5. The current API structure is based on MVP-level planning and may be expanded later with resources such as:
   - creatives
   - analyses
   - recommendations
6. Swagger/OpenAPI documentation is used for local development and endpoint testing.
7. The current implementation is focused on backend structure and API behavior, not final business logic.

## Pending Dependencies
The following parts are still dependent on other team members or future implementation work:

1. Product Manager
   - confirmation of final MVP flow
   - confirmation of final input/output requirements
   - confirmation of which resources are required in the first release

2. Database Developer
   - final database schema
   - table definitions and relationships
   - database integration for persistent storage instead of dummy in-memory storage

3. Frontend Developer
   - final frontend forms and expected request payloads
   - integration of backend endpoints into the user interface
   - confirmation of what response format is most useful for frontend display

4. Data Scientist
   - final prediction logic
   - model input requirements
   - model output format
   - recommendation logic for campaign improvement and best creative selection

## Expected Future API Extensions
The backend will likely be extended with additional resources such as:
- creatives
- analyses
- predictions
- recommendations

These will be implemented after team alignment on product flow, database design, and model requirements.

## Notes
This document reflects the current state of the backend during the early MVP development stage and is intended to clarify what is already implemented versus what still depends on team coordination.
