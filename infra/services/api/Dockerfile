# infra/services/api/Dockerfile

# 1) Base Python image
FROM python:3.12-slim

# 2) Set working directory
WORKDIR /app

# 3) Copy only requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copy your FastAPI source
COPY . .

# 5) Expose port and run Uvicorn
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
