FROM python:3.11-slim
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the bridge code
COPY app.py .

# Run the bridge on container start
CMD ["python", "app.py"]
