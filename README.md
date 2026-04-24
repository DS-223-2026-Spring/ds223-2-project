# AdVise — Dockerized PostgreSQL, pgAdmin, FastAPI, Streamlit, and DS

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

**Follow to [this](https://hovhannisyan91.github.io/pythonmicroservicedesign/) link.**

## Installation

Before getting started, ensure you have the following prerequisites installed:

1. Clone the repository:
   ```bash
   git clone https://github.com/DS-223-2026-Spring/ds223-2-project.git
   cd ds223-2-project
   ```

2. Create a **`.env`** file in the repository root. There is no committed template; copy the block under [Environment variables](#db) into a new file named `.env` and set **`DB_USER`**, **`DB_PASSWORD`**, and a **`DATABASE_URL`** whose database name matches **`DB_NAME`** (default **`marketing_db`**). Do not commit **`.env`**.

3. Build and start the Docker containers from the repository root:
   ```bash
   docker compose up --build
   ```

   **ETL:** keep the two source CSVs under **`AdVise/etl/db/data_raw/`** (`tech_advertising_campaigns_dataset.csv`, `marketing_campaign_dataset.csv`). The **`etl_db`** service runs once after Postgres is healthy (schema + **`preprocessing.py`** + **`load_to_db.py`** into **`training_dataset`**). The **API** starts only after **`etl_db` exits successfully**; if the pipeline fails, **`api`** and **`app`** will not start.

## Access the Application

After running `docker compose up --build`, you can access each component of the application at the following URLs:


- **Streamlit Frontend:** http://localhost:8501 The main interface for managing employees, built with Streamlit. Use this to add, view, update, and delete employee records.
- **FastAPI Backend**: [http://localhost:8008](http://localhost:8008)  
  The backend API where requests are processed. You can use tools like [Swagger UI](http://localhost:8008/docs) (provided by FastAPI) to explore the API endpoints and their details.

- **PgAdmin** (optional): [http://localhost:5050](http://localhost:5050)  
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

`docker compose up` / `docker compose up --build` starts the **default** services below (order matters for **`api`** / **`app`**). The **`ds`** (Jupyter) service is **not** in that default set: it is tagged with the Compose profile **`data-science`**, so you must pass **`--profile data-science`** when you want Jupyter. More detail: **`AdVise/ds/README.md`**.

1. **PostgreSQL** – primary database
2. **pgAdmin** – database administration UI
3. **etl_db** – one-shot ETL (schema, preprocessing, `load_to_db` → **`training_dataset`** only). Uses raw CSVs in `AdVise/etl/db/data_raw/`. Re-running **`up`** truncates and reloads the offline training table. **`api`** waits until **`etl_db` finishes successfully.**
4. **api** – FastAPI backend (`AdVise/api/`)
5. **app** – Streamlit (`AdVise/app/`)
6. **ds** (optional, profile **`data-science`**) – Jupyter under **`AdVise/ds`**:  
   `docker compose --profile data-science up -d --build ds` — http://localhost:8888

## Prerequisites

Before running this setup, ensure Docker and Docker Compose are installed on your system.


- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)


## DB

- Access pgAdmin for PostgreSQL management: [http://localhost:5050](http://localhost:5050)
    - username: admin@admin.com 
    - password: admin
    - When running for the first time, you must create a server. Configure it as shown in the below image (Password is blurred it should be `password`.)
    ![Server Setup](docs/imgs/pgadmin_setup.png)

### Environment variables

Create a **`.env`** file in the root directory (this file is gitignored). Use variable names and layout like below; substitute your own user, password, and host (`db` inside Compose).

```env
# Used by the API container; path must end with the same DB as DB_NAME (default: marketing_db)
DATABASE_URL=postgresql+psycopg2://<user>:<password>@db:5432/marketing_db

# PostgreSQL (Compose `db` service)
DB_USER=<your_database_user>
DB_PASSWORD=<your_database_password>
DB_NAME=marketing_db

# pgAdmin
PGADMIN_EMAIL=admin@admin.com
PGADMIN_PASSWORD=admin
```

Do not commit **`.env`** or real secrets.



## Data modeling and ETL

Schema diagrams and notes also live under **`docs/`** (for example `docs/etl.md` and `docs/imgs/star_schema.png`). The marketing pipeline lives under **`AdVise/etl/db`**, and the Compose service **`etl_db`** is part of the default stack. See **`docs/etl.md`**.

## API


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

Adding another service named app, which is going to be responsible for the frontend.

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

# Copy the contents of the front directory to /app in the container
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.headless=true", "--server.runOnSave=true"] 
```


### Service

```yaml
  app:
    container_name: streamlit_app
    build:
      context: ./AdVise/app
      dockerfile: Dockerfile
    ports:
      - 8501:8501
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api
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

- **docker-build** – creates a throwaway **`.env`** in the job (placeholders for Compose), validates Compose, and builds **api**, **app**, and **etl_db** images (ETL is built but not executed in CI).
- **mkdocs** – installs **docs/requirements.txt**, **AdVise/api/requirements.txt**, and runs **`mkdocs build`**.