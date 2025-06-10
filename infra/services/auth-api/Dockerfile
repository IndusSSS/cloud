# 1. Start from the official slim Python image
FROM python:3.12-slim

# 2. Prevent .pyc files and force stdout/stderr to flush immediately
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Create & set our working directory inside the container
WORKDIR /app

# 4. Install any OS‐level dependencies (only if you need them)
#    e.g. gcc/build-essential if you have binary wheels
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

# 5. Copy & install Python deps
#    Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 6. Copy your FastAPI application code
COPY app/ ./app/

# 7. (Optional) create a non-root user and switch  
#    RUN useradd --create-home appuser && chown -R appuser /app  
#    USER appuser

# 8. Expose the port your app will run on
EXPOSE 8000

# 9. Run Uvicorn; --reload is great for dev but remove it in production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
