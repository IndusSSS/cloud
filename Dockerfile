# Dockerfile  — Build image for both “api” and “worker” services
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y python3-distutils

# Set workdir
WORKDIR /app

# Install Poetry
COPY pyproject.toml poetry.lock* /app/
RUN pip install --no-cache-dir poetry  \
 && poetry config virtualenvs.create false  \
 && poetry install --only main --no-root

# Copy rest of the code
COPY . /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
