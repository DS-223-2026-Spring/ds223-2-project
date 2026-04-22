# Dockerized PostgreSQL, pgAdmin, FastAPI, and Streamlit

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
4. Select a folder to work in: repository root, `app/`, or `api/`, depending on your role.



## Presentation 

**Follow to [this](https://hovhannisyan91.github.io/pythonmicroservicedesign/) link.**

## Installation

Before getting started, ensure you have the following prerequisites installed:

1. Clone the repository:
   ```bash
   git clone https://github.com/hovhannisyan91/pythonmicroservicedesign.git
   cd pythonmicroservicedesign
   ```

2. Create a local environment file (copy the example, then adjust values for your machine if needed):
   ```bash
   cp .env.example .env
   ```

3. Build and start the Docker containers from the repository root:
   ```bash
   docker compose up --build
   ```

## Access the Application

After running `docker compose up --build`, you can access each component of the application at the following URLs:


- **Streamlit Frontend:** http://localhost:8501 The main interface for managing employees, built with Streamlit. Use this to add, view, update, and delete employee records.
- **FastAPI Backend**: [http://localhost:8008](http://localhost:8008)  
  The backend API where requests are processed. You can use tools like [Swagger UI](http://localhost:8008/docs) (provided by FastAPI) to explore the API endpoints and their details.

- **PgAdmin** (optional): [http://localhost:5050](http://localhost:5050)  
  A graphical tool for PostgreSQL, which allows you to view and manage the database. Login using the credentials set in the `.env` file:
  
  - **Email**: Value of `PGADMIN_EMAIL` in your `.env` file
  - **Password**: Value of `PGADMIN_PASSWORD` in your `.env` file

> Note: Ensure Docker is running, and you have created `.env` from `.env.example` (see Installation) with values that match your setup.



## Project Structure

Here’s an overview of the project’s file structure:

```bash
.
├── LICENSE
├── README.md
├── .github/            # CI workflows
├── .env.example        # Example environment (copy to `.env`)
├── .env                # Your local environment (not committed; create from `.env.example`)
├── docker-compose.yml  # Docker Compose configuration
├── api                 # FastAPI backend folder
│   ├── Dockerfile      # Dockerfile for FastAPI container
│   ├── __init__.py     # Marks this directory as a package
│   ├── main.py         # FastAPI main entry point
│   ├── database.py     # Database configuration and connection setup
│   ├── models.py       # SQLAlchemy models for database tables
│   ├── schema.py       # Pydantic schemas for request and response validation
│   └── requirements.txt # Backend dependencies
├── app                 # Streamlit frontend folder
│   ├── Dockerfile      # Dockerfile for Streamlit container
│   ├── __init__.py
│   ├── app.py          # Streamlit main entry point
│   ├── pages           # Additional pages for Streamlit
│   │   ├── page1.py
│   │   └── page2.py
│   └── requirements.txt #frontend dependancies
├── mkdocs.yaml         # MkDocs site config (run `mkdocs serve` from repo root)
└── docs                # Documentation assets
    ├── requirements.txt # pip deps for building docs (MkDocs, theme, mkdocstrings)
    ├── imgs            # Image assets for documentation
    ├── index.md        # MkDocs home page (builds to `site/index.html`)
    ├── index.html      # Optional static page (open locally; excluded from MkDocs output)
    └── *.md              # Other pages (API, app, ETL, demo, …)
```

## Docker

`docker compose` brings up the following services:

1. **PostgreSQL** – primary database
2. **pgAdmin** – database administration UI
3. **api** – FastAPI backend (`./api`, image built from `api/Dockerfile`)
4. **app** – Streamlit frontend (`./app`, image built from `app/Dockerfile`)

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

### Environment Variables

Create a `.env` file in the root directory to define your environment variables as below:

```env
# Used by the API container (SQLAlchemy connection string)
DATABASE_URL=postgresql+psycopg2://<user>:<password>@db:5432/<database>

# PostgreSQL (Compose `db` service)
DB_USER=<your_database_user>
DB_PASSWORD=<your_database_password>
DB_NAME=<your_database_name>

# pgAdmin
PGADMIN_EMAIL=admin@admin.com
PGADMIN_PASSWORD=admin
```

Copy `.env.example` to `.env` and adjust; do not commit real secrets.



## Data modeling and ETL (reference)

Schema diagrams and ETL notes for the course live under `docs/` (for example `docs/etl.md` and `docs/imgs/star_schema.png`). The repository root is organized around the Dockerized **db**, **api**, and **app** services; a separate batch ETL service is not part of the default Compose file so orchestration and data-science work can be added in a way that fits your team’s workflow.

## API


### Features

- **Add New Employee**: Enter details like first name, last name, email, department, position, and salary to add a new employee.
- **Get Employee by ID**: Retrieve an employee’s information using their unique ID.
- **Update Salary**: Update the salary of an existing employee by providing their ID and the new salary.
- **Delete Employee**: Remove an employee record from the system using their ID.

The FastAPI app under `api/` connects HTTP endpoints to PostgreSQL; you can create, read, update, and delete employees by id.

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
      context: ./app
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

- **`mkdocs.yaml`** – site name, navigation, Material theme, and **mkdocstrings** for `api` / `app` code.
- **`docs/index.md`** – MkDocs home; other pages are linked from there and from the nav in `mkdocs.yaml`.
- **`docs/index.html`** – optional static HTML (open the file in a browser without MkDocs); it is not copied into `site/` when `index.md` is present (that is normal).
- **`docs/imgs/`** – images referenced from the Markdown files.

## CI

The workflow in **`.github/workflows/ci.yaml`** runs on pushes and pull requests to `main` and `master`:

- **docker-build** – creates `.env` from **`.env.example`**, validates Compose, and builds **api** and **app** images.
- **mkdocs** – installs **docs/requirements.txt** and runs **`mkdocs build`** so documentation always builds.