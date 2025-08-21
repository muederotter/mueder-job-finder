FROM python:3.12-slim

# Basic environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=${PORT} \
    STREAMLIT_ENABLE_CORS=false \
    PYTHONIOENCODING=utf-8

WORKDIR /app

# Install system dependencies required to build some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt ./

# Install Python dependencies
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip install -r requirements.txt

# Copy application source
COPY . /app

# Create a directory for persistent data (SQLite files). Make it writable.
RUN mkdir -p /app/data && chown -R root:root /app/data

EXPOSE ${PORT}

# Run the streamlit app in headless mode. Override CMD with environment variables if needed.
CMD ["streamlit", "run", "main.py", "--server.port", "8501", "--server.headless", "true"]
