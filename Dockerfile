# Base Image: Lightweight Python 3.12 (Matches Project Env)
FROM python:3.12-slim

# Set working directory
WORKDIR /app

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

# Expose Streamlit port
EXPOSE 8501

# Healthcheck for Cloud Run
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Start Streamlit
ENTRYPOINT ["streamlit", "run", "run.py", "--server.port=8501", "--server.address=0.0.0.0"]
