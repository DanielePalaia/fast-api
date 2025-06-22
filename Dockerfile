# Use official Python slim image as base
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies needed for Poetry and building packages
RUN apt-get update && apt-get install -y curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry (using the official install script)
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy only Poetry files to leverage Docker cache
COPY pyproject.toml poetry.lock* /app/

# Install dependencies without creating a virtual environment (use system env)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the app code
COPY . .

# Expose port
EXPOSE 8000

# Run the FastAPI app with uvicorn and 4 workers
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
