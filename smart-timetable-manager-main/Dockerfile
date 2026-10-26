# Production Dockerfile for EduNova Smart Timetable Manager
# Optimized for Google Cloud Run / Container Hosting

FROM python:3.11-slim

# Set environment variables for production execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    FLASK_DEBUG=false

# Set container working directory
WORKDIR /app

# Install dependencies first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files, templates, static assets, and bundled SQLite database
COPY . .

# Expose standard Cloud Run HTTP port
EXPOSE 8080

# Production startup using Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]
