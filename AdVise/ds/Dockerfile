FROM python:3.12-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8888
# Notebook 7+ uses Jupyter Server: disable auth for local dev (exec + shell so empty token is not mangled)
CMD ["sh", "-c", "exec jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --ServerApp.token= --ServerApp.password="]
