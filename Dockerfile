FROM python:3.11-slim

LABEL maintainer="Banking API Test Team"
LABEL description="Banking API BDD Test Framework"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Set work directory
WORKDIR /app

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies
RUN poetry install --only=main --no-root && rm -rf $POETRY_CACHE_DIR

# Copy project files
COPY . .

# Install project
RUN poetry install --only-root

# Create directories for reports and logs
RUN mkdir -p reports/allure-results reports/junit logs

# Set the default command
CMD ["poetry", "run", "behave", "--help"]