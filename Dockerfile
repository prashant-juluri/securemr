FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Fix git safe directory issue in CI containers
RUN git config --global --add safe.directory /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install semgrep
RUN pip install semgrep

# Create a non-root user
RUN useradd --create-home --shell /bin/bash securemr-user && \
    chown -R securemr-user:securemr-user /app

# Switch to non-root user
USER securemr-user

# Default command
CMD ["python", "securemr.py"]