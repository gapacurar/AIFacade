# Use a lightweight Python image
FROM python:3.13.5-slim

# Set working directory inside a container
WORKDIR /app

# Install required system dependencies for Python packages (e.g., for SQLite support)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure instance/ folder exists for SQLite
RUN mkdir -p /app/instance

# Copy the whole project (app and config)
COPY . .

# Expose port 5000
EXPOSE 5000

# Use environment variables for secrets
ENV FLASK_APP=project
ENV FLASK_ENV=production

# Run Gunicorn as production server
CMD ["gunicorn", "--config", "gunicorn.conf.py", "project:create_app()"]
