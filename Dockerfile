# Mini Search Engine with Web Crawler
# Production-style Docker image

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY app/ ./app/
COPY scripts/ ./scripts/

# Data directory (mounted or created at runtime)
ENV SEARCH_ENGINE_DB_PATH=/data/search_engine.db
RUN mkdir -p /data

EXPOSE 8000

# Run the web app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
