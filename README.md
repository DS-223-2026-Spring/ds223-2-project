# AdVise — Predict Before You Launch

AdVise is an AI-powered marketing analytics platform that predicts the potential success of advertising campaigns before they go live. By analyzing creatives, audience details, campaign goals, and budget inputs, AdVise provides performance forecasts such as predicted CTR, conversion rate, engagement, and reach.

The platform helps marketers identify the strongest creatives, optimize campaign strategy early, and reduce wasted ad spend through data-driven insights and machine learning predictions.

## Branches

This repository contains the following branches:

- **main**: The primary branch containing the complete project setup.
<!-- - **db-setup**: Contains:
  - the database setup and configuration.
  - ETL (Extract, Transform, Load) process implementation

- **backend:** Contains the backend with `FastAPI`.
- **front**: Contains the Streamlit frontend application. -->
- **gh-pages:** Deploying the documentation.
- **jupyter-notebook**: Contains the Jupyter Notebook container setup.

## Dev Container (optional)

1. Install the **Dev Containers** extension in VS Code.
2. From the repository root, run `docker compose up --build` to build the images.
3. Open the **Dev Containers** command palette action and pick **Reopen in Container** when you want a containerized dev environment.
4. Select a folder to work in: repository root, `AdVise/app/`, `AdVise/api/`, or `AdVise/ds/`, depending on your role.



## Presentation 

