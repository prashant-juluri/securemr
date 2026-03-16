FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for git, semgrep and llama-cpp compilation
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Fix git safe directory issue in CI containers
RUN git config --global --add safe.directory /app

# Copy project files
COPY . .

# Upgrade pip first (important for compiling wheels)
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Semgrep
RUN pip install --no-cache-dir semgrep

# Create a non-root user
RUN useradd --create-home --shell /bin/bash securemr-user && \
    chown -R securemr-user:securemr-user /app

# Switch to non-root user
USER securemr-user

# Default command
CMD ["python", "securemr.py"]