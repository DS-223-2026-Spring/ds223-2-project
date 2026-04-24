# Marketing ETL: apply schema, preprocessing, load training_dataset (DB_NAME from .env; same Postgres as Compose `db`)
# Build:  docker build -t etl-db ./AdVise/etl/db
# Run:     use Compose service `etl_db` (profile `marketing`) or: docker run --env-file .env -e POSTGRES_HOST=host.docker.internal ... 
FROM python:3.12-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/docker-entrypoint.sh /app/sql/apply_marketing_schema.sh 2>/dev/null || true

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Override in Compose: bind-mount ./AdVise/etl/db for live data_raw CSVs
CMD ["/app/docker-entrypoint.sh"]