**Documentation (MkDocs / GitHub Pages):** [https://ds-223-2026-spring.github.io/ds223-2-project/](https://ds-223-2026-spring.github.io/ds223-2-project/) — enable **Pages** in the repo settings if this 404s; you can always run **`mkdocs serve`** locally. **Source:** [github.com/DS-223-2026-Spring/ds223-2-project](https://github.com/DS-223-2026-Spring/ds223-2-project).

## Installation

Before getting started, ensure you have the following prerequisites installed:

1. Clone the repository:
   ```bash
   git clone https://github.com/DS-223-2026-Spring/ds223-2-project.git
   cd ds223-2-project
   ```

2. Create a **`.env`** file in the repository root. There is no committed template; copy the block under [Environment variables](#db) into a new file named `.env` and set **`DB_USER`**, **`DB_PASSWORD`**, and **`DB_NAME`** (default **`marketing_db`**). For Compose, **`back`** derives **`DATABASE_URL`** from those variables. Do not commit **`.env`**.

3. Build and start the Docker containers from the repository root:
   ```bash
   docker compose up --build
   ```

   **ETL:** keep the two source CSVs under **`AdVise/etl/db/data_raw/`** (`tech_advertising_campaigns_dataset.csv`, `marketing_campaign_dataset.csv`). The **`etl_db`** service runs once after Postgres is healthy (schema + **`preprocessing.py`** + **`load_to_db.py`** into **`training_dataset`**). The **API** (Compose service **`back`**) starts only after **`etl_db` exits successfully**; if the pipeline fails, **`back`** and **`front`** will not start.

For **`back`**, Docker Compose builds **`DATABASE_URL`** from **`DB_USER`**, **`DB_PASSWORD`**, and **`DB_NAME`** so credentials always match the **`db`** service (`postgresql+psycopg2://…@db:5432/…`). Running the API **outside** Compose still requires **`DATABASE_URL`** yourself; URL-encode special characters in the password (RFC 3986).

## Access the Application

After running `docker compose up --build`, you can access each component of the application at the following URLs:


- **Streamlit Frontend:** http://localhost:8501 The main interface for managing employees, built with Streamlit. Use this to add, view, update, and delete employee records.
- **FastAPI Backend**: [http://localhost:8008](http://localhost:8008)  
  The backend API where requests are processed. You can use tools like [Swagger UI](http://localhost:8008/docs) (provided by FastAPI) to explore the API endpoints and their details.

- **PgAdmin** (optional): `http://localhost:${PGADMIN_PORT:-5050}`  

  A graphical tool for PostgreSQL, which allows you to view and manage the database. Login using the credentials set in the `.env` file:
  
  - **Email**: Value of `PGADMIN_EMAIL` in your `.env` file
  - **Password**: Value of `PGADMIN_PASSWORD` in your `.env` file

> Note: Ensure Docker is running, and you have created **`.env`** (see [Environment variables](#db)) with values that match your setup.



## Project Structure

Here’s an overview of the project’s file structure:

```bash
.
├── LICENSE
├── README.md
├── .github/             # CI workflows
├── .env                 # Your local environment (create yourself; not committed)
├── docker-compose.yml
├── mkdocs.yaml
├── AdVise/              # Product package
│   ├── __init__.py
│   ├── api/             # FastAPI backend
│   │   ├── Dockerfile
│   │   ├── main.py      # Wires route groups
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schema.py
│   │   ├── routes/      # route1, route2, routen, …
│   │   └── requirements.txt
│   ├── app/             # Streamlit frontend
│   │   ├── Dockerfile
│   │   ├── app.py
│   │   ├── pages/
│   │   └── requirements.txt
│   ├── ds/              # Data science (Jupyter, modeling)
│   │   ├── Dockerfile
│   │   ├── experiments.ipynb
│   │   ├── modeling_related_files.py
│   │   └── requirements.txt
│   └── etl/             # DB / marketing ETL (kept)
│       ├── requirements.txt
│       └── db/
│           ├── Dockerfile
│           ├── data_raw/  # source CSVs (in repo) + generated paths
│           ├── data_clean/  # build output (gitignored)
│           ├── sql/
│           └── scripts/
└── docs/
    ├── imgs/
    ├── index.html
    └── (Markdown pages, MkDocs)
```

## Docker

`docker compose up` brings up the following services (order matters for **`back`** / **`front`**):

1. **PostgreSQL** – primary database
2. **pgAdmin** – database administration UI
3. **etl_db** – one-shot ETL (schema, preprocessing, `load_to_db` → **`training_dataset`** only). Uses raw CSVs in `AdVise/etl/db/data_raw/`. Re-running **`up`** truncates and reloads the offline training table. **`back`** waits until **`etl_db` finishes successfully.**
4. **back** – FastAPI backend (`AdVise/api/`)
5. **front** – Streamlit (`AdVise/app/`; Compose service name **`front`**)
6. **ds** (optional) – Jupyter: `docker compose --profile data-science up -d --build ds` — http://localhost:8888

## Prerequisites

Before running this setup, ensure Docker and Docker Compose are installed on your system.


- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)


## DB

- Access pgAdmin for PostgreSQL management: use `http://localhost:<PGADMIN_PORT>` (default **5050** unless you set **`PGADMIN_PORT`** in `.env`).
    - username: admin@admin.com 
    - password: admin
    - When running for the first time, you must create a server. Configure it as shown in the below image (Password is blurred it should be `password`.)
    ![Server Setup](docs/imgs/pgadmin_setup.png)

### Environment variables

Create a **`.env`** file in the root directory (this file is gitignored). Use variable names and layout like below; substitute your own user and password.

```env
# Canonical credentials for the Compose `db` service.
# The `back` service DATABASE_URL is derived inside docker-compose.yml from DB_* (no drift).
DB_USER=<your_database_user>
DB_PASSWORD=<your_database_password>
DB_NAME=marketing_db

# Optional: explicit URL for running FastAPI on the host only (not required for Compose `back`)
# DATABASE_URL=postgresql+psycopg2://<user>:<url_encoded_password>@localhost:5432/marketing_db

# pgAdmin (compose host port; default 5050 if unset)
# PGADMIN_PORT=5050

PGADMIN_EMAIL=admin@admin.com
PGADMIN_PASSWORD=admin
```

Compose sets **`ADVISE_PREFECT_AVAILABLE=true`** on **`back`** so **`GET /v1/status`** reflects that preview creative extraction uses Prefect (see **`AdVise/api/creative_prefect.py`**). Override in **`.env`** only if you need **`false`**.

Optional: **`ADVISE_SKIP_PREFECT_CREATIVE=true`** on **`back`** skips the Prefect wrapper for **`creative_image_base64`** (debug).

Do not commit **`.env`** or real secrets.

Structured **v1** HTTP examples: [`docs/api/v1-endpoints.md`](docs/api/v1-endpoints.md). Refresh **`docs/api/openapi.json`** with **`python3 scripts/export_openapi.py`** after route changes.



## Data modeling and ETL

Schema diagrams and notes also live under **`docs/`** (for example `docs/etl.md` and `docs/imgs/star_schema.png`). The marketing pipeline lives under **`AdVise/etl/db`**, and the Compose service **`etl_db`** is part of the default stack. See **`docs/etl.md`**.

## API

### Tier models and creative extraction

- **`GET /v1/meta/enums`** pulls dropdown values from **`training_dataset`** so the Streamlit form matches the CSV/ETL vocabulary models were trained on.
- **`POST /v1/predictions/preview`** loads joblib artifacts from **`AdVise/ds/models`** mounted as **`/api/ds_models`** in Compose. Prefer per-metric files from **`python AdVise/ds/train.py`** (`model_ctr.pkl`, `encoders_ctr.pkl`, …). A legacy trio **`model.pkl` / `encoders.pkl` / `feature_cols.pkl`** is used **only** when the resolved target metric matches **`ADVISE_LEGACY_MODEL_ONLY_FOR`** (default **`ctr`**). Set that env on **`back`** if your single bundle was trained for another target.
- **Git LFS:** **`AdVise/ds/models/*.pkl`** are tracked with [Git LFS](https://git-lfs.github.com/) (some files exceed GitHub’s plain-file size limit). Install the **git-lfs** CLI, run **`git lfs install`** once per machine, then **`git clone`** / **`git pull`** as usual—LFS downloads real binaries instead of stub pointers when configured. Without Git LFS, pushes of new **`*.pkl`** files may fail.
- **`creative_image_base64`** on the preview request runs **`AdVise/ds/creative_extract.py`** via a **Prefect** flow (**`creative_prefect.py`** → **`api-creative-extraction-preview`**) inside **`back`** (Compose bind-mount). Set **`ADVISE_SKIP_PREFECT_CREATIVE=1`** to bypass Prefect for debugging. Rebuild **`back`** after changing **`AdVise/api/requirements.txt`** (adds prefect, numpy, pandas, scikit-learn, joblib, OpenCV headless, Pillow).
- Batch files such as **`AdVise/ds/outputs/predictions.csv`** are not used for live HTTP inference; they come from offline scoring pipelines.


### Features

- **Add New Employee**: Enter details like first name, last name, email, department, position, and salary to add a new employee.
- **Get Employee by ID**: Retrieve an employee’s information using their unique ID.
- **Update Salary**: Update the salary of an existing employee by providing their ID and the new salary.
- **Delete Employee**: Remove an employee record from the system using their ID.

The FastAPI app under **`AdVise/api/`** (with **`routes/`** for route groups) connects HTTP endpoints to PostgreSQL; you can create, read, update, and delete employees by id.

### Requests

- `POST /employees/: Create a new employee. Requests`

- `GET /employees/{employee_id}: Retrieve employee details by ID. Requests`

- `PUT /employees/{employee_id}: Update an employee’s salary by ID. Requests`

- `DELETE /employees/{employee_id}: Delete an employee by ID.`


## Web Application

The Streamlit UI is the Compose service **`front`** (code in **`AdVise/app/`**).

To Open the web app visit: [here](http://localhost:8501/)


### Dockerfile

```bash
# Dockerfile

# pull the official docker image
FROM python:3.12-slim-bullseye

RUN apt-get update && apt-get install -y \
    build-essential libpq-dev libfreetype6-dev libpng-dev libjpeg-dev \
    libblas-dev liblapack-dev gfortran \
    && rm -rf /var/lib/apt/lists/*

# set work directory
WORKDIR /app


# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the contents of the AdVise/app package to /app in the container
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.headless=true", "--server.runOnSave=true"] 
```


### Service

```yaml
  front:
    container_name: front
    build:
      context: ./AdVise/app
      dockerfile: Dockerfile
    ports:
      - 8501:8501
    environment:
      - API_URL=http://back:8000
    depends_on:
      - back
```

## Documentation in this repo

1. Install [MkDocs](https://www.mkdocs.org/) tooling (from the repository root):
   ```bash
   pip install -r docs/requirements.txt
   pip install -r AdVise/api/requirements.txt
   ```
2. Live preview:
   ```bash
   mkdocs serve
   ```
   Open the URL shown in the terminal (usually `http://127.0.0.1:8000`).
3. Static build output is written to **`site/`** (ignored by git):
   ```bash
   mkdocs build
   ```

- **`mkdocs.yaml`** – site name, navigation, Material theme, and **mkdocstrings** for the **`api`** and **`app`** packages under **`AdVise/`** (install **`AdVise/api/requirements.txt`** for doc builds that import the FastAPI app).
- **`docs/index.md`** – MkDocs home; other pages are linked from there and from the nav in `mkdocs.yaml`.
- **`docs/index.html`** – optional static HTML (open the file in a browser without MkDocs); it is not copied into `site/` when `index.md` is present (that is normal).
- **`docs/imgs/`** – images referenced from the Markdown files.

## CI

The workflow in **`.github/workflows/ci.yaml`** runs on pushes and pull requests to `main` and `master`:

- **docker-build** – creates a throwaway **`.env`** in the job (placeholders for Compose), validates Compose, and builds **back**, **front**, and **etl_db** images (ETL is built but not executed in CI).
- **mkdocs** – installs **docs/requirements.txt**, **AdVise/api/requirements.txt**, and runs **`mkdocs build`**.