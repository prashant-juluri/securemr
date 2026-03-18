FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Fix git safe directory issue
RUN git config --global --add safe.directory /app

# Copy project files
COPY . .

# 🔥 Download model during build
RUN mkdir -p /models && \
    curl -L -o /models/qwen-coder.gguf \
    https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install semgrep
RUN pip install --no-cache-dir semgrep

# Create non-root user
RUN useradd --create-home --shell /bin/bash securemr-user && \
    chown -R securemr-user:securemr-user /app

USER securemr-user

CMD ["python", "securemr.py"]