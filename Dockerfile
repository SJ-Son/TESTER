# Base Image: Lightweight Python 3.12 (Matches Project Env)
FROM python:3.12-slim

# Set working directory
# Set working directory
WORKDIR /app

# Prevent Python from writing pyc files to disc and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies (minimal)
# curl is added for HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary source code (Strict Copy)
COPY src/ ./src/
COPY run.py .

# Expose Streamlit port (Cloud Run default is 8080)
EXPOSE 8080

# Healthcheck for Cloud Run
HEALTHCHECK CMD curl --fail http://localhost:8080/ || exit 1

# Start Streamlit on port 8080
# Start FastAPI with Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
